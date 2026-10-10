@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   Week 7 RAG API -- Automated Environment Setup
echo ============================================================
echo.

:: 1. Verify Python is installed and accessible in PATH
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python was not found in your system PATH.
    echo Please install Python 3.10, 3.11, or 3.12 from https://www.python.org/downloads/
    echo and ensure "Add python.exe to PATH" is checked during installation.
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set "PY_VER=%%i"
echo Detected system Python: %PY_VER%
echo.

:: 2. Create or verify virtual environment in .\venv
echo [1/3] Setting up Python virtual environment in .\venv ...
if not exist "venv\Scripts\python.exe" (
    echo Creating fresh virtual environment...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        echo Please ensure you have permission to create folders in this directory.
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
) else (
    echo Existing virtual environment found.
)
echo.

:: 3. Upgrade pip
echo [2/3] Upgrading pip inside virtual environment...
".\venv\Scripts\python.exe" -m pip install --upgrade pip --quiet --timeout 60 --retries 10
echo.

:: 4. Install dependencies from requirements.txt
echo [3/3] Installing project dependencies from requirements.txt...
echo (Note: Downloads lightweight local CPU embeddings: all-MiniLM-L6-v2)
".\venv\Scripts\python.exe" -m pip install --timeout 60 --retries 10 -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Dependency installation encountered an issue.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   Setup Complete!
echo ============================================================
echo   Quick-Start Options:
echo     1. Double-click "Start_API.bat"
echo        - Runs FastAPI service at http://localhost:8000
echo        - Swagger documentation at http://localhost:8000/docs
echo.
echo     2. Double-click "Start_Dashboard.bat"
echo        - Runs Streamlit UI at http://localhost:8501
echo ============================================================
echo.
pause
