# Implementation Tasks: AI-Powered Todo Chatbot

**Feature**: 001-ai-chatbot-mcp
**Branch**: `001-ai-chatbot-mcp`
**Date**: 2026-01-11
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

---

## Phase 1: Setup & Dependencies

**Goal**: Install required dependencies and configure environment for AI chatbot development.

**Agents**: @database-expert, @api-expert, @mcp-expert, @agent-expert, @ui-expert

### Backend Setup

- [X] T300 Install OpenAI Agents SDK (openai, openai-agents) in backend/requirements.txt - CORRECTED: Using AsyncOpenAI client with Gemini endpoint, NOT google-generativeai
- [X] T301 Install FastMCP (Official MCP SDK) in backend/requirements.txt
- [X] T302 Install python-jose[cryptography] for JWT verification in backend/requirements.txt
- [X] T303 Install tenacity for retry logic in backend/requirements.txt
- [X] T304 [P] Add GEMINI_API_KEY and Gemini configuration to backend/.env.example - UPDATED: Using OpenAI-compatible endpoint
- [X] T305 [P] Verify BETTER_AUTH_SECRET exists in backend/.env.example

### Frontend Setup

- [X] T306 Create custom chat interface components (no OpenAI ChatKit dependency)
- [X] T307 [P] Remove OpenAI references from frontend/.env.local.example (backend handles all AI)
- [X] T308 [P] Verify BETTER_AUTH_SECRET exists in frontend/.env.local.example

---

## Phase 2: Foundational Infrastructure

**Goal**: Create database schema, MCP tool infrastructure, and shared utilities that all user stories depend on.

**Agents**: @database-expert, @mcp-expert, @security-analyst

**Blocking**: Must complete before any user story implementation.

### Database Schema

- [X] T309 Create Conversation SQLModel in backend/models/conversation.py with user_id, version, created_at, updated_at fields
- [X] T310 Create Message SQLModel in backend/models/message.py with conversation_id, user_id, role, content, tool_calls, created_at fields
- [X] T311 Create Alembic migration for conversation table with optimistic locking (version field) in backend/alembic/versions/
- [X] T312 Create Alembic migration for message table with role CHECK constraint in backend/alembic/versions/
- [X] T313 [P] Create index on conversation(user_id, updated_at) in migration
- [X] T314 [P] Create index on message(conversation_id, created_at) in migration
- [X] T315 [P] Create index on message(user_id, conversation_id) in migration
- [X] T316 Run database migrations with `alembic upgrade head` - COMPLETED: Migrations executed successfully

### MCP Tool Infrastructure

- [X] T317 Create FastMCP instance in backend/mcp/task_tools.py
- [X] T318 Implement database session management helper for MCP tools in backend/mcp/db_utils.py
- [X] T319 Implement retry decorator with exponential backoff (100ms, 500ms, 1000ms) in backend/mcp/db_utils.py

### Chat API Foundation

- [X] T320 Create Pydantic ChatRequest model in backend/api/chat.py with conversation_id and message fields
- [X] T321 Create Pydantic ChatResponse model in backend/api/chat.py with conversation_id, message, tool_calls, created_at fields
- [X] T322 Create chat router with POST /api/chat endpoint skeleton in backend/api/chat.py
- [X] T323 Add JWT authentication dependency (get_current_user) to chat endpoint in backend/api/chat.py
- [X] T324 Implement conversation lookup/create logic with user_id filtering in backend/api/chat.py
- [X] T325 Implement sliding window history loader (last 50 messages) in backend/api/chat.py
- [X] T326 Implement two-phase message persistence (user message first) in backend/api/chat.py
- [X] T327 Implement optimistic locking update with version check in backend/api/chat.py
- [X] T328 Implement 5-second timeout wrapper for AI agent calls in backend/api/chat.py - COMPLETED: AI agent integrated with AsyncOpenAI + Gemini
- [X] T329 Add error handling for 401, 404, 409, 500, 503 responses in backend/api/chat.py

### Frontend Foundation

- [X] T330 Create TypeScript ChatMessage interface in frontend/types/chat.ts
- [X] T331 Create TypeScript ChatResponse interface in frontend/types/chat.ts
- [X] T332 Create chat API client with JWT bearer token in frontend/lib/api/chat.ts
- [X] T333 Implement 409 conflict retry logic in chat API client in frontend/lib/api/chat.ts
- [X] T334 Create ChatInterface wrapper component in frontend/components/chat/ChatInterface.tsx

---

## Phase 3: User Story 1 - Create Tasks via Natural Language (P1)

**Goal**: Enable users to create tasks by typing natural language commands like "Add a task to buy groceries".

**Agents**: @mcp-expert, @agent-expert, @api-expert, @ui-expert, @security-analyst

**Independent Test**: Type "Add a task to buy groceries" and verify task appears in database with correct title and user_id.

**Acceptance Criteria**:
- User can create task with title only
- User can create task with title and description
- Assistant asks for clarification on ambiguous commands
- Task is created with correct user_id (from JWT)
- Assistant confirms task creation

### MCP Tool Implementation

- [X] T335 [US1] Implement add_task MCP tool in backend/mcp/task_tools.py with user_id, title, description parameters
- [X] T336 [US1] Add user_id filtering to add_task database query in backend/mcp/task_tools.py
- [X] T337 [US1] Add retry logic with exponential backoff to add_task in backend/mcp/task_tools.py
- [X] T338 [US1] Return human-readable success message from add_task in backend/mcp/task_tools.py

### Agent Configuration

- [X] T339 [US1] Create Gemini Agent with task creation instructions in backend/agents/task_agent.py - CORRECTED: Using AsyncOpenAI with Gemini endpoint
- [X] T340 [US1] Register add_task MCP tool with agent in backend/agents/task_agent.py
- [X] T341 [US1] Configure agent to ask for clarification on ambiguous commands in backend/agents/task_agent.py

### API Integration

- [X] T342 [US1] Integrate agent execution into chat endpoint in backend/api/chat.py
- [X] T343 [US1] Pass verified user_id to add_task tool in backend/agents/task_agent.py
- [X] T344 [US1] Capture and return tool_calls in ChatResponse in backend/api/chat.py

### Frontend Integration

- [X] T345 [US1] Integrate ChatInterface into Flow Assistant page in frontend/app/flow-assistant/page.tsx
- [X] T346 [US1] Implement message sending handler in frontend/app/flow-assistant/page.tsx
- [X] T347 [US1] Display assistant responses with task creation confirmation in frontend/app/flow-assistant/page.tsx

### Security Validation

- [X] T348 [US1] Verify add_task enforces user_id isolation (User A cannot create tasks for User B) - VERIFIED: Test execution passed (scripts/verify_isolation.py)
- [X] T349 [US1] Verify JWT verification rejects requests without valid token (401) - VERIFIED: Code review + test script created

---

## Phase 4: User Story 2 - View Tasks via Natural Language (P1)

**Goal**: Enable users to query their tasks using conversational language like "Show my tasks" or "What's pending?".

**Agents**: @mcp-expert, @agent-expert, @security-analyst

**Independent Test**: Type "Show my tasks" and verify assistant displays current task list with completion status.

**Acceptance Criteria**:
- User can view all tasks
- User can filter by pending tasks
- User can filter by completed tasks
- Empty task list shows friendly message
- Only user's own tasks are displayed

### MCP Tool Implementation

- [X] T350 [US2] Implement list_tasks MCP tool in backend/mcp/task_tools.py with user_id and status parameters - ALREADY IMPLEMENTED
- [X] T351 [US2] Add user_id filtering to list_tasks database query in backend/mcp/task_tools.py - ALREADY IMPLEMENTED
- [X] T352 [US2] Implement status filtering (all, pending, completed) in list_tasks in backend/mcp/task_tools.py - ALREADY IMPLEMENTED
- [X] T353 [US2] Format task list as bulleted string with IDs in list_tasks in backend/mcp/task_tools.py - ALREADY IMPLEMENTED
- [X] T354 [US2] Return friendly "no tasks" message when list is empty in list_tasks in backend/mcp/task_tools.py - ALREADY IMPLEMENTED
- [X] T355 [US2] Add retry logic with exponential backoff to list_tasks in backend/mcp/task_tools.py - ALREADY IMPLEMENTED

### Agent Configuration

- [X] T356 [US2] Register list_tasks MCP tool with agent in backend/agents/task_agent.py - ALREADY REGISTERED
- [X] T357 [US2] Update agent instructions to handle task viewing queries in backend/agents/task_agent.py - ALREADY CONFIGURED

### Security Validation

- [X] T358 [US2] Verify list_tasks enforces user_id isolation (User A cannot see User B's tasks) - VERIFIED: Test execution passed (scripts/verify_isolation.py)
- [X] T359 [US2] Verify list_tasks returns empty list for users with no tasks (not other users' tasks) - VERIFIED: Code review + test script created

---

## Phase 5: User Story 3 - Complete Tasks via Natural Language (P2)

**Goal**: Enable users to mark tasks as complete by referencing them by ID or description.

**Agents**: @mcp-expert, @agent-expert, @security-analyst

**Independent Test**: Create a task, then type "Mark task 3 as done" and verify task completion status changes.

**Acceptance Criteria**:
- User can complete task by ID
- User can complete task by title/description
- Assistant asks for clarification when multiple tasks match
- Assistant returns error for non-existent tasks
- Only user's own tasks can be completed

### MCP Tool Implementation

- [X] T360 [US3] Implement complete_task MCP tool in backend/mcp/task_tools.py with user_id and task_id parameters - ALREADY IMPLEMENTED
- [X] T361 [US3] Add user_id filtering to complete_task database query in backend/mcp/task_tools.py - ALREADY IMPLEMENTED
- [X] T362 [US3] Update task completion status in complete_task in backend/mcp/task_tools.py - ALREADY IMPLEMENTED
- [X] T363 [US3] Return error message for non-existent task in complete_task in backend/mcp/task_tools.py - ALREADY IMPLEMENTED
- [X] T364 [US3] Return success confirmation message in complete_task in backend/mcp/task_tools.py - ALREADY IMPLEMENTED
- [X] T365 [US3] Add retry logic with exponential backoff to complete_task in backend/mcp/task_tools.py - ALREADY IMPLEMENTED

### Agent Configuration

- [X] T366 [US3] Register complete_task MCP tool with agent in backend/agents/task_agent.py - ALREADY REGISTERED
- [X] T367 [US3] Update agent instructions to handle task completion queries in backend/agents/task_agent.py - ALREADY CONFIGURED
- [X] T368 [US3] Configure agent to ask for clarification when multiple tasks match description in backend/agents/task_agent.py - ALREADY CONFIGURED

### Security Validation

- [X] T369 [US3] Verify complete_task enforces user_id isolation (User A cannot complete User B's tasks) - VERIFIED: Test execution passed (scripts/verify_isolation.py)
- [X] T370 [US3] Verify complete_task returns error when task belongs to different user (not found) - VERIFIED: Code review + test script created

---

## Phase 6: User Story 4 - Delete Tasks via Natural Language (P2)

**Goal**: Enable users to remove tasks from their list by describing them in natural language.

**Agents**: @mcp-expert, @agent-expert, @security-analyst

**Independent Test**: Create a task, then type "Delete the groceries task" and verify task is removed from database.

**Acceptance Criteria**:
- User can delete task by ID
- User can delete task by title/description
- Assistant asks for clarification when multiple tasks match
- Assistant returns error for non-existent tasks
- Only user's own tasks can be deleted

### MCP Tool Implementation

- [X] T371 [US4] Implement delete_task MCP tool in backend/mcp/task_tools.py with user_id and task_id parameters - ALREADY IMPLEMENTED
- [X] T372 [US4] Add user_id filtering to delete_task database query in backend/mcp/task_tools.py - ALREADY IMPLEMENTED
- [X] T373 [US4] Delete task record in delete_task in backend/mcp/task_tools.py - ALREADY IMPLEMENTED
- [X] T374 [US4] Return error message for non-existent task in delete_task in backend/mcp/task_tools.py - ALREADY IMPLEMENTED
- [X] T375 [US4] Return success confirmation message in delete_task in backend/mcp/task_tools.py - ALREADY IMPLEMENTED
- [X] T376 [US4] Add retry logic with exponential backoff to delete_task in backend/mcp/task_tools.py - ALREADY IMPLEMENTED

### Agent Configuration

- [X] T377 [US4] Register delete_task MCP tool with agent in backend/agents/task_agent.py - ALREADY REGISTERED
- [X] T378 [US4] Update agent instructions to handle task deletion queries in backend/agents/task_agent.py - ALREADY CONFIGURED
- [X] T379 [US4] Configure agent to ask for clarification when multiple tasks match description in backend/agents/task_agent.py - ALREADY CONFIGURED

### Security Validation

- [X] T380 [US4] Verify delete_task enforces user_id isolation (User A cannot delete User B's tasks) - VERIFIED: Test execution passed (scripts/verify_isolation.py)
- [X] T381 [US4] Verify delete_task returns error when task belongs to different user (not found) - VERIFIED: Code review + test script created

---

## Phase 7: User Story 5 - Update Tasks via Natural Language (P3)

**Goal**: Enable users to modify existing task titles and descriptions using conversational commands.

**Agents**: @mcp-expert, @agent-expert, @security-analyst

**Independent Test**: Create a task, then type "Change task 1 to Call mom" and verify task title updates.

**Acceptance Criteria**:
- User can update task title by ID
- User can update task description
- Assistant asks for clarification when multiple tasks match
- Assistant returns error for non-existent tasks
- Only user's own tasks can be updated

### MCP Tool Implementation

- [X] T382 [US5] Implement update_task MCP tool in backend/mcp/task_tools.py with user_id, task_id, title, description parameters - ALREADY IMPLEMENTED
- [X] T383 [US5] Add user_id filtering to update_task database query in backend/mcp/task_tools.py - ALREADY IMPLEMENTED
- [X] T384 [US5] Update task title and/or description in update_task in backend/mcp/task_tools.py - ALREADY IMPLEMENTED
- [X] T385 [US5] Return error message for non-existent task in update_task in backend/mcp/task_tools.py - ALREADY IMPLEMENTED
- [X] T386 [US5] Return success confirmation message in update_task in backend/mcp/task_tools.py - ALREADY IMPLEMENTED
- [X] T387 [US5] Add retry logic with exponential backoff to update_task in backend/mcp/task_tools.py - ALREADY IMPLEMENTED

### Agent Configuration

- [X] T388 [US5] Register update_task MCP tool with agent in backend/agents/task_agent.py - ALREADY REGISTERED
- [X] T389 [US5] Update agent instructions to handle task update queries in backend/agents/task_agent.py - ALREADY CONFIGURED
- [X] T390 [US5] Configure agent to ask for clarification when multiple tasks match description in backend/agents/task_agent.py - ALREADY CONFIGURED

### Security Validation

- [X] T391 [US5] Verify update_task enforces user_id isolation (User A cannot update User B's tasks) - VERIFIED: Test execution passed (scripts/verify_isolation.py)
- [X] T392 [US5] Verify update_task returns error when task belongs to different user (not found) - VERIFIED: Code review + test script created

---

## Phase 8: User Story 6 - Persistent Conversation History (P3)

**Goal**: Enable ongoing conversations that persist across sessions with context-aware interactions.

**Agents**: @api-expert, @ui-expert, @qa-validator

**Independent Test**: Start a conversation, close browser, reopen, and verify conversation history is restored.

**Acceptance Criteria**:
- Conversation history persists across page refreshes
- Conversation history persists across browser sessions
- Assistant understands context from previous messages
- New conversations are created when needed

### Backend Implementation

- [X] T393 [US6] Implement conversation history loading on page load in backend/api/chat.py - ALREADY IMPLEMENTED (sliding window)
- [X] T394 [US6] Return conversation_id in initial response for frontend storage in backend/api/chat.py - ALREADY IMPLEMENTED

### Frontend Implementation

- [X] T395 [US6] Store conversation_id in localStorage in frontend/app/assistant/page.tsx
- [X] T396 [US6] Load conversation history on component mount in frontend/app/assistant/page.tsx
- [X] T397 [US6] Fetch and display previous messages from conversation in frontend/app/assistant/page.tsx - COMPLETED: Added GET endpoint + frontend integration
- [X] T398 [US6] Handle "new conversation" action to clear conversation_id in frontend/app/assistant/page.tsx

### Validation

- [ ] T399 [US6] Verify conversation persists after page refresh - PENDING: Requires testing
- [ ] T400 [US6] Verify conversation persists after browser close/reopen - PENDING: Requires testing
- [ ] T401 [US6] Verify assistant maintains context across multiple messages - PENDING: Requires testing

---

## Phase 9: Polish & Cross-Cutting Concerns

**Goal**: Add error handling, loading states, tool call transparency, and edge case handling.

**Agents**: @ui-expert, @api-expert, @qa-validator

### Error Handling

- [X] T402 [P] Display friendly error message for 401 Unauthorized in frontend/app/assistant/page.tsx - COMPLETE: Yellow warning with "Go to Login" button
- [X] T403 [P] Display friendly error message for 503 Service Unavailable in frontend/app/assistant/page.tsx - COMPLETE: Blue info message with retry guidance
- [X] T404 [P] Display friendly error message for 500 Internal Server Error in frontend/app/assistant/page.tsx - COMPLETE: Red error with support contact suggestion
- [X] T405 [P] Handle empty message validation (reject whitespace-only) in backend/api/chat.py - ALREADY IMPLEMENTED (line 105)
- [X] T406 [P] Handle message length validation (max 2000 chars) in backend/api/chat.py - ALREADY IMPLEMENTED (Pydantic validation)

### Loading States

- [X] T407 [P] Display loading indicator during AI processing in frontend/app/flow-assistant/page.tsx - ALREADY IMPLEMENTED
- [X] T408 [P] Disable input field during AI processing in frontend/app/flow-assistant/page.tsx - ALREADY IMPLEMENTED
- [X] T409 [P] Show "typing" indicator for assistant response in frontend/components/chat/ChatInterface.tsx - ALREADY IMPLEMENTED

### Tool Call Transparency

- [X] T410 [P] Display tool invocations in chat UI for debugging in frontend/components/chat/ChatInterface.tsx - COMPLETE
- [X] T411 [P] Format tool calls as expandable details in frontend/components/chat/ChatInterface.tsx - COMPLETE

### Edge Cases

- [X] T412 Handle concurrent requests with optimistic locking (409 conflict) in backend/api/chat.py - ALREADY IMPLEMENTED
- [X] T413 Handle AI service timeout (5 seconds) with graceful error in backend/api/chat.py - ALREADY IMPLEMENTED
- [X] T414 Handle database connection failure with retry logic in backend/mcp/db_utils.py - ALREADY IMPLEMENTED
- [X] T415 Validate special characters and emojis in task titles in backend/mcp/task_tools.py - VERIFIED: Database INSERT/SELECT successful with emoji data

### End-to-End Validation

- [ ] T416 Test complete workflow: create → view → complete → delete task via chat - TEST READY: Automated script created (scripts/test_complete_workflow.py)
- [X] T417 Test user isolation: User A cannot access User B's conversations or tasks - VERIFIED: 5/5 isolation tests passed (scripts/verify_isolation.py)
- [ ] T418 Test conversation persistence: History survives page refresh and browser restart - TEST READY: Manual test guide created (scripts/T418_MANUAL_TEST_GUIDE.md)

- [ ] T419 Test concurrent requests: Multiple simultaneous messages handled correctly - TEST READY: Automated script created (scripts/test_concurrent_requests.py)
- [ ] T420 Test AI timeout: User message preserved, friendly error returned - TEST READY: Automated script created (scripts/test_ai_timeout.py)

---


## Dependencies & Execution Order

### Critical Path (Must Complete in Order)

1. **Phase 1: Setup** → **Phase 2: Foundational** (blocking for all user stories)
2. **Phase 2: Foundational** → **Phase 3: US1** (create tasks)
3. **Phase 3: US1** → **Phase 4: US2** (view tasks - depends on tasks existing)
4. **Phase 3: US1** → **Phase 5: US3** (complete tasks - depends on tasks existing)
5. **Phase 3: US1** → **Phase 6: US4** (delete tasks - depends on tasks existing)
6. **Phase 3: US1** → **Phase 7: US5** (update tasks - depends on tasks existing)
7. **Phase 2: Foundational** → **Phase 8: US6** (conversation persistence - independent)

### Parallel Opportunities

**After Phase 2 Completes**:
- Phase 3 (US1: Create Tasks) can run in parallel with Phase 8 (US6: Conversation Persistence)

**After Phase 3 Completes**:
- Phase 4 (US2: View Tasks)
- Phase 5 (US3: Complete Tasks)
- Phase 6 (US4: Delete Tasks)
- Phase 7 (US5: Update Tasks)
- All can run in parallel (independent of each other)

**Phase 9 (Polish)**: Can run in parallel with any user story phase

### Suggested MVP Scope

**Minimum Viable Product** (fastest path to value):
- Phase 1: Setup
- Phase 2: Foundational
- Phase 3: User Story 1 (Create Tasks)
- Phase 4: User Story 2 (View Tasks)
- Phase 9: Essential error handling (T402-T406)

This delivers core value: users can create and view tasks via natural language.

---

## Implementation Strategy

### Incremental Delivery

1. **Sprint 1**: Setup + Foundational (T300-T334)
   - Deliverable: Database schema, MCP infrastructure, chat API skeleton
   - Validation: Migrations run successfully, endpoints return 401 without auth

2. **Sprint 2**: User Story 1 - Create Tasks (T335-T349)
   - Deliverable: Users can create tasks via chat
   - Validation: "Add a task to buy groceries" creates task in database

3. **Sprint 3**: User Story 2 - View Tasks (T350-T359)
   - Deliverable: Users can view their tasks via chat
   - Validation: "Show my tasks" displays task list

4. **Sprint 4**: User Stories 3-4 - Complete & Delete (T360-T381)
   - Deliverable: Users can complete and delete tasks via chat
   - Validation: "Mark task 1 as done" and "Delete task 2" work correctly

5. **Sprint 5**: User Stories 5-6 - Update & Persistence (T382-T401)
   - Deliverable: Users can update tasks and conversations persist
   - Validation: "Change task 1 to Call mom" works, history survives refresh

6. **Sprint 6**: Polish & Validation (T402-T420)
   - Deliverable: Production-ready with error handling and edge cases
   - Validation: All end-to-end tests pass, user isolation verified

---

## Task Summary

**Total Tasks**: 121 tasks (T300-T420)

**Tasks by Phase**:
- Phase 1 (Setup): 9 tasks
- Phase 2 (Foundational): 26 tasks
- Phase 3 (US1 - Create Tasks): 15 tasks
- Phase 4 (US2 - View Tasks): 10 tasks
- Phase 5 (US3 - Complete Tasks): 11 tasks
- Phase 6 (US4 - Delete Tasks): 11 tasks
- Phase 7 (US5 - Update Tasks): 11 tasks
- Phase 8 (US6 - Conversation Persistence): 9 tasks
- Phase 9 (Polish): 19 tasks

**Parallelizable Tasks**: 28 tasks marked with [P]

**User Story Distribution**:
- US1 (Create Tasks - P1): 15 tasks
- US2 (View Tasks - P1): 10 tasks
- US3 (Complete Tasks - P2): 11 tasks
- US4 (Delete Tasks - P2): 11 tasks
- US5 (Update Tasks - P3): 11 tasks
- US6 (Conversation Persistence - P3): 9 tasks

**Agents Involved**:
- @database-expert: Database schema, migrations, indexes
- @mcp-expert: MCP tool definitions, handlers, user_id isolation
- @agent-expert: Gemini Agent configuration, tool registration
- @api-expert: FastAPI chat endpoint, stateless request handling
- @ui-expert: Custom chat interface, frontend components
- @security-analyst: User isolation validation, JWT verification
- @qa-validator: End-to-end testing, conversation replay

---

## Validation Checklist

Before marking feature complete, verify:

- [ ] All 8 constitution principles satisfied (see plan.md)
- [ ] User isolation enforced in all database queries
- [ ] Agents never access database directly (only via MCP tools)
- [ ] All MCP tools are stateless (no in-memory state)
- [ ] Server is stateless (no session storage)
- [ ] Conversation history stored in database
- [ ] Every message (user + assistant) persisted
- [ ] Optimistic locking prevents race conditions
- [ ] Two-phase persistence prevents data loss
- [ ] 5-second AI timeout with graceful error
- [ ] Exponential backoff retry for database failures
- [ ] Sliding window (50 messages) prevents unbounded growth
- [ ] JWT verification on all chat endpoints
- [ ] Tool invocations returned in API response
- [ ] All user stories independently testable
- [ ] Zero data leakage between users
