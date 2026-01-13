"""
User Routes for Midnight Genesis

Protected endpoints that require JWT authentication.
Created by @fastapi-jwt-guardian (T036)
Enhanced with profile endpoints (T116-T120)
"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from sqlmodel import Session, select, func
from typing import Dict
from datetime import datetime
from pathlib import Path
import os
import uuid
from backend.auth import get_current_user
from backend.database import get_session
from backend.models import User, Task, TaskStatus

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/me")
async def get_current_user_profile(
    current_user: Dict[str, int] = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Get current user profile information (T116).

    Protected endpoint - requires valid JWT in Authorization header.
    Returns full user profile including email, display_name, profile_image_url, created_at.

    Returns:
        dict: Complete user profile data

    Example Response:
        {
            "id": 123,
            "email": "user@example.com",
            "display_name": "John Doe",
            "profile_image_url": null,
            "created_at": "2026-01-05T10:30:00Z"
        }
    """
    user_id = current_user["user_id"]

    # Fetch user from database
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name,
        "profile_image_url": user.profile_image_url,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


@router.get("/me/stats")
async def get_user_statistics(
    current_user: Dict[str, int] = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Get current user's task statistics (T117).

    Protected endpoint - requires valid JWT in Authorization header.
    Returns count of total tasks and completed tasks for the current user.

    Returns:
        dict: Task statistics

    Example Response:
        {
            "total_tasks": 15,
            "completed_tasks": 8
        }
    """
    user_id = current_user["user_id"]

    # Count total tasks
    total_statement = select(func.count(Task.id)).where(Task.user_id == user_id)
    total_tasks = session.exec(total_statement).one()

    # Count completed tasks
    completed_statement = select(func.count(Task.id)).where(
        Task.user_id == user_id,
        Task.status == TaskStatus.completed
    )
    completed_tasks = session.exec(completed_statement).one()

    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
    }


@router.post("/me/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: Dict[str, int] = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Upload user profile avatar image (T118, T119).

    Protected endpoint - requires valid JWT in Authorization header.
    Accepts JPG/PNG images up to 2MB.
    Saves image to backend/uploads/avatars/ directory.
    Updates user.profile_image_url in database.

    Args:
        file: Uploaded image file (multipart/form-data)

    Returns:
        dict: Updated profile image URL

    Example Response:
        {
            "profile_image_url": "/uploads/avatars/123_1704454800.jpg"
        }
    """
    user_id = current_user["user_id"]

    # Validate file type (T119)
    allowed_types = ["image/jpeg", "image/jpg", "image/png"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPG and PNG images are allowed"
        )

    # Validate file size (T119)
    MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB in bytes
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image must be under 2MB"
        )

    # Reset file pointer for saving
    await file.seek(0)

    # Sanitize filename and create unique filename (T119)
    file_extension = Path(file.filename or "image.jpg").suffix.lower()
    if file_extension not in [".jpg", ".jpeg", ".png"]:
        file_extension = ".jpg"

    timestamp = int(datetime.utcnow().timestamp())
    safe_filename = f"{user_id}_{timestamp}{file_extension}"

    # Create uploads directory if it doesn't exist
    uploads_dir = Path("backend/uploads/avatars")
    uploads_dir.mkdir(parents=True, exist_ok=True)

    # Save file
    file_path = uploads_dir / safe_filename
    with open(file_path, "wb") as f:
        f.write(content)

    # Update user profile_image_url in database
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Store URL path relative to backend root
    image_url = f"/uploads/avatars/{safe_filename}"
    user.profile_image_url = image_url
    user.updated_at = datetime.utcnow()

    session.add(user)
    session.commit()
    session.refresh(user)

    return {
        "profile_image_url": image_url
    }
