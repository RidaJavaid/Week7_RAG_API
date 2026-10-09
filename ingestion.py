
import hashlib
import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "documents"
REGISTRY_FILE = BASE_DIR / "indexed_documents.json"

DOCS_DIR.mkdir(parents=True, exist_ok=True)


def get_document_hash(content):
    """Generate SHA-256 hash from document content."""
    return hashlib.sha256(content).hexdigest()


def load_registry():
    if REGISTRY_FILE.exists():
        return json.loads(
            REGISTRY_FILE.read_text(encoding="utf-8")
        )
    return {}


def save_registry(registry):
    temporary = REGISTRY_FILE.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(registry, indent=4),
        encoding="utf-8"
    )
    os.replace(temporary, REGISTRY_FILE)


def ingest_document(filename, content):
    """Store a document once, using its content hash."""

    if not isinstance(content, bytes) or not content:
        raise ValueError("Document must contain bytes")

    text = content.decode("utf-8")
    if not text.strip():
        raise ValueError("Document cannot be empty")

    doc_hash = get_document_hash(content)
    registry = load_registry()

    if doc_hash in registry:
        return {
            "status": "skipped",
            "reason": "Duplicate document",
            "hash": doc_hash
        }

    # Use hash-based filename to avoid overwrites
    safe_filename = f"{doc_hash}.txt"
    destination = DOCS_DIR / safe_filename

    destination.write_bytes(content)

    registry[doc_hash] = {
        "original_filename": Path(filename).name,
        "stored_filename": safe_filename
    }

    save_registry(registry)

    return {
        "status": "indexed",
        "filename": safe_filename,
        "hash": doc_hash
    }
