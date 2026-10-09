"""
Week 7 Day 4 — Auto-ingestion tests.

Test A: Same valid document 3x → 1 indexed, 2 skipped.
Test B: Invalid document → dead_letter folder.
Test C: Notification integration test (marked pending if no webhook).

Run with:  pytest tests/test_auto_ingest.py -v
"""

import os
import tempfile
import time
from pathlib import Path

import pytest

import ingestion
import auto_ingest


def _patch_auto_ingest(tmp_path):
    """Return a context-free override dict for auto_ingest paths."""
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    registry = tmp_path / "registry.json"
    return docs_dir, registry


# ─────────────────────────────────────────────────────────────
# Test A — Three ingestions of the same document
# ─────────────────────────────────────────────────────────────

def test_A_same_document_three_times(tmp_path):
    """
    Exactly one successful indexing, two duplicate skips.
    Index count must not grow after second and third ingestion.
    """
    incoming = tmp_path / "incoming"
    dead_letter = tmp_path / "dead_letter"
    incoming.mkdir()
    dead_letter.mkdir()

    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    registry_file = tmp_path / "registry.json"
    jobs_file = tmp_path / "jobs.jsonl"

    # Patch auto_ingest globals
    orig_watch = auto_ingest.WATCH_FOLDER
    orig_dead  = auto_ingest.DEAD_LETTER_FOLDER
    orig_jobs  = auto_ingest.JOB_LOG_FILE
    orig_ingest_docs = ingestion.DOCS_DIR
    orig_ingest_reg  = ingestion.REGISTRY_FILE

    auto_ingest.WATCH_FOLDER       = incoming
    auto_ingest.DEAD_LETTER_FOLDER = dead_letter
    auto_ingest.JOB_LOG_FILE       = jobs_file
    ingestion.DOCS_DIR             = docs_dir
    ingestion.REGISTRY_FILE        = registry_file

    try:
        content = b"Week 7 Day 4 Test A: stable document for deduplication testing."
        filename = "test_a_doc.txt"

        results = []
        for i in range(3):
            file_path = incoming / filename
            file_path.write_bytes(content)
            job = auto_ingest.process_file(file_path)
            results.append(job)
            # Clean up incoming (simulate file being moved/consumed)
            if file_path.exists():
                file_path.unlink()

        statuses = [r["status"] for r in results]
        print("\nTest A results:", statuses)
        print("Ingest statuses:", [r.get("ingest_status") for r in results])

        assert results[0]["status"] == "success",            f"Run 1: {results[0]}"
        assert results[1]["status"] == "skipped_duplicate",  f"Run 2: {results[1]}"
        assert results[2]["status"] == "skipped_duplicate",  f"Run 3: {results[2]}"

        # Only one file in documents/
        stored = list(docs_dir.glob("*.txt"))
        assert len(stored) == 1, f"Expected 1 stored file, got {len(stored)}"

        print("✓ Test A PASSED")

    finally:
        auto_ingest.WATCH_FOLDER       = orig_watch
        auto_ingest.DEAD_LETTER_FOLDER = orig_dead
        auto_ingest.JOB_LOG_FILE       = orig_jobs
        ingestion.DOCS_DIR             = orig_ingest_docs
        ingestion.REGISTRY_FILE        = orig_ingest_reg


# ─────────────────────────────────────────────────────────────
# Test B — Invalid document goes to dead_letter
# ─────────────────────────────────────────────────────────────

def test_B_invalid_document_dead_letter(tmp_path):
    """Empty document must land in dead_letter with an error record."""
    incoming    = tmp_path / "incoming"
    dead_letter = tmp_path / "dead_letter"
    incoming.mkdir()
    dead_letter.mkdir()
    jobs_file = tmp_path / "jobs.jsonl"

    orig_watch = auto_ingest.WATCH_FOLDER
    orig_dead  = auto_ingest.DEAD_LETTER_FOLDER
    orig_jobs  = auto_ingest.JOB_LOG_FILE

    auto_ingest.WATCH_FOLDER       = incoming
    auto_ingest.DEAD_LETTER_FOLDER = dead_letter
    auto_ingest.JOB_LOG_FILE       = jobs_file

    try:
        bad_file = incoming / "empty_doc.txt"
        bad_file.write_bytes(b"   \n\n  ")  # whitespace only

        job = auto_ingest.process_with_retry(bad_file)

        print("\nTest B job:", job)
        assert job["status"] == "dead_letter", f"Expected dead_letter, got {job['status']}"
        assert job["error"] is not None
        # File should be in dead_letter now
        dead_files = list(dead_letter.glob("*"))
        assert len(dead_files) >= 1, "Expected at least one file in dead_letter"
        # Job log should contain the record
        assert jobs_file.exists()
        log_content = jobs_file.read_text()
        assert "dead_letter" in log_content

        print("✓ Test B PASSED")

    finally:
        auto_ingest.WATCH_FOLDER       = orig_watch
        auto_ingest.DEAD_LETTER_FOLDER = orig_dead
        auto_ingest.JOB_LOG_FILE       = orig_jobs


# ─────────────────────────────────────────────────────────────
# Test C — Notification (pending integration test)
# ─────────────────────────────────────────────────────────────

@pytest.mark.skipif(
    not os.environ.get("SLACK_WEBHOOK_URL"),
    reason="PENDING INTEGRATION TEST: SLACK_WEBHOOK_URL not set. "
           "Set the environment variable to run the live notification test.",
)
def test_C_slack_notification_live():
    """Live Slack notification test — only runs when SLACK_WEBHOOK_URL is set."""
    sent = auto_ingest.send_notification("Week 7 Day 4 Test C: Live notification test ✅")
    assert sent, "Slack notification failed"
    print("✓ Test C PASSED — live Slack notification sent")


def test_C_notification_without_webhook_logs():
    """Without a webhook URL, notification falls back to logging (returns True)."""
    orig = auto_ingest.SLACK_WEBHOOK_URL
    auto_ingest.SLACK_WEBHOOK_URL = ""
    try:
        result = auto_ingest.send_notification("Test fallback log notification")
        assert result is True
    finally:
        auto_ingest.SLACK_WEBHOOK_URL = orig
