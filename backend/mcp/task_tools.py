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

from fastmcp import FastMCP
from sqlmodel import Session, select
from typing import Optional
from backend.models.task import Task
from backend.mcp.db_utils import get_mcp_session, with_db_retry

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

    Example:
        add_task(user_id=1, title="Buy groceries", description="Milk, eggs, bread")
        -> "Task 'Buy groceries' has been added."
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

    Example:
        list_tasks(user_id=1, status="pending")
        -> "You have 2 pending tasks:\n1. Buy groceries\n2. Call dentist"
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
            if status == "all":
                return "You don't have any tasks yet."
            elif status == "pending":
                return "You don't have any pending tasks."
            else:
                return "You don't have any completed tasks."

        # Format task list
        status_label = status if status != "all" else ""
        task_list = [f"{i+1}. {task.title} (ID: {task.id})" for i, task in enumerate(tasks)]

        count = len(tasks)
        header = f"You have {count} {status_label} task{'s' if count != 1 else ''}:\n"
        return header + "\n".join(task_list)


@mcp.tool()
def complete_task(user_id: int, task_id: Optional[int] = None, title: Optional[str] = None) -> str:
    """
    Mark a task as complete by ID or title.

    Args:
        user_id: ID of the authenticated user (from JWT)
        task_id: ID of the task to complete (optional if title provided)
        title: Title of the task to complete (optional if task_id provided)

    Returns:
        Human-readable success or error message

    Example:
        complete_task(user_id=1, title="Buy groceries")
        -> "Successfully marked task 'Buy groceries' as completed."
    """
    from backend.models.task import TaskStatus

    @with_db_retry
    def _complete_task(session: Session) -> tuple[Optional[Task], Optional[str]]:
        # Search by ID if provided
        if task_id is not None:
            task = session.exec(
                select(Task)
                .where(Task.id == task_id)
                .where(Task.user_id == user_id)
            ).first()

            if not task:
                return None, f"Task with ID {task_id} not found."

            task.status = TaskStatus.completed
            session.add(task)
            session.commit()
            session.refresh(task)
            return task, None

        # Search by title if provided
        if title is not None:
            tasks = session.exec(
                select(Task)
                .where(Task.title.ilike(f"%{title}%"))
                .where(Task.user_id == user_id)
            ).all()

            if len(tasks) == 0:
                return None, f"I couldn't find a task with the title '{title}'."

            if len(tasks) > 1:
                task_list = ", ".join([f"ID {t.id}: {t.title}" for t in tasks])
                return None, f"Multiple tasks found: {task_list}. Please provide the specific ID to complete."

            # Exactly one match
            task = tasks[0]
            task.status = TaskStatus.completed
            session.add(task)
            session.commit()
            session.refresh(task)
            return task, None

        return None, "Please provide either a task_id or title to complete."

    with get_mcp_session() as session:
        task, error = _complete_task(session)

        if error:
            return error

        return f"Successfully marked task '{task.title}' as completed."


@mcp.tool()
def delete_task(user_id: int, task_id: Optional[int] = None, title: Optional[str] = None) -> str:
    """
    Delete a task by ID or title.

    Args:
        user_id: ID of the authenticated user (from JWT)
        task_id: ID of the task to delete (optional if title provided)
        title: Title of the task to delete (optional if task_id provided)

    Returns:
        Human-readable success or error message

    Example:
        delete_task(user_id=1, title="Buy groceries")
        -> "Successfully deleted task with ID 5"
    """
    @with_db_retry
    def _delete_task(session: Session) -> tuple[Optional[int], Optional[str], Optional[str]]:
        # Search by ID if provided
        if task_id is not None:
            task = session.exec(
                select(Task)
                .where(Task.id == task_id)
                .where(Task.user_id == user_id)
            ).first()

            if not task:
                return None, None, f"Task with ID {task_id} not found."

            task_title = task.title
            task_id_val = task.id
            session.delete(task)
            session.commit()
            return task_id_val, task_title, None

        # Search by title if provided
        if title is not None:
            tasks = session.exec(
                select(Task)
                .where(Task.title.ilike(f"%{title}%"))
                .where(Task.user_id == user_id)
            ).all()

            if len(tasks) == 0:
                return None, None, f"I couldn't find a task with the title '{title}'."

            if len(tasks) > 1:
                task_list = ", ".join([f"ID {t.id}: {t.title}" for t in tasks])
                return None, None, f"Multiple tasks found: {task_list}. Please provide the specific ID to delete."

            # Exactly one match
            task = tasks[0]
            task_title = task.title
            task_id_val = task.id
            session.delete(task)
            session.commit()
            return task_id_val, task_title, None

        return None, None, "Please provide either a task_id or title to delete."

    with get_mcp_session() as session:
        deleted_id, deleted_title, error = _delete_task(session)

        if error:
            return error

        return f"Successfully deleted task with ID {deleted_id}"


@mcp.tool()
def update_task(
    user_id: int,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> str:
    """
    Update a task's title and/or description.

    Args:
        user_id: ID of the authenticated user (from JWT)
        task_id: ID of the task to update
        title: New title (optional)
        description: New description (optional)

    Returns:
        Human-readable success or error message

    Example:
        update_task(user_id=1, task_id=5, title="Buy groceries and cook dinner")
        -> "Task has been updated to 'Buy groceries and cook dinner'."
    """
    @with_db_retry
    def _update_task(session: Session) -> Optional[Task]:
        task = session.exec(
            select(Task)
            .where(Task.id == task_id)
            .where(Task.user_id == user_id)
        ).first()

        if not task:
            return None

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
            return f"Task with ID {task_id} not found."

        return f"Successfully updated task '{task.title}'"
