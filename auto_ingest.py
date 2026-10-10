"""
Week 7 Day 4 — Automated Ingestion Watcher
===========================================
Watches the `incoming/` folder for new .txt files.
For each file:
  1. Validate content
  2. SHA-256 deduplication check
  3. Ingest via existing ingestion.py pipeline
  4. Rebuild FAISS index
  5. Send Slack / email notification (optional)
  6. Retry with backoff on transient errors
  7. Move permanently failed files to `dead_letter/`

Configuration via environment variables:
  WATCH_FOLDER       — folder to watch          (default: ./incoming)
  DEAD_LETTER_FOLDER — folder for failed files  (default: ./dead_letter)
  MAX_RETRIES        — max retry attempts        (default: 3)
  RETRY_BACKOFF_S    — base backoff seconds      (default: 2)
  SLACK_WEBHOOK_URL  — optional Slack webhook
  NOTIFY_EMAIL       — optional email address

Usage:
  python auto_ingest.py
  python auto_ingest.py --once    # process existing files then exit
"""

import hashlib
import json
import logging
import os
import re
import shutil
import time
from pathlib import Path
import argparse

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ─── Configuration ─────────────────────────────────────────────────────────────
BASE_DIR          = Path(__file__).resolve().parent
WATCH_FOLDER      = Path(os.environ.get("WATCH_FOLDER",       BASE_DIR / "incoming"))
DEAD_LETTER_FOLDER = Path(os.environ.get("DEAD_LETTER_FOLDER", BASE_DIR / "dead_letter"))
MAX_RETRIES       = int(os.environ.get("MAX_RETRIES",       "3"))
RETRY_BACKOFF_S   = float(os.environ.get("RETRY_BACKOFF_S", "2"))
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "")
NOTIFY_EMAIL      = os.environ.get("NOTIFY_EMAIL", "")
JOB_LOG_FILE      = BASE_DIR / "auto_ingest_jobs.jsonl"

WATCH_FOLDER.mkdir(parents=True, exist_ok=True)
DEAD_LETTER_FOLDER.mkdir(parents=True, exist_ok=True)


# ─── Notification ─────────────────────────────────────────────────────────────

def send_notification(message: str) -> bool:
    """Send Slack or log notification. Returns True if sent."""
    if SLACK_WEBHOOK_URL:
        import urllib.request
        for attempt in range(2):
            try:
                payload = json.dumps({"text": message}).encode()
                req = urllib.request.Request(
                    SLACK_WEBHOOK_URL,
                    data=payload,
                    headers={"Content-Type": "application/json"},
                )
                with urllib.request.urlopen(req, timeout=20) as resp:
                    ok = resp.status == 200
                    logger.info("Slack notification sent: %s", ok)
                    return ok
            except Exception as exc:
                if attempt == 0:
                    time.sleep(1)
                    continue
                err_msg = re.sub(r"https?://\S+", "[REDACTED_URL]", str(exc))
                logger.warning("Slack notification failed: %s", err_msg)
                return False
    else:
        logger.info("NOTIFICATION (no webhook configured): %s", message)
        return True  # logged successfully


# ─── Job logger ───────────────────────────────────────────────────────────────

def log_job(record: dict):
    with open(JOB_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


# ─── Validation ───────────────────────────────────────────────────────────────

def validate_document(path: Path) -> bytes:
    """Read and validate a document file. Returns content bytes."""
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if path.suffix.lower() not in (".txt", ".md"):
        raise ValueError(f"Unsupported file type: {path.suffix}")
    content = path.read_bytes()
    if not content.strip():
        raise ValueError("Document is empty or whitespace only")
    if len(content) > 500_000:
        raise ValueError(f"Document too large: {len(content)} bytes")
    return content


# ─── Process one file ─────────────────────────────────────────────────────────

def process_file(path: Path) -> dict:
    """
    Validate → deduplicate → ingest → rebuild index → notify.
    Returns a job record dict.
    """
    import ingestion
    from rag import rebuild_index

    filename = path.name
    job = {
        "filename": filename,
        "path": str(path),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "status": "pending",
        "error": None,
        "hash": None,
        "index_vectors": None,
    }

    # Validate
    content = validate_document(path)

    # Hash
    doc_hash = hashlib.sha256(content).hexdigest()
    job["hash"] = doc_hash

    # Ingest (idempotent)
    result = ingestion.ingest_document(filename, content)
    job["ingest_status"] = result["status"]

    if result["status"] == "skipped":
        job["status"] = "skipped_duplicate"
        logger.info("DUPLICATE — %s (hash %s)", filename, doc_hash[:16])
        log_job(job)
        return job

    # Rebuild index
    total_vectors = rebuild_index()
    job["index_vectors"] = total_vectors
    job["status"] = "success"
    logger.info(
        "INDEXED — %s → %d vectors in FAISS", filename, total_vectors
    )

    # Notify
    msg = f"✅ Indexed: `{filename}` — {total_vectors} total vectors."
    send_notification(msg)

    log_job(job)
    return job


# ─── Retry wrapper ────────────────────────────────────────────────────────────

def process_with_retry(path: Path) -> dict:
    """Attempt process_file up to MAX_RETRIES times with exponential backoff."""
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return process_file(path)
        except (FileNotFoundError, ValueError) as exc:
            # Permanent failures — no retry
            logger.error("PERMANENT FAILURE — %s: %s", path.name, exc)
            return _send_to_dead_letter(path, str(exc))
        except Exception as exc:
            last_error = exc
            wait = RETRY_BACKOFF_S * (2 ** (attempt - 1))
            logger.warning(
                "Attempt %d/%d failed for %s: %s. Retrying in %.1fs …",
                attempt, MAX_RETRIES, path.name, exc, wait,
            )
            time.sleep(wait)

    # All retries exhausted
    logger.error("ALL RETRIES EXHAUSTED — %s", path.name)
    return _send_to_dead_letter(path, str(last_error))


def _send_to_dead_letter(path: Path, error: str) -> dict:
    dest = DEAD_LETTER_FOLDER / path.name
    # Avoid clobbering
    if dest.exists():
        dest = DEAD_LETTER_FOLDER / f"{path.stem}_{int(time.time())}{path.suffix}"
    try:
        shutil.move(str(path), str(dest))
    except Exception as mv_err:
        logger.error("Could not move to dead_letter: %s", mv_err)

    job = {
        "filename": path.name,
        "path": str(path),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "status": "dead_letter",
        "error": error,
        "dead_letter_path": str(dest),
    }
    log_job(job)

    msg = f"❌ Failed ingestion: `{path.name}` → dead_letter. Error: {error}"
    send_notification(msg)
    return job


# ─── Watcher loop ─────────────────────────────────────────────────────────────

def watch(once: bool = False):
    """
    Poll WATCH_FOLDER every 5 seconds for new .txt / .md files.
    If once=True, process existing files then exit.
    """
    processed = set()

    logger.info("Auto-ingest watcher started.")
    logger.info("Watching: %s", WATCH_FOLDER)
    logger.info("Dead-letter: %s", DEAD_LETTER_FOLDER)

    try:
        while True:
            for path in sorted(WATCH_FOLDER.glob("*.txt")) + sorted(WATCH_FOLDER.glob("*.md")):
                if path in processed:
                    continue
                processed.add(path)
                logger.info("Detected new file: %s", path.name)
                job = process_with_retry(path)
                logger.info("Job result: %s — %s", job["filename"], job["status"])

            if once:
                break
            time.sleep(5)
    except KeyboardInterrupt:
        logger.info("Watcher stopped by user.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto-ingest watcher")
    parser.add_argument("--once", action="store_true",
                        help="Process existing files then exit")
    args = parser.parse_args()
    watch(once=args.once)
