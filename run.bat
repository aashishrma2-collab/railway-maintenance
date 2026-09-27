@echo off
REM Run on Windows. No Docker required - just Python 3.10+ installed
REM (get it from python.org, tick "Add Python to PATH" during install).
cd /d "%~dp0backend"

if not exist ".venv" (
  echo Creating virtual environment...
  python -m venv .venv
)
call .venv\Scripts\activate.bat

pip install -q -r requirements.txt

if not exist "..\.env" (
  copy ..\.env.example ..\.env
  echo Created .env from .env.example - edit JWT_SECRET before real deployment.
)

if not exist "data" mkdir data
python -m app.seed

if "%PORT%"=="" set PORT=8000
echo Starting server on http://0.0.0.0:%PORT%
uvicorn app.main:app --host 0.0.0.0 --port %PORT%
