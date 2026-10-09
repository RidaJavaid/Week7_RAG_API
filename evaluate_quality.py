"""
Week 7 Day 5 Part A — Quality Evaluation
=========================================
Uses the evaluation set from eval_questions.json.
Computes a keyword-overlap quality score per answer.
Fails (exit 1) when score drops below QUALITY_THRESHOLD.

Usage:
  python evaluate_quality.py                     # normal run
  python evaluate_quality.py --regression        # with reranking disabled
  python evaluate_quality.py --output report.json
"""

import argparse
import json
import re
import sys
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent
EVAL_FILE = ROOT / "eval_questions.json"
QUALITY_THRESHOLD = 0.99  # REGRESSION INJECTION   # 40% keyword overlap minimum (documented threshold)


def tokenize(text: str) -> set:
    return set(re.findall(r"\w+", text.lower()))


def keyword_overlap_score(answer: str, reference: str) -> float:
    """Fraction of reference keywords present in the answer."""
    ref_tokens = tokenize(reference)
    if not ref_tokens:
        return 1.0
    ans_tokens = tokenize(answer)
    overlap = ref_tokens & ans_tokens
    return len(overlap) / len(ref_tokens)


def load_eval_set() -> list:
    if not EVAL_FILE.exists():
        print(
            "ERROR: eval_questions.json not found.\n"
            "The official Week 6 evaluation set (eval_questions.json) is required.\n"
            "Please place it at: " + str(EVAL_FILE)
        )
        sys.exit(2)
    return json.loads(EVAL_FILE.read_text(encoding="utf-8"))


def run_evaluation(disable_reranking: bool = False) -> dict:
    from rag import ask_rag, rebuild_index
    import rag

    rebuild_index()

    # Optional: patch reranker out for regression test
    original_reranker = None
    if disable_reranking:
        original_reranker = rag.reranker
        class _DummyReranker:
            def predict(self, pairs):
                return [0.0] * len(pairs)
        rag.reranker = _DummyReranker()
        print("[REGRESSION MODE] Reranking disabled.")

    questions = load_eval_set()
    results = []
    scores = []

    for i, item in enumerate(questions, 1):
        q = item["question"]
        ref = item.get("reference_answer", item.get("answer", ""))
        try:
            resp = ask_rag(q)
            answer = resp.get("answer", "")
        except Exception as exc:
            answer = ""
            print(f"  Q{i} ERROR: {exc}")

        score = keyword_overlap_score(answer, ref)
        scores.append(score)
        results.append({
            "id": i,
            "question": q,
            "reference": ref,
            "answer": answer,
            "score": round(score, 4),
        })
        print(f"  Q{i:2d}  score={score:.3f}  A: {answer[:80]}")

    # Restore reranker
    if original_reranker is not None:
        rag.reranker = original_reranker

    mean_score = sum(scores) / len(scores) if scores else 0.0
    passed = mean_score >= QUALITY_THRESHOLD

    report = {
        "mode": "regression_no_rerank" if disable_reranking else "normal",
        "num_questions": len(questions),
        "mean_score": round(mean_score, 4),
        "threshold": QUALITY_THRESHOLD,
        "passed": passed,
        "results": results,
    }
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--regression", action="store_true",
                        help="Disable reranking to test quality regression")
    parser.add_argument("--output", default=None,
                        help="JSON file to write results to")
    args = parser.parse_args()

    print("=" * 55)
    print("WEEK 7 DAY 5 — QUALITY EVALUATION")
    print("=" * 55)

    report = run_evaluation(disable_reranking=args.regression)

    print("\n" + "=" * 55)
    print(f"Mode          : {report['mode']}")
    print(f"Questions     : {report['num_questions']}")
    print(f"Mean score    : {report['mean_score']:.4f}")
    print(f"Threshold     : {report['threshold']:.4f}")
    print(f"RESULT        : {'PASSED' if report['passed'] else 'FAILED'}")
    print("=" * 55)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"Report saved -> {out}")

    sys.exit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
