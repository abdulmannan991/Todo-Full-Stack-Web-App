# Implementation Plan: Phase 2 Sprint 1 – Landing & Authentication

**Branch**: `001-phase2-todo-app` | **Date**: 2025-12-31 | **Spec**: [spec.md](spec.md)
**Input**: Phase 2 Project Overview Specification + Constitution v1.0.0

---

## Executive Summary

**Sprint 1 Scope**: Establish monorepo infrastructure, implement Premium Midnight visual system foundations, build landing page with motion, and complete secure authentication flow (Signup → Login → JWT validation → Dashboard).

**Duration Estimate**: 5-7 implementation sessions (not including this planning phase)

**Key Deliverables**:
1. Monorepo structure (`frontend/`, `backend/`) with Next.js 15 + FastAPI
2. Global Premium Midnight color token system
3. Landing page (`/`) with Framer Motion entrance animations
4. Signup flow with green toast notification and redirect to login
5. Login flow with JWT issuance and redirect to dashboard
6. JWT validation middleware in FastAPI
7. Email-prefix parsing for display names
8. Protected route guards (`/dashboard`, `/profile`)

---

## 1. Agent Responsibility Mapping (Mandatory)

### @ui-auth-expert (Produces the "Bones")

**Owns**:
- Page structure and layout (HTML semantic elements)
- Routing configuration (Next.js App Router)
- Component composition and hierarchy
- Form structure and validation logic
- Better Auth integration and configuration
- JWT client-side handling (token storage, Authorization headers)
- Responsive layout implementation (300px-2560px)
- Accessibility (ARIA labels, keyboard navigation, semantic HTML)
- State management (React hooks, Context API)
- API client setup with JWT interceptor
- Route protection logic (redirect unauthenticated users)
- Email-prefix parsing utility for display names

**Produces**:
- `/frontend/app/` directory structure (pages)
- `/frontend/components/` (functional UI components)
- `/frontend/lib/auth.ts` (Better Auth config, JWT utilities)
- `/frontend/lib/api-client.ts` (fetch wrapper with JWT headers)
- `/frontend/utils/profile.ts` (email parsing logic)
- `/frontend/middleware.ts` (route guards)
- Tailwind utility classes for spacing, layout, flexbox

**Handoff Point**: Completes structural HTML with Tailwind utility classes for layout. Hands off to @css-animation-expert for visual enhancement (colors, glassmorphism, animations).

**Does NOT Touch**:
- Visual styling (colors, glassmorphism, shadows, gradients)
- Framer Motion animation definitions
- Theme token values (reads tokens, does not define)

---

### @css-animation-expert (Produces the "Skin")

**Owns**:
- Visual design system (Premium Midnight theme)
- Global color token definition (CSS custom properties or Tailwind config)
- Glassmorphism implementation (backdrop-blur, borders, shadows)
- Framer Motion animation definitions (variants, transitions)
- Micro-interactions (button hover, focus states)
- Toast notification styling
- Gradient backgrounds (radial, linear)
- Typography styling (font weights, sizes, line heights)
- Visual feedback animations (green check on task complete, etc.)

**Produces**:
- `/frontend/app/globals.css` (color tokens, theme definitions)
- `/frontend/tailwind.config.ts` (extended color palette)
- `/frontend/lib/motion-variants.ts` (reusable Framer Motion variants)
- `/frontend/components/ui/Toast.tsx` (styled toast component)
- Tailwind classes for colors, shadows, effects

**Handoff Point**: Receives structural components from @ui-auth-expert. Applies visual enhancements without modifying HTML structure or functionality.

**Does NOT Touch**:
- Page routing or navigation logic
- Form validation or submission logic
- Better Auth configuration
- API calls or data fetching
- Component structure or hierarchy

---

### Responsibility Boundaries

| Concern | @ui-auth-expert | @css-animation-expert |
|---------|-----------------|----------------------|
| HTML structure | ✅ Owns | ❌ Does not modify |
| Tailwind layout utilities (flex, grid, p-, m-) | ✅ Owns | ❌ Does not modify |
| Tailwind color/visual utilities (bg-, text-, shadow-) | ❌ Does not define | ✅ Owns |
| Form validation | ✅ Owns | ❌ Does not touch |
| Better Auth config | ✅ Owns | ❌ Does not touch |
| Framer Motion variants | ❌ Does not define | ✅ Owns |
| Toast notification logic | ✅ Owns (trigger) | ✅ Owns (styling) |
| Email parsing | ✅ Owns | ❌ Does not touch |
| Route guards | ✅ Owns | ❌ Does not touch |

**Conflict Resolution**: If a task requires both structural and visual work, @ui-auth-expert completes structure first, then @css-animation-expert enhances visuals.

---

## 2. Ordered Task Checklist

### Phase 0: Infrastructure Setup (Foundational - Blocks All Other Work)

#### T001 - Initialize Frontend (Next.js 15)
- **Owner**: @ui-auth-expert
- **Dependencies**: None
- **Description**: Create `/frontend` directory, initialize Next.js 15 with App Router, TypeScript, Tailwind CSS
- **Acceptance Criteria**:
  - [ ] `frontend/package.json` created with Next.js 15, React 18, TypeScript, Tailwind CSS dependencies
  - [ ] `frontend/tsconfig.json` with strict mode enabled
  - [ ] `frontend/tailwind.config.ts` initialized (basic setup, extended by @css-animation-expert later)
  - [ ] `frontend/app/layout.tsx` with basic HTML structure
  - [ ] `frontend/app/page.tsx` with placeholder landing page
  - [ ] `npm run dev` starts development server on `localhost:3000`
  - [ ] No TypeScript errors

#### T002 - Initialize Backend (FastAPI)
- **Owner**: @database-expert (if available) or @ui-auth-expert (fallback)
- **Dependencies**: None
- **Description**: Create `/backend` directory, initialize FastAPI with Python 3.11+, SQLModel, Pydantic v2
- **Acceptance Criteria**:
  - [ ] `backend/pyproject.toml` or `backend/requirements.txt` created with FastAPI, SQLModel, Pydantic, jose, python-dotenv dependencies
  - [ ] `backend/main.py` with basic FastAPI app initialization
  - [ ] `backend/.env.example` template created (includes `BETTER_AUTH_SECRET`, `DATABASE_URL`)
  - [ ] `uvicorn backend.main:app --reload` starts development server on `localhost:8000`
  - [ ] GET `/` returns 200 OK (health check endpoint)
  - [ ] No Python type errors (run `mypy backend/` if available)

#### T003 - Validate Monorepo Structure
- **Owner**: @logic-coordinator (if available) or @ui-auth-expert (fallback)
- **Dependencies**: T001, T002
- **Description**: Verify monorepo structure complies with Constitution Principle I
- **Acceptance Criteria**:
  - [ ] Directory structure matches constitution:
    ```
    /
    ├── frontend/
    ├── backend/
    ├── .claude/
    └── specs/
    ```
  - [ ] No frontend code exists in `backend/`
  - [ ] No backend code exists in `frontend/`
  - [ ] Both servers start independently

---

### Phase 1: Theme Foundation & Color Tokenization

#### T004 - Define Premium Midnight Color Tokens
- **Owner**: @css-animation-expert
- **Dependencies**: T001
- **Description**: Create global color token system in Tailwind config and CSS custom properties
- **Acceptance Criteria**:
  - [ ] `frontend/tailwind.config.ts` extended with custom colors:
    - `midnight-bg`: `#0F172A` (background)
    - `primary-violet`: `#8B5CF6` (primary accent)
    - `secondary-indigo`: `#6366F1` (secondary accent)
    - `text-primary`: `#FFFFFF` (headers, primary text)
    - `text-secondary`: `#94A3B8` (body text, muted)
  - [ ] `frontend/app/globals.css` includes CSS custom properties:
    ```css
    :root {
      --color-midnight-bg: #0F172A;
      --color-primary-violet: #8B5CF6;
      --color-secondary-indigo: #6366F1;
      --color-text-primary: #FFFFFF;
      --color-text-secondary: #94A3B8;
    }
    ```
  - [ ] Tokens accessible via Tailwind classes: `bg-midnight-bg`, `text-primary-violet`, etc.
  - [ ] No hardcoded hex values in component files (all use tokens)

#### T005 - Establish Glassmorphism Base Styles
- **Owner**: @css-animation-expert
- **Dependencies**: T004
- **Description**: Create reusable Tailwind classes and CSS for glassmorphic card effects
- **Acceptance Criteria**:
  - [ ] `frontend/app/globals.css` includes `.glass-card` utility class:
    ```css
    .glass-card {
      @apply backdrop-blur-md bg-white/10 border border-white/10 rounded-lg;
    }
    ```
  - [ ] Radial gradient background applied to `<body>` in `layout.tsx`
  - [ ] Background uses `bg-midnight-bg` with radial gradient overlay
  - [ ] Visual preview available at `/` (apply to landing page container)

---

### Phase 2: Landing Page Structure & Motion

#### T006 - Build Landing Page Layout (Structure Only)
- **Owner**: @ui-auth-expert
- **Dependencies**: T001, T003
- **Description**: Create semantic HTML structure for landing page with hero section and CTA
- **Acceptance Criteria**:
  - [ ] `frontend/app/page.tsx` created with structure:
    - Hero section (h1, subtitle, CTA button)
    - Application description section
    - Features grid (3-4 feature cards)
  - [ ] "Get Started" button implemented as `<Link href="/signup">`
  - [ ] Responsive layout using Tailwind flexbox/grid (300px-2560px)
  - [ ] Semantic HTML (`<main>`, `<section>`, `<h1>`, `<p>`, `<button>`)
  - [ ] No visual styling applied yet (Tailwind spacing/layout only)
  - [ ] Clicking "Get Started" navigates to `/signup` (even if signup page doesn't exist yet)

#### T007 - Apply Premium Midnight Visual Theme to Landing Page
- **Owner**: @css-animation-expert
- **Dependencies**: T004, T005, T006
- **Description**: Enhance landing page with Premium Midnight colors, glassmorphism, and gradients
- **Acceptance Criteria**:
  - [ ] Hero section uses `bg-midnight-bg` with radial gradient
  - [ ] Feature cards use `.glass-card` class
  - [ ] "Get Started" button uses `bg-primary-violet` with `hover:bg-secondary-indigo` transition
  - [ ] Headings use `text-text-primary` (white)
  - [ ] Body text uses `text-text-secondary` (muted silver)
  - [ ] Visual coherence matches spec: dark background, high contrast, glassmorphic surfaces

#### T008 - Implement Landing Page Entrance Animations
- **Owner**: @css-animation-expert
- **Dependencies**: T001 (Framer Motion installed), T007
- **Description**: Add Framer Motion staggered entrance animations to landing page elements
- **Acceptance Criteria**:
  - [ ] `frontend/lib/motion-variants.ts` created with reusable variants:
    - `fadeInUp`: opacity 0→1, y 20→0
    - `staggerContainer`: staggerChildren: 0.1s
  - [ ] Hero section animates on page load (fade in from bottom)
  - [ ] Feature cards stagger in (each delayed by 0.1s)
  - [ ] CTA button animates after hero section (final element)
  - [ ] Animations use GPU-accelerated properties only (`transform`, `opacity`)
  - [ ] `useReducedMotion()` hook implemented to respect user preferences
  - [ ] Animation duration <600ms total (per constitution performance standards)

#### T009 - Authenticated User Redirect Logic
- **Owner**: @ui-auth-expert
- **Dependencies**: T006, T013 (Better Auth setup)
- **Description**: Redirect authenticated users from landing page to dashboard
- **Acceptance Criteria**:
  - [ ] `frontend/app/page.tsx` checks for active session on mount
  - [ ] If user is authenticated, `redirect('/dashboard')` is called
  - [ ] Unauthenticated users see landing page normally
  - [ ] No flash of landing page content for authenticated users (server-side redirect if possible)

---

### Phase 3: Authentication Infrastructure

#### T010 - Install and Configure Better Auth
- **Owner**: @ui-auth-expert
- **Dependencies**: T001
- **Description**: Install Better Auth, configure JWT plugin, set up authentication endpoints
- **Acceptance Criteria**:
  - [ ] Better Auth installed via npm: `better-auth` package
  - [ ] `frontend/lib/auth.ts` created with Better Auth configuration:
    - Database connection configured (if Better Auth requires it, or use in-memory for dev)
    - JWT plugin enabled with `secret` from `process.env.BETTER_AUTH_SECRET`
    - Email/password provider enabled
  - [ ] `BETTER_AUTH_SECRET` environment variable added to `frontend/.env.local`
  - [ ] API routes created at `frontend/app/api/auth/[...all]/route.ts` (Better Auth handler)
  - [ ] Better Auth client utility exported from `lib/auth.ts`

#### T011 - Create Signup Page Structure
- **Owner**: @ui-auth-expert
- **Dependencies**: T010
- **Description**: Build signup page with form structure, validation, and Better Auth integration
- **Acceptance Criteria**:
  - [ ] `frontend/app/signup/page.tsx` created with form:
    - Email input (type="email", required)
    - Password input (type="password", required, min 8 characters)
    - Confirm Password input (must match password)
    - Submit button
  - [ ] Client-side validation implemented:
    - Valid email format
    - Password min 8 characters
    - Passwords match
    - Display validation errors below inputs
  - [ ] Form submission calls Better Auth signup function
  - [ ] On success: Trigger green toast notification (see T016) and redirect to `/login`
  - [ ] On error: Display error message (red toast)
  - [ ] Loading state during submission (disable button, show spinner)

#### T012 - Apply Visual Styling to Signup Page
- **Owner**: @css-animation-expert
- **Dependencies**: T004, T011
- **Description**: Style signup form with Premium Midnight theme and glassmorphism
- **Acceptance Criteria**:
  - [ ] Form container uses `.glass-card` class
  - [ ] Input fields styled with dark theme:
    - Background: `bg-white/5`
    - Border: `border-white/10`
    - Text: `text-text-primary`
    - Placeholder: `text-text-secondary`
  - [ ] Submit button uses `bg-primary-violet` with hover effect
  - [ ] Form centered on page with responsive padding (300px-2560px)
  - [ ] Focus states visible (outline with `ring-primary-violet`)

#### T013 - Create Login Page Structure
- **Owner**: @ui-auth-expert
- **Dependencies**: T010
- **Description**: Build login page with form structure and Better Auth integration
- **Acceptance Criteria**:
  - [ ] `frontend/app/login/page.tsx` created with form:
    - Email input (type="email", required)
    - Password input (type="password", required)
    - Submit button
    - Link to signup page: "Don't have an account? Sign up"
  - [ ] Client-side validation (valid email format)
  - [ ] Form submission calls Better Auth login function
  - [ ] On success: Redirect to `/dashboard`
  - [ ] On error: Display red toast notification with error message
  - [ ] Loading state during submission

#### T014 - Apply Visual Styling to Login Page
- **Owner**: @css-animation-expert
- **Dependencies**: T004, T013
- **Description**: Style login form with Premium Midnight theme (consistent with signup)
- **Acceptance Criteria**:
  - [ ] Visual styling identical to signup page (T012)
  - [ ] Form container uses `.glass-card` class
  - [ ] Submit button uses `bg-primary-violet`
  - [ ] "Sign up" link styled with `text-primary-violet hover:text-secondary-indigo`

#### T015 - Email Prefix Parsing Utility
- **Owner**: @ui-auth-expert
- **Dependencies**: None (utility function)
- **Description**: Create utility function to parse display name from email prefix
- **Acceptance Criteria**:
  - [ ] `frontend/utils/profile.ts` created with function:
    ```typescript
    export function getDisplayName(user: { email: string; displayName?: string | null }): string {
      if (user.displayName) return user.displayName;
      const username = user.email.split('@')[0];
      return username.charAt(0).toUpperCase() + username.slice(1);
    }
    ```
  - [ ] Function handles edge cases:
    - Email without @ → returns "User"
    - Empty email → returns "User"
    - Capitalizes first letter of username
  - [ ] Unit tests written (if test setup exists)
  - [ ] Exported and ready for use in navbar

#### T016 - Toast Notification System
- **Owner**: @ui-auth-expert (logic), @css-animation-expert (styling)
- **Dependencies**: T001
- **Description**: Implement toast notification system for user feedback
- **Acceptance Criteria**:
  - [ ] Toast notification library installed (e.g., `sonner`, `react-hot-toast`) OR custom implementation
  - [ ] `frontend/components/ui/Toast.tsx` created with:
    - Green success variant (for "Account created successfully!")
    - Red error variant (for authentication failures)
    - Auto-dismiss after 5 seconds
    - Positioned top-right of viewport
  - [ ] Toast provider added to `layout.tsx`
  - [ ] Utility function `showToast(message, variant)` exported
  - [ ] Visual styling by @css-animation-expert:
    - Success: `bg-green-500/90` with white text
    - Error: `bg-red-500/90` with white text
    - Glassmorphism effect (backdrop-blur)
    - Slide-in animation from right

---

### Phase 4: Backend Authentication & JWT Validation

#### T017 - FastAPI JWT Validation Middleware
- **Owner**: @fastapi-jwt-guardian (if available) or @ui-auth-expert (fallback)
- **Dependencies**: T002, T010
- **Description**: Implement JWT validation dependency in FastAPI to verify tokens from Better Auth
- **Acceptance Criteria**:
  - [ ] `backend/auth.py` created with `get_current_user()` dependency:
    ```python
    from fastapi import Depends, HTTPException, status
    from fastapi.security import HTTPBearer
    from jose import JWTError, jwt

    security = HTTPBearer()

    async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
        token = credentials.credentials
        try:
            payload = jwt.decode(token, settings.BETTER_AUTH_SECRET, algorithms=["HS256"])
            user_id = payload.get("sub")
            if user_id is None:
                raise HTTPException(status_code=401, detail="Invalid token")
            return {"user_id": int(user_id)}
        except JWTError:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
    ```
  - [ ] `BETTER_AUTH_SECRET` environment variable added to `backend/.env` (MUST match frontend)
  - [ ] Dependency tested with mock JWT token
  - [ ] Returns 401 Unauthorized for missing/invalid tokens
  - [ ] Extracts `user_id` from JWT `sub` claim

#### T018 - Protected Route Example Endpoint
- **Owner**: @fastapi-jwt-guardian (if available) or @ui-auth-expert (fallback)
- **Dependencies**: T017
- **Description**: Create example protected endpoint to validate JWT auth flow
- **Acceptance Criteria**:
  - [ ] `backend/routers/users.py` created with endpoint:
    ```python
    @router.get("/me")
    async def get_current_user_info(current_user: dict = Depends(get_current_user)):
        return {"user_id": current_user["user_id"], "message": "Authenticated"}
    ```
  - [ ] Endpoint returns 401 without JWT
  - [ ] Endpoint returns 200 with valid JWT from Better Auth
  - [ ] Response includes `user_id` extracted from token

#### T019 - CORS Configuration
- **Owner**: @fastapi-jwt-guardian (if available) or @ui-auth-expert (fallback)
- **Dependencies**: T002
- **Description**: Configure CORS middleware to allow requests from Next.js frontend
- **Acceptance Criteria**:
  - [ ] CORS middleware added to `backend/main.py`:
    ```python
    from fastapi.middleware.cors import CORSMiddleware

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],  # Next.js dev server
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["Authorization", "Content-Type"],
    )
    ```
  - [ ] Frontend can successfully make authenticated requests to backend
  - [ ] Preflight OPTIONS requests handled correctly

---

### Phase 5: Frontend-Backend Integration

#### T020 - API Client with JWT Interceptor
- **Owner**: @ui-auth-expert
- **Dependencies**: T010, T017
- **Description**: Create API client utility that automatically includes JWT token in requests
- **Acceptance Criteria**:
  - [ ] `frontend/lib/api-client.ts` created with fetch wrapper:
    ```typescript
    export async function apiClient(url: string, options: RequestInit = {}) {
      const session = await getSession(); // Better Auth function
      const token = session?.accessToken;

      return fetch(`http://localhost:8000${url}`, {
        ...options,
        headers: {
          ...options.headers,
          'Authorization': token ? `Bearer ${token}` : '',
          'Content-Type': 'application/json',
        },
      });
    }
    ```
  - [ ] Function handles missing token (does not send Authorization header)
  - [ ] Function handles 401 responses (redirect to login)
  - [ ] Environment variable `NEXT_PUBLIC_API_URL` used for base URL

#### T021 - Protected Dashboard Page Placeholder
- **Owner**: @ui-auth-expert
- **Dependencies**: T020
- **Description**: Create placeholder dashboard page with route protection
- **Acceptance Criteria**:
  - [ ] `frontend/app/dashboard/page.tsx` created with:
    - Server-side authentication check (redirect to /login if not authenticated)
    - Displays user's parsed display name in heading
    - Placeholder text: "Task list coming in Sprint 2"
  - [ ] Unauthenticated users redirected to `/login`
  - [ ] Authenticated users see personalized greeting using `getDisplayName(user)`

#### T022 - Navbar Component with User Identity
- **Owner**: @ui-auth-expert
- **Dependencies**: T015, T021
- **Description**: Create navigation bar component displaying profile icon and username
- **Acceptance Criteria**:
  - [ ] `frontend/components/Navbar.tsx` created with:
    - Profile icon (avatar image or default SVG)
    - User's display name (parsed from email using T015 utility)
    - Logout button/link
  - [ ] Navbar included in `layout.tsx` for authenticated pages
  - [ ] Responsive design (300px-2560px): collapses on mobile, full on desktop
  - [ ] Only visible on `/dashboard` and `/profile` routes

#### T023 - Apply Visual Styling to Navbar
- **Owner**: @css-animation-expert
- **Dependencies**: T004, T022
- **Description**: Style navbar with Premium Midnight theme
- **Acceptance Criteria**:
  - [ ] Navbar background uses `bg-midnight-bg/80` with backdrop-blur (sticky header effect)
  - [ ] Profile icon has border `border-primary-violet`
  - [ ] Username text uses `text-text-primary`
  - [ ] Logout button uses `text-primary-violet hover:text-secondary-indigo`
  - [ ] Glassmorphism effect for navbar container

#### T024 - Route Guard Middleware
- **Owner**: @ui-auth-expert
- **Dependencies**: T010
- **Description**: Implement Next.js middleware to protect `/dashboard` and `/profile` routes
- **Acceptance Criteria**:
  - [ ] `frontend/middleware.ts` created with route protection logic:
    ```typescript
    export async function middleware(request: NextRequest) {
      const session = await getSession();
      const { pathname } = request.nextUrl;

      if ((pathname.startsWith('/dashboard') || pathname.startsWith('/profile')) && !session) {
        return NextResponse.redirect(new URL('/login', request.url));
      }

      return NextResponse.next();
    }
    ```
  - [ ] Unauthenticated access to `/dashboard` redirects to `/login`
  - [ ] Unauthenticated access to `/profile` redirects to `/login`
  - [ ] Public routes (`/`, `/signup`, `/login`) remain accessible

---

## 3. QA & Validation Checklist

### Constitution Compliance

#### ✅ Principle I: Monorepo Architecture
- [ ] `frontend/` and `backend/` exist as separate root directories
- [ ] No frontend code in `backend/`
- [ ] No backend code in `frontend/`
- [ ] Both services start independently

#### ✅ Principle II: Zero Trust Security Model
- [ ] Better Auth issues JWTs on frontend
- [ ] FastAPI validates JWT signature using `BETTER_AUTH_SECRET`
- [ ] `BETTER_AUTH_SECRET` identical in frontend/.env.local and backend/.env
- [ ] FastAPI returns 401 for missing/invalid JWTs
- [ ] User ID extracted from JWT `sub` claim only (not client-provided)

#### ✅ Principle III: Mandatory Data Isolation
- [ ] No database queries in Sprint 1 (deferred to Sprint 2)
- [ ] JWT validation middleware ready for future queries (T017)

#### ✅ Principle IV: UI/UX & Responsive Standards
- [ ] All pages tested at 300px, 375px, 768px, 1024px, 1440px, 2560px widths
- [ ] No horizontal scrolling at any viewport
- [ ] Touch targets ≥44x44px on mobile (buttons, links)
- [ ] Text readable (min 14px font size)

#### ✅ Principle V: Agent Responsibility Separation
- [ ] @ui-auth-expert completed structure before @css-animation-expert styling
- [ ] No overlap: @ui-auth-expert did not define color values
- [ ] No overlap: @css-animation-expert did not modify HTML structure

#### ✅ Principle VI: Spec-Driven Development
- [ ] All tasks reference requirements from spec.md
- [ ] No features implemented outside spec scope

#### ✅ Principle VII: API Contract Synchronization
- [ ] `/me` endpoint matches expected schema (returns user_id)
- [ ] CORS headers allow frontend-backend communication

#### ✅ Principle VIII: Type Safety
- [ ] Frontend: Zero TypeScript errors (`npm run type-check`)
- [ ] Backend: Zero mypy errors (if mypy configured)
- [ ] No `any` types in TypeScript code

### Performance Standards (from Constitution)

#### Frontend
- [ ] Lighthouse Performance score >90 (run on `/`)
- [ ] LCP (Largest Contentful Paint) <2.5s
- [ ] FID (First Input Delay) <100ms
- [ ] CLS (Cumulative Layout Shift) <0.1
- [ ] Animations maintain 60 FPS (tested in Chrome DevTools)
- [ ] Animations use only `transform` and `opacity` properties

#### Backend
- [ ] `/me` endpoint p95 latency <300ms (tested with 100 requests)
- [ ] Health check (`GET /`) responds <100ms

### Security Validation

- [ ] `BETTER_AUTH_SECRET` never exposed to client (not in frontend bundle)
- [ ] JWT validation happens on every protected API request
- [ ] Protected routes (`/dashboard`, `/profile`) redirect unauthenticated users to `/login`
- [ ] No CORS misconfiguration (only localhost:3000 allowed in dev)
- [ ] Password inputs use `type="password"` (masked)
- [ ] No console.log of sensitive data (tokens, passwords)

### Responsiveness Validation (300px - 2560px)

**Test Matrix**:

| Viewport | Width | Page | Validation |
|----------|-------|------|------------|
| Mobile S | 300px | Landing | No horizontal scroll, readable text, button tappable |
| Mobile M | 375px | Signup | Form fields full width, button centered, no overflow |
| Tablet | 768px | Login | Form max-width applied, centered layout |
| Desktop | 1024px | Dashboard | Navbar full, content centered with max-width |
| Wide | 2560px | Landing | Content max-width, no excessive whitespace stretching |

### Accessibility Validation

- [ ] All interactive elements keyboard navigable (Tab key)
- [ ] Forms have `<label>` elements associated with inputs
- [ ] Focus indicators visible (ring on focus)
- [ ] Color contrast WCAG 2.1 AA compliant (use contrast checker):
  - White (#FFFFFF) on Midnight (#0F172A): ✅ Pass
  - Primary Violet (#8B5CF6) on Midnight (#0F172A): Check ratio ≥4.5:1
  - Secondary Indigo (#6366F1) on Midnight (#0F172A): Check ratio ≥4.5:1
- [ ] Error messages announced to screen readers (aria-live regions)
- [ ] Semantic HTML used (`<main>`, `<nav>`, `<h1>`, `<form>`, `<button>`)

### Functional Validation

**Landing Page**:
- [ ] "Get Started" button redirects to `/signup`
- [ ] Authenticated users auto-redirect to `/dashboard`
- [ ] Entrance animations play on page load
- [ ] Reduced motion respected (animations disabled if user prefers reduced motion)

**Signup Flow**:
- [ ] Valid email/password creates account
- [ ] Green toast notification appears: "Account created successfully!"
- [ ] Redirect to `/login` after success
- [ ] Red toast notification appears on error
- [ ] Password mismatch prevented (confirm password validation)
- [ ] Empty fields prevent submission

**Login Flow**:
- [ ] Valid credentials log user in
- [ ] Redirect to `/dashboard` after success
- [ ] Red toast notification appears on invalid credentials
- [ ] User remains on `/login` page on error

**Dashboard**:
- [ ] Unauthenticated access redirects to `/login`
- [ ] Authenticated user sees personalized greeting
- [ ] Navbar displays profile icon and parsed username (e.g., "abc" from "abc@gmail.com")
- [ ] Logout button clears session and redirects to landing page

**JWT Flow**:
- [ ] Better Auth issues JWT on successful login
- [ ] JWT stored securely (httpOnly cookie or secure localStorage)
- [ ] FastAPI `/me` endpoint accepts JWT in `Authorization: Bearer <token>` header
- [ ] FastAPI returns 401 for missing token
- [ ] FastAPI returns 401 for invalid/expired token
- [ ] FastAPI returns 200 with `user_id` for valid token

---

## 4. Sprint 1 Completion Criteria

### What Must Be Visible

✅ **Landing Page (`/`)**:
- Premium Midnight theme (dark background, glassmorphic cards)
- Entrance animations (staggered fade-in)
- "Get Started" button navigates to `/signup`
- Authenticated users auto-redirect to `/dashboard`

✅ **Signup Page (`/signup`)**:
- Styled form with email/password/confirm password
- Client-side validation with error messages
- Green toast notification on success: "Account created successfully!"
- Redirect to `/login` on success
- Red toast notification on error

✅ **Login Page (`/login`)**:
- Styled form with email/password
- Client-side validation
- Redirect to `/dashboard` on success
- Red toast notification on error
- Link to signup page

✅ **Dashboard Page (`/dashboard`)**:
- Navbar with profile icon and parsed username
- Personalized greeting: "Welcome, [parsed name from email]!"
- Placeholder text: "Task list coming in Sprint 2"
- Logout button

### What Must Be Blocked

❌ **Unauthenticated Access**:
- Access to `/dashboard` without login → Redirect to `/login`
- Access to `/profile` without login → Redirect to `/login`

❌ **Invalid Authentication**:
- Missing JWT token to FastAPI → 401 Unauthorized
- Invalid JWT signature → 401 Unauthorized
- Expired JWT → 401 Unauthorized (if expiration enabled)

### What Must Be Validated

🔒 **Security**:
- JWT validation on every protected API request
- `BETTER_AUTH_SECRET` matches between frontend and backend
- No client-provided user IDs accepted (only JWT-derived)
- CORS restricted to `localhost:3000` (dev environment)

🎨 **Visual Design**:
- Premium Midnight color palette applied consistently
- Glassmorphism effect on cards and forms
- High contrast text (white on dark background)
- Button hover states with color transitions

⚡ **Performance**:
- All animations run at 60 FPS
- Landing page LCP <2.5s
- API latency p95 <300ms
- No layout shift (CLS <0.1)

📱 **Responsiveness**:
- All pages functional at 300px width (no horizontal scroll)
- Touch targets ≥44x44px on mobile
- Content readable at all viewport sizes (300px - 2560px)

♿ **Accessibility**:
- Keyboard navigation works on all forms
- Focus indicators visible
- Color contrast WCAG 2.1 AA compliant
- Screen reader compatible (semantic HTML, ARIA labels)

---

## 5. Dependencies & Environment Setup

### Frontend Dependencies (package.json)

```json
{
  "dependencies": {
    "next": "^15.0.0",
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "better-auth": "^latest",
    "framer-motion": "^11.0.0",
    "sonner": "^1.3.0"
  },
  "devDependencies": {
    "typescript": "^5.3.0",
    "@types/node": "^20.0.0",
    "@types/react": "^18.3.0",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0"
  }
}
```

### Backend Dependencies (requirements.txt)

```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
sqlmodel>=0.0.14
pydantic>=2.5.0
python-jose[cryptography]>=3.3.0
python-dotenv>=1.0.0
```

### Environment Variables

**Frontend (`.env.local`)**:
```
BETTER_AUTH_SECRET=your-secret-key-min-32-characters
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Backend (`.env`)**:
```
BETTER_AUTH_SECRET=your-secret-key-min-32-characters
DATABASE_URL=postgresql://user:pass@localhost/dbname
```

⚠️ **CRITICAL**: `BETTER_AUTH_SECRET` MUST be identical in both files.

---

## 6. Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| JWT secret mismatch between frontend/backend | High | Validate on startup; document setup in README; add startup check to log secrets match (first 8 chars only) |
| CORS misconfiguration blocking requests | High | Test frontend-backend communication early (T019, T020); add CORS preflight test |
| Animations causing layout shift | Medium | Use `will-change` sparingly; test CLS in Lighthouse; avoid animating layout properties |
| Email parsing edge cases (no @, empty) | Low | Implement fallback to "User" in T015; add unit tests |
| Better Auth configuration errors | Medium | Follow official Better Auth docs; test signup/login flow immediately after T010 |

---

## 7. Testing Strategy (Sprint 1 Scope)

### Manual Testing (Required)

**Signup Flow**:
1. Navigate to `/signup`
2. Enter invalid email → See validation error
3. Enter mismatched passwords → See validation error
4. Enter valid credentials → See green toast "Account created successfully!" → Redirect to `/login`

**Login Flow**:
1. Navigate to `/login`
2. Enter invalid credentials → See red toast error → Remain on `/login`
3. Enter valid credentials → Redirect to `/dashboard`

**Protected Routes**:
1. Open `/dashboard` in incognito (no session) → Redirect to `/login`
2. Login → Access `/dashboard` → See personalized greeting with parsed username

**Responsive Testing**:
1. Open Chrome DevTools → Device toolbar
2. Test at: 300px, 375px, 768px, 1024px, 1440px, 2560px
3. Verify no horizontal scroll, readable text, tappable buttons

### Automated Testing (Optional for Sprint 1, Recommended for Sprint 2)

- Unit tests for `getDisplayName()` utility (T015)
- Integration tests for JWT validation (T017)
- E2E tests for signup/login flow (Playwright)

---

## 8. Handoff Notes for Sprint 2

**Completed in Sprint 1**:
- ✅ Monorepo infrastructure
- ✅ Premium Midnight theme foundation
- ✅ Landing page with motion
- ✅ Signup/Login flow with JWT
- ✅ Protected route guards
- ✅ Navbar with user identity

**Deferred to Sprint 2**:
- Task CRUD operations (create, read, update, delete)
- Task completion flow (Pending → Done transition)
- Task list UI with card layout
- Green check animation on task complete
- Database setup (Neon PostgreSQL)
- SQLModel User and Task entities
- Profile page with image upload

**Known Limitations**:
- Dashboard placeholder (no task list yet)
- No database persistence (Better Auth may use in-memory or file-based storage for dev)
- Profile page (`/profile`) not implemented (protected but returns 404)

---

## Awaiting Architect Approval to Begin Task 1.

**Next Steps**:
1. Review this plan for completeness and accuracy
2. Confirm agent responsibility boundaries are clear
3. Approve Sprint 1 scope and task order
4. Authorize @ui-auth-expert to begin T001 (Initialize Frontend)

Once approved, implementation will proceed in task order (T001 → T024) with quality gates enforced at each phase.
