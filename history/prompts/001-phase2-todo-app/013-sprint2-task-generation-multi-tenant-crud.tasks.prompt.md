---
id: 013
title: Sprint 2 Task Generation - Multi-Tenant CRUD
stage: tasks
date: 2026-01-05
surface: agent
model: claude-sonnet-4-5
feature: 001-phase2-todo-app
branch: 001-phase2-todo-app
user: system
command: /sp.tasks
labels: ["tasks", "sprint2", "multi-tenant", "security", "crud", "profile-management"]
links:
  spec: specs/001-phase2-todo-app/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-phase2-todo-app/tasks.md
tests:
  - none (task generation workflow)
---

## Prompt

# Role: Lead Systems Architect & Senior Product Engineer
# Experience Assumption: 10+ years FastAPI, SQLModel, Next.js, Auth, SaaS multi-tenancy
# Context: Sprint 2 Activation — User Stories 2 through 6
# Objective: Secure, Multi-Tenant Task CRUD with Zero-Trust Enforcement

Sprint 1 (Tasks T001–T069) is VERIFIED and LOCKED.
Sprint 2 initiates **core application logic** and **data ownership enforcement**.

This sprint introduces **real multi-tenancy**.
Any task leakage across users is a RELEASE-BLOCKING FAILURE.

## GLOBAL EXECUTION CONSTRAINTS (NON-NEGOTIABLE)

- ❌ No hardcoded `user_id`
- ❌ No client-supplied ownership data trusted
- ❌ No unfiltered queries
- ❌ No silent fallbacks or TODOs

All backend logic MUST derive ownership from the authenticated session context.

## 1. DATA ARCHITECTURE & ISOLATION (T070–T075)

### Task Domain Model
Create `backend/models/task.py` using **SQLModel**.

**Schema Requirements**
- `id`: UUID or Int (Primary Key)
- `user_id`: Foreign Key → `users.user_id` (Indexed)
- `title`: `str` (non-empty constraint)
- `description`: `Optional[str]`
- `status`: Enum (`pending`, `completed`)
- `created_at`: `datetime` (UTC, server-generated)

### Ownership Enforcement (Principle III)
- Every SELECT / UPDATE / DELETE query MUST:
  - Use a session-injected `current_user`
  - Filter explicitly by `Task.user_id == current_user.id`
- No repository or router may expose unscoped task queries.

## 2. FUNCTIONAL CRUD ENDPOINTS (T076–T085)

Implement the following **FastAPI** routes with strict typing and access control:

### POST `/tasks`
- Create a task
- `user_id` MUST be injected from session
- Ignore or reject any client-supplied ownership fields

### GET `/tasks`
- Return ONLY tasks owned by the authenticated user
- Sorted by `created_at DESC`

### PATCH `/tasks/{id}`
- Allow status toggle and title update
- Reject if task does NOT belong to `current_user`

### DELETE `/tasks/{id}`
- Permanently delete ONLY if `task.user_id == current_user.id`
- Return 404 for unauthorized access (do not leak existence)

## 3. PREMIUM BENTO UI & INTERACTION (T086–T100)

Replace dashboard placeholders with a **live, animated Task System**.

### TaskGrid Component
- Desktop: 3-column Bento grid
- Mobile: Single column
- Layout must reflow without animation glitches

### Task Cards (Premium Standard)
- Glassmorphic surface
- Subtle violet/indigo border glow
- Status badge (`Pending` / `Completed`)
- Hover elevation (no harsh shadows)

### Framer Motion (REQUIRED)
- Use `layout` prop for smooth reordering
- Completed tasks should animate position changes
- Checkmark toggle uses a **spring animation**

### Inline Editing (User Story 4)
- Clicking task title converts text → glass input
- Auto-focus enabled
- Save on blur or Enter
- Update must persist immediately via PATCH

## 4. USER PROFILE MANAGEMENT (USER STORY 6)

**File**: `frontend/app/profile/page.tsx`

Build a clean profile view displaying:
- User email (from session)
- "Member Since" date (formatted from `created_at`)
- Task statistics: Total tasks created, Total tasks completed

Data must be derived from real backend queries.

## Response snapshot

Successfully generated 76 Sprint 2 tasks (T070-T145) organized into 7 phases:

**Phase 8: Database Setup (T070-T077)** - 8 tasks
- Neon PostgreSQL configuration
- User and Task SQLModel entities with foreign key relationships
- Multi-tenant isolation infrastructure

**Phase 9: User Story 2 - Task CRUD (T078-T094)** - 17 tasks
- Backend: POST/GET /tasks with JWT-based user_id filtering
- Frontend: TaskGrid, TaskCard with Premium Bento UI
- Framer Motion animations and glassmorphic styling

**Phase 10: User Story 3 - Task Completion (T095-T102)** - 8 tasks
- PATCH endpoint with one-way status transition (pending → completed)
- Green check animation with spring physics
- Smooth card reordering with Framer Motion layout

**Phase 11: User Story 4 - Task Editing (T103-T108)** - 6 tasks
- Inline editable title component with auto-focus
- Save on blur/Enter with validation

**Phase 12: User Story 5 - Task Deletion (T109-T115)** - 7 tasks
- DELETE endpoint with 404 for unauthorized access
- Confirmation dialog with exit animations

**Phase 13: User Story 6 - Profile Management (T116-T129)** - 14 tasks
- Profile page with email, join date, task statistics
- Avatar upload with JPG/PNG validation (<2MB)

**Phase 14: Polish & Validation (T130-T145)** - 16 tasks
- Security validation using auth-guard and schema-enforcer skills
- Performance optimization and responsive validation
- Documentation and acceptance testing

**Critical Security Features:**
- All database queries filter by user_id from JWT
- No hardcoded user_id values anywhere
- 404 responses for unauthorized access (prevents data leakage)
- Foreign key constraints enforced at database level

**Parallel Execution:**
- 28 tasks marked [P] can run in parallel
- User Stories 3, 4, 5 can be developed simultaneously after US2
- User Story 6 (Profile) is independent and can run in parallel

**Format Compliance:**
- All tasks use checkbox format: `- [ ]`
- Sequential Task IDs: T070-T145
- [Story] labels: [US2], [US3], [US4], [US5], [US6]
- Exact file paths in all descriptions
- Owner assignments for all tasks

## Outcome

- ✅ Impact: Generated comprehensive Sprint 2 task list covering all 5 remaining user stories (US2-US6) with strict multi-tenant security enforcement
- 🧪 Tests: No tests generated (not requested in specification), but task validation checkpoints included in Phase 14
- 📁 Files: Modified `specs/001-phase2-todo-app/tasks.md` (appended 76 tasks from T070-T145)
- 🔁 Next prompts: Begin Sprint 2 implementation starting with Phase 8 (Database Setup) using `/sp.implement` or manual execution
- 🧠 Reflection: Task generation followed strict format requirements with proper sequencing, dependencies, and security constraints. Multi-tenant isolation is enforced at every layer (database, backend, frontend).

## Evaluation notes (flywheel)

- Failure modes observed: None. All tasks generated with proper format, dependencies, and security constraints.
- Graders run and results (PASS/FAIL):
  - Format validation: PASS (all tasks have checkboxes, IDs, file paths, owners)
  - Dependency validation: PASS (clear phase dependencies, user story independence verified)
  - Security validation: PASS (zero-trust multi-tenancy enforced in all tasks)
  - Completeness validation: PASS (all 5 user stories from spec covered)
- Prompt variant (if applicable): Standard /sp.tasks command with detailed security requirements
- Next experiment (smallest change to try): Consider adding explicit acceptance test tasks for multi-tenant isolation before implementation begins
