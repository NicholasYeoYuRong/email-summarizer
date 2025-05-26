# Use official Python slim image
FROM python:3.13.0-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_VENV=/opt/venv \
    PATH="/root/.local/bin:$PATH"

# Install system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
    curl git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install UV with pipx (most reliable method)
RUN python -m pip install --user pipx && \
    python -m pipx ensurepath && \
    pipx install uv

# Create and activate virtual environment
RUN python -m venv $UV_VENV
ENV PATH="$UV_VENV/bin:$PATH"

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies with UV
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install .

# Runtime stage
FROM python:3.13.0-slim

ENV UV_VENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

# Install Ollama and runtime dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
    curl && \
    curl -fsSL https://ollama.com/install.sh | sh && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

WORKDIR /app

# Copy application code
COPY . .

EXPOSE 8000


CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port 8000"]
