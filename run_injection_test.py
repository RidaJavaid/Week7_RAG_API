from pathlib import Path
import subprocess, sys

BASE_DIR = Path(__file__).resolve().parent
PYTHON = sys.executable

result = subprocess.run(
    [PYTHON, "prompt_injection_test.py"],
    capture_output=True, text=True,
    cwd=str(BASE_DIR),
)
print(result.stdout)
print(result.stderr)
out_path = BASE_DIR / "injection_output.txt"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(result.stdout + result.stderr)
print(f"Saved to {out_path}")
