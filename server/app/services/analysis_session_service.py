"""
Persist and load analysis session payloads (transactions, insights, dashboard summary).

Uses lightweight driver-level persistence so local SQLite works even when
SQLAlchemy async extras such as greenlet are unavailable.
"""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import aiosqlite

from app.core.config import get_settings
from app.services.dashboard_builder import build_dashboard_data
from app.services.store import FileResults

logger = logging.getLogger(__name__)
settings = get_settings()

_session_cache: Dict[str, Dict[str, Any]] = {}
_init_lock = asyncio.Lock()
_initialized = False


def _serialize_transactions(results: FileResults) -> list:
    if not results.categorization_result:
        return []
    return [
        t.model_dump(mode="json")
        for t in results.categorization_result.transactions
    ]


def _serialize_insights(results: FileResults) -> dict:
    if not results.profile_result:
        return {}
    return results.profile_result.model_dump(mode="json")


def _serialize_summary(results: FileResults, file_id: str) -> dict:
    dashboard = build_dashboard_data(file_id, results)
    return dashboard.model_dump(mode="json")


def _build_payload(results: FileResults) -> Dict[str, Any]:
    file_id = results.file_id
    return {
        "transactions": _serialize_transactions(results),
        "insights": _serialize_insights(results),
        "summary": _serialize_summary(results, file_id),
    }


def _db_url() -> str:
    return settings.DATABASE_URL


def _is_sqlite(url: str) -> bool:
    return url.startswith("sqlite")


def _is_postgres(url: str) -> bool:
    return url.startswith("postgresql+asyncpg://") or url.startswith("postgresql://")


def _sqlite_path(url: str) -> Path:
    for prefix in ("sqlite+aiosqlite:///", "sqlite:///"):
        if url.startswith(prefix):
            raw = url[len(prefix):]
            return Path(raw)
    raise ValueError(f"Unsupported SQLite URL: {url}")


async def _init_sqlite() -> None:
    path = _sqlite_path(_db_url())
    if path.parent and str(path.parent) not in ("", "."):
        path.parent.mkdir(parents=True, exist_ok=True)

    async with aiosqlite.connect(path) as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS analysis_sessions (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                transactions TEXT NOT NULL,
                insights TEXT NOT NULL,
                summary TEXT NOT NULL
            )
            """
        )
        await conn.commit()


async def _init_postgres() -> None:
    import asyncpg

    dsn = _db_url().replace("postgresql+asyncpg://", "postgresql://", 1)
    conn = await asyncpg.connect(dsn)
    try:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS analysis_sessions (
                id UUID PRIMARY KEY,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                transactions JSONB NOT NULL,
                insights JSONB NOT NULL,
                summary JSONB NOT NULL
            )
            """
        )
    finally:
        await conn.close()


async def initialize_session_store() -> None:
    """Initialize durable session storage when a supported DB URL is configured."""
    global _initialized

    if _initialized:
        return

    async with _init_lock:
        if _initialized:
            return

        url = _db_url()

        if _is_sqlite(url):
            await _init_sqlite()
            logger.info("Initialized SQLite session store at %s", _sqlite_path(url))
        elif _is_postgres(url):
            await _init_postgres()
            logger.info("Initialized PostgreSQL session store")
        else:
            logger.warning("Unsupported DATABASE_URL for session persistence: %s", url)

        _initialized = True


async def _persist_sqlite(session_id: str, payload: Dict[str, Any]) -> None:
    path = _sqlite_path(_db_url())
    async with aiosqlite.connect(path) as conn:
        await conn.execute(
            """
            INSERT OR REPLACE INTO analysis_sessions
                (id, created_at, transactions, insights, summary)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                session_id,
                datetime.now(timezone.utc).isoformat(),
                json.dumps(payload["transactions"]),
                json.dumps(payload["insights"]),
                json.dumps(payload["summary"]),
            ),
        )
        await conn.commit()


async def _persist_postgres(session_id: str, payload: Dict[str, Any]) -> None:
    import asyncpg

    dsn = _db_url().replace("postgresql+asyncpg://", "postgresql://", 1)
    conn = await asyncpg.connect(dsn)
    try:
        await conn.execute(
            """
            INSERT INTO analysis_sessions (id, created_at, transactions, insights, summary)
            VALUES ($1::uuid, NOW(), $2::jsonb, $3::jsonb, $4::jsonb)
            ON CONFLICT (id) DO UPDATE SET
                transactions = EXCLUDED.transactions,
                insights = EXCLUDED.insights,
                summary = EXCLUDED.summary
            """,
            session_id,
            json.dumps(payload["transactions"]),
            json.dumps(payload["insights"]),
            json.dumps(payload["summary"]),
        )
    finally:
        await conn.close()


async def persist_analysis_session(results: FileResults) -> str:
    """Save pipeline results and fall back to in-memory cache if DB is unavailable."""
    session_id = str(uuid.uuid4())
    payload = _build_payload(results)
    _session_cache[session_id] = payload

    try:
        await initialize_session_store()

        url = _db_url()
        if _is_sqlite(url):
            await _persist_sqlite(session_id, payload)
        elif _is_postgres(url):
            await _persist_postgres(session_id, payload)
        else:
            logger.warning(
                "Skipping durable session persistence for %s because DATABASE_URL is unsupported",
                session_id,
            )
            return session_id

        logger.info("Persisted analysis session %s to durable store", session_id)
    except Exception as exc:
        logger.warning(
            "Durable session persistence unavailable for %s; using in-memory fallback: %s",
            session_id,
            exc,
        )

    return session_id


async def _load_sqlite(session_id: str) -> Optional[Dict[str, Any]]:
    path = _sqlite_path(_db_url())
    async with aiosqlite.connect(path) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute(
            """
            SELECT transactions, insights, summary
            FROM analysis_sessions
            WHERE id = ?
            """,
            (session_id,),
        ) as cursor:
            row = await cursor.fetchone()

    if row is None:
        return None

    return {
        "transactions": json.loads(row["transactions"]),
        "insights": json.loads(row["insights"]),
        "summary": json.loads(row["summary"]),
    }


async def _load_postgres(session_id: str) -> Optional[Dict[str, Any]]:
    import asyncpg

    dsn = _db_url().replace("postgresql+asyncpg://", "postgresql://", 1)
    conn = await asyncpg.connect(dsn)
    try:
        row = await conn.fetchrow(
            """
            SELECT transactions, insights, summary
            FROM analysis_sessions
            WHERE id = $1::uuid
            """,
            session_id,
        )
    finally:
        await conn.close()

    if row is None:
        return None

    return {
        "transactions": row["transactions"],
        "insights": row["insights"],
        "summary": row["summary"],
    }


async def get_session_payload(session_id: str) -> Optional[Dict[str, Any]]:
    """Load session JSON blobs from memory first, then durable storage if available."""
    cached = _session_cache.get(session_id)
    if cached is not None:
        return cached

    try:
        await initialize_session_store()

        url = _db_url()
        if _is_sqlite(url):
            payload = await _load_sqlite(session_id)
        elif _is_postgres(url):
            payload = await _load_postgres(session_id)
        else:
            payload = None
    except Exception as exc:
        logger.warning(
            "Durable session lookup unavailable for %s: %s",
            session_id,
            exc,
        )
        return None

    if payload is not None:
        _session_cache[session_id] = payload

    return payload
