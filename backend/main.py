"""
FastAPI application entry point for Midnight Genesis.

Sprint 2 - Task: T075, T120
Owner: @fastapi-jwt-guardian

Configured with:
- CORS middleware for frontend communication
- Database initialization on startup
- Task and User model registration
- Authentication and task routers
- Static file serving for uploaded avatars (T120)

CRITICAL: Models are registered via database.init_db() which imports them.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path
from dotenv import load_dotenv
from routers import users, auth, tasks
from database import init_db

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Midnight Genesis API",
    description="Premium Full-Stack Todo Platform with Multi-Tenant Security - Backend API",
    version="0.2.0",  # Sprint 2
)


@app.on_event("startup")
async def startup_event():
    """
    Initialize database tables on application startup.

    This will:
    1. Import User and Task models from backend/models/
    2. Create tables if they don't exist
    3. Verify foreign key constraint between Task.user_id and User.id
    """
    init_db()

# Configure CORS middleware
# Allows frontend (Next.js on localhost:3000 or 3001) to communicate with backend
CORS_ORIGINS = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001").split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,  # Frontend URL(s)
    allow_credentials=True,  # Allow cookies and Authorization headers
    allow_methods=["*"],  # All HTTP methods
    allow_headers=["*"],  # All headers
)

# Register routers
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(tasks.router)  # Sprint 2: Task CRUD endpoints

# Mount static files directory for avatar uploads (T120)
# Create uploads directory if it doesn't exist
uploads_dir = Path("backend/uploads")
uploads_dir.mkdir(parents=True, exist_ok=True)

app.mount("/uploads", StaticFiles(directory="backend/uploads"), name="uploads")


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the API is running.

    Returns:
        dict: Status message indicating API health
    """
    return {"status": "ok", "message": "Midnight Genesis API is running"}


@app.get("/")
async def root():
    """
    Root endpoint providing API information.

    Returns:
        dict: API metadata
    """
    return {
        "name": "Midnight Genesis API",
        "version": "0.1.0",
        "status": "operational",
    }
