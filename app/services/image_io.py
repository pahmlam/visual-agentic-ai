from __future__ import annotations

import base64
import mimetypes
import re
from pathlib import Path
from urllib.parse import urlparse

import magic
import requests


IMAGE_REF_RE = re.compile(
    r"""(?ix)
    (?:
        image(?:_path|_url)?\s*[:=]\s*
        |img\s*[:=]\s*
        |path\s*[:=]\s*
    )?
    (?P<ref>
        https?://[^\s"'<>]+
        |
        [./~\w\-\s]+?\.(?:png|jpg|jpeg|webp)
    )
    """
)


def extract_image_reference(text: str) -> str | None:
    """Extract the first image path or URL from free-form text."""
    for match in IMAGE_REF_RE.finditer(text):
        ref = match.group("ref").strip().strip('"').strip("'").rstrip(".,)")
        if ref:
            return ref
    return None


def get_mime_type(path_or_url: str) -> str | None:
    if path_or_url.startswith(("http://", "https://")):
        try:
            response = requests.head(path_or_url, timeout=10, allow_redirects=True)
            mime = response.headers.get("content-type")
            if mime:
                return mime.split(";")[0].strip()
        except requests.RequestException:
            guessed, _ = mimetypes.guess_type(urlparse(path_or_url).path)
            return guessed
        return None

    path = Path(path_or_url).expanduser()
    if not path.exists() or not path.is_file():
        return None

    try:
        return magic.Magic(mime=True).from_file(str(path))
    except Exception:
        guessed, _ = mimetypes.guess_type(path.name)
        return guessed


def encode_image_data_url(path_or_url: str) -> str:
    """Return a data URL for a local image or remote image URL."""
    if path_or_url.startswith(("http://", "https://")):
        response = requests.get(path_or_url, timeout=20)
        response.raise_for_status()
        mime = response.headers.get("content-type", "image/png").split(";")[0].strip()
        if not mime.startswith("image/"):
            raise ValueError(f"URL does not point to an image: {mime}")
        raw = response.content
    else:
        path = Path(path_or_url).expanduser()
        if not path.exists() or not path.is_file():
            raise ValueError(f"Image file does not exist: {path_or_url}")
        mime = get_mime_type(str(path))
        if not mime or not mime.startswith("image/"):
            raise ValueError(f"Unsupported image MIME type: {mime}")
        raw = path.read_bytes()

    encoded = base64.b64encode(raw).decode("utf-8")
    return f"data:{mime};base64,{encoded}"

