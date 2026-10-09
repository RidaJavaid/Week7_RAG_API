"""
Week 7 Master Runner
====================
Runs all verification steps in sequence and writes a summary.
Steps:
  1. Register Week 6 documents into indexed_documents.json
  2. Run all pytest suites and save test output
  3. Run optimised benchmark (FAST_RERANK=1) and save results
  4. Run quality evaluation on the real 50-Q set
  5. Write updated summary

Usage:
  python run_all_week7.py
"""

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT   = Path(__file__).resolve().parent
PYTHON = ROOT / "venv" / "Scripts" / "python.exe"
OUT    = ROOT / "Week7_Submission"

def run(label, args, extra_env=None, capture_output_path=None):
    env = {**os.environ}
    if extra_env:
        env.update(extra_env)
    print(f"\n{'='*55}\n{label}\n{'='*55}")
    result = subprocess.run(
        [str(PYTHON)] + args,
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        env=env,
    )
    combined = result.stdout + result.stderr
    print(combined[-3000:] if len(combined) > 3000 else combined)
    if capture_output_path:
        Path(capture_output_path).write_text(combined, encoding="utf-8")
    return result.returncode, combined

def main():
    # ── 1. Register Week 6 docs ────────────────────────────────────────────────
    rc, out = run("STEP 1: Register Week 6 documents",
                  ["register_week6_docs.py"])

    # ── 2. Run all tests ───────────────────────────────────────────────────────
    rc, out = run(
        "STEP 2: pytest — ingestion + cost + auto-ingest",
        ["-m", "pytest",
         "tests/test_ingestion_day3.py",
         "tests/test_cost_tracker.py",
         "tests/test_auto_ingest.py",
         "-v", "--tb=short", "--no-header"],
        capture_output_path=ROOT / "test_output.txt",
    )
    test_rc = rc
    print(f"\npytest exit code: {rc}")

    # ── 3. Optimised benchmark ─────────────────────────────────────────────────
    rc, out = run(
        "STEP 3: Benchmark (FAST_RERANK=1)",
        ["run_benchmark.py"],
        extra_env={"FAST_RERANK": "1"},
        capture_output_path=ROOT / "benchmark_output.txt",
    )

    # ── 4. Quality evaluation (50 questions) ───────────────────────────────────
    rc, out = run(
        "STEP 4: Quality evaluation (50 questions, FAST_RERANK=1)",
        ["evaluate_quality.py",
         "--output", str(OUT / "Day5" / "quality_report.json")],
        extra_env={"FAST_RERANK": "1"},
        capture_output_path=ROOT / "quality_output.txt",
    )
    quality_rc = rc

    # ── 5. Print summary ───────────────────────────────────────────────────────
    print("\n" + "="*55)
    print("MASTER RUN SUMMARY")
    print("="*55)

    # Tests
    test_output = Path(ROOT / "test_output.txt").read_text(encoding="utf-8")
    if "passed" in test_output:
        import re
        m = re.search(r"(\d+) passed", test_output)
        s = re.search(r"(\d+) skipped", test_output)
        passed = m.group(0) if m else "?"
        skipped = s.group(0) if s else ""
        print(f"Tests:   {passed} {skipped}")
    else:
        print("Tests:   see test_output.txt")

    # Benchmark
    bench_json = OUT / "Day1" / "benchmark_summary.json"
    if bench_json.exists():
        b = json.loads(bench_json.read_text())
        s = b.get("total_latency_stats", {})
        print(f"Benchmark: median={s.get('median','?')}s  P95={s.get('p95','?')}s  slowest={b.get('slowest_stage','?')}")

    # Quality
    qual_json = OUT / "Day5" / "quality_report.json"
    if qual_json.exists():
        q = json.loads(qual_json.read_text())
        print(f"Quality: mean={q.get('mean_score','?')} threshold={q.get('threshold','?')} passed={q.get('passed','?')}")

    print(f"\ntest_rc={test_rc}  quality_rc={quality_rc}")
    print("="*55)

if __name__ == "__main__":
    main()
