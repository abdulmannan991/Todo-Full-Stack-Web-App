"""
Task Agent - AI agent for conversational task management using OpenAI Agents SDK + Gemini

Owner: @agent-expert, @mcp-expert
Tasks: T339, T340, T341, T342, T343, T344

CRITICAL ARCHITECTURE:
- Uses OpenAI Agents SDK (openai-agents package) for agent orchestration
- AsyncOpenAI client pointed at Google's Gemini OpenAI-compatible endpoint
- Imports google_gemini_config from Os_config/setup_config.py
- Integrates MCP tools for task operations
- Enforces user_id isolation by passing user_id to all tools

Per Master Architect Command:
- Framework: OpenAI Agents SDK (NOT native google-generativeai)
- Endpoint: https://generativelanguage.googleapis.com/v1beta/openai/
- Model: gemini-1.5-flash via OpenAIChatCompletionsModel wrapper
"""

import asyncio
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from Os_config.setup_config import get_gemini_config
from backend.mcp.task_tools import add_task, list_tasks, complete_task, delete_task, update_task


class TaskAgent:
    """
    AI agent for conversational task management.

    Uses OpenAI Agents SDK with Gemini backend for natural language
    task management with tool calling capabilities.
    """

    def __init__(self):
        """Initialize the task agent with Gemini configuration."""
        # Get Gemini configuration
        self.config = get_gemini_config()

        # Initialize AsyncOpenAI client with Gemini endpoint
        openai_config = self.config.get_async_openai_config()
        self.client = AsyncOpenAI(**openai_config)

        # Get model configuration
        self.model_config = self.config.get_model_config()

        # Agent instructions
        self.system_instructions = """You are a helpful task management assistant. You help users manage their todo tasks through natural language commands.

Your capabilities:
- Create new tasks with titles and optional descriptions
- List tasks (all, pending, or completed)
- Mark tasks as complete
- Delete tasks
- Update task titles and descriptions

Guidelines:
- Be conversational and friendly
- Ask for clarification when commands are ambiguous
- Confirm actions after completing them
- Use the provided tools to interact with the task database
- Always reference tasks by their ID when performing operations
- When listing tasks, present them in a clear, numbered format

Remember: You can only access and modify tasks for the current user."""

    async def run(
        self,
        user_id: int,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        timeout: float = 5.0
    ) -> Dict[str, Any]:
        """
        Run the agent with a user message and conversation history.

        Args:
            user_id: ID of the authenticated user (for tool isolation)
            user_message: The user's message
            conversation_history: List of previous messages [{"role": "user"|"assistant", "content": "..."}]
            timeout: Maximum execution time in seconds (default: 5.0)

        Returns:
            Dict with:
                - content: Assistant's response text
                - tool_calls: List of tool invocations made

        Raises:
            asyncio.TimeoutError: If execution exceeds timeout
            Exception: For other errors during execution
        """
        try:
            # Build messages for the API call
            messages = [
                {"role": "system", "content": self.system_instructions}
            ]

            # Add conversation history
            messages.extend(conversation_history)

            # Add current user message
            messages.append({"role": "user", "content": user_message})

            # Define tools for the agent
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "add_task",
                        "description": "Add a new task for the user",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "string",
                                    "description": "Task title (required)"
                                },
                                "description": {
                                    "type": "string",
                                    "description": "Optional task description"
                                }
                            },
                            "required": ["title"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "list_tasks",
                        "description": "List tasks for the user",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "status": {
                                    "type": "string",
                                    "enum": ["all", "pending", "completed"],
                                    "description": "Filter by status (default: all)"
                                }
                            }
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "complete_task",
                        "description": "Mark a task as complete by ID or title. Users typically don't know IDs, so prefer using title.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "task_id": {
                                    "type": "integer",
                                    "description": "ID of the task to complete (optional if title provided)"
                                },
                                "title": {
                                    "type": "string",
                                    "description": "Title or partial title of the task to complete (optional if task_id provided)"
                                }
                            }
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "delete_task",
                        "description": "Delete a task by ID or title. Users typically don't know IDs, so prefer using title.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "task_id": {
                                    "type": "integer",
                                    "description": "ID of the task to delete (optional if title provided)"
                                },
                                "title": {
                                    "type": "string",
                                    "description": "Title or partial title of the task to delete (optional if task_id provided)"
                                }
                            }
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "update_task",
                        "description": "Update a task's title and/or description",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "task_id": {
                                    "type": "integer",
                                    "description": "ID of the task to update"
                                },
                                "title": {
                                    "type": "string",
                                    "description": "New title (optional)"
                                },
                                "description": {
                                    "type": "string",
                                    "description": "New description (optional)"
                                }
                            },
                            "required": ["task_id"]
                        }
                    }
                }
            ]

            # Execute with timeout
            response = await asyncio.wait_for(
                self._execute_agent(messages, tools, user_id),
                timeout=timeout
            )

            return response

        except asyncio.TimeoutError:
            raise
        except Exception as e:
            raise Exception(f"Agent execution failed: {str(e)}")

    async def _execute_agent(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        user_id: int
    ) -> Dict[str, Any]:
        """
        Execute the agent with tool calling support.

        This method handles the agent loop:
        1. Call the model with tools
        2. If tool calls are requested, execute them
        3. Add tool results to messages
        4. Call the model again with tool results
        5. Repeat until no more tool calls

        Args:
            messages: Conversation messages
            tools: Available tools
            user_id: User ID for tool isolation

        Returns:
            Dict with content and tool_calls
        """
        tool_calls_made = []
        max_iterations = 5  # Prevent infinite loops

        for iteration in range(max_iterations):
            # Call the model
            response = await self.client.chat.completions.create(
                model=self.model_config["model"],
                messages=messages,
                tools=tools,
                temperature=self.model_config["temperature"],
                max_tokens=self.model_config["max_tokens"]
            )

            message = response.choices[0].message

            # Check if tool calls were requested
            if message.tool_calls:
                # Execute tool calls
                messages.append({
                    "role": "assistant",
                    "content": message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in message.tool_calls
                    ]
                })

                # Execute each tool call
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = eval(tool_call.function.arguments)  # Parse JSON string

                    # Add user_id to all tool calls for isolation
                    function_args["user_id"] = user_id

                    # Execute the tool
                    result = await self._execute_tool(function_name, function_args)

                    # Record tool call for transparency
                    tool_calls_made.append({
                        "tool": function_name,
                        "arguments": function_args,
                        "result": result
                    })

                    # Add tool result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result
                    })

                # Continue loop to get final response
                continue
            else:
                # No more tool calls, return final response
                return {
                    "content": message.content or "I'm here to help with your tasks!",
                    "tool_calls": tool_calls_made
                }

        # Max iterations reached
        return {
            "content": "I've completed the requested operations.",
            "tool_calls": tool_calls_made
        }

    async def _execute_tool(self, function_name: str, function_args: Dict[str, Any]) -> str:
        """
        Execute a tool function.

        Args:
            function_name: Name of the tool to execute
            function_args: Arguments for the tool (includes user_id)

        Returns:
            Tool execution result as string
        """
        # Map function names to actual functions
        # Note: MCP tools are wrapped by @mcp.tool() decorator, so we need to access the underlying function
        tool_map = {
            "add_task": add_task.fn if hasattr(add_task, 'fn') else add_task,
            "list_tasks": list_tasks.fn if hasattr(list_tasks, 'fn') else list_tasks,
            "complete_task": complete_task.fn if hasattr(complete_task, 'fn') else complete_task,
            "delete_task": delete_task.fn if hasattr(delete_task, 'fn') else delete_task,
            "update_task": update_task.fn if hasattr(update_task, 'fn') else update_task
        }

        if function_name not in tool_map:
            return f"Error: Unknown tool '{function_name}'"

        try:
            # Execute the tool (MCP tools are synchronous)
            tool_function = tool_map[function_name]
            result = tool_function(**function_args)
            return result
        except Exception as e:
            return f"Error executing {function_name}: {str(e)}"


# Global agent instance (stateless, can be reused)
_task_agent: Optional[TaskAgent] = None


def get_task_agent() -> TaskAgent:
    """
    Get or create the global task agent instance.

    Returns:
        TaskAgent instance
    """
    global _task_agent
    if _task_agent is None:
        _task_agent = TaskAgent()
    return _task_agent
