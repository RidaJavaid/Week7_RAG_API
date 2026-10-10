from pathlib import Path
import subprocess
import sys

BASE_DIR = Path(__file__).resolve().parent
PYTHON = sys.executable
OUTPUT = BASE_DIR / "test_output.txt"

result = subprocess.run(
    [PYTHON, "-m", "pytest",
     "tests/test_ingestion_day3.py",
     "tests/test_cost_tracker.py",
     "tests/test_auto_ingest.py",
     "-v", "--tb=short", "--no-header"],
    capture_output=True,
    text=True,
    cwd=str(BASE_DIR),
)
combined = result.stdout + result.stderr
print(combined)
with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(combined)
print(f"\nSaved to {OUTPUT}")
sys.exit(result.returncode)
