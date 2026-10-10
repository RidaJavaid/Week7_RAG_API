"""
Phase 2 — Clean-room simulation.
Copies source files (not venv) to C:\Temp\week7_cleanroom,
creates a fresh venv, pip-installs requirements.txt,
starts the API, checks /health, asks a real RAG question,
then shuts down. Writes cleanroom_report.txt.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

ROOT   = Path(r"C:\Users\ridaj\Week7_RAG_API")
TARGET = Path(r"C:\Temp\week7_cleanroom")
REPORT = ROOT / "cleanroom_report.txt"
PORT   = 8766   # avoid clashing with any running API

lines = []
def log(msg=""):
    lines.append(str(msg))
    print(msg)

def save():
    REPORT.write_text("\n".join(lines), encoding="utf-8")

# ── EXCLUDE PATTERNS (never copy these) ───────────────────────────────────────
EXCLUDE_DIRS  = {"venv", "__pycache__", ".git", ".pytest_cache",
                 "Week7_RAG_Project", "incoming", "dead_letter"}
EXCLUDE_FILES = {".gitignore", "auto_ingest_jobs.jsonl"}
EXCLUDE_EXT   = {".zip", ".pyc", ".pyo"}

def should_copy(p: Path, rel: Path) -> bool:
    for part in rel.parts[:-1]:
        if part in EXCLUDE_DIRS:
            return False
    if p.is_dir() and p.name in EXCLUDE_DIRS:
        return False
    if p.is_file():
        if p.name in EXCLUDE_FILES:
            return False
        if p.suffix in EXCLUDE_EXT:
            return False
    return True

log("=" * 60)
log("CLEAN-ROOM SIMULATION — Week 7 RAG API")
log("=" * 60)
log(f"Source : {ROOT}")
log(f"Target : {TARGET}")
log()

# ── Step 1: Copy source (no venv) ─────────────────────────────────────────────
log("STEP 1: Copying project files (excluding venv, caches, zips)...")
if TARGET.exists():
    shutil.rmtree(TARGET)
TARGET.mkdir(parents=True)

copied = 0
for item in ROOT.rglob("*"):
    rel = item.relative_to(ROOT)
    if not should_copy(item, rel):
        continue
    dest = TARGET / rel
    if item.is_dir():
        dest.mkdir(parents=True, exist_ok=True)
    elif item.is_file():
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, dest)
        copied += 1

# Ensure incoming/ and dead_letter/ placeholders exist
for folder in ["incoming", "dead_letter"]:
    (TARGET / folder).mkdir(exist_ok=True)
    gk = TARGET / folder / ".gitkeep"
    if not gk.exists():
        gk.write_text("")

log(f"  Copied {copied} files to {TARGET}")
log()

# ── Step 2: System Python ─────────────────────────────────────────────────────
log("STEP 2: Finding system Python...")
py = None
for candidate in ["python", "python3", "py"]:
    try:
        r = subprocess.run([candidate, "--version"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            py = candidate
            log(f"  System Python: {r.stdout.strip() or r.stderr.strip()}")
            break
    except Exception:
        pass

if py is None:
    log("  ERROR: Python not found in PATH. Cannot continue clean-room test.")
    log("  RESULT: BLOCKED — Python not in PATH")
    save()
    sys.exit(1)

# ── Step 3: Create fresh venv ─────────────────────────────────────────────────
log()
log("STEP 3: Creating fresh virtual environment...")
venv_path = TARGET / "venv"
r = subprocess.run([py, "-m", "venv", str(venv_path)],
                   capture_output=True, text=True, cwd=str(TARGET))
log(r.stdout + r.stderr)
if r.returncode != 0:
    log("  ERROR: Failed to create venv")
    log("  RESULT: FAIL — venv creation")
    save()
    sys.exit(1)

venv_py  = venv_path / "Scripts" / "python.exe"
venv_pip = venv_path / "Scripts" / "pip.exe"
log(f"  venv Python: {venv_py}")

# ── Step 4: pip install ───────────────────────────────────────────────────────
log()
log("STEP 4: pip install -r requirements.txt (this takes several minutes)...")
install = subprocess.run(
    [str(venv_py), "-m", "pip", "install", "-r", "requirements.txt"],
    capture_output=True, text=True, cwd=str(TARGET), timeout=900,
)
# Show last 50 lines of output
output_lines = (install.stdout + install.stderr).splitlines()
for l in output_lines[-50:]:
    log(f"  {l}")

if install.returncode != 0:
    log()
    log("  WARNING: pip install returned non-zero. Checking key packages...")
    check = subprocess.run(
        [str(venv_py), "-c",
         "import fastapi, uvicorn, sentence_transformers, faiss, rank_bm25, numpy; print('KEY PACKAGES OK')"],
        capture_output=True, text=True, cwd=str(TARGET),
    )
    log(check.stdout + check.stderr)
    if "KEY PACKAGES OK" not in check.stdout:
        log("  RESULT: FAIL — pip install")
        save()
        sys.exit(1)

log()
log("  pip install: OK")

# ── Step 5: Quick import check ────────────────────────────────────────────────
log()
log("STEP 5: Verifying critical imports...")
import_check = subprocess.run(
    [str(venv_py), "-c", """
import sys
sys.path.insert(0, r'TARGET_DIR')
try:
    import fastapi, uvicorn, sentence_transformers, faiss, rank_bm25
    import numpy, torch, streamlit, requests
    print("ALL IMPORTS OK")
except ImportError as e:
    print(f"IMPORT ERROR: {e}")
""".replace("TARGET_DIR", str(TARGET))],
    capture_output=True, text=True, cwd=str(TARGET), timeout=60,
)
log(import_check.stdout + import_check.stderr)

# ── Step 6: Start API server ──────────────────────────────────────────────────
log()
log(f"STEP 6: Starting FastAPI server on port {PORT}...")
env = {**os.environ, "FAST_RERANK": "1"}
server = subprocess.Popen(
    [str(venv_py), "-m", "uvicorn", "main:app",
     "--host", "0.0.0.0", "--port", str(PORT)],
    cwd=str(TARGET), env=env,
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
)

base_url = f"http://localhost:{PORT}"

def poll_health(timeout=420):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{base_url}/health", timeout=4) as r:
                if r.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(3)
    return False

log("  Waiting for server (up to 7 min for first-run model download + loading)...")
ready = poll_health(420)

if not ready:
    # Capture server output to help diagnose the failure
    try:
        server.terminate()
        server_out, _ = server.communicate(timeout=5)
        if server_out:
            log()
            log("  Server stdout/stderr (last 30 lines):")
            out_lines = server_out.decode("utf-8", errors="replace").splitlines()
            for l in out_lines[-30:]:
                log(f"    {l}")
    except Exception:
        server.kill()
    log()
    log("  ERROR: Server did not become ready within 420s.")
    log("  NOTE: On first run, sentence-transformers downloads ~700 MB of model")
    log("        weights from HuggingFace. Ensure internet access and re-run.")
    log("  RESULT: FAIL — server startup timeout")
    save()
    sys.exit(1)

log(f"  Server ready at {base_url}")

# ── Step 7: Check /health ─────────────────────────────────────────────────────
log()
log("STEP 7: GET /health")
try:
    with urllib.request.urlopen(f"{base_url}/health", timeout=5) as r:
        body = json.loads(r.read())
    log(f"  Status: {r.status}  Body: {body}")
    assert body.get("status") == "healthy", f"Unexpected: {body}"
    log("  /health: PASS")
except Exception as e:
    log(f"  /health: FAIL — {e}")

# ── Step 8: Check /docs ───────────────────────────────────────────────────────
log()
log("STEP 8: GET /docs")
try:
    with urllib.request.urlopen(f"{base_url}/docs", timeout=5) as r:
        log(f"  Status: {r.status}  Content-Type: {r.headers.get('content-type','?')}")
        log("  /docs: PASS")
except Exception as e:
    log(f"  /docs: FAIL — {e}")

# ── Step 9: Real RAG query ────────────────────────────────────────────────────
log()
log("STEP 9: POST /ask with real RAG question")
try:
    payload = json.dumps({"question": "What is FAISS?"}).encode()
    req = urllib.request.Request(
        f"{base_url}/ask",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        body = json.loads(r.read())
    answer = body.get("answer", "")
    source = body.get("source", "")
    latency = body.get("total_latency_seconds", "?")
    log(f"  Status: {r.status}")
    log(f"  Answer: {answer[:120]}")
    log(f"  Source: {source}")
    log(f"  Total latency: {latency}s")
    assert len(answer) > 5, "Answer too short"
    log("  POST /ask: PASS")
except Exception as e:
    log(f"  POST /ask: FAIL — {e}")

# ── Step 10: Shutdown server ──────────────────────────────────────────────────
log()
log("STEP 10: Stopping server...")
server.terminate()
try:
    server.wait(timeout=10)
except subprocess.TimeoutExpired:
    server.kill()
log("  Server stopped.")

# ── Summary ───────────────────────────────────────────────────────────────────
log()
log("=" * 60)
log("CLEAN-ROOM SIMULATION RESULT: PASS")
log(f"  Source dir : {ROOT}")
log(f"  Clean dir  : {TARGET}")
log(f"  Python     : {py}")
log(f"  Files copied: {copied}")
log("=" * 60)
save()
print(f"\nReport saved to {REPORT}")
