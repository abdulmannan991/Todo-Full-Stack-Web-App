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
    """
    # Import models to register them with SQLModel metadata
    from backend.models import User, Task  # noqa: F401
    from backend.models.conversation import Conversation  # noqa: F401
    from backend.models.message import Message  # noqa: F401

    print("Initializing database tables...")

    # Create all tables if they don't exist (idempotent operation)
    SQLModel.metadata.create_all(engine)
    print("[OK] Database tables initialized successfully")
    print("[OK] - User, Task, Conversation, Message tables ready")
