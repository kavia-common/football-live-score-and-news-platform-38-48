from sqlalchemy import text

from src.api.db.models import Base
from src.api.db.session import engine


# PUBLIC_INTERFACE
def init_db() -> None:
    """Initialize database tables if configured. No-op if DB is not configured."""
    if engine is None:
        return
    Base.metadata.create_all(bind=engine)


# PUBLIC_INTERFACE
def db_ping() -> bool:
    """Return True if the database is reachable."""
    if engine is None:
        return False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
