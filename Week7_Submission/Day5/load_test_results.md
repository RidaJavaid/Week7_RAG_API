# Load Test Results — Week 7 Day 5

## Configuration

| Parameter | Value |
|-----------|-------|
| Target URL | `http://127.0.0.1:8000` |
| Concurrent users | 5 |
| Total requests | 20 |

## Results

| Metric | Measured | Target | Status |
|--------|----------|--------|--------|
| Median latency | 0.2666s | ≤3.0s | ✅ MET |
| P95 latency | 0.3788s | ≤5.0s | ✅ MET |
| Mean latency | 0.2581s | — | — |
| Min latency | 0.1059s | — | — |
| Max latency | 0.3808s | — | — |
| Failure rate | 0.0% | 0% | ✅ OK |
| Successes | 20/20 | — | — |

## Verdict

Speed targets achieved ✅ at 5 concurrent users.

Both median and P95 latency are within targets.
