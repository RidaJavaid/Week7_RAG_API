# Week 7 RAG API: Performance Optimization, Production Serving, and Evaluation

A software engineering project implementing an end-to-end Retrieval-Augmented Generation (RAG) system with hybrid search, microsecond latency profiling, zero paid API inference costs, CI/CD quality gating, and real-time monitoring.

---

## Project Overview

This repository contains the Week 7 RAG API implementation, focusing on production engineering for retrieval systems:

- **FastAPI REST Service**: Endpoints for synchronous and streaming question answering with Pydantic request validation and error handling.
- **Hybrid Search**: Combines dense vector retrieval (FAISS `IndexFlatIP`) with sparse lexical matching (BM25Okapi) using Reciprocal Rank Fusion (RRF).
- **Local Embedding & Reranking**: Utilizes `sentence-transformers/all-MiniLM-L6-v2` for dense embeddings and cosine similarity reranking, eliminating third-party inference costs ($0.000000 API cost).
- **Cost & Latency Instrumentation**: Microsecond per-stage profiling (`perf_counter`) and deterministic budget enforcement (`CostTracker`).
- **Idempotent Ingestion**: SHA-256 document deduplication preventing redundant chunk indexing.
- **Automated Directory Watcher**: Polling ingestion pipeline with exponential backoff retries and dead-letter queue routing.
- **Continuous Integration**: GitHub Actions workflows for automated test suites and retrieval quality gates (`GOLD_QA` 50-question set).
- **Monitoring Dashboard**: Streamlit interface displaying real-time query metrics, stage latency distributions, and retrieval health.

---

## System Architecture

```text
Client Applications
  │
  ├── GET /health           ──> Health check status
  ├── GET /docs             ──> OpenAPI Swagger documentation
  ├── POST /ask             ──> Synchronous JSON Q&A with timing telemetry
  ├── POST /ask/stream      ──> Server-Sent Events (SSE) token stream
  └── POST /ingest          ──> Idempotent document ingestion (SHA-256)
         │
         ▼
  RAG Engine (rag.py)
         │
         ├── 1. Query Embedding   (all-MiniLM-L6-v2, 384 dimensions)
         ├── 2. Hybrid Search      (FAISS vector search + BM25Okapi lexical matching)
         ├── 3. Candidate Fusion   (Reciprocal Rank Fusion, k=60)
         ├── 4. Fast Reranking     (Cosine similarity rescoring)
         └── 5. Answer Extraction  (Highest overlap passage selection)
```

---

## Directory Structure

```text
Week7_RAG_API/
├── main.py                     # FastAPI application endpoints
├── rag.py                      # Hybrid retrieval pipeline and FAISS index
├── ingestion.py                # SHA-256 document ingestion and registry
├── cost_tracker.py             # Telemetry tracking for stage latencies and budgets
├── auto_ingest.py              # Automated file ingestion watcher and retry queue
├── evaluate_quality.py         # Quality evaluation script for 50-question eval set
├── create_regression_branch.py # Script for generating CI quality gate test branch
├── prompt_injection_test.py    # Security evaluation and defense demonstration
├── run_benchmark.py            # Latency benchmark harness (10 runs)
├── load_test.py                # Concurrent load test harness
├── eval_questions.json         # 50 technical evaluation questions (GOLD_QA)
├── requirements.txt            # Python dependencies (CPU-optimized)
├── render.yaml                 # Render Blueprint deployment configuration
├── Procfile                    # ASGI production startup command
├── incoming/                   # Monitored directory for new documents
├── dead_letter/                # Malformed/unparseable document queue
├── documents/                  # Ingested and stored documents
├── dashboard/
│   └── app.py                  # Streamlit monitoring and interactive querying UI
├── tests/
│   ├── test_api.py             # FastAPI endpoint and validation tests
│   ├── test_cost_tracker.py    # Cost tracker budget and timeout tests
│   ├── test_ingestion_day3.py  # Idempotent ingestion tests
│   └── test_auto_ingest.py     # Ingestion watcher and dead-letter tests
└── Week7_Submission/           # Project reports, benchmark CSVs, and artifacts
    ├── Day1/                   # Speed & cost benchmark results and notebook
    ├── Day2/                   # API documentation and test logs
    ├── Day3/                   # Cost tracking and deduplication test logs
    ├── Day4/                   # Automation, retries, and dead-letter evidence
    ├── Day5/                   # Quality gate, prompt injection, and load test reports
    ├── dashboard/              # Dashboard setup guide and interface screenshot
    └── SUBMISSION_CHECKLIST.md # Technical requirements audit table
```

---

## Quick Start

### 1. Environment Setup

```bash
# Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the FastAPI Service

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive documentation is available at `http://localhost:8000/docs`.

### 3. Launch the Monitoring Dashboard

```bash
streamlit run dashboard/app.py
```

Access the dashboard at `http://localhost:8501`.

---

## Testing & Quality Evaluation

```bash
# Run unit and integration tests
pytest tests/ -v

# Run the 50-question retrieval quality evaluation
python evaluate_quality.py --output Week7_Submission/Day5/quality_report.json

# Run the prompt injection security test
python prompt_injection_test.py

# Run the concurrent load test
python run_server_and_loadtest.py
```

---

## Performance Summary

- **Median Latency**: 1.57s (Target: ≤ 3.0s — **Met**)
- **P95 Latency**: 1.75s (Target: ≤ 5.0s — **Met**)
- **API Cost**: $0.000000 per request (100% local model inference)
- **Quality Score**: 0.6919 on 50 questions (Threshold: ≥ 0.40 — **Passed**)
- **Concurrent Load**: 20/20 successful requests under 5 concurrent users (0.525s median latency)

---

## Public Live Demo (GitHub Codespaces)

> **Temporary hosting:** These URLs require the GitHub Codespace to remain active.
> They are not permanent and future uptime is not guaranteed. The latest check
> during this submission run received HTTP 404 from both hosts; the previous
> browser verification below is historical evidence supplied by the project owner.

| Item | Detail |
|------|--------|
| **Dashboard URL** | https://psychic-bassoon-q7p4xrq7vr6934q7v-8501.app.github.dev/ |
| **FastAPI URL** | https://psychic-bassoon-q7p4xrq7vr6934q7v-8000.app.github.dev/ |
| **FastAPI health** | https://psychic-bassoon-q7p4xrq7vr6934q7v-8000.app.github.dev/health |
| **FastAPI Swagger** | https://psychic-bassoon-q7p4xrq7vr6934q7v-8000.app.github.dev/docs |
| **FastAPI question endpoint** | `POST https://psychic-bassoon-q7p4xrq7vr6934q7v-8000.app.github.dev/ask` |
| **Historical verification** | Owner reported Incognito dashboard access and successful API endpoint checks on October 10, 2026. |
| **Historical test query** | "What is FAISS?" → "FAISS is a library for efficient similarity search over dense vectors." |
| **Historical dashboard response time** | 0.024s, as reported by owner |
| **Current reachability** | HTTP 404 from both public hosts during the final submission check; currently unavailable. |

For the exact historical evidence and current recheck, see
`Week7_Submission/Day5/deployment_status.md`. Codespaces links can expire when the
Codespace is paused, deleted, or times out.

For local use, follow `TEACHER_START_HERE.md` and the included Windows batch
scripts (`setup.bat`, `Start_API.bat`, and `Start_Dashboard.bat`).
