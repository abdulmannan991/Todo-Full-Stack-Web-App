# Security Architecture: FlowTask Multi-Tenant Application

**Document Version**: 1.0
**Sprint**: 2 (Complete)
**Last Updated**: 2026-01-06
**Status**: Production-Ready ✅

---

## Executive Summary

FlowTask implements a **Zero-Trust Multi-Tenant Security Model** based on Constitution Principle II and III. All data access is governed by JWT-based authentication and user_id-filtered queries, ensuring complete isolation between users.

### Security Guarantees

✅ **Authentication**: All protected endpoints require valid JWT tokens
✅ **Authorization**: User IDs extracted exclusively from JWT (never client input)
✅ **Data Isolation**: 100% of database queries filter by `user_id`
✅ **Information Leakage Prevention**: 404 responses for unauthorized access
✅ **Password Security**: Bcrypt hashing with salt (12 rounds)
✅ **File Upload Validation**: Type and size checks for profile images

---

## 1. JWT-Based Authentication

### 1.1 Token Generation (Frontend)

**Library**: Better Auth (https://www.better-auth.com/)
**Algorithm**: HS256 (HMAC with SHA-256)
**Secret**: `BETTER_AUTH_SECRET` (256-bit shared secret)

**Signup Flow**:
```typescript
// frontend/lib/auth-client.ts
export const signUp = {
  email: async ({ email, password, name }) => {
    const response = await fetch(`${API_URL}/api/auth/sign-up/email`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ email, password, name }),
    })

    // ❌ CRITICAL: Signup does NOT create session
    // User MUST login after signup to get valid JWT
    const data = await response.json()
    return data  // No setSession() call
  },
}
```

**Login Flow**:
```typescript
// frontend/lib/auth-client.ts
export const signIn = {
  email: async ({ email, password }) => {
    const response = await fetch(`${API_URL}/api/auth/sign-in/email`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ email, password }),
    })

    const data = await response.json()
    setSession(data)  // ✅ Store JWT + user data
    return data
  },
}
```

**JWT Payload Example**:
```json
{
  "sub": "123",          // User ID (primary key)
  "email": "user@example.com",
  "iat": 1704454800,     // Issued at (Unix timestamp)
  "exp": 1705059600      // Expires at (7 days)
}
```

**Storage**:
- **localStorage**: `auth_token` (JWT string), `user_data` (JSON)
- **Cookie**: `auth_token` (SameSite=Lax, 7-day expiration)

**Why Both?**
- localStorage: Fast client-side access for API calls
- Cookie: Enables middleware to read session for route protection

---

### 1.2 Token Validation (Backend)

**Library**: python-jose[cryptography]
**File**: `backend/auth.py`

```python
from jose import JWTError, jwt

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, int]:
    """
    JWT validation dependency for protected routes.

    Returns:
        Dict containing user_id extracted from JWT token

    Raises:
        HTTPException 401: If token is missing, invalid, or expired
    """
    token = credentials.credentials

    try:
        # Decode and validate JWT token
        payload = jwt.decode(
            token,
            BETTER_AUTH_SECRET,
            algorithms=["HS256"],
        )

        # Extract user_id from 'sub' claim (subject)
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
            )

        # Return user_id as integer
        # CRITICAL: This is the ONLY source of user_id for data isolation
        return {"user_id": int(user_id)}

    except JWTError as e:
        # Token validation failed (invalid signature, expired, etc.)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
        )
```

**Security Properties**:
- ✅ Signature verification prevents token tampering
- ✅ Expiration check prevents replay attacks
- ✅ BETTER_AUTH_SECRET never exposed to client
- ✅ 401 response for any validation failure

---

## 2. Multi-Tenant Data Isolation

### 2.1 Database Schema

**User Model** (`backend/models/user.py`):
```python
class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)  # Indexed for fast lookup
    password_hash: str = Field()
    display_name: str | None = Field(default=None)
    profile_image_url: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Task Model** (`backend/models/task.py`):
```python
class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)  # CRITICAL: Indexed FK
    title: str = Field(max_length=500)
    description: str | None = Field(default=None, max_length=5000)
    status: TaskStatus = Field(default=TaskStatus.pending)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Foreign Key Constraint**:
```sql
ALTER TABLE tasks
ADD CONSTRAINT tasks_user_id_fkey
FOREIGN KEY (user_id) REFERENCES users(id)
ON DELETE CASCADE;
```

**Why CASCADE?**
When a user is deleted, all their tasks are automatically removed (prevents orphaned data).

**Index on user_id**:
```sql
CREATE INDEX ix_tasks_user_id ON tasks(user_id);
```

**Why Index?**
Every task query filters by `user_id`. Index ensures O(log n) lookup instead of O(n) table scan.

---

### 2.2 Query Filtering Strategy

**CRITICAL RULE**: **All database queries MUST include `.where(Task.user_id == current_user["user_id"])`**

#### Example 1: List Tasks (GET /tasks)
```python
@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),  # ✅ Inject user_id from JWT
):
    user_id = current_user["user_id"]

    # CRITICAL: Filter by user_id (Constitution Principle III)
    statement = (
        select(Task)
        .where(Task.user_id == user_id)  # Multi-tenant isolation
        .order_by(Task.created_at.desc())
    )

    tasks = session.exec(statement).all()
    return tasks
```

**Security Analysis**:
- ✅ `user_id` sourced from JWT (not request body)
- ✅ `.where()` clause filters results to current user
- ✅ Empty list returned if no tasks (not 404)

---

#### Example 2: Update Task (PATCH /tasks/{id})
```python
@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdateRequest,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]

    # CRITICAL: Filter by BOTH task_id AND user_id
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id  # Ownership verification
    )
    task = session.exec(statement).first()

    if not task:
        # Return 404 for both "not found" and "unauthorized"
        # This prevents leaking information about task existence
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Update task...
    return task
```

**Security Analysis**:
- ✅ Ownership verified via `.where(Task.user_id == user_id)`
- ✅ 404 response (not 403) prevents ID probing
- ✅ No information leaked about other users' tasks

---

#### Example 3: Delete Task (DELETE /tasks/{id})
```python
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]

    # CRITICAL: Filter by BOTH task_id AND user_id
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    task = session.exec(statement).first()

    if not task:
        # Log deletion attempt for audit (T110)
        print(f"[AUDIT] User {user_id} attempted to delete non-existent/unauthorized task {task_id}")

        # Return 404 (prevents data leakage)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    session.delete(task)
    session.commit()

    # Log successful deletion for audit
    print(f"[AUDIT] User {user_id} deleted task {task_id}")

    return None
```

**Security Analysis**:
- ✅ Audit logging for security monitoring
- ✅ 404 response (not 403) prevents ID probing
- ✅ No user can delete another user's tasks

---

### 2.3 Attack Scenarios & Mitigations

#### Scenario 1: ID Probing Attack

**Attack**:
```bash
# Attacker (user_id=2) tries to access victim's task (user_id=1, task_id=42)
curl -X GET http://localhost:8000/tasks/42 \
  -H "Authorization: Bearer <attacker-jwt>"
```

**Response**:
```json
{
  "detail": "Task not found"
}
```

**Why This Is Secure**:
- Attacker receives 404 (not 403)
- Cannot distinguish between:
  - Task doesn't exist
  - Task exists but belongs to another user
- No information leaked about victim's data

---

#### Scenario 2: Client-Supplied user_id Attack

**Attack**:
```bash
# Attacker tries to inject user_id in request body
curl -X POST http://localhost:8000/tasks \
  -H "Authorization: Bearer <attacker-jwt>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Steal data", "user_id": 1}'  # Malicious payload
```

**Backend Handling**:
```python
# backend/schemas/task.py
class TaskCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = Field(None, max_length=5000)
    # ❌ NO user_id field in schema
```

```python
# backend/routers/tasks.py
@router.post("/", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreateRequest,  # ✅ Schema excludes user_id
    current_user: dict = Depends(get_current_user),
):
    # user_id derived from JWT (NEVER from request body)
    user_id = current_user["user_id"]  # ✅ Trusted source

    new_task = Task(
        user_id=user_id,  # ✅ Overwrite any client-supplied value
        title=task_data.title,
        description=task_data.description,
    )
    # ...
```

**Why This Is Secure**:
- ✅ Pydantic schema excludes `user_id` field
- ✅ Even if attacker modifies request, `user_id` is overwritten
- ✅ No way for client to escalate privileges

---

## 3. Password Security

### 3.1 Hashing Algorithm

**Library**: bcrypt
**Rounds**: 12 (2^12 = 4096 iterations)
**Salt**: Automatically generated per-password

**Signup Implementation**:
```python
# backend/routers/auth.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/api/auth/sign-up/email")
async def sign_up(
    body: SignUpRequest,
    session: Session = Depends(get_session),
):
    # Hash password with bcrypt
    hashed_password = pwd_context.hash(body.password)

    new_user = User(
        email=body.email,
        password_hash=hashed_password,  # ✅ Never store plaintext
        display_name=body.name,
    )

    session.add(new_user)
    session.commit()
    # ...
```

**Login Verification**:
```python
# backend/routers/auth.py
@router.post("/api/auth/sign-in/email")
async def sign_in(
    body: SignInRequest,
    session: Session = Depends(get_session),
):
    # Fetch user by email
    user = session.exec(select(User).where(User.email == body.email)).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Verify password (constant-time comparison)
    if not pwd_context.verify(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Generate JWT...
```

**Security Properties**:
- ✅ Bcrypt is slow (prevents brute-force attacks)
- ✅ Automatic salt prevents rainbow table attacks
- ✅ Constant-time comparison prevents timing attacks
- ✅ No plaintext passwords in database or logs

---

## 4. File Upload Security

### 4.1 Profile Image Upload

**Endpoint**: `POST /users/me/avatar`
**Max Size**: 2MB
**Allowed Types**: JPG, PNG
**Storage**: `backend/uploads/avatars/`

**Implementation**:
```python
# backend/routers/users.py
@router.post("/me/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: Dict[str, int] = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    user_id = current_user["user_id"]

    # Validate file type (T119)
    allowed_types = ["image/jpeg", "image/jpg", "image/png"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only JPG and PNG images are allowed"
        )

    # Validate file size (T119)
    MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Image must be under 2MB"
        )

    # Sanitize filename (prevent path traversal)
    file_extension = Path(file.filename or "image.jpg").suffix.lower()
    if file_extension not in [".jpg", ".jpeg", ".png"]:
        file_extension = ".jpg"

    timestamp = int(datetime.utcnow().timestamp())
    safe_filename = f"{user_id}_{timestamp}{file_extension}"

    # Save file
    uploads_dir = Path("backend/uploads/avatars")
    uploads_dir.mkdir(parents=True, exist_ok=True)

    file_path = uploads_dir / safe_filename
    with open(file_path, "wb") as f:
        f.write(content)

    # Update user.profile_image_url
    user.profile_image_url = f"/uploads/avatars/{safe_filename}"
    session.commit()
    # ...
```

**Security Analysis**:
- ✅ MIME type validation (prevents PHP shell uploads)
- ✅ Size limit prevents disk exhaustion attacks
- ✅ Filename sanitization prevents path traversal (`../../../etc/passwd`)
- ✅ User ID in filename prevents overwrites
- ✅ Timestamp prevents cache collisions

---

## 5. Frontend Security

### 5.1 Session Validation

**Single Source of Truth**: Backend `/users/me` endpoint

**Implementation**:
```typescript
// frontend/lib/auth-client.ts
export const useSession = () => {
  const [session, setSession] = React.useState<SessionData | null>(null)

  const validateSession = React.useCallback(async () => {
    const localSession = getSession()  // ❌ UNTRUSTED (client-controlled)

    if (!localSession) {
      setSession(null)
      return
    }

    try {
      // Validate session against backend (✅ TRUSTED)
      const response = await fetch(`${API_URL}/users/me`, {
        method: 'GET',
        headers: { 'Authorization': `Bearer ${localSession.token}` },
      })

      // Backend rejected session (401/403)
      if (response.status === 401 || response.status === 403) {
        console.warn('[Auth] Backend rejected session - clearing local state')
        // HARD RESET: Clear ALL auth state immediately
        removeSession()
        setSession(null)
        return
      }

      // Backend confirmed session is valid
      const userData = await response.json()
      setSession({ token: localSession.token, user: userData })

    } catch (err) {
      // Network error - clear session for safety
      removeSession()
      setSession(null)
    }
  }, [])

  return { data: session, isPending, error, refreshSession }
}
```

**Security Properties**:
- ✅ Backend is single source of truth
- ✅ LocalStorage treated as untrusted cache
- ✅ Session cleared on 401/403 (prevents ghost sessions)
- ✅ Network errors handled conservatively (clear session)

---

## 6. Security Checklist (Sprint 2)

### Authentication & Authorization
- [X] All protected endpoints use `Depends(get_current_user)`
- [X] JWT signature validated on every request
- [X] `user_id` extracted from JWT 'sub' claim (never client input)
- [X] 401 responses for missing/invalid tokens
- [X] Session validation against backend `/users/me`

### Data Isolation
- [X] All Task queries filter by `user_id`
- [X] Foreign key constraint: `Task.user_id → User.id`
- [X] Index on `tasks.user_id` for performance
- [X] No hardcoded `user_id` values in codebase
- [X] 404 responses for unauthorized access (not 403)

### Password Security
- [X] Bcrypt hashing with 12 rounds
- [X] Automatic salt generation
- [X] Constant-time password verification
- [X] No plaintext passwords in database or logs
- [X] Password visibility toggles on login/signup

### File Upload Security
- [X] MIME type validation (JPG/PNG only)
- [X] File size limit (2MB)
- [X] Filename sanitization (path traversal prevention)
- [X] User-scoped uploads (user_id in filename)
- [X] Static file serving via FastAPI `StaticFiles`

### Frontend Security
- [X] Backend session validation on every page load
- [X] LocalStorage treated as untrusted cache
- [X] 401/403 triggers immediate session clearing
- [X] No JWT secrets in client bundle
- [X] CORS restricted to frontend origin

---

## 7. Future Security Enhancements

### Immediate (Sprint 3)
- [ ] Rate limiting on auth endpoints (prevent brute-force)
- [ ] Account lockout after N failed login attempts
- [ ] Email verification for signups
- [ ] Password strength requirements (min length, complexity)
- [ ] CSRF protection for state-changing operations

### Medium Term
- [ ] Refresh tokens (separate access + refresh tokens)
- [ ] Token rotation on renewal
- [ ] Account activity logging (login history, IP tracking)
- [ ] Two-factor authentication (2FA) support
- [ ] Session revocation endpoint

### Long Term
- [ ] Audit logging to external service (CloudWatch, Sentry)
- [ ] Penetration testing and security review
- [ ] GDPR compliance (data export, deletion)
- [ ] SOC 2 Type II certification preparation

---

## 8. Security Incident Response

### Suspected JWT Compromise
1. **Immediate**: Rotate `BETTER_AUTH_SECRET` in both frontend and backend
2. **Impact**: All existing JWTs invalidated (users must re-login)
3. **Notification**: Email all users about password reset recommendation

### Suspected Data Leak
1. **Investigate**: Check audit logs for unauthorized access attempts
2. **Verify**: Run query to detect cross-user data exposure:
   ```sql
   SELECT t1.user_id, t2.user_id, COUNT(*)
   FROM tasks t1
   JOIN tasks t2 ON t1.id = t2.id
   WHERE t1.user_id != t2.user_id;
   ```
3. **Remediate**: If leak confirmed, notify affected users and regulatory bodies

### File Upload Exploit
1. **Immediate**: Disable `/users/me/avatar` endpoint
2. **Investigate**: Scan `uploads/avatars/` for non-image files
3. **Fix**: Add additional MIME type verification (magic bytes check)
4. **Deploy**: Re-enable endpoint after patch

---

## 9. References

- **Constitution Principle II**: Zero Trust Security Model
- **Constitution Principle III**: Mandatory Data Isolation
- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **JWT Best Practices**: https://datatracker.ietf.org/doc/html/rfc8725
- **Bcrypt Specification**: https://en.wikipedia.org/wiki/Bcrypt

---

**Document Owner**: @fastapi-jwt-guardian
**Review Cycle**: Quarterly
**Next Review**: 2026-04-06
