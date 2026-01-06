<!--
SYNC IMPACT REPORT - Constitution Update
=========================================
Version Change: 1.0.0 (NEW) → 1.0.0 (Initial ratification)
Ratification Date: 2025-12-31
Last Amended: 2025-12-31

Modified Principles:
- NEW: I. Monorepo Architecture
- NEW: II. Zero Trust Security Model
- NEW: III. Mandatory Data Isolation
- NEW: IV. UI/UX & Responsive Standards
- NEW: V. Agent Responsibility Separation
- NEW: VI. Spec-Driven Development
- NEW: VII. API Contract Synchronization
- NEW: VIII. Type Safety

Added Sections:
- Core Principles (8 principles defined)
- Technology Stack
- Performance Standards
- Governance

Removed Sections:
- None (initial constitution)

Templates Requiring Updates:
✅ Updated: .specify/templates/plan-template.md (Constitution Check section aligns)
✅ Updated: .specify/templates/spec-template.md (Requirements align with JWT/data isolation)
✅ Updated: .specify/templates/tasks-template.md (Test-driven tasks align with principles)

Follow-up TODOs:
- None
-->

# Full-Stack Todo Application Constitution

**Project**: Phase 2 Full-Stack Todo Application (Next.js + FastAPI + Neon)

This document is the **highest authority** governing all agents, tools, and contributors.
All rules herein are **mandatory**, **non-optional**, and **enforced by design**.

Failure to comply constitutes a **critical violation**.

---

## Core Principles

### I. Monorepo Architecture

**Rule**: The project MUST maintain a clean monorepo structure with frontend (Next.js) and backend (FastAPI) in separate root-level directories.

**Structure**:
```
frontend/          # Next.js 15 App Router
backend/           # FastAPI + SQLModel
.claude/           # Agent definitions and skills
specs/             # Feature specifications
```

**Rationale**: Clear separation of concerns enables independent development, testing, and deployment while maintaining tight integration through shared specifications. This structure supports the agent-based workflow where specialized agents own specific layers.

**Enforcement**: All file operations MUST respect directory boundaries. Frontend code MUST NOT exist in backend/, and vice versa.

---

### II. Zero Trust Security Model (Better Auth)

**Rule**: Authentication MUST be handled exclusively by Next.js via Better Auth. JWTs are issued by the frontend and MUST be verified by FastAPI using the shared `BETTER_AUTH_SECRET` on **every request**.

**JWT Handshake Flow**:
1. User authenticates via Better Auth (Next.js)
2. Better Auth issues JWT with `user_id` claim
3. Frontend includes JWT in `Authorization: Bearer <token>` header
4. FastAPI validates JWT signature using `BETTER_AUTH_SECRET`
5. FastAPI extracts `user_id` from verified token
6. All operations execute within user context

**Rationale**: Centralized authentication in the frontend provides a single source of truth for user identity while enabling stateless verification in the backend. The shared secret ensures cryptographic verification without database lookups.

**Enforcement**:
- FastAPI MUST reject requests without valid JWT (401 Unauthorized)
- FastAPI MUST validate token signature before processing any request
- `BETTER_AUTH_SECRET` MUST be identical in frontend (.env.local) and backend (.env)
- Client-provided user IDs MUST be ignored; only JWT-derived `user_id` is trusted

---

### III. Mandatory Data Isolation (CRITICAL RULE)

**Rule**: Every API endpoint and database query MUST filter by `user_id` extracted from a verified JWT. No user MUST be able to access, modify, or delete data belonging to another user.

**Requirements**:
- ALL SQLModel queries MUST include `.where(Model.user_id == current_user.id)`
- ALL route handlers MUST use `Depends(get_current_user)` dependency injection
- Pagination, search, and filtering MUST maintain user isolation
- Aggregation queries MUST be scoped to the authenticated user

**Example (Correct)**:
```python
@router.get("/todos")
async def get_todos(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    todos = session.exec(
        select(Todo).where(Todo.user_id == current_user.id)
    ).all()
    return todos
```

**Example (VIOLATION)**:
```python
# ❌ SEVERITY-1 VIOLATION - Data leakage risk
@router.get("/todos")
async def get_todos(session: Session = Depends(get_session)):
    todos = session.exec(select(Todo)).all()  # Returns ALL users' todos
    return todos
```

**Rationale**: Data isolation is the cornerstone of multi-tenant security. A single violation can expose all user data. This principle enforces defense-in-depth by making user context mandatory at every layer.

**Enforcement**:
- Code reviews MUST verify user isolation on ALL database queries
- Integration tests MUST verify users cannot access each other's data
- The `@database-expert` agent MUST audit all queries for `user_id` filters
- The `/schema-enforcer` skill MUST flag missing user isolation

🚨 **Any data access without verified user context is a SEVERITY-1 VIOLATION.**

---

### IV. UI/UX & Responsive Standards (Hebbia/OneText Inspired)

**Rule**: All UI components MUST be fully functional and visually coherent across viewport widths from **300px to 2560px**.

**Requirements**:
- Horizontal scrolling is **strictly forbidden**
- Layouts MUST adapt fluidly using Tailwind CSS responsive utilities
- Touch targets MUST be minimum 44x44px on mobile
- Text MUST be readable (min 14px) at all sizes
- Images MUST scale proportionally without distortion

**Responsive Breakpoints** (Tailwind CSS):
- Mobile: 300px - 639px (default)
- Tablet: 640px - 1023px (`sm:`)
- Desktop: 1024px - 1919px (`md:`, `lg:`, `xl:`)
- Wide Desktop: 1920px - 2560px (`2xl:`)

**Testing Requirements**: Every component MUST be tested at critical widths: 320px, 375px, 768px, 1024px, 1440px, 2560px.

**Rationale**: Modern applications serve users on diverse devices. Breakage at any viewport size creates a poor user experience and reflects poorly on product quality. Mobile-first responsive design ensures accessibility for all users.

**Enforcement**:
- The `@ui-auth-expert` agent owns responsive implementation
- The `/responsive-validator` skill audits all components
- CI/CD MUST include visual regression tests at multiple viewports

---

### V. Agent Responsibility Separation

**Rule**: Frontend structure/accessibility and visual design are separate concerns owned by different specialized agents. Agents MUST NOT override each other's domain.

**Agent Domains**:

**@ui-auth-expert** (Produces the "Bones"):
- Layout structure (grids, flexbox, containers)
- Spacing and alignment
- Accessibility (ARIA, semantic HTML, keyboard navigation)
- Responsive behavior (breakpoints, mobile-first)
- Better Auth integration
- JWT client configuration

**@css-animation-expert** (Produces the "Skin"):
- Visual design (glassmorphism, gradients, shadows)
- Framer Motion animations
- Micro-interactions and transitions
- Brand aesthetics (Hebbia/OneText-inspired)
- Color schemes and theming

**Rationale**: Separating structural concerns from visual design enables parallel work and reduces conflicts. The @ui-auth-expert ensures functional correctness and accessibility, while @css-animation-expert adds visual polish without breaking functionality.

**Enforcement**:
- Structural changes (HTML, layout, responsiveness) → `@ui-auth-expert`
- Visual enhancements (animations, styling, effects) → `@css-animation-expert`
- Both agents MUST coordinate through the `@logic-coordinator` for cross-cutting changes

---

### VI. Spec-Driven Development (Non-Negotiable)

**Rule**: All features MUST originate from a specification in `/specs/<feature-name>/spec.md`. No implementation MUST occur without an approved specification.

**Workflow**:
1. User describes feature intent
2. `/sp.specify` creates `spec.md` with user stories and requirements
3. `/sp.plan` creates `plan.md` with architecture and design
4. `/sp.tasks` creates `tasks.md` with implementation tasks
5. Implementation follows `tasks.md` strictly
6. Specs are updated if requirements change during implementation

**Specification Structure**:
```
specs/<feature-name>/
├── spec.md          # User stories, requirements, acceptance criteria
├── plan.md          # Architecture, technical decisions, structure
├── tasks.md         # Granular implementation tasks
└── contracts/       # API contracts (if applicable)
```

**Rationale**: Specifications serve as the single source of truth for what needs to be built and why. Spec-driven development prevents scope creep, misaligned implementations, and wasted effort. It enables asynchronous collaboration and provides a clear audit trail.

**Enforcement**:
- Features without specs MUST be rejected in code review
- Breaking changes MUST update specs before implementation
- Specs are the source of truth; code reflects specs, not vice versa

---

### VII. API Contract Synchronization

**Rule**: Frontend and backend MUST coordinate through explicit API contracts documented in `specs/api/rest-endpoints.md`. Breaking changes MUST update contracts before implementation.

**Contract Requirements**:
- Endpoint path and HTTP method
- Request schema (headers, body, query params)
- Response schema (success and error cases)
- Authentication requirements (JWT mandatory/optional)
- User isolation guarantees (which fields are filtered)

**Example Contract**:
```markdown
### GET /api/todos

**Authentication**: Required (JWT)
**Authorization**: User can only access their own todos

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "title": "Buy groceries",
    "completed": false,
    "user_id": 42,
    "created_at": "2024-10-15T10:30:00Z"
  }
]
```

**Errors**:
- 401: Invalid or missing JWT
- 500: Server error
```

**Rationale**: API contracts prevent frontend/backend misalignment and enable parallel development. They serve as a versioned agreement between layers and facilitate automated testing.

**Enforcement**:
- Breaking changes MUST increment API version
- The `@logic-coordinator` agent MUST verify contract compliance
- Integration tests MUST validate request/response schemas against contracts

---

### VIII. Type Safety

**Rule**: Both frontend and backend MUST enforce strict static typing with zero tolerance for implicit types or unchecked data flows.

**Frontend (TypeScript)**:
- 100% TypeScript coverage (no `.js` files except config)
- `strict: true` in `tsconfig.json`
- No `any` types except in explicitly justified cases
- Props interfaces for all components
- API response types matching backend schemas

**Backend (Python)**:
- Pydantic models for all request/response bodies
- SQLModel for all database entities
- Type hints on all functions and methods
- mypy strict mode in CI/CD

**Rationale**: Type safety catches entire classes of bugs at compile time, improves IDE autocomplete, and serves as living documentation. It reduces runtime errors and makes refactoring safer.

**Enforcement**:
- TypeScript errors MUST fail the build
- mypy errors MUST fail CI/CD
- Code reviews MUST reject untyped code

---

## Technology Stack

### Frontend
- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS
- **Authentication**: Better Auth
- **Animations**: Framer Motion
- **State**: React hooks + Context API
- **API Client**: Fetch API with JWT interceptor

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **ORM**: SQLModel
- **Database**: Neon Postgres (serverless)
- **Auth**: JWT verification (jose library)
- **Validation**: Pydantic v2

### Shared
- **Auth Secret**: `BETTER_AUTH_SECRET` (environment variable)
- **API Protocol**: REST (JSON)
- **Date Format**: ISO 8601

---

## Performance Standards

### Frontend
- **Core Web Vitals**:
  - LCP (Largest Contentful Paint): <2.5s
  - FID (First Input Delay): <100ms
  - CLS (Cumulative Layout Shift): <0.1
- **Animations**: GPU-accelerated only (`transform`, `opacity`)
- **Frame Rate**: 60 FPS maintained during all animations
- **Bundle Size**: <200KB initial, <500KB total (gzipped)

### Backend
- **API Response Times**:
  - p50: <100ms
  - p95: <300ms
  - p99: <500ms
- **Database Queries**: Indexed on `user_id`, no N+1 queries
- **Concurrency**: Support 100+ concurrent users per worker

### Enforcement
- Lighthouse CI MUST enforce frontend performance budgets
- API monitoring MUST track p95/p99 latency
- The `/performance-optimizer` skill audits both layers

---

## Governance

### Amendment Procedure
1. Propose change with rationale and impact analysis
2. Update this constitution with version bump
3. Identify affected templates and update them
4. Create migration plan if code changes required
5. Document in PHR under `history/prompts/constitution/`

### Versioning Policy
- **MAJOR**: Backward-incompatible principle removals or redefinitions
- **MINOR**: New principles added or material expansions
- **PATCH**: Clarifications, wording fixes, non-semantic refinements

### Compliance Review
- All PRs MUST verify compliance with constitution principles
- The `/sp.plan` command MUST include "Constitution Check" gate
- Violations MUST be documented and justified in `plan.md` Complexity Tracking section

### Enforcement Hierarchy

If a conflict arises between:
- **Code and Constitution** → Constitution wins
- **Convenience and Standards** → Standards win
- **Speed and Correctness** → Correctness wins

This constitution supersedes all other instructions, guidelines, and preferences.

---

**Version**: 1.0.0 | **Ratified**: 2025-12-31 | **Last Amended**: 2025-12-31
