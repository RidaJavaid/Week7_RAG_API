"""Register the 5 Week 6 source documents into indexed_documents.json."""
import sys
sys.path.insert(0, r"C:\Users\ridaj\Week7_RAG_API")
import ingestion

docs = {
    "01_machine_learning.txt": "01_machine_learning.txt",
    "02_embeddings.txt": "02_embeddings.txt",
    "03_rag.txt": "03_rag.txt",
    "04_vector_search.txt": "04_vector_search.txt",
    "05_chunking_bm25_reranking.txt": "05_chunking_bm25_reranking.txt",
}

from pathlib import Path
DOCS_DIR = Path(r"C:\Users\ridaj\Week7_RAG_API\documents")

for fname in docs:
    path = DOCS_DIR / fname
    content = path.read_bytes()
    result = ingestion.ingest_document(fname, content)
    print(f"{fname}: {result['status']}")
