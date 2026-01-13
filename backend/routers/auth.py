"""
Authentication endpoints for signup and login.

Handles password hashing, user creation, and JWT token generation.
Owner: @fastapi-jwt-guardian
"""

from fastapi import APIRouter, HTTPException, Depends, Response
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import os
from backend.database import engine, get_session
from backend.models import User

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Request/Response Models
class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    user: dict
    token: str


# Database session dependency
def get_session():
    with Session(engine) as session:
        yield session


# Helper functions
def hash_password(password: str) -> str:
    """Hash a password using bcrypt (truncates to 72 bytes as per bcrypt spec)."""
    # Bcrypt has a 72-byte limit - manually truncate
    password_bytes = password.encode('utf-8')[:72]
    truncated_password = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.hash(truncated_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash (truncates to 72 bytes as per bcrypt spec)."""
    # Bcrypt has a 72-byte limit - manually truncate
    password_bytes = plain_password.encode('utf-8')[:72]
    truncated_password = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.verify(truncated_password, hashed_password)


def create_access_token(user_id: int) -> str:
    """Create a JWT access token."""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
    }
    encoded_jwt = jwt.encode(to_encode, BETTER_AUTH_SECRET, algorithm=ALGORITHM)
    return encoded_jwt


# Authentication Endpoints
@router.post("/sign-up/email", response_model=AuthResponse)
async def signup(request: SignupRequest, response: Response, session: Session = Depends(get_session)):
    """
    Create a new user account with email and password.

    Returns:
        AuthResponse: User data and JWT token

    Raises:
        HTTPException: 400 if email already exists
    """
    try:
        print(f"[DEBUG] Signup request: {request.email}", flush=True)

        # Check if user already exists
        existing_user = session.exec(
            select(User).where(User.email == request.email)
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

        # Create new user
        print(f"[DEBUG] Hashing password...", flush=True)
        hashed_password = hash_password(request.password)

        # Extract display name from email if not provided
        display_name = request.name if request.name else request.email.split("@")[0]

        print(f"[DEBUG] Creating user object...", flush=True)
        new_user = User(
            email=request.email,
            display_name=display_name,
            password_hash=hashed_password,  # FIXED: Use password_hash to match User model
        )

        print(f"[DEBUG] Adding to session...", flush=True)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        # Generate JWT token
        print(f"[DEBUG] Generating JWT token...", flush=True)
        token = create_access_token(new_user.id)  # FIXED: Use .id instead of .user_id

        # Set session cookie (cross-origin compatible)
        response.set_cookie(
            key="auth_token",
            value=token,
            httponly=True,
            samesite="lax",
            secure=False,  # Set to True in production with HTTPS
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

        print(f"[DEBUG] Signup successful for user {new_user.id}", flush=True)
        return AuthResponse(
            user={
                "id": new_user.id,  # FIXED: Use .id instead of .user_id
                "email": new_user.email,
                "name": new_user.display_name,
            },
            token=token,
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Signup failed: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sign-in/email", response_model=AuthResponse)
async def login(request: LoginRequest, response: Response, session: Session = Depends(get_session)):
    """
    Authenticate user with email and password.

    Returns:
        AuthResponse: User data and JWT token

    Raises:
        HTTPException: 401 if credentials are invalid
    """
    try:
        print(f"[DEBUG] Login attempt for: {request.email}", flush=True)

        # Find user by email
        user = session.exec(
            select(User).where(User.email == request.email)
        ).first()

        if not user:
            print(f"[DEBUG] User not found: {request.email}", flush=True)
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        print(f"[DEBUG] User found: {user.id}, verifying password...", flush=True)

        # Verify password
        is_valid = verify_password(request.password, user.password_hash)  # FIXED: Use password_hash
        print(f"[DEBUG] Password verification result: {is_valid}", flush=True)

        if not is_valid:
            print(f"[DEBUG] Invalid password for user: {request.email}", flush=True)
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        # Generate JWT token
        print(f"[DEBUG] Generating JWT for user {user.id}", flush=True)
        token = create_access_token(user.id)  # FIXED: Use .id instead of .user_id

        # Set session cookie (cross-origin compatible)
        response.set_cookie(
            key="auth_token",
            value=token,
            httponly=True,
            samesite="lax",
            secure=False,  # Set to True in production with HTTPS
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

        print(f"[DEBUG] Login successful for user {user.id}", flush=True)
        return AuthResponse(
            user={
                "id": user.id,  # FIXED: Use .id instead of .user_id
                "email": user.email,
                "name": user.display_name,
            },
            token=token,
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Login failed: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
