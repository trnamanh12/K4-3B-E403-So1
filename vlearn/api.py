import html
import secrets
import threading
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from pydantic import Field

from .config import Settings
from .models import Query, StrictModel
from .openrouter import ProviderError
from .store import Store
from .tutor import Tutor


class Feedback(StrictModel):
    trace_id: str = Field(max_length=100)
    helpful: bool
    comment: str = Field(default="", max_length=1000)


def create_app(settings=None, tutor=None):
    settings = settings or Settings.from_env()
    store = Store(settings.artifacts_dir)
    lock = threading.Lock()
    service = tutor

    @asynccontextmanager
    async def lifespan(app):
        yield
        if service:
            service.close()

    app = FastAPI(title="VLearn RAG", version="0.1.0", lifespan=lifespan)

    def authorize(request: Request):
        if settings.api_token:
            bearer = request.headers.get("Authorization", "").removeprefix("Bearer ")
            cookie = request.cookies.get("vlearn_token", "")
            if not any(secrets.compare_digest(x, settings.api_token) for x in (bearer, cookie)):
                raise HTTPException(401, "Authentication required")
            origin = request.headers.get("origin")
            if request.method == "POST" and origin and origin.rstrip("/") != str(request.base_url).rstrip("/"):
                raise HTTPException(403, "Cross-origin request rejected")

    auth = [Depends(authorize)]

    @app.exception_handler(ValueError)
    async def invalid_input(request, exc):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(ProviderError)
    async def upstream_error(request, exc):
        return JSONResponse(status_code=503, content={"detail": str(exc), "status": "ERROR"})

    @app.get("/", response_class=HTMLResponse)
    def home():
        return (Path(__file__).parent / "static" / "index.html").read_text()

    @app.post("/api/session", dependencies=auth)
    def login(request: Request):
        response = JSONResponse({"authenticated": True})
        if settings.api_token:
            response.set_cookie("vlearn_token", settings.api_token, httponly=True, samesite="strict",
                                secure=request.url.scheme == "https", max_age=3600)
        return response

    @app.get("/api/health", dependencies=auth)
    def health():
        return {"status": "ok", "embedding_model": settings.embedding_model,
                "api_key_configured": bool(settings.api_key)}

    @app.get("/api/corpus", dependencies=auth)
    def corpus():
        with store.connect() as db:
            snapshots = [dict(r) for r in db.execute("SELECT id,status,created FROM snapshots ORDER BY created DESC")]
            active = db.execute("SELECT value FROM state WHERE key='active'").fetchone()
        return {"active": active[0] if active else None, "snapshots": snapshots}

    @app.get("/api/documents/{sid}", dependencies=auth)
    def documents(sid: str):
        store.snapshot(sid)
        return [{k: v for k, v in d.items() if k != "archive_path"} for d in store.records("documents", sid)]

    @app.get("/api/units/{sid}/{document_id}", dependencies=auth)
    def units(sid: str, document_id: str):
        store.record("documents", sid, document_id)
        return [{k: u[k] for k in ("id", "section_title", "pdf_page", "segment_id", "evidence_eligible")}
                for u in store.records("units", sid) if u["document_id"] == document_id]

    @app.get("/api/sources/{sid}/{unit_id}", dependencies=auth)
    def source(sid: str, unit_id: str):
        return store.record("units", sid, unit_id)

    @app.get("/api/files/{sid}/{document_id}", dependencies=auth)
    def source_file(sid: str, document_id: str):
        doc = store.record("documents", sid, document_id)
        path = Path(doc["archive_path"])
        if not path.is_file():
            raise HTTPException(404, "Archived document is unavailable")
        return FileResponse(path, filename=doc["filename"], content_disposition_type="inline",
                            media_type="application/pdf" if doc["source_type"] == "slide" else "text/plain")

    @app.get("/sources/{sid}/{unit_id}", dependencies=auth, response_class=HTMLResponse)
    def source_view(sid: str, unit_id: str, start: int = 0, end: int | None = None):
        unit = store.record("units", sid, unit_id)
        text = unit["text"]
        end = len(text) if end is None else end
        if not 0 <= start <= end <= len(text):
            raise ValueError("Invalid citation span")
        highlighted = html.escape(text[:start]) + "<mark>" + html.escape(text[start:end]) + "</mark>" + html.escape(text[end:])
        frame = ""
        if unit["source_type"] == "slide":
            url = f"/api/files/{sid}/{unit['document_id']}#page={unit['pdf_page']}"
            frame = f'<iframe title="Slide gốc" src="{html.escape(url, quote=True)}" style="width:100%;height:65vh"></iframe>'
        return ("<!doctype html><html lang='vi'><meta charset='utf-8'><title>Nguồn trích dẫn</title>"
                "<body style='max-width:1100px;margin:24px auto;font:16px system-ui'>"
                f"<h1>{html.escape(unit['section_title'])}</h1><p>{html.escape(unit_id)}</p>"
                f"{frame}<pre style='white-space:pre-wrap;line-height:1.7'>{highlighted}</pre></body></html>")

    def get_service():
        nonlocal service
        if service is None:
            service = Tutor(settings)
        return service

    @app.post("/api/search", dependencies=auth)
    def search(query: Query, backend: str = "hybrid"):
        with lock:
            return get_service().retriever.search(query, backend)

    @app.post("/api/ask", dependencies=auth)
    def ask(query: Query):
        with lock:
            return get_service().ask(query)

    @app.post("/api/feedback", dependencies=auth)
    def feedback(body: Feedback):
        store.feedback(body.trace_id, body.helpful, body.comment)
        return {"saved": True}

    return app
