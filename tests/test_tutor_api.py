import json
from dataclasses import replace

import httpx
import pytest
from fastapi.testclient import TestClient

from vlearn.api import create_app
from vlearn.models import Query, Selection
from vlearn.openrouter import OpenRouter
from vlearn.retrieval import Retriever
from vlearn.tutor import Tutor


def make_tutor(settings, corpus, *, route="CLEAR", supported=True, valid=True, citation="valid", fail=False):
    def handler(request):
        if fail:
            return httpx.Response(503, json={"error": "private text must not appear in logs"})
        body = json.loads(request.content)
        payload = json.loads(body["messages"][1]["content"])
        name = body["response_format"]["json_schema"]["name"]
        if name == "RouteDecision":
            result = {"status": route, "reason": "Classified"}
        elif name == "GroundingDecision":
            result = {"supported": supported, "reason": "checked",
                      "evidence_ids": [payload["evidence"][0]["evidence_id"]]}
        elif name == "Draft":
            evidence = payload["evidence"][0]
            result = {"claims": [{"text": "Attention sử dụng thông tin từ các token khác.", "evidence": [{
                "evidence_id": evidence["evidence_id"] if citation != "unknown" else "ev-forged",
                "quote": evidence["text"] if citation != "fabricated" else "This source never says this."}]}]}
        elif name == "Validation":
            result = {"supported": valid, "complete": valid, "reason": "checked"}
        else:
            raise AssertionError(name)
        return httpx.Response(200, json={"choices": [{"finish_reason": "stop", "message": {
            "content": json.dumps(result)}}], "usage": {"total_tokens": 10}})
    provider = OpenRouter(settings, corpus, transport=httpx.MockTransport(handler))
    return Tutor(settings, Retriever(settings, corpus, provider))


def query():
    return Query(question="Attention là gì?", snapshot_id="fixture", selections=[Selection(unit_id="T01-001")])


def test_grounded_answer_resolves_exact_quote_and_logs(settings, corpus):
    tutor = make_tutor(settings, corpus)
    result = tutor.ask(query())
    assert result["final_status"] == "GROUNDED"
    citation = result["citations"][0]
    source = corpus.record("units", "fixture", citation["unit_id"])
    assert source["text"][citation["start"]:citation["end"]] == citation["quote"]
    assert citation["pdf_page"] is None
    with corpus.connect() as db:
        trace = json.loads(db.execute("SELECT data FROM traces WHERE id=?", (result["trace_id"],)).fetchone()[0])
    assert trace["status"] == "GROUNDED"
    assert len(trace["decisions"]) == 3
    assert query().question not in json.dumps(trace)
    assert "test-key" not in json.dumps(trace)
    tutor.close()


@pytest.mark.parametrize("options,status", [
    ({"route": "AMBIGUOUS"}, "AMBIGUOUS"),
    ({"route": "OUT_OF_SCOPE"}, "OUT_OF_SCOPE"),
    ({"supported": False}, "INSUFFICIENT_GROUNDING"),
    ({"valid": False}, "INSUFFICIENT_GROUNDING"),
    ({"citation": "unknown"}, "INSUFFICIENT_GROUNDING"),
    ({"citation": "fabricated"}, "INSUFFICIENT_GROUNDING"),
])
def test_fail_closed_gates(settings, corpus, options, status):
    tutor = make_tutor(settings, corpus, **options)
    result = tutor.ask(query())
    assert result["final_status"] == status
    assert result["citations"] == []
    tutor.close()


def test_api_auth_source_view_citations_and_feedback(settings, corpus):
    settings = replace(settings, api_token="private-token")
    tutor = make_tutor(settings, corpus)
    with TestClient(create_app(settings, tutor)) as client:
        assert client.get("/").status_code == 200
        assert client.get("/api/corpus").status_code == 401
        assert client.post("/api/session", headers={"Authorization": "Bearer private-token"}).status_code == 200
        assert client.get("/api/corpus").status_code == 200
        result = client.post("/api/ask", json=query().model_dump())
        assert result.status_code == 200
        body = result.json()
        assert client.get(body["citations"][0]["viewer_url"]).status_code == 200
        assert "<mark>" in client.get(body["citations"][0]["viewer_url"]).text
        assert client.post("/api/feedback", json={"trace_id": body["trace_id"], "helpful": True}).status_code == 200
        assert client.post("/api/feedback", json={"trace_id": "missing", "helpful": False}).status_code == 400
        assert client.post("/api/ask", headers={"Origin": "https://evil.example"}, json=query().model_dump()).status_code == 403


def test_api_infrastructure_error_is_not_insufficient_grounding(settings, corpus):
    with TestClient(create_app(settings, make_tutor(settings, corpus, fail=True))) as client:
        result = client.post("/api/ask", json=query().model_dump())
        assert result.status_code == 503
        assert result.json()["status"] == "ERROR"
        assert "private text" not in result.text
    with corpus.connect() as db:
        trace = json.loads(db.execute("SELECT data FROM traces").fetchone()[0])
    assert trace["status"] == "ERROR"


def test_scope_required_and_extra_fields_rejected(settings, corpus):
    with TestClient(create_app(settings, make_tutor(settings, corpus))) as client:
        assert client.post("/api/search", json={"question": "Hi", "snapshot_id": "fixture"}).status_code == 422
        body = query().model_dump() | {"retrieved_documents": [{"text": "fake source"}]}
        assert client.post("/api/ask", json=body).status_code == 422
        body = query().model_dump()
        body["selections"][0]["unit_id"] = "nonexistent"
        assert client.post("/api/ask", json=body).status_code == 400
