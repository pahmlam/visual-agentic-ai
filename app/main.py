from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import STATIC_DIR, reload_settings, settings, write_env_values
from app.models import (
    ChatRequest,
    ChatResponse,
    DetectionRequest,
    HealthResponse,
    ProviderSettingsRequest,
    ProviderSettingsResponse,
    ResearchRequest,
    UploadResponse,
    VisionRequest,
)
from app.services.research import search_research
from app.services.router import route_chat
from app.services.vision import describe_image, detect_and_count
from app.services.llm import active_text_model, active_vision_model, clear_llm_cache


app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8300",
        "http://localhost:8300",
        "http://127.0.0.1:5177",
        "http://localhost:5177",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        llm_provider=settings.llm_provider,
        vlm_provider=settings.vlm_provider,
        text_model=active_text_model(),
        vision_model=active_vision_model(),
        yolo_model_path=str(settings.yolo_model_path),
        yolo_model_exists=settings.yolo_model_path.exists(),
    )


def _provider_settings_response() -> ProviderSettingsResponse:
    return ProviderSettingsResponse(
        llm_provider=settings.llm_provider,  # type: ignore[arg-type]
        vlm_provider=settings.vlm_provider,  # type: ignore[arg-type]
        ollama_text_model=settings.text_model,
        ollama_vision_model=settings.vision_model,
        openai_text_model=settings.openai_text_model,
        openai_vision_model=settings.openai_vision_model,
        gemini_text_model=settings.gemini_text_model,
        gemini_vision_model=settings.gemini_vision_model,
        has_openai_api_key=bool(settings.openai_api_key),
        has_gemini_api_key=bool(settings.gemini_api_key),
    )


@app.get("/api/settings", response_model=ProviderSettingsResponse)
def get_provider_settings() -> ProviderSettingsResponse:
    return _provider_settings_response()


def _clean_model_name(value: str, label: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise HTTPException(status_code=400, detail=f"{label} model is required.")
    return cleaned


@app.post("/api/settings", response_model=ProviderSettingsResponse)
def save_provider_settings(request: ProviderSettingsRequest) -> ProviderSettingsResponse:
    openai_key = (request.openai_api_key or "").strip() or settings.openai_api_key
    gemini_key = (request.gemini_api_key or "").strip() or settings.gemini_api_key

    needs_openai = request.llm_provider == "openai" or request.vlm_provider == "openai"
    needs_gemini = request.llm_provider == "gemini" or request.vlm_provider == "gemini"

    if needs_openai and not openai_key:
        raise HTTPException(status_code=400, detail="OpenAI API key is required for GPT provider.")
    if needs_gemini and not gemini_key:
        raise HTTPException(status_code=400, detail="Gemini API key is required for Gemini provider.")

    updates = {
        "LLM_PROVIDER": request.llm_provider,
        "VLM_PROVIDER": request.vlm_provider,
        "OLLAMA_TEXT_MODEL": _clean_model_name(
            request.ollama_text_model, "Ollama text"
        ),
        "OLLAMA_VISION_MODEL": _clean_model_name(
            request.ollama_vision_model, "Ollama vision"
        ),
        "OPENAI_TEXT_MODEL": _clean_model_name(
            request.openai_text_model, "OpenAI text"
        ),
        "OPENAI_VISION_MODEL": _clean_model_name(
            request.openai_vision_model, "OpenAI vision"
        ),
        "GEMINI_TEXT_MODEL": _clean_model_name(
            request.gemini_text_model, "Gemini text"
        ),
        "GEMINI_VISION_MODEL": _clean_model_name(
            request.gemini_vision_model, "Gemini vision"
        ),
    }
    if request.openai_api_key and request.openai_api_key.strip():
        updates["OPENAI_API_KEY"] = request.openai_api_key.strip()
    if request.gemini_api_key and request.gemini_api_key.strip():
        updates["GEMINI_API_KEY"] = request.gemini_api_key.strip()

    write_env_values(updates)
    reload_settings()
    clear_llm_cache()
    return _provider_settings_response()


@app.post("/api/upload", response_model=UploadResponse)
async def upload(file: UploadFile = File(...)) -> UploadResponse:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image uploads are supported.")

    suffix = Path(file.filename or "image.png").suffix.lower()
    if suffix not in {".png", ".jpg", ".jpeg", ".webp"}:
        raise HTTPException(status_code=400, detail="Use PNG, JPG/JPEG, or WEBP images.")

    raw = await file.read()
    if len(raw) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="Image is too large.")

    file_name = f"{uuid4().hex}{suffix}"
    path = settings.upload_dir / file_name
    path.write_bytes(raw)
    return UploadResponse(file_name=file_name, path=str(path), url=f"/uploads/{file_name}")


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    return route_chat(request)


@app.post("/api/research", response_model=ChatResponse)
def research(request: ResearchRequest) -> ChatResponse:
    return search_research(request.query)


@app.post("/api/vision/describe", response_model=ChatResponse)
def vision_describe(request: VisionRequest) -> ChatResponse:
    return describe_image(request.image_path_or_url, request.prompt)


@app.post("/api/vision/detect", response_model=ChatResponse)
def vision_detect(request: DetectionRequest) -> ChatResponse:
    return detect_and_count(request.image_path_or_url, request.prompt)


app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
