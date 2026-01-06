"""
JWT Authentication Middleware for Midnight Genesis

Implements JWT validation using jose library with BETTER_AUTH_SECRET.
Enforces Constitution Principle II: Zero Trust Security Model.

Owner: @fastapi-jwt-guardian
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import os
from dotenv import load_dotenv
from typing import Dict

# Load environment variables
load_dotenv()

# Security scheme setup
security = HTTPBearer()

# Load BETTER_AUTH_SECRET from environment
# CRITICAL: This MUST match the secret in frontend/.env.local
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")

if not BETTER_AUTH_SECRET:
    raise ValueError(
        "BETTER_AUTH_SECRET not set in environment variables. "
        "Please add it to backend/.env and ensure it matches frontend/.env.local"
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, int]:
    """
    JWT validation dependency for protected routes.

    Validates JWT token from Authorization header and extracts user_id.

    Args:
        credentials: HTTPAuthorizationCredentials from request header

    Returns:
        Dict containing user_id extracted from JWT token

    Raises:
        HTTPException 401: If token is missing, invalid, or expired
        HTTPException 401: If user_id (sub claim) is missing from token

    Usage:
        @router.get("/protected")
        async def protected_route(current_user: dict = Depends(get_current_user)):
            user_id = current_user["user_id"]
            # ... use user_id for data isolation
    """
    token = credentials.credentials

    try:
        # Decode and validate JWT token
        # Better Auth uses HS256 algorithm by default
        payload = jwt.decode(
            token,
            BETTER_AUTH_SECRET,
            algorithms=["HS256"],
        )

        # Extract user_id from 'sub' claim (subject)
        # Better Auth stores user ID in the 'sub' claim
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Return user_id as integer
        # CRITICAL: This is the ONLY source of user_id for data isolation
        # Never accept user_id from client input
        return {"user_id": int(user_id)}

    except JWTError as e:
        # Token validation failed (invalid signature, expired, malformed, etc.)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ValueError:
        # user_id is not a valid integer
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: user ID must be an integer",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
) -> Dict[str, int] | None:
    """
    Optional JWT validation dependency for routes that work with or without auth.

    Returns user data if token is valid, None if token is missing or invalid.

    Returns:
        Dict containing user_id if authenticated, None otherwise
    """
    if credentials is None:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
