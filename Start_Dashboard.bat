@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   Week 7 RAG API -- Starting Monitoring Dashboard
echo ============================================================
echo.

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found in .\venv\
    echo Please double-click "setup.bat" first to set up the environment.
    echo.
    pause
    exit /b 1
)

echo Starting Streamlit monitoring dashboard...
echo.
echo Dashboard URL: http://localhost:8501
echo.
echo Press Ctrl+C in this terminal window to stop the dashboard.
echo ============================================================
echo.

".\venv\Scripts\python.exe" -m streamlit run dashboard\app.py
pause
