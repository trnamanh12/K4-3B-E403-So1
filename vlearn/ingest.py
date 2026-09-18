import hashlib
import json
import re
import shutil
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

import pymupdf
from filelock import FileLock

from .config import digest
from .store import Store
from .text import TokenCounter, normalize, split_spans

PIPELINE_VERSION = "parse-chunk-v2"
DEFAULT_LESSONS = {"d1-slide-hackathon": "day-1", "d2-slide-hackathon": "day-2",
                   "transcript-01-clean": "day-2", "transcript-04-clean": "day-1"}


def parse_transcript(path: Path, document):
    content = normalize(path.read_text(encoding="utf-8"))
    events = list(re.finditer(r"^##\s+(.+)$|^\*\*\[(T\d{2}-\d{3})\]\*\*\s*", content, re.M))
    heading, result = "", []
    for i, event in enumerate(events):
        if event.group(1):
            heading = event.group(1).strip()
            continue
        text = content[event.end():events[i+1].start() if i+1 < len(events) else len(content)].strip()
        if not text:
            raise ValueError(f"Empty transcript segment: {event.group(2)}")
        lower = text.lower()
        kind = "lecture"
        if lower.startswith(("[học viên]", "[hv]")):
            kind = "student_speech"
        elif lower.startswith("[hoạt động lớp:"):
            kind = "class_activity"
        elif any(x in heading.lower() for x in ("điểm danh", "giới thiệu học viên", "ổn định lớp")):
            kind = "administrative"
        result.append({
            "id": event.group(2), "document_id": document["id"], "document_version": document["version"],
            "lesson_id": document["lesson_id"], "source_type": "transcript", "section_title": heading,
            "order": len(result), "text": text, "raw_text": text, "pdf_page": None,
            "printed_slide_label": None, "segment_id": event.group(2), "blocks": [],
            "content_kind": kind, "has_unclear_span": "[không nghe rõ]" in text,
            "quality_flags": ["unclear_audio"] if "[không nghe rõ]" in text else [],
            "evidence_eligible": kind == "lecture", "parse_status": "text_extracted",
        })
    if not result or len({x["id"] for x in result}) != len(result):
        raise ValueError(f"Transcript IDs missing or duplicated in {path.name}")
    for i, unit in enumerate(result):
        unit["previous_id"] = result[i-1]["id"] if i else None
        unit["next_id"] = result[i+1]["id"] if i+1 < len(result) else None
    return result


def parse_pdf(path: Path, document):
    result = []
    with pymupdf.open(path) as pdf:
        for page in pdf:
            blocks, parts, removed = [], [], 0
            title_candidates = []
            # Preserve PDF content order (these decks follow DOM order), not line-wise column interleaving.
            data = page.get_text("dict", flags=pymupdf.TEXTFLAGS_DICT & ~pymupdf.TEXT_PRESERVE_IMAGES)
            label = None
            ordered_blocks = sorted(enumerate(data["blocks"]),
                                    key=lambda item: (item[1]["bbox"][1] >= page.rect.height * .15, item[0]))
            for _, block in ordered_blocks:
                lines = []
                for line in block.get("lines", []):
                    text = normalize("".join(span["text"] for span in line["spans"]))
                    if abs(line["dir"][1]) > .1 and "HACKATHON" in text.upper():
                        removed += 1
                        continue
                    if page.rect.height * .9 < line["bbox"][1]:
                        match = re.search(r"DAY\s+\d+\s*[·•]\s*(\d+)\s*/\s*(\d+)", text, re.I)
                        if match:
                            label = f"{match[1]} / {match[2]}"
                            continue
                    if text:
                        lines.append(text)
                        if len(text) > 8 and line["bbox"][1] < page.rect.height * .5:
                            title_candidates.append((max(s["size"] for s in line["spans"]),
                                                     -line["bbox"][1], text))
                if lines:
                    text = "\n".join(lines)
                    start = sum(len(p) + 2 for p in parts)
                    blocks.append({"bbox": list(block["bbox"]), "start": start, "end": start+len(text)})
                    parts.append(text)
            text = "\n\n".join(parts)
            image_area = sum(pymupdf.Rect(i["bbox"]).get_area() for i in page.get_image_info())
            visual_risk = image_area / page.rect.get_area() > .2
            flags = []
            if visual_risk:
                flags.append("visual_content_needs_review")
            if len(text) < 80:
                flags.append("little_text_needs_review")
            result.append({
                "id": f"{document['id']}:p{page.number+1:03d}", "document_id": document["id"],
                "document_version": document["version"], "lesson_id": document["lesson_id"],
                "source_type": "slide", "order": page.number,
                "section_title": max(title_candidates)[2] if title_candidates else (parts[0] if parts else ""),
                "text": text, "raw_text": page.get_text(), "pdf_page": page.number+1,
                "printed_slide_label": label, "segment_id": None, "blocks": blocks,
                "content_kind": "lecture", "has_unclear_span": False,
                "quality_flags": flags, "watermarks_removed": removed,
                "evidence_eligible": bool(text) and not flags, "parse_status": "text_extracted",
            })
    return result


def build_chunks(units, settings, counter):
    chunks = []
    for unit in units:
        if not unit["text"]:
            continue
        # Metadata prefix is capped separately and included in the context-limit check at index time.
        title = counter.truncate(unit["section_title"], 32)
        for start, end in split_spans(unit["text"], counter, settings.chunk_tokens, settings.chunk_overlap):
            text = unit["text"][start:end]
            identity = [unit["id"], unit["document_version"], start, end, PIPELINE_VERSION,
                        counter.fingerprint, settings.chunk_tokens, settings.chunk_overlap]
            chunks.append({
                "id": str(uuid5(NAMESPACE_URL, digest(identity))), "unit_id": unit["id"],
                "document_id": unit["document_id"], "document_version": unit["document_version"],
                "lesson_id": unit["lesson_id"], "source_type": unit["source_type"],
                "pdf_page": unit["pdf_page"], "segment_id": unit["segment_id"],
                "start": start, "end": end, "text": text,
                "embedding_text": (title + "\n" + text) if title else text,
                "token_count": counter.count(text), "evidence_eligible": unit["evidence_eligible"],
            })
    return chunks


def prepare(settings):
    store = Store(settings.artifacts_dir)
    with FileLock(str(settings.artifacts_dir / "ingestion.lock"), timeout=1):
        counter = TokenCounter(settings)
        paths = sorted((settings.data_dir / "slides").glob("*.pdf"))
        paths += sorted((settings.data_dir / "transcript").glob("transcript-*-clean.md"))
        if not paths:
            raise ValueError("No slide PDFs or transcript files found in RAG_DATA_DIR")
        lessons = DEFAULT_LESSONS.copy()
        if settings.lesson_map:
            custom = json.loads(settings.lesson_map.read_text())
            if not isinstance(custom, dict) or any(v is not None and not isinstance(v, str) for v in custom.values()):
                raise ValueError("Lesson mapping must be an object of document_id to lesson_id or null")
            lessons.update(custom)
        reviews = json.loads(settings.review_file.read_text()) if settings.review_file else {}
        docs, units = [], []
        for path in paths:
            version = hashlib.sha256(path.read_bytes()).hexdigest()
            archived = settings.artifacts_dir / "sources" / (version + path.suffix)
            archived.parent.mkdir(exist_ok=True)
            if not archived.exists():
                shutil.copyfile(path, archived)
            doc = {"id": path.stem, "version": version, "filename": path.name,
                   "archive_path": str(archived.resolve()), "lesson_id": lessons.get(path.stem),
                   "source_type": "slide" if path.suffix == ".pdf" else "transcript"}
            parsed = parse_pdf(path, doc) if path.suffix == ".pdf" else parse_transcript(path, doc)
            doc["unit_count"] = len(parsed)
            docs.append(doc)
            units.extend(parsed)
        if len({x["id"] for x in units}) != len(units):
            raise ValueError("Duplicate source unit IDs across documents")
        unknown_reviews = set(reviews) - {u["id"] for u in units}
        if unknown_reviews:
            raise ValueError("Review file contains unknown source units")
        for unit in units:
            review = reviews.get(unit["id"])
            if review:
                if review.get("document_version") != unit["document_version"]:
                    raise ValueError(f"Review is stale for {unit['id']}")
                if not isinstance(review.get("evidence_eligible"), bool):
                    raise ValueError("Review requires boolean evidence_eligible")
                if "text" in review:
                    if not isinstance(review["text"], str) or not review["text"].strip():
                        raise ValueError("Reviewed text cannot be empty")
                    unit["text"] = normalize(review["text"])
                    unit["blocks"] = []  # Old layout offsets no longer match a corrected transcription.
                unit["evidence_eligible"] = review["evidence_eligible"]
                unit["parse_status"] = "human_reviewed"
        chunks = build_chunks(units, settings, counter)
        config = {"pipeline_version": PIPELINE_VERSION, "tokenizer": counter.fingerprint,
                  "chunk_tokens": settings.chunk_tokens, "chunk_overlap": settings.chunk_overlap,
                  "embedding": settings.embedding_signature(),
                  "sources": [(d["id"], d["version"], d["lesson_id"]) for d in docs], "reviews": reviews}
        sid = digest(config)[:24]
        store.save_snapshot(sid, config, docs, units, chunks)
        out = settings.artifacts_dir / "snapshots" / sid
        out.mkdir(parents=True, exist_ok=True)
        for filename, records in (("manifest", docs), ("source_units", units), ("chunks", chunks)):
            (out / (filename + ".jsonl")).write_text(
                "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records), encoding="utf-8")
        report = {"snapshot_id": sid, "documents": len(docs), "source_units": len(units),
                  "slide_pages": sum(u["source_type"] == "slide" for u in units),
                  "transcript_segments": sum(u["source_type"] == "transcript" for u in units),
                  "chunks": len(chunks), "eligible_chunks": sum(c["evidence_eligible"] for c in chunks),
                  "max_chunk_tokens": max((c["token_count"] for c in chunks), default=0),
                  "tokenizer": counter.fingerprint,
                  "needs_review": [{"unit_id": u["id"], "flags": u["quality_flags"],
                                    "eligible": u["evidence_eligible"]}
                                   for u in units if u["quality_flags"]],
                  "artifact_directory": str(out)}
        (out / "parse_quality_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
        return report
