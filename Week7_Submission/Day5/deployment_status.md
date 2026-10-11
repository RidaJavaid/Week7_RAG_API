# Public Deployment Evidence — Week 7 Day 5

## Hosting and current availability

The old public URLs used GitHub Codespaces forwarded ports. Codespaces is
temporary hosting, not a permanent deployment; those URLs require the Codespace
to remain active and the ports to remain forwarded and public. Do not assume
future uptime.

| Service | Public URL | Latest Codespaces check, October 11, 2026 |
|---|---|---|
| Streamlit dashboard | https://psychic-bassoon-q7p4xrq7vr6934q7v-8501.app.github.dev/ | HTTP 200 after redirect, but response was GitHub Codespaces authentication-gateway HTML, not the dashboard. Not publicly verified. |
| FastAPI root | https://psychic-bassoon-q7p4xrq7vr6934q7v-8000.app.github.dev/ | Not verified. |
| FastAPI health | https://psychic-bassoon-q7p4xrq7vr6934q7v-8000.app.github.dev/health | HTTP 200 after redirect, but response was GitHub Codespaces authentication-gateway HTML, not `{"status":"healthy"}`. Not publicly verified. |
| FastAPI Swagger | https://psychic-bassoon-q7p4xrq7vr6934q7v-8000.app.github.dev/docs | HTTP 200 after redirect, but response was GitHub Codespaces authentication-gateway HTML, not Swagger. Not publicly verified. |
| FastAPI ask | https://psychic-bassoon-q7p4xrq7vr6934q7v-8000.app.github.dev/ask | POST `{"question":"What is FAISS?"}` returned HTTP 401. No RAG answer was received. |

GitHub's Codespaces list showed the existing `psychic bassoon` Codespace as
**Active**. However, its browser VS Code session logged repeated HTTP 504 and
connection/authentication errors. The host probes also previously returned 404.
The latest 200 responses above were the GitHub authentication gateway (identified
by its `authUrl` page metadata), not application responses. Public access without
GitHub authentication, both Public port settings, and both running application
processes could not be confirmed. No deployment result is claimed as live.

The project owner previously reported successful Incognito dashboard and API
checks on October 10, 2026. Those are historical owner-reported results, not
verification of the current deployment.

## Public Streamlit Community Cloud dashboard

**URL:** https://week7ragapi-wtq6v9sv6sbwudtzgtfq7d.streamlit.app/

**Status: LIVE and browser-verified October 11, 2026.** The dashboard rendered
without a GitHub sign-in prompt. Its sidebar reported `RAG Engine: Healthy`,
`Indexed Documents: 15`, and `Reranking: cosine_fast`. A live submission of
`What is FAISS?` returned:

> FAISS is a library for efficient similarity search over dense vectors.

The response UI reported `Served via: Local Hybrid Engine (rag.py)` and a
retrieved primary source file
`a70b67df529974688113159ce1499eceb90f00e9ee7003128201b2f36778cd0f.txt`.
This verifies real retrieval against the hosted app's document corpus, FAISS
and BM25 pipeline rather than a canned answer. The application is a standalone
Streamlit dashboard; a separate public FastAPI service is not required for this
demo. The app-specific CPU dependencies are in `dashboard/requirements.txt`.

Streamlit Community Cloud is subject to provider availability, sleeping, and
resource limits. This check does not promise permanent or uninterrupted uptime.

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

## Public API status

The former Codespaces FastAPI endpoint returned authentication-gateway results
or 404 during the October 11 checks; it is not represented as live. The hosted
Streamlit demo above performs RAG directly and needs no separate API URL.

The Codespace must stay active for these temporary URLs to work. No permanent
hosting or guaranteed future availability is claimed.
