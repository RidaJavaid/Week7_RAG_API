"""Wrapper: run prompt injection test and save output."""
import subprocess, sys
PYTHON = r"C:\Users\ridaj\Week7_RAG_API\venv\Scripts\python.exe"
result = subprocess.run(
    [PYTHON, "prompt_injection_test.py"],
    capture_output=True, text=True,
    cwd=r"C:\Users\ridaj\Week7_RAG_API",
)
print(result.stdout)
print(result.stderr)
out_path = r"C:\Users\ridaj\Week7_RAG_API\injection_output.txt"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(result.stdout + result.stderr)
print(f"Saved to {out_path}")
