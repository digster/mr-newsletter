"""SQLAlchemy base model and database engine configuration."""

import logging
from collections.abc import AsyncGenerator
from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.config.settings import get_settings

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    """Get current UTC datetime.

    Used as Python-side default for timestamps, compatible with both SQLite and PostgreSQL.
    """
    return datetime.now(UTC)


class Base(DeclarativeBase):
    """Base model for all database entities."""

    pass


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps.

    Uses Python-side defaults for SQLite compatibility.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )


_engine = None
_async_session_maker = None


def get_async_engine():
    """Get or create async engine with database-specific configuration."""
    global _engine
    if _engine is None:
        settings = get_settings()

        engine_kwargs = {
            "echo": settings.debug,
        }

        if settings.is_desktop_mode:
            # SQLite configuration
            from sqlalchemy.pool import StaticPool

            engine_kwargs.update(
                {
                    "poolclass": StaticPool,
                    "connect_args": {"check_same_thread": False},
                }
            )
            logger.info(f"Using SQLite database at: {settings.sqlite_database_path}")
        else:
            # PostgreSQL configuration
            engine_kwargs.update(
                {
                    "pool_pre_ping": True,
                }
            )
            logger.info("Using PostgreSQL database")

        _engine = create_async_engine(
            settings.database_url,
            **engine_kwargs,
        )
    return _engine


def get_async_session_maker():
    """Get or create async session maker."""
    global _async_session_maker
    if _async_session_maker is None:
        _async_session_maker = async_sessionmaker(
            get_async_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _async_session_maker


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async session for dependency injection."""
    async_session_maker = get_async_session_maker()
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables.

    For desktop mode (SQLite), creates tables directly.
    For web mode (PostgreSQL), tables should typically be created via migrations,
    but this will also create them if they don't exist.
    """
    settings = get_settings()
    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    if settings.is_desktop_mode:
        logger.info(f"SQLite database initialized at: {settings.sqlite_database_path}")
    else:
        logger.info("PostgreSQL database connection established")


async def close_db() -> None:
    """Close database connections."""
    global _engine, _async_session_maker
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _async_session_maker = None
