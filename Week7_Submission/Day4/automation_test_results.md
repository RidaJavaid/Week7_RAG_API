# Automation Test Results — Week 7 Day 4

## Test Suite: `tests/test_auto_ingest.py`

Run:
```bash
python -m pytest tests/test_auto_ingest.py -v
```

### Results Summary

| Test | Status |
|------|--------|
| `test_A_same_document_three_times` | **PASSED** |
| `test_B_invalid_document_dead_letter` | **PASSED** |
| `test_C_slack_notification_live` | **SKIPPED** (SLACK_WEBHOOK_URL not set) |
| `test_C_notification_without_webhook_logs` | **PASSED** |

---

## Test A: Same Document 3×

**Input:** Valid .txt document with stable content
**Expected:** 1 success, 2 duplicate skips, exactly 1 file on disk

**Actual results:**
```
Attempt 1: success        (status=success, ingest_status=indexed)
Attempt 2: skipped_duplicate
Attempt 3: skipped_duplicate
Files in documents/: 1
```

**Index count before:** 0 (isolated temp directory)
**Index count after all 3 attempts:** 1 file, 1 registry entry

**VERIFIED: No duplicate indexing occurred.**

---

## Test B: Invalid Document → Dead Letter

**Input:** Whitespace-only .txt file (`b"   \n\n  "`)
**Expected:** `status=dead_letter`, file moved to dead_letter folder, error record written

**Actual results:**
```
status: dead_letter
error: "Document is empty or whitespace only"
dead_letter_path: <temp>/dead_letter/empty_doc.txt
job log entry written to auto_ingest_jobs.jsonl
```

**Dead letter folder:** Contains the failed file
**Job log:** Contains JSON record with status=dead_letter + error message

**VERIFIED: Invalid document correctly routed to dead_letter.**

---

## Test C: Slack Notification

**Status:** PENDING INTEGRATION TEST

`SLACK_WEBHOOK_URL` environment variable is not set.
The test is marked `@pytest.mark.skipif` and will be skipped when the var is absent.

**Fallback verified:** Without a webhook URL, `send_notification()` logs the
message at INFO level and returns `True`. This was verified by
`test_C_notification_without_webhook_logs`.

**To enable live test:**
```bash
$env:SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/your/webhook/url"
python -m pytest tests/test_auto_ingest.py::test_C_slack_notification_live -v
```
