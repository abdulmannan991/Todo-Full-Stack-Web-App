# Implementation Plan: AI-Powered Todo Chatbot

**Branch**: `001-ai-chatbot-mcp` | **Date**: 2026-01-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-ai-chatbot-mcp/spec.md`

## Summary

Implement a conversational AI assistant that allows users to manage their todo tasks through natural language commands. The system integrates OpenAI ChatKit (frontend), OpenAI Agents SDK (backend), and Official MCP SDK (tool layer) to provide a stateless, scalable chat interface. Users can create, view, update, complete, and delete tasks by typing natural language commands like "Add a task to buy groceries" or "Show my pending tasks". The implementation maintains full user data isolation, conversation persistence across sessions, and graceful handling of AI service failures.

## Technical Context

**Language/Version**:
- Frontend: TypeScript (Next.js 15 App Router)
- Backend: Python 3.11+ (FastAPI)

**Primary Dependencies**:
- Frontend: OpenAI ChatKit, Better Auth, React 18, Tailwind CSS
- Backend: OpenAI Agents SDK, Official MCP SDK (FastMCP), FastAPI, SQLModel, python-jose (JWT)

**Storage**:
- Neon PostgreSQL (serverless) for tasks, conversations, and messages
- Existing Task table (unchanged)
- New tables: Conversation, Message

**Testing**:
- Frontend: Jest + React Testing Library
- Backend: pytest + httpx
- Integration: End-to-end chat flow tests

**Target Platform**:
- Frontend: Web browsers (Chrome, Firefox, Safari, Edge)
- Backend: Linux server (containerized FastAPI)

**Project Type**: Web application (monorepo with frontend/ and backend/)

**Performance Goals**:
- Chat responses: <3 seconds for simple operations (target), <5 seconds maximum (with timeout)
- Database queries: <500ms
- Conversation history loading: <1 second (last 50 messages)
- Support 100 concurrent users without degradation

**Constraints**:
- Stateless backend (no in-memory session storage)
- Sliding window conversation history (last 50 messages)
- Optimistic locking for concurrent request handling
- Two-phase message persistence (user message first, then AI response)
- 5-second AI service timeout with graceful degradation
- Exponential backoff retry for database failures (3 attempts: 100ms, 500ms, 1000ms)

**Scale/Scope**:
- Multi-tenant system with user isolation
- Unlimited conversations per user (single active conversation in Phase 3)
- Conversation history retained indefinitely
- Support for 5+ natural language variations per operation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Monorepo Architecture ✅ PASS
- Frontend code remains in `frontend/` directory
- Backend code remains in `backend/` directory
- Agent definitions in `.claude/agents/`
- Specifications in `specs/001-ai-chatbot-mcp/`
- No cross-contamination of concerns

### II. Zero Trust Security Model (Better Auth) ✅ PASS
- JWT verification mandatory on all chat API endpoints
- `BETTER_AUTH_SECRET` shared between frontend and backend
- User ID extracted from verified JWT, never from client input
- 401 Unauthorized returned for invalid/missing tokens
- MCP tools receive verified user_id from FastAPI layer

### III. Mandatory Data Isolation ✅ PASS
- All Conversation queries filtered by `user_id`
- All Message queries filtered by `user_id`
- All Task operations (via MCP tools) filtered by `user_id`
- `Depends(get_current_user)` on all chat endpoints
- No cross-user data access possible

### IV. UI/UX & Responsive Standards ✅ PASS
- ChatKit components integrated into existing Flow Assistant page
- Responsive design maintained (300px - 2560px)
- No modifications to global Navbar, Sidebar, or Footer
- Mobile-first approach with Tailwind breakpoints
- Touch targets meet 44x44px minimum on mobile

### V. Agent Responsibility Separation ✅ PASS
- `@ui-auth-expert`: ChatKit integration, layout structure, Better Auth JWT client
- `@css-animation-expert`: Visual polish, animations (if needed)
- `@fastapi-jwt-guardian`: JWT verification middleware in FastAPI
- `@database-expert`: Schema design for Conversation and Message tables
- `@logic-coordinator`: End-to-end flow verification

### VI. Spec-Driven Development ✅ PASS
- Feature originated from `specs/001-ai-chatbot-mcp/spec.md`
- This plan.md created by `/sp.plan`
- tasks.md will be created by `/sp.tasks`
- Implementation follows tasks.md strictly

### VII. API Contract Synchronization ✅ PASS
- Chat API contract documented in `contracts/chat-api.md`
- Request/response schemas defined
- Error codes specified (401, 500, 503)
- JWT authentication requirements explicit
- Tool invocation transparency in responses

### VIII. Type Safety ✅ PASS
- Frontend: TypeScript strict mode, typed API responses
- Backend: Pydantic models for requests/responses, SQLModel for entities
- Type hints on all Python functions
- No `any` types in TypeScript (except justified cases)

**Constitution Compliance**: ✅ ALL GATES PASSED

## Project Structure

### Documentation (this feature)

```text
specs/001-ai-chatbot-mcp/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (current)
├── research.md          # Phase 0 output (to be created)
├── data-model.md        # Phase 1 output (to be created)
├── quickstart.md        # Phase 1 output (to be created)
├── contracts/           # Phase 1 output (to be created)
│   └── chat-api.md      # Chat endpoint contract
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
backend/
├── models/
│   ├── conversation.py      # New: Conversation SQLModel
│   └── message.py           # New: Message SQLModel
├── api/
│   └── chat.py              # New: Chat endpoint
├── middleware/
│   └── auth.py              # Existing: JWT verification (may need updates)
├── mcp/
│   └── task_tools.py        # New: MCP tools for task operations
└── tests/
    ├── test_chat_api.py     # New: Chat endpoint tests
    └── test_mcp_tools.py    # New: MCP tool tests

frontend/
├── app/
│   └── flow-assistant/
│       └── page.tsx         # Modified: Integrate ChatKit
├── components/
│   └── chat/
│       ├── ChatInterface.tsx    # New: ChatKit wrapper
│       └── MessageList.tsx      # New: Message display
├── lib/
│   └── api/
│       └── chat.ts          # New: Chat API client
└── types/
    └── chat.ts              # New: Chat-related types

skills/
└── task-manager/
    └── SKILL.md             # Existing: Task manager skill spec
```

**Structure Decision**: Web application structure (Option 2) selected. The project follows the monorepo pattern with separate frontend/ and backend/ directories. New chat functionality integrates into existing structure without modifying core application layout. MCP tools are added to backend/mcp/ to maintain separation between FastAPI coordination layer and tool execution layer.

## Complexity Tracking

> **No violations detected. All constitution principles satisfied.**

