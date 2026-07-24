"""
MCP Task Tools - FastMCP tool definitions for task management

Owner: @mcp-expert
Task: T317

Provides MCP tools for:
- Creating tasks (add_task)
- Listing tasks (list_tasks)
- Completing tasks (complete_task)
- Deleting tasks (delete_task)
- Updating tasks (update_task)

CRITICAL ARCHITECTURE RULES:
1. MCP tools are the ONLY layer allowed to mutate task data
2. All tools MUST enforce user_id isolation
3. All tools MUST use retry logic for transient failures
4. All tools return human-readable strings for agent responses
5. Tools are stateless - no in-memory state

Per Constitution Principle III: All database operations MUST be scoped to authenticated user.
"""

try:
    from fastmcp import FastMCP
except Exception:
    from fastmcp.server.server import FastMCP

from sqlmodel import Session, select
from typing import Optional

try:
    from backend.models.task import Task
    from backend.mcp_tools.db_utils import get_mcp_session, with_db_retry
except ModuleNotFoundError:
    from models.task import Task
    from mcp_tools.db_utils import get_mcp_session, with_db_retry

# Initialize FastMCP instance
mcp = FastMCP("TaskOperations")


@mcp.tool()
def add_task(user_id: int, title: str, description: Optional[str] = None) -> str:
    """
    Add a new task for the user.

    Args:
        user_id: ID of the authenticated user (from JWT)
        title: Task title (required)
        description: Optional task description

    Returns:
        Human-readable success message
    """
    @with_db_retry
    def _create_task(session: Session) -> Task:
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            completed=False
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

    with get_mcp_session() as session:
        task = _create_task(session)
        return f"Successfully created task: {task.title}"


@mcp.tool()
def list_tasks(user_id: int, status: str = "all") -> str:
    """
    List tasks for the user.

    Args:
        user_id: ID of the authenticated user (from JWT)
        status: Filter by status - "all", "pending", or "completed"

    Returns:
        Human-readable task list or empty message
    """
    @with_db_retry
    def _fetch_tasks(session: Session) -> list[Task]:
        query = select(Task).where(Task.user_id == user_id)

        if status == "pending":
            query = query.where(Task.completed == False)
        elif status == "completed":
            query = query.where(Task.completed == True)

        tasks = session.exec(query).all()
        return list(tasks)

    with get_mcp_session() as session:
        tasks = _fetch_tasks(session)
        if not tasks:
            return "No tasks found."

        task_lines = []
        for i, t in enumerate(tasks, 1):
            status_str = "[X]" if t.completed else "[ ]"
            desc_str = f" - {t.description}" if t.description else ""
            task_lines.append(f"{i}. {status_str} (ID: {t.id}) {t.title}{desc_str}")

        return f"Found {len(tasks)} task(s):\n" + "\n".join(task_lines)


@mcp.tool()
def complete_task(user_id: int, task_id: int) -> str:
    """
    Mark a task as completed for the user.

    Args:
        user_id: ID of the authenticated user (from JWT)
        task_id: ID of the task to complete

    Returns:
        Human-readable success or error message
    """
    @with_db_retry
    def _mark_completed(session: Session) -> Optional[Task]:
        task = session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).first()

        if task:
            task.completed = True
            session.add(task)
            session.commit()
            session.refresh(task)
        return task

    with get_mcp_session() as session:
        task = _mark_completed(session)
        if not task:
            return f"Error: Task with ID {task_id} not found."
        return f"Successfully marked task '{task.title}' as completed."


@mcp.tool()
def delete_task(user_id: int, task_id: int) -> str:
    """
    Delete a task for the user.

    Args:
        user_id: ID of the authenticated user (from JWT)
        task_id: ID of the task to delete

    Returns:
        Human-readable success or error message
    """
    @with_db_retry
    def _delete_task(session: Session) -> Optional[str]:
        task = session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).first()

        if task:
            title = task.title
            session.delete(task)
            session.commit()
            return title
        return None

    with get_mcp_session() as session:
        title = _delete_task(session)
        if not title:
            return f"Error: Task with ID {task_id} not found."
        return f"Successfully deleted task '{title}'."


@mcp.tool()
def update_task(
    user_id: int,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> str:
    """
    Update a task's title or description.

    Args:
        user_id: ID of the authenticated user (from JWT)
        task_id: ID of the task to update
        title: New title (optional)
        description: New description (optional)

    Returns:
        Human-readable success or error message
    """
    @with_db_retry
    def _update_task(session: Session) -> Optional[Task]:
        task = session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).first()

        if task:
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            session.add(task)
            session.commit()
            session.refresh(task)
        return task

    with get_mcp_session() as session:
        task = _update_task(session)
        if not task:
            return f"Error: Task with ID {task_id} not found."
        return f"Successfully updated task #{task.id}."
