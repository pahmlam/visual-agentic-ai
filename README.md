# Visual Agent

Local web app for a visual/research agent pipeline.

## What It Runs

- FastAPI backend at `http://127.0.0.1:8300`
- Vue 3 + Vite + TypeScript frontend built into FastAPI static assets
- Selectable LLM provider: Ollama local, GPT/OpenAI, or Gemini
- Selectable VLM provider: Ollama local, GPT/OpenAI, or Gemini
- YOLO model for object detection and counting
- arXiv and Wikipedia tools for research lookup

Ollama and YOLO run locally. Research lookup calls arXiv/Wikipedia over the network. GPT/OpenAI and Gemini modes call their provider APIs.

## Requirements

- Python virtual environment in `venv/`
- Ollama running locally
- Models:

```bash
ollama pull llama3.2:3b
ollama pull llama3.2-vision
```

- YOLO weights at `./yolo11x.pt`

## Setup

```bash
source venv/bin/activate
pip install -r requirements.txt
```

Frontend setup:

```bash
cd frontend
npm install
npm run build
cd ..
```

Optional config:

```bash
cp .env.example .env
```

The Settings button in the UI can update provider/model values and store API keys in `.env`.
If you select GPT/OpenAI or Gemini, enter the key in Settings once; the app stores it as `OPENAI_API_KEY` or `GEMINI_API_KEY`.

## Run

```bash
./scripts/run_local.sh
```

Open:

```text
http://127.0.0.1:8300
```

Frontend dev mode, with API proxy to FastAPI:

```bash
cd frontend
npm run dev
```

Open the Vite URL, usually:

```text
http://127.0.0.1:5177
```

## Provider Settings

Use the `SETTINGS` button in the top bar to choose:

- LLM provider for text/research synthesis: `ollama`, `openai`, or `gemini`
- VLM provider for image description: `ollama`, `openai`, or `gemini`
- Model names for each provider
- API keys for GPT/OpenAI or Gemini

The backend saves these values into `.env`. API keys are never returned to the frontend; the UI only receives `has_openai_api_key` and `has_gemini_api_key`.

## API

- `GET /api/health`
- `POST /api/upload`
- `POST /api/chat`
- `POST /api/research`
- `POST /api/vision/describe`
- `POST /api/vision/detect`

Example:

```bash
curl -X POST http://127.0.0.1:8300/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"mode":"research","message":"What is the latest research on positional embeddings?"}'
```

## Notes

- The frontend follows the same stack style as `knowte`: Vue 3, Vite, TypeScript, scoped Vue component CSS, and a small API client wrapper.
- The UI uses a local monospace stack: `Menlo`, `Monaco`, `Consolas`, monospace.
- Local small models can be weak at tool-calling, so the backend routes requests explicitly instead of relying only on LangGraph handoff.
- Uploaded files are stored under `data/uploads/` and ignored by git.
