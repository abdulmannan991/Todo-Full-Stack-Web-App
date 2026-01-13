---
id: 001
title: Create AI Chatbot Specification
stage: spec
date: 2026-01-11
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-ai-chatbot-mcp
branch: 001-ai-chatbot-mcp
user: system
command: /sp.specify
labels: ["specification", "ai-chatbot", "mcp", "phase-3", "natural-language"]
links:
  spec: specs/001-ai-chatbot-mcp/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-ai-chatbot-mcp/spec.md
  - specs/001-ai-chatbot-mcp/checklists/requirements.md
tests:
  - None (specification phase)
---

## Prompt

```
specs/phase-3.md

# Phase 3 — AI-Powered Todo Chatbot (MCP + Agents)

## 1. Purpose

This phase adds an AI-powered conversational layer to the Todo system.
Users must be able to manage tasks using natural language through the existing "Flow Assistant" UI.

The system must use:
- OpenAI ChatKit (frontend)
- FastAPI (backend)
- OpenAI Agents SDK (agent + runner)
- Official MCP SDK (tool layer)
- SQLModel + Neon PostgreSQL (persistence)
- Better Auth (already implemented)

The architecture must be fully stateless on the server.

## 2. Core Architecture Rules

These rules are non-negotiable:

1. The FastAPI server holds ZERO memory between requests.
2. Every chat request must:
   - Load conversation from DB
   - Append the new user message
   - Send full history to the agent
   - Run the agent
   - Store assistant response
   - Return result to client
3. The AI agent must NEVER access the database directly.
4. The AI agent can ONLY interact with tasks via MCP tools.
5. MCP tools are stateless and persist data to the database.
6. All tool calls must be returned to the frontend.

## 3. System Architecture

ChatKit UI (Flow Assistant)
│
▼
POST /api/{user_id}/chat (FastAPI)
│
▼
OpenAI Agents SDK (Agent + Runner)
│
▼
MCP Server (Official MCP SDK)
│
▼
Neon PostgreSQL (SQLModel ORM)

The FastAPI layer coordinates the agent and database but does not hold state.

## 4. Database Models

### Task
- id
- user_id
- title
- description
- completed
- created_at
- updated_at

### Conversation
- id
- user_id
- created_at
- updated_at

### Message
- id
- user_id
- conversation_id
- role ("user" | "assistant")
- content
- created_at

Conversation history is the single source of context for the agent.

## 5. Chat API

### Endpoint
POST `/api/{user_id}/chat`

### Request
{
  conversation_id?: number,
  message: string
}

If conversation_id is not provided, a new conversation must be created.

### Response
{
  conversation_id: number,
  response: string,
  tool_calls: array
}

tool_calls contains all MCP tools invoked during this turn.

## 6. MCP Tool Layer

The MCP server must expose the following tools:

### add_task
Create a new task

Input:
- user_id (string, required)
- title (string, required)
- description (string, optional)

Output:
- task_id
- status
- title

### list_tasks
Retrieve tasks

Input:
- user_id (string, required)
- status (optional: "all", "pending", "completed")

Output:
Array of:
- id
- title
- completed

### complete_task
Mark task complete

Input:
- user_id (string, required)
- task_id (integer, required)

Output:
- task_id
- status
- title

### delete_task
Remove a task

Input:
- user_id (string, required)
- task_id (integer, required)

Output:
- task_id
- status
- title

### update_task
Modify task

Input:
- user_id (string, required)
- task_id (integer, required)
- title (optional)
- description (optional)

Output:
- task_id
- status
- title

## 7. Agent Behavior Specification

The agent must:
- Interpret natural language
- Decide which MCP tool to call
- Call the tool
- Receive the tool response
- Generate a friendly confirmation message

### Intent → Tool Mapping

| User Says | Agent Action |
|---------|--------------|
| "Add a task to buy groceries" | add_task |
| "Show my tasks" | list_tasks(status="all") |
| "What's pending?" | list_tasks(status="pending") |
| "Mark task 3 as done" | complete_task |
| "Delete the meeting task" | list_tasks → delete_task |
| "Change task 1 to Call mom" | update_task |
| "What have I completed?" | list_tasks(status="completed") |

If multiple tasks match, the agent must ask for clarification.

## 8. Conversation Flow (Stateless)

For every request:

1. Receive user message
2. Load conversation messages from DB
3. Append new user message
4. Store user message in DB
5. Run agent with history
6. Agent calls MCP tools if needed
7. Store assistant message in DB
8. Return response + tool_calls

The server keeps NO in-memory state.

## 9. Frontend Integration

The existing "Flow Assistant" UI must be used.
No UI redesign is allowed in this phase.

It sends messages to:
POST /api/{user_id}/chat

It renders:
- assistant.response
- tool_calls (for debugging)

## 10. Non-Functional Requirements

- Stateless backend
- Multi-tenant safe (user_id isolation)
- All tool calls must enforce user ownership
- Conversations must survive server restarts
- The system must be horizontally scalable

## 11. Success Criteria

The system is considered complete when:

- Users can manage tasks by typing natural language
- The agent correctly calls MCP tools
- Conversations persist across requests
- The server remains stateless
- Tool calls and responses are visible in the API output

CRITICAL IMPLEMENTATION INSTRUCTIONS:

Zero Destructive Changes: Do NOT modify, delete, or rename any existing tables or data in the database. Use if_not_exists patterns for migrations.

UI Preservation: Integrate the OpenAI ChatKit components inside the existing /flow-assistant page. Do not change the global Navbar, Sidebar, or Footer.

Stateless Enforcement: Ensure ai_service.py is fully stateless. It must fetch all history from the Message table at the start of every request.

No Logic Leakage: Business logic for tasks must stay in the MCP tools. The FastAPI endpoint should only act as a proxy between ChatKit and the Agents SDK.

Analyze First: Before writing any code, run /sp.plan and wait for my explicit approval of the file changes.
```

## Response snapshot

Created comprehensive specification for Phase 3 AI-Powered Todo Chatbot feature:

**Branch Created**: `001-ai-chatbot-mcp`

**Specification Highlights**:
- 6 prioritized user stories (P1-P3) covering all task operations via natural language
- 20 functional requirements ensuring stateless architecture and user isolation
- 10 measurable success criteria (technology-agnostic)
- Comprehensive edge cases, constraints, and dependencies
- Clear scope boundaries with explicit exclusions

**Key Architectural Principles Captured**:
- Fully stateless backend (zero in-memory state)
- AI agent interacts only via MCP tools (no direct DB access)
- Conversation history as single source of context
- User isolation enforced at all layers
- Existing UI and data preservation

**Validation Results**:
- All checklist items passed
- No [NEEDS CLARIFICATION] markers needed
- All requirements testable and unambiguous
- Success criteria measurable and technology-agnostic
- Ready for `/sp.plan` phase

**Files Created**:
1. `specs/001-ai-chatbot-mcp/spec.md` - Complete feature specification
2. `specs/001-ai-chatbot-mcp/checklists/requirements.md` - Quality validation checklist

## Outcome

- ✅ Impact: Complete specification created for AI chatbot feature with clear architectural constraints and user-focused requirements
- 🧪 Tests: No tests (specification phase) - acceptance scenarios defined for implementation phase
- 📁 Files: 2 files created (spec.md, requirements.md)
- 🔁 Next prompts: `/sp.plan` to create architectural plan and identify implementation tasks
- 🧠 Reflection: Specification successfully balances technical precision with business clarity. All requirements are independently testable. The stateless architecture constraint is clearly enforced throughout.

## Evaluation notes (flywheel)

- Failure modes observed: None - specification completed without clarifications needed
- Graders run and results (PASS/FAIL): Quality checklist validation - ALL PASS (14/14 items)
- Prompt variant (if applicable): Standard /sp.specify workflow
- Next experiment (smallest change to try): Proceed to planning phase to validate architectural feasibility of stateless MCP integration
