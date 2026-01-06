---
id: 001
title: Phase 2 Monorepo Constitution
stage: constitution
date: 2025-12-31
surface: agent
model: claude-sonnet-4-5
feature: none
branch: 001-todo-cli-mvp
user: system
command: /sp.constitution
labels: ["constitution", "governance", "security", "architecture", "full-stack"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

# Phase 2 Monorepo Constitution
## Full-Stack Todo Application

This document is the **highest authority** governing all agents, tools, and contributors.
All rules herein are **mandatory**, **non-optional**, and **enforced by design**.

Failure to comply constitutes a **critical violation**.

---

## 1. Monorepo Architecture (Immutable)

### JWT Handshake (Better Auth) — ZERO TRUST
- JWTs are issued by **Next.js via Better Auth**
- FastAPI MUST verify JWTs using `BETTER_AUTH_SECRET`
- Tokens must be validated on **every request**

---

### Mandatory Data Isolation (Critical Rule)
Every API endpoint and database query MUST:
- Extract `user_id` from a verified JWT
- Filter ALL queries by `user_id`

🚨 Any data access without verified user context is a **SEVERITY-1 VIOLATION**.

---

### Forbidden
- Public endpoints accessing user data
- Client-provided user IDs
- Trusting headers without verification

---

## 3. UI/UX & Responsive Mandate (Hebbia / OneText Standard)

### Responsiveness
- Supported widths: **300px → 2560px**
- Horizontal scrolling is **strictly forbidden**
- Layout must adapt fluidly, not via breakage

---

### Styling Responsibility Separation
- **@ui-auth-expert**
  - Builds layout structure, grids, spacing
  - Owns accessibility and responsiveness
  - Produces the **Bones**

- **@css-expert**
  - Applies visual design (glassmorphism, bento grids)
  - Adds Framer Motion animations
  - Produces the **Skin**

Neither agent may override the other's domain.

---

### Performance
- Animations limited to `transform` and `opacity`
- Must maintain **60 FPS**
- No layout thrashing or blocking animations

---

## 4. Development Workflow & Standards

### Spec-Driven Development (Non-Negotiable)
- All features MUST originate from `/specs`
- Any implementation without an updated spec is invalid
- Specs are the source of truth, not code

---

### API Contract Synchronization
- Backend and Frontend MUST coordinate via:
  - `specs/api/rest-endpoints.md`
- Breaking changes require spec updates first

---

### Type Safety
- Frontend: **100% TypeScript coverage**
- Backend: Strict Pydantic + SQLModel typing
- No implicit types
- No unchecked data flows

---

## 5. Enforcement Clause

If a conflict arises between:
- Code and this Constitution → **Constitution wins**
- Convenience and standards → **Standards win**
- Speed and correctness → **Correctness wins**

This document supersedes all other instructions.

## Response snapshot

Constitution created successfully with the following structure:

**Version**: 1.0.0 (Initial ratification)
**Ratified**: 2025-12-31
**Last Amended**: 2025-12-31

**Core Principles Established** (8 total):
1. **Monorepo Architecture** - Clean separation: frontend/ and backend/
2. **Zero Trust Security Model** - Better Auth JWT handshake with BETTER_AUTH_SECRET
3. **Mandatory Data Isolation** - All queries filtered by user_id (SEVERITY-1 violation if missing)
4. **UI/UX & Responsive Standards** - 300px-2560px support, no horizontal scroll
5. **Agent Responsibility Separation** - @ui-auth-expert (bones) vs @css-animation-expert (skin)
6. **Spec-Driven Development** - Features must originate from /specs
7. **API Contract Synchronization** - Frontend/backend coordination via contracts
8. **Type Safety** - 100% TypeScript, strict Pydantic/SQLModel

**Technology Stack Defined**:
- Frontend: Next.js 15 + TypeScript + Tailwind + Better Auth + Framer Motion
- Backend: FastAPI + Python 3.11+ + SQLModel + Neon Postgres + JWT (jose)
- Shared: BETTER_AUTH_SECRET, REST/JSON, ISO 8601 dates

**Performance Standards**:
- Frontend: LCP <2.5s, FID <100ms, CLS <0.1, 60 FPS animations, <200KB initial bundle
- Backend: p50 <100ms, p95 <300ms, p99 <500ms, indexed queries, no N+1

**Governance**:
- Amendment procedure with version bumping (semantic versioning)
- Compliance review requirements for all PRs
- Enforcement hierarchy: Constitution > Convenience, Standards > Speed, Correctness > Speed

**Templates Alignment**:
✅ plan-template.md: Constitution Check section aligns with principles
✅ spec-template.md: Requirements align with JWT/data isolation
✅ tasks-template.md: Test-driven approach aligns with principles

## Outcome

- ✅ Impact: Constitution v1.0.0 ratified - establishes governance foundation for Phase 2 full-stack development
- 🧪 Tests: No tests required (documentation)
- 📁 Files: Created .specify/memory/constitution.md (375 lines)
- 🔁 Next prompts: Feature specifications should reference constitution principles; /sp.plan should enforce Constitution Check gate
- 🧠 Reflection: Constitution successfully translates user's security and architecture requirements into enforceable principles with clear rationale, examples, and agent ownership

## Evaluation notes (flywheel)

- Failure modes observed: None - initial ratification successful
- Graders run and results (PASS/FAIL): PASS - All 8 principles clearly defined with enforcement mechanisms
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Validate constitution enforcement in first feature specification
