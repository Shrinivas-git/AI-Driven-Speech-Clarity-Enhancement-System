@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv .venv
)
echo Activating virtual environment...
call .venv\Scripts\activate.bat
echo Starting backend server...
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pause


