"""Find git executable on this system."""
import os, subprocess, sys
from pathlib import Path

# Try subprocess directly (git might be in PATH for cmd even if not PS)
candidates = [
    "git",
    r"C:\Program Files\Git\bin\git.exe",
    r"C:\Program Files\Git\cmd\git.exe",
    r"C:\Program Files (x86)\Git\bin\git.exe",
    str(Path.home() / r"AppData\Local\Programs\Git\bin\git.exe"),
    str(Path.home() / r"AppData\Local\Programs\Git\cmd\git.exe"),
]

found = None
for c in candidates:
    try:
        r = subprocess.run([c, "--version"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            print(f"FOUND: {c}")
            print(f"Version: {r.stdout.strip()}")
            found = c
            break
    except (FileNotFoundError, subprocess.TimeoutExpired, PermissionError):
        pass

if not found:
    # Search PATH entries
    for p in os.environ.get("PATH", "").split(os.pathsep):
        candidate = Path(p) / "git.exe"
        if candidate.exists():
            print(f"FOUND in PATH: {candidate}")
            found = str(candidate)
            break

if not found:
    print("git NOT FOUND. Please install Git from https://git-scm.com/download/win")
    sys.exit(1)

# Write git path to a file so other scripts can use it
Path("git_path.txt").write_text(found, encoding="utf-8")
print(f"Path written to git_path.txt")
