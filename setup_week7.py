"""Install missing Week 7 dependencies."""
import subprocess
import sys

PYTHON = r"C:\Users\ridaj\Week7_RAG_API\venv\Scripts\python.exe"

packages = [
    "pytest",
    "pytest-asyncio",
    "httpx",
    "streamlit",
    "matplotlib",
    "watchdog",
    "locust",
    "requests",
]

for pkg in packages:
    result = subprocess.run(
        [PYTHON, "-m", "pip", "install", pkg],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print(f"OK: {pkg}")
    else:
        print(f"FAIL: {pkg}")
        print(result.stderr[-300:])
