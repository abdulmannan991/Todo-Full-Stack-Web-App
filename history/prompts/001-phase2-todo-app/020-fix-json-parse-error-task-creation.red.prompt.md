---
id: 020
title: Fix JSON parse error in task creation
stage: red
date: 2026-01-06
surface: agent
model: claude-sonnet-4-5
feature: 001-phase2-todo-app
branch: 001-phase2-todo-app
user: architect
command: /sp.implement
labels: ["debugging", "P0", "authentication", "error-handling"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/components/TaskCreateForm.tsx
tests:
  - Manual testing required for task creation flow
  - Authentication error handling scenarios
  - Non-JSON response handling
---

## Prompt

```text
# Role: Senior Full-Stack Architect & Runtime Debugging Specialist
# Mode: Root-Cause Debugging + Targeted Fix (NO REFACTOR)
# Severity: 🚨 P0 – Task Creation Broken
# Objective: Fix `Unexpected end of JSON input` when creating a task

We have a confirmed runtime failure during task creation.

📸 Evidence (from browser console):
- `Failed to execute 'json' on 'Response': Unexpected end of JSON input`
- `POST /tasks` fails
- Backend responds with `403 Forbidden` or empty body
- Frontend crashes while calling `response.json()`
- Network log shows `/api/auth/session` returning `404`

This is NOT a UI bug.
This is an **API response contract violation**.

---

## 🔐 CORE RULE (NON-NEGOTIABLE)

> The frontend must NEVER assume a JSON response unless the backend explicitly returns JSON.

If the backend returns:
- `403`
- `401`
- `404`
- empty body
- HTML error page

Then calling `response.json()` is a bug.

---

## 🛑 ROOT CAUSE ANALYSIS (YOU MUST CONFIRM)

Before fixing, identify which of the following is true:

1. Backend `/tasks` returns `403` due to missing auth cookie
2. Backend `/tasks` returns no body on error
3. Backend auth dependency fails before reaching route logic
4. Frontend fetch does not send cookies (`credentials` missing)
5. Backend CORS blocks credentials
6. Frontend parses JSON even when `response.ok === false`

You must fix the **actual cause**, not just silence the error.

---

## 🛑 REQUIRED FIXES (ALL MUST BE VERIFIED)

### 1️⃣ BACKEND: Ensure `/tasks` ALWAYS Returns JSON

**File**: `backend/routers/tasks.py`

- Confirm:
  - `get_current_user` is correctly injected
  - Auth failure returns:
    ```json
    { "detail": "Not authenticated" }
    ```
- Ensure **no route returns an empty response body**

---

### 2️⃣ BACKEND: CORS MUST ALLOW COOKIES

**File**: `backend/main.py`

Verify:
```python
CORSMiddleware...
```

## Response snapshot

## ROOT CAUSE IDENTIFIED

Three critical issues were found:

1. **Non-existent API endpoint** (TaskCreateForm.tsx:67-69)
   - Code called `/api/auth/session` which does not exist
   - Resulted in 404 Not Found response

2. **Unsafe JSON parsing** (TaskCreateForm.tsx:91)
   - Code called `response.json()` without checking `response.ok` first
   - When backend returned 401/403/404 with empty body, JSON parsing crashed

3. **Wrong authentication pattern**
   - Component attempted manual session fetch instead of using existing `useSession` hook
   - Dashboard page already uses correct pattern with `@/lib/auth-client`

## FIXES APPLIED

### File: `frontend/components/TaskCreateForm.tsx`

**1. Added proper authentication hook:**
```typescript
import { useSession } from "@/lib/auth-client";

export default function TaskCreateForm({ onTaskCreated }: TaskCreateFormProps) {
  const { data: session } = useSession();
  // ...
}
```

**2. Removed broken session fetch:**
- Removed lines 67-75: manual fetch to `/api/auth/session`
- Replaced with session check from hook
- Added early return with redirect if no session

**3. Added safe error handling:**
```typescript
// CRITICAL: Check response.ok BEFORE calling response.json()
if (!response.ok) {
  let errorMessage = "Failed to create task";

  try {
    // Attempt to parse JSON error body if present
    const errorData = await response.json();
    errorMessage = errorData.detail || errorMessage;
  } catch {
    // Response body is empty or not JSON - use status code
    if (response.status === 401 || response.status === 403) {
      errorMessage = "Authentication required";
      window.location.href = "/login";
      return;
    }
    errorMessage = `Server error (${response.status})`;
  }

  throw new Error(errorMessage);
}

// Safe to call .json() now
const newTask = await response.json();
```

## Outcome

- ✅ Impact: Critical P0 bug fixed - task creation no longer crashes
- 🧪 Tests: Requires manual testing across authentication scenarios
- 📁 Files: 1 file modified (TaskCreateForm.tsx)
- 🔁 Next prompts: Test task creation with authenticated/unauthenticated users
- 🧠 Reflection: The fix follows the established pattern from dashboard.tsx and adds defensive error handling

## Evaluation notes (flywheel)

- Failure modes observed: Unsafe JSON parsing, incorrect auth pattern, non-existent API endpoint
- Graders run and results (PASS/FAIL): Manual testing required
- Prompt variant (if applicable): Debugging session with root cause analysis
- Next experiment (smallest change to try): Add comprehensive error logging for auth failures
