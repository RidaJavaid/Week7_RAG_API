
import tempfile
from pathlib import Path

import ingestion


def test_same_document_three_times():

    original_docs_dir = ingestion.DOCS_DIR
    original_registry = ingestion.REGISTRY_FILE

    try:
        # Create temporary test folder
        with tempfile.TemporaryDirectory() as temp:

            ingestion.DOCS_DIR = Path(temp) / "documents"
            ingestion.DOCS_DIR.mkdir(parents=True, exist_ok=True)

            ingestion.REGISTRY_FILE = (
                Path(temp) / "registry.json"
            )

            # Sample document
            content = (
                b"RAG combines document retrieval "
                b"with answer generation."
            )

            # Ingest same document three times
            first = ingestion.ingest_document(
                "sample.txt", content
            )

            second = ingestion.ingest_document(
                "sample.txt", content
            )

            third = ingestion.ingest_document(
                "sample.txt", content
            )

            # Verify duplicate prevention
            assert first["status"] == "indexed"
            assert second["status"] == "skipped"
            assert third["status"] == "skipped"

            # Verify only one file was stored
            stored_files = list(
                ingestion.DOCS_DIR.glob("*.txt")
            )

            assert len(stored_files) == 1

            # Verify registry contains one document
            registry = ingestion.load_registry()
            assert len(registry) == 1

            print("\nDOCUMENT INGESTION TEST")
            print("----------------------------")
            print("Run 1:", first["status"])
            print("Run 2:", second["status"])
            print("Run 3:", third["status"])
            print("Stored files:", len(stored_files))
            print("Registry entries:", len(registry))
            print("TEST PASSED")

    finally:
        # Restore original project paths
        ingestion.DOCS_DIR = original_docs_dir
        ingestion.REGISTRY_FILE = original_registry


if __name__ == "__main__":
    test_same_document_three_times()
