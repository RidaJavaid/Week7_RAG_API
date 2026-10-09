"""Run all Week 7 tests and save output to test_output.txt."""
import subprocess
import sys

PYTHON = r"C:\Users\ridaj\Week7_RAG_API\venv\Scripts\python.exe"
OUTPUT = r"C:\Users\ridaj\Week7_RAG_API\test_output.txt"

result = subprocess.run(
    [PYTHON, "-m", "pytest",
     "tests/test_ingestion_day3.py",
     "tests/test_cost_tracker.py",
     "tests/test_auto_ingest.py",
     "-v", "--tb=short", "--no-header"],
    capture_output=True,
    text=True,
    cwd=r"C:\Users\ridaj\Week7_RAG_API",
)
combined = result.stdout + result.stderr
print(combined)
with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(combined)
print(f"\nSaved to {OUTPUT}")
sys.exit(result.returncode)
