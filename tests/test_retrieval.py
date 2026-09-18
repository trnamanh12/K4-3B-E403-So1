import json
from dataclasses import replace

import httpx
import pytest

from vlearn.models import Query, Selection
from vlearn.openrouter import OpenRouter
from vlearn.retrieval import Retriever, Vectors, index_snapshot


def test_bm25_filters_lesson_and_strict_does_not_expand(settings, corpus):
    retriever = Retriever(settings, corpus)
    expanded = Query(question="Attention", mode="LESSON_EXPANDED", snapshot_id="fixture", lesson_id="day-1")
    found = retriever.search(expanded, "bm25")
    assert found["evidence"] and {e["unit_id"] for e in found["evidence"]} == {"T01-001"}
    strict = Query(question="Attention", snapshot_id="fixture", selections=[Selection(unit_id="T01-002")])
    found = retriever.search(strict)
    assert found["backend"] == "direct"
    assert {e["unit_id"] for e in found["evidence"]} == {"T01-002"}
    retriever.close()


def test_selection_scope_offsets_and_no_eligible_fallback(settings, corpus):
    retriever = Retriever(settings, corpus)
    query = Query(question="Attention", snapshot_id="fixture", lesson_id="day-1",
                  selections=[Selection(unit_id="T02-001")])
    with pytest.raises(ValueError, match="outside"):
        retriever.search(query)
    query = Query(question="Attention", snapshot_id="fixture", selections=[Selection(unit_id="T01-001", start=0, end=9)])
    assert retriever.search(query)["evidence"][0]["text"] == "Attention"
    with pytest.raises(ValueError, match="exceed"):
        retriever.search(query.model_copy(update={"selections": [Selection(unit_id="T01-001", start=0, end=999)]}))
    with corpus.connect() as db:
        unit = corpus.record("units", "fixture", "T01-001")
        unit["evidence_eligible"] = False
        db.execute("UPDATE units SET data=? WHERE snapshot='fixture' AND id='T01-001'", (json.dumps(unit),))
    found = retriever.search(query)
    assert found["evidence"] == []
    assert found["unavailable_sources"] == ["T01-001"]
    retriever.close()


def test_index_hybrid_roundtrip_and_idempotence(settings, corpus, monkeypatch):
    calls = []
    def handler(request):
        if request.method == "GET":
            return httpx.Response(200, json={"data": [{"id": settings.embedding_model, "context_length": 512}]})
        body = json.loads(request.content)
        calls.append(body)
        return httpx.Response(200, json={"data": [
            {"index": i, "embedding": [1.0, float("Attention" in text), float("Temperature" in text)]}
            for i, text in enumerate(body["input"])]})
    def provider_factory(config, store, counter):
        return OpenRouter(config, store, counter, transport=httpx.MockTransport(handler))
    monkeypatch.setattr("vlearn.retrieval.OpenRouter", provider_factory)
    first = index_snapshot(settings, "fixture")
    assert first["points"] == 3
    with pytest.raises(ValueError, match="No active"):
        corpus.snapshot()
    corpus.activate("fixture")
    assert corpus.snapshot()["id"] == "fixture"
    before = len(calls)
    assert index_snapshot(settings, "fixture")["points"] == 3
    assert len(calls) == before
    retriever = Retriever(settings, corpus)
    query = Query(question="Attention", mode="LESSON_EXPANDED", lesson_id="day-1", snapshot_id="fixture")
    result = retriever.search(query)
    assert result["evidence"][0]["unit_id"] == "T01-001"
    assert all(e["unit_id"] != "T02-001" for e in result["evidence"])
    assert "dense" in result["candidates"][0]["ranks"]
    retriever.close()
    mismatched = Retriever(replace(settings, embedding_revision="2"), corpus)
    with pytest.raises(ValueError, match="differ"):
        mismatched.search(query)
    mismatched.close()


def test_incomplete_index_cannot_activate(settings, corpus, monkeypatch):
    def handler(request):
        if request.method == "GET":
            return httpx.Response(200, json={"data": [{"id": settings.embedding_model, "context_length": 512}]})
        return httpx.Response(503, json={"error": "unavailable"})
    monkeypatch.setattr("vlearn.retrieval.OpenRouter", lambda c, s, t: OpenRouter(
        c, s, t, transport=httpx.MockTransport(handler)))
    with pytest.raises(RuntimeError):
        index_snapshot(settings, "fixture")
    with pytest.raises(ValueError, match="Only"):
        corpus.activate("fixture")
    with pytest.raises(ValueError, match="No active"):
        corpus.snapshot()


def test_vector_database_rejects_dimension_change(settings):
    vector = Vectors(settings)
    vector.create("test", 3)
    with pytest.raises(ValueError, match="dimensions"):
        vector.create("test", 4)
    vector.close()
