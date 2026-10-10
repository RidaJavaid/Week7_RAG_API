# Week 7 RAG API -- Quick Start & Evaluation Guide

This guide provides simple, step-by-step instructions to run and evaluate the **Week 7 Retrieval-Augmented Generation (RAG) API & Monitoring System** on any Windows machine.

---

## 1. System Requirements & Prerequisites

- **Operating System**: Windows 10 or Windows 11 (64-bit)
- **Python**: Python 3.10, 3.11, or 3.12 installed ([Download from Python.org](https://www.python.org/downloads/))
  > *Important*: Ensure the checkbox **"Add python.exe to PATH"** was checked during Python installation.
- **API Keys / Secrets**: **None required!**
  > The system runs 100% locally using lightweight open-source embeddings (`all-MiniLM-L6-v2`) and FAISS dense vector search ($0.000000 external API inference cost).
- **Internet Access**: Only required during initial setup to download standard Python wheels from PyPI and the ~90MB local model weights from Hugging Face. After the first run, the system operates completely offline.

---

## 2. Quick Setup (Automated Environment Setup)

### Option A: 1-Click Batch Setup (Recommended)
1. Extract the `Week7_RAG_Project.zip` folder to any location on your machine.
2. Double-click **`setup.bat`**.

### Option B: Python Setup Script
Alternatively, open PowerShell in the extracted folder and run:
```powershell
python setup_week7.py
```

**What the setup scripts do automatically:**
- Verify Python installation and environment isolation.
- Create a dedicated virtual environment in `.\venv` (preventing any global site-packages permission issues).
- Install all required dependencies from `requirements.txt` (CPU-optimized PyTorch, FAISS, FastAPI, Streamlit, etc.).
- Verify that every critical package (`fastapi`, `uvicorn`, `sentence_transformers`, `faiss`, `streamlit`, `torch`, etc.) imports successfully.


---

## 3. Launching the Services

Once `setup.bat` completes, you can run the services using the provided batch scripts:

### A. FastAPI REST API Service
- Double-click **`Start_API.bat`**.
- The API will warm up the local embedding models and bind to `http://localhost:8000`.
- **Interactive OpenAPI / Swagger Documentation**: Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser.
- **Service Health Check**: Open [http://localhost:8000/health](http://localhost:8000/health) (returns `{"status": "healthy"}`).
- **Key API Endpoints**:
  - `POST /ask`: Synchronous question answering with per-stage latency telemetry.
  - `POST /ask/stream`: Server-Sent Events (SSE) streaming token response.
  - `POST /ingest`: SHA-256 deduplicated idempotent document ingestion.

### B. Interactive Monitoring Dashboard
- Double-click **`Start_Dashboard.bat`**.
- The dashboard automatically opens in your browser at [http://localhost:8501](http://localhost:8501).
- **Features**:
  - **Ask RAG Interactive UI**: Query the local hybrid retrieval engine live.
  - **Latency Profiling**: Empirical median (`1.57s`) and P95 (`1.75s`) timing distributions.
  - **Zero Cost Telemetry**: Proof of $0.000000 paid inference cost.
  - **Quality Gate**: Official 50-question retrieval score evaluation (`0.6919` vs `0.40` threshold).
  - **Document Index Status**: Live display of all indexed document chunks.

---

## 4. Running the Verification & Test Suite

To run all automated test suites, open a terminal in this project directory and run:

```powershell
# Run the complete test suite (API endpoints, deduplication, cost tracker, and ingestion watcher)
.\venv\Scripts\python.exe -m pytest tests/ -v

# Run the official 50-question quality evaluation
.\venv\Scripts\python.exe evaluate_quality.py --output Week7_Submission/Day5/quality_report.json

# Run the prompt injection security test
.\venv\Scripts\python.exe prompt_injection_test.py

# Run the concurrent load test
.\venv\Scripts\python.exe run_server_and_loadtest.py
```

---

## 5. Submission Directory Structure (`Week7_Submission/`)

All deliverables across all five assignment days are pre-computed, verified, and organized in `Week7_Submission/`:

- **`Day1/`**: 10-run speed & cost benchmark data, latency distribution chart, and Google Colab notebook (`Week7_Day1_Speed_Cost.ipynb`).
- **`Day2/`**: FastAPI endpoint documentation, error handling tests, and Render Blueprint deployment specifications.
- **`Day3/`**: Idempotent document ingestion logs, 3× duplicate test evidence, and budget limits.
- **`Day4/`**: Directory watcher test logs, dead-letter routing evidence, and Slack integration results with verified screenshot (`slack_notification_evidence.png`).
- **`Day5/`**: 50-question quality gate report, prompt injection defense report, concurrent load test results, and Streamlit dashboard screenshot.
- **`SUBMISSION_CHECKLIST.md`**: Complete audit matrix mapping all course requirements to verified artifacts on disk.
