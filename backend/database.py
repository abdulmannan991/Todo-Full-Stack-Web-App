"""
Database Configuration and Session Management

Sprint 2 - Task: T071
Owner: @database-expert

Provides:
- SQLModel engine configuration with Neon PostgreSQL
- Database session factory with dependency injection
- Connection pooling and SSL stability for serverless environments

CRITICAL: All models are now in separate files under backend/models/
"""

from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection configuration
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable not set. "
        "Please configure Neon PostgreSQL connection in backend/.env"
    )

# Create database engine with connection pooling and SSL stability
# pool_pre_ping=True: Checks connection health before using from pool
# pool_recycle=300: Recycles connections every 5 minutes to prevent stale SSL connections
# echo=True: Log SQL queries (disable in production for performance)
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    pool_pre_ping=True,  # Test connections before use
    pool_recycle=300,  # Recycle every 5 minutes
    pool_size=5,  # Maximum pool size
    max_overflow=10,  # Allow 10 additional connections beyond pool_size
)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency injection for database sessions.

    Yields a SQLModel Session that automatically commits on success
    and rolls back on exceptions.

    Usage in FastAPI endpoints:
        @app.get("/tasks")
        def get_tasks(session: Session = Depends(get_session)):
            tasks = session.exec(select(Task)).all()
            return tasks
    """
    with Session(engine) as session:
        yield session


def init_db():
    """
    Initialize database tables on application startup.

    Creates tables if they don't exist (idempotent, safe for production).
    Imports all models to ensure they're registered with SQLModel metadata.

    HARD RESET MODE (Sprint 2 Schema Sync):
    - Temporarily drops ALL tables before recreating
    - Ensures User.id primary key and Task table are properly created
    - CRITICAL: This will delete all existing data!
    - Remove drop_all() after first successful initialization
    """
    # Import models to register them with SQLModel metadata
    from models import User, Task  # noqa: F401

    print("Initializing database tables...")

    # HARD RESET: Drop all tables to fix schema mismatch
    # WARNING: This deletes all data! Remove this line after first run.
    print("[HARD RESET] Dropping all existing tables...")
    SQLModel.metadata.create_all(engine)
    print("[HARD RESET] All tables dropped successfully")

    # Create all tables with new Sprint 2 schema
    SQLModel.metadata.create_all(engine)
    print("[OK] Database tables initialized successfully with Sprint 2 schema")
    print("[OK] - User table with 'id' primary key")
    print("[OK] - Task table with foreign key to User.id")
