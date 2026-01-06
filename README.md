# FlowTask - Premium Full-Stack Todo Application

**Status**: Sprint 2 Complete ✅
**Tech Stack**: Next.js 15 + TypeScript, FastAPI + Python, Better Auth (JWT), Neon PostgreSQL
**Theme**: Premium Midnight with Glassmorphism

---

## Quick Start

### Prerequisites
- Node.js 18+ and npm/pnpm
- Python 3.11+
- Git

### Installation

1. **Clone repository**:
   ```bash
   git clone <repository-url>
   cd full-stack-todo-app
   ```

2. **Install frontend dependencies**:
   ```bash
   cd frontend
   npm install
   ```

3. **Install backend dependencies**:
   ```bash
   cd ../backend
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:

   Create `frontend/.env.local`:
   ```env
   BETTER_AUTH_SECRET=your-256-bit-secret-here
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

   Create `backend/.env`:
   ```env
   BETTER_AUTH_SECRET=your-256-bit-secret-here
   CORS_ORIGINS=http://localhost:3000
   DATABASE_URL=postgresql://<user>:<password>@<host>/<database>?sslmode=require
   ```

   **⚠️ CRITICAL**: `BETTER_AUTH_SECRET` must be identical in both files for JWT authentication to work.

   Generate a secure secret:
   ```bash
   # Node.js
   node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"

   # Python
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

### Running the Application

**Development Mode**:

1. **Start Frontend** (Terminal 1):
   ```bash
   cd frontend
   npm run dev
   ```
   → Opens at http://localhost:3000

2. **Start Backend** (Terminal 2):
   ```bash
   cd backend
   uvicorn main:app --reload
   ```
   → API at http://localhost:8000

**Production Mode**:

1. **Build Frontend**:
   ```bash
   cd frontend
   npm run build
   npm run start
   ```

2. **Run Backend**:
   ```bash
   cd backend
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

---

## Project Structure

```
full-stack-todo-app/
├── frontend/               # Next.js 15 App Router
│   ├── app/
│   │   ├── page.tsx       # Landing page (Bento grid, animations)
│   │   ├── signup/        # Signup flow
│   │   ├── login/         # Login flow
│   │   ├── dashboard/     # Protected dashboard with task CRUD
│   │   ├── profile/       # User profile management
│   │   ├── assistant/     # AI chat interface (placeholder)
│   │   ├── layout.tsx     # Root layout with Navbar
│   │   └── globals.css    # Glassmorphism + theme
│   ├── components/
│   │   ├── Navbar.tsx     # Responsive navbar with hamburger menu
│   │   ├── Footer.tsx     # Premium SaaS footer
│   │   ├── TaskCard.tsx   # Individual task display
│   │   ├── TaskGrid.tsx   # Responsive task grid (3-col → 1-col)
│   │   ├── TaskCreateForm.tsx  # Task creation form
│   │   ├── TaskSkeleton.tsx    # Loading skeletons
│   │   ├── DeleteTaskButton.tsx # Delete confirmation dialog
│   │   ├── EditableTitle.tsx   # Inline title editing
│   │   ├── EmptyState.tsx      # No tasks placeholder
│   │   └── StatusBadge.tsx     # Task status indicator
│   ├── lib/
│   │   ├── auth-client.ts # Custom auth client with session management
│   │   ├── api-client.ts  # API client with JWT
│   │   └── toast.ts       # Toast notification utilities
│   ├── utils/
│   │   └── profile.ts     # Email-to-username parser
│   └── middleware.ts      # Route protection
├── backend/                # FastAPI application
│   ├── main.py            # FastAPI app with CORS + static files
│   ├── auth.py            # JWT validation middleware
│   ├── database.py        # Neon PostgreSQL connection
│   ├── models/
│   │   ├── user.py        # User SQLModel
│   │   └── task.py        # Task SQLModel with status enum
│   ├── schemas/
│   │   └── task.py        # Pydantic request/response schemas
│   ├── routers/
│   │   ├── users.py       # User endpoints (GET /users/me, stats, avatar)
│   │   ├── tasks.py       # Task CRUD endpoints
│   │   └── auth.py        # Auth endpoints (signup, login)
│   └── uploads/avatars/   # User profile images
└── specs/                  # Specification documents
    └── 001-phase2-todo-app/
        ├── spec.md
        ├── plan.md
        ├── tasks.md
        ├── security.md
        ├── sprint1-completion-report.md
        └── sprint2-completion-report.md
```

---

## Features

### ✅ Sprint 1 (Complete)
- **Landing Page**: Premium Hebbia/OneText-inspired design with Bento grid layout
- **Authentication**: Signup, login, logout flows with Better Auth + JWT
- **Protected Routes**: Middleware-based route protection
- **Responsive Design**: 300px-2560px with mobile hamburger menu
- **Premium UI**: Glassmorphism, Framer Motion animations, midnight theme
- **Backend API**: FastAPI with JWT validation endpoint (`GET /users/me`)
- **Type Safety**: Zero TypeScript errors, strict type checking
- **Performance**: Animations 60 FPS, CLS 0

### ✅ Sprint 2 (Complete)
- **Task CRUD Operations**:
  - ✅ Create tasks with title and description
  - ✅ View all tasks in responsive Bento grid (3-col → 2-col → 1-col)
  - ✅ Mark tasks as complete with green check animation
  - ✅ Inline edit task titles (click to edit, blur/Enter to save)
  - ✅ Delete tasks with confirmation dialog
  - ✅ One-way status transition (pending → completed only)

- **Database & Multi-Tenancy**:
  - ✅ Neon PostgreSQL serverless database integration
  - ✅ SQLModel ORM with Task and User models
  - ✅ **Zero-trust data isolation**: All queries filter by `user_id` from JWT
  - ✅ Foreign key constraints (Task.user_id → User.id)
  - ✅ **404 responses for unauthorized access** (prevents ID probing)

- **User Profile Management**:
  - ✅ Profile page with email, join date, task statistics
  - ✅ Profile image upload (JPG/PNG, max 2MB)
  - ✅ Avatar display in navbar (desktop + mobile)
  - ✅ Real-time statistics (total tasks, completed tasks, completion rate)
  - ✅ Display name editing with email prefix fallback

- **Premium UX Features**:
  - ✅ Loading skeletons for async operations
  - ✅ Toast notifications for all CRUD actions
  - ✅ Framer Motion entrance/exit animations
  - ✅ Password visibility toggles on login/signup
  - ✅ Empty state UI ("No tasks yet...")
  - ✅ Glassmorphic confirmation dialogs
  - ✅ Smooth task reordering animations

---

## Authentication Flow

1. **Signup** (`/signup`):
   - Client-side validation (email format, password ≥8 chars, matching passwords)
   - Better Auth `signUp.email()` creates account
   - Green toast → Redirect to `/login`

2. **Login** (`/login`):
   - Better Auth `signIn.email()` validates credentials
   - JWT token stored in cookie (`better-auth.session_token`)
   - Redirect to `/dashboard`

3. **Protected Routes**:
   - Middleware checks session token
   - Unauthenticated → Redirect to `/login?redirect=<original-path>`

4. **Logout**:
   - Navbar button calls `signOut()`
   - Session cleared → Redirect to `/`

5. **Backend Validation**:
   - API client auto-includes `Authorization: Bearer <jwt>` header
   - Backend validates JWT signature with `BETTER_AUTH_SECRET`
   - Returns `{"user_id": <int>}` from JWT 'sub' claim

---

## API Endpoints

### Frontend (Next.js)
- `GET /` - Landing page
- `GET /signup` - Signup form
- `GET /login` - Login form
- `GET /dashboard` - Protected dashboard with task CRUD (requires auth)
- `GET /profile` - User profile management (requires auth)
- `GET /assistant` - AI chat interface placeholder (requires auth)
- `POST /api/auth/[...all]` - Better Auth API routes

### Backend (FastAPI)

**Authentication**:
- `POST /api/auth/sign-up/email` - Create new user account
- `POST /api/auth/sign-in/email` - Login with email/password

**User Endpoints** (all require JWT):
- `GET /users/me` - Get current user profile
- `GET /users/me/stats` - Get user task statistics
- `POST /users/me/avatar` - Upload profile image

**Task Endpoints** (all require JWT):
- `POST /tasks` - Create new task
- `GET /tasks` - List all user's tasks (filtered by user_id)
- `PATCH /tasks/{id}` - Update task status/title (ownership verified)
- `DELETE /tasks/{id}` - Delete task (ownership verified, returns 404 if unauthorized)

---

## Environment Variables Reference

### Frontend (`frontend/.env.local`)
| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `BETTER_AUTH_SECRET` | ✅ Yes | 256-bit secret for JWT signing (MUST match backend) | `abc123...` |
| `NEXT_PUBLIC_API_URL` | ✅ Yes | Backend API base URL | `http://localhost:8000` |

### Backend (`backend/.env`)
| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `BETTER_AUTH_SECRET` | ✅ Yes | 256-bit secret for JWT validation (MUST match frontend) | `abc123...` |
| `CORS_ORIGINS` | ✅ Yes | Allowed frontend origins (comma-separated) | `http://localhost:3000` |
| `DATABASE_URL` | ✅ Yes | Neon PostgreSQL connection string (Sprint 2) | `postgresql://...` |

---

## Scripts

### Frontend
```bash
npm run dev          # Development server (localhost:3000)
npm run build        # Production build
npm run start        # Production server
npm run lint         # ESLint check
npm run type-check   # TypeScript validation
```

### Backend
```bash
uvicorn main:app --reload              # Development server
uvicorn main:app --host 0.0.0.0 --port 8000  # Production server
python -m pytest                        # Run tests (Sprint 2)
```

---

## Development Guidelines

### Code Style
- **Frontend**: ESLint + Next.js config, TypeScript strict mode
- **Backend**: PEP 8, type hints required
- **Commits**: Conventional commits (`feat:`, `fix:`, `docs:`)

### Constitution Principles
1. **Monorepo Architecture**: Separate frontend/backend directories
2. **Zero Trust Security**: JWT validation on all protected routes
3. **Data Isolation**: User ID from JWT 'sub' claim (Sprint 2 database queries)
4. **Responsive Standards**: 300px-2560px, no horizontal scroll
5. **Agent Separation**: UI (structure) vs CSS (styling) responsibilities
6. **Spec-Driven Development**: All features trace to `spec.md`
7. **API Contracts**: Frontend-backend schema synchronization
8. **Type Safety**: Zero `any` types, strict TypeScript

---

## Troubleshooting

### "JWT validation failed" error
- **Cause**: `BETTER_AUTH_SECRET` mismatch between frontend and backend
- **Fix**: Ensure both `.env` files use the same secret

### Horizontal scrolling on mobile
- **Fix**: Implemented hamburger menu (Sprint 1 Phase 5)
- Verify navbar responsive classes: `hidden sm:flex` for desktop buttons

### CORS errors
- **Cause**: Backend not allowing frontend origin
- **Fix**: Update `CORS_ORIGINS` in `backend/.env` to include frontend URL

### TypeScript errors
- **Check**: Run `npm run type-check` in `frontend/`
- **Fix**: All errors must be resolved before deployment

---

## Performance Metrics

**Lighthouse Audit (Production Build)**:
- Performance: 77/100 (⚠️ Target: >90)
- Accessibility: 95/100 ✓
- Best Practices: 92/100 ✓
- LCP: 3.8s (⚠️ Target: <2.5s)
- CLS: 0 ✓

**Optimization Roadmap** (Sprint 2):
- Enable Next.js code splitting for Framer Motion
- Implement route-based lazy loading
- Optimize package imports in `next.config.ts`

---

## Deployment

### Frontend (Vercel Recommended)
1. Push to GitHub
2. Import repository in Vercel
3. Add environment variables:
   - `BETTER_AUTH_SECRET`
   - `NEXT_PUBLIC_API_URL` (production backend URL)
4. Deploy

### Backend (Render/Railway Recommended)
1. Create web service
2. Add environment variables:
   - `BETTER_AUTH_SECRET`
   - `CORS_ORIGINS` (production frontend URL)
   - `DATABASE_URL` (Neon PostgreSQL)
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

---

## Contributing

1. Create feature branch: `git checkout -b feature/name`
2. Follow constitutional principles
3. Write tests (Sprint 2)
4. Submit PR with description

---

## License

MIT License

---

## Support

For issues or questions, check:
- Sprint 1 Completion Report: `specs/001-phase2-todo-app/sprint1-completion-report.md`
- Technical Specification: `specs/001-phase2-todo-app/spec.md`
- Implementation Plan: `specs/001-phase2-todo-app/plan.md`

---

**Built with**:
- [Next.js 15](https://nextjs.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Better Auth](https://www.better-auth.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Framer Motion](https://www.framer.com/motion/)
- [Neon PostgreSQL](https://neon.tech/)
