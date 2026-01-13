"""
Task CRUD Endpoints with Multi-Tenant Security

Sprint 2 - Phase 9: User Story 2 (Task Creation and Reading)
Owner: @fastapi-jwt-guardian
Tasks: T080 (POST), T081 (GET), T082 (Security), T083 (Error Handling)
       T096 (PATCH), T097 (Status Validation)
       T109 (DELETE), T110 (Security)

CRITICAL - ZERO-TRUST MULTI-TENANCY:
ALL endpoints inject current_user from JWT and filter by user_id.
NO client-supplied user_id values are ever trusted.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from backend.database import get_session
from backend.auth import get_current_user
from backend.models import Task, TaskStatus
from backend.schemas.task import TaskCreateRequest, TaskUpdateRequest, TaskResponse
from datetime import datetime

router = APIRouter(prefix="/tasks", tags=["tasks"])


# ============================================================================
# POST /tasks - Create Task (T080)
# ============================================================================


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreateRequest,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """
    Create a new task for the authenticated user.

    **Security**: user_id is injected from JWT (get_current_user dependency).
    Client-supplied user_id values are IGNORED and REJECTED.

    **Request Body**:
    - title (required): Task title (non-empty, max 500 chars)
    - description (optional): Task description (max 5000 chars)

    **Response**: TaskResponse with created task data

    **Status Codes**:
    - 201 Created: Task created successfully
    - 400 Bad Request: Invalid input (empty title, oversized description)
    - 401 Unauthorized: Missing or invalid JWT
    - 500 Internal Server Error: Database error
    """
    try:
        # Extract user_id from JWT (NEVER from request body)
        user_id = current_user["user_id"]

        # Create new task with user_id from JWT
        new_task = Task(
            user_id=user_id,  # CRITICAL: Derived from JWT, not client input
            title=task_data.title,
            description=task_data.description,
            status=TaskStatus.pending,  # Default status
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        session.add(new_task)
        session.commit()
        session.refresh(new_task)

        return new_task

    except Exception as e:
        session.rollback()
        # Log error for debugging (in production, use proper logging)
        print(f"[ERROR] Task creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create task. Please try again.",
        )


# ============================================================================
# GET /tasks - List User's Tasks (T081)
# ============================================================================


@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """
    Retrieve all tasks for the authenticated user.

    **Security**: ONLY returns tasks where task.user_id == current_user.id.
    Multi-tenant isolation enforced via WHERE clause.

    **Response**: List of TaskResponse (sorted by created_at DESC)

    **Status Codes**:
    - 200 OK: Tasks retrieved successfully (empty list if no tasks)
    - 401 Unauthorized: Missing or invalid JWT
    - 500 Internal Server Error: Database error
    """
    try:
        # Extract user_id from JWT
        user_id = current_user["user_id"]

        # CRITICAL: Filter by user_id (Constitution Principle III)
        # This query MUST NOT return tasks from other users
        statement = (
            select(Task)
            .where(Task.user_id == user_id)  # Multi-tenant isolation
            .order_by(Task.created_at.desc())  # Newest first
        )

        tasks = session.exec(statement).all()

        return tasks

    except Exception as e:
        # Log error for debugging
        print(f"[ERROR] Task retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve tasks. Please try again.",
        )


# ============================================================================
# PATCH /tasks/{id} - Update Task (T096, T097, T103)
# ============================================================================


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdateRequest,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """
    Update an existing task (status and/or title).

    **Security**:
    - Task MUST belong to the authenticated user (task.user_id == current_user.id)
    - Returns 404 if task not found OR unauthorized (prevents data leakage)

    **Status Transition Rule**:
    - pending → completed: ALLOWED (one-way transition)
    - completed → pending: FORBIDDEN (returns 400 Bad Request)

    **Request Body** (all fields optional):
    - status: New task status (pending or completed)
    - title: New task title (non-empty, max 500 chars)

    **Response**: TaskResponse with updated task data

    **Status Codes**:
    - 200 OK: Task updated successfully
    - 400 Bad Request: Invalid status transition (completed → pending)
    - 404 Not Found: Task not found or unauthorized access
    - 401 Unauthorized: Missing or invalid JWT
    """
    try:
        # Extract user_id from JWT
        user_id = current_user["user_id"]

        # Fetch task with ownership verification
        # CRITICAL: Filter by BOTH task_id AND user_id
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        task = session.exec(statement).first()

        if not task:
            # Return 404 for both "not found" and "unauthorized"
            # This prevents leaking information about task existence
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        # Update status if provided
        if task_data.status is not None:
            # Enforce one-way status transition (T097)
            if task.status == TaskStatus.completed and task_data.status == TaskStatus.pending:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot revert completed tasks to pending",
                )
            task.status = task_data.status

        # Update title if provided (T103)
        if task_data.title is not None:
            task.title = task_data.title

        # Update timestamp
        task.updated_at = datetime.utcnow()

        session.add(task)
        session.commit()
        session.refresh(task)

        return task

    except HTTPException:
        # Re-raise HTTP exceptions (404, 400)
        raise
    except Exception as e:
        session.rollback()
        print(f"[ERROR] Task update failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update task. Please try again.",
        )


# ============================================================================
# DELETE /tasks/{id} - Delete Task (T109, T110)
# ============================================================================


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """
    Permanently delete a task.

    **Security**:
    - Task MUST belong to the authenticated user (task.user_id == current_user.id)
    - Returns 404 if task not found OR unauthorized (prevents data leakage)
    - Deletion attempts are logged for audit purposes

    **Response**: 204 No Content (empty body)

    **Status Codes**:
    - 204 No Content: Task deleted successfully
    - 404 Not Found: Task not found or unauthorized access
    - 401 Unauthorized: Missing or invalid JWT
    """
    try:
        # Extract user_id from JWT
        user_id = current_user["user_id"]

        # Fetch task with ownership verification
        # CRITICAL: Filter by BOTH task_id AND user_id
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        task = session.exec(statement).first()

        if not task:
            # Log deletion attempt for audit (T110)
            print(f"[AUDIT] User {user_id} attempted to delete non-existent/unauthorized task {task_id}")

            # Return 404 for both "not found" and "unauthorized"
            # This prevents leaking information about task existence
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        # Delete task
        session.delete(task)
        session.commit()

        # Log successful deletion for audit
        print(f"[AUDIT] User {user_id} deleted task {task_id}")

        # Return 204 No Content (no response body)
        return None

    except HTTPException:
        # Re-raise HTTP exceptions (404)
        raise
    except Exception as e:
        session.rollback()
        print(f"[ERROR] Task deletion failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete task. Please try again.",
        )
