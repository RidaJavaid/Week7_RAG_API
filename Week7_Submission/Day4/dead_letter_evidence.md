# Dead Letter Evidence — Week 7 Day 4

## Dead Letter Folder

Path: `./dead_letter/` (configurable via `DEAD_LETTER_FOLDER` env var)

## How It Works

1. `process_with_retry()` attempts `process_file()` up to `MAX_RETRIES` times.
2. On permanent failure (empty file, unsupported type, file not found),
   `_send_to_dead_letter()` is called immediately — no retries.
3. On transient failure (unexpected exception), retries with exponential backoff:
   - Attempt 1: immediate
   - Attempt 2: wait 2s
   - Attempt 3: wait 4s
   - After 3 failures: dead_letter
4. The failed file is moved (not copied) to `./dead_letter/`.
5. A JSON job record is appended to `auto_ingest_jobs.jsonl`.
6. A notification is sent (Slack or log).

## Test B Evidence

Test input: `empty_doc.txt` containing only whitespace.

Failure path:
```
auto_ingest.process_with_retry("incoming/empty_doc.txt")
  -> auto_ingest.process_file(...)
  -> auto_ingest.validate_document(...)
  -> raises ValueError("Document is empty or whitespace only")
  -> caught as permanent failure in process_with_retry
  -> _send_to_dead_letter(path, "Document is empty or whitespace only")
  -> shutil.move("incoming/empty_doc.txt", "dead_letter/empty_doc.txt")
  -> log_job({"status": "dead_letter", "error": "Document is empty or whitespace only", ...})
```

Job record written to `auto_ingest_jobs.jsonl`:
```json
{
  "filename": "empty_doc.txt",
  "path": "incoming/empty_doc.txt",
  "timestamp": "2026-10-09T...",
  "status": "dead_letter",
  "error": "Document is empty or whitespace only",
  "dead_letter_path": "dead_letter/empty_doc.txt"
}
```

## Permanent vs Transient Failures

| Exception Type | Behaviour |
|---------------|-----------|
| `FileNotFoundError` | Immediate dead_letter (permanent) |
| `ValueError` | Immediate dead_letter (permanent) |
| Any other `Exception` | Retry with backoff, then dead_letter |

## Collision Avoidance

If a file with the same name already exists in dead_letter:
```python
dest = DEAD_LETTER_FOLDER / f"{path.stem}_{int(time.time())}{path.suffix}"
```
A timestamp suffix is added to prevent overwriting.
