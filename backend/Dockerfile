# syntax=docker/dockerfile:1

# Use the official UV Python base image with Python 3.13 on Debian Bookworm
ARG PYTHON_VERSION=3.13
FROM ghcr.io/astral-sh/uv:python${PYTHON_VERSION}-bookworm-slim AS base

# Keeps Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

# --- Build stage ---
FROM base AS build

# Install build dependencies required for native extensions
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
  && rm -rf /var/lib/apt/lists/*

# Application directory
WORKDIR /app

# Copy dependency specifications first for optimal layer caching
COPY pyproject.toml uv.lock ./
RUN mkdir -p src

# Install dependencies into virtualenv using UV
RUN uv sync --locked

# Copy remaining application source code
COPY . .

# Pre-download ML models / Silero VAD weights
RUN uv run python src/agent.py download-files

# --- Production stage ---
FROM base

ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/app" \
    --shell "/sbin/nologin" \
    --uid "${UID}" \
    appuser

# Explicitly set working directory for production runtime
WORKDIR /app

# Copy application and virtual environment from build stage
COPY --from=build --chown=appuser:appuser /app /app

# Ensure SQLite data directory exists and has proper permissions
RUN mkdir -p /app/data && chown -R appuser:appuser /app

# Switch to unprivileged user
USER appuser

# Health check port exposed for cloud web services (Render / Cloud Run)
EXPOSE 8080

# Execute voice agent via python inside UV virtualenv
CMD ["uv", "run", "python", "src/agent.py", "start"]
