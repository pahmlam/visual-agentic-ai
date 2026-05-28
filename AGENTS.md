# AGENTS.md

Hướng dẫn cho Codex hoặc agent mới khi làm việc trong repo này.

## Ngôn ngữ Làm Việc

- Trả lời người dùng bằng tiếng Việt.
- Ghi chú kỹ thuật, fix bug, quyết định thiết kế, hoặc kiến thức mới vào `docs/knowledge.md`.
- Giữ câu trả lời gọn, trực tiếp, có đường dẫn file khi cần.

## Tổng Quan Project

`visual-agent` là web app local được tách từ `workspace.ipynb`.

App gồm:

- Backend FastAPI: `app/main.py`
- Services:
  - `app/services/research.py`: Wikipedia + arXiv + Ollama text synthesis.
  - `app/services/vision.py`: provider-based vision description + YOLO detection/counting.
  - `app/services/router.py`: route thủ công giữa research/vision.
  - `app/services/image_io.py`: xử lý path/URL/base64 image.
  - `app/services/llm.py`: chọn provider Ollama/OpenAI/Gemini cho LLM và VLM.
- Frontend Vue/Vite/TypeScript: `frontend/`
- Static build output: `app/static/`
- Knowledge log: `docs/knowledge.md`
- Notebook gốc/tham khảo: `workspace.ipynb`

`workspace.ipynb` không còn là source chính của app. Khi sửa app, ưu tiên code trong `app/` và `frontend/`.

## Tech Stack

Backend:

- FastAPI
- Pydantic v2
- LangChain + `langchain-ollama`
- OpenAI Python SDK
- Gemini REST API qua `requests`
- arXiv + Wikipedia wrappers
- Ultralytics YOLO

Frontend:

- Vue 3
- Vite
- TypeScript
- Single File Components
- Scoped CSS
- API client wrapper trong `frontend/src/api/client.ts`

Frontend style được lấy cảm hứng từ repo:

```text
/Users/phamtunglam/Documents/Projects/knowte
```

Các đặc điểm UI cần giữ:

- Dark alien/space/technology theme.
- Menlo/monospace font stack.
- Teal accent.
- Sharp radius khoảng 3px.
- Dense operational UI, không làm landing page.
- Không quay lại static HTML/CSS/JS thủ công nếu không có lý do rõ ràng.

## Lệnh Chạy

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

Hoặc:

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

Vite proxy `/api` và `/uploads` về FastAPI.
Vite mặc định chạy ở:

```text
http://127.0.0.1:5177
```

## Kiểm Tra Nhanh

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

Smoke test FastAPI không cần network/model:

```bash
venv/bin/python - <<'PY'
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
print(client.get("/api/health").status_code)
print(client.post("/api/chat", json={"mode": "vision", "message": "describe this image"}).json())
PY
```

## Ollama Và Model Local

Mặc định:

- Text model: `llama3.2:3b`
- Vision model: `llama3.2-vision`

Khai báo trong `.env` nếu cần:

```bash
OLLAMA_TEXT_MODEL=llama3.2:3b
OLLAMA_VISION_MODEL=llama3.2-vision
LLM_PROVIDER=ollama
VLM_PROVIDER=ollama
YOLO_MODEL_PATH=./yolo11x.pt
UPLOAD_DIR=./data/uploads
```

Lưu ý:

- `llama3.2:3b` là text model, không đọc ảnh.
- `llama3.2-vision` dùng cho mô tả ảnh.
- Local model nhỏ có thể yếu ở tool-calling/handoff. Vì vậy backend đang dùng router thủ công trong `app/services/router.py` thay vì phụ thuộc hoàn toàn vào LangGraph supervisor.

## Provider Settings

- UI có một nút `SETTINGS` trên top bar để chọn provider cho LLM và VLM.
- Provider hợp lệ: `ollama`, `openai`, `gemini`.
- Nếu chọn `openai` hoặc `gemini`, frontend yêu cầu nhập key nếu `.env` chưa có key.
- API keys được lưu vào `.env` bởi `POST /api/settings`.
- `GET /api/settings` không trả raw key, chỉ trả `has_openai_api_key` và `has_gemini_api_key`.
- Model/provider đang active được trả qua `GET /api/health`.
- Khi sửa phần này, nhớ giữ nguyên nguyên tắc không log, không render, không trả API key về client.

## Vision Và YOLO

- YOLO weights hiện nằm ở `./yolo11x.pt`.
- Upload ảnh lưu vào `data/uploads/`.
- File upload runtime bị ignore bởi git.
- Annotated detection images cũng được lưu vào `data/uploads/` và serve qua `/uploads/...`.

## Research

- Research route gọi Wikipedia và arXiv qua network.
- arXiv có thể rate-limit HTTP 429.
- `RateLimitFriendlyArxivAPIWrapper` trong `app/services/research.py` dùng `arxiv.Client(page_size=top_k_results, delay_seconds=5.0, num_retries=5)` để giảm request quá lớn.
- Nếu source ngoài lỗi, endpoint vẫn nên trả lỗi mềm thay vì crash UI.

## Quy Ước Code

- Không commit secrets hoặc API keys. Notebook cũ có thể chứa key demo; không copy sang source mới.
- Không sửa repo `knowte` khi user yêu cầu “theo stack knowte”; chỉ đọc để tham khảo.
- Khi sửa frontend:
  - Sửa source trong `frontend/src/`.
  - Chạy `npm run build`.
  - Build output sẽ ghi vào `app/static/`.
- Khi sửa backend:
  - Giữ response schema trong `app/models.py`.
  - Bắt lỗi service và trả thông báo có ích cho UI.
  - Không để endpoint crash vì Ollama/arXiv/Wikipedia tạm lỗi.
- Sau thay đổi đáng kể, cập nhật `docs/knowledge.md`.
