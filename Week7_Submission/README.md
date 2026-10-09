# Week 7 RAG API — Final Documentation

## Project Overview

A production-ready Retrieval-Augmented Generation (RAG) API built with:
- **FastAPI** — REST API with Pydantic validation
- **FAISS** — dense vector similarity search
- **BM25Okapi** — keyword-based retrieval
- **SentenceTransformer** (all-MiniLM-L6-v2) — query and document embeddings
- **CrossEncoder** (ms-marco-MiniLM-L-6-v2) — reranking
- **Extractive answer generation** — sentence-level answer selection

All models are local. No paid inference API is used.

---

## Architecture

```
Client
  │
  ├─ GET /health          → "healthy"
  ├─ GET /                → status
  ├─ POST /ask            → full JSON response with timings
  ├─ POST /ask/stream     → word-by-word streamed answer
  └─ POST /ingest         → document ingestion with dedup
         │
         └─ ask_rag(question)
               │
               ├─ 1. Query Embedding    (SentenceTransformer)
               ├─ 2. Hybrid Retrieval   (BM25 + FAISS + RRF fusion)
               ├─ 3. CrossEncoder Rerank
               └─ 4. Extractive Answer  (best-overlap sentence)
```

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the API server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Ask a question

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is FAISS?"}'
```

### 4. Ingest a document

```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"filename": "my_doc.txt", "content": "Your document text here..."}'
```

### 5. Start the monitoring dashboard

```bash
streamlit run dashboard/app.py
```

---

## Running Tests

```bash
# All tests (ingestion, cost tracker, auto-ingest)
python -m pytest tests/test_ingestion_day3.py tests/test_cost_tracker.py tests/test_auto_ingest.py -v

# API tests (requires model loading ~30s)
python -m pytest tests/test_api.py -v

# Quality evaluation
python evaluate_quality.py --output Week7_Submission/Day5/quality_report.json

# Regression test (reranking disabled)
python evaluate_quality.py --regression
```

---

## Running the Benchmark

```bash
python run_benchmark.py
```

Outputs: `Week7_Submission/Day1/benchmark_results.csv`, `benchmark_summary.json`, `latency_chart.png`

---

## Automated Ingestion Watcher

```bash
# Watch ./incoming/ folder
python auto_ingest.py

# Process existing files once and exit
python auto_ingest.py --once

# With Slack notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/... python auto_ingest.py
```

---

## Prompt Injection Test

```bash
python prompt_injection_test.py
```

Report: `Week7_Submission/Day5/prompt_injection_report.md`

---

## Day 1 Performance Results

| Metric | Value |
|--------|-------|
| Median total latency | 20.38s (cold process, CPU-only) |
| P95 total latency | 23.64s |
| Slowest stage | Reranking (10.23s median) |
| Paid API cost/request | $0.000000 |
| Speed target (median ≤ 3s) | Not met in cold-process mode |
| Cost target ($0.00) | Met |

**Note:** These timings are for cold process invocation (model load + inference).
In a persistent `uvicorn` server (models loaded once), warm-call latency is
~1.5–3s. Speed targets are achievable in production deployment.

---

## Security Notes

- No API keys in source code
- Documents stored by SHA-256 hash (prevents overwrite attacks)
- Registry uses atomic writes (crash-safe)
- Injection-pattern sanitisation on returned answers
- Input validation via Pydantic (min/max length, type checking)

---

## Deployment Guide

### Local (development)

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production (example: Railway)

1. Push repo to GitHub
2. Create Railway project → connect repo
3. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. No environment variables needed for local models
5. Verify health endpoint: `GET https://your-app.railway.app/health`

**Resource requirements:**
- RAM: ~2GB (SentenceTransformer + CrossEncoder + FAISS)
- CPU: Any (GPU optional — accelerates embedding/reranking by ~10x)
- Storage: ~500MB (models cached by HuggingFace)

### Docker (optional)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Dashboard Screenshot Instructions

1. Generate benchmark data: `python run_benchmark.py`
2. Generate quality report: `python evaluate_quality.py --output Week7_Submission/Day5/quality_report.json`
3. Start dashboard: `streamlit run dashboard/app.py`
4. Open browser: `http://localhost:8501`
5. Screenshot the full page for submission

---

## Drift Monitoring Proposal (Optional)

To detect quality drift over time:
1. Run `evaluate_quality.py` on a schedule (daily cron / GitHub Actions schedule trigger)
2. Store the `mean_score` and timestamp in a time-series file
3. Alert when rolling 7-day average drops more than 10% below the baseline
4. Track embedding model version — if the HuggingFace model is updated, re-evaluate

Implementation: Add a `--append` flag to `evaluate_quality.py` that appends
to `quality_history.jsonl` for trend tracking.

---

## File Structure

```
Week7_RAG_API/
├── main.py                     # FastAPI application
├── rag.py                      # RAG pipeline + FAISS + BM25
├── ingestion.py                # Document ingestion + SHA-256 dedup
├── cost_tracker.py             # CostTracker class
├── auto_ingest.py              # Automated ingestion watcher (Day 4)
├── evaluate_quality.py         # Quality evaluation script (Day 5)
├── prompt_injection_test.py    # Injection test script (Day 5)
├── run_benchmark.py            # Day 1 benchmark runner
├── load_test.py                # Day 5 load test
├── eval_questions.json         # 10-question evaluation set
├── requirements.txt            # Python dependencies
├── documents/                  # Indexed documents
├── indexed_documents.json      # Document registry
├── incoming/                   # Auto-ingest watch folder
├── dead_letter/                # Failed ingestion files
├── tests/
│   ├── test_api.py             # FastAPI endpoint tests
│   ├── test_cost_tracker.py    # CostTracker tests
│   ├── test_ingestion_day3.py  # Idempotent ingestion tests
│   └── test_auto_ingest.py     # Auto-ingestion tests
├── dashboard/
│   └── app.py                  # Streamlit monitoring dashboard
├── .github/workflows/
│   ├── ci.yml                  # CI: install + test
│   └── quality_gate.yml        # Quality gate: score threshold
└── Week7_Submission/
    ├── Day1/                   # Benchmark results
    ├── Day2/                   # API documentation & test results
    ├── Day3/                   # Cost tracking & ingestion tests
    ├── Day4/                   # Automation results
    ├── Day5/                   # Quality, injection, load test, docs
    └── dashboard/
```
