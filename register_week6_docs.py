from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
import ingestion

docs = {
    "01_machine_learning.txt": "01_machine_learning.txt",
    "02_embeddings.txt": "02_embeddings.txt",
    "03_rag.txt": "03_rag.txt",
    "04_vector_search.txt": "04_vector_search.txt",
    "05_chunking_bm25_reranking.txt": "05_chunking_bm25_reranking.txt",
}

DOCS_DIR = BASE_DIR / "documents"

for fname in docs:
    path = DOCS_DIR / fname
    content = path.read_bytes()
    result = ingestion.ingest_document(fname, content)
    print(f"{fname}: {result['status']}")
