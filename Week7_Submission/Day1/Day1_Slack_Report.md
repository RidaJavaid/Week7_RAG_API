# Day 1 — Speed & Cost Report (UPDATED with optimization)

**Week 7 RAG API | Day 1 | Reranker Optimization Applied**

---

## Pipeline Under Test

Local hybrid RAG: BM25 + FAISS retrieval → fast cosine reranking → extractive answer.

Optimization: CrossEncoder (~10s/request) replaced with cosine similarity on cached chunk embeddings (<0.001s/request). This was the Day 1 evidence-based recommendation.

No paid inference API. All models run locally.

---

## 10-Run Timing Results (FAST_RERANK=1)

| Run | Total (s) | Embed (s) | Retrieve (s) | Rerank (s)  | Generate (s) |
|-----|-----------|-----------|--------------|-------------|--------------|
| 1   | 1.353     | 1.343     | 0.005        | 0.002        | 0.001        |
| 2   | 1.435     | 1.431     | 0.001        | 0.000        | 0.001        |
| 3   | 1.791     | 1.788     | 0.001        | 0.000        | 0.000        |
| 4   | 1.749     | 1.747     | 0.001        | 0.000        | 0.000        |
| 5   | 1.653     | 1.651     | 0.000        | 0.000        | 0.000        |
| 6   | 1.479     | 1.477     | 0.001        | 0.000        | 0.000        |
| 7   | 1.710     | 1.703     | 0.001        | 0.000        | 0.000        |
| 8   | 1.617     | 1.610     | 0.001        | 0.000        | 0.000        |
| 9   | 1.066     | 1.043     | 0.003        | 0.000        | 0.004        |
| 10  | 1.526     | 1.522     | 0.001        | 0.000        | 0.000        |

*(Full table in `benchmark_results.csv`)*

---

## Latency Statistics

| Metric | Before optimization | After optimization | Change |
|--------|--------------------|--------------------|--------|
| **Median** | 20.38 s | **1.57 s** | -18.81 s |
| **Mean**   | 20.54 s | **1.54 s** | -19.00 s |
| **P95**    | 23.64 s | **1.75 s** | -21.89 s |
| Min        | 16.95 s | 1.07 s     | |
| Max        | 25.18 s | 1.79 s     | |

**Speedup: 13x**

---

## Per-Stage Median Breakdown (After Optimization)

| Stage      | Before | After   | Change     |
|------------|--------|---------|------------|
| Embedding  | 5.60s  | **1.57s**   | -4.03s    |
| Retrieval  | 0.001s | 0.001s  | unchanged  |
| **Reranking** | **10.23s** | **0.0002s** | **-10.23s** |
| Generation | 0.0002s | 0.0002s | unchanged |

New bottleneck: **Embedding** (>95% of total time)

---

## Speed & Cost Targets

| Target | Value | Measured | Status |
|--------|-------|----------|--------|
| Median latency | ≤ 3.0 s | **1.57 s** | **MET** |
| P95 latency | ≤ 5.0 s | **1.75 s** | **MET** |
| API cost/req | $0.000 | $0.000 | **MET** |

Both speed targets are now met.

---

## Cost per Question

| Metric | Value |
|--------|-------|
| Paid API cost | **$0.000000** |
| Models used | All local (SentenceTransformer, BM25, FAISS, cosine sim) |
| Infrastructure | Excluded per spec |

---

## Optimization Applied

**Change:** `FAST_RERANK=1` env var (default on) replaces CrossEncoder with cosine similarity on pre-computed unit-normalized chunk embeddings.

- CrossEncoder: full cross-attention forward pass, ~10s/call on CPU
- Cosine similarity: dot product of unit vectors, <1ms

**Quality tradeoff (from Week 6 ablation data):**
- With CrossEncoder: MRR@5=0.9700, NDCG@5=0.9779
- Without reranker (RRF only): MRR@5=0.9500, NDCG@5=0.9631
- With cosine similarity: expected ~0.965 NDCG (between the two)

The assignment requires a speed target; quality is verified separately via the 50-question evaluation (mean keyword overlap: 0.692, threshold: 0.40 → PASSED).

## Next Optimization Plan (Proposed, Not Yet Implemented)

Embedding now accounts for more than 95% of measured request time, so further
work should target embedding without weakening retrieval quality:

1. Profile warm and cold embedding separately and repeat the 10-question latency
   benchmark to confirm the bottleneck.
2. Evaluate CPU-int8/ONNX embedding inference against the current Sentence
   Transformer on the same benchmark and 50-question evaluation set.
3. Adopt a faster option only if median latency remains at or below 3.0 seconds,
   P95 remains at or below 5.0 seconds, and mean quality remains at or above the
   0.40 threshold. Record the comparison before changing the default.

These are proposed experiments, not completed optimizations or measured results.

---

*Files:* `benchmark_results.csv` · `benchmark_summary.json` · `latency_chart.png`
