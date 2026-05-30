from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


Mode = Literal["auto", "research", "vision"]
Provider = Literal["ollama", "openai", "gemini"]


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    mode: Mode = "auto"
    image_path_or_url: str | None = None


class ResearchRequest(BaseModel):
    query: str = Field(min_length=1)


class VisionRequest(BaseModel):
    image_path_or_url: str = Field(min_length=1)
    prompt: str = "Describe this image."


class DetectionRequest(BaseModel):
    image_path_or_url: str = Field(min_length=1)
    prompt: str = "Detect and count objects."


class UploadResponse(BaseModel):
    file_name: str
    path: str
    url: str


class DetectionItem(BaseModel):
    label: str
    confidence: float
    bbox: tuple[int, int, int, int]


class ChatResponse(BaseModel):
    route: str
    answer: str
    sources: dict[str, str] = Field(default_factory=dict)
    artifacts: dict[str, Any] = Field(default_factory=dict)


class MemoryEntry(BaseModel):
    id: str
    created_at: str
    user_message: str
    route: str
    answer: str
    sources: dict[str, str] = Field(default_factory=dict)
    artifacts_summary: dict[str, Any] = Field(default_factory=dict)


class MemoryListResponse(BaseModel):
    items: list[MemoryEntry]


class MemoryClearResponse(BaseModel):
    deleted: int


class HealthResponse(BaseModel):
    status: str
    llm_provider: Provider
    vlm_provider: Provider
    text_model: str
    vision_model: str
    yolo_model_path: str
    yolo_model_exists: bool


class ProviderSettingsResponse(BaseModel):
    llm_provider: Provider
    vlm_provider: Provider
    ollama_text_model: str
    ollama_vision_model: str
    openai_text_model: str
    openai_vision_model: str
    gemini_text_model: str
    gemini_vision_model: str
    has_openai_api_key: bool
    has_gemini_api_key: bool


class ProviderSettingsRequest(BaseModel):
    llm_provider: Provider
    vlm_provider: Provider
    ollama_text_model: str = Field(min_length=1)
    ollama_vision_model: str = Field(min_length=1)
    openai_text_model: str = Field(min_length=1)
    openai_vision_model: str = Field(min_length=1)
    gemini_text_model: str = Field(min_length=1)
    gemini_vision_model: str = Field(min_length=1)
    openai_api_key: str | None = None
    gemini_api_key: str | None = None
