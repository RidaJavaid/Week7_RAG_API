@echo off
set "PYTHON=%~dp0venv\Scripts\python.exe"
"%PYTHON%" -m pip install -r "%~dp0requirements.txt" 2>&1
echo DONE
