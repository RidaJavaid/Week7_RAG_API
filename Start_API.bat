@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   Week 7 RAG API -- Starting FastAPI Server
echo ============================================================
echo.

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found in .\venv\
    echo Please double-click "setup.bat" first to set up the environment.
    echo.
    pause
    exit /b 1
)

echo Loading local AI models (all-MiniLM-L6-v2) and starting server...
echo.
echo   Service URL:          http://localhost:8000
echo   Interactive Swagger:  http://localhost:8000/docs
echo   Health Check:         http://localhost:8000/health
echo.
echo Press Ctrl+C in this terminal window to stop the server.
echo ============================================================
echo.

set "FAST_RERANK=1"
".\venv\Scripts\python.exe" -m uvicorn main:app --host 0.0.0.0 --port 8000
pause
