# AGENTS.md

Instructions for Codex or new agents working in this repository.

## Working Language

- Answer the user in Vietnamese.
- Write technical notes, bug fixes, design decisions, or new knowledge in `docs/knowledge.md`.
- Keep answers concise, direct, and include file paths when necessary.

## Project Overview

`visual-agent` is a local web application split from `workspace.ipynb`.

The app consists of:

- Backend FastAPI: `app/main.py`
- Services:
  - `app/services/research.py`: Wikipedia + arXiv + Ollama text synthesis.
  - `app/services/vision.py`: provider-based vision description + YOLO detection/counting.
  - `app/services/router.py`: manual routing between research/vision.
  - `app/services/image_io.py`: processes paths/URLs/base64 images.
  - `app/services/llm.py`: selects Ollama/OpenAI/Gemini providers for LLM and VLM.
- Frontend Vue/Vite/TypeScript: `frontend/`
- Static build output: `app/static/`
- Knowledge log: `docs/knowledge.md`
- Original/reference notebook: `workspace.ipynb`

`workspace.ipynb` is no longer the main source of the application. When modifying the application, prioritize coding in `app/` and `frontend/`.

## Tech Stack

Backend:

- FastAPI
- Pydantic v2
- LangChain + `langchain-ollama`
- OpenAI Python SDK
- Gemini REST API via `requests`
- arXiv + Wikipedia wrappers
- Ultralytics YOLO

Frontend:

- Vue 3
- Vite
- TypeScript
- Single File Components
- Scoped CSS
- API client wrapper in `frontend/src/api/client.ts`

The frontend style is inspired by the repository:

```text
/Users/phamtunglam/Documents/Projects/knowte
```

UI characteristics to preserve:

- Dark alien/space/technology theme.
- Menlo/monospace font stack.
- Teal accent.
- Sharp radius of around 3px.
- Dense operational UI, not a landing page.
- Do not revert to manual static HTML/CSS/JS without a clear reason.

## Run Commands

Backend + built frontend:

```bash
./scripts/run_local.sh
```

URL:

```text
http://127.0.0.1:8300
```

Build frontend:

```bash
./scripts/build_frontend.sh
```

Or:

```bash
cd frontend
npm install
npm run build
```

Frontend dev mode:

```bash
cd frontend
npm run dev
```

Vite proxies `/api` and `/uploads` to FastAPI.
Vite runs by default at:

```text
http://127.0.0.1:5177
```

## Quick Check

Python compile:

```bash
venv/bin/python -m compileall app
```

Health:

```bash
curl -s http://127.0.0.1:8300/api/health
```

Frontend build:

```bash
cd frontend
npm run build
```

Smoke test FastAPI without network/model:

```bash
venv/bin/python - <<'PY'
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
print(client.get("/api/health").status_code)
print(client.post("/api/chat", json={"mode": "vision", "message": "describe this image"}).json())
PY
```

## Ollama and Local Models

Defaults:

- Text model: `llama3.2:3b`
- Vision model: `llama3.2-vision`

Declare in `.env` if needed:

```bash
OLLAMA_TEXT_MODEL=llama3.2:3b
OLLAMA_VISION_MODEL=llama3.2-vision
LLM_PROVIDER=ollama
VLM_PROVIDER=ollama
YOLO_MODEL_PATH=./yolo11x.pt
UPLOAD_DIR=./data/uploads
```

Notes:

- `llama3.2:3b` is a text model and cannot process images.
- `llama3.2-vision` is used for image description.
- Small local models may be weak at tool-calling/handoff. Therefore, the backend uses manual routing in `app/services/router.py` instead of relying entirely on a LangGraph supervisor.

## Provider Settings

- The UI has a `SETTINGS` button on the top bar to select the provider for LLM and VLM.
- Valid providers: `ollama`, `openai`, `gemini`.
- If `openai` or `gemini` is selected, the frontend will request a key if it is not already in `.env`.
- API keys are saved to `.env` via `POST /api/settings`.
- `GET /api/settings` does not return the raw key, only `has_openai_api_key` and `has_gemini_api_key`.
- The currently active model/provider is returned via `GET /api/health`.
- When modifying this section, remember to preserve the principle of not logging, not rendering, and not returning the API key to the client.

## Vision and YOLO

- YOLO weights are currently located at `./yolo11x.pt`.
- Uploaded images are stored in `data/uploads/`.
- Uploaded runtime files are ignored by git.
- Annotated detection images are also saved in `data/uploads/` and served via `/uploads/...`.

## Research

- The research route calls Wikipedia and arXiv over the network.
- arXiv may return HTTP 429 rate limit.
- `RateLimitFriendlyArxivAPIWrapper` in `app/services/research.py` uses `arxiv.Client(page_size=top_k_results, delay_seconds=5.0, num_retries=5)` to reduce oversized requests.
- If external sources fail, the endpoint should return a soft error instead of crashing the UI.

## Coding Conventions

- Do not commit secrets or API keys. Old notebooks may contain demo keys; do not copy them to the new source code.
- Do not modify the `knowte` repository when the user requests "following the knowte stack"; only read it for reference.
- When modifying the frontend:
  - Edit the source code in `frontend/src/`.
  - Run `npm run build`.
  - The build output will be written to `app/static/`.
- When modifying the backend:
  - Maintain the response schema in `app/models.py`.
  - Catch service errors and return helpful messages to the UI.
  - Do not let endpoints crash due to temporary Ollama/arXiv/Wikipedia errors.
- After significant changes, update `docs/knowledge.md`.
