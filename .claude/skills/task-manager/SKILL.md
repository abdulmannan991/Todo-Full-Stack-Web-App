# Task Manager Skill

## Objective
Create a specialized skill to manage task operations using the Official MCP SDK (FastMCP) and SQLModel.

## Metadata

**Name**: task-manager

**Description**: A technical skill for executing Task CRUD (Create, Read, Update, Delete) operations. This skill provides the "hands" for the Flow Assistant.

## Instruction for Claude

Use the following Python logic to implement the tools for this skill. Ensure all tools are asynchronous and follow the Zero-Trust Multi-Tenancy rule by requiring a user_id for every database operation.

```python
from fastmcp import FastMCP
from sqlmodel import Session, select
from backend.models.task import Task, TaskStatus # Reference existing model

mcp = FastMCP("TaskOperations")

@mcp.tool()
async def add_task(user_id: int, title: str, description: str = None) -> str:
    """Skill to add a new task. Use when user wants to remember or create a todo."""
    # Implementation: Insert task with user_id into Neon DB
    return f"Task '{title}' has been added."

@mcp.tool()
async def list_tasks(user_id: int, status: str = "all") -> str:
    """Skill to retrieve tasks. Use to show pending or completed todos."""
    # Implementation: Query tasks where Task.user_id == user_id
    return "List of tasks formatted as text..."

@mcp.tool()
async def complete_task(user_id: int, task_id: int) -> str:
    """Skill to mark task as done. Use when user says 'complete' or 'finished'."""
    # Implementation: Update Task status to 'completed' for given task_id
    return f"Task {task_id} marked as complete."

@mcp.tool()
async def delete_task(user_id: int, task_id: int) -> str:
    """Skill to remove a task. Use when user says 'delete' or 'remove'."""
    # Implementation: Delete record where Task.id == task_id
    return f"Task {task_id} has been deleted."
```

In the `list_tasks` implementation, format the list as a clean, bulleted string (e.g., '• [ID: 1] Buy Milk - pending'). If no tasks are found, return 'You have no tasks in your list yet.'

## Constraints

- **Statelessness**: Every tool call must initialize its own database session and close it upon completion.
- **Context**: Return concise, high-signal text responses to the agent. Do not return raw JSON unless requested.
