import json
from dataclasses import replace

import httpx
import pytest

from vlearn.models import RouteDecision
from vlearn.openrouter import OpenRouter, ProviderError
from vlearn.store import Store
from vlearn.text import TokenCounter


def test_embedding_order_prefix_cache_and_dimensions(settings):
    requests = []
    def handler(request):
        body = json.loads(request.content)
        requests.append(body)
        assert request.url.path == "/api/v1/embeddings"
        assert request.headers["authorization"] == "Bearer test-key"
        assert "dimensions" not in body
        return httpx.Response(200, json={"data": [
            {"index": i, "embedding": [float(i+1), 2.0, 3.0]} for i in reversed(range(len(body["input"])))]})
    client = OpenRouter(settings, Store(settings.artifacts_dir), transport=httpx.MockTransport(handler))
    first = client.embed(["A", "B"])
    assert first == [[1, 2, 3], [2, 2, 3]]
    assert requests[0]["input"] == ["document: A", "document: B"]
    assert client.embed(["A", "B"]) == first
    assert len(requests) == 1
    client.embed(["A"], kind="query")
    assert requests[-1]["input"] == ["query: A"]
    client.close()


@pytest.mark.parametrize("rows", [
    [{"index": 0, "embedding": [0, 0]}],
    [{"index": 0, "embedding": []}],
    [{"index": 1, "embedding": [1, 2]}],
    [{"index": 0, "embedding": [True, 2]}],
    [],
])
def test_reject_invalid_embedding_responses(settings, rows):
    client = OpenRouter(settings, transport=httpx.MockTransport(lambda _: httpx.Response(200, json={"data": rows})))
    with pytest.raises(ProviderError):
        client.embed(["A"])
    client.close()


def test_dimension_override_and_input_type(settings):
    settings = replace(settings, embedding_dimensions=2, document_input_type="search_document")
    def handler(request):
        body = json.loads(request.content)
        assert body["dimensions"] == 2
        assert body["input_type"] == "search_document"
        return httpx.Response(200, json={"data": [{"index": 0, "embedding": [1, 2, 3]}]})
    client = OpenRouter(settings, transport=httpx.MockTransport(handler))
    with pytest.raises(ProviderError, match="dimensions"):
        client.embed(["A"])
    client.close()


def test_retry_429_without_leaking_error_body(settings, monkeypatch):
    calls = []
    sleeps = []
    monkeypatch.setattr("vlearn.openrouter.time.sleep", sleeps.append)
    def handler(request):
        calls.append(request)
        if len(calls) == 1:
            return httpx.Response(429, headers={"Retry-After": "0"}, json={"error": "secret"})
        return httpx.Response(200, json={"data": [{"index": 0, "embedding": [1, 2]}]})
    client = OpenRouter(replace(settings, max_retries=1), transport=httpx.MockTransport(handler))
    assert client.embed(["A"]) == [[1, 2]]
    assert len(calls) == 2 and sleeps == [0]
    client.close()


def test_training_data_privacy_error_is_actionable_without_echoing_body(settings):
    response = {"error": {"message": "0 endpoints available. Free model training violation "
                                     "(account settings). private-source-text"}}
    client = OpenRouter(settings, transport=httpx.MockTransport(
        lambda _: httpx.Response(404, json=response)))
    with pytest.raises(ProviderError, match="privacy settings") as caught:
        client.embed(["synthetic input"])
    assert "private-source-text" not in str(caught.value)
    client.close()


def test_daily_free_quota_error_is_actionable_without_echoing_body(settings):
    response = {"error": {"message": "Rate limit exceeded: free-models-per-day. private-source-text"}}
    client = OpenRouter(settings, transport=httpx.MockTransport(
        lambda _: httpx.Response(429, json=response)))
    with pytest.raises(ProviderError, match="daily free-model request quota") as caught:
        client.embed(["synthetic input"])
    assert "private-source-text" not in str(caught.value)
    client.close()


def test_no_key_and_no_truncation(no_key, settings):
    client = OpenRouter(no_key)
    with pytest.raises(ProviderError, match="OPENROUTER_API_KEY"):
        client.embed(["A"])
    client.close()
    client = OpenRouter(settings, counter=TokenCounter(settings))
    with pytest.raises(ValueError, match="exceeds"):
        client.embed(["A" * 600], context_limit=512)
    client.close()


def test_structured_output_requires_valid_schema(settings):
    def handler(request):
        body = json.loads(request.content)
        assert body["response_format"]["json_schema"]["strict"] is True
        return httpx.Response(200, json={"choices": [{"finish_reason": "stop", "message": {
            "content": json.dumps({"status": "GUESS", "reason": "no"})}}]})
    client = OpenRouter(settings, transport=httpx.MockTransport(handler))
    with pytest.raises(ProviderError, match="schema-invalid"):
        client.structured("system", {}, RouteDecision)
    client.close()
