"""
Week 7 RAG API -- Virtual Environment Dependency Installer & Import Validator
=============================================================================
Ensures all required project packages are installed inside the isolated
project virtual environment (.\\venv), preventing permission errors or conflicts
with global system Python installations.
"""
import importlib
from pathlib import Path
import subprocess
import sys

BASE_DIR = Path(__file__).resolve().parent
VENV_DIR = BASE_DIR / "venv"
VENV_PYTHON = VENV_DIR / "Scripts" / "python.exe"


def ensure_virtualenv():
    """Ensure virtual environment exists, creating it if needed."""
    if not VENV_PYTHON.exists():
        print(f"[INFO] Virtual environment not found at {VENV_DIR}. Creating...")
        res = subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)
        print("[SUCCESS] Virtual environment created.")
    else:
        print(f"[INFO] Using existing virtual environment: {VENV_PYTHON}")


def install_requirements():
    """Install dependencies inside the isolated virtual environment."""
    req_file = BASE_DIR / "requirements.txt"
    if not req_file.exists():
        print(f"[ERROR] requirements.txt not found at {req_file}")
        sys.exit(1)

    print(f"[INFO] Installing dependencies from {req_file.name} using virtual environment Python...")
    cmd = [str(VENV_PYTHON), "-m", "pip", "install", "-r", str(req_file)]
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print("[ERROR] Failed to install requirements inside virtual environment.")
        sys.exit(res.returncode)
    print("[SUCCESS] Dependencies installed inside virtual environment.")


def verify_imports():
    """Verify that every critical dependency imports cleanly."""
    packages_to_verify = [
        ("fastapi", "FastAPI web framework"),
        ("uvicorn", "ASGI server"),
        ("pydantic", "Data validation"),
        ("sentence_transformers", "Dense vector embeddings"),
        ("faiss", "FAISS vector search"),
        ("rank_bm25", "BM25 lexical retrieval"),
        ("torch", "PyTorch"),
        ("streamlit", "Streamlit UI"),
        ("httpx", "HTTP client"),
        ("pandas", "Data manipulation"),
        ("pytest", "Testing suite"),
        ("matplotlib", "Plotting"),
        ("requests", "HTTP requests"),
    ]

    print("\n" + "=" * 60)
    print("VERIFYING DEPENDENCY IMPORTS IN VIRTUAL ENVIRONMENT")
    print("=" * 60)

    verify_script = """
import sys
packages = %r
all_ok = True
for mod_name, desc in packages:
    try:
        __import__(mod_name)
        print(f"  [OK]   {mod_name:<24} -- {desc}")
    except Exception as exc:
        print(f"  [FAIL] {mod_name:<24} -- ERROR: {exc}")
        all_ok = False
sys.exit(0 if all_ok else 1)
""" % packages_to_verify

    res = subprocess.run(
        [str(VENV_PYTHON), "-c", verify_script],
        text=True,
        capture_output=True,
    )
    print(res.stdout)
    if res.returncode != 0:
        print(res.stderr)
        print("[ERROR] One or more package imports failed.")
        sys.exit(1)

    print("=" * 60)
    print("[ALL PASS] All project dependencies verified successfully!")
    print("=" * 60)


if __name__ == "__main__":
    ensure_virtualenv()
    install_requirements()
    verify_imports()
