# Duplicate Ingestion Test Results — Week 7 Day 3

## MANDATORY TEST: 3× Same Document

Test file: `tests/test_ingestion_day3.py::test_same_document_three_times_mandatory`

### Test Setup

**Content:** `b"RAG combines document retrieval with answer generation."`
**Filename:** `mandatory_test.txt`
**Hash (SHA-256):** `dfe3...` (full hash printed in test output)

### Test Execution

```python
r1 = ingest_document(filename, content)
r2 = ingest_document(filename, content)
r3 = ingest_document(filename, content)
```

### Results

| Attempt | Status | Reason |
|---------|--------|--------|
| 1 | **indexed** | New document |
| 2 | **skipped** | Duplicate document |
| 3 | **skipped** | Duplicate document |

### Index Verification

| Metric | Before any attempt | After attempt 1 | After attempts 2 & 3 |
|--------|-------------------|----------------|----------------------|
| Files on disk | 0 | 1 | 1 (unchanged) |
| Registry entries | 0 | 1 | 1 (unchanged) |

**Conclusion:** Exactly one file was stored. The registry correctly detected the
duplicate hash on attempts 2 and 3, returning `status=skipped` without writing
any additional files or index entries.

### Test Output (pytest)

```
tests/test_ingestion_day3.py::test_same_document_three_times_mandatory PASSED [  5%]
```

## Idempotency Guarantees

1. **Hash-based deduplication:** SHA-256 of content bytes is computed before ingestion.
2. **Registry lookup:** If hash exists in `indexed_documents.json`, ingestion returns `skipped`.
3. **Atomic writes:** Registry updates use temp file + `os.replace()` — crash-safe.
4. **Stored filename:** Each document is stored as `<sha256>.txt` — prevents overwrites.

## Additional Test Cases

| Test | Result |
|------|--------|
| `test_different_content_gets_indexed_separately` | PASSED |
| `test_empty_content_raises_value_error` | PASSED |
| `test_whitespace_only_raises_value_error` | PASSED |
| `test_hash_is_sha256` | PASSED |
| `test_registry_persists_across_calls` | PASSED |
