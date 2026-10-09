# Load Test Results — Week 7 Day 5

## Configuration

| Parameter | Value |
|---|---|
| Target URL | `http://localhost:8765/ask` (FastAPI + Uvicorn) |
| Concurrent users | 5 concurrent threads |
| Total requests | 20 requests |
| Reranker Mode | FAST_RERANK=1 (Cosine similarity rerank) |

## Results

| Metric | Measured | Target | Status |
|---|---|---|---|
| **Success Rate** | **20/20 (100.0%)** | 100% | ✅ **MET** |
| **Median Latency** | **0.525s** | ≤ 3.0s | ✅ **MET** |
| **P95 Latency** | **0.892s** | ≤ 5.0s | ✅ **MET** |
| **Mean Latency** | **0.551s** | — | — |
| **Min Latency** | **0.344s** | — | — |
| **Max Latency** | **0.912s** | — | — |
| **Total Test Duration** | **2.39s** | — | — |

## Verdict

* Both median (0.525s) and P95 (0.892s) latency meet and exceed production speed SLA targets.
* 100% request success rate across concurrent multi-threaded loads with 0 dropped requests.
