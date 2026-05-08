"""
Database Configuration
======================
Async SQLAlchemy engine, session factory, and Base for ORM models.
Uses asyncpg for PostgreSQL connections.
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

settings = get_settings()

# ── Engine ────────────────────────────────────────────────────────────────
engine_options = {
    "echo": settings.APP_ENV == "development",
    "pool_pre_ping": True,
}

if settings.DATABASE_URL.startswith("postgresql"):
    engine_options.update({"pool_size": 5, "max_overflow": 10})

engine = create_async_engine(settings.DATABASE_URL, **engine_options)

# ── Session factory ───────────────────────────────────────────────────────
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ── Base class ────────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    """Declarative base for all ORM models."""
    pass


# ── Dependency ────────────────────────────────────────────────────────────
async def get_db() -> AsyncSession:
    """FastAPI dependency — yields an async database session."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ── Table creation (dev convenience) ──────────────────────────────────────
async def create_tables():
    """Create all tables. Call from lifespan on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    """Drop all tables. Use with caution."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
