from __future__ import annotations

import base64
from functools import lru_cache
from urllib.parse import quote

import requests
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from openai import OpenAI

from app.config import settings


VISION_SYSTEM_PROMPT = (
    "You are an expert image describer. Describe only visible content. "
    "Avoid speculation. If text appears, transcribe it accurately. Answer in English."
)


@lru_cache(maxsize=8)
def get_ollama_text_llm(model: str, base_url: str) -> ChatOllama:
    return ChatOllama(model=model, base_url=base_url, temperature=0)


@lru_cache(maxsize=8)
def get_ollama_vision_llm(model: str, base_url: str) -> ChatOllama:
    return ChatOllama(model=model, base_url=base_url, temperature=0)


def clear_llm_cache() -> None:
    get_ollama_text_llm.cache_clear()
    get_ollama_vision_llm.cache_clear()


def active_text_model() -> str:
    if settings.llm_provider == "openai":
        return settings.openai_text_model
    if settings.llm_provider == "gemini":
        return settings.gemini_text_model
    return settings.text_model


def active_vision_model() -> str:
    if settings.vlm_provider == "openai":
        return settings.openai_vision_model
    if settings.vlm_provider == "gemini":
        return settings.gemini_vision_model
    return settings.vision_model


def _require_key(value: str, label: str) -> str:
    if not value:
        raise RuntimeError(f"{label} API key is missing. Open Settings and save a key.")
    return value


def _invoke_openai_text(prompt: str) -> str:
    client = OpenAI(api_key=_require_key(settings.openai_api_key, "OpenAI"))
    response = client.chat.completions.create(
        model=settings.openai_text_model,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content or ""


def _invoke_openai_vision(prompt: str, data_url: str) -> str:
    client = OpenAI(api_key=_require_key(settings.openai_api_key, "OpenAI"))
    response = client.chat.completions.create(
        model=settings.openai_vision_model,
        temperature=0,
        messages=[
            {"role": "system", "content": VISION_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            },
        ],
    )
    return response.choices[0].message.content or ""


def _gemini_generate(model: str, parts: list[dict]) -> str:
    api_key = _require_key(settings.gemini_api_key, "Gemini")
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{quote(model, safe='')}:generateContent"
    )
    response = requests.post(
        url,
        params={"key": api_key},
        json={
            "contents": [{"role": "user", "parts": parts}],
            "generationConfig": {"temperature": 0},
        },
        timeout=90,
    )
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        detail = response.text[:500]
        raise RuntimeError(
            f"Gemini API request failed with HTTP {response.status_code}: {detail}"
        ) from exc
    data = response.json()
    candidates = data.get("candidates") or []
    if not candidates:
        return ""
    parts = candidates[0].get("content", {}).get("parts", [])
    return "\n".join(part.get("text", "") for part in parts).strip()


def _invoke_gemini_text(prompt: str) -> str:
    return _gemini_generate(settings.gemini_text_model, [{"text": prompt}])


def _split_data_url(data_url: str) -> tuple[str, str]:
    header, encoded = data_url.split(",", 1)
    mime_type = header.removeprefix("data:").split(";")[0]
    # Validate base64 early so Gemini receives clean inline data.
    base64.b64decode(encoded)
    return mime_type, encoded


def _invoke_gemini_vision(prompt: str, data_url: str) -> str:
    mime_type, encoded = _split_data_url(data_url)
    return _gemini_generate(
        settings.gemini_vision_model,
        [
            {"text": f"{VISION_SYSTEM_PROMPT}\n\n{prompt}"},
            {"inline_data": {"mime_type": mime_type, "data": encoded}},
        ],
    )


def invoke_text(prompt: str) -> str:
    if settings.llm_provider == "openai":
        return _invoke_openai_text(prompt)
    if settings.llm_provider == "gemini":
        return _invoke_gemini_text(prompt)
    response = get_ollama_text_llm(
        settings.text_model, settings.ollama_base_url
    ).invoke(prompt)
    return getattr(response, "content", str(response))


def invoke_vision(prompt: str, data_url: str) -> str:
    if settings.vlm_provider == "openai":
        return _invoke_openai_vision(prompt, data_url)
    if settings.vlm_provider == "gemini":
        return _invoke_gemini_vision(prompt, data_url)

    messages = [
        SystemMessage(content=VISION_SYSTEM_PROMPT),
        HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": data_url}},
            ]
        ),
    ]
    response = get_ollama_vision_llm(
        settings.vision_model, settings.ollama_base_url
    ).invoke(messages)
    return getattr(response, "content", str(response))
