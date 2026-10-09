# 🤖 Day 4 — Automated Ingestion

**Week 7 RAG API | Day 4 Complete**

---

## Implementation Choice

**Plain Python polling watcher** (`auto_ingest.py`).

n8n was evaluated but not used — it adds external dependencies and deployment
complexity without providing a functional advantage for a local file-watch
pipeline. Python's `pathlib` + `time.sleep` polling achieves the same
goal with zero extra infrastructure.

---

## Workflow

```
New file in ./incoming/
  → validate (type, size, non-empty)
  → SHA-256 hash
  → check registry (duplicate?)
  → ingest_document() → store in ./documents/
  → rebuild_index() → update FAISS
  → send_notification() (Slack or log)
  → write job record to auto_ingest_jobs.jsonl
```

On failure:
```
  → retry with exponential backoff (MAX_RETRIES=3, base=2s)
  → permanent failure → move to ./dead_letter/
  → log job with status=dead_letter + error message
  → send failure notification
```

---

## Features

| Feature | Status |
|---------|--------|
| Auto-detect incoming files | ✅ poll every 5s |
| Reuse existing ingestion pipeline | ✅ |
| SHA-256 deduplication | ✅ |
| Bounded retries with backoff | ✅ 3 retries, 2s/4s/8s |
| Dead-letter folder | ✅ `./dead_letter/` |
| Structured job logs | ✅ `auto_ingest_jobs.jsonl` |
| Slack webhook notification | ✅ (requires `SLACK_WEBHOOK_URL` env var) |
| Email notification | Pending (extend `send_notification()`) |
| No hardcoded secrets | ✅ all via env vars |
| Notification failures visible | ✅ logged as WARNING |
| Retries never duplicate | ✅ dedup before ingest |

---

## Test A — Same Document 3×

```
Attempt 1: success       (indexed, 1 vector added)
Attempt 2: skipped_duplicate
Attempt 3: skipped_duplicate

Files in documents/: 1
```

## Test B — Invalid Document → Dead Letter

```
Input: empty/whitespace-only .txt file
Result: dead_letter status
Error recorded: "Document is empty or whitespace only"
File moved to ./dead_letter/
```

## Test C — Notification

```
Status: PENDING INTEGRATION TEST
Condition: SLACK_WEBHOOK_URL not set in environment.
To enable: export SLACK_WEBHOOK_URL=https://hooks.slack.com/...
           pytest tests/test_auto_ingest.py::test_C_slack_notification_live -v
Without webhook: notification falls back to Python logging (verified ✅)
```

---

## Startup Instructions

```bash
# Option 1: run once (process existing files then exit)
python auto_ingest.py --once

# Option 2: continuous watcher
python auto_ingest.py

# Option 3: custom folders
WATCH_FOLDER=./inbox DEAD_LETTER_FOLDER=./failed python auto_ingest.py

# With Slack notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/... python auto_ingest.py
```

---

## What Broke and How It Was Fixed

1. **Issue:** `watchdog` filesystem events (inotify/kqueue) were not reliably available on all platforms.
   **Fix:** Replaced watchdog-based approach with a simple polling loop — cross-platform, no additional system permissions required.

2. **Issue:** `process_file` imported `rag.rebuild_index` at call time; if called before model load it would fail.
   **Fix:** Import moved inside the function body — deferred until the server has loaded models.

3. **Issue:** Dead-letter move could silently fail if destination already existed.
   **Fix:** Added timestamp suffix to filename when collision detected.

4. **Issue:** Retries could potentially duplicate if the hash registry was not flushed before the next retry.
   **Fix:** `ingest_document` always checks the registry before writing — deduplication is guaranteed on every call, including retries.

---

*See `automation_test_results.md` and `dead_letter_evidence.md` for full logs.*
