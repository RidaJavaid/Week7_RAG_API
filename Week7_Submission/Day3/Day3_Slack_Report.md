# 🔒 Day 3 — Cost Infrastructure & Idempotent Ingestion

**Week 7 RAG API | Day 3 Complete**

---

## Cost / Time Tracking Layer

`cost_tracker.py` — `CostTracker` class

| Feature | Implementation |
|---------|----------------|
| Per-step timing | `time.perf_counter()` via context manager |
| Step names | Embedding, Retrieval, Reranking, Generation |
| Cost accumulation | `estimated_cost_usd` per step (0.0 for local models) |
| Max step time | 30s (configurable via `MAX_STEP_SECONDS`) |
| Max total time | 90s (configurable via `MAX_REQUEST_SECONDS`) |
| Max cost budget | $0.01 (configurable via `MAX_COST_USD`) |
| Budget enforcement | `RuntimeError: Cost budget exceeded` |
| Step timeout | `TimeoutError` if step exceeds limit |
| Report | `.get_report()` returns structured dict |

**Cost transparency:** All models are local. `estimated_cost_usd = 0.0` for every
step. This is not an approximation — there is genuinely no paid API being called.
Infrastructure costs (electricity, hardware) are excluded per assignment spec.

---

## Idempotent Ingestion

`ingestion.py` — `ingest_document(filename, content_bytes)`

| Feature | Implementation |
|---------|----------------|
| Content hash | SHA-256 of raw bytes |
| Registry | `indexed_documents.json` (persistent JSON) |
| Atomic write | temp file + `os.replace()` |
| Duplicate detection | Hash lookup before write |
| Stored filename | `<sha256>.txt` (prevents overwrite) |

---

## MANDATORY Duplicate Test — 3× Same Document

```
Attempt 1: indexed   ✅
Attempt 2: skipped   ✅  (reason: Duplicate document)
Attempt 3: skipped   ✅  (reason: Duplicate document)

Files on disk after 3 attempts: 1
Registry entries after 3 attempts: 1
```

**Index counts verified:**
- Before: 0 vectors in isolated test environment
- After attempt 1: 1 file, 1 registry entry
- After attempts 2 & 3: 1 file, 1 registry entry (unchanged)

---

## CI

GitHub Actions workflow: `.github/workflows/ci.yml`

- Triggers on every push and pull request
- Installs all dependencies from `requirements.txt`
- Runs all test suites: ingestion, cost-tracker, API, auto-ingest

---

*See `cost_tracking_tests.md` and `duplicate_ingestion_results.md` for full evidence.*
