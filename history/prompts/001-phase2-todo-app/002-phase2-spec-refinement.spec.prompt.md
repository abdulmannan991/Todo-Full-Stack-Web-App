---
id: 002
title: Phase 2 Spec Visual Refinement
stage: spec
date: 2025-12-31
surface: agent
model: claude-sonnet-4-5
feature: 001-phase2-todo-app
branch: 001-phase2-todo-app
user: system
command: /sp.specify
labels: ["specification", "refinement", "visual-identity", "ux-flow", "premium-midnight", "toast-notifications"]
links:
  spec: specs/001-phase2-todo-app/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-phase2-todo-app/spec.md
  - specs/001-phase2-todo-app/checklists/requirements.md
tests:
  - none
---

## Prompt

# Role: Project Architect
# Goal: Update and finalize Phase 2 Project Overview Specification

This is a refinement of the existing Phase 2 spec.
Merge the following updates into the current specification,
resolve any conflicts, and produce a single finalized version.
Do not remove existing constraints unless explicitly overridden.

## 1. Visual Identity (Premium Midnight Aesthetic)

- **Primary Theme**: High-end SaaS "Midnight" look inspired by Hebbia/OneText.
- **Background**: Deep Slate/Navy (#0F172A) with radial gradients.
- **Accents**: Electric Violet (#8B5CF6) and Indigo (#6366F1) for buttons, progress bars, and glows.
- **Text**: Crisp White (#FFFFFF) for headers; muted Silver (#94A3B8) for body text.
- **Surface**: Glassmorphic cards (backdrop-blur-md) with 10% white borders.

## 2. Mandatory User Flow & Redirections

- **Landing Page**: Features a "Get Started" button that leads to Signup.
- **Auth Sequence**:
    1. **Signup**: User registers. On success, show a Green Toast and redirect to `/login`.
    2. **Login**: User enters credentials. On success, redirect to `/dashboard`.
- **Dashboard Identity**: Navbar must display the profile icon and the user's name (parsed from email prefix: `abc@gmail.com` -> `abc`).

## 3. Core Functional Requirements

- **Task Management**: Full CRUD in a clean, card-based dashboard layout.
- **Profile (/profile)**: Dedicated page for image uploads, account info, and "Member since" metadata.
- **Persistence**: All data stored in Neon DB, secured by JWT, and strictly filtered by authenticated user_id.

## Response snapshot

Specification refinement completed successfully. Updated existing `001-phase2-todo-app` specification with enhanced visual identity and UX flow details.

**Updates Applied**:

1. **New User Story 0**: Landing Page and Onboarding (P1)
   - Added landing page with "Get Started" button
   - Redirect flow: `/` → `/signup` → `/login` (with toast) → `/dashboard`

2. **Enhanced Visual Identity** (Premium Midnight - Hebbia/OneText-Inspired):
   - Background: Deep Slate/Navy (#0F172A) with radial gradients
   - Accents: Electric Violet (#8B5CF6) and Indigo (#6366F1)
   - Text: Crisp White (#FFFFFF) headers, Muted Silver (#94A3B8) body
   - Surface: Glassmorphic cards with backdrop-blur-md and 10% white borders

3. **Toast Notification System**:
   - Green success toast: "Account created successfully!" (on signup)
   - Red error toast: Authentication failures
   - Toast notifications for all critical actions

4. **Navigation Bar Identity**:
   - Profile icon display
   - User name parsed from email prefix (e.g., "abc@gmail.com" → "abc")

5. **Updated Requirements**:
   - Added 10 new functional requirements (FR-001 to FR-017 for Landing, Auth, Toast, Navbar)
   - Updated visual design requirements with specific color hex codes
   - Refined user acceptance scenarios with explicit redirect flows
   - Total: 45 functional requirements + 23 non-functional requirements (68 total)

6. **Authentication Flow Refinement**:
   - Signup → Green Toast + Redirect to /login
   - Login → Redirect to /dashboard
   - Dashboard navbar shows profile icon + parsed username

**Quality Validation**: ✅ ALL CHECKS PASSED
- Zero [NEEDS CLARIFICATION] markers
- All requirements testable and unambiguous
- Success criteria remain measurable and technology-agnostic
- Specification ready for `/sp.plan` phase

**Key Preserved Constraints**:
- One-way task status transition (Pending → Done only)
- Mandatory user_id filtering on all queries
- 300px-2560px responsive requirement
- 60 FPS animation constraint
- JWT-based authentication with Better Auth
- Profile image 2MB max, JPG/PNG only

## Outcome

- ✅ Impact: Enhanced specification with detailed visual identity (specific hex colors), complete UX flow (landing → signup with toast → login → dashboard with navbar), and 10 additional functional requirements
- 🧪 Tests: No tests required (documentation refinement)
- 📁 Files: Updated spec.md and requirements.md checklist
- 🔁 Next prompts: `/sp.plan` to generate implementation architecture with visual design patterns
- 🧠 Reflection: Successfully merged visual refinements into existing spec without removing constraints; specification now provides complete guidance for implementing Premium Midnight aesthetic and user flow

## Evaluation notes (flywheel)

- Failure modes observed: None - refinement successfully merged with existing spec
- Graders run and results (PASS/FAIL): PASS - All checklist items validated, no conflicts introduced
- Prompt variant (if applicable): Refinement/merge variant (update existing spec vs create new)
- Next experiment (smallest change to try): Validate visual design requirements against Tailwind CSS capabilities during planning phase
