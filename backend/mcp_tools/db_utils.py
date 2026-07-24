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

_mcp_engine = None

def get_mcp_engine():
    """Lazy engine creation to prevent import-time database failures."""
    global _mcp_engine
    if _mcp_engine is None:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError(
                "DATABASE_URL environment variable not set. "
                "Please configure Neon PostgreSQL connection in backend/.env"
            )
        _mcp_engine = create_engine(
            database_url,
            echo=False,  # Disable SQL logging for MCP tools
            pool_pre_ping=True,  # Test connections before use
            pool_recycle=300,  # Recycle every 5 minutes
            pool_size=5,
            max_overflow=10,
        )
    return _mcp_engine


@contextmanager
def get_mcp_session() -> Generator[Session, None, None]:
    """
    Database session factory for MCP tools.

    Yields a SQLModel Session that automatically commits on success
    and rolls back on exceptions.
    """
    engine = get_mcp_engine()
    with Session(engine) as session:
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
