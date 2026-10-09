"""
Start the FastAPI server, run the load test, save results.
Usage:  python run_server_and_loadtest.py
"""
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT   = Path(__file__).resolve().parent
PYTHON = ROOT / "venv" / "Scripts" / "python.exe"
PORT   = 8765   # use non-standard port to avoid conflicts

def wait_for_server(url, timeout=120):
    import urllib.request
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = urllib.request.urlopen(f"{url}/health", timeout=3)
            if r.status == 200:
                return True
        except Exception:
            pass
        time.sleep(2)
    return False

def main():
    env = {**os.environ, "FAST_RERANK": "1"}

    print(f"Starting FastAPI server on port {PORT} ...")
    server = subprocess.Popen(
        [str(PYTHON), "-m", "uvicorn", "main:app",
         "--host", "0.0.0.0", "--port", str(PORT)],
        cwd=str(ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    url = f"http://localhost:{PORT}"
    print("Waiting for server to be ready ...")
    ready = wait_for_server(url, timeout=180)

    if not ready:
        print("ERROR: Server did not become ready within 180s.")
        server.terminate()
        sys.exit(1)

    print(f"Server ready at {url}")

    # Run load test
    print("\nRunning load test (5 concurrent, 20 requests)...")
    lt = subprocess.run(
        [str(PYTHON), "load_test.py",
         "--url", url,
         "--users", "5",
         "--requests", "20"],
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
    )
    print(lt.stdout)
    print(lt.stderr)

    print("\nStopping server ...")
    server.terminate()
    try:
        server.wait(timeout=10)
    except subprocess.TimeoutExpired:
        server.kill()

    print("Done. Load test results: Week7_Submission/Day5/load_test_results.md")

if __name__ == "__main__":
    main()
