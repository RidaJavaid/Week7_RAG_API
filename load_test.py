"""
Week 7 Day 5 Part E — Load Test (no Locust dependency required)
===============================================================
Sends concurrent POST /ask requests to the local FastAPI server
and records latency statistics.

Usage (server must be running first):
  uvicorn main:app --host 0.0.0.0 --port 8000
  python load_test.py --url http://localhost:8000 --users 5 --requests 20

Output:
  Week7_Submission/Day5/load_test_results.md
"""

import argparse
import concurrent.futures
import json
import statistics
import time
from pathlib import Path

try:
    import requests as req_lib
except ImportError:
    req_lib = None

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "Week7_Submission" / "Day5" / "load_test_results.md"
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

TARGET_MEDIAN_S = 3.0
TARGET_P95_S    = 5.0

QUESTIONS = [
    "What is RAG?",
    "How does FAISS work?",
    "What is BM25?",
    "How does reranking work?",
    "What is SentenceTransformer?",
]


def single_request(url: str, question: str) -> dict:
    start = time.perf_counter()
    try:
        resp = req_lib.post(
            f"{url}/ask",
            json={"question": question},
            timeout=30,
        )
        elapsed = time.perf_counter() - start
        return {
            "latency": elapsed,
            "status_code": resp.status_code,
            "success": resp.status_code == 200,
        }
    except Exception as e:
        elapsed = time.perf_counter() - start
        return {
            "latency": elapsed,
            "status_code": 0,
            "success": False,
            "error": str(e),
        }


def run_load_test(url: str, concurrency: int, total_requests: int) -> dict:
    print(f"\nLoad test: {total_requests} requests, {concurrency} concurrent → {url}")

    tasks = []
    for i in range(total_requests):
        q = QUESTIONS[i % len(QUESTIONS)]
        tasks.append((url, q))

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = [pool.submit(single_request, url, q) for url, q in tasks]
        for f in concurrent.futures.as_completed(futures):
            results.append(f.result())

    latencies = [r["latency"] for r in results]
    successes = [r for r in results if r["success"]]
    failures  = [r for r in results if not r["success"]]

    sorted_lat = sorted(latencies)
    p95_idx = max(int(0.95 * len(sorted_lat)) - 1, 0)

    stats = {
        "total_requests": total_requests,
        "concurrency": concurrency,
        "success_count": len(successes),
        "failure_count": len(failures),
        "failure_rate_pct": round(100 * len(failures) / total_requests, 1),
        "median_latency_s": round(statistics.median(latencies), 4),
        "mean_latency_s": round(statistics.mean(latencies), 4),
        "p95_latency_s": round(sorted_lat[p95_idx], 4),
        "min_latency_s": round(min(latencies), 4),
        "max_latency_s": round(max(latencies), 4),
    }

    print(f"  Requests:       {total_requests}")
    print(f"  Succeeded:      {stats['success_count']}")
    print(f"  Failed:         {stats['failure_count']}  ({stats['failure_rate_pct']}%)")
    print(f"  Median latency: {stats['median_latency_s']:.4f}s")
    print(f"  P95 latency:    {stats['p95_latency_s']:.4f}s")

    return stats


def write_report(stats: dict | None, url: str, server_available: bool):
    if not server_available or stats is None:
        content = f"""# Load Test Results — Week 7 Day 5

## Status

**Server not reachable at `{url}`.**

The load test requires the FastAPI server to be running.

To run the load test:

```bash
# Terminal 1 — start the server
uvicorn main:app --host 0.0.0.0 --port 8000

# Terminal 2 — run the load test
python load_test.py --url http://localhost:8000 --users 5 --requests 20
```

## Day 1 Speed Targets (for comparison)

| Target | Value |
|--------|-------|
| Median latency | ≤ {TARGET_MEDIAN_S}s |
| P95 latency | ≤ {TARGET_P95_S}s |

## Note

This file will be overwritten with real measurements once the server is running.
"""
    else:
        median_ok = stats["median_latency_s"] <= TARGET_MEDIAN_S
        p95_ok    = stats["p95_latency_s"]    <= TARGET_P95_S

        content = f"""# Load Test Results — Week 7 Day 5

## Configuration

| Parameter | Value |
|-----------|-------|
| Target URL | `{url}` |
| Concurrent users | {stats['concurrency']} |
| Total requests | {stats['total_requests']} |

## Results

| Metric | Measured | Target | Status |
|--------|----------|--------|--------|
| Median latency | {stats['median_latency_s']:.4f}s | ≤{TARGET_MEDIAN_S}s | {'✅ MET' if median_ok else '⚠️ OVER'} |
| P95 latency | {stats['p95_latency_s']:.4f}s | ≤{TARGET_P95_S}s | {'✅ MET' if p95_ok else '⚠️ OVER'} |
| Mean latency | {stats['mean_latency_s']:.4f}s | — | — |
| Min latency | {stats['min_latency_s']:.4f}s | — | — |
| Max latency | {stats['max_latency_s']:.4f}s | — | — |
| Failure rate | {stats['failure_rate_pct']}% | 0% | {'✅ OK' if stats['failure_rate_pct'] == 0 else '⚠️ FAILURES'} |
| Successes | {stats['success_count']}/{stats['total_requests']} | — | — |

## Verdict

Speed targets {'achieved ✅' if median_ok and p95_ok else 'NOT yet achieved ⚠️'} at {stats['concurrency']} concurrent users.

{'Both median and P95 latency are within targets.' if median_ok and p95_ok else 'One or more latency targets exceeded. Consider caching, model quantisation, or async retrieval.'}
"""
    OUTPUT.write_text(content, encoding="utf-8")
    print(f"\nReport saved → {OUTPUT}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url",      default="http://localhost:8000")
    parser.add_argument("--users",    type=int, default=5)
    parser.add_argument("--requests", type=int, default=20)
    args = parser.parse_args()

    if req_lib is None:
        print("ERROR: 'requests' package not installed. Run: pip install requests")
        write_report(None, args.url, False)
        return

    # Check server availability
    try:
        health = req_lib.get(f"{args.url}/health", timeout=5)
        server_available = health.status_code == 200
    except Exception:
        server_available = False

    if not server_available:
        print(f"Server not reachable at {args.url}. Writing placeholder report.")
        write_report(None, args.url, False)
        return

    stats = run_load_test(args.url, args.users, args.requests)
    write_report(stats, args.url, True)


if __name__ == "__main__":
    main()
