# Production Worker Dockerfile for Asynchronous Celery Tasks
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    tesseract-ocr \
    tesseract-ocr-all \
    poppler-utils \
    ghostscript \
    qpdf \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY ../backend/requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app/workers
COPY ../backend/app /app/backend/app

ENV PYTHONPATH="/app/backend:/app/workers"
WORKDIR /app/workers

CMD ["celery", "-A", "celery_app", "worker", "--loglevel=info", "--concurrency=4"]
