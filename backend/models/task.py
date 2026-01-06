"""
Task Model - SQLModel table definition with TaskStatus enum

CRITICAL - ZERO-TRUST MULTI-TENANCY:
ALL queries against Task MUST filter by user_id from JWT.
NO client-supplied user_id values are EVER trusted.

Owner: @database-expert
Tasks: T073 (TaskStatus enum), T074 (Task model)
"""

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """
    Task status enumeration.

    Values:
    - pending: Task not yet completed (default state)
    - completed: Task marked as done (one-way transition from pending)

    Note: Status transition is ONE-WAY ONLY (pending → completed).
    Reverting completed tasks to pending is not allowed per spec.
    """

    pending = "pending"
    completed = "completed"


class Task(SQLModel, table=True):
    """
    Task model representing a todo item.

    CRITICAL - TENANT ISOLATION RULE (Constitution Principle III):
    ============================================================
    ALL queries against this model MUST filter by user_id to enforce
    data isolation between users. The user_id MUST be extracted from
    the JWT token via get_current_user dependency, NEVER from client input.

    ❌ FORBIDDEN (Data Leakage):
        session.exec(select(Task)).all()  # Returns ALL users' tasks!

    ✅ REQUIRED (Secure):
        session.exec(select(Task).where(Task.user_id == current_user.id)).all()

    Fields:
    - id: Primary key (int, auto-increment)
    - user_id: Foreign key to users.id (indexed, non-nullable)
    - title: Task title (non-empty, max 500 chars)
    - description: Optional task description (max 5000 chars)
    - status: TaskStatus enum (default: pending)
    - created_at: Creation timestamp (UTC, server-generated)
    - updated_at: Last modification timestamp (UTC, auto-update)

    Foreign Keys:
    - user_id references users.id (enforces referential integrity)

    Indexes:
    - user_id (for fast filtered queries)
    - created_at (for chronological ordering)

    Constraints:
    - Status transition: pending → completed (one-way only)
    - Title: non-empty, max 500 characters
    - Description: nullable, max 5000 characters
    """

    __tablename__ = "tasks"

    # Primary key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign key to User (CRITICAL: MUST be included in ALL query filters)
    user_id: int = Field(foreign_key="users.id", index=True, nullable=False)

    # Task data
    title: str = Field(min_length=1, max_length=500)  # Non-empty constraint
    description: Optional[str] = Field(default=None, max_length=5000)

    # Task status (default: pending)
    status: TaskStatus = Field(default=TaskStatus.pending)

    # Timestamps (UTC, server-generated)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
