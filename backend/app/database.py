"""
SQLAlchemy database setup for NiyamDrishti.

Uses PostgreSQL for the MVP database.
All tables are created automatically on startup via create_tables().

CONNECTION CONFIGURATION:
  Set the DATABASE_URL environment variable to override the default:
    export DATABASE_URL="postgresql://user:password@host:port/dbname"

  For local development (Postgres.app, no password):
    export DATABASE_URL="postgresql://udbhav@localhost:5432/niyamdrishti"

  If DATABASE_URL is not set, it defaults to the local dev connection above.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Read from environment variable, fall back to local dev default.
# NOTE: No password is hard-coded. For production or shared environments,
#       set DATABASE_URL with your actual credentials:
#         export DATABASE_URL="postgresql://user:password@host:port/niyamdrishti"
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "sqlite:///./niyamdrishti.db",
)

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


def get_db():
    """
    FastAPI dependency that provides a database session.

    Usage in route:
        def my_endpoint(db: Session = Depends(get_db)):
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables. Safe to call multiple times (won't drop existing data)."""
    Base.metadata.create_all(bind=engine)
    # Safe migration: ensure is_ecommerce column exists on existing installations
    from sqlalchemy import text
    with engine.begin() as conn:
        try:
            conn.execute(text("ALTER TABLE inspections ADD COLUMN is_ecommerce BOOLEAN DEFAULT FALSE;"))
        except Exception:
            pass
