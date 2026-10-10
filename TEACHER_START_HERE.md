# Week 7 RAG API — Teacher Start Guide

**Author:** Rida Javaid  
**Assignment:** Week 7 — Production RAG API (Days 1–5)  
**Python Version Required:** 3.10, 3.11, or 3.12  
**Platform:** Windows 10/11

---

## Quick Start (3 steps)

### Step 1 — Install Python (if not already installed)

Download Python 3.11 from: https://www.python.org/downloads/

**Important:** During installation, check the box **"Add python.exe to PATH"**.

Verify installation by opening a Command Prompt and typing:
```
python --version
```

---

### Step 2 — Set up the environment

Extract this ZIP to any folder (e.g., `C:\Week7_RAG_API`).

Open that folder in Windows Explorer and **double-click `setup.bat`**.

A window will open and automatically:
- Create a Python virtual environment in `.\venv\`
- Install all required packages (PyTorch, FastAPI, FAISS, Streamlit, etc.)

**First-run internet requirement:** The setup downloads ~200 MB of packages from PyPI and PyTorch CDN. After the first setup, no internet is needed.

Wait for the message: `Setup Complete!` then close the window.

---

### Step 3 — Run the application

**Open two Command Prompt windows in the project folder:**

**Window 1 — Start the API backend:**
Double-click `Start_API.bat`

Wait for: `Application startup complete.`

**First-run note:** Loading AI models (all-MiniLM-L6-v2) takes **1–3 minutes** on first startup. Subsequent starts are faster.

- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

**Window 2 — Start the monitoring dashboard:**
Double-click `Start_Dashboard.bat`

- Dashboard: http://localhost:8501

---

## Sample RAG Question

With both windows running, open your browser and go to:

http://localhost:8000/docs

Click `POST /ask` → `Try it out` → enter:
```json
{"question": "What is FAISS?"}
```
Click **Execute**.

**Expected answer:** "FAISS is a library for efficient similarity search over dense vectors."

---

## Assignment Deliverables Location

All Day 1–5 reports, notebooks, test results, and evidence are in:

```
Week7_Submission/
  Day1/  — Speed & cost benchmark (notebook, CSV, chart)
  Day2/  — FastAPI documentation and test results
  Day3/  — Cost tracking and ingestion deduplication tests
  Day4/  — Automated ingestion and Slack notification evidence
  Day5/  — Quality evaluation, injection test, CI guide, dashboard screenshot
  README.md
  SUBMISSION_CHECKLIST.md
```

---

## Running the Test Suite

```
.\venv\Scripts\python.exe -m pytest tests/ -v
```

Expected: **19 passed** (or 18 passed, 1 skipped if Slack webhook not configured)

---

## Key Performance Results (Verified)

| Metric | Result | Target | Status |
|--------|--------|--------|--------|
| Median request latency | 1.57s | ≤ 3.0s | PASS |
| P95 request latency | 1.75s | ≤ 5.0s | PASS |
| Paid API cost/request | $0.00 | $0.00 | PASS |
| Quality score (50 questions) | 0.692 | ≥ 0.40 | PASS |
| Test suite | 19 passed | All pass | PASS |

---

## GitHub Repository

https://github.com/RidaJavaid/Week7_RAG_API

---

## Troubleshooting

**"Python not found"** → Re-install Python with "Add to PATH" checked.

**Setup takes more than 10 minutes** → Normal on slow internet — PyTorch CPU (~100 MB) and sentence-transformers (~90 MB) are being downloaded.

**Dashboard shows "benchmark data not found"** → Run `Start_API.bat` first (it rebuilds the FAISS index), then refresh the dashboard.

**Port already in use** → Another application is using port 8000 or 8501. Restart your computer and try again.

**Model loading slow** → Normal on first run. Subsequent runs reuse the cached model files from `~/.cache/huggingface/`.
