"""
Week 7 Day 2 — FastAPI endpoint tests.
Run with:  pytest tests/test_api.py -v
"""

import pytest
from fastapi.testclient import TestClient

# Import app — this also triggers model loading
from main import app

client = TestClient(app)


# ─────────────────────────────────────────────
# Health & home
# ─────────────────────────────────────────────

def test_health_returns_200():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_home_returns_200():
    r = client.get("/")
    assert r.status_code == 200
    assert "status" in r.json()


# ─────────────────────────────────────────────
# POST /ask — valid requests
# ─────────────────────────────────────────────

def test_ask_valid_question():
    r = client.post("/ask", json={"question": "What is RAG?"})
    assert r.status_code == 200
    body = r.json()
    assert "answer" in body
    assert isinstance(body["answer"], str)
    assert "total_latency_seconds" in body


def test_ask_returns_timing_fields():
    r = client.post("/ask", json={"question": "How does FAISS work?"})
    assert r.status_code == 200
    body = r.json()
    assert "steps" in body
    assert "total_time_seconds" in body
    assert body["total_latency_seconds"] > 0


def test_ask_returns_source():
    r = client.post("/ask", json={"question": "What is BM25?"})
    assert r.status_code == 200
    body = r.json()
    # source can be a string or None; just confirm key exists
    assert "source" in body


# ─────────────────────────────────────────────
# POST /ask — invalid requests (validation)
# ─────────────────────────────────────────────

def test_ask_empty_question_rejected():
    r = client.post("/ask", json={"question": ""})
    assert r.status_code == 422


def test_ask_whitespace_only_rejected():
    # strip() makes it < 3 chars → validator raises ValueError → 422
    r = client.post("/ask", json={"question": "   "})
    assert r.status_code == 422


def test_ask_too_short_rejected():
    r = client.post("/ask", json={"question": "ab"})
    assert r.status_code == 422


def test_ask_too_long_rejected():
    r = client.post("/ask", json={"question": "x" * 501})
    assert r.status_code == 422


def test_ask_missing_field_rejected():
    r = client.post("/ask", json={})
    assert r.status_code == 422


def test_ask_wrong_type_rejected():
    r = client.post("/ask", json={"question": 12345})
    # Pydantic will coerce int to str "12345" (len 5 ≥ 3), so 200 is also
    # acceptable.  Just confirm no server crash.
    assert r.status_code in (200, 422)


def test_ask_null_question_rejected():
    r = client.post("/ask", json={"question": None})
    assert r.status_code == 422


# ─────────────────────────────────────────────
# POST /ask/stream
# ─────────────────────────────────────────────

def test_stream_valid_question():
    r = client.post("/ask/stream", json={"question": "What is RAG?"})
    assert r.status_code == 200
    text = r.text
    assert len(text) > 0


def test_stream_invalid_rejected():
    r = client.post("/ask/stream", json={"question": ""})
    assert r.status_code == 422


def test_stream_emits_words():
    r = client.post("/ask/stream", json={"question": "What is FAISS?"})
    assert r.status_code == 200
    # Should have at least one word in the streamed body
    assert r.text.strip() != ""


# ─────────────────────────────────────────────
# POST /ingest
# ─────────────────────────────────────────────

def test_ingest_valid_document():
    r = client.post("/ingest", json={
        "filename": "test_day2.txt",
        "content": "This is a test document for Day 2 API testing."
    })
    assert r.status_code == 200
    body = r.json()
    assert body["status"] in ("indexed", "skipped")


def test_ingest_duplicate_returns_skipped():
    payload = {
        "filename": "dup_test.txt",
        "content": "Duplicate detection test content for Week 7 Day 2."
    }
    r1 = client.post("/ingest", json=payload)
    r2 = client.post("/ingest", json=payload)
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r2.json()["status"] == "skipped"


def test_ingest_empty_content_rejected():
    r = client.post("/ingest", json={"filename": "empty.txt", "content": ""})
    assert r.status_code == 422


def test_ingest_empty_filename_rejected():
    r = client.post("/ingest", json={"filename": "", "content": "Some content"})
    assert r.status_code == 422


def test_ingest_missing_fields_rejected():
    r = client.post("/ingest", json={"filename": "only_name.txt"})
    assert r.status_code == 422
