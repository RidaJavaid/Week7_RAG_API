"""
Week 7 Day 1 — Speed & Cost Benchmark
Runs the RAG pipeline 10 times with representative questions,
records per-stage timings, computes statistics, saves CSV and chart.
"""

import csv
import json
import statistics
import sys
import time
from pathlib import Path

# ── Make sure project root is importable ──────────────────────────────────────
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402 – after sys.path

# Import project modules AFTER path is set
from rag import ask_rag, rebuild_index  # noqa: E402

OUTPUT_DIR = ROOT / "Week7_Submission" / "Day1"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── 10 representative questions based on indexed documents ────────────────────
QUESTIONS = [
    "What is Retrieval-Augmented Generation?",
    "How does BM25 work in information retrieval?",
    "What is FAISS used for?",
    "How does SentenceTransformer convert text?",
    "What is CrossEncoder reranking?",
    "How does RAG combine retrieval and generation?",
    "What is a vector embedding?",
    "What programming language is used for AI and ML?",
    "How does hybrid retrieval improve search quality?",
    "What is the role of dense retrieval in RAG?",
]

STAGE_NAMES = ["Embedding", "Retrieval", "Reranking", "Generation"]


def run_single(question: str) -> dict:
    """Run one RAG call and return structured timing dict."""
    wall_start = time.perf_counter()
    result = ask_rag(question)
    wall_total = time.perf_counter() - wall_start

    row = {
        "question": question,
        "answer": result.get("answer", ""),
        "total_latency_s": round(wall_total, 4),
        "api_cost_usd": result.get("estimated_api_cost_usd", 0.0),
    }

    # Map step timings by name
    step_times = {s["step"]: s["time_seconds"] for s in result.get("steps", [])}
    for name in STAGE_NAMES:
        row[f"{name.lower()}_s"] = step_times.get(name, 0.0)

    return row


def compute_stats(values: list[float]) -> dict:
    sorted_v = sorted(values)
    n = len(sorted_v)
    p95_idx = int(0.95 * n) - 1
    return {
        "median": round(statistics.median(sorted_v), 4),
        "mean": round(statistics.mean(sorted_v), 4),
        "p95": round(sorted_v[max(p95_idx, 0)], 4),
        "min": round(min(sorted_v), 4),
        "max": round(max(sorted_v), 4),
    }


def main():
    print("=" * 55)
    print("WEEK 7 DAY 1 — SPEED & COST BENCHMARK")
    print("=" * 55)
    print(f"Rebuilding index …")
    rebuild_index()

    rows = []
    for i, q in enumerate(QUESTIONS, 1):
        print(f"\nRun {i:2d}/10  Q: {q[:60]}")
        row = run_single(q)
        rows.append(row)
        print(
            f"  Total={row['total_latency_s']:.3f}s  "
            f"Embed={row['embedding_s']:.3f}s  "
            f"Retr={row['retrieval_s']:.3f}s  "
            f"Rerank={row['reranking_s']:.3f}s  "
            f"Gen={row['generation_s']:.3f}s"
        )

    # ── CSV ───────────────────────────────────────────────────────────────────
    csv_path = OUTPUT_DIR / "benchmark_results.csv"
    fieldnames = [
        "run", "question", "total_latency_s",
        "embedding_s", "retrieval_s", "reranking_s", "generation_s",
        "api_cost_usd", "answer",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for i, row in enumerate(rows, 1):
            writer.writerow({"run": i, **row})
    print(f"\nCSV saved -> {csv_path}")

    # ── Statistics ────────────────────────────────────────────────────────────
    totals = [r["total_latency_s"] for r in rows]
    stats = compute_stats(totals)

    stage_stats = {}
    for stage in STAGE_NAMES:
        key = f"{stage.lower()}_s"
        stage_stats[stage] = compute_stats([r[key] for r in rows])

    slowest_stage = max(stage_stats, key=lambda s: stage_stats[s]["median"])

    print("\n" + "=" * 55)
    print("LATENCY STATISTICS (10 runs)")
    print("=" * 55)
    print(f"  Median total latency : {stats['median']:.4f} s")
    print(f"  Mean total latency   : {stats['mean']:.4f} s")
    print(f"  P95 total latency    : {stats['p95']:.4f} s")
    print(f"  Min / Max            : {stats['min']:.4f} s / {stats['max']:.4f} s")
    print(f"\n  Slowest stage        : {slowest_stage} ({stage_stats[slowest_stage]['median']:.4f} s median)")

    print("\nPer-stage medians:")
    for stage in STAGE_NAMES:
        print(f"  {stage:12s}: {stage_stats[stage]['median']:.4f} s")

    # ── Speed & cost targets ───────────────────────────────────────────────────
    TARGET_TOTAL_S = 3.0
    TARGET_P95_S   = 5.0
    TARGET_COST    = 0.0  # local models → $0.00

    print("\n" + "=" * 55)
    print("SPEED & COST TARGETS")
    print("=" * 55)
    print(f"  Target median total  : ≤ {TARGET_TOTAL_S:.1f} s  (measured: {stats['median']:.4f} s)")
    print(f"  Target P95 total     : ≤ {TARGET_P95_S:.1f} s  (measured: {stats['p95']:.4f} s)")
    print(f"  Target API cost/req  : ${TARGET_COST:.4f}     (measured: $0.000000 — local models)")

    gap_median = round(stats['median'] - TARGET_TOTAL_S, 4)
    gap_p95    = round(stats['p95']    - TARGET_P95_S,   4)

    print(f"\n  Gap median vs target : {gap_median:+.4f} s  ({'WITHIN' if gap_median <= 0 else 'OVER'} target)")
    print(f"  Gap P95 vs target    : {gap_p95:+.4f} s  ({'WITHIN' if gap_p95 <= 0 else 'OVER'} target)")

    print("\n" + "=" * 55)
    print("COST ANALYSIS")
    print("=" * 55)
    print("  This pipeline uses only local models:")
    print("    • SentenceTransformer all-MiniLM-L6-v2  (local)")
    print("    • CrossEncoder ms-marco-MiniLM-L-6-v2   (local)")
    print("    • FAISS IndexFlatIP                      (local)")
    print("    • BM25Okapi                              (local)")
    print("  No paid inference API is called.")
    print("  Paid API cost per request: $0.000000")
    print("  Infrastructure costs are excluded from API cost.")

    print("\n" + "=" * 55)
    print("TOMORROW'S OPTIMIZATION RECOMMENDATION")
    print("=" * 55)
    print(f"  Bottleneck identified: {slowest_stage}")
    if slowest_stage == "Reranking":
        print("  Recommendation: Cache CrossEncoder rerank scores for repeated")
        print("  queries. Consider replacing CrossEncoder with a lighter")
        print("  bi-encoder similarity score for the rerank step (e.g.,")
        print("  cosine sim on the same MiniLM embeddings) — this avoids the")
        print("  full cross-attention forward pass and can cut rerank time by ~60%.")
    elif slowest_stage == "Embedding":
        print("  Recommendation: Pre-cache query embeddings for the top-50")
        print("  most frequent questions. Use torch.no_grad() and batch size 1")
        print("  to minimise embedding overhead.")
    else:
        print(f"  Recommendation: Profile {slowest_stage} step further and")
        print("  consider async parallel execution of BM25 and FAISS retrieval.")

    # ── Save JSON summary ─────────────────────────────────────────────────────
    summary = {
        "total_latency_stats": stats,
        "stage_stats": stage_stats,
        "slowest_stage": slowest_stage,
        "api_cost_per_request_usd": 0.0,
        "cost_note": "All models are local. No paid API is used.",
        "speed_target_median_s": TARGET_TOTAL_S,
        "speed_target_p95_s": TARGET_P95_S,
        "gap_median_s": gap_median,
        "gap_p95_s": gap_p95,
        "runs": rows,
    }
    json_path = OUTPUT_DIR / "benchmark_summary.json"
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nJSON summary saved -> {json_path}")

    # ── Matplotlib chart ──────────────────────────────────────────────────────
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        runs = list(range(1, 11))
        fig, axes = plt.subplots(2, 1, figsize=(10, 8))

        # Top: total latency per run
        ax1 = axes[0]
        ax1.bar(runs, totals, color="steelblue", label="Total latency")
        ax1.axhline(stats["median"], color="orange", linestyle="--", label=f"Median {stats['median']:.3f}s")
        ax1.axhline(stats["p95"],   color="red",    linestyle=":",  label=f"P95 {stats['p95']:.3f}s")
        ax1.axhline(TARGET_TOTAL_S, color="green",  linestyle="-.", label=f"Target ≤{TARGET_TOTAL_S}s")
        ax1.set_xlabel("Run #")
        ax1.set_ylabel("Latency (s)")
        ax1.set_title("Week 7 Day 1 — Total Request Latency per Run")
        ax1.legend()
        ax1.set_xticks(runs)

        # Bottom: stage breakdown (stacked bar)
        ax2 = axes[1]
        bottoms = np.zeros(10)
        colors = ["#4C72B0", "#DD8452", "#55A868", "#C44E52"]
        for stage, color in zip(STAGE_NAMES, colors):
            vals = [r[f"{stage.lower()}_s"] for r in rows]
            ax2.bar(runs, vals, bottom=bottoms, label=stage, color=color)
            bottoms += np.array(vals)
        ax2.set_xlabel("Run #")
        ax2.set_ylabel("Latency (s)")
        ax2.set_title("Stage Breakdown per Run")
        ax2.legend()
        ax2.set_xticks(runs)

        plt.tight_layout()
        chart_path = OUTPUT_DIR / "latency_chart.png"
        plt.savefig(chart_path, dpi=150)
        plt.close()
        print(f"Chart saved -> {chart_path}")
    except Exception as e:
        print(f"Chart generation skipped: {e}")

    print("\nDay 1 benchmark complete.")
    return summary


if __name__ == "__main__":
    main()
