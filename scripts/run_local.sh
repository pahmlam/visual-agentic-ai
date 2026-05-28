#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ -f ".env" ]; then
  set -a
  # shellcheck disable=SC1091
  source ".env"
  set +a
fi

if [ ! -x "venv/bin/python" ]; then
  echo "venv/bin/python not found. Create a virtual environment first."
  exit 1
fi

exec venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8300 --reload
