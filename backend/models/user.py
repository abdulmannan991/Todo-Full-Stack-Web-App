"""
User Model - SQLModel table definition

Per Constitution Principle III: All user data access MUST be scoped to the authenticated user.

Owner: @database-expert
Task: T072 - Create User model in backend/models/user.py
"""

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class User(SQLModel, table=True):
    """
    User model representing an authenticated account.

    Fields:
    - id: Primary key (int, auto-increment)
    - email: Unique email address (indexed for fast lookups)
    - password_hash: Hashed password for email/password authentication
    - display_name: Optional custom display name (nullable)
    - profile_image_url: Optional profile avatar URL (nullable)
    - created_at: Account creation timestamp (UTC)
    - updated_at: Last modification timestamp (UTC)

    Notes:
    - Better Auth handles authentication on the frontend
    - Backend references user_id for task ownership and data isolation
    - Foreign key relationships enforce multi-tenant data isolation
    """

    __tablename__ = "users"

    # Primary key
    id: Optional[int] = Field(default=None, primary_key=True)

    # User identity
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)

    # Optional profile data
    display_name: Optional[str] = Field(default=None, max_length=100)
    profile_image_url: Optional[str] = Field(default=None, max_length=500)

    # Timestamps (UTC, server-generated)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
