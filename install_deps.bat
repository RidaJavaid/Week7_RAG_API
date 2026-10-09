@echo off
set PYTHON=C:\Users\ridaj\Week7_RAG_API\venv\Scripts\python.exe
%PYTHON% -m pip install pytest pytest-asyncio httpx streamlit matplotlib watchdog locust requests 2>&1
echo DONE
