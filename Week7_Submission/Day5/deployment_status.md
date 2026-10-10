# Public Deployment Evidence — Week 7 Day 5

## Hosting and current availability

Both deployments use GitHub Codespaces forwarded ports. Codespaces is temporary
hosting, not a permanent deployment; the public URLs require the Codespace to
remain active and the ports to remain forwarded and public. Do not assume future
uptime.

| Service | Public URL | Historical verification reported by owner | Rechecked October 10, 2026 |
|---|---|---|---|
| Streamlit dashboard | https://psychic-bassoon-q7p4xrq7vr6934q7v-8501.app.github.dev/ | Opened in Incognito without GitHub login; "What is FAISS?" returned a correct answer. | HTTP 404; not currently reachable. |
| FastAPI root | https://psychic-bassoon-q7p4xrq7vr6934q7v-8000.app.github.dev/ | GET `/` returned running status. | HTTP 404; not currently reachable. |
| FastAPI health | https://psychic-bassoon-q7p4xrq7vr6934q7v-8000.app.github.dev/health | GET `/health` returned `{"status":"healthy"}`. | HTTP 404; not currently reachable. |
| FastAPI Swagger | https://psychic-bassoon-q7p4xrq7vr6934q7v-8000.app.github.dev/docs | Swagger UI opened. | HTTP 404; not currently reachable. |
| FastAPI ask | https://psychic-bassoon-q7p4xrq7vr6934q7v-8000.app.github.dev/ask | POST `/ask` returned HTTP 200 with a RAG answer and source. | HTTP 404 host response; not currently reachable. |

The historical results in the third column were supplied by the project owner.
During this later check, direct requests to both public hosts returned HTTP 404,
including requests to `/health`, `/docs`, and the dashboard root. This indicates
the old forwarded endpoints cannot presently be confirmed live; it does not
invalidate the local verification recorded below. The Codespace owner must resume
or recreate the Codespace and re-share active public port links to restore access.

## Historical RAG query evidence

The owner reported that the dashboard answered:

- Question: `What is FAISS?`
- Answer: `FAISS is a library for efficient similarity search over dense vectors.`
- Reported response time: `0.024s`
- Engine: local hybrid RAG (`rag.py`) in the Codespace.

The owner's deployment note says the dashboard query used its local engine, not
the public FastAPI endpoint. The separate public FastAPI tests reported by the
owner were GET `/`, GET `/health`, GET `/docs`, and POST `/ask`.

## Current local ZIP verification

The extracted ZIP clean-room test independently confirmed:

- `Start_API.bat`, GET `/health` -> HTTP 200.
- GET `/docs` -> HTTP 200.
- POST `/ask` with `{"question":"What is FAISS?"}` -> HTTP 200 and a grounded
  answer with a source.
- `Start_Dashboard.bat`, dashboard root -> HTTP 200.
- Submitting the same question in the dashboard returned the same answer via
  the locally running FastAPI service.

See the ZIP-root `cleanroom_report.txt` for environment, test counts, and details.
This local test is a same-machine simulation, not a second-PC test.

## Recreate the public deployment

1. Create or resume a GitHub Codespace for the repository.
2. Install dependencies with `pip install -r requirements.txt`.
3. Start FastAPI with `FAST_RERANK=1 uvicorn main:app --host 0.0.0.0 --port 8000`.
4. Set port 8000 to **Public** in the Codespaces Ports panel.
5. Set `RAG_API_URL` to the active public port-8000 URL and start Streamlit:
   `streamlit run dashboard/app.py --server.port 8501 --server.address 0.0.0.0`.
6. Set port 8501 to **Public** and use the newly displayed forwarded URL.

The Codespace must stay active for these temporary URLs to work. No permanent
hosting or guaranteed future availability is claimed.
