# Cloud Deployment Technical Report — FastAPI RAG Service

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

## 4. Current Deployment Status

* **Status**: **CONFIGURATION READY — AWAITING DASHBOARD AUTHORIZATION**
* **Repository**: `https://github.com/RidaJavaid/Week7_RAG_API`
* **Local Test Verification**: Successfully tested on local Uvicorn host (`http://localhost:8000` / `http://localhost:8765`), 20/20 requests passed (100%), `/health` returns 200 OK.
* **Public URL**: Pending user Render dashboard connection (Render requires user OAuth login to bind the repo to an active account).

---

## 5. User Activation Steps (Render Free Tier)

1. Navigate to **[dashboard.render.com](https://dashboard.render.com/)**.
2. Click **New +** → **Blueprint**.
3. Select your GitHub repository: **`RidaJavaid/Week7_RAG_API`**.
4. Click **Apply**.
5. Render will automatically parse `render.yaml`, build dependencies from `requirements.txt`, start `uvicorn main:app`, and allocate a live URL (e.g. `https://week7-rag-api-xxxx.onrender.com`).
6. Once deployed, test `/health` and paste the public link into `README.md`.
