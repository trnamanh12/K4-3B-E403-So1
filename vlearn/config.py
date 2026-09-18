import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


@dataclass(frozen=True)
class Settings:
    data_dir: Path = Path("data/vlearn-pack")
    artifacts_dir: Path = Path("artifacts")
    api_key: str = ""
    base_url: str = "https://openrouter.ai/api/v1"
    embedding_model: str = "liquid/lfm-2.5-embedding-350m:free"
    embedding_dimensions: int | None = None
    embedding_revision: str = "1"
    chat_model: str = "google/gemini-3.5-flash-lite"
    chat_base_url: str = ""
    chat_api_key: str = ""
    timeout: float = 60
    max_retries: int = 3
    batch_size: int = 32
    document_input_type: str = ""
    query_input_type: str = ""
    document_prefix: str = "document: "
    query_prefix: str = "query: "
    tokenizer: str = "auto"
    chunk_tokens: int = 360
    chunk_overlap: int = 40
    context_tokens: int = 6000
    retrieval_k: int = 8
    candidate_k: int = 20
    rerank: bool = False
    lesson_map: Path | None = None
    review_file: Path | None = None
    qdrant_url: str = ""
    qdrant_api_key: str = ""
    api_token: str = ""

    def __post_init__(self):
        if not 0 <= self.chunk_overlap < self.chunk_tokens:
            raise ValueError("RAG_CHUNK_OVERLAP must be >= 0 and smaller than RAG_CHUNK_TOKENS")
        if min(self.batch_size, self.context_tokens, self.retrieval_k, self.candidate_k) < 1:
            raise ValueError("Batch size, context budget and retrieval limits must be positive")
        if self.timeout <= 0 or self.max_retries < 0:
            raise ValueError("Invalid timeout/retry configuration")
        if self.embedding_dimensions is not None and self.embedding_dimensions < 1:
            raise ValueError("Embedding dimensions must be positive")
        if not self.base_url.startswith("https://"):
            raise ValueError("OpenRouter base URL must use HTTPS")
        if self.chat_base_url and not self.chat_base_url.startswith("https://"):
            raise ValueError("Chat base URL must use HTTPS")

    @classmethod
    def from_env(cls):
        load_dotenv(Path.cwd() / ".env", override=False)
        env = os.getenv
        model = env("OPENROUTER_EMBEDDING_MODEL", "liquid/lfm-2.5-embedding-350m:free")
        liquid = model.startswith("liquid/lfm-2.5-embedding")
        gemini_key = env("GEMINI_API_KEY", "")
        gemini_model = env("GEMINI_MODEL", "")
        chat_base_url = env("OPENROUTER_CHAT_BASE_URL", env("CHAT_BASE_URL", ""))
        chat_api_key = env("OPENROUTER_CHAT_API_KEY", env("CHAT_API_KEY", ""))
        chat_model = env("OPENROUTER_CHAT_MODEL", "")

        if gemini_key:
            chat_api_key = chat_api_key or gemini_key
            if not chat_base_url:
                chat_base_url = "https://generativelanguage.googleapis.com/v1beta/openai"
            if gemini_model:
                chat_model = gemini_model
            elif not chat_model:
                chat_model = "gemini-3.5-flash-lite"
            if "googleapis.com" in chat_base_url:
                chat_model = chat_model.removeprefix("google/")
        else:
            chat_model = chat_model or "gemini-3.5-flash-lite"

        return cls(
            data_dir=Path(env("RAG_DATA_DIR", "data/vlearn-pack")),
            artifacts_dir=Path(env("RAG_ARTIFACTS_DIR", "artifacts")),
            api_key=env("OPENROUTER_API_KEY", ""),
            base_url=env("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/"),
            embedding_model=model,
            embedding_dimensions=int(env("OPENROUTER_EMBEDDING_DIMENSIONS"))
            if env("OPENROUTER_EMBEDDING_DIMENSIONS") else None,
            embedding_revision=env("OPENROUTER_EMBEDDING_REVISION", "1"),
            chat_model=chat_model,
            chat_base_url=chat_base_url.rstrip("/"),
            chat_api_key=chat_api_key,
            timeout=float(env("OPENROUTER_TIMEOUT", "60")),
            max_retries=int(env("OPENROUTER_MAX_RETRIES", "3")),
            batch_size=int(env("OPENROUTER_BATCH_SIZE", "32")),
            document_input_type=env("OPENROUTER_DOCUMENT_INPUT_TYPE", ""),
            query_input_type=env("OPENROUTER_QUERY_INPUT_TYPE", ""),
            document_prefix=env("OPENROUTER_DOCUMENT_PREFIX", "document: " if liquid else ""),
            query_prefix=env("OPENROUTER_QUERY_PREFIX", "query: " if liquid else ""),
            tokenizer=env("RAG_TOKENIZER", "auto"),
            chunk_tokens=int(env("RAG_CHUNK_TOKENS", "360")),
            chunk_overlap=int(env("RAG_CHUNK_OVERLAP", "40")),
            context_tokens=int(env("RAG_CONTEXT_TOKENS", "6000")),
            retrieval_k=int(env("RAG_RETRIEVAL_K", "8")),
            candidate_k=int(env("RAG_CANDIDATE_K", "20")),
            rerank=env("RAG_RERANK", "false").lower() == "true",
            lesson_map=Path(env("RAG_LESSON_MAP")) if env("RAG_LESSON_MAP") else None,
            review_file=Path(env("RAG_REVIEW_FILE")) if env("RAG_REVIEW_FILE") else None,
            qdrant_url=env("QDRANT_URL", ""), qdrant_api_key=env("QDRANT_API_KEY", ""),
            api_token=env("RAG_API_TOKEN", ""),
        )

    def embedding_signature(self):
        return {key: getattr(self, key) for key in (
            "base_url", "embedding_model", "embedding_dimensions", "embedding_revision",
            "document_input_type", "query_input_type", "document_prefix", "query_prefix",
        )}
