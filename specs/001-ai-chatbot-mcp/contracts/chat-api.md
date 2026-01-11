# Chat API Contract

**Feature**: 001-ai-chatbot-mcp
**Date**: 2026-01-11
**Version**: 1.0.0
**Purpose**: Define the REST API contract for the conversational AI chat endpoint.

## Overview

The Chat API enables users to interact with the AI assistant through natural language to manage their todo tasks. The API maintains conversation history, executes tool calls, and returns both the assistant's response and tool invocation details.

---

## Endpoint: POST /api/chat

Send a message to the AI assistant and receive a response with tool execution results.

### Authentication

**Required**: Yes (JWT Bearer token)

**Header**:
```
Authorization: Bearer <jwt_token>
```

**JWT Claims Required**:
- `user_id`: Integer - Extracted and used for all operations
- `exp`: Expiration timestamp
- Signature verified using `BETTER_AUTH_SECRET`

**Error Response** (401 Unauthorized):
```json
{
  "detail": "Invalid or missing authentication token"
}
```

---

### Request

**Content-Type**: `application/json`

**Body Schema**:
```typescript
{
  conversation_id?: number;  // Optional: null for new conversation
  message: string;            // Required: User's message (1-2000 chars)
}
```

**Field Validation**:
- `conversation_id`:
  - Optional (null creates new conversation)
  - Must belong to authenticated user if provided
  - Returns 404 if conversation doesn't exist or belongs to another user
- `message`:
  - Required
  - Min length: 1 character
  - Max length: 2000 characters
  - Whitespace-only messages rejected

**Example Request**:
```json
{
  "conversation_id": 42,
  "message": "Add a task to buy groceries"
}
```

**Example Request (New Conversation)**:
```json
{
  "conversation_id": null,
  "message": "Show me my tasks"
}
```

---

### Response (200 OK)

**Content-Type**: `application/json`

**Body Schema**:
```typescript
{
  conversation_id: number;        // ID of the conversation (new or existing)
  message: {
    role: "assistant";
    content: string;              // Assistant's response text
  };
  tool_calls: Array<{             // Tools invoked during processing
    tool: string;                 // Tool name (e.g., "add_task")
    arguments: Record<string, any>; // Tool input parameters
    result: string;               // Tool execution result
  }>;
  created_at: string;             // ISO 8601 timestamp
}
```

**Example Response**:
```json
{
  "conversation_id": 42,
  "message": {
    "role": "assistant",
    "content": "I've added 'Buy groceries' to your task list."
  },
  "tool_calls": [
    {
      "tool": "add_task",
      "arguments": {
        "user_id": 123,
        "title": "Buy groceries",
        "description": null
      },
      "result": "Task 'Buy groceries' has been added."
    }
  ],
  "created_at": "2026-01-11T14:30:00Z"
}
```

**Example Response (Multiple Tools)**:
```json
{
  "conversation_id": 42,
  "message": {
    "role": "assistant",
    "content": "Here are your pending tasks:\n• [ID: 1] Buy groceries\n• [ID: 2] Call dentist\n\nYou have 2 pending tasks."
  },
  "tool_calls": [
    {
      "tool": "list_tasks",
      "arguments": {
        "user_id": 123,
        "status": "pending"
      },
      "result": "• [ID: 1] Buy groceries - pending\n• [ID: 2] Call dentist - pending"
    }
  ],
  "created_at": "2026-01-11T14:31:00Z"
}
```

---

### Error Responses

#### 400 Bad Request

**Cause**: Invalid request body or validation failure

**Response**:
```json
{
  "detail": "Message is required and cannot be empty"
}
```

**Common Validation Errors**:
- Missing `message` field
- Empty or whitespace-only message
- Message exceeds 2000 characters
- Invalid JSON body

---

#### 401 Unauthorized

**Cause**: Missing, invalid, or expired JWT token

**Response**:
```json
{
  "detail": "Invalid or missing authentication token"
}
```

**Triggers**:
- No `Authorization` header
- Invalid JWT signature
- Expired token
- Malformed token

---

#### 404 Not Found

**Cause**: Conversation ID doesn't exist or belongs to another user

**Response**:
```json
{
  "detail": "Conversation not found"
}
```

**Triggers**:
- `conversation_id` doesn't exist in database
- `conversation_id` belongs to different user (enforces user isolation)

---

#### 409 Conflict

**Cause**: Optimistic locking conflict (concurrent request modified conversation)

**Response**:
```json
{
  "detail": "Conversation was modified by another request. Please retry."
}
```

**Triggers**:
- Two simultaneous requests for same conversation
- Version mismatch during update
- Client should retry the request

---

#### 500 Internal Server Error

**Cause**: Unexpected server error (database failure, unhandled exception)

**Response**:
```json
{
  "detail": "An unexpected error occurred. Please try again later."
}
```

**Triggers**:
- Database connection failure (after retry exhaustion)
- Unhandled exception in application code
- Critical system failure

---

#### 503 Service Unavailable

**Cause**: AI service timeout or unavailability

**Response**:
```json
{
  "detail": "The assistant is taking longer than expected. Please try again."
}
```

**Triggers**:
- OpenAI API timeout (>5 seconds)
- OpenAI API rate limit exceeded
- OpenAI API service outage

**Note**: User's message is already saved; retry will include it in conversation history.

---

## Request Flow

1. **Authentication**: Verify JWT and extract `user_id`
2. **Validation**: Validate request body (message length, conversation ownership)
3. **Conversation Lookup/Create**:
   - If `conversation_id` provided: Load conversation (verify user ownership)
   - If `conversation_id` null: Create new conversation for user
4. **Load History**: Fetch last 50 messages from conversation (sliding window)
5. **Persist User Message**: Save user's message to database (two-phase persistence)
6. **Run AI Agent**: Execute agent with conversation history and MCP tools (5-second timeout)
7. **Persist Assistant Response**: Save assistant's message and tool calls to database
8. **Update Conversation**: Increment version, update timestamp (optimistic locking)
9. **Return Response**: Send assistant message and tool call details to client

---

## Concurrency Handling

**Strategy**: Optimistic locking with version numbers

**Behavior**:
- Multiple simultaneous requests for same conversation detected via version mismatch
- First request succeeds, subsequent requests receive 409 Conflict
- Client retries automatically with updated conversation state

**Example Scenario**:
1. Request A and Request B arrive simultaneously for conversation (version=5)
2. Request A completes first, updates conversation to version=6
3. Request B attempts update with version=5, detects mismatch
4. Request B returns 409 Conflict
5. Client retries Request B, loads conversation (now version=6), succeeds

---

## Performance Characteristics

**Target Latency**:
- Simple operations (create task): <3 seconds (p95)
- Complex operations (list + analyze): <5 seconds (p95)
- Database queries: <500ms each
- History loading (50 messages): <1 second

**Timeout Behavior**:
- AI service timeout: 5 seconds
- Database retry: 3 attempts with exponential backoff (100ms, 500ms, 1000ms)
- Total request timeout: ~7 seconds maximum

**Throughput**:
- Support 100 concurrent users
- No rate limiting in Phase 3 (future consideration)

---

## Security Guarantees

1. **User Isolation**: Users can only access their own conversations and messages
2. **JWT Verification**: All requests require valid, signed JWT
3. **No Client-Provided user_id**: User ID extracted from verified JWT only
4. **Tool Execution**: All MCP tools enforce user_id filtering
5. **No Data Leakage**: Conversation IDs are not guessable; ownership verified on every request

---

## Tool Transparency

**Requirement**: All tool invocations MUST be returned in the response

**Purpose**:
- Debugging: Developers can see what tools were called
- Transparency: Users understand what actions were taken
- Audit: Tool calls logged for compliance and troubleshooting

**Format**:
```json
{
  "tool_calls": [
    {
      "tool": "tool_name",
      "arguments": { /* input params */ },
      "result": "human-readable result"
    }
  ]
}
```

---

## Versioning

**Current Version**: 1.0.0

**Breaking Changes** (require version bump):
- Changing request/response schema
- Removing fields
- Changing authentication mechanism
- Modifying error codes

**Non-Breaking Changes** (no version bump):
- Adding optional fields
- Adding new error codes
- Performance improvements
- Bug fixes

**Version Header** (future):
```
API-Version: 1.0.0
```

---

## Testing Requirements

### Contract Tests

1. **Request Validation**:
   - Empty message rejected (400)
   - Message >2000 chars rejected (400)
   - Invalid conversation_id rejected (404)
   - Missing auth token rejected (401)

2. **Response Format**:
   - All required fields present
   - Tool calls array populated correctly
   - Timestamps in ISO 8601 format

3. **User Isolation**:
   - User A cannot access User B's conversation (404)
   - Conversation ID ownership verified

4. **Concurrency**:
   - Simultaneous requests handled correctly (409 on conflict)
   - Retry succeeds after conflict

5. **Error Handling**:
   - AI timeout returns 503 with friendly message
   - Database failure returns 500 after retries
   - User message preserved on AI failure

---

## Example Integration (Frontend)

```typescript
// Frontend API client
async function sendChatMessage(
  conversationId: number | null,
  message: string
): Promise<ChatResponse> {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getAuthToken()}`
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

---

## Future Enhancements

1. **Streaming Responses**: Server-Sent Events for real-time assistant responses
2. **Rate Limiting**: Per-user request limits to prevent abuse
3. **Conversation Metadata**: Title, tags, archived status
4. **Message Reactions**: User feedback on assistant responses
5. **Multi-Modal**: Support for images and file attachments
6. **Conversation Search**: Full-text search across message history
