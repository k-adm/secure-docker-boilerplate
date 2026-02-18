import os
from contextlib import asynccontextmanager

import asyncpg
from fastapi import FastAPI

# Database connection settings from environment variables
DB_CONFIG = {
    "user": os.getenv("DB_USER", "appuser"),
    "password": os.getenv("DB_PASS", "change_me_in_production"),
    "host": os.getenv("DB_HOST", "db"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "appdb"),
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create connection pool on startup, close on shutdown."""
    app.state.db_pool = await asyncpg.create_pool(**DB_CONFIG, min_size=2, max_size=10)
    yield
    await app.state.db_pool.close()


app = FastAPI(
    title="Secure Docker Boilerplate",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None,
    lifespan=lifespan,
)


@app.get("/")
async def root():
    """Service info — quick way to verify the app is alive."""
    return {
        "service": "secure-docker-boilerplate",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
async def health():
    """Lightweight probe for docker-compose healthcheck."""
    return {"status": "ok"}


@app.get("/db/health")
async def db_health():
    """End-to-end check: app -> PostgreSQL connectivity."""
    try:
        result = await app.state.db_pool.fetchval("SELECT 1")
        return {"database": "ok", "result": result}
    except Exception as e:
        return {"database": "error", "detail": str(e)}
