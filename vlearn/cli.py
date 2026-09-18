import argparse
import json
import sys

from .config import Settings
from .ingest import prepare
from .models import Query, Selection
from .openrouter import OpenRouter
from .retrieval import Retriever, index_snapshot
from .store import Store
from .text import TokenCounter
from .tutor import Tutor


def output(data):
    print(json.dumps(data, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="VLearn RAG with OpenRouter embeddings")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("models", help="List live OpenRouter embedding models")
    sub.add_parser("prepare", help="Parse and chunk locally; does not send corpus to an API")
    sub.add_parser("status", help="List prepared/indexed snapshots")
    sub.add_parser("doctor", help="Check config, catalog and tokenizer; no embedding requests")
    sub.add_parser("smoke", help="Embed two synthetic sentences to verify the configured provider")
    for command in ("index", "activate"):
        cmd = sub.add_parser(command)
        cmd.add_argument("--snapshot", required=True)
    for command in ("search", "ask"):
        cmd = sub.add_parser(command)
        cmd.add_argument("question")
        cmd.add_argument("--snapshot", help="Defaults to active snapshot")
        cmd.add_argument("--lesson")
        cmd.add_argument("--unit", action="append", default=[])
        cmd.add_argument("--mode", choices=["STRICT_SOURCE", "LESSON_EXPANDED"], default="STRICT_SOURCE")
        if command == "search":
            cmd.add_argument("--backend", choices=["bm25", "dense", "hybrid"], default="hybrid")
            cmd.add_argument("--top-k", type=int, default=8)
    serve = sub.add_parser("serve")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", default=8000, type=int)
    args = parser.parse_args()
    settings = Settings.from_env()
    try:
        if args.command == "prepare":
            output(prepare(settings))
        elif args.command in {"models", "doctor", "smoke"}:
            provider = OpenRouter(settings, Store(settings.artifacts_dir))
            try:
                if args.command == "models":
                    output([{k: m.get(k) for k in ("id", "context_length", "pricing")}
                            for m in provider.models()])
                else:
                    provider.counter = TokenCounter(settings)
                    info = provider.model_info()
                    result = {"model": info["id"], "context_length": info.get("context_length"),
                              "api_key_configured": bool(settings.api_key),
                              "tokenizer": provider.counter.fingerprint,
                              "document_prefix": settings.document_prefix, "query_prefix": settings.query_prefix,
                              "description": info.get("description")}
                    if args.command == "smoke":
                        vectors = provider.embed(["A cat sits on a mat.", "A dog runs in a park."],
                                                 context_limit=info["context_length"])
                        result.update({"vectors": len(vectors), "dimensions": len(vectors[0]),
                                       "finite_nonzero_vectors": True})
                    output(result)
            finally:
                provider.close()
        elif args.command == "status":
            store = Store(settings.artifacts_dir)
            with store.connect() as db:
                snapshots = [dict(r) for r in db.execute(
                    "SELECT id,created,status,collection,dimensions FROM snapshots ORDER BY created DESC")]
                active = db.execute("SELECT value FROM state WHERE key='active'").fetchone()
            output({"active": active[0] if active else None, "snapshots": snapshots})
        elif args.command == "index":
            if settings.embedding_model == "liquid/lfm-2.5-embedding-350m:free":
                print("Provider notice: Liquid's free endpoint may retain requests/embeddings for training. "
                      "This command sends eligible corpus chunks to OpenRouter.", file=sys.stderr)
            output(index_snapshot(settings, args.snapshot,
                                  progress=lambda done, total: print(f"Indexed {done}/{total}", file=sys.stderr)))
        elif args.command == "activate":
            store = Store(settings.artifacts_dir)
            store.activate(args.snapshot)
            output({"active": args.snapshot})
        elif args.command in {"search", "ask"}:
            if args.command == "search" and args.top_k < 1:
                raise ValueError("top-k must be positive")
            sid = args.snapshot or Store(settings.artifacts_dir).snapshot()["id"]
            query = Query(question=args.question, snapshot_id=sid, lesson_id=args.lesson,
                          mode=args.mode, selections=[Selection(unit_id=u) for u in args.unit])
            service = Retriever(settings) if args.command == "search" else Tutor(settings)
            try:
                output(service.search(query, args.backend, args.top_k) if args.command == "search"
                       else service.ask(query))
            finally:
                service.close()
        elif args.command == "serve":
            if args.host not in {"127.0.0.1", "localhost", "::1"} and not settings.api_token:
                raise ValueError("Set RAG_API_TOKEN before binding outside loopback")
            import uvicorn
            uvicorn.run("vlearn.api:create_app", factory=True, host=args.host, port=args.port, workers=1)
    except Exception as exc:
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
