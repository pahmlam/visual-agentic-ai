FROM node:20-alpine AS frontend-builder

WORKDIR /build

COPY frontend/package*.json frontend/
RUN cd frontend && npm ci

COPY frontend frontend
RUN cd frontend && npm run build


FROM python:3.10-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLCONFIGDIR=/app/data/.cache/matplotlib \
    YOLO_CONFIG_DIR=/app/data/.cache/ultralytics \
    XDG_CACHE_HOME=/app/data/.cache/xdg

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        libmagic1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app app
COPY --from=frontend-builder /build/app/static app/static

RUN mkdir -p /app/data/uploads /app/data/.cache /app/models

EXPOSE 8300

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8300"]
