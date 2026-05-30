from __future__ import annotations

import json
import re
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.config import settings
from app.models import ChatResponse, MemoryEntry


_INIT_LOCK = threading.Lock()
_INITIALIZED_PATH: Path | None = None
_FTS_AVAILABLE: bool | None = None

STOPWORDS = {
    "about",
    "after",
    "again",
    "anything",
    "before",
    "could",
    "from",
    "have",
    "latest",
    "please",
    "research",
    "show",
    "tell",
    "that",
    "the",
    "this",
    "what",
    "when",
    "where",
    "which",
    "with",
    "would",
    "ảnh",
    "bài",
    "cho",
    "của",
    "hãy",
    "hình",
    "không",
    "là",
    "một",
    "nghiên",
    "này",
    "tôi",
    "về",
}

SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_\-]{20,}"),
    re.compile(r"AIza[0-9A-Za-z_\-]{20,}"),
    re.compile(
        r"(?i)\b(OPENAI_API_KEY|GEMINI_API_KEY|API_KEY)\s*=\s*[^\s]+"
    ),
)


def _connect() -> sqlite3.Connection:
    settings.memory_db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(settings.memory_db_path, timeout=15)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_db() -> None:
    global _FTS_AVAILABLE, _INITIALIZED_PATH
    if _INITIALIZED_PATH == settings.memory_db_path:
        return

    with _INIT_LOCK:
        if _INITIALIZED_PATH == settings.memory_db_path:
            return

        with _connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memory_entries (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    route TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    sources_json TEXT NOT NULL,
                    artifacts_summary_json TEXT NOT NULL,
                    searchable_text TEXT NOT NULL
                )
                """
            )
            try:
                conn.execute(
                    """
                    CREATE VIRTUAL TABLE IF NOT EXISTS memory_entries_fts
                    USING fts5(id UNINDEXED, searchable_text)
                    """
                )
                _FTS_AVAILABLE = True
            except sqlite3.Error:
                _FTS_AVAILABLE = False

        _INITIALIZED_PATH = settings.memory_db_path


def _truncate(value: str, max_chars: int) -> str:
    value = value.strip()
    if len(value) <= max_chars:
        return value
    return value[: max_chars - 3].rstrip() + "..."


def _scrub_secrets(text: str) -> str:
    cleaned = text
    for pattern in SECRET_PATTERNS:
        cleaned = pattern.sub("[REDACTED_SECRET]", cleaned)
    return cleaned


def _tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[\wÀ-ỹ]{3,}", text.lower(), re.UNICODE)
    return [token for token in tokens if token not in STOPWORDS]


def _json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _json_loads(value: str, default: Any) -> Any:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default


def _summarize_sources(sources: dict[str, str]) -> dict[str, str]:
    return {
        str(key): _scrub_secrets(_truncate(str(value), 1800))
        for key, value in sources.items()
    }


def _summarize_artifacts(artifacts: dict[str, Any]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for key, value in artifacts.items():
        if key in {"memory_used", "memory_error"}:
            continue
        if key == "detections" and isinstance(value, list):
            summary[key] = {"count": len(value)}
        elif key == "counts" and isinstance(value, dict):
            summary[key] = value
        elif key in {"annotated_url", "image_path_or_url"}:
            summary[key] = value
        elif isinstance(value, (str, int, float, bool)) or value is None:
            summary[key] = value
        else:
            summary[key] = _truncate(str(value), 400)
    return summary


def _row_to_entry(row: sqlite3.Row) -> MemoryEntry:
    return MemoryEntry(
        id=row["id"],
        created_at=row["created_at"],
        user_message=row["user_message"],
        route=row["route"],
        answer=row["answer"],
        sources=_json_loads(row["sources_json"], {}),
        artifacts_summary=_json_loads(row["artifacts_summary_json"], {}),
    )


def _public_entries(rows: list[sqlite3.Row]) -> list[MemoryEntry]:
    return [_row_to_entry(row) for row in rows]


def _fts_query(query: str) -> str:
    tokens = []
    seen = set()
    for token in _tokenize(query):
        if token in seen:
            continue
        seen.add(token)
        tokens.append(f'"{token}"')
        if len(tokens) >= 10:
            break
    return " OR ".join(tokens)


def _fallback_retrieve(query: str, limit: int) -> list[MemoryEntry]:
    query_tokens = set(_tokenize(query))
    if not query_tokens:
        return []

    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM memory_entries
            ORDER BY created_at DESC
            LIMIT 80
            """
        ).fetchall()

    scored: list[tuple[int, sqlite3.Row]] = []
    for row in rows:
        row_tokens = set(_tokenize(row["searchable_text"]))
        score = len(query_tokens & row_tokens)
        if score > 0:
            scored.append((score, row))

    scored.sort(key=lambda item: (item[0], item[1]["created_at"]), reverse=True)
    return _public_entries([row for _, row in scored[:limit]])


def retrieve_relevant(query: str, limit: int | None = None) -> list[MemoryEntry]:
    if not settings.memory_enabled:
        return []

    _ensure_db()
    limit = limit or settings.memory_max_results
    fts_query = _fts_query(query)
    if not fts_query:
        return []

    if _FTS_AVAILABLE:
        try:
            with _connect() as conn:
                rows = conn.execute(
                    """
                    SELECT m.*
                    FROM memory_entries_fts f
                    JOIN memory_entries m ON m.id = f.id
                    WHERE memory_entries_fts MATCH ?
                    ORDER BY bm25(memory_entries_fts)
                    LIMIT ?
                    """,
                    (fts_query, limit),
                ).fetchall()
            return _public_entries(rows)
        except sqlite3.Error:
            pass

    return _fallback_retrieve(query, limit)


def format_memory_context(entries: list[MemoryEntry]) -> str:
    if not entries:
        return ""

    lines = ["Relevant previous interactions:"]
    for entry in entries:
        timestamp = entry.created_at.split("T", 1)[0]
        lines.append(
            f"[{timestamp}] User asked: {_truncate(entry.user_message, 300)}\n"
            f"Assistant answered: {_truncate(entry.answer, 700)}"
        )
    return "\n\n".join(lines)


def store_interaction(
    user_message: str,
    response: ChatResponse,
) -> MemoryEntry | None:
    if not settings.memory_enabled:
        return None

    _ensure_db()
    entry_id = uuid4().hex
    created_at = datetime.now(timezone.utc).isoformat()
    sources = _summarize_sources(response.sources)
    artifacts_summary = _summarize_artifacts(response.artifacts)
    answer = _scrub_secrets(_truncate(response.answer, 4000))
    message = _scrub_secrets(_truncate(user_message, 1600))
    searchable_text = _scrub_secrets(
        "\n".join(
            [
                message,
                response.route,
                answer,
                _json_dumps(sources),
                _json_dumps(artifacts_summary),
            ]
        )
    )

    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO memory_entries (
                id,
                created_at,
                user_message,
                route,
                answer,
                sources_json,
                artifacts_summary_json,
                searchable_text
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry_id,
                created_at,
                message,
                response.route,
                answer,
                _json_dumps(sources),
                _json_dumps(artifacts_summary),
                searchable_text,
            ),
        )
        if _FTS_AVAILABLE:
            try:
                conn.execute(
                    """
                    INSERT INTO memory_entries_fts (id, searchable_text)
                    VALUES (?, ?)
                    """,
                    (entry_id, searchable_text),
                )
            except sqlite3.Error:
                pass

    return MemoryEntry(
        id=entry_id,
        created_at=created_at,
        user_message=message,
        route=response.route,
        answer=answer,
        sources=sources,
        artifacts_summary=artifacts_summary,
    )


def list_recent(limit: int = 50) -> list[MemoryEntry]:
    _ensure_db()
    safe_limit = max(1, min(limit, 200))
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM memory_entries
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (safe_limit,),
        ).fetchall()
    return _public_entries(rows)


def clear_memory() -> int:
    _ensure_db()
    with _connect() as conn:
        count = conn.execute("SELECT COUNT(*) FROM memory_entries").fetchone()[0]
        conn.execute("DELETE FROM memory_entries")
        if _FTS_AVAILABLE:
            try:
                conn.execute("DELETE FROM memory_entries_fts")
            except sqlite3.Error:
                pass
    return int(count)
