"""
Task Pydantic Schemas - Request/Response Models

Sprint 2 - Tasks: T078 (TaskCreateRequest), T079 (TaskResponse), T095 (TaskUpdateRequest)
Owner: @fastapi-jwt-guardian

These schemas define the shape of data for task API endpoints.

SECURITY NOTE:
- TaskCreateRequest does NOT include user_id (derived from JWT)
- TaskResponse does NOT expose user_id (privacy protection)
- TaskUpdateRequest allows partial updates (status and/or title)
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from typing import Optional
from backend.models.task import TaskStatus


class TaskCreateRequest(BaseModel):
    """
    Request schema for creating a new task.

    Fields:
    - title: Task title (required, non-empty, max 500 chars)
    - description: Task description (optional, max 5000 chars)

    SECURITY: user_id is NOT included in request.
    It is injected from JWT via get_current_user dependency.
    """

    title: str = Field(..., min_length=1, max_length=500, description="Task title")
    description: Optional[str] = Field(
        None, max_length=5000, description="Optional task description"
    )

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v):
        """Ensure title is not just whitespace."""
        if not v or not v.strip():
            raise ValueError("Title cannot be empty or whitespace")
        return v.strip()


class TaskUpdateRequest(BaseModel):
    """
    Request schema for updating an existing task.

    Fields:
    - status: Optional task status (pending or completed)
    - title: Optional new title (non-empty, max 500 chars)

    Notes:
    - Both fields are optional (partial updates allowed)
    - Status transition: pending → completed (one-way only, enforced in endpoint)
    - Empty title is rejected in endpoint validation
    """

    status: Optional[TaskStatus] = Field(None, description="New task status")
    title: Optional[str] = Field(
        None, min_length=1, max_length=500, description="New task title"
    )

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v):
        """Ensure title is not just whitespace if provided."""
        if v is not None and (not v or not v.strip()):
            raise ValueError("Title cannot be empty or whitespace")
        return v.strip() if v else None


class TaskResponse(BaseModel):
    """
    Response schema for task data.

    Fields:
    - id: Task ID (primary key)
    - title: Task title
    - description: Task description (nullable)
    - status: Task status (pending or completed)
    - created_at: Creation timestamp (UTC)
    - updated_at: Last modification timestamp (UTC)

    SECURITY: user_id is NOT exposed in responses.
    This prevents information leakage and maintains privacy.
    """

    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        # This force-serializes datetimes to include the 'Z' (Zulu/UTC) suffix
        json_encoders={
            datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%SZ") if v.tzinfo is None else v.isoformat()
        }
    )

