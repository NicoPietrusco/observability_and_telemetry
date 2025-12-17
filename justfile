# Justfile for Observability and Telemetry project

# Show available commands
default:
    just --list

# Run the API locally
run:
    uv sync
    uv run uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload

# Start all services (detached)
up:
    docker-compose up -d

# Stop all services
down:
    docker-compose down

# View logs (all services)
logs *args:
    docker-compose logs -f {{ args }}

# Rebuild and restart everything
restart:
    docker-compose down
    docker-compose build
    docker-compose up -d

# Stop and remove all data
clean:
    docker-compose down -v
    find logs grafana-data minio-data -mindepth 1 ! -name ".gitkeep" -exec rm -rf {} + 2>/dev/null || true
    rm -rf .ruff_cache/
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Format and lint code
fmt:
    uv run ruff format . && uv run ruff check --fix .
