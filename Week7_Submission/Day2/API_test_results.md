# API Test Results — Week 7 Day 2

## Test Suite: `tests/test_api.py`

Run command:
```bash
python -m pytest tests/test_api.py -v
```

**Note:** API tests require model loading (~30–60s first run).
Run together with other tests: `python run_tests.py`

## Test Cases

| Test | Expected | Description |
|------|----------|-------------|
| `test_health_returns_200` | 200 | GET /health returns healthy |
| `test_home_returns_200` | 200 | GET / returns status |
| `test_ask_valid_question` | 200 | Normal Q&A works |
| `test_ask_returns_timing_fields` | 200 | Response includes steps + latency |
| `test_ask_returns_source` | 200 | Response includes source field |
| `test_ask_empty_question_rejected` | 422 | Empty string rejected |
| `test_ask_whitespace_only_rejected` | 422 | Whitespace-only rejected |
| `test_ask_too_short_rejected` | 422 | <3 chars rejected |
| `test_ask_too_long_rejected` | 422 | >500 chars rejected |
| `test_ask_missing_field_rejected` | 422 | Missing question field |
| `test_ask_wrong_type_rejected` | 200 or 422 | Int coerced to str |
| `test_ask_null_question_rejected` | 422 | Null question rejected |
| `test_stream_valid_question` | 200 | Streaming returns text |
| `test_stream_invalid_rejected` | 422 | Empty stream request rejected |
| `test_stream_emits_words` | 200 | Streamed body is non-empty |
| `test_ingest_valid_document` | 200 | Document indexed or skipped |
| `test_ingest_duplicate_returns_skipped` | 200 | Second ingest = skipped |
| `test_ingest_empty_content_rejected` | 422 | Empty content rejected |
| `test_ingest_empty_filename_rejected` | 422 | Empty filename rejected |
| `test_ingest_missing_fields_rejected` | 422 | Missing content field |

## HTTP Status Codes Verified

| Code | Trigger | Verified |
|------|---------|----------|
| 200 | Valid ask / stream / ingest | YES |
| 422 | Pydantic validation failure | YES |
| 400 | ValueError in ingestion | YES (unit) |
| 500 | Unexpected internal error | YES (unit) |
| 504 | CostTracker timeout | YES (unit) |

## Streaming Behaviour

`POST /ask/stream` emits the full answer word-by-word using `asyncio.sleep(0.03)`.
The underlying generation is NOT streamed — the full answer is computed first,
then emitted incrementally. This is honest word-level streaming of a
pre-computed extractive answer.

## Swagger Evidence

Start the server and visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

Command: `uvicorn main:app --reload --host 0.0.0.0 --port 8000`
