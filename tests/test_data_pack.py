from pathlib import Path

import pytest

from vlearn.ingest import parse_pdf, parse_transcript

DATA = Path(__file__).resolve().parents[1] / "data" / "vlearn-pack"


@pytest.mark.skipif(not DATA.exists(), reason="Private data pack not present")
def test_real_pack_source_counts_watermarks_and_page_labels():
    expected = {1: 89, 2: 43, 3: 154, 4: 98, 5: 154, 6: 162}
    total = 0
    for number, count in expected.items():
        path = DATA / "transcript" / f"transcript-{number:02d}-clean.md"
        units = parse_transcript(path, {"id": path.stem, "version": "test", "lesson_id": None})
        assert len(units) == count
        total += len(units)
    assert total == 700
    for filename in ("d1-slide-hackathon.pdf", "d2-slide-hackathon.pdf"):
        path = DATA / "slides" / filename
        pages = parse_pdf(path, {"id": path.stem, "version": "test", "lesson_id": None})
        assert len(pages) == 29
        assert all("AI IN ACTION - HACKATHON" not in p["text"] for p in pages)
        if filename.startswith("d2"):
            assert pages[20]["printed_slide_label"] == "55 / 83"
            assert pages[20]["pdf_page"] == 21
            assert not pages[20]["evidence_eligible"]
            assert pages[5]["section_title"] == "Tìm bài toán AI ở đâu?"
