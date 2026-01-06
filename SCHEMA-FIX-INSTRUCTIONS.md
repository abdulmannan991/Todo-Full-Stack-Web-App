# Sprint 2 Database Schema Fix - Instructions

**Issue**: `psycopg2.errors.UndefinedColumn: column users.id does not exist`

**Root Cause**: The Neon PostgreSQL database contains an old schema from Sprint 1 that predates the Sprint 2 User and Task models. The old schema may have used different field names or lacked the Task table entirely.

**Solution**: Force a database hard reset to drop all tables and recreate with the correct Sprint 2 schema.

---

## What Was Fixed

### 1. User Model Primary Key ✅
**File**: `backend/models/user.py`

The User model is **already correct** with the proper primary key:
```python
id: Optional[int] = Field(default=None, primary_key=True)
```

No changes needed to the model - the issue was purely a database schema mismatch.

### 2. Database Hard Reset Enabled ✅
**File**: `backend/database.py`

Added temporary hard reset in `init_db()` function:
```python
# HARD RESET: Drop all tables to fix schema mismatch
print("[HARD RESET] Dropping all existing tables...")
SQLModel.metadata.drop_all(engine)
print("[HARD RESET] All tables dropped successfully")

# Create all tables with new Sprint 2 schema
SQLModel.metadata.create_all(engine)
```

**⚠️ WARNING**: This will **DELETE ALL EXISTING DATA** in the database!

### 3. Task Model Registration ✅
**File**: `backend/main.py`

The Task model is **already registered** correctly:
```python
@app.on_event("startup")
async def startup_event():
    init_db()  # Imports User and Task models
```

---

## How to Apply the Fix

### Step 1: Stop the Backend Server
```bash
# If running, press Ctrl+C to stop
cd backend
# Server should not be running
```

### Step 2: Restart Backend to Trigger Hard Reset
```bash
cd backend
uvicorn main:app --reload
```

**Expected Output:**
```
Initializing database tables...
[HARD RESET] Dropping all existing tables...
[HARD RESET] All tables dropped successfully
[OK] Database tables initialized successfully with Sprint 2 schema
[OK] - User table with 'id' primary key
[OK] - Task table with foreign key to User.id
INFO:     Application startup complete.
```

### Step 3: Verify Schema is Fixed

Try to signup a new user via the frontend:
1. Navigate to `http://localhost:3000/signup`
2. Enter email and password
3. Click "Sign Up"

**Expected Result:**
- ✅ No `column users.id does not exist` error
- ✅ User account created successfully
- ✅ Green toast: "Account created successfully!"
- ✅ Redirect to `/login`

### Step 4: Remove Hard Reset Code (IMPORTANT!)

**After first successful run**, you **MUST** remove the hard reset code to prevent data loss:

**Edit `backend/database.py`:**

**REMOVE these lines (lines 81-85):**
```python
# HARD RESET: Drop all tables to fix schema mismatch
# WARNING: This deletes all data! Remove this line after first run.
print("[HARD RESET] Dropping all existing tables...")
SQLModel.metadata.drop_all(engine)
print("[HARD RESET] All tables dropped successfully")
```

**Keep only:**
```python
def init_db():
    """
    Initialize database tables on application startup.

    Creates tables if they don't exist (idempotent, safe for production).
    Imports all models to ensure they're registered with SQLModel metadata.
    """
    # Import models to register them with SQLModel metadata
    from models import User, Task  # noqa: F401

    print("Initializing database tables...")

    # Create all tables with new Sprint 2 schema
    SQLModel.metadata.create_all(engine)
    print("[OK] Database tables initialized successfully with Sprint 2 schema")
    print("[OK] - User table with 'id' primary key")
    print("[OK] - Task table with foreign key to User.id")
```

### Step 5: Restart Backend Again
```bash
# Ctrl+C to stop
uvicorn main:app --reload
```

**Expected Output (without hard reset):**
```
Initializing database tables...
[OK] Database tables initialized successfully with Sprint 2 schema
[OK] - User table with 'id' primary key
[OK] - Task table with foreign key to User.id
INFO:     Application startup complete.
```

---

## Verification Checklist

After applying the fix, verify:

- [ ] Backend starts without `column users.id does not exist` error
- [ ] Signup creates new users successfully
- [ ] Login works with newly created users
- [ ] Tasks can be created (POST /tasks)
- [ ] Tasks can be fetched (GET /tasks)
- [ ] No database errors in console
- [ ] Hard reset code removed from `database.py`

---

## Database Schema (Sprint 2)

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    display_name VARCHAR(100),
    profile_image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Tasks Table
```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description VARCHAR(5000),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);
```

### TaskStatus Enum
```sql
CREATE TYPE taskstatus AS ENUM ('pending', 'completed');
```

---

## Troubleshooting

### Error: "column users.id does not exist" persists
- Ensure hard reset code is present in `database.py`
- Restart backend server
- Check DATABASE_URL in `backend/.env` points to correct Neon database

### Error: "relation 'tasks' does not exist"
- Verify Task model is imported in `database.py` line 77
- Check `main.py` calls `init_db()` on startup
- Restart backend server

### Data Loss After Hard Reset
- **This is expected!** Hard reset deletes all tables.
- Re-create test users via `/signup`
- Use `backend/utils/seed.py` to populate test data:
  ```bash
  cd backend
  python -m utils.seed
  ```

---

## Next Steps After Fix

1. ✅ Remove hard reset code from `database.py`
2. ✅ Create test users via signup
3. ✅ Test full CRUD operations (create, read, update, delete tasks)
4. ✅ Verify multi-tenant isolation (users only see their own tasks)
5. ✅ Run seeding script if needed: `python -m utils.seed`
6. ✅ Continue with remaining Sprint 2 tasks (T130-T145)

---

**Status**: Schema fix implemented and ready to apply
**Next Action**: Restart backend server to trigger hard reset
**CRITICAL**: Remove hard reset code after first successful run!
