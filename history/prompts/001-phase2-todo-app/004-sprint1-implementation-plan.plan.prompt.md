---
id: 004
title: Sprint 1 Implementation Plan (Landing & Auth)
stage: plan
date: 2026-01-01
surface: agent
model: claude-sonnet-4-5
feature: 001-phase2-todo-app
branch: 001-phase2-todo-app
user: system
command: /sp.plan
labels: ["planning", "architecture", "sprint1", "landing-page", "authentication", "jwt", "agent-mapping", "quality-gates"]
links:
  spec: specs/001-phase2-todo-app/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-phase2-todo-app/plan.md
tests:
  - none
---

## Prompt

# Role: Project Architect
# Goal: Produce Phase 2 – Sprint 1 Execution Plan (Landing & Authentication)

Do NOT write code. Do NOT make assumptions. Do NOT skip any detail.

Your deliverable is the plan.md file that:
- Focuses exclusively on Landing Page & Authentication flows.
- Defines agent capabilities in detail (which agent owns what).
- Lists ordered, testable tasks with acceptance criteria.
- States explicit environment dependencies (e.g., Better Auth installation, FastAPI JWT middleware).
- Enforces constitution principles (Zero Trust, Data Isolation, Responsive 300–2560px, etc.).
- Includes Sprint Completion Criteria (what must be visible, blocked, validated).

## 1. Agent Capability & Responsibility Mapping (Mandatory)

Create a table that shows which concerns belong to @ui-auth-expert vs. @css-animation-expert.

Example:
| Concern | @ui-auth-expert | @css-animation-expert |
|---------|-----------------|----------------------|
| HTML structure | ✅ Owns | ❌ Does not modify |
| Tailwind layout utilities (flex, grid, p-*, m-*) | ✅ Owns | ❌ Does not modify |
| Tailwind color/visual utilities (bg-*, text-*, border-*) | ❌ Does not define | ✅ Owns |
| Form validation logic | ✅ Owns | ❌ Does not touch |
| Better Auth integration | ✅ Owns | ❌ Does not touch |
| Framer Motion variants | ❌ Does not define | ✅ Owns |
| Responsive breakpoints (sm:, md:, lg:) | ✅ Owns | ❌ Does not modify |
| Glassmorphism effects (backdrop-blur, bg-opacity) | ❌ Does not define | ✅ Owns |

Ensure each row is unambiguous.

## 2. Step-by-Step Execution Plan

Break the Sprint into ordered tasks. For each task:
- Assign owner (@ui-auth-expert or @css-animation-expert).
- State dependencies (e.g., "Requires T004 completion").
- Provide acceptance criteria (what must be true when done).

Suggested phases:
A. Infrastructure & Theme Foundation
B. Landing Page (Structure → Visual Design → Motion)
C. Signup & Login Pages (Structure → Visual Design → Toast Integration)
D. Backend JWT Validation (FastAPI Middleware)
E. Frontend-Backend Integration (API Client, Protected Routes)

## 3. Secure Authentication Flow Planning

Document the full JWT handshake:
1. User submits credentials on frontend.
2. Better Auth issues JWT.
3. Frontend stores JWT (where? httpOnly cookie? localStorage?).
4. Frontend includes JWT in Authorization header for API calls.
5. FastAPI middleware validates JWT using BETTER_AUTH_SECRET.
6. If valid, extract user_id and attach to request context.
7. If invalid, return 401 Unauthorized.

State environment variable requirements:
- BETTER_AUTH_SECRET must match between Next.js and FastAPI.

## 4. Landing Page & Motion Strategy

Landing page requirements:
- Route: /
- Content: Hero section with "Get Started" button.
- Behavior: If user is authenticated, redirect to /dashboard.
- Motion: Entrance animations for hero text and button (stagger pattern).

Define which agent does what:
- @ui-auth-expert: Creates page structure, implements auth redirect logic.
- @css-animation-expert: Applies Premium Midnight theme, implements Framer Motion entrance animations.

## 5. Verification & Quality Gates

For each task, define how to verify success:
- Constitution compliance checklist (e.g., "Zero Trust enforced? Data Isolation checked?").
- Performance validation (e.g., "Animations run at 60 FPS?").
- Responsiveness testing matrix (300px, 375px, 640px, 1024px, 1920px, 2560px).
- Security validation (e.g., "Unauthenticated user cannot access /dashboard?").

## 6. Sprint Completion Criteria

What must be visible:
- Landing page with Premium Midnight theme and entrance animations.
- Signup page with green toast notification on success.
- Login page with redirect to /dashboard on success.
- Dashboard navbar showing user identity (parsed from email).

What must be blocked:
- Unauthenticated access to /dashboard and /profile.

What must be validated:
- JWT flow works end-to-end (signup → login → protected route).
- All animations run at 60 FPS.
- No horizontal scrolling at any viewport (300px–2560px).

## Response snapshot

Sprint 1 implementation plan created successfully with comprehensive architecture and task breakdown.

**Plan Structure**:

1. **Agent Responsibility Mapping**: Created detailed table showing clear ownership boundaries between @ui-auth-expert (structure, auth, responsive, accessibility) and @css-animation-expert (visual design, animations, glassmorphism, theme tokens)

2. **24 Ordered Tasks** organized in 5 phases:
   - **Phase 0: Infrastructure (T001-T003)** - Next.js 15 setup, FastAPI setup, monorepo validation
   - **Phase 1: Theme Foundation (T004-T005)** - Color tokens, glassmorphism base styles
   - **Phase 2: Landing Page (T006-T009)** - Structure → Visual → Animations → Auth redirect
   - **Phase 3: Authentication (T010-T016)** - Better Auth config, Signup/Login pages, Email parsing, Toast system
   - **Phase 4: Backend JWT (T017-T019)** - JWT middleware, Protected endpoint, CORS
   - **Phase 5: Integration (T020-T024)** - API client, Dashboard, Navbar, Route guards

3. **JWT Handshake Documentation**:
   - Better Auth issues JWT on frontend (httpOnly cookie recommended)
   - Authorization header: `Bearer <token>`
   - FastAPI validates with BETTER_AUTH_SECRET
   - Extract user_id from payload.sub
   - 401 on invalid/expired tokens

4. **Quality Gates**:
   - Constitution Compliance: 8 principles validated
   - Performance Validation: 60 FPS animations, LCP <2.5s, API p95 <500ms
   - Security Validation: JWT middleware, 401/403 responses, no credential exposure
   - Responsiveness Testing: Matrix for 300px, 375px, 640px, 1024px, 1920px, 2560px
   - Accessibility Validation: Keyboard navigation, ARIA labels, reduced motion

5. **Sprint Completion Criteria**:
   - **Visible**: Landing with animations, Signup with green toast, Login with redirect, Dashboard with navbar identity
   - **Blocked**: Unauthenticated /dashboard and /profile access
   - **Validated**: JWT flow, 60 FPS, no horizontal scroll

6. **Environment Setup**:
   - Frontend: Next.js 15, Better Auth, Framer Motion, Tailwind CSS, Sonner
   - Backend: FastAPI, SQLModel, python-jose[cryptography], Neon PostgreSQL driver
   - Environment: BETTER_AUTH_SECRET must match across layers

7. **Risk Mitigation**:
   - JWT secret mismatch → Document .env.local setup in both directories
   - Animation performance → GPU-accelerated properties only (transform, opacity)
   - Responsive layout breaks → Test all breakpoints before marking task complete
   - CORS issues → Configure origins explicitly in FastAPI

**Key Code Examples**:

**Color Token System (T004)**:
```typescript
// tailwind.config.ts
colors: {
  'midnight-bg': '#0F172A',
  'primary-violet': '#8B5CF6',
  'secondary-indigo': '#6366F1',
  'text-primary': '#FFFFFF',
  'text-secondary': '#94A3B8'
}
```

**JWT Validation Middleware (T017)**:
```python
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=["HS256"]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"user_id": int(user_id)}
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )
```

**Email Parsing Utility (T015)**:
```typescript
export function getDisplayName(user: {
  email: string;
  displayName?: string | null
}): string {
  if (user.displayName) return user.displayName;
  const username = user.email.split('@')[0];
  return username.charAt(0).toUpperCase() + username.slice(1);
}
```

**Plan Status**: Awaiting Architect Approval to Begin Task 1

## Outcome

- ✅ Impact: Created comprehensive Sprint 1 plan with 24 ordered tasks, explicit agent responsibility mapping, JWT handshake documentation, quality gates across 5 dimensions, and clear completion criteria for Landing & Authentication flows
- 🧪 Tests: No tests required (planning artifact)
- 📁 Files: Created plan.md with architecture, task breakdown, dependencies, risk mitigation, and handoff notes
- 🔁 Next prompts: User approval required before executing T001 (Initialize Frontend); subsequent implementation via /sp.tasks or manual task execution
- 🧠 Reflection: Plan successfully balances comprehensive detail with practical execution; agent boundaries prevent overlap; quality gates enforce constitution principles; Sprint 1 scope limited to Landing & Auth enables focused delivery

## Evaluation notes (flywheel)

- Failure modes observed: None - plan template not found but adapted successfully using constitution and spec as authoritative sources
- Graders run and results (PASS/FAIL): PASS - All constitution principles addressed, agent responsibilities clearly delineated, tasks have measurable acceptance criteria
- Prompt variant (if applicable): Full planning workflow with explicit agent capability mapping requirement
- Next experiment (smallest change to try): Validate JWT middleware implementation against Better Auth token format during T017 execution; consider documenting ADR for authentication architecture if significant tradeoffs emerge
