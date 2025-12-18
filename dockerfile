FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy only dependency files first (better Docker cache)
COPY pyproject.toml uv.lock .python-version ./

# Create venv and install deps from lockfile
RUN uv sync --frozen

# Copy app code (FastAPI lives in app/)
COPY app ./app

# Ensure logs dirs exist in container (compose bind-mounts host logs into /app/logs)
RUN mkdir -p /app/logs

EXPOSE 8000

# Run using the venv created by uv (./.venv)
CMD ["./.venv/bin/uvicorn", "app.api:app", "--host", "0.0.0.0", "--port",  "8000"]

