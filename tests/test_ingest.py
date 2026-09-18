from dataclasses import replace

import pymupdf

from vlearn.ingest import parse_pdf, parse_transcript, prepare
from vlearn.store import Store
from vlearn.text import TokenCounter, split_spans


def test_transcript_heading_does_not_attach_to_previous_segment(tmp_path):
    path = tmp_path / "transcript.md"
    path.write_text("# Title\n## First\n\n**[T01-001]** Hello.\n\n## Second\n\n"
                    "**[T01-002]** [học viên]: Why?\n\n**[T01-003]** [không nghe rõ] End.")
    units = parse_transcript(path, {"id": "transcript", "version": "v1", "lesson_id": "day-1"})
    assert [u["id"] for u in units] == ["T01-001", "T01-002", "T01-003"]
    assert units[0]["text"] == "Hello."
    assert units[1]["section_title"] == "Second"
    assert not units[1]["evidence_eligible"]
    assert units[2]["has_unclear_span"]
    assert units[1]["previous_id"] == "T01-001"


def test_pdf_page_label_watermark_and_title(tmp_path):
    path = tmp_path / "slide.pdf"
    pdf = pymupdf.open()
    page = pdf.new_page(width=960, height=540)
    page.insert_text((50, 160), "Body content contains enough words to be useful as source evidence.")
    page.insert_text((20, 40), "Important title", fontsize=24)
    page.insert_text((20, 520), "DAY 02 · 55 / 83")
    page.insert_text((800, 480), "AI IN ACTION - HACKATHON", rotate=90)
    pdf.save(path)
    pdf.close()
    unit = parse_pdf(path, {"id": "slide", "version": "v1", "lesson_id": "day-2"})[0]
    assert unit["pdf_page"] == 1
    assert unit["printed_slide_label"] == "55 / 83"
    assert unit["section_title"] == "Important title"
    assert "HACKATHON" not in unit["text"]
    assert unit["text"].startswith("Important title")
    assert unit["watermarks_removed"] == 1


def test_unicode_chunk_offsets_cover_every_nonspace_character(settings):
    text = "Tiếng Việt có dấu 🧠. " * 50
    counter = TokenCounter(settings)
    spans = list(split_spans(text, counter, 120, 20))
    covered = set()
    for start, end in spans:
        assert counter.count(text[start:end]) <= 120
        covered.update(range(start, end))
    assert all(i in covered for i, char in enumerate(text) if not char.isspace())
    assert len(spans) > 5


def test_prepare_idempotent_and_version_changes(settings):
    directory = settings.data_dir / "transcript"
    directory.mkdir(parents=True)
    path = directory / "transcript-01-clean.md"
    path.write_text("## Heading\n\n**[T01-001]** First source passage with enough text.")
    first = prepare(settings)
    second = prepare(settings)
    assert first["snapshot_id"] == second["snapshot_id"]
    store = Store(settings.artifacts_dir)
    assert len(store.records("units", first["snapshot_id"])) == 1
    path.write_text("## Heading\n\n**[T01-001]** A revised source passage.")
    third = prepare(settings)
    assert third["snapshot_id"] != first["snapshot_id"]
    assert store.records("units", first["snapshot_id"])[0]["text"].startswith("First")
    resized = prepare(replace(settings, chunk_tokens=100))
    assert resized["snapshot_id"] != third["snapshot_id"]
