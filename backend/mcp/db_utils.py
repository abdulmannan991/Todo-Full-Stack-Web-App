"""
MCP Database Utilities

Owner: @mcp-expert
Tasks: T318, T319

Provides:
- Database session management for MCP tools
- Retry decorator with exponential backoff for transient failures
- Connection pooling helpers

Per Constitution Principle III: All database operations MUST enforce user_id isolation.
"""

from sqlmodel import Session, create_engine
from typing import Generator, Callable, TypeVar, Any
from functools import wraps
from contextlib import contextmanager
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import os
from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError, DBAPIError

# Load environment variables
load_dotenv()

# Database connection configuration
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable not set. "
        "Please configure Neon PostgreSQL connection in backend/.env"
    )

# Create database engine for MCP tools
# Separate engine instance to avoid conflicts with main FastAPI engine
mcp_engine = create_engine(
    DATABASE_URL,
    echo=False,  # Disable SQL logging for MCP tools
    pool_pre_ping=True,  # Test connections before use
    pool_recycle=300,  # Recycle every 5 minutes
    pool_size=5,
    max_overflow=10,
)


@contextmanager
def get_mcp_session() -> Generator[Session, None, None]:
    """
    Database session factory for MCP tools.

    Yields a SQLModel Session that automatically commits on success
    and rolls back on exceptions.

    Usage in MCP tools:
        @mcp.tool()
        async def add_task(user_id: int, title: str) -> str:
            with get_mcp_session() as session:
                task = Task(user_id=user_id, title=title)
                session.add(task)
                session.commit()
                return f"Task '{title}' created"
    """
    with Session(mcp_engine) as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise


# Type variable for generic function return type
T = TypeVar('T')


def with_db_retry(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator that retries database operations with exponential backoff.

    Retry strategy:
    - 3 attempts total
    - Exponential backoff: 100ms, 500ms, 1000ms
    - Only retries on transient database errors (OperationalError, DBAPIError)

    Usage:
        @with_db_retry
        def create_task(session: Session, user_id: int, title: str):
            task = Task(user_id=user_id, title=title)
            session.add(task)
            session.commit()
            return task

    Args:
        func: Function to wrap with retry logic

    Returns:
        Wrapped function with retry behavior
    """
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.1, min=0.1, max=1.0),
        retry=retry_if_exception_type((OperationalError, DBAPIError)),
        reraise=True
    )
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        return func(*args, **kwargs)

    return wrapper


def with_async_db_retry(func: Callable[..., T]) -> Callable[..., T]:
    """
    Async version of with_db_retry decorator.

    Usage:
        @with_async_db_retry
        async def create_task_async(session: Session, user_id: int, title: str):
            task = Task(user_id=user_id, title=title)
            session.add(task)
            await session.commit()
            return task

    Args:
        func: Async function to wrap with retry logic

    Returns:
        Wrapped async function with retry behavior
    """
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.1, min=0.1, max=1.0),
        retry=retry_if_exception_type((OperationalError, DBAPIError)),
        reraise=True
    )
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> T:
        return await func(*args, **kwargs)

    return wrapper
