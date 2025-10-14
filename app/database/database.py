"""
Database connection and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
import os
from pathlib import Path

from .models import Base

# Database file location
DB_DIR = Path(__file__).parent.parent.parent / "data"
DB_DIR.mkdir(exist_ok=True)
DATABASE_URL = f"sqlite:///{DB_DIR}/oil_fields.db"

# Create engine
# Using StaticPool for SQLite to handle threading issues
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False  # Set to True for SQL query logging
)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """
    Initialize database - create all tables
    """
    Base.metadata.create_all(bind=engine)
    print(f"Database initialized at: {DATABASE_URL}")


def drop_db():
    """
    Drop all tables (use with caution!)
    """
    Base.metadata.drop_all(bind=engine)
    print("All tables dropped")


def get_db() -> Session:
    """
    Dependency for FastAPI to get database session

    Usage in FastAPI:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(OilField).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_session():
    """
    Context manager for database sessions

    Usage:
        with get_db_session() as db:
            field = db.query(OilField).filter_by(field_id="EKOFISK").first()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def reset_db():
    """
    Drop and recreate all tables (for development/testing)
    """
    drop_db()
    init_db()
