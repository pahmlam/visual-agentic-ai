from __future__ import annotations

from app.models import ChatRequest, ChatResponse
from app.services.image_io import extract_image_reference
from app.services.research import search_research
from app.services.vision import answer_vision


RESEARCH_HINTS = (
    "research",
    "paper",
    "papers",
    "arxiv",
    "wikipedia",
    "latest",
    "nghiên cứu",
    "bài báo",
    "tài liệu",
)

VISION_HINTS = (
    "image",
    "photo",
    "picture",
    "ảnh",
    "hình",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    "detect",
    "count",
    "describe",
)


def route_chat(request: ChatRequest) -> ChatResponse:
    message = request.message.strip()
    lowered = message.lower()
    image_ref = request.image_path_or_url or extract_image_reference(message)

    if request.mode == "research":
        return search_research(message)

    if request.mode == "vision":
        return answer_vision(message, image_ref)

    wants_vision = bool(image_ref) or any(hint in lowered for hint in VISION_HINTS)
    wants_research = any(hint in lowered for hint in RESEARCH_HINTS)

    if wants_vision and wants_research:
        vision_result = answer_vision(message, image_ref)
        research_query = (
            "Provide research background and relevant papers for this visual concept:\n"
            f"User request: {message}\n"
            f"Vision result: {vision_result.answer}"
        )
        research_result = search_research(research_query)
        return ChatResponse(
            route="supervisor.vision+research",
            answer=(
                "VISION\n"
                f"{vision_result.answer}\n\n"
                "RESEARCH\n"
                f"{research_result.answer}"
            ),
            sources=research_result.sources,
            artifacts=vision_result.artifacts,
        )

    if wants_vision:
        return answer_vision(message, image_ref)

    return search_research(message)

