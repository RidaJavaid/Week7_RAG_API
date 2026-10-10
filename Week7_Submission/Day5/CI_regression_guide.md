# CI Quality Gate Regression Test Guide

## Overview

The GitHub Actions quality gate (`.github/workflows/quality_gate.yml`) fails
when mean quality score drops below the threshold (0.40).

To **verify** the gate actually blocks regressions, we inject a deliberate
threshold change on a separate branch.

---

## How the Regression Works

`evaluate_quality.py` contains:
```python
QUALITY_THRESHOLD = 0.40
```

The regression changes this to `0.99`, making it impossible for the current
system (mean score ~0.56) to pass.

---

## Step-by-Step (requires GitHub push access)

### 1. Initialize git repo (if not done)
```powershell
cd <extracted project folder>
git init
git add .
git commit -m "feat: Week7 RAG API complete submission"
```

### 2. Create GitHub repo
- Go to https://github.com/new
- Create repo: `Week7_RAG_API`
- Copy the remote URL

### 3. Push main branch
```powershell
git remote add origin https://github.com/YOUR_USERNAME/Week7_RAG_API.git
git push -u origin main
```

### 4. Create regression branch
```powershell
.\venv\Scripts\python.exe create_regression_branch.py
git push -u origin test/quality-regression
```

### 5. Observe CI failure
- Go to: https://github.com/YOUR_USERNAME/Week7_RAG_API/actions
- Click the `test/quality-regression` run
- `quality_gate.yml` step "Run quality evaluation" will show **red X**
- Exit code: 1 (mean score 0.56 < threshold 0.99)

### 6. Restore main branch
```powershell
.\venv\Scripts\python.exe create_regression_branch.py --restore
git checkout main
# Verify main CI passes (score 0.56 >= threshold 0.40)
```

---

## What the CI YAML Does

```yaml
- name: Run quality evaluation
  run: |
    python evaluate_quality.py \
      --output Week7_Submission/Day5/quality_report.json
  # exit 1 when score < threshold → CI step FAILS
```

---

## Evidence Required

After pushing both branches, provide:
1. Screenshot of GitHub Actions showing red X on `test/quality-regression`
2. Screenshot of green check on `main`
3. The CI log showing the actual score vs threshold

---

## Status

**BLOCKED: Requires GitHub account and push access.**

This guide provides all commands needed. Once you push:
- I cannot access your GitHub account
- The CI run is external to this environment
- You will need to provide a screenshot as evidence

The regression mechanism is correct and verified locally:
- `QUALITY_THRESHOLD = 0.99` with mean score 0.56 → `sys.exit(1)` → CI fails
- `QUALITY_THRESHOLD = 0.40` with mean score 0.56 → `sys.exit(0)` → CI passes
