"""
Week 7 Day 3 — Idempotent ingestion tests.
MANDATORY: Same document 3x → indexed, skipped, skipped.
Run with:  pytest tests/test_ingestion_day3.py -v
"""

import tempfile
from pathlib import Path

import ingestion


def _isolated_ingest(docs_dir, registry_file, filename, content_bytes):
    """Call ingestion.ingest_document with temporarily patched paths."""
    orig_docs = ingestion.DOCS_DIR
    orig_reg = ingestion.REGISTRY_FILE
    try:
        ingestion.DOCS_DIR = docs_dir
        ingestion.REGISTRY_FILE = registry_file
        return ingestion.ingest_document(filename, content_bytes)
    finally:
        ingestion.DOCS_DIR = orig_docs
        ingestion.REGISTRY_FILE = orig_reg


# ─────────────────────────────────────────────────────────────
# MANDATORY TEST: same document three times
# ─────────────────────────────────────────────────────────────

def test_same_document_three_times_mandatory():
    """
    Attempt 1: indexed
    Attempt 2: skipped (duplicate)
    Attempt 3: skipped (duplicate)
    Exactly one file on disk, one registry entry.
    """
    content = b"RAG combines document retrieval with answer generation."
    filename = "mandatory_test.txt"

    with tempfile.TemporaryDirectory() as tmp:
        docs_dir = Path(tmp) / "documents"
        docs_dir.mkdir()
        registry_file = Path(tmp) / "registry.json"

        r1 = _isolated_ingest(docs_dir, registry_file, filename, content)
        r2 = _isolated_ingest(docs_dir, registry_file, filename, content)
        r3 = _isolated_ingest(docs_dir, registry_file, filename, content)

        print(f"\nAttempt 1: {r1['status']}")
        print(f"Attempt 2: {r2['status']} — reason: {r2.get('reason', '')}")
        print(f"Attempt 3: {r3['status']} — reason: {r3.get('reason', '')}")

        # Index counts
        stored_before = list(docs_dir.glob("*.txt"))
        print(f"Files on disk: {len(stored_before)}")

        ingestion.DOCS_DIR = docs_dir
        ingestion.REGISTRY_FILE = registry_file
        registry = ingestion.load_registry()
        ingestion.DOCS_DIR = Path(ingestion.__file__).resolve().parent / "documents"
        ingestion.REGISTRY_FILE = Path(ingestion.__file__).resolve().parent / "indexed_documents.json"

        print(f"Registry entries: {len(registry)}")

        assert r1["status"] == "indexed",  f"Expected indexed, got {r1['status']}"
        assert r2["status"] == "skipped",  f"Expected skipped, got {r2['status']}"
        assert r3["status"] == "skipped",  f"Expected skipped, got {r3['status']}"
        assert len(stored_before) == 1,    f"Expected 1 file, found {len(stored_before)}"
        assert len(registry) == 1,         f"Expected 1 registry entry, found {len(registry)}"

        print("✓ MANDATORY DUPLICATE TEST PASSED")


def test_different_content_gets_indexed_separately():
    content_a = b"Document Alpha content about Python."
    content_b = b"Document Beta content about FAISS vectors."

    with tempfile.TemporaryDirectory() as tmp:
        docs_dir = Path(tmp) / "documents"
        docs_dir.mkdir()
        registry_file = Path(tmp) / "registry.json"

        r_a = _isolated_ingest(docs_dir, registry_file, "alpha.txt", content_a)
        r_b = _isolated_ingest(docs_dir, registry_file, "beta.txt", content_b)

        assert r_a["status"] == "indexed"
        assert r_b["status"] == "indexed"
        assert r_a["hash"] != r_b["hash"]


def test_empty_content_raises_value_error():
    with tempfile.TemporaryDirectory() as tmp:
        docs_dir = Path(tmp) / "documents"
        docs_dir.mkdir()
        registry_file = Path(tmp) / "registry.json"

        import pytest
        with pytest.raises(ValueError):
            _isolated_ingest(docs_dir, registry_file, "empty.txt", b"")


def test_whitespace_only_raises_value_error():
    with tempfile.TemporaryDirectory() as tmp:
        docs_dir = Path(tmp) / "documents"
        docs_dir.mkdir()
        registry_file = Path(tmp) / "registry.json"

        import pytest
        with pytest.raises(ValueError):
            _isolated_ingest(docs_dir, registry_file, "blank.txt", b"   \n\n  ")


def test_hash_is_sha256():
    content = b"Test content for hash validation."
    import hashlib
    expected = hashlib.sha256(content).hexdigest()
    assert len(expected) == 64

    with tempfile.TemporaryDirectory() as tmp:
        docs_dir = Path(tmp) / "documents"
        docs_dir.mkdir()
        registry_file = Path(tmp) / "registry.json"

        r = _isolated_ingest(docs_dir, registry_file, "hash_test.txt", content)
        assert r["hash"] == expected


def test_registry_persists_across_calls():
    content = b"Persistent registry test document."

    with tempfile.TemporaryDirectory() as tmp:
        docs_dir = Path(tmp) / "documents"
        docs_dir.mkdir()
        registry_file = Path(tmp) / "registry.json"

        _isolated_ingest(docs_dir, registry_file, "persist.txt", content)

        # Load registry independently to confirm it was saved to disk
        ingestion.DOCS_DIR = docs_dir
        ingestion.REGISTRY_FILE = registry_file
        reg = ingestion.load_registry()
        ingestion.DOCS_DIR = Path(ingestion.__file__).resolve().parent / "documents"
        ingestion.REGISTRY_FILE = Path(ingestion.__file__).resolve().parent / "indexed_documents.json"

        assert len(reg) == 1
