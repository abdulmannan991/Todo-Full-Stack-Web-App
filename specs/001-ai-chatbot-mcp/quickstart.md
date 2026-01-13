# Quickstart Guide: AI-Powered Todo Chatbot

**Feature**: 001-ai-chatbot-mcp
**Date**: 2026-01-11
**Purpose**: Get developers up to speed on implementing the conversational AI assistant.

## Overview

This guide walks you through setting up, understanding, and implementing the AI-powered todo chatbot feature. The feature integrates OpenAI ChatKit (frontend), OpenAI Agents SDK (backend), and FastMCP (tool layer) to provide natural language task management.

---

## Prerequisites

### Required Knowledge
- TypeScript and React (Next.js 15 App Router)
- Python 3.11+ and FastAPI
- SQLModel and PostgreSQL
- JWT authentication concepts
- Basic understanding of AI agents and tool calling

### Required Tools
- Node.js 18+ and npm/yarn
- Python 3.11+
- PostgreSQL (Neon account)
- OpenAI API key
- Git

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  ChatKit UI  │───▶│  API Client  │───▶│  Better Auth │  │
│  │  Components  │    │  (JWT Bearer)│    │  (JWT Issue) │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ POST /api/chat
                              │ Authorization: Bearer <JWT>
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                         Backend                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  JWT Verify  │───▶│  Chat API    │───▶│ Agents SDK   │  │
│  │  Middleware  │    │  Endpoint    │    │ (OpenAI)     │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                              │                    │          │
│                              │                    ▼          │
│                              │         ┌──────────────┐      │
│                              │         │  MCP Tools   │      │
│                              │         │  (FastMCP)   │      │
│                              │         └──────────────┘      │
│                              ▼                    │          │
│                      ┌──────────────┐            │          │
│                      │  PostgreSQL  │◀───────────┘          │
│                      │  (Neon)      │                       │
│                      └──────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

**Key Principles**:
1. **Stateless**: No in-memory session storage
2. **User Isolation**: All queries filtered by JWT-derived user_id
3. **Tool Transparency**: All tool calls returned in API response
4. **Optimistic Locking**: Version-based concurrency control
5. **Two-Phase Persistence**: User message saved before AI processing

---

## Environment Setup

### 1. Backend Environment Variables

Create or update `backend/.env`:

```bash
# Database
DATABASE_URL=postgresql://user:password@host/database

# Authentication (MUST match frontend)
BETTER_AUTH_SECRET=your-secret-key-here

# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
```

**Critical**: `BETTER_AUTH_SECRET` must be identical in frontend and backend.

### 2. Frontend Environment Variables

Create or update `frontend/.env.local`:

```bash
# API
NEXT_PUBLIC_API_URL=http://localhost:8000

# Authentication (MUST match backend)
BETTER_AUTH_SECRET=your-secret-key-here
BETTER_AUTH_URL=http://localhost:3000

# OpenAI (for ChatKit)
NEXT_PUBLIC_OPENAI_API_KEY=sk-your-openai-api-key
```

---

## Database Setup

### 1. Run Migration

```bash
cd backend
alembic upgrade head
```

This creates:
- `conversation` table with optimistic locking
- `message` table with role validation
- Indexes for user isolation and query performance

### 2. Verify Schema

```sql
-- Check conversation table
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'conversation';

-- Check message table
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'message';
```

Expected tables:
- `conversation`: id, user_id, version, created_at, updated_at
- `message`: id, conversation_id, user_id, role, content, tool_calls, created_at

---

## Backend Implementation

### 1. Install Dependencies

```bash
cd backend
pip install openai fastmcp python-jose[cryptography] tenacity
```

### 2. Create SQLModel Entities

**File**: `backend/models/conversation.py`

```python
from sqlmodel import SQLModel, Field
from datetime import datetime

class Conversation(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    version: int = Field(default=1, ge=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**File**: `backend/models/message.py`

```python
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON
from datetime import datetime
from typing import Literal

class Message(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id", index=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    role: Literal["user", "assistant"] = Field(max_length=20)
    content: str = Field(min_length=1)
    tool_calls: list[dict] | None = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### 3. Create MCP Tools

**File**: `backend/mcp/task_tools.py`

```python
from fastmcp import FastMCP
from sqlmodel import Session, select
from backend.models.task import Task

mcp = FastMCP("TaskOperations")

@mcp.tool()
async def add_task(user_id: int, title: str, description: str = None) -> str:
    """Add a new task for the user."""
    # Implementation with user_id filtering
    pass

@mcp.tool()
async def list_tasks(user_id: int, status: str = "all") -> str:
    """List tasks for the user."""
    # Implementation with user_id filtering
    pass

@mcp.tool()
async def complete_task(user_id: int, task_id: int) -> str:
    """Mark a task as complete."""
    # Implementation with user_id filtering
    pass

@mcp.tool()
async def delete_task(user_id: int, task_id: int) -> str:
    """Delete a task."""
    # Implementation with user_id filtering
    pass
```

### 4. Create Chat API Endpoint

**File**: `backend/api/chat.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from backend.middleware.auth import get_current_user
from backend.models.user import User

router = APIRouter()

class ChatRequest(BaseModel):
    conversation_id: int | None = None
    message: str

class ChatResponse(BaseModel):
    conversation_id: int
    message: dict
    tool_calls: list[dict]
    created_at: str

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    # 1. Validate and load/create conversation
    # 2. Load last 50 messages (sliding window)
    # 3. Persist user message (two-phase)
    # 4. Run AI agent with MCP tools (5-second timeout)
    # 5. Persist assistant response
    # 6. Update conversation version (optimistic locking)
    # 7. Return response with tool calls
    pass
```

---

## Frontend Implementation

### 1. Install Dependencies

```bash
cd frontend
npm install @openai/chatkit-react
```

### 2. Create Chat API Client

**File**: `frontend/lib/api/chat.ts`

```typescript
export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatResponse {
  conversation_id: number;
  message: ChatMessage;
  tool_calls: Array<{
    tool: string;
    arguments: Record<string, any>;
    result: string;
  }>;
  created_at: string;
}

export async function sendChatMessage(
  conversationId: number | null,
  message: string
): Promise<ChatResponse> {
  const token = getAuthToken(); // From Better Auth

  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      conversation_id: conversationId,
      message: message
    })
  });

  if (!response.ok) {
    if (response.status === 409) {
      // Retry on conflict
      return sendChatMessage(conversationId, message);
    }
    throw new Error(`Chat API error: ${response.status}`);
  }

  return response.json();
}
```

### 3. Integrate ChatKit

**File**: `frontend/app/flow-assistant/page.tsx`

```typescript
'use client';

import { useState } from 'react';
import { ChatInterface } from '@openai/chatkit-react';
import { sendChatMessage } from '@/lib/api/chat';

export default function FlowAssistantPage() {
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async (message: string) => {
    setIsLoading(true);

    // Add user message to UI immediately
    setMessages(prev => [...prev, { role: 'user', content: message }]);

    try {
      const response = await sendChatMessage(conversationId, message);

      // Update conversation ID if new
      if (!conversationId) {
        setConversationId(response.conversation_id);
      }

      // Add assistant response
      setMessages(prev => [...prev, response.message]);
    } catch (error) {
      console.error('Chat error:', error);
      // Show error message to user
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Flow Assistant</h1>
      <ChatInterface
        messages={messages}
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
      />
    </div>
  );
}
```

---

## Testing

### Backend Tests

```bash
cd backend
pytest tests/test_chat_api.py -v
pytest tests/test_mcp_tools.py -v
```

**Key Test Cases**:
1. User isolation (User A cannot access User B's conversations)
2. Optimistic locking (concurrent requests handled correctly)
3. Two-phase persistence (user message saved before AI processing)
4. AI timeout handling (503 returned, user message preserved)
5. Tool execution (all tools enforce user_id filtering)

### Frontend Tests

```bash
cd frontend
npm test
```

**Key Test Cases**:
1. ChatKit integration renders correctly
2. API client handles 409 conflicts with retry
3. Loading states displayed during AI processing
4. Error messages shown on API failures

---

## Development Workflow

### 1. Start Backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 2. Start Frontend

```bash
cd frontend
npm run dev
```

### 3. Test Chat Flow

1. Navigate to `http://localhost:3000/flow-assistant`
2. Log in via Better Auth
3. Type: "Add a task to buy groceries"
4. Verify task created and assistant responds
5. Type: "Show my tasks"
6. Verify task list displayed

---

## Debugging

### Enable Verbose Logging

**Backend** (`backend/.env`):
```bash
LOG_LEVEL=DEBUG
```

**Frontend** (browser console):
```typescript
localStorage.setItem('debug', 'chat:*');
```

### Common Issues

**Issue**: 401 Unauthorized
- **Cause**: JWT token invalid or expired
- **Fix**: Verify `BETTER_AUTH_SECRET` matches in frontend and backend

**Issue**: 404 Conversation Not Found
- **Cause**: Conversation belongs to different user
- **Fix**: Check user_id filtering in queries

**Issue**: 503 Service Unavailable
- **Cause**: AI service timeout
- **Fix**: Check OpenAI API key and network connectivity

**Issue**: 409 Conflict
- **Cause**: Concurrent requests modified conversation
- **Fix**: Client should retry automatically (already implemented)

---

## Performance Monitoring

### Key Metrics

1. **API Latency**: p95 should be <3 seconds for simple operations
2. **Database Queries**: Should complete in <500ms
3. **AI Service Calls**: Should complete in <5 seconds
4. **Conversation History Load**: Should complete in <1 second (50 messages)

### Monitoring Tools

- Backend: FastAPI built-in metrics at `/metrics`
- Database: Neon dashboard for query performance
- Frontend: Browser DevTools Network tab

---

## Next Steps

1. **Implement Backend**:
   - Create SQLModel entities
   - Implement MCP tools with user_id filtering
   - Create chat API endpoint with optimistic locking
   - Add retry logic with exponential backoff

2. **Implement Frontend**:
   - Integrate ChatKit components
   - Create chat API client with JWT bearer token
   - Handle loading and error states
   - Display tool invocations for transparency

3. **Testing**:
   - Write unit tests for MCP tools
   - Write integration tests for chat API
   - Test user isolation thoroughly
   - Test concurrent request handling

4. **Documentation**:
   - Update API documentation
   - Create user guide for natural language commands
   - Document troubleshooting steps

---

## Resources

- [OpenAI ChatKit Documentation](https://platform.openai.com/docs/chatkit)
- [OpenAI Agents SDK](https://platform.openai.com/docs/agents)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Better Auth Documentation](https://better-auth.com)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com)
- [Feature Specification](./spec.md)
- [Implementation Plan](./plan.md)
- [Data Model](./data-model.md)
- [API Contract](./contracts/chat-api.md)

---

## Support

For questions or issues:
1. Check the [spec.md](./spec.md) for requirements
2. Review [research.md](./research.md) for technology decisions
3. Consult [data-model.md](./data-model.md) for schema details
4. Reference [contracts/chat-api.md](./contracts/chat-api.md) for API details
5. Create a GitHub issue with detailed reproduction steps
