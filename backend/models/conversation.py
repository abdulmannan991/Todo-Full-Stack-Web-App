"""
Conversation Model - SQLModel table definition for chat sessions

Per Constitution Principle III: All user data access MUST be scoped to the authenticated user.

Owner: @database-expert
Task: T309 - Create Conversation SQLModel in backend/models/conversation.py
"""

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class Conversation(SQLModel, table=True):
    """
    Conversation model representing a chat session between a user and the AI assistant.

    Fields:
    - id: Primary key (int, auto-increment)
    - user_id: Foreign key to user.id (indexed for user isolation)
    - version: Optimistic locking version number (incremented on each update)
    - created_at: Conversation creation timestamp (UTC)
    - updated_at: Last modification timestamp (UTC)

    Notes:
    - Optimistic locking prevents race conditions on concurrent requests
    - All queries MUST filter by user_id for data isolation
    - Version incremented on every conversation update
    - Conversations retained indefinitely (no deletion in scope)
    """

    __tablename__ = "conversation"

    # Primary key
    id: Optional[int] = Field(default=None, primary_key=True)

    # User ownership (enforces multi-tenant isolation)
    user_id: int = Field(foreign_key="users.id", index=True)

    # Optimistic locking version
    version: int = Field(default=1, ge=1)

    # Timestamps (UTC, server-generated)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
