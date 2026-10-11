# Week 7 RAG API — Teacher Start Guide

**Assignment:** Week 7 — Production RAG API (Days 1–5)  
**Platform:** Windows 10/11, 64-bit  
**Python:** 3.10–3.12 (Python 3.12.10 was used for the ZIP clean-room test)

## 1. Extract the ZIP

Extract `Week7_RAG_Project_FINAL.zip` to a writable folder, for example
`C:\Week7_RAG_API`. Do not run the project from inside the ZIP file.

## 2. Install Python and project dependencies

Install Python 3.10, 3.11, or 3.12 from
[python.org](https://www.python.org/downloads/). During installation, enable
**Add python.exe to PATH**. Check it in Command Prompt:

```bat
python --version
```

From File Explorer, double-click `setup.bat` in the extracted project folder.
It creates the project's `venv` and installs packages from `requirements.txt`.
Wait for **Setup Complete!** and press a key to close the window.

An internet connection is required for the first setup to download Python
packages and for the first app launch to download the `all-MiniLM-L6-v2`
embedding model from Hugging Face. Allow several minutes and about 1 GB of free
disk space for packages, model files, and working data. Model weights are not
bundled in the ZIP. Later launches can use the local Hugging Face cache.

No paid inference API key is needed. Slack notifications are optional and need
a `SLACK_WEBHOOK_URL` only if live Slack delivery is being configured.

## 3. Start the FastAPI service

Double-click `Start_API.bat`. Keep its window open while using the app. The
script starts Uvicorn on port 8000 and sets the fast cosine reranker.

- API root: <http://localhost:8000/>
- Health check: <http://localhost:8000/health>
- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

The first start loads or downloads local models and builds the FAISS index.
Wait for the startup-complete message before sending a request.

## 4. Start the Streamlit dashboard

Open a second window and double-click `Start_Dashboard.bat`. Keep this window
open too.

- Dashboard: <http://localhost:8501/>

The dashboard connects to the local API at `http://localhost:8000` by default.
Use its **Ask RAG** form for an interactive query.

## 5. Try a RAG question

In the browser, open <http://localhost:8000/docs>, expand `POST /ask`, select
**Try it out**, and submit:

```json
{"question": "What is FAISS?"}
```

The tested answer is: **“FAISS is a library for efficient similarity search
over dense vectors.”** The response also includes a source document, stage
timings, and the estimated inference API cost (`0.0`).

## 6. Run automated tests

Open Command Prompt in the extracted project folder and run:

```bat
venv\Scripts\python.exe -m pytest tests -v
```

The latest fresh ZIP clean-room test on Python 3.12.10 collected and passed all
42 tests (0 failed, 0 skipped; 108.35 seconds). Three warnings were emitted:
one upstream Starlette/httpx deprecation and two pytest warnings about test
functions returning values. To repeat the test without relying on an active API
or dashboard window, stop those services first with Ctrl+C in their respective
windows.

## 7. Day 1–5 assignment deliverables

Open `Week7_Submission/`:

- `Day1/` — ten-run benchmark CSV and summary, latency chart, notebook, and
  speed/cost report.
- `Day2/` — API documentation, test results, deployment configuration and
  deployment evidence.
- `Day3/` — cost tracking and idempotent ingestion evidence.
- `Day4/` — automated ingestion, retry/dead-letter evidence, Slack integration
  report and screenshot.
- `Day5/` — evaluation report/data, quality gate, prompt-injection testing,
  concurrent load-test results, dashboard screenshot, deployment status, and
  actual clean-room command/test logs in `Day5/cleanroom_evidence/`.
- `README.md` and `SUBMISSION_CHECKLIST.md` — assignment overview and checklist.

The ZIP root also includes `cleanroom_report.txt`, which records the actual
ZIP-extraction, Windows setup, API, dashboard, and test results from this
same-machine simulation. It is not a physical second-PC test.

## 8. Public Codespaces demo (temporary)

The following are the supplied public Codespaces URLs:

- Dashboard: <https://psychic-bassoon-q7p4xrq7vr6934q7v-8501.app.github.dev/>
- FastAPI root: <https://psychic-bassoon-q7p4xrq7vr6934q7v-8000.app.github.dev/>
- FastAPI health: <https://psychic-bassoon-q7p4xrq7vr6934q7v-8000.app.github.dev/health>
- FastAPI Swagger: <https://psychic-bassoon-q7p4xrq7vr6934q7v-8000.app.github.dev/docs>
- FastAPI question endpoint: `POST
  https://psychic-bassoon-q7p4xrq7vr6934q7v-8000.app.github.dev/ask`

The owner reported successful public browser checks on October 10, 2026.
On October 11, the existing Codespace appeared Active in GitHub, but its
browser session reported connection errors (504). Requests to the public links
reached the GitHub authentication gateway, not the apps; the POST `/ask` check
returned 401. The deployment is **not currently verified live or publicly
accessible without GitHub login**.

To restore the existing deployment, resume the existing `psychic bassoon`
Codespace (do not create a new one), run these commands in separate terminals,
and set both ports to **Public** in the Codespaces Ports panel:

```bash
FAST_RERANK=1 python -m uvicorn main:app --host 0.0.0.0 --port 8000
python -m streamlit run dashboard/app.py --server.address 0.0.0.0 --server.port 8501
```

Then verify the forwarded `/health`, `/docs`, and `/ask` API endpoints and submit
`What is FAISS?` in the dashboard from a logged-out browser. A GitHub login page,
401, 404, or 502 is not a successful deployment check. Codespaces is temporary
hosting: URLs work only while the Codespace and forwarded ports are active. No
permanent hosting or future uptime is promised. Use the local setup above if the
demo links are unavailable.

## 9. Troubleshooting

- **“Python was not found”** — install Python 3.10–3.12 and enable **Add
  python.exe to PATH**, then open a new Command Prompt.
- **Setup fails while downloading** — confirm internet access, free disk space,
  and that the extracted folder is writable; run `setup.bat` again.
- **Model download fails or startup is slow** — allow first-run internet access
  to Hugging Face and wait for model/index initialization to finish.
- **Port 8000 or 8501 is occupied** — close another service using that port,
  then restart the relevant batch file.
- **Dashboard says FastAPI is offline** — start `Start_API.bat` first and check
  <http://localhost:8000/health>.
- **A public link returns 401, 404, or 502, or shows GitHub login** — resume the
  existing Codespace, start the appropriate app, and set the forwarded port to
  **Public** in the Ports panel. Use the local launch scripts if it remains
  unavailable; Codespaces URLs are temporary.
- **Slack notifications are not delivered** — Slack is optional; configure
  `SLACK_WEBHOOK_URL` in the environment only when testing live notification
  delivery. Never put a webhook URL or other secret in the project or ZIP.
