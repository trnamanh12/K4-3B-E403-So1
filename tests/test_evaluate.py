import json

from vlearn.evaluate import evaluate_retrieval


def test_retrieval_evaluator_does_not_supply_gold_context(settings, corpus, tmp_path, monkeypatch):
    cases = tmp_path / "cases.json"
    cases.write_text(json.dumps([{"id": "R1", "question": "Attention", "lesson_id": "day-1",
                                 "expected_sources": ["T01-001"]}]))
    from vlearn.retrieval import Retriever
    original = Retriever.search
    def checked_search(self, query, *args, **kwargs):
        assert query.selections == []
        assert "expected_sources" not in query.model_dump()
        return original(self, query, *args, **kwargs)
    monkeypatch.setattr(Retriever, "search", checked_search)
    result = evaluate_retrieval(settings, cases, "fixture", backend="bm25")
    assert result["recall_at_k"] == 1
    assert result["mrr_at_k"] == 1
    assert result["embedding_model"] is None
