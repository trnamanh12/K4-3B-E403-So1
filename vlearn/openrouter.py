import json
import math
import time

import httpx
from pydantic import ValidationError

from .config import digest


class ProviderError(RuntimeError):
    pass


class OpenRouter:
    def __init__(self, settings, store=None, counter=None, transport=None):
        self.settings, self.store, self.counter = settings, store, counter
        self.client = httpx.Client(base_url=settings.base_url + "/", timeout=settings.timeout,
                                   transport=transport)
        chat_base = (settings.chat_base_url or settings.base_url).rstrip("/") + "/"
        self.chat_client = (self.client if (chat_base == (settings.base_url.rstrip("/") + "/")
                                            and not settings.chat_api_key)
                            else httpx.Client(base_url=chat_base, timeout=settings.timeout,
                                              transport=transport))
        self.usage = []

    def close(self):
        self.client.close()
        if self.chat_client is not self.client:
            self.chat_client.close()

    def request(self, method, path, body=None, require_key=True, client=None, api_key=None):
        target_client = client or self.client
        key = api_key if api_key is not None else self.settings.api_key
        if require_key and not key:
            raise ProviderError("Set OPENROUTER_API_KEY in .env before calling OpenRouter")
        headers = {"X-Title": "VLearn RAG"}
        if key:
            headers["Authorization"] = "Bearer " + key
        max_attempts = max(self.settings.max_retries, 20)
        for attempt in range(max_attempts + 1):
            try:
                response = target_client.request(method, path, json=body, headers=headers)
            except httpx.TransportError:
                if attempt == self.settings.max_retries:
                    raise ProviderError("OpenRouter connection failed or timed out") from None
                time.sleep(min(2 ** attempt, 15))
                continue
            if response.status_code == 429 or response.status_code >= 500:
                # Always retry on rate limits (up to 20 attempts) with proper wait time
                if attempt < max(self.settings.max_retries, 20):
                    delay = 15.0  # default safe wait for rate limit
                    try:
                        if "retry-after" in response.headers:
                            delay = float(response.headers.get("retry-after"))
                        else:
                            resp_json = response.json()
                            for detail in resp_json.get("error", {}).get("details", []):
                                if "retryDelay" in detail:
                                    delay = float(detail["retryDelay"].rstrip("s"))
                    except Exception:
                        pass
                    delay = max(delay, 15.0)
                    time.sleep(min(delay, 60))
                    continue
            if not response.is_success:
                # Do not include arbitrary upstream bodies: they may echo documents or credentials.
                # Recognize a small allowlist of provider/account errors that need an actionable fix.
                upstream_message = ""
                try:
                    upstream_error = response.json().get("error", {})
                    if isinstance(upstream_error, dict):
                        upstream_message = str(upstream_error.get("message", ""))
                except (ValueError, AttributeError):
                    pass
                if "Free model training violation" in upstream_message:
                    raise ProviderError(
                        "OpenRouter privacy settings exclude this free training-data endpoint. "
                        "Choose an embedding model compatible with the account data policy, or explicitly "
                        "change the account privacy setting before retrying."
                    )
                if "free-models-per-day" in upstream_message:
                    raise ProviderError(
                        "OpenRouter's daily free-model request quota is exhausted. Cached embeddings are safe; "
                        "retry after the daily reset or increase the account's free-model quota."
                    )
                hint = {401: "check API key", 402: "check credits", 429: "rate limit; retry later",
                        400: "check model parameters and input length", 404: "check model ID"}
                raise ProviderError(f"OpenRouter HTTP {response.status_code}: "
                                    + hint.get(response.status_code, "upstream request failed"))
            try:
                data = response.json()
            except ValueError:
                raise ProviderError("OpenRouter returned invalid JSON") from None
            if not isinstance(data, dict) or data.get("error"):
                raise ProviderError("OpenRouter returned an error payload")
            if data.get("usage"):
                self.usage.append({"model": body.get("model") if body else None, "usage": data["usage"]})
            return data
        raise ProviderError("OpenRouter request exhausted retries")

    def models(self):
        return self.request("GET", "embeddings/models", require_key=False)["data"]

    def model_info(self):
        if self.settings.embedding_model.startswith("gemini-") or "gemini" in self.settings.embedding_model:
            return {"id": self.settings.embedding_model, "context_length": 2048, "canonical_slug": self.settings.embedding_model, "native_dimensions": 3072}
        for model in self.models():
            if model["id"] == self.settings.embedding_model:
                return model
        raise ProviderError("Configured embedding model is absent from OpenRouter's embeddings catalog")

    def embed(self, texts, kind="document", context_limit=None):
        if kind not in {"document", "query"}:
            raise ValueError("Embedding kind must be document or query")
        if not texts:
            return []
        prefix = getattr(self.settings, kind + "_prefix")
        input_type = getattr(self.settings, kind + "_input_type")
        inputs = [prefix + text for text in texts]
        if any(not text.strip() for text in texts):
            raise ValueError("Cannot embed empty text")
        if context_limit and self.counter:
            if any(self.counter.count(x) > context_limit for x in inputs):
                raise ValueError("Embedding input exceeds model context; reduce chunk size or shorten query")
        keys = [digest({"signature": self.settings.embedding_signature(), "kind": kind, "text": x})
                for x in inputs]
        vectors = [self.store.cached_embedding(k) if self.store else None for k in keys]
        missing = [i for i, vector in enumerate(vectors) if vector is None]
        for start in range(0, len(missing), self.settings.batch_size):
            indexes = missing[start:start+self.settings.batch_size]
            body = {"model": self.settings.embedding_model, "input": [inputs[i] for i in indexes],
                    "encoding_format": "float"}
            if self.settings.embedding_dimensions is not None:
                body["dimensions"] = self.settings.embedding_dimensions
            if input_type:
                body["input_type"] = input_type
            use_gemini = self.settings.embedding_model.startswith("gemini-") and bool(self.settings.chat_api_key)
            target_client = self.chat_client if use_gemini else self.client
            target_key = self.settings.chat_api_key if use_gemini else self.settings.api_key
            data = self.request("POST", "embeddings", body, client=target_client, api_key=target_key)
            rows = data.get("data", [])
            if len(rows) != len(indexes):
                raise ProviderError("Embedding response item count does not match input count")
            if any("index" not in r or r.get("index") is None for r in rows):
                batch = [r.get("embedding") for r in rows]
            else:
                if sorted(r.get("index", -1) for r in rows) != list(range(len(indexes))):
                    raise ProviderError("Embedding response has duplicate or out-of-order input indexes")
                batch = [r.get("embedding") for r in sorted(rows, key=lambda r: r["index"])]
            self.validate_vectors(batch)
            for i, vector in zip(indexes, batch, strict=True):
                vectors[i] = vector
                if self.store:
                    self.store.cache_embedding(keys[i], vector)
        self.validate_vectors(vectors)
        return vectors

    def validate_vectors(self, vectors):
        dims = self.settings.embedding_dimensions
        for vector in vectors:
            if not isinstance(vector, list) or not vector:
                raise ProviderError("Empty or malformed embedding vector")
            if dims is None:
                dims = len(vector)
            if len(vector) != dims or any(type(v) not in (int, float) or not math.isfinite(v) for v in vector):
                raise ProviderError("Embedding dimensions or values are invalid")
            if not any(v != 0 for v in vector):
                raise ProviderError("Embedding must not be a zero vector")

    def structured(self, system, payload, result_type):
        body = {
            "model": self.settings.chat_model,
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}],
            "temperature": 0,
            "max_tokens": 3000,
            "response_format": {"type": "json_schema", "json_schema": {
                "name": result_type.__name__, "strict": True, "schema": result_type.model_json_schema()}},
        }
        if "openrouter.ai" in str(self.chat_client.base_url):
            body["provider"] = {"require_parameters": True}
        data = self.request("POST", "chat/completions", body,
                            client=self.chat_client,
                            api_key=self.settings.chat_api_key or self.settings.api_key)
        try:
            choice = data["choices"][0]
            if choice.get("finish_reason") != "stop":
                raise ValueError("Incomplete output")
            return result_type.model_validate_json(choice["message"]["content"])
        except (KeyError, IndexError, TypeError, ValueError, ValidationError):
            raise ProviderError("Model returned incomplete or schema-invalid structured output") from None
