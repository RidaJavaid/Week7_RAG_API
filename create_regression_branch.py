"""
Create a regression branch to test the GitHub Actions quality gate.

This script:
1. Creates branch 'test/quality-regression'
2. Injects a regression into evaluate_quality.py (forces FAILED)
3. Commits and pushes
4. Shows what the CI will check

After pushing, open GitHub Actions to confirm the quality gate fails.
Then run this script with --restore to revert.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EVAL = ROOT / "evaluate_quality.py"

REGRESSION_PATCH = '''
# REGRESSION INJECTION: force threshold impossibly high to simulate quality drop
# This is the deliberate regression for CI testing — remove to restore.
QUALITY_THRESHOLD = 0.99   # was 0.40
'''

def run_git(args, check=True):
    git_bin = "git"
    git_path_file = ROOT / "git_path.txt"
    if git_path_file.exists():
        p = git_path_file.read_text(encoding="utf-8").strip()
        if Path(p).exists():
            git_bin = p
    result = subprocess.run(
        [git_bin] + args,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    if check and result.returncode != 0:
        print(f"git {' '.join(args)} failed:\n{result.stderr}")
    else:
        print(f"git {' '.join(args)}: {result.stdout.strip() or 'ok'}")
    return result

def inject_regression():
    content = EVAL.read_text(encoding="utf-8")
    if "REGRESSION INJECTION" in content:
        print("Regression already injected.")
        return
    # Replace the threshold line
    content = content.replace(
        "QUALITY_THRESHOLD = 0.40",
        "QUALITY_THRESHOLD = 0.99  # REGRESSION INJECTION"
    )
    EVAL.write_text(content, encoding="utf-8")
    print("Regression injected: QUALITY_THRESHOLD set to 0.99")

def restore():
    content = EVAL.read_text(encoding="utf-8")
    content = content.replace(
        "QUALITY_THRESHOLD = 0.99  # REGRESSION INJECTION",
        "QUALITY_THRESHOLD = 0.40"
    )
    EVAL.write_text(content, encoding="utf-8")
    print("Threshold restored to 0.40")

def main():
    if "--restore" in sys.argv:
        restore()
        run_git(["checkout", "main"], check=False)
        print("Restored to main branch with correct threshold.")
        return

    # Check we have a git repo
    r = run_git(["status"], check=False)
    if r.returncode != 0:
        print("ERROR: Not a git repository. Run: git init && git add . && git commit -m 'initial'")
        sys.exit(1)

    # Create regression branch
    run_git(["checkout", "-b", "test/quality-regression"], check=False)

    # Inject regression
    inject_regression()

    # Stage and commit
    run_git(["add", "evaluate_quality.py"])
    run_git(["commit", "-m", "test: inject quality regression (threshold=0.99) for CI gate test"])

    print("""
Regression branch created: test/quality-regression
Threshold changed: 0.40 -> 0.99 (all scores will fail)

To push and trigger GitHub Actions CI:
  git push -u origin test/quality-regression

Expected CI outcome:
  - quality_gate.yml runs evaluate_quality.py
  - mean score (0.56) < threshold (0.99) -> exit 1
  - GitHub Actions step FAILS (red X)

To restore main branch:
  python create_regression_branch.py --restore
  git push origin main
""")

if __name__ == "__main__":
    main()
