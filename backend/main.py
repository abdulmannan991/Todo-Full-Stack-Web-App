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

import os
import sys
import gc
import types
from pathlib import Path
from dotenv import load_dotenv

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

# Add parent directory to sys.path so 'from backend...' imports work cleanly
current_dir = Path(__file__).parent.resolve()
parent_dir = current_dir.parent.resolve()

if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

# Create 'backend' package alias if running directly inside backend folder / HF Space root
try:
    import backend
except ModuleNotFoundError:
    backend_pkg = types.ModuleType("backend")
    backend_pkg.__path__ = [str(current_dir)]
    sys.modules["backend"] = backend_pkg

# Load environment variables FIRST before importing backend modules
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)
load_dotenv()

from backend.routers import users, auth, tasks
from backend.api import chat
from backend.database import init_db, engine
from sqlalchemy.pool import NullPool


class SessionCleanupMiddleware(BaseHTTPMiddleware):
    """
    Middleware to ensure database sessions are properly closed after each request.

    CRITICAL: Prevents session leaks that cause "hanging" loading screens.
    This middleware runs AFTER the response is sent, ensuring cleanup happens
    even if the endpoint doesn't explicitly close the session.

    Architecture:
    - Runs after every request completes (success or failure)
    - Disposes all connections in the pool
    - Forces garbage collection to release leaked sessions
    - Prevents ROLLBACK loops from long-running agent.run() calls
    """
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        finally:
            # MANDATORY: Dispose all connections to prevent leaks
            engine.dispose()
            # Force garbage collection to release any leaked sessions
            gc.collect()


app = FastAPI(
    title="Midnight Genesis API",
    description="Premium Full-Stack Todo Platform with Multi-Tenant Security - Backend API",
    version="0.2.0",  # Sprint 2
)

# Configure CORS middleware
cors_origins_env = os.getenv("CORS_ORIGINS", "")
allowed_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]
default_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://todo-full-stack-web-app-a2xu.vercel.app",
]
for origin in default_origins:
    if origin not in allowed_origins:
        allowed_origins.append(origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def custom_cors_middleware(request: Request, call_next):
    origin = request.headers.get("origin")
    if request.method == "OPTIONS":
        response = Response(status_code=200)
    else:
        response = await call_next(request)
    if origin:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, Accept"
    return response

# Add session cleanup middleware to prevent database connection leaks
# CRITICAL: This runs AFTER every request to dispose connections
app.add_middleware(SessionCleanupMiddleware)


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

# Register routers
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(tasks.router)  # Sprint 2: Task CRUD endpoints
app.include_router(chat.router)  # Phase 3: AI Chat endpoint

# Mount static files directory for avatar uploads (T120)
# Create uploads directory if it doesn't exist
uploads_dir = Path("backend/uploads") if Path("backend/uploads").exists() or Path("backend").exists() else Path("uploads")
uploads_dir.mkdir(parents=True, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")


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
