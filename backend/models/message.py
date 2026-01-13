"""
Message Model - SQLModel table definition for chat messages

Per Constitution Principle III: All user data access MUST be scoped to the authenticated user.

Owner: @database-expert
Task: T310 - Create Message SQLModel in backend/models/message.py
"""

from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON, Text, String, CheckConstraint
from typing import Optional
from datetime import datetime


class Message(SQLModel, table=True):
    """
    Message model representing a single message in a conversation (user or assistant).

    Fields:
    - id: Primary key (int, auto-increment)
    - conversation_id: Foreign key to conversation.id (indexed)
    - user_id: Foreign key to user.id (denormalized for query efficiency, indexed)
    - role: Message sender role ('user' or 'assistant')
    - content: Message text content
    - tool_calls: Tool invocations made by assistant (JSON, nullable)
    - created_at: Message creation timestamp (UTC)

    Notes:
    - user_id denormalized for fast user isolation filtering without joins
    - Messages are immutable (append-only log)
    - tool_calls stored for transparency and debugging
    - All queries MUST filter by user_id for data isolation
    """

    __tablename__ = "message"
    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant')", name='check_message_role'),
    )

    # Primary key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Relationships
    conversation_id: int = Field(foreign_key="conversation.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)

    # Message data
    role: str = Field(sa_column=Column(String(20), nullable=False))
    content: str = Field(sa_column=Column(Text, nullable=False))
    tool_calls: Optional[list[dict]] = Field(default=None, sa_column=Column(JSON))

    # Timestamp (UTC, server-generated)
    created_at: datetime = Field(default_factory=datetime.utcnow)
