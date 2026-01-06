# Signup NotNullViolation Fix - Instructions

**Issue**: `500 Internal Server Error` during signup with error:
```
(psycopg2.errors.NotNullViolation) null value in column "password_hash" of relation "users" violates not-null constraint
DETAIL: Failing row contains (1, gg@gmail.com, null, gg, null, 2026-01-05 13:58:42.684395, 2026-01-05 13:58:42.684563).
```

**Root Cause**: Field name mismatch between User model and auth.py signup logic.

---

## Problem Analysis

### User Model Definition (`backend/models/user.py`)
```python
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)  # ← Field is named "password_hash"
    display_name: Optional[str] = Field(default=None, max_length=100)
    # ...
```

### Signup Endpoint (`backend/routers/auth.py`) - BEFORE FIX
```python
new_user = User(
    email=request.email,
    display_name=display_name,
    hashed_password=hashed_password,  # ❌ WRONG: Field doesn't exist!
)
```

**Result**: `password_hash` was set to `NULL` because `hashed_password` doesn't match any field in the User model.

### Additional Issues Found
- **user.user_id** → Should be **user.id** (primary key renamed in Sprint 2)
- All references to `user_id` attribute needed to be changed to `id`

---

## What Was Fixed

### 1. Password Hash Field Name ✅
**File**: `backend/routers/auth.py` line 117

**Before**:
```python
new_user = User(
    email=request.email,
    display_name=display_name,
    hashed_password=hashed_password,  # ❌ Wrong field name
)
```

**After**:
```python
new_user = User(
    email=request.email,
    display_name=display_name,
    password_hash=hashed_password,  # ✅ Correct field name
)
```

### 2. Primary Key References ✅
**File**: `backend/routers/auth.py` lines 127, 139-142, 183, 197-198, 210-213

**Changed all references**:
- `new_user.user_id` → `new_user.id`
- `user.user_id` → `user.id`

This affects:
- JWT token generation (line 127, 198)
- Response payload (lines 142, 213)
- Debug logging (lines 139, 183, 197, 210)

### 3. Password Verification Field ✅
**File**: `backend/routers/auth.py` line 186

**Before**:
```python
is_valid = verify_password(request.password, user.hashed_password)  # ❌ Wrong field
```

**After**:
```python
is_valid = verify_password(request.password, user.password_hash)  # ✅ Correct field
```

---

## Database Schema Verification

The database hard reset from the previous fix ensures the schema matches the User model:

**Table Structure**:
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,                -- ✅ Primary key is 'id', not 'user_id'
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,  -- ✅ Field name is 'password_hash'
    display_name VARCHAR(100),
    profile_image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## How to Verify the Fix

### Step 1: Restart Backend Server
```bash
cd backend
uvicorn main:app --reload
```

**Expected Console Output**:
```
Initializing database tables...
[HARD RESET] Dropping all existing tables...
[HARD RESET] All tables dropped successfully
[OK] Database tables initialized successfully with Sprint 2 schema
[OK] - User table with 'id' primary key
[OK] - Task table with foreign key to User.id
```

### Step 2: Test Signup Flow

Navigate to `http://localhost:3000/signup` and create an account:

**Email**: `test@example.com`
**Password**: `password123`
**Confirm Password**: `password123`

Click "Sign Up"

**Expected Result**:
- ✅ Green toast: "Account created successfully!"
- ✅ Redirect to `/login`
- ✅ NO `500 Internal Server Error`
- ✅ NO `password_hash violates not-null constraint` error

**Backend Console Output**:
```
[DEBUG] Signup request: test@example.com
[DEBUG] Hashing password...
[DEBUG] Creating user object...
[DEBUG] Adding to session...
[DEBUG] Generating JWT token...
[DEBUG] Signup successful for user 1
```

### Step 3: Test Login Flow

Navigate to `http://localhost:3000/login`:

**Email**: `test@example.com`
**Password**: `password123`

Click "Log In"

**Expected Result**:
- ✅ Redirect to `/dashboard`
- ✅ Navbar shows "Welcome, Test!" (parsed from email)
- ✅ Dashboard displays correctly

**Backend Console Output**:
```
[DEBUG] Login attempt for: test@example.com
[DEBUG] User found: 1, verifying password...
[DEBUG] Password verification result: True
[DEBUG] Generating JWT for user 1
[DEBUG] Login successful for user 1
```

### Step 4: Verify Database Entry

Check Neon DB console:

**Query**:
```sql
SELECT id, email, password_hash, display_name, created_at
FROM users
WHERE email = 'test@example.com';
```

**Expected Result**:
```
id | email             | password_hash                                          | display_name | created_at
---|-------------------|--------------------------------------------------------|--------------|------------------
1  | test@example.com  | $2b$12$... (bcrypt hash, ~60 characters)                 | test         | 2026-01-05 ...
```

**Verify**:
- ✅ `password_hash` is NOT NULL
- ✅ `password_hash` starts with `$2b$12$` (bcrypt format)
- ✅ `id` is an integer (auto-generated)
- ✅ `display_name` matches email prefix

---

## Verification Checklist

After applying the fix, verify:

- [ ] Backend restarts without errors
- [ ] Signup creates new users successfully
- [ ] `password_hash` column populated correctly (not NULL)
- [ ] Login works with newly created users
- [ ] JWT token generated with correct user.id
- [ ] Dashboard displays "Welcome, [User]!"
- [ ] No `NotNullViolation` errors in console
- [ ] Database entry shows bcrypt hash in `password_hash` field

---

## Troubleshooting

### Error: "password_hash violates not-null constraint" persists
- Verify `backend/routers/auth.py` line 117 uses `password_hash=hashed_password`
- Restart backend server to reload code changes
- Clear browser cache and try signup again

### Error: "AttributeError: 'User' object has no attribute 'user_id'"
- Verify all references changed from `.user_id` to `.id`
- Check lines 127, 142, 183, 198, 213 in `auth.py`
- Restart backend server

### Error: "AttributeError: 'User' object has no attribute 'hashed_password'"
- Verify line 186 in `auth.py` uses `user.password_hash`
- Restart backend server

### Signup succeeds but login fails
- Check password verification uses correct field: `user.password_hash`
- Verify bcrypt hash was saved correctly in database
- Test password hashing manually:
  ```python
  from passlib.context import CryptContext
  pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
  hashed = pwd_context.hash("password123")
  print(pwd_context.verify("password123", hashed))  # Should be True
  ```

---

## Next Steps After Fix

1. ✅ Remove hard reset code from `database.py` (lines 81-85) after first successful signup
2. ✅ Test full authentication flow:
   - Signup → green toast → redirect to login
   - Login → dashboard with navbar
   - Logout → redirect to landing
3. ✅ Create multiple test users to verify unique email constraint
4. ✅ Test task CRUD operations with authenticated users
5. ✅ Verify multi-tenant isolation (users only see their own tasks)

---

## Files Modified

1. ✅ **backend/routers/auth.py** - Fixed field names (5 changes)
   - Line 117: `hashed_password` → `password_hash`
   - Line 127: `new_user.user_id` → `new_user.id`
   - Line 142: `new_user.user_id` → `new_user.id`
   - Line 183: `user.user_id` → `user.id`
   - Line 186: `user.hashed_password` → `user.password_hash`
   - Line 198: `user.user_id` → `user.id`
   - Line 213: `user.user_id` → `user.id`

2. ✅ **backend/database.py** - Hard reset already in place (from previous fix)

---

**Status**: Signup fix implemented and ready to test
**Next Action**: Restart backend server and test signup flow
**CRITICAL**: Remove hard reset code after first successful signup!
