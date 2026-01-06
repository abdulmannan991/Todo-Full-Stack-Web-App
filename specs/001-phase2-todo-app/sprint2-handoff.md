# Sprint 2 Handoff Notes
**Feature**: Phase 2 Full-Stack Todo Application
**Sprint**: Sprint 2 - Task CRUD & Database Integration
**Handoff Date**: 2026-01-04

---

## Sprint 1 Completions

### ✅ Infrastructure
- [X] Monorepo structure (`frontend/`, `backend/`)
- [X] Next.js 15 + TypeScript frontend
- [X] FastAPI + Python backend
- [X] Environment configuration with shared `BETTER_AUTH_SECRET`

### ✅ Authentication System
- [X] Better Auth JWT integration
- [X] Signup flow with client validation
- [X] Login flow with error handling
- [X] Protected route middleware (`/dashboard`, `/profile`)
- [X] Logout functionality
- [X] Backend JWT validation (`GET /users/me`)
- [X] API client wrapper with auto JWT headers

### ✅ UI/UX
- [X] Premium Midnight theme (Tailwind + CSS vars)
- [X] Glassmorphism design system
- [X] Landing page with Bento grid layout
- [X] Responsive navbar with hamburger menu (300px-2560px)
- [X] Premium SaaS footer
- [X] Framer Motion animations (staggered, spring physics)
- [X] Toast notifications (sonner)

### ✅ Quality Assurance
- [X] Constitution compliance (all 8 principles)
- [X] TypeScript type safety (zero errors, no `any`)
- [X] Responsive validation (300px-2560px)
- [X] Accessibility (keyboard nav, WCAG AA contrast)
- [X] Security (JWT validation, CORS, secrets not exposed)

---

## Sprint 2 Scope

### User Stories to Implement

#### **User Story 2: Task Creation and Reading** (Priority: P1)
- **FR-007**: As a user, I want to create a new task so that I can track my work
- **FR-008**: As a user, I want to view all my tasks so that I can see what needs to be done

**Implementation Requirements**:
- Create `tasks` table in Neon PostgreSQL:
  ```sql
  CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
  );
  ```
- Implement `POST /tasks` endpoint (FastAPI)
- Implement `GET /tasks` endpoint with `user_id` filtering
- Add task list UI to dashboard
- Add "Create Task" form/modal
- Ensure data isolation (JWT `user_id` required)

#### **User Story 3: Task Completion** (Priority: P1)
- **FR-009**: As a user, I want to mark tasks as complete so that I can track my progress

**Implementation Requirements**:
- Implement `PATCH /tasks/{id}` endpoint
- Add toggle checkbox UI
- Optimistic UI updates with rollback on error
- Show completed tasks with visual distinction (strikethrough, opacity)

#### **User Story 4: Task Title Editing** (Priority: P2)
- **FR-010**: As a user, I want to edit task titles so that I can correct mistakes

**Implementation Requirements**:
- Implement `PUT /tasks/{id}` endpoint
- Add inline editing UI (click to edit)
- Client-side validation (title required, max 255 chars)
- Auto-save on blur

#### **User Story 5: Task Deletion** (Priority: P2)
- **FR-011**: As a user, I want to delete tasks so that I can remove completed or irrelevant items

**Implementation Requirements**:
- Implement `DELETE /tasks/{id}` endpoint
- Add delete button with confirmation dialog
- Soft delete vs hard delete decision

#### **User Story 6: User Profile Management** (Priority: P3)
- **FR-017**: As a user, I want to view my profile so that I can see my account information

**Implementation Requirements**:
- Create profile page UI (`/profile`)
- Display email, username, join date
- Profile image upload (future enhancement)

---

## Technical Prerequisites

### Database Setup (CRITICAL for Sprint 2)

1. **Create Neon PostgreSQL Database**:
   - Sign up at https://console.neon.tech
   - Create new project "flowtask-production"
   - Copy connection string

2. **Update Environment Variables**:
   ```env
   # backend/.env
   DATABASE_URL=postgresql://user:password@host/database?sslmode=require
   ```

3. **Run Better Auth Migrations**:
   ```bash
   # Better Auth will create necessary tables on first run
   # Verify tables: user, session, account
   ```

4. **Create Tasks Table**:
   ```bash
   # Use Neon SQL Editor or migrate script
   ```

5. **Update SQLModel Models**:
   ```python
   # backend/models.py
   from sqlmodel import SQLModel, Field
   from datetime import datetime

   class Task(SQLModel, table=True):
       id: int | None = Field(default=None, primary_key=True)
       user_id: int = Field(foreign_key="user.id")
       title: str = Field(max_length=255)
       completed: bool = Field(default=False)
       created_at: datetime = Field(default_factory=datetime.utcnow)
       updated_at: datetime = Field(default_factory=datetime.utcnow)
   ```

---

## API Contract Specifications

### Task Endpoints

```typescript
// POST /tasks
Request:
{
  "title": string (required, 1-255 chars)
}

Response: 201 Created
{
  "id": number,
  "user_id": number,
  "title": string,
  "completed": boolean,
  "created_at": string (ISO 8601),
  "updated_at": string (ISO 8601)
}

// GET /tasks
Response: 200 OK
{
  "tasks": [
    {
      "id": number,
      "user_id": number,
      "title": string,
      "completed": boolean,
      "created_at": string,
      "updated_at": string
    }
  ]
}

// PATCH /tasks/{id}
Request:
{
  "completed": boolean
}

Response: 200 OK
{
  "id": number,
  "completed": boolean,
  "updated_at": string
}

// PUT /tasks/{id}
Request:
{
  "title": string (required, 1-255 chars)
}

Response: 200 OK
{
  "id": number,
  "title": string,
  "updated_at": string
}

// DELETE /tasks/{id}
Response: 204 No Content
```

### Authentication Header (All Endpoints)
```
Authorization: Bearer <jwt-token>
```

### Error Responses
```typescript
// 401 Unauthorized
{
  "detail": "Could not validate credentials"
}

// 403 Forbidden (user_id mismatch)
{
  "detail": "Not authorized to access this resource"
}

// 404 Not Found
{
  "detail": "Task not found"
}

// 422 Validation Error
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Frontend Components to Build

### Dashboard Page (`app/dashboard/page.tsx`)
```tsx
// Replace placeholder with:
- Task list component
- "Create Task" button
- Empty state ("No tasks yet")
- Loading states
- Error boundaries
```

### Task List Component (`components/TaskList.tsx`)
```tsx
// Features:
- Render all tasks
- Toggle completion checkbox
- Inline title editing
- Delete button with confirmation
- Optimistic UI updates
- Sort by created_at DESC
```

### Create Task Form (`components/CreateTaskForm.tsx`)
```tsx
// Features:
- Input field with validation
- Submit button
- Loading state
- Error handling
- Auto-focus on mount
```

---

## Data Isolation Requirements (CRITICAL)

**Constitution Principle III**: ALL database queries MUST filter by `user_id` from JWT.

### Backend Pattern (REQUIRED)
```python
from fastapi import Depends
from auth import get_current_user

@router.get("/tasks")
async def get_tasks(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    # CRITICAL: ALWAYS filter by user_id
    tasks = session.exec(
        select(Task).where(Task.user_id == user_id)
    ).all()
    return {"tasks": tasks}
```

**NEVER** accept `user_id` from client input. **ALWAYS** extract from JWT.

---

## Performance Optimizations

### High Priority
1. **Bundle Splitting**:
   - Enable Next.js code splitting for Framer Motion
   - Lazy load dashboard components
   - Target LCP <2.5s

2. **Database Indexing**:
   ```sql
   CREATE INDEX idx_tasks_user_id ON tasks(user_id);
   CREATE INDEX idx_tasks_created_at ON tasks(created_at);
   ```

3. **API Response Caching**:
   - Implement React Query / SWR for task list
   - Stale-while-revalidate pattern

### Medium Priority
4. **Optimistic UI**:
   - Immediate task creation feedback
   - Rollback on API error

5. **Pagination**:
   - Implement cursor-based pagination for task list
   - Load 50 tasks per page

---

## Testing Strategy (New for Sprint 2)

### Unit Tests
- **Backend**: pytest for all endpoints
- **Frontend**: Jest + React Testing Library for components

### Integration Tests
- Task CRUD flow end-to-end
- JWT validation across all endpoints
- Data isolation verification

### E2E Tests
- Playwright tests for critical paths:
  - Create task → Toggle completion → Delete
  - User A cannot see User B's tasks

---

## Known Issues from Sprint 1

### 🐛 To Fix in Sprint 2
1. **Performance**: Lighthouse 77/100 (target: >90)
   - LCP 3.8s needs optimization
   - Bundle size reduction required

2. **Database**: In-memory session storage
   - Migrate to Neon PostgreSQL
   - Implement session persistence

3. **Mobile UX**: Hamburger menu implemented but untested at 300px
   - Manual testing required

---

## Sprint 2 Success Criteria

### Definition of Done
- [ ] All 5 user stories implemented (US2-US6)
- [ ] Database connected to Neon PostgreSQL
- [ ] All CRUD endpoints functional
- [ ] Data isolation verified (user A cannot access user B's tasks)
- [ ] TypeScript zero errors
- [ ] Responsive 300px-2560px verified
- [ ] Lighthouse Performance >85 (target >90)
- [ ] Unit test coverage >80%
- [ ] E2E tests passing

### Acceptance Tests
1. Create task → Appears in list
2. Toggle completion → Visual update + persisted in DB
3. Edit title → Updates immediately
4. Delete task → Removed from list
5. Logout + login → Tasks still present
6. Second user cannot see first user's tasks

---

## Dependencies & Blockers

### External Dependencies
- Neon PostgreSQL account and database
- Better Auth database migrations

### Potential Blockers
- Database schema changes requiring migrations
- JWT claim structure (ensure `sub` contains user ID)

---

## Resources

### Documentation
- Neon PostgreSQL Docs: https://neon.tech/docs
- Better Auth Database Adapter: https://www.better-auth.com/docs/database
- SQLModel Guide: https://sqlmodel.tiangolo.com/

### Sprint 1 Artifacts
- Completion Report: `specs/001-phase2-todo-app/sprint1-completion-report.md`
- Technical Spec: `specs/001-phase2-todo-app/spec.md`
- Implementation Plan: `specs/001-phase2-todo-app/plan.md`
- Task Breakdown: `specs/001-phase2-todo-app/tasks.md`

---

## Next Steps (Immediate Actions)

1. **Week 1**: Database setup + Task model + GET/POST endpoints
2. **Week 2**: Dashboard UI + Task list component
3. **Week 3**: Update/Delete endpoints + Inline editing UI
4. **Week 4**: Profile page + Testing + Performance optimization

---

**Sprint 2 Kickoff**: Ready to begin ✅
**Estimated Completion**: 4 weeks
**Priority**: P1 (High)
