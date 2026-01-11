# Data Model: AI-Powered Todo Chatbot

**Feature**: 001-ai-chatbot-mcp
**Date**: 2026-01-11
**Purpose**: Define database schema for conversations and messages with user isolation and optimistic locking.

## Entity Relationship Diagram

```
User (existing)
  ↓ 1:N
Conversation (new)
  ↓ 1:N
Message (new)

Task (existing) - referenced by MCP tools, no schema changes
```

## Entities

### Conversation

Represents a chat session between a user and the AI assistant.

**Table Name**: `conversation`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PRIMARY KEY, AUTO_INCREMENT | Unique conversation identifier |
| `user_id` | Integer | FOREIGN KEY → user.id, NOT NULL, INDEXED | Owner of the conversation (enforces user isolation) |
| `version` | Integer | NOT NULL, DEFAULT 1 | Optimistic locking version number (incremented on each update) |
| `created_at` | Timestamp | NOT NULL, DEFAULT CURRENT_TIMESTAMP | When conversation was created |
| `updated_at` | Timestamp | NOT NULL, DEFAULT CURRENT_TIMESTAMP | When conversation was last modified |

**Indexes**:
- Primary: `id`
- Foreign Key: `user_id` → `user.id`
- Query Optimization: `(user_id, updated_at DESC)` for listing user's conversations

**Validation Rules**:
- `user_id` must reference existing user
- `version` must be positive integer
- `updated_at` must be >= `created_at`

**State Transitions**:
- Created: New conversation initialized with version=1
- Updated: Version incremented on each message addition
- No deletion: Conversations retained indefinitely (per spec)

**SQLModel Definition**:
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

**User Isolation**:
- ALL queries MUST filter by `user_id`
- Example: `select(Conversation).where(Conversation.user_id == current_user.id)`

---

### Message

Represents a single message in a conversation (user or assistant).

**Table Name**: `message`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PRIMARY KEY, AUTO_INCREMENT | Unique message identifier |
| `conversation_id` | Integer | FOREIGN KEY → conversation.id, NOT NULL, INDEXED | Parent conversation |
| `user_id` | Integer | FOREIGN KEY → user.id, NOT NULL, INDEXED | Owner of the conversation (denormalized for query efficiency) |
| `role` | String(20) | NOT NULL, CHECK IN ('user', 'assistant') | Message sender role |
| `content` | Text | NOT NULL | Message text content |
| `tool_calls` | JSON | NULLABLE | Tool invocations made by assistant (for transparency) |
| `created_at` | Timestamp | NOT NULL, DEFAULT CURRENT_TIMESTAMP | When message was created |

**Indexes**:
- Primary: `id`
- Foreign Keys: `conversation_id` → `conversation.id`, `user_id` → `user.id`
- Query Optimization: `(conversation_id, created_at ASC)` for loading conversation history
- User Isolation: `(user_id, conversation_id)` for filtering

**Validation Rules**:
- `conversation_id` must reference existing conversation
- `user_id` must match conversation's user_id (enforced in application logic)
- `role` must be either 'user' or 'assistant'
- `content` must not be empty (min length: 1)
- `tool_calls` must be valid JSON array if present

**State Transitions**:
- Created: Message added to conversation
- Immutable: Messages never updated or deleted (append-only log)

**SQLModel Definition**:
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

**User Isolation**:
- ALL queries MUST filter by `user_id`
- Example: `select(Message).where(Message.user_id == current_user.id).where(Message.conversation_id == conv_id)`

---

## Relationships

### User → Conversation (1:N)
- One user can have multiple conversations
- Each conversation belongs to exactly one user
- Cascade: Conversations retained even if user deleted (soft delete recommended)

### Conversation → Message (1:N)
- One conversation contains multiple messages
- Each message belongs to exactly one conversation
- Cascade: Messages deleted if conversation deleted (though deletion not in scope)

### User → Message (1:N - Denormalized)
- `user_id` denormalized in Message for query efficiency
- Enables fast user isolation filtering without joining Conversation table
- Must match parent Conversation's user_id (enforced in application)

---

## Migration Strategy

**Approach**: Additive only (no destructive changes per constitution)

**Migration Script** (Alembic):
```python
def upgrade():
    # Create conversation table
    op.create_table(
        'conversation',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        if_exists='skip'  # Safe for re-runs
    )
    op.create_index('ix_conversation_user_id', 'conversation', ['user_id'])
    op.create_index('ix_conversation_user_updated', 'conversation', ['user_id', 'updated_at'])

    # Create message table
    op.create_table(
        'message',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tool_calls', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversation.id']),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.CheckConstraint("role IN ('user', 'assistant')", name='check_message_role'),
        if_exists='skip'
    )
    op.create_index('ix_message_conversation_id', 'message', ['conversation_id'])
    op.create_index('ix_message_user_id', 'message', ['user_id'])
    op.create_index('ix_message_conversation_created', 'message', ['conversation_id', 'created_at'])

def downgrade():
    # Not implemented - migrations are additive only
    pass
```

**Rollback Strategy**: Not applicable (additive migrations only per constitution)

---

## Data Volume Estimates

**Assumptions**:
- 1,000 active users
- Average 10 conversations per user
- Average 20 messages per conversation
- Average message size: 200 bytes

**Storage Estimates**:
- Conversations: 10,000 rows × 100 bytes = 1 MB
- Messages: 200,000 rows × 250 bytes = 50 MB
- Total: ~51 MB (negligible for Neon PostgreSQL)

**Query Performance**:
- Conversation lookup by user_id: <10ms (indexed)
- Message history load (50 messages): <50ms (indexed, limited)
- Concurrent writes: Handled by optimistic locking

---

## Data Retention Policy

**Current Scope**: Indefinite retention (per spec)

**Future Considerations**:
- Archive conversations older than 1 year
- Implement soft delete for user-requested deletions
- GDPR compliance: Export and delete user data on request

---

## Security Considerations

1. **User Isolation**: All queries filtered by `user_id` from verified JWT
2. **No Direct Access**: Frontend never queries database directly (API only)
3. **Content Sanitization**: Message content stored as plain text (no XSS risk in database)
4. **Tool Call Transparency**: Tool invocations logged for debugging and audit
5. **No PII in Logs**: Message content not logged in application logs

---

## Testing Requirements

1. **Unit Tests**:
   - Conversation creation with user_id
   - Message creation with role validation
   - Optimistic locking version increment

2. **Integration Tests**:
   - User A cannot access User B's conversations
   - User A cannot access User B's messages
   - Concurrent message creation handled correctly

3. **Performance Tests**:
   - Load 50 messages in <50ms
   - Create conversation in <10ms
   - Handle 100 concurrent message writes

---

## Next Steps

1. Implement SQLModel entities in `backend/models/`
2. Create Alembic migration script
3. Add database session management for MCP tools
4. Implement user isolation in all queries
5. Add integration tests for data isolation
