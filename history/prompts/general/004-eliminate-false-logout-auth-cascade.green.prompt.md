---
id: 004
title: Eliminate False Logout Auth Cascade
stage: green
date: 2026-01-07
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: developer
command: /sp.implement
labels: ["bugfix", "frontend", "authentication", "error-handling", "ux"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/components/TaskCreateForm.tsx
  - frontend/components/TaskCard.tsx
  - frontend/components/EditableTitle.tsx
  - frontend/components/DeleteTaskButton.tsx
tests:
  - Verified middleware only checks auth_token cookie presence
  - Confirmed 401/403 error handling remains intact
  - Removed premature session checks from all task operations
---

## Prompt

# Role: Senior Full-Stack Developer
# Objective: Eliminate False Logouts and Fix Error Handling Logic

The backend serialization is fixed, but the frontend still intermittently redirects to `/login` when a task operation fails (especially with descriptions). We need to stop this "Auth Cascade."

---

## 🛠️ REQUIRED INVESTIGATION & CHANGES

### 1. Global Middleware Check (CRITICAL)
- **File**: Search for `middleware.ts` or `src/middleware.ts`.
- **Logic**: Ensure the middleware is NOT redirecting to `/login` based on generic API error statuses (like 422 or 500). It should only handle redirection if the actual session cookie/token is missing or if the backend explicitly returns a 401 Unauthorized.

### 2. Dashboard API Logic (Frontend)
- **File**: `Dashboard.tsx` or your Task API client.
- **Change**: Wrap the response check in a specific conditional:
  ```javascript
  if (response.status === 401 || response.status === 403) {
      handleLogout(); // Only for true auth failure
  } else if (!response.ok) {
      const errorData = await response.json();
      showNotification(`Error: ${errorData.detail || 'Action failed'}`);
      // DO NOT REDIRECT HERE
  }
  ```

## Response snapshot

**ROOT CAUSE IDENTIFIED:**

The frontend had **premature authentication checks** in all task operation components that redirected to login **before** making API calls:

```javascript
// ❌ PROBLEMATIC CODE (lines 67-72 in TaskCreateForm.tsx and similar in other components)
if (!session?.token) {
  toast.error("Authentication required");
  window.location.href = "/login";  // Immediate redirect!
  return;
}
```

**The Problem:**
1. React `useSession()` hook can return `null`/`undefined` temporarily during re-renders
2. This triggers immediate logout redirect even for authenticated users
3. The middleware already protects these routes - **these checks were redundant**
4. Backend 401/403 error handling in catch blocks was sufficient

**Verification Results:**

1. **Middleware (frontend/middleware.ts:34):** ✅ CORRECT
   - Only checks for `auth_token` cookie presence
   - Does NOT redirect based on API error statuses
   - No false logout triggers

2. **Error Handling:** ✅ CORRECT
   - All components properly handle 401/403 in catch blocks
   - Only redirect on genuine auth failures from backend
   - Other errors (422, 500) show toast without logout

3. **The Auth Cascade Pattern Found:**
   - TaskCreateForm.tsx:68-70
   - TaskCard.tsx:53-55
   - EditableTitle.tsx:95-97
   - DeleteTaskButton.tsx:46-48

**Fix Applied:**

Removed premature `if (!session?.token)` checks from all 4 components and updated Authorization header to use fallback:

**Before:**
```javascript
// Premature check causing false logouts
if (!session?.token) {
  toast.error("Authentication required");
  window.location.href = "/login";
  return;
}

// API call
const response = await fetch(url, {
  headers: {
    Authorization: `Bearer ${session.token}`,
  }
});
```

**After:**
```javascript
// No premature check - let backend be the authority
const response = await fetch(url, {
  headers: {
    Authorization: `Bearer ${session?.token || ''}`,
  }
});

// Backend returns 401 if token is invalid/missing
// Catch block handles redirect properly:
if (response.status === 401 || response.status === 403) {
  window.location.href = "/login";
}
```

**Benefits:**
1. ✅ Backend is single source of truth for authentication
2. ✅ No false logouts from transient React state
3. ✅ Middleware provides route protection
4. ✅ Proper error handling for 422/500 without logout
5. ✅ Cleaner code - removed redundant checks

## Outcome

- ✅ Impact: Eliminated false logout auth cascade caused by premature session checks
- 🧪 Tests: Verified middleware and error handling correctly distinguish auth failures from validation errors
- 📁 Files: Removed premature auth checks from 4 task operation components
- 🔁 Next prompts: Test task operations to confirm no more false logouts on transient errors
- 🧠 Reflection: Backend should be single source of truth for authentication; client-side checks cause race conditions

## Evaluation notes (flywheel)

- Failure modes observed: React hooks returning null during re-renders triggered premature redirects
- Graders run and results (PASS/FAIL): Middleware check: PASS, Error handling: PASS, Redundant checks removed: PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test with slow network to verify no false logouts during API delays
