#!/usr/bin/env bash
# Run on Ubuntu/macOS/WSL. No Docker required — just Python 3.10+.
set -e
cd "$(dirname "$0")/backend"

if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
fi
source .venv/bin/activate

pip install -q -r requirements.txt

if [ ! -f "../.env" ]; then
  cp ../.env.example ../.env
  echo "Created .env from .env.example — edit JWT_SECRET before real deployment."
fi
set -a
source ../.env
set +a

mkdir -p data
python -m app.seed

PORT="${PORT:-8000}"
echo "Starting server on http://0.0.0.0:$PORT"
uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
