from __future__ import annotations

from collections import Counter
from functools import lru_cache
from pathlib import Path
from uuid import uuid4

import cv2
from ultralytics import YOLO

from app.config import settings
from app.models import ChatResponse, DetectionItem
from app.services.image_io import encode_image_data_url, extract_image_reference
from app.services.llm import invoke_vision


COUNT_WORDS = ("count", "how many", "detect", "detection", "đếm", "bao nhiêu", "phát hiện")


@lru_cache(maxsize=1)
def get_yolo_model() -> YOLO:
    return YOLO(str(settings.yolo_model_path))


def _target_from_prompt(prompt: str, labels: list[str]) -> str | None:
    lowered = prompt.lower()
    for label in labels:
        candidates = {label.lower(), f"{label.lower()}s"}
        if label.lower() == "person":
            candidates.add("people")
        if candidates & set(lowered.replace("?", " ").replace(".", " ").split()):
            return label
    return None


def describe_image(image_path_or_url: str, prompt: str = "Describe this image.") -> ChatResponse:
    data_url = encode_image_data_url(image_path_or_url)
    answer = invoke_vision(prompt, data_url)
    return ChatResponse(
        route="vision.describe",
        answer=answer,
        artifacts={"image_path_or_url": image_path_or_url},
    )


def detect_and_count(image_path_or_url: str, prompt: str = "Detect and count objects.") -> ChatResponse:
    results = get_yolo_model()(image_path_or_url, verbose=False)
    detections: list[DetectionItem] = []
    labels: list[str] = []
    annotated_url: str | None = None

    for result in results:
        class_names = result.names
        for box in result.boxes:
            class_id = int(box.cls[0])
            label = class_names[class_id]
            labels.append(label)
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            detections.append(
                DetectionItem(
                    label=label,
                    confidence=round(float(box.conf[0]), 4),
                    bbox=(x1, y1, x2, y2),
                )
            )

        plotted = result.plot()
        annotated_name = f"annotated-{uuid4().hex}.jpg"
        annotated_path = settings.upload_dir / annotated_name
        cv2.imwrite(str(annotated_path), plotted)
        annotated_url = f"/uploads/{annotated_name}"

    counts = dict(Counter(labels))
    target = _target_from_prompt(prompt, list(counts.keys()))
    if target:
        answer = f"Phát hiện {counts.get(target, 0)} đối tượng `{target}` trong ảnh."
    elif counts:
        count_text = ", ".join(f"{label}: {count}" for label, count in sorted(counts.items()))
        answer = f"Phát hiện các đối tượng: {count_text}."
    else:
        answer = "Không phát hiện được đối tượng rõ ràng trong ảnh."

    return ChatResponse(
        route="vision.detect",
        answer=answer,
        artifacts={
            "image_path_or_url": image_path_or_url,
            "counts": counts,
            "detections": [item.model_dump() for item in detections],
            "annotated_url": annotated_url,
        },
    )


def answer_vision(message: str, image_path_or_url: str | None = None) -> ChatResponse:
    image_ref = image_path_or_url or extract_image_reference(message)
    if not image_ref:
        return ChatResponse(
            route="vision",
            answer="Chưa tìm thấy đường dẫn ảnh hoặc URL ảnh trong yêu cầu.",
        )

    lowered = message.lower()
    if any(word in lowered for word in COUNT_WORDS):
        return detect_and_count(image_ref, prompt=message)
    return describe_image(image_ref, prompt=message)
