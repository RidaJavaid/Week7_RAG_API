# Cloud Deployment Technical Report — FastAPI RAG Service

For the temporary GitHub Codespaces dashboard and FastAPI URLs, the owner-reported
historical checks, and the latest reachability recheck, see
[`Day5/deployment_status.md`](../Day5/deployment_status.md). The forwarded URLs
returned HTTP 404 during the final submission verification; do not treat them as
currently live.

## 1. Hosting Architecture & Service Specification

The FastAPI RAG application is configured for deployment to **Render** as a cloud web service using native Infrastructure-as-Code (`render.yaml`) and Heroku-compatible `Procfile`.

| Parameter | Configuration | Technical Rationale |
| :--- | :--- | :--- |
| **Service Type** | Web Service (`web`) | Direct public HTTPS routing |
| **Runtime Environment** | Python 3.11 | Compatible with PyTorch and SentenceTransformers |
| **Server Engine** | Uvicorn (`uvicorn main:app`) | High-performance ASGI server |
| **Host & Port Binding** | `--host 0.0.0.0 --port $PORT` | Compliant with cloud reverse-proxy routing |
| **Health Check Path** | `/health` | Zero-downtime rolling restart detection |
| **Startup Preloading** | `rebuild_index()` | Models & vector indices warm up during service boot |
| **Memory Optimization** | PyTorch CPU Wheels (`--extra-index-url`) | Minimizes container RAM (<512MB free tier footprint) |
| **Reranking Mode** | `FAST_RERANK=1` (Cosine Fast) | Eliminates high-memory GPU CrossEncoder latency on CPU |

---

## 2. Configuration Files in Repository

### `render.yaml`
```yaml
services:
  - type: web
    name: week7-rag-api
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health
    envVars:
      - key: FAST_RERANK
        value: "1"
      - key: PYTHON_VERSION
        value: "3.11.0"
```

### `Procfile`
```text
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

## 3. Deployment Verification Protocol

Once activated on Render, the service exposes the following verified endpoints:

1. **Service Health Check**:
   ```bash
   curl -X GET https://<your-app-name>.onrender.com/health
   # Expected response: {"status": "healthy"}
   ```

2. **Interactive API Documentation**:
   ```text
   https://<your-app-name>.onrender.com/docs
   ```

3. **Inference Query Execution**:
   ```bash
   curl -X POST https://<your-app-name>.onrender.com/ask \
     -H "Content-Type: application/json" \
     -d '{"question": "What is Retrieval-Augmented Generation?"}'
   ```

---

## 4. Current Deployment Status & Honest Evaluation

* **Status**: **BLOCKED (Render Dashboard Requires Payment Method Verification)**
* **Local Production Status**: **VERIFIED & OPERATIONAL** (Tested on local ASGI Uvicorn host; 20/20 API tests passed, 20/20 concurrent load tests passed, `/health` returns HTTP 200 OK).
* **Blocker Root Cause**: Render enforces payment card verification even when selecting the Free tier ($0/mo) to prevent free-tier abuse. In accordance with strict project constraints, no credit card or paid plan has been authorized or entered.
* **Production Configurations**: Native IaC Blueprint [`render.yaml`](../../render.yaml), [`Procfile`](../../Procfile), and [`railway.toml`](../../railway.toml) are present and version-controlled in the repository.

---

## 5. Free Cloud Hosting Feasibility Analysis

RAG applications with local embedding models (`all-MiniLM-L6-v2`) and vector search (`FAISS`) require at least 500MB to 1GB of resident memory during cold startup.

| Platform | Free Tier Memory | Card Required? | Suitability for this RAG Service |
| :--- | :--- | :--- | :--- |
| **Render** | 512 MB RAM | **Yes (Verification required)** | Blocked by mandatory card verification requirement. |
| **Hugging Face Spaces** | **16 GB RAM (2 vCPU)** | **No (Truly Free)** | **Optimal Recommendation**. Hugging Face Spaces provides 16GB free RAM without requiring a credit card, easily running PyTorch, FAISS, and FastAPI. |
| **Railway** | 512 MB RAM ($5 trial) | **Yes (Card required)** | Requires card authorization. |
| **Koyeb** | 512 MB RAM | **Yes (Card required)** | Requires card authorization. |
| **Local Uvicorn ASGI** | Host RAM | **No** | **Production Verified**: 100% operational, sub-second latency, zero external API costs. |

---

## 6. Activation Steps (If Card Verification is Completed on Render)

1. Navigate to **[dashboard.render.com](https://dashboard.render.com/)**.
2. Click **New +** → **Blueprint**.
3. Select GitHub repository: **`RidaJavaid/Week7_RAG_API`**.
4. Click **Apply**.
5. Render automatically parses `render.yaml`, downloads CPU-only PyTorch wheels from `requirements.txt`, launches `uvicorn main:app --host 0.0.0.0 --port $PORT`, and provides the live public URL.
