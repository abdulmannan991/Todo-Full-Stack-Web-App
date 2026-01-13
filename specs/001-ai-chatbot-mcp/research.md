# Research: AI-Powered Todo Chatbot

**Feature**: 001-ai-chatbot-mcp
**Date**: 2026-01-11
**Purpose**: Document technology choices, integration patterns, and best practices for implementing the conversational AI assistant.

## Research Areas

### 1. OpenAI ChatKit Integration (Frontend)

**Decision**: Use OpenAI ChatKit React components for chat UI

**Rationale**:
- Pre-built, production-ready chat interface components
- Handles message rendering, input, and streaming responses
- Integrates seamlessly with Next.js App Router
- Provides accessibility features out of the box
- Reduces frontend development time significantly

**Integration Pattern**:
```typescript
// Frontend integration approach
import { ChatInterface } from '@openai/chatkit-react'

// Pass conversation history and send handler
<ChatInterface
  messages={conversationHistory}
  onSendMessage={handleSendMessage}
  isLoading={isProcessing}
/>
```

**Key Considerations**:
- ChatKit expects messages in `{ role: 'user' | 'assistant', content: string }` format
- Must map backend Message entities to ChatKit format
- Handle loading states during AI processing
- Display tool invocations for transparency

**Alternatives Considered**:
- Custom React chat UI: Rejected due to development time and accessibility concerns
- Third-party chat libraries (react-chat-elements): Rejected due to lack of AI-specific features

---

### 2. OpenAI Agents SDK (Backend)

**Decision**: Use OpenAI Agents SDK for agent orchestration and tool execution

**Rationale**:
- Official SDK for building AI agents with tool calling
- Handles conversation context management
- Supports streaming responses
- Integrates with OpenAI API for language model access
- Provides structured tool invocation and result handling

**Integration Pattern**:
```python
from openai import OpenAI
from openai.agents import Agent

# Initialize agent with tools
agent = Agent(
    name="TaskAssistant",
    instructions="You help users manage their todo tasks...",
    tools=[add_task, list_tasks, complete_task, delete_task],
    model="gpt-4"
)

# Run agent with conversation history
response = agent.run(
    messages=conversation_history,
    user_message=new_user_message
)
```

**Key Considerations**:
- Agent must be initialized per-request (stateless)
- Conversation history loaded from database and passed to agent
- Tool results must be captured and returned to frontend
- Error handling for AI service timeouts (5 seconds)

**Alternatives Considered**:
- LangChain: Rejected due to complexity and overhead for simple tool calling
- Direct OpenAI API calls: Rejected due to lack of structured tool orchestration
- Custom agent implementation: Rejected due to development time and maintenance burden

---

### 3. Official MCP SDK (FastMCP) for Tool Layer

**Decision**: Use FastMCP to define and execute MCP tools

**Rationale**:
- Official Python implementation of Model Context Protocol
- Provides clean decorator-based tool definition
- Handles tool parameter validation automatically
- Integrates with OpenAI Agents SDK
- Maintains separation between FastAPI layer and tool logic

**Tool Definition Pattern**:
```python
from fastmcp import FastMCP

mcp = FastMCP("TaskOperations")

@mcp.tool()
async def add_task(user_id: int, title: str, description: str = None) -> str:
    """Add a new task for the user."""
    # Implementation with database session
    async with get_session() as session:
        task = Task(user_id=user_id, title=title, description=description)
        session.add(task)
        await session.commit()
        return f"Task '{title}' has been added."
```

**Key Considerations**:
- Each tool must initialize its own database session (stateless)
- All tools must enforce user_id filtering (data isolation)
- Tools return human-readable strings for agent responses
- Error handling must be graceful and user-friendly

**Alternatives Considered**:
- Direct function calls: Rejected due to lack of structured tool protocol
- Custom tool framework: Rejected due to reinventing the wheel
- LangChain tools: Rejected due to tight coupling with LangChain ecosystem

---

### 4. Optimistic Locking for Concurrent Requests

**Decision**: Implement version-based optimistic locking on Conversation entity

**Rationale**:
- Prevents race conditions when multiple requests arrive simultaneously
- Maintains stateless architecture (no distributed locks)
- Standard pattern for distributed systems
- Minimal performance overhead

**Implementation Pattern**:
```python
class Conversation(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    version: int = Field(default=1)  # Optimistic lock version
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Update with version check
def update_conversation(conversation_id: int, expected_version: int):
    result = session.exec(
        update(Conversation)
        .where(Conversation.id == conversation_id)
        .where(Conversation.version == expected_version)
        .values(version=expected_version + 1, updated_at=datetime.utcnow())
    )
    if result.rowcount == 0:
        raise ConflictError("Conversation was modified by another request")
```

**Key Considerations**:
- Version incremented on every conversation update
- Retry logic on version conflict (exponential backoff)
- Clear error messages for users on persistent conflicts

**Alternatives Considered**:
- Pessimistic locking (row locks): Rejected due to deadlock risk and poor scalability
- Request serialization per user: Rejected due to infrastructure complexity (message queue)
- No locking: Rejected due to data corruption and message ordering risks

---

### 5. Sliding Window Conversation History

**Decision**: Load last 50 messages per conversation

**Rationale**:
- Prevents unbounded memory growth and query slowdown
- Provides sufficient context for most conversations
- Industry standard (ChatGPT, Claude use similar approaches)
- Balances performance with context preservation

**Implementation Pattern**:
```python
def load_conversation_history(conversation_id: int, user_id: int, limit: int = 50):
    messages = session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .where(Message.user_id == user_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    ).all()
    return list(reversed(messages))  # Oldest first for agent context
```

**Key Considerations**:
- Messages ordered by timestamp (oldest first for agent)
- User isolation enforced in query
- Pagination possible for future "view full history" feature

**Alternatives Considered**:
- Load all messages: Rejected due to performance degradation risk
- Time-based window (24 hours): Rejected due to potential context loss
- Summary + recent messages: Rejected due to implementation complexity

---

### 6. Two-Phase Message Persistence

**Decision**: Store user message first, then AI response separately

**Rationale**:
- Preserves user input even if AI service fails
- Enables retry with full context
- Matches user expectations (input never lost)
- Standard pattern in chat applications

**Implementation Pattern**:
```python
async def handle_chat_request(user_message: str, conversation_id: int, user_id: int):
    # Phase 1: Persist user message immediately
    user_msg = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role="user",
        content=user_message
    )
    session.add(user_msg)
    await session.commit()

    try:
        # Phase 2: Run AI agent
        response = await run_agent(conversation_id, user_id)

        # Phase 3: Persist assistant response
        assistant_msg = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role="assistant",
            content=response.content
        )
        session.add(assistant_msg)
        await session.commit()

        return response
    except TimeoutError:
        # User message already saved, can retry
        raise ServiceUnavailableError("AI service timeout")
```

**Key Considerations**:
- User message persisted before AI processing
- AI failures don't lose user input
- Conversation history includes user message on retry

**Alternatives Considered**:
- Atomic commit after AI completes: Rejected due to data loss risk on AI failure
- Placeholder + update: Rejected due to update complexity
- Store only on success: Rejected due to poor UX

---

### 7. Database Retry with Exponential Backoff

**Decision**: Retry database operations 3 times with exponential backoff (100ms, 500ms, 1000ms)

**Rationale**:
- Handles transient connection failures gracefully
- Standard pattern for distributed systems
- Balances reliability with latency
- Prevents cascading failures

**Implementation Pattern**:
```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=0.1, min=0.1, max=1.0)
)
async def execute_with_retry(operation):
    return await operation()
```

**Key Considerations**:
- Applied to all database operations
- Clear error messages after exhausting retries
- Logging for monitoring transient failures

**Alternatives Considered**:
- Fail fast: Rejected due to poor UX for transient issues
- Circuit breaker: Rejected due to state management complexity
- Async queue: Rejected due to infrastructure overhead

---

### 8. AI Service Timeout Strategy

**Decision**: 5-second timeout with graceful error handling

**Rationale**:
- Prevents indefinite hangs
- Allows reasonable processing time for complex queries
- User message preserved for retry (two-phase persistence)
- Balances reliability with UX

**Implementation Pattern**:
```python
import asyncio

async def run_agent_with_timeout(conversation_id: int, user_id: int):
    try:
        response = await asyncio.wait_for(
            run_agent(conversation_id, user_id),
            timeout=5.0
        )
        return response
    except asyncio.TimeoutError:
        raise ServiceUnavailableError(
            "The assistant is taking longer than expected. Please try again."
        )
```

**Key Considerations**:
- Friendly error messages for users
- User message already saved (can retry)
- Monitoring for timeout frequency

**Alternatives Considered**:
- 3-second timeout: Rejected due to frequent timeouts on complex operations
- 10-second timeout: Rejected due to poor UX
- No timeout: Rejected due to indefinite hang risk

---

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend UI | OpenAI ChatKit | Pre-built chat interface components |
| Frontend Framework | Next.js 15 App Router | React-based web application |
| Frontend Auth | Better Auth | JWT issuance and client-side auth |
| Backend Framework | FastAPI | REST API server |
| Backend Agent | OpenAI Agents SDK | AI agent orchestration and tool calling |
| Backend Tools | FastMCP (Official MCP SDK) | Tool definition and execution |
| Backend Auth | python-jose | JWT verification |
| Database | Neon PostgreSQL | Serverless Postgres for data persistence |
| ORM | SQLModel | Type-safe database models |

---

## Best Practices Applied

1. **Stateless Architecture**: No in-memory session storage; all state in database
2. **User Isolation**: All queries filtered by verified user_id from JWT
3. **Optimistic Locking**: Version-based concurrency control
4. **Sliding Window**: Last 50 messages for performance
5. **Two-Phase Persistence**: User message saved before AI processing
6. **Exponential Backoff**: Retry transient database failures
7. **Timeout Handling**: 5-second AI service timeout with graceful degradation
8. **Type Safety**: TypeScript strict mode, Pydantic models, SQLModel entities
9. **Error Handling**: User-friendly error messages, preserved user input
10. **Tool Transparency**: All tool invocations returned in API response

---

## Next Steps

1. **Phase 1**: Generate data-model.md with Conversation and Message schemas
2. **Phase 1**: Generate contracts/chat-api.md with endpoint specification
3. **Phase 1**: Generate quickstart.md with setup instructions
4. **Phase 2**: Generate tasks.md with implementation tasks (/sp.tasks command)
