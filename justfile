# Justfile for Observability and Telemetry project

# Show available commands
default:
    just --list

# Run the API locally
run:
    uv sync
    uv run uvicorn app.api:app --host 0.0.0.0 --port 8000 --reload

# Start all services (detached)
up:
    docker-compose -f infra/docker-compose.yml up -d

# Stop all services
down:
    docker-compose -f infra/docker-compose.yml down

# View logs (all services)
logs *args:
    docker-compose -f infra/docker-compose.yml logs -f {{ args }}

# Rebuild and restart everything
restart:
    docker-compose -f infra/docker-compose.yml down
    docker-compose -f infra/docker-compose.yml build
    docker-compose -f infra/docker-compose.yml up -d

# Stop and remove all data
clean:
    docker-compose -f infra/docker-compose.yml down -v
    find var/logs var/grafana var/minio -mindepth 1 ! -name ".gitkeep" -exec rm -rf {} + 2>/dev/null || true
    rm -rf .ruff_cache/
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Format and lint code
fmt:
    uv run ruff format . && uv run ruff check --fix .
