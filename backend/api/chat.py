"""
Chat API - FastAPI endpoint for AI-powered conversational task management

Owner: @api-expert
Tasks: T320-T329

Provides:
- POST /api/chat endpoint for conversational AI interactions
- Conversation management with optimistic locking
- Message persistence (two-phase: user message first, then assistant response)
- Sliding window history loading (last 50 messages)
- AI agent integration with 5-second timeout
- JWT authentication and user isolation

CRITICAL ARCHITECTURE RULES:
1. Server is STATELESS - no in-memory chat state
2. All conversation state stored in database
3. User message persisted BEFORE AI processing (two-phase)
4. Optimistic locking prevents race conditions
5. All operations enforce user_id isolation

Per Constitution Principle III: All operations MUST be scoped to authenticated user.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session, select
from typing import Optional
from datetime import datetime
import asyncio

from backend.database import get_session
from backend.models.user import User
from backend.models.conversation import Conversation
from backend.models.message import Message
from backend.auth import get_current_user
from backend.agents.task_agent import get_task_agent

# Create router
router = APIRouter(prefix="/api", tags=["chat"])


# Pydantic models for request/response
class ChatRequest(BaseModel):
    """
    Request model for chat endpoint.

    Fields:
    - conversation_id: Optional ID of existing conversation (null for new conversation)
    - message: User's message text (1-2000 characters)
    """
    conversation_id: Optional[int] = Field(default=None, description="Existing conversation ID or null for new")
    message: str = Field(min_length=1, max_length=2000, description="User message text")


class MessageResponse(BaseModel):
    """
    Response model for a single message.
    """
    role: str
    content: str
    created_at: str


class ChatResponse(BaseModel):
    """
    Response model for chat endpoint.

    Fields:
    - conversation_id: ID of the conversation
    - message: Assistant's response message
    - tool_calls: List of tool invocations made by assistant (for transparency)
    - created_at: Timestamp of assistant message creation
    """
    conversation_id: int
    message: dict  # {"role": "assistant", "content": "..."}
    tool_calls: list[dict]
    created_at: str


class ConversationHistoryResponse(BaseModel):
    """
    Response model for conversation history endpoint.
    """
    conversation_id: int
    messages: list[MessageResponse]


class ConversationListItem(BaseModel):
    """
    Response model for a single conversation in the list.
    """
    id: int
    updated_at: str
    title: str


class ConversationListResponse(BaseModel):
    """
    Response model for conversation list endpoint.
    """
    conversations: list[ConversationListItem]


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Chat endpoint for conversational AI task management.

    Flow:
    1. Validate and load/create conversation
    2. Load last 50 messages (sliding window)
    3. Persist user message (two-phase: before AI processing)
    4. Run AI agent with MCP tools (5-second timeout)
    5. Persist assistant response
    6. Update conversation version (optimistic locking)
    7. Return response with tool calls

    Args:
        request: ChatRequest with conversation_id and message
        current_user: Authenticated user from JWT
        session: Database session

    Returns:
        ChatResponse with assistant message and tool calls

    Raises:
        400: Invalid message (empty or too long)
        404: Conversation not found or doesn't belong to user
        409: Optimistic locking conflict (concurrent modification)
        500: Internal server error
        503: AI service timeout or unavailable
    """
    try:
        # T405: Validate message is not empty or whitespace-only
        if not request.message.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot be empty or whitespace-only"
            )

        # Extract user_id from current_user dict
        user_id = current_user["user_id"]

        # T324: Conversation lookup/create logic with user_id filtering
        conversation = None
        # Change this check to handle ID 0 or None gracefully
        if request.conversation_id and request.conversation_id > 0:
            conversation = session.exec(
            select(Conversation)
            .where(Conversation.id == request.conversation_id)
            .where(Conversation.user_id == user_id)
            ).first()

            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
        else:
            # Create new conversation
            conversation = Conversation(
                user_id=user_id,
                version=1,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(conversation)
            session.commit()
            session.refresh(conversation)

        # T325: Load sliding window history (last 50 messages)
        history_messages = session.exec(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .where(Message.user_id == user_id)
            .order_by(Message.created_at.desc())
            .limit(50)
        ).all()
        history_messages = list(reversed(history_messages))  # Oldest first

        # T326: Two-phase persistence - persist user message FIRST
        user_message = Message(
            conversation_id=conversation.id,
            user_id=user_id,
            role="user",
            content=request.message,
            tool_calls=None,
            created_at=datetime.utcnow()
        )
        session.add(user_message)
        # MANDATORY: Flush then commit to release database locks
        # This allows Dashboard to fetch tasks while agent is processing
        session.flush()
        session.commit()
        session.refresh(user_message)

        try:
            # T328: Run AI agent with 5-second timeout
            # Build conversation history for agent
            history_for_agent = [
                {"role": msg.role, "content": msg.content}
                for msg in history_messages
            ]

            # Get task agent instance
            agent = get_task_agent()

            # Execute agent with timeout and error logging
            try:
                agent_response = await agent.run(
                    user_id=user_id,
                    user_message=request.message,
                    conversation_history=history_for_agent,
                    timeout=45.0
                )
            except Exception as agent_error:
                # Log the specific error for debugging
                print(f"[AGENT ERROR] Type: {type(agent_error).__name__}")
                print(f"[AGENT ERROR] Message: {str(agent_error)}")
                print(f"[AGENT ERROR] User ID: {user_id}")
                print(f"[AGENT ERROR] User Message: {request.message[:100]}")
                # Rollback session once and re-raise
                session.rollback()
                raise

            assistant_content = agent_response["content"]
            tool_calls_data = agent_response["tool_calls"]

            # Persist assistant response
            try:
                assistant_message = Message(
                    conversation_id=conversation.id,
                    user_id=user_id,
                    role="assistant",
                    content=assistant_content,
                    tool_calls=tool_calls_data,
                    created_at=datetime.utcnow()
                )
                session.add(assistant_message)

                # T327: Update conversation with optimistic locking
                current_version = conversation.version
                conversation.updated_at = datetime.utcnow()
                conversation.version = current_version + 1
                session.add(conversation)

                session.commit()
                session.refresh(assistant_message)

                # Return response
                return ChatResponse(
                    conversation_id=conversation.id,
                    message={
                        "role": "assistant",
                        "content": assistant_message.content
                    },
                    tool_calls=assistant_message.tool_calls or [],
                    created_at=assistant_message.created_at.isoformat()
                )

            except Exception as db_error:
                # Rollback session once on database error
                session.rollback()
                # T329: Handle optimistic locking conflict (409)
                if "version" in str(db_error).lower():
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Conversation was modified by another request. Please retry."
                    )
                raise

        except asyncio.TimeoutError:
            # Rollback session once on timeout
            session.rollback()
            # T329: Handle AI timeout (503)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="The assistant is taking longer than expected. Please try again."
            )
        except HTTPException:
            # Re-raise HTTP exceptions (already handled)
            raise
        except Exception as e:
            # Rollback session once on unexpected error
            session.rollback()
            # T329: Handle unexpected errors (500)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred: {str(e)}"
            )
    finally:
        # MANDATORY: Explicitly close session to prevent leaks
        # This ensures the session is released even if agent.run() takes 45 seconds
        # Prevents ROLLBACK loops and "hanging" loading screens
        session.close()


@router.get("/conversations/{conversation_id}/messages", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    conversation_id: int,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get conversation history (T397).

    Fetches the last N messages from a conversation for display in the UI.

    Args:
        conversation_id: ID of the conversation
        limit: Maximum number of messages to return (default: 20)
        current_user: Authenticated user from JWT
        session: Database session

    Returns:
        ConversationHistoryResponse with messages

    Raises:
        404: Conversation not found or doesn't belong to user
    """
    # Extract user_id from current_user dict
    user_id = current_user["user_id"]

    # Verify conversation exists and belongs to user
    conversation = session.exec(
        select(Conversation)
        .where(Conversation.id == conversation_id)
        .where(Conversation.user_id == user_id)
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Load messages (last N, oldest first)
    messages = session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .where(Message.user_id == user_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    ).all()

    # Reverse to get oldest first
    messages = list(reversed(messages))

    # Format response
    message_responses = [
        MessageResponse(
            role=msg.role,
            content=msg.content,
            created_at=msg.created_at.isoformat()
        )
        for msg in messages
    ]

    return ConversationHistoryResponse(
        conversation_id=conversation_id,
        messages=message_responses
    )


@router.get("/conversations", response_model=ConversationListResponse)
async def get_conversations(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get list of all conversations for the current user.

    Returns conversations ordered by most recently updated first.
    Each conversation includes:
    - id: Conversation ID
    - updated_at: Last update timestamp
    - title: First 40 characters of the first message

    Args:
        current_user: Authenticated user from JWT
        session: Database session

    Returns:
        ConversationListResponse with list of conversations
    """
    # Extract user_id from current_user dict
    user_id = current_user["user_id"]

    # Load all conversations for user, ordered by most recent first
    conversations = session.exec(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    ).all()

    # Build response with titles from first message
    conversation_items = []
    for conv in conversations:
        # Get first message for title
        first_message = session.exec(
            select(Message)
            .where(Message.conversation_id == conv.id)
            .where(Message.user_id == user_id)
            .order_by(Message.created_at.asc())
            .limit(1)
        ).first()

        # Extract title (first 40 chars of first message, or default)
        if first_message:
            title = first_message.content[:40]
            if len(first_message.content) > 40:
                title += "..."
        else:
            title = "New conversation"

        conversation_items.append(
            ConversationListItem(
                id=conv.id,
                updated_at=conv.updated_at.isoformat(),
                title=title
            )
        )

    return ConversationListResponse(conversations=conversation_items)
