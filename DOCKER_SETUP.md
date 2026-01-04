# Docker Setup for Axelle AI Stack

This unified Docker Compose configuration orchestrates all three services:
- **aegra**: LangGraph server with agent orchestration
- **axelle_ai**: AI agent implementation with medical search capabilities
- **weaviate-min**: Vector database and search API

## Architecture

All services run on a shared `axelle_network` Docker network, allowing them to communicate using service names as hostnames.

### Services

1. **postgres** (port 5432) - PostgreSQL database for LangGraph metadata
2. **weaviate** (ports 8080, 50051) - Vector database for medical documents
3. **weaviate-api** (port 8001) - FastAPI service for Weaviate search
4. **aegra** (port 2024) - Main LangGraph server
5. **redis** (port 6379) - Optional caching layer

## Getting Started

### Start all services
```bash
cd aegra
docker compose up -d
```

### View logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f aegra
docker compose logs -f weaviate
```

### Stop services
```bash
docker compose down
```

### Rebuild after dependency changes
```bash
docker compose build
docker compose up -d
```

## Development Mode

All code directories are mounted as volumes for **live reload**:
- Changes to Python files are detected automatically
- No rebuild needed for code changes
- Only rebuild when dependencies in `pyproject.toml` change

### Volume Mounts
- `aegra/graphs` → `/app/graphs`
- `aegra/src` → `/app/src`
- `axelle_ai` → `/app/axelle_ai`
- `weaviate-min` → `/app/weaviate-min`

## Service Communication

Services communicate using Docker DNS:
- Aegra → Weaviate: `http://weaviate:8080`
- Aegra → Postgres: `postgresql+asyncpg://user:password@postgres:5432/aegra`
- Weaviate API → Weaviate: `http://weaviate:8080`

## Environment Variables

Set `WEAVIATE_URL=http://weaviate:8080` in the container (already configured).
For local development outside Docker, it defaults to `http://localhost:8080`.

## Accessing Services

From your host machine:
- Aegra API: http://localhost:2024
- Weaviate: http://localhost:8080
- Weaviate API: http://localhost:8001
- PostgreSQL: localhost:5432
