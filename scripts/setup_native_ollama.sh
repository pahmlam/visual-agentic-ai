#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is not installed or not available in PATH."
  echo "Install Docker Desktop, then run this script again."
  exit 1
fi

if ! command -v ollama >/dev/null 2>&1; then
  echo "Ollama is not installed."
  echo "Install it from https://ollama.com/download, then run this script again."
  exit 1
fi

if ! ollama list >/dev/null 2>&1; then
  echo "Ollama is installed but not reachable."
  echo "Start the Ollama app or run 'ollama serve', then run this script again."
  exit 1
fi

if [ ! -f ".env" ]; then
  cp ".env.example" ".env"
  echo "Created .env from .env.example"
fi

mkdir -p "models" "data/uploads" "data/.cache" "data/memory"

echo "Pulling Ollama text model..."
ollama pull llama3.2:3b

echo "Pulling Ollama vision model..."
ollama pull llama3.2-vision

if [ ! -f "models/yolo11x.pt" ]; then
  echo "Downloading YOLO weights to models/yolo11x.pt..."
  curl -L -o "models/yolo11x.pt" \
    "https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11x.pt"
else
  echo "YOLO weights already exist at models/yolo11x.pt"
fi

echo "Bootstrap complete."
echo "Run: docker compose up --build"
