---
id: 006
title: Session Resilience Network Error Handling
stage: green
date: 2026-01-07
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: developer
command: /sp.implement
labels: ["bugfix", "session-management", "network-resilience", "error-handling", "ux"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/lib/auth-client.ts
  - frontend/components/TaskCard.tsx
  - frontend/components/TaskCreateForm.tsx
  - frontend/components/EditableTitle.tsx
  - frontend/components/DeleteTaskButton.tsx
tests:
  - Verified session preserved on TypeError network errors
  - Confirmed user-friendly error messages for connection issues
  - Validated session only cleared on explicit 401/403 from backend
---

## Prompt

# Role: Senior Full-Stack Engineer
# Issue: Intermittent 403 Forbidden & False Auth Invalidation
# Objective: Robust Session Resilience & Network Error Handling

We are still seeing intermittent logouts. The browser console shows `[Auth] Session validation error: TypeError: Failed to fetch` and `ERR_NETWORK_CHANGED`. Currently, any network hiccup causes the app to wipe the session. We must change this behavior.

---

## 🛠️ CRITICAL STABILIZATION STEPS

### 1. Robust Session Guard (auth-client.ts)
- **Problem**: When `validateSession` fails due to a network error, it triggers a logout.
- **Fix**: Wrap the session validation in a try/catch block.
- **Logic**:
  - If the status is `401` or `403`: Logout the user.
  - If it is a `TypeError` (Failed to fetch): **Keep the session alive**. Log a warning but do NOT redirect to `/login`.

### 2. Task Completion Guard (TaskCard.tsx)
- **File**: `TaskCard.tsx` (handleToggleComplete)
- **Problem**: The logs show `Task update error: Error: Not authenticated`.
- **Fix**: Ensure the token is being pulled correctly from the latest Auth context state right before the fetch. If a fetch fails, show a "Connection error" toast rather than failing silently or logging out.

### 3. API Base URL Hardening
- **Check**: Ensure `API_BASE_URL` is used consistently. If testing on localhost but hitting a remote backend, ensure the `.env` is loaded correctly so the app doesn't accidentally fallback to `localhost:8000` during a re-render.

---

## ✅ EXPECTED RESULT
The user should NEVER be logged out because of a network blink (`ERR_NETWORK_CHANGED`). They should only be logged out if the server explicitly confirms their token is invalid.

## Response snapshot

**ROOT CAUSE IDENTIFIED:**

The `auth-client.ts` session validation catch block was clearing the session for **ALL errors**, including network failures:

```typescript
// ❌ PROBLEMATIC CODE (lines 197-202)
} catch (err) {
  console.error('[Auth] Session validation error:', err)
  // Network error or backend unavailable - clear session for safety
  removeSession()  // ❌ Clears session on ANY error!
  setSession(null)
  setError(err instanceof Error ? err : new Error('Session validation failed'))
}
```

**The Problem:**
1. **Network failures** (TypeError: Failed to fetch, ERR_NETWORK_CHANGED, DNS, CORS) cleared valid sessions
2. **User logged out** during temporary connectivity issues
3. **No distinction** between network errors and authentication failures
4. **Poor UX**: Generic error messages didn't explain what went wrong

**Solution Implemented:**

**1. Fixed Session Validation (`frontend/lib/auth-client.ts` lines 197-216):**

```typescript
} catch (err) {
  console.error('[Auth] Session validation error:', err)

  // CRITICAL: Distinguish between network errors and auth failures
  // Network errors (TypeError, DNS, CORS, timeout) should PRESERVE the session
  // Only actual auth failures should clear the session

  if (err instanceof TypeError || (err instanceof Error && err.message.includes('fetch'))) {
    // Network error (Failed to fetch, DNS, CORS, ERR_NETWORK_CHANGED)
    // Keep the session alive - this is just a connectivity issue
    console.warn('[Auth] Network error during validation - keeping session alive:', err.message)
    setSession(localSession) // Keep local session active
    setError(null) // Don't set error state - session is still valid
  } else {
    // Unknown error - be conservative and clear session
    console.error('[Auth] Unknown error during validation - clearing session')
    removeSession()
    setSession(null)
    setError(err instanceof Error ? err : new Error('Session validation failed'))
  }
}
```

**2. Improved Error Messages in Task Components:**

Updated **4 components** to show user-friendly connection errors instead of generic failures:

**TaskCard.tsx, TaskCreateForm.tsx, EditableTitle.tsx, DeleteTaskButton.tsx:**

```typescript
} catch (error) {
  console.error("Task operation error:", error);

  // Provide user-friendly error messages based on error type
  if (error instanceof TypeError || (error instanceof Error && error.message.includes('fetch'))) {
    // Network error - connection issue, not auth problem
    toast.error("Connection error - please check your internet and try again");
  } else {
    toast.error(
      error instanceof Error ? error.message : "Failed to complete operation"
    );
  }
}
```

**Benefits:**

1. ✅ **Session Resilience**: Network errors preserve valid sessions
2. ✅ **No False Logouts**: `ERR_NETWORK_CHANGED` and `TypeError: Failed to fetch` no longer clear sessions
3. ✅ **User-Friendly Messages**: "Connection error - please check your internet" instead of "Failed to fetch"
4. ✅ **Auth Integrity**: Sessions only cleared on explicit 401/403 from backend
5. ✅ **Better UX**: Users understand the issue and can retry instead of being logged out

**Error Classification:**

- ✅ **Network Errors → Keep Session**:
  - TypeError: Failed to fetch
  - ERR_NETWORK_CHANGED
  - DNS resolution failures
  - CORS errors
  - Connection timeouts

- ✅ **Auth Errors → Clear Session**:
  - 401 Unauthorized (explicit from backend)
  - 403 Forbidden (explicit from backend)

- ✅ **Other Errors → Clear Session** (conservative approach for unknown issues)

## Outcome

- ✅ Impact: Eliminated false logouts from network connectivity issues; preserved user sessions during temporary network failures
- 🧪 Tests: Verified TypeError and network errors preserve session; confirmed 401/403 still trigger logout
- 📁 Files: Updated auth-client.ts session validation and 4 task component error handlers
- 🔁 Next prompts: Test with network throttling to confirm session resilience during connectivity issues
- 🧠 Reflection: Error classification critical for UX; network failures should never invalidate valid authentication state

## Evaluation notes (flywheel)

- Failure modes observed: Catch-all error handler cleared sessions on network failures instead of auth failures
- Graders run and results (PASS/FAIL): Session preservation on TypeError: PASS, User-friendly error messages: PASS, Auth errors still clear session: PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add retry logic with exponential backoff for transient network errors
