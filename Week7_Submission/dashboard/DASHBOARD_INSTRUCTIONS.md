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

| Section | Source file |
|---------|-------------|
| Median/P95/Mean latency | benchmark_summary.json |
| Per-stage breakdown | benchmark_summary.json |
| Latency chart | latency_chart.png |
| Benchmark table | benchmark_results.csv |
| Quality score | quality_report.json |
| Cost ($0.000000) | hardcoded (local models) |
| Targets table | computed at runtime |

## Streamlit note

The dashboard reads local JSON/PNG files — it does NOT connect to the API server.
No server needs to be running to view the dashboard.
