from dataclasses import replace

import pytest

from vlearn.config import Settings
from vlearn.store import Store


@pytest.fixture
def settings(tmp_path):
    return Settings(artifacts_dir=tmp_path / "artifacts", data_dir=tmp_path / "data",
                    embedding_model="test/embedding", api_key="test-key", tokenizer="bytes",
                    document_prefix="document: ", query_prefix="query: ", max_retries=0,
                    chunk_tokens=120, chunk_overlap=15)


@pytest.fixture
def corpus(settings):
    store = Store(settings.artifacts_dir)
    units = []
    for uid, lesson, text in (
        ("T01-001", "day-1", "Attention lets a token use information from other tokens."),
        ("T01-002", "day-1", "Temperature changes the distribution of token probabilities."),
        ("T02-001", "day-2", "Attention is a keyword on a different lesson. This source must not leak."),
    ):
        units.append({"id": uid, "document_id": lesson, "document_version": "version-1",
                      "source_type": "transcript", "text": text, "raw_text": text,
                      "lesson_id": lesson, "pdf_page": None, "segment_id": uid,
                      "section_title": "Lesson", "printed_slide_label": None,
                      "quality_flags": [], "evidence_eligible": True})
    from vlearn.ingest import build_chunks
    from vlearn.text import TokenCounter
    counter = TokenCounter(settings)
    chunks = build_chunks(units, settings, counter)
    docs = [{"id": day, "version": "version-1", "filename": day+".md", "lesson_id": day,
             "source_type": "transcript", "unit_count": 2} for day in ("day-1", "day-2")]
    store.save_snapshot("fixture", {"embedding": settings.embedding_signature(), "tokenizer": counter.fingerprint},
                        docs, units, chunks)
    return store


@pytest.fixture
def no_key(settings):
    return replace(settings, api_key="")
