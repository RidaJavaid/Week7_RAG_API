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

## Standalone public dashboard deployment

The selected no-cost deployment approach is Streamlit Community Cloud hosting
`dashboard/app.py` as a standalone app. It uses the same repository's
`dashboard/requirements.txt`, loads the existing document corpus, FAISS index,
sentence-transformer embeddings, BM25 retrieval, and the existing RAG answer
path directly. It does not require a separate FastAPI host, localhost, or a
Codespace. The dashboard defaults to cached-embedding reranking to avoid loading
the unused cross-encoder model.

**Status: NOT DEPLOYED OR PUBLICLY VERIFIED.** Creating the app requires the
repository owner to sign in to Streamlit Community Cloud, authorize GitHub
repository access, select `RidaJavaid/Week7_RAG_API`, branch `main`, and entry
point `dashboard/app.py`. No app URL can be supplied until that owner-controlled
authorization and deployment occur. No public RAG query or logged-out visitor
test has succeeded yet.

The app-specific requirements file is placed beside its entry point so
Community Cloud uses the lightweight CPU dependency set rather than installing
the project's test/load-testing dependencies. The Streamlit default fast-rerank
mode avoids loading the cross-encoder reranking model; the FAISS-backed semantic
retrieval and source output remain in use. First startup needs internet access
to download the sentence-transformer model. This no-cost hosted path is still
subject to provider quotas, sleeping, and resource limits; no uninterrupted or
permanent availability is guaranteed.

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

## Create and verify the standalone public dashboard

1. Sign in to Streamlit Community Cloud and authorize access to the public
   `RidaJavaid/Week7_RAG_API` GitHub repository.
2. Create an app using branch `main` and entry point `dashboard/app.py`. The
   adjacent `dashboard/requirements.txt` supplies the app dependencies.
3. Wait for the actual app build to finish, then use the URL Streamlit provides.
4. In a logged-out browser, verify the dashboard renders, submit
   `What is FAISS?`, and confirm the returned answer includes a retrieved source.
5. Record the real URL, response and verification time here only after those
   checks succeed.

The Codespace must stay active for these temporary URLs to work. No permanent
hosting or guaranteed future availability is claimed.
