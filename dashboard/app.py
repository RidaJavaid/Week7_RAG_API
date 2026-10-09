"""
Week 7 Day 5 Part C — Monitoring Dashboard
==========================================
Run with:  streamlit run dashboard/app.py
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st

st.set_page_config(
    page_title="Week 7 RAG Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Week 7 RAG API — Monitoring Dashboard")

# ─── Load benchmark data ──────────────────────────────────────────────────────
BENCHMARK_JSON = ROOT / "Week7_Submission" / "Day1" / "benchmark_summary.json"
BENCHMARK_CSV  = ROOT / "Week7_Submission" / "Day1" / "benchmark_results.csv"
QUALITY_JSON   = ROOT / "Week7_Submission" / "Day5" / "quality_report.json"

@st.cache_data
def load_benchmark():
    if BENCHMARK_JSON.exists():
        return json.loads(BENCHMARK_JSON.read_text(encoding="utf-8"))
    return None

@st.cache_data
def load_quality():
    if QUALITY_JSON.exists():
        return json.loads(QUALITY_JSON.read_text(encoding="utf-8"))
    return None

bench = load_benchmark()
qual  = load_quality()

# ─── Speed & Cost Targets ─────────────────────────────────────────────────────
TARGET_MEDIAN_S = 3.0
TARGET_P95_S    = 5.0
TARGET_COST     = 0.0

# ─── Top metrics row ─────────────────────────────────────────────────────────
st.subheader("📈 Latency Metrics")
col1, col2, col3, col4 = st.columns(4)

if bench:
    stats = bench.get("total_latency_stats", {})
    stage = bench.get("stage_stats", {})

    col1.metric(
        "Median Latency",
        f"{stats.get('median', 0):.3f}s",
        delta=f"target ≤{TARGET_MEDIAN_S}s",
        delta_color="normal" if stats.get("median", 99) <= TARGET_MEDIAN_S else "inverse",
    )
    col2.metric(
        "P95 Latency",
        f"{stats.get('p95', 0):.3f}s",
        delta=f"target ≤{TARGET_P95_S}s",
        delta_color="normal" if stats.get("p95", 99) <= TARGET_P95_S else "inverse",
    )
    col3.metric(
        "Mean Latency",
        f"{stats.get('mean', 0):.3f}s",
    )
    col4.metric(
        "Paid API Cost / Request",
        "$0.000000",
        delta="Local models only",
        delta_color="off",
    )
else:
    st.warning(
        "Benchmark data not found. "
        "Run `python run_benchmark.py` to generate it."
    )

# ─── Stage breakdown ─────────────────────────────────────────────────────────
if bench:
    st.subheader("⏱ Per-Stage Median Latency")
    stage_stats = bench.get("stage_stats", {})
    stage_cols = st.columns(len(stage_stats))
    for col, (stage_name, s) in zip(stage_cols, stage_stats.items()):
        col.metric(stage_name, f"{s.get('median', 0):.4f}s")

    slowest = bench.get("slowest_stage", "Unknown")
    st.info(f"🐢 Slowest stage: **{slowest}**")

# ─── Latency chart ───────────────────────────────────────────────────────────
CHART_PATH = ROOT / "Week7_Submission" / "Day1" / "latency_chart.png"
if CHART_PATH.exists():
    st.subheader("📉 Latency Chart (10 Runs)")
    st.image(str(CHART_PATH), use_column_width=True)

# ─── CSV table ───────────────────────────────────────────────────────────────
if BENCHMARK_CSV.exists():
    try:
        import pandas as pd
        df = pd.read_csv(BENCHMARK_CSV)
        st.subheader("📋 Benchmark Run Details")
        st.dataframe(df[[
            "run", "total_latency_s", "embedding_s",
            "retrieval_s", "reranking_s", "generation_s", "api_cost_usd"
        ]])
    except Exception:
        pass

# ─── Quality score ────────────────────────────────────────────────────────────
st.subheader("🎯 Retrieval Quality")
if qual:
    q_col1, q_col2, q_col3 = st.columns(3)
    q_col1.metric("Mean Quality Score",   f"{qual.get('mean_score', 0):.4f}")
    q_col2.metric("Quality Threshold",    f"{qual.get('threshold', 0.4):.2f}")
    q_col3.metric("Evaluation Passed",    "✅ YES" if qual.get("passed") else "❌ NO")

    if qual.get("results"):
        import pandas as pd
        qdf = pd.DataFrame(qual["results"])[["id", "question", "score"]]
        st.dataframe(qdf)
else:
    st.info(
        "Quality report not found. "
        "Run `python evaluate_quality.py --output Week7_Submission/Day5/quality_report.json`."
    )

# ─── Cost section ─────────────────────────────────────────────────────────────
st.subheader("💰 Cost Analysis")
st.markdown("""
| Item | Value |
|------|-------|
| Embedding model | `all-MiniLM-L6-v2` (local) |
| Reranking model | `cross-encoder/ms-marco-MiniLM-L-6-v2` (local) |
| Vector search | FAISS IndexFlatIP (local) |
| Keyword search | BM25Okapi (local) |
| Paid API calls per request | **0** |
| Paid API cost per request | **$0.000000** |
| Infrastructure cost | Excluded from API cost |
""")

# ─── Speed & cost targets summary ─────────────────────────────────────────────
st.subheader("🏁 Targets vs Measured")
if bench:
    stats = bench.get("total_latency_stats", {})
    t_data = {
        "Metric": ["Median latency", "P95 latency", "API cost/req"],
        "Target": [f"≤{TARGET_MEDIAN_S}s", f"≤{TARGET_P95_S}s", "$0.000000"],
        "Measured": [
            f"{stats.get('median', 0):.4f}s",
            f"{stats.get('p95', 0):.4f}s",
            "$0.000000",
        ],
        "Status": [
            "✅ MET" if stats.get("median", 99) <= TARGET_MEDIAN_S else "⚠️ OVER",
            "✅ MET" if stats.get("p95",    99) <= TARGET_P95_S    else "⚠️ OVER",
            "✅ MET",
        ],
    }
    import pandas as pd
    st.dataframe(pd.DataFrame(t_data))

st.markdown("---")
st.caption("Week 7 RAG API Dashboard — built with Streamlit")
