"""Async Postgres connection pool for RAG backend."""

import asyncpg
from contextlib import asynccontextmanager
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Global connection pool
_pool: Optional[asyncpg.Pool] = None


async def init_db_pool() -> asyncpg.Pool:
    """Initialize the database connection pool."""
    global _pool

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is required")

    _pool = await asyncpg.create_pool(
        database_url,
        min_size=2,
        max_size=10,
        command_timeout=60,
        ssl="require",
    )

    return _pool


async def get_db_pool() -> asyncpg.Pool:
    """Get the database connection pool, initializing if needed."""
    global _pool

    if _pool is None:
        _pool = await init_db_pool()

    return _pool


async def close_db_pool():
    """Close the database connection pool."""
    global _pool

    if _pool is not None:
        await _pool.close()
        _pool = None


@asynccontextmanager
async def get_connection():
    """Get a database connection from the pool."""
    pool = await get_db_pool()
    async with pool.acquire() as connection:
        yield connection


async def fetch_user_profile(user_id: str) -> Optional[dict]:
    """Fetch user profile for personalization."""
    async with get_connection() as conn:
        row = await conn.fetchrow(
            """
            SELECT
                user_id,
                software_background,
                hardware_background,
                background_summary,
                preferred_language,
                personalization_enabled,
                onboarding_completed
            FROM user_profiles
            WHERE user_id = $1
            """,
            user_id,
        )

        if row:
            return dict(row)
        return None


async def get_translation_cache(
    source_path: str, content_hash: str, target_language: str = "ur"
) -> Optional[str]:
    """Check translation cache for existing translation."""
    async with get_connection() as conn:
        row = await conn.fetchrow(
            """
            SELECT translated_content
            FROM translation_cache
            WHERE source_path = $1
              AND content_hash = $2
              AND target_language = $3
              AND (expires_at IS NULL OR expires_at > NOW())
            """,
            source_path,
            content_hash,
            target_language,
        )

        if row:
            return row["translated_content"]
        return None


async def set_translation_cache(
    source_path: str,
    content_hash: str,
    translated_content: str,
    target_language: str = "ur",
    model_version: str = None,
) -> None:
    """Store translation in cache."""
    async with get_connection() as conn:
        await conn.execute(
            """
            INSERT INTO translation_cache
                (source_path, content_hash, target_language, translated_content, model_version)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (source_path, content_hash, target_language)
            DO UPDATE SET
                translated_content = $4,
                model_version = $5,
                created_at = NOW()
            """,
            source_path,
            content_hash,
            target_language,
            translated_content,
            model_version,
        )


async def get_personalization_cache(
    user_id: str, source_path: str, content_hash: str, profile_hash: str
) -> Optional[str]:
    """Check personalization cache for existing personalized content."""
    async with get_connection() as conn:
        row = await conn.fetchrow(
            """
            SELECT personalized_content
            FROM personalization_cache
            WHERE user_id = $1
              AND source_path = $2
              AND content_hash = $3
              AND profile_hash = $4
            """,
            user_id,
            source_path,
            content_hash,
            profile_hash,
        )

        if row:
            return row["personalized_content"]
        return None


async def set_personalization_cache(
    user_id: str,
    source_path: str,
    content_hash: str,
    profile_hash: str,
    personalized_content: str,
    model_version: str = None,
) -> None:
    """Store personalized content in cache."""
    async with get_connection() as conn:
        await conn.execute(
            """
            INSERT INTO personalization_cache
                (user_id, source_path, content_hash, profile_hash, personalized_content, model_version)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (user_id, source_path, content_hash, profile_hash)
            DO UPDATE SET
                personalized_content = $5,
                model_version = $6,
                created_at = NOW()
            """,
            user_id,
            source_path,
            content_hash,
            profile_hash,
            personalized_content,
            model_version,
        )
