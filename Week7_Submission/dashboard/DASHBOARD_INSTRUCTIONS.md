# Streamlit Dashboard — Launch & Screenshot Instructions

## Prerequisites

Install streamlit (included in requirements.txt):
```powershell
.\venv\Scripts\pip.exe install streamlit
```

## Generate data first (one-time)

```powershell
# 1. Run benchmark (creates benchmark_summary.json and latency_chart.png)
.\venv\Scripts\python.exe run_benchmark.py

# 2. Run quality evaluation (creates quality_report.json)
.\venv\Scripts\python.exe evaluate_quality.py --output Week7_Submission/Day5/quality_report.json
```

## Launch dashboard

```powershell
.\venv\Scripts\python.exe -m streamlit run dashboard/app.py
```

Browser opens automatically at: http://localhost:8501

## Screenshot instructions

1. Let the dashboard fully load (a few seconds)
2. Scroll to see all sections:
   - Latency metrics row (4 metric cards)
   - Per-stage breakdown
   - Latency chart image
   - Benchmark CSV table
   - Quality section
   - Cost analysis table
   - Targets vs Measured table
3. Use browser's built-in screenshot or Windows Snipping Tool (Win+Shift+S)
4. Save as: `Week7_Submission/dashboard/dashboard_screenshot.png`

## What the dashboard shows (with real data)

| Section | Source / Mechanism | Description |
|---|---|---|
| **Ask RAG Interactive UI** | Live RAG execution (`rag.py`) | Interactive question answering with live per-stage latency breakdown |
| **Median/P95/Mean latency** | `benchmark_summary.json` | Empirical 10-run microsecond latency metrics |
| **Per-stage breakdown** | `benchmark_summary.json` | Detailed chart of embedding, retrieval, reranking, and generation |
| **Latency chart** | `latency_chart.png` | Stage distribution visualization |
| **Benchmark table** | `benchmark_results.csv` | Full telemetry log across 10 benchmark queries |
| **Quality score gate** | `quality_report.json` | Official 50-question retrieval evaluation (0.6919 vs 0.40 threshold) |
| **Cost analysis** | `CostTracker` telemetry | $0.000000 per request (100% local model inference) |
| **SLA Compliance** | Real-time computation | Verification of speed, cost, and quality against production SLAs |
| **Query History** | Session state log | In-memory record of queries executed in the current session |

## Operational Modes

The dashboard functions in dual modes:
1. **Telemetry & Benchmark Mode**: Automatically loads and displays verified benchmark artifacts (`benchmark_summary.json`, `quality_report.json`, `benchmark_results.csv`) without requiring a separate backend process.
2. **Interactive Live Mode**: If the user submits a question in the "Ask RAG" panel, it executes the local hybrid retrieval engine directly to provide real-time extractive answers and stage timing telemetry.

