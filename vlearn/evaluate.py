import json
import time
from pathlib import Path

from .models import Query, Selection
from .retrieval import Retriever
from .store import Store, now
from .tutor import Tutor


def evaluate_retrieval(settings, cases_path: Path, sid, backend="bm25", k=10):
    cases = json.loads(cases_path.read_text())
    service = Retriever(settings)
    results = []
    try:
        for case in cases:
            gold = set(case["expected_sources"])
            if not gold:
                raise ValueError("Retrieval cases require at least one expected source")
            for uid in gold:
                unit = service.store.record("units", sid, uid)
                if not unit["evidence_eligible"] or unit["lesson_id"] != case["lesson_id"]:
                    raise ValueError(f"{case['id']} has ineligible or out-of-scope gold evidence")
            query = Query(question=case["question"], mode="LESSON_EXPANDED", snapshot_id=sid,
                          lesson_id=case["lesson_id"])
            started = time.monotonic()
            # Gold sources never enter the search request.
            retrieved = service.search(query, backend, top_k=k)
            ranked = list(dict.fromkeys(e["unit_id"] for e in retrieved["evidence"]))
            positions = [i+1 for i, uid in enumerate(ranked) if uid in gold]
            results.append({"id": case["id"], "retrieved_sources": ranked, "gold_sources": sorted(gold),
                            "recall": len(gold.intersection(ranked))/len(gold),
                            "reciprocal_rank": 1/min(positions) if positions else 0,
                            "complete_evidence": gold.issubset(ranked),
                            "seconds": round(time.monotonic()-started, 4)})
    finally:
        service.close()
    if not results:
        raise ValueError("Empty evaluation set")
    return {"created": now(), "snapshot_id": sid, "backend": backend, "k": k,
            "embedding_model": settings.embedding_model if backend != "bm25" else None,
            "cases": len(results), "recall_at_k": sum(r["recall"] for r in results)/len(results),
            "mrr_at_k": sum(r["reciprocal_rank"] for r in results)/len(results),
            "complete_evidence_cases": sum(r["complete_evidence"] for r in results),
            "note": "Seed development set, not a held-out benchmark. Gold lists designate target pages; "
                    "other relevant transcript passages may not yet be annotated.", "results": results}


def evaluate_e2e(settings, cases_path: Path, sid):
    service = Tutor(settings)
    results = []
    try:
        for case in json.loads(cases_path.read_text()):
            query = Query(question=case["question"], snapshot_id=sid, mode=case["mode"],
                          lesson_id=case.get("lesson_id"),
                          selections=[Selection(unit_id=u) for u in case.get("unit_ids", [])])
            started = time.monotonic()
            try:
                response = service.ask(query)
                citations = response["citations"]
                locator_valid = True
                for citation in citations:
                    unit = service.store.record("units", sid, citation["unit_id"])
                    locator_valid &= (unit["document_version"] == citation["document_version"] and
                                      unit["text"][citation["start"]:citation["end"]] == citation["quote"])
                grounded = response["final_status"] == "GROUNDED"
                passed = (response["final_status"] == case["expected_status"] and locator_valid
                          and (bool(citations) if grounded else not citations))
                results.append({"id": case["id"], "expected_status": case["expected_status"],
                                "actual_status": response["final_status"], "passed": passed,
                                "locator_valid": locator_valid, "trace_id": response["trace_id"],
                                "seconds": round(time.monotonic()-started, 3)})
            except Exception as exc:
                results.append({"id": case["id"], "passed": False, "actual_status": "ERROR",
                                "error_type": type(exc).__name__})
    finally:
        service.close()
    return {"created": now(), "snapshot_id": sid, "provider": "openrouter",
            "chat_model": settings.chat_model, "embedding_model": settings.embedding_model,
            "cases": len(results), "passed": sum(r["passed"] for r in results),
            "note": "Checks routes and citation locators. Semantic claim support still needs independent human audit.",
            "results": results}


def main():
    import argparse

    from .config import Settings
    parser = argparse.ArgumentParser(description="Evaluate the real VLearn retrieval/tutor pipeline")
    parser.add_argument("kind", choices=["retrieval", "e2e"])
    parser.add_argument("--snapshot")
    parser.add_argument("--cases", type=Path)
    parser.add_argument("--backend", choices=["bm25", "dense", "hybrid"], default="bm25")
    parser.add_argument("--k", type=int, default=10)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.k < 1:
        parser.error("--k must be positive")
    settings = Settings.from_env()
    sid = args.snapshot or Store(settings.artifacts_dir).snapshot()["id"]
    path = args.cases or Path("eval") / ("retrieval_cases.json" if args.kind == "retrieval" else "e2e_cases.json")
    report = evaluate_retrieval(settings, path, sid, args.backend, args.k) if args.kind == "retrieval" else evaluate_e2e(settings, path, sid)
    target = args.output or settings.artifacts_dir / "eval" / (args.kind + "_" + args.backend + ".json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps({k: v for k, v in report.items() if k != "results"}, ensure_ascii=False, indent=2))
    print("Report:", target)
    return 1 if args.kind == "e2e" and report["passed"] < report["cases"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
