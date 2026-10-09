# 🌐 Day 2 — FastAPI & Streaming Report

**Week 7 RAG API | Day 2 Complete**

---

## Endpoints Verified

| Endpoint | Method | Purpose | Status |
|----------|--------|---------|--------|
| `/` | GET | Home / status | ✅ |
| `/health` | GET | Health check | ✅ |
| `/ask` | POST | Q&A with timing | ✅ |
| `/ask/stream` | POST | Streaming response | ✅ |
| `/ingest` | POST | Document ingestion | ✅ |

---

## Validation Behaviour

| Input | Expected | Actual |
|-------|----------|--------|
| Empty question `""` | 422 | 422 ✅ |
| Whitespace `"   "` | 422 | 422 ✅ |
| Too short `"ab"` | 422 | 422 ✅ |
| Too long (501 chars) | 422 | 422 ✅ |
| Missing field `{}` | 422 | 422 ✅ |
| Null question | 422 | 422 ✅ |
| Valid question | 200 | 200 ✅ |

---

## Streaming Honesty Note

`POST /ask/stream` streams the **answer text word-by-word** with a 30ms delay
between words using `asyncio.sleep`. The underlying RAG pipeline itself is
**not** streamed — it runs synchronously and returns a complete answer, which is
then emitted incrementally via `StreamingResponse`. This is word-level streaming
of a pre-computed answer, not token-level streaming from a generative model.

---

## Error Handling

- `500` returned for unexpected internal errors
- `504` returned for timeout (step or total budget exceeded)
- `400` returned for invalid document ingestion content
- `422` returned for Pydantic validation failures
- All errors logged via Python `logging` — no secrets exposed in logs

---

## HTTP Status Code Coverage

| Code | Trigger |
|------|---------|
| 200 | Successful ask / ingest |
| 422 | Pydantic validation failure |
| 400 | ValueError in ingestion |
| 500 | Unexpected server error |
| 504 | CostTracker timeout exceeded |

---

## Test Suite

```
tests/test_api.py
```

Tests cover: valid requests, invalid requests (all edge cases),
streaming endpoint, ingest endpoint, duplicate detection.

---

## Swagger UI

Available at: `http://localhost:8000/docs`
(Start with: `uvicorn main:app --reload`)

---

*See `API_test_results.md` and `API_documentation.md` for full detail.*
