# === Stage 1: Build dependencies ===
FROM python:3.12-slim AS builder

# Don't create .pyc files and flush logs immediately
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Isolated venv keeps runtime image clean
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements first — layer is cached until deps change
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# === Stage 2: Runtime (no build tools, smaller attack surface) ===
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Bring only the pre-built venv from builder
COPY --from=builder /opt/venv /opt/venv
COPY main.py .

# Non-root user (UID 1000) — never run as root in production
RUN addgroup --gid 1000 appgroup && \
    adduser --uid 1000 --gid 1000 --disabled-password --gecos "" appuser

USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
