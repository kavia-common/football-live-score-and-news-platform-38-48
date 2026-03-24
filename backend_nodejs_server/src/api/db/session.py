from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.api.core.config import settings


def _build_mysql_dsn() -> Optional[str]:
    """
    Build a SQLAlchemy MySQL DSN from either MYSQL_URL or discrete MYSQL_* variables.

    Supports:
    - MYSQL_URL like: mysql://host:port/db  (no user/pass)
    - MYSQL_USER/MYSQL_PASSWORD/MYSQL_URL (where MYSQL_URL can be host:port/db too)
    """
    if settings.mysql_url:
        # Accept both mysql://host:port/db and host:port/db
        url = settings.mysql_url.strip()
        if url.startswith("mysql://") or url.startswith("mysql+pymysql://"):
            # If it already includes a driver prefix, use it as-is (but ensure pymysql driver)
            if url.startswith("mysql://"):
                url = url.replace("mysql://", "mysql+pymysql://", 1)
            return url

        # If it's a naked host[:port]/db, convert to mysql+pymysql://host[:port]/db
        url = url.lstrip("/")
        return f"mysql+pymysql://{url}"

    # Fall back to discrete env vars (preferred in many container setups)
    if not (settings.mysql_user and settings.mysql_password and settings.mysql_db):
        return None

    host = os.getenv("MYSQL_HOST", "localhost")
    port = settings.mysql_port or "3306"
    return f"mysql+pymysql://{settings.mysql_user}:{settings.mysql_password}@{host}:{port}/{settings.mysql_db}"


DATABASE_DSN = _build_mysql_dsn()

if not DATABASE_DSN:
    # DB is optional for health-check; actual routes will error with a clear message if missing.
    engine = None
    SessionLocal = None
else:
    engine = create_engine(
        DATABASE_DSN,
        pool_pre_ping=True,
        pool_recycle=3600,
        future=True,
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)


# PUBLIC_INTERFACE
def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a SQLAlchemy session."""
    if SessionLocal is None:
        raise RuntimeError(
            "Database is not configured. Please set MYSQL_URL or MYSQL_USER/MYSQL_PASSWORD/MYSQL_DB."
        )
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def db_session() -> Generator[Session, None, None]:
    """Context manager for non-request DB use (background tasks)."""
    if SessionLocal is None:
        raise RuntimeError(
            "Database is not configured. Please set MYSQL_URL or MYSQL_USER/MYSQL_PASSWORD/MYSQL_DB."
        )
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
