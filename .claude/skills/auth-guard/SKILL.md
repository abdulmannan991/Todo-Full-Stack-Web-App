---
name: auth-guard
description: Validates JWT middleware and enforces 401/403 security responses on all protected endpoints
version: 1.0.0
owner: fastapi-jwt-guardian
tags: [security, jwt, authentication, authorization, fastapi]
---

# Auth Guard Skill

## Purpose
Enforce JWT-based authentication and authorization across all FastAPI endpoints, ensuring proper 401 (Unauthorized) and 403 (Forbidden) responses.

## Scope
- **Owned By**: @fastapi-jwt-guardian
- **Technology Stack**: FastAPI, JWT, Better Auth
- **Security Mandate**: All protected routes must validate JWT tokens

## Mandatory Security Requirements

### 1. Authentication Flow
```
Client Request → JWT Validation → User Extraction → Authorization Check → Business Logic
```

### 2. HTTP Status Codes
- **401 Unauthorized**: Missing or invalid JWT token
- **403 Forbidden**: Valid token but insufficient permissions
- **200/201**: Successful authenticated request
- **400**: Bad request (validation errors)
- **404**: Resource not found (after auth check)

### 3. JWT Middleware Pattern

#### Dependency Injection
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Extract and validate JWT token from Authorization header.
    Raises 401 if token is missing, expired, or invalid.
    """
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user from database
    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user
```

#### Protected Endpoint Pattern
```python
@router.get("/todos", response_model=list[TodoRead])
async def get_todos(
    current_user: User = Depends(get_current_user)  # ✅ Mandatory
):
    """
    Get all todos for the authenticated user.
    Returns 401 if not authenticated.
    """
    return get_user_todos(current_user.id)
```

#### Public Endpoint Pattern
```python
@router.post("/auth/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    """
    Public endpoint - no authentication required.
    """
    # Login logic
    return create_access_token(user.id)
```

### 4. Authorization Patterns

#### Role-Based Access Control (RBAC)
```python
def require_admin(current_user: User = Depends(get_current_user)):
    """
    Dependency for admin-only endpoints.
    Returns 403 if user is not an admin.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user
```

#### Resource Ownership Check
```python
@router.delete("/todos/{todo_id}")
async def delete_todo(
    todo_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a todo. Returns 403 if user doesn't own the todo.
    """
    todo = get_todo(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    if todo.user_id != current_user.id:  # ✅ Authorization check
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this todo"
        )

    delete_todo_by_id(todo_id)
    return {"message": "Todo deleted"}
```

### 5. Token Management

#### Token Structure
```python
{
    "sub": user_id,        # Subject (user identifier)
    "exp": timestamp,      # Expiration time
    "iat": timestamp,      # Issued at
    "type": "access",      # Token type
}
```

#### Token Creation
```python
from datetime import datetime, timedelta
from jose import jwt

def create_access_token(user_id: int) -> str:
    """Create JWT access token."""
    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    }
    return jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )
```

### 6. Security Best Practices

#### Environment Variables
```bash
# .env file (NEVER commit to git)
JWT_SECRET=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### CORS Configuration
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # ✅ Specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)
```

## Validation Checks

When invoked, this skill will:
1. Scan all FastAPI route handlers in `backend/routers/`
2. Identify endpoints without authentication
3. Verify proper 401/403 error handling
4. Check JWT secret configuration
5. Validate token expiration settings
6. Test CORS configuration
7. Generate security audit report

## Automatic Fixes

The skill can automatically:
- Add `Depends(get_current_user)` to unprotected endpoints
- Generate proper error responses
- Create JWT middleware boilerplate
- Add security headers

## Usage

```bash
# Validate all endpoints
/auth-guard

# Audit specific router
/auth-guard --router todos

# Test JWT validation
/auth-guard --test-tokens

# Security audit report
/auth-guard --security-audit
```

## Success Criteria
- ✅ All protected endpoints require valid JWT
- ✅ 401 responses for missing/invalid tokens
- ✅ 403 responses for insufficient permissions
- ✅ JWT secrets properly configured in .env
- ✅ Token expiration enforced
- ✅ CORS configured securely

## Integration
This skill integrates with:
- **@fastapi-jwt-guardian**: Primary owner and executor
- **@database-expert**: User validation and queries
- **@logic-coordinator**: Better Auth secret synchronization
- **@qa-automation**: Security testing and penetration testing

## Common Vulnerabilities Prevented
1. **Missing Authentication**: Unprotected endpoints
2. **Token Replay**: Expiration enforcement
3. **IDOR**: Resource ownership validation
4. **CSRF**: Token-based auth (stateless)
5. **XSS**: HTTPOnly cookies (if using cookie auth)
6. **Timing Attacks**: Constant-time comparisons for secrets
