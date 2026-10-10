"""Write the optimized benchmark summary JSON from the CSV that was already saved."""
import csv, json, statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CSV  = ROOT / "Week7_Submission" / "Day1" / "benchmark_results.csv"
JSON = ROOT / "Week7_Submission" / "Day1" / "benchmark_summary.json"

rows = list(csv.DictReader(CSV.open(encoding="utf-8")))

def to_float(v): return float(v)

totals      = [to_float(r["total_latency_s"])  for r in rows]
embeddings  = [to_float(r["embedding_s"])      for r in rows]
retrievals  = [to_float(r["retrieval_s"])      for r in rows]
rerankings  = [to_float(r["reranking_s"])      for r in rows]
generations = [to_float(r["generation_s"])     for r in rows]

def stats(vals):
    s = sorted(vals)
    p95_idx = max(int(0.95 * len(s)) - 1, 0)
    return {
        "median": round(statistics.median(s), 4),
        "mean":   round(statistics.mean(s),   4),
        "p95":    round(s[p95_idx],            4),
        "min":    round(min(s),                4),
        "max":    round(max(s),                4),
    }

total_stats = stats(totals)
stage_stats = {
    "Embedding":  stats(embeddings),
    "Retrieval":  stats(retrievals),
    "Reranking":  stats(rerankings),
    "Generation": stats(generations),
}
slowest = max(stage_stats, key=lambda k: stage_stats[k]["median"])

TARGET_MEDIAN = 3.0
TARGET_P95    = 5.0

summary = {
    "rerank_mode": "cosine_fast",
    "total_latency_stats": total_stats,
    "stage_stats": stage_stats,
    "slowest_stage": slowest,
    "api_cost_per_request_usd": 0.0,
    "cost_note": "All models are local. No paid API is used.",
    "speed_target_median_s": TARGET_MEDIAN,
    "speed_target_p95_s": TARGET_P95,
    "gap_median_s": round(total_stats["median"] - TARGET_MEDIAN, 4),
    "gap_p95_s":    round(total_stats["p95"]    - TARGET_P95,    4),
    "vs_baseline": {
        "baseline_median_s": 20.38,
        "optimized_median_s": total_stats["median"],
        "speedup_x": round(20.38 / total_stats["median"], 1),
    },
    "runs": [{"run": i+1, **r} for i, r in enumerate(rows)],
}

JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")

print("=== OPTIMIZED BENCHMARK RESULTS (FAST_RERANK=1) ===")
print(f"Median total latency : {total_stats['median']:.4f}s  (was 20.38s)")
print(f"P95 total latency    : {total_stats['p95']:.4f}s   (was 23.64s)")
print(f"Speedup              : {summary['vs_baseline']['speedup_x']}x")
print(f"Reranking median     : {stage_stats['Reranking']['median']:.4f}s  (was 10.23s)")
print(f"Slowest stage        : {slowest}")
print(f"Target median (<=3s) : {'MET' if total_stats['median'] <= 3.0 else 'OVER'}")
print(f"Target P95 (<=5s)    : {'MET' if total_stats['p95'] <= 5.0 else 'OVER'}")
print(f"Summary saved: {JSON}")
