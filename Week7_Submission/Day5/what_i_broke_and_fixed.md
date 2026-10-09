# What I Broke and Fixed — Week 7

## 1. Unicode print statements crashing on Windows cp1252 terminal

**What broke:**
`evaluate_quality.py` and `prompt_injection_test.py` used Unicode symbols (→, ✓, ✗, ⚠️)
in `print()` statements. The Windows console default encoding (cp1252) cannot encode
these characters, causing a `UnicodeEncodeError` that crashed the scripts before
writing output files.

**How it was fixed:**
Replaced all Unicode symbols and emojis with ASCII alternatives (`->`, `PASSED`, `FAILED`, `[REGRESSION MODE]`).
Also ensured output file persistence is isolated from terminal stdout encoding failures.

---

## 2. `process_file` importing `rebuild_index` at module top-level

**What broke:**
`auto_ingest.py` initially imported `from rag import rebuild_index` at the top of
the file. When the watcher started before the API server had loaded models,
this triggered model loading in the watcher process — doubling memory use and
slowing startup.

**How it was fixed:**
Moved `from rag import rebuild_index` and `import ingestion` inside the
`process_file` function body. This defers model loading until the first
document actually needs to be indexed.

---

## 3. Dead-letter collision on repeated failures

**What broke:**
If a file with the same name failed twice (e.g., during testing), `shutil.move`
would attempt to overwrite the existing dead-letter file, raising a `FileExistsError`
on Windows.

**How it was fixed:**
Added a timestamp suffix (`_{int(time.time())}`) to the dead-letter filename
whenever the target path already exists.

---

## 4. Benchmark timing inflated by cold-start model loading

**What broke:**
The first few benchmark runs had much higher latency than steady-state because
Torch/Transformers load model weights from disk on first call. This skewed the
median upward.

**How it was fixed:**
`rebuild_index()` is called once at the start of `run_benchmark.py` before the
timed loop, ensuring models are warm before measurements begin. Run 1 still shows
higher latency due to JIT compilation warm-up; this is documented in the report.

---

## 5. Missing system Git executable breaking automated tasks

**What broke:**
The local Windows operating environment lacked a system-level Git CLI, causing
interrupted scripts, `create_regression_branch.py` failures, and preventing GitHub sync.

**How it was fixed:**
Installed portable MinGit (`2.56.0`) directly into user space (`AppData\Local\Programs\Git\cmd`),
updated User `PATH`, and enhanced `run_git` subprocess calls in Python scripts to dynamically
resolve the git binary via `shutil.which` and fallback discovery paths.

---

## 6. Pip version conflicts between Streamlit and Pandas in CI requirements

**What broke:**
`requirements.txt` previously pinned `streamlit==1.40.0` while requiring `pandas==3.0.6`.
Streamlit 1.40.0 restricts `pandas < 3`, causing `pip install -r requirements.txt` to fail with
dependency resolution conflict on GitHub Actions runners.

**How it was fixed:**
Updated version pins in `requirements.txt` to compatible `>=` version ranges matching the verified
local virtual environment (`streamlit>=1.40.0`, `pandas>=2.0.0`), allowing pip to install smoothly
on both Python 3.11 (CI) and Python 3.13 (local/production).
