from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
import os

from .models import Base

# Database URL - can be overridden via environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./barbershop.db")

# Create engine with SQLite-specific settings
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    echo=False,  # Set to True for SQL query logging during development
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """
    Initialize the database by creating all tables.
    This should be called once when setting up the application.
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")


def drop_all_tables():
    """
    Drop all tables. USE WITH CAUTION - only for development/testing.
    """
    Base.metadata.drop_all(bind=engine)
    print("⚠️  All database tables dropped!")


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get a database session.

    Usage:
        with get_db() as db:
            user = db.query(User).filter(User.phone_number == phone).first()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session() -> Session:
    """
    Get a database session (for use in FastAPI dependencies).

    Usage in FastAPI:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db_session)):
            return db.query(User).all()
    """
    return SessionLocal()
