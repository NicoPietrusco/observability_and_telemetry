# Justfile for Observability and Telemetry project

# Show available commands
default:
    just --list

# Run the API locally
local-run:
    uv sync
    uv run uvicorn app.api:app --host 0.0.0.0 --port 8000 --reload

# Ensure the shared network exists (needed because the split compose files use an external network)
net:
    docker network create observability-network 2>/dev/null || true

# Start the stack (default = cloud-like two-unit topology)
up: net
    COMPOSE_PROJECT_NAME=otel-obs docker compose -f infra/docker-compose.obs.yml up -d
    COMPOSE_PROJECT_NAME=otel-api docker compose -f infra/docker-compose.api.yml up -d

# Cloud-like: run as two units (API unit + OBS unit)
up-obs:
    just net
    COMPOSE_PROJECT_NAME=otel-obs docker compose -f infra/docker-compose.obs.yml up -d

up-api:
    just net
    COMPOSE_PROJECT_NAME=otel-api docker compose -f infra/docker-compose.api.yml up -d

# Stop the stack (recommended order)
down:
    COMPOSE_PROJECT_NAME=otel-api docker compose -f infra/docker-compose.api.yml down
    COMPOSE_PROJECT_NAME=otel-obs docker compose -f infra/docker-compose.obs.yml down

down-obs:
    COMPOSE_PROJECT_NAME=otel-obs docker compose -f infra/docker-compose.obs.yml down

down-api:
    COMPOSE_PROJECT_NAME=otel-api docker compose -f infra/docker-compose.api.yml down

# View logs (both units)
logs *args:
    sh -c 'COMPOSE_PROJECT_NAME=otel-obs docker compose -f infra/docker-compose.obs.yml logs -f {{ args }} & COMPOSE_PROJECT_NAME=otel-api docker compose -f infra/docker-compose.api.yml logs -f {{ args }} & wait'

logs-obs *args:
    COMPOSE_PROJECT_NAME=otel-obs docker compose -f infra/docker-compose.obs.yml logs -f {{ args }}

logs-api *args:
    COMPOSE_PROJECT_NAME=otel-api docker compose -f infra/docker-compose.api.yml logs -f {{ args }}

# Rebuild and restart everything (both units)
restart:
    COMPOSE_PROJECT_NAME=otel-api docker compose -f infra/docker-compose.api.yml down
    COMPOSE_PROJECT_NAME=otel-obs docker compose -f infra/docker-compose.obs.yml down
    COMPOSE_PROJECT_NAME=otel-obs docker compose -f infra/docker-compose.obs.yml build
    COMPOSE_PROJECT_NAME=otel-api docker compose -f infra/docker-compose.api.yml build
    COMPOSE_PROJECT_NAME=otel-obs docker compose -f infra/docker-compose.obs.yml up -d
    COMPOSE_PROJECT_NAME=otel-api docker compose -f infra/docker-compose.api.yml up -d

# Stop and remove all data (both units)
clean:
    COMPOSE_PROJECT_NAME=otel-api docker compose -f infra/docker-compose.api.yml down -v
    COMPOSE_PROJECT_NAME=otel-obs docker compose -f infra/docker-compose.obs.yml down -v
    find var/logs var/grafana var/minio -mindepth 1 ! -name ".gitkeep" -exec rm -rf {} + 2>/dev/null || true
    rm -rf .ruff_cache/
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Format and lint code
fmt:
    uv run ruff format . && uv run ruff check --fix .
