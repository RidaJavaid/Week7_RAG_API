# Week 7 RAG API Documentation

**Base URL:** `http://localhost:8000`
**Swagger UI:** `http://localhost:8000/docs`
**ReDoc:** `http://localhost:8000/redoc`

---

## GET /

Returns API status.

**Response 200:**
```json
{
  "status": "running",
  "message": "Week 7 RAG API",
  "performance_tracking": "enabled"
}
```

---

## GET /health

Health probe for load balancers and CI.

**Response 200:**
```json
{"status": "healthy"}
```

---

## POST /ask

Ask a question against the indexed documents.

**Request body:**
```json
{"question": "What is FAISS?"}
```

**Constraints:**
- `question`: string, 3–500 characters (trimmed)

**Response 200:**
```json
{
  "answer": "FAISS is a library for efficient similarity search over vector embeddings.",
  "source": "rag_notes.txt",
  "steps": [
    {"step": "Embedding",  "time_seconds": 5.60, "estimated_cost_usd": 0.0},
    {"step": "Retrieval",  "time_seconds": 0.001, "estimated_cost_usd": 0.0},
    {"step": "Reranking",  "time_seconds": 10.23, "estimated_cost_usd": 0.0},
    {"step": "Generation", "time_seconds": 0.0002, "estimated_cost_usd": 0.0}
  ],
  "total_time_seconds": 15.83,
  "estimated_api_cost_usd": 0.0,
  "total_latency_seconds": 15.84
}
```

**Error codes:**
- `422` — validation error (empty, too short, too long, missing field)
- `500` — internal server error
- `504` — timeout

---

## POST /ask/stream

Streams the answer word-by-word.

**Request body:** Same as `/ask`

**Response 200:** `text/plain` stream
```
FAISS is a library for efficient similarity search over vector embeddings. [Source: rag_notes.txt]
```
Words are emitted with 30ms gaps. The full answer is computed before streaming begins.

---

## POST /ingest

Index a new document.

**Request body:**
```json
{
  "filename": "my_doc.txt",
  "content": "Document text content here..."
}
```

**Constraints:**
- `filename`: 1–255 characters
- `content`: 1–100,000 characters

**Response 200 (new document):**
```json
{
  "status": "indexed",
  "filename": "<sha256hash>.txt",
  "hash": "<sha256>",
  "total_vectors": 5
}
```

**Response 200 (duplicate):**
```json
{
  "status": "skipped",
  "reason": "Duplicate document",
  "hash": "<sha256>"
}
```

**Error codes:**
- `422` — validation failure
- `400` — empty content after decoding
- `500` — ingestion error

---

## Security Notes

- Documents are stored using SHA-256 content hash as filename — prevents overwrite attacks
- Registry file uses atomic write (temp file + os.replace) — crash-safe
- No API keys are stored or logged
- Ingestion lock prevents concurrent index corruption
