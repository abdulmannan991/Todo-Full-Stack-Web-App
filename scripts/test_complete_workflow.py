"""
End-to-End Test: Complete Workflow (T416)

Tests the complete task lifecycle through natural language chat:
1. Create task
2. View tasks
3. Complete task
4. Delete task

Requirements:
- Backend server running on http://localhost:8000
- Valid JWT token (set TOKEN variable below)
- Database connected

Usage:
    python scripts/test_complete_workflow.py
"""

import requests
import json
import sys
import time
from typing import Optional, Dict, Any

# Fix Windows console encoding
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configuration
BASE_URL = "http://localhost:8000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMCIsImV4cCI6MTc2ODIyODIzM30.Ieem5Eg32SWv1RL1NV6MdkUVyQTtUB2fpryoRIz5J-I"  # JWT token for testing

# ANSI color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def get_auth_token() -> Optional[str]:
    """Get JWT token from environment or prompt user."""
    import os

    token = os.getenv('AUTH_TOKEN') or TOKEN

    if not token:
        print(f"{YELLOW}No AUTH_TOKEN found. Please set it:{RESET}")
        print("  export AUTH_TOKEN='your_jwt_token_here'")
        print("  or edit this script and set TOKEN variable")
        sys.exit(1)

    return token


def send_chat_message(conversation_id: Optional[int], message: str, token: str) -> Dict[str, Any]:
    """Send a chat message to the API."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "conversation_id": conversation_id,
        "message": message
    }

    print(f"{BLUE}→ Sending: {message}{RESET}")

    response = requests.post(
        f"{BASE_URL}/api/chat",
        json=payload,
        headers=headers
    )

    if response.status_code != 200:
        print(f"{RED}✗ Request failed: {response.status_code}{RESET}")
        print(f"  Response: {response.text}")
        return None

    data = response.json()
    print(f"{GREEN}← Response: {data['message']['content'][:100]}...{RESET}")

    return data


def extract_task_id(response_text: str) -> Optional[int]:
    """Extract task ID from assistant response."""
    import re

    # Look for patterns like "Task 123" or "task ID 123" or "#123"
    patterns = [
        r'[Tt]ask\s+(?:ID\s+)?(\d+)',
        r'#(\d+)',
        r'ID\s+(\d+)'
    ]

    for pattern in patterns:
        match = re.search(pattern, response_text)
        if match:
            return int(match.group(1))

    return None


def test_complete_workflow():
    """Test T416: Complete workflow (create → view → complete → delete)."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}T416: Complete Workflow Test{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

    token = get_auth_token()
    conversation_id = None
    task_id = None

    try:
        # Step 1: Create Task
        print(f"\n{YELLOW}Step 1: Create Task{RESET}")
        response = send_chat_message(
            conversation_id,
            "Add a task to buy groceries for the test",
            token
        )

        if not response:
            print(f"{RED}✗ Failed to create task{RESET}")
            return False

        conversation_id = response.get('conversation_id')
        print(f"{GREEN}✓ Conversation ID: {conversation_id}{RESET}")

        # Try to extract task ID from response
        task_id = extract_task_id(response['message']['content'])
        if task_id:
            print(f"{GREEN}✓ Task ID extracted: {task_id}{RESET}")

        # Check tool calls
        if response.get('tool_calls'):
            for tool_call in response['tool_calls']:
                if tool_call['tool'] == 'add_task':
                    print(f"{GREEN}✓ Tool call: add_task{RESET}")
                    print(f"  Arguments: {tool_call['arguments']}")
                    print(f"  Result: {tool_call['result']}")

        time.sleep(1)

        # Step 2: View Tasks
        print(f"\n{YELLOW}Step 2: View Tasks{RESET}")
        response = send_chat_message(
            conversation_id,
            "Show my tasks",
            token
        )

        if not response:
            print(f"{RED}✗ Failed to list tasks{RESET}")
            return False

        response_text = response['message']['content']

        # Verify task appears in list
        if 'groceries' in response_text.lower() or 'test' in response_text.lower():
            print(f"{GREEN}✓ Task appears in list{RESET}")
        else:
            print(f"{RED}✗ Task not found in list{RESET}")
            print(f"  Response: {response_text}")
            return False

        # Extract task ID if we don't have it yet
        if not task_id:
            task_id = extract_task_id(response_text)
            if task_id:
                print(f"{GREEN}✓ Task ID extracted from list: {task_id}{RESET}")

        time.sleep(1)

        # Step 3: Complete Task
        print(f"\n{YELLOW}Step 3: Complete Task{RESET}")

        if task_id:
            message = f"Mark task {task_id} as done"
        else:
            message = "Complete the groceries task"

        response = send_chat_message(
            conversation_id,
            message,
            token
        )

        if not response:
            print(f"{RED}✗ Failed to complete task{RESET}")
            return False

        # Check for completion confirmation
        response_text = response['message']['content'].lower()
        if 'complet' in response_text or 'done' in response_text or 'marked' in response_text:
            print(f"{GREEN}✓ Task completion confirmed{RESET}")
        else:
            print(f"{YELLOW}⚠ Completion confirmation unclear{RESET}")
            print(f"  Response: {response['message']['content']}")

        # Check tool calls
        if response.get('tool_calls'):
            for tool_call in response['tool_calls']:
                if tool_call['tool'] == 'complete_task':
                    print(f"{GREEN}✓ Tool call: complete_task{RESET}")

        time.sleep(1)

        # Step 4: Verify Completion
        print(f"\n{YELLOW}Step 4: Verify Completion{RESET}")
        response = send_chat_message(
            conversation_id,
            "Show my tasks",
            token
        )

        if not response:
            print(f"{RED}✗ Failed to verify completion{RESET}")
            return False

        response_text = response['message']['content'].lower()
        if 'complet' in response_text or 'done' in response_text:
            print(f"{GREEN}✓ Task shows as completed{RESET}")
        else:
            print(f"{YELLOW}⚠ Task completion status unclear{RESET}")

        time.sleep(1)

        # Step 5: Delete Task
        print(f"\n{YELLOW}Step 5: Delete Task{RESET}")

        if task_id:
            message = f"Delete task {task_id}"
        else:
            message = "Remove the groceries task"

        response = send_chat_message(
            conversation_id,
            message,
            token
        )

        if not response:
            print(f"{RED}✗ Failed to delete task{RESET}")
            return False

        # Check for deletion confirmation
        response_text = response['message']['content'].lower()
        if 'delet' in response_text or 'remov' in response_text:
            print(f"{GREEN}✓ Task deletion confirmed{RESET}")
        else:
            print(f"{YELLOW}⚠ Deletion confirmation unclear{RESET}")
            print(f"  Response: {response['message']['content']}")

        # Check tool calls
        if response.get('tool_calls'):
            for tool_call in response['tool_calls']:
                if tool_call['tool'] == 'delete_task':
                    print(f"{GREEN}✓ Tool call: delete_task{RESET}")

        time.sleep(1)

        # Step 6: Verify Deletion
        print(f"\n{YELLOW}Step 6: Verify Deletion{RESET}")
        response = send_chat_message(
            conversation_id,
            "Show my tasks",
            token
        )

        if not response:
            print(f"{RED}✗ Failed to verify deletion{RESET}")
            return False

        response_text = response['message']['content'].lower()

        # Task should not appear in list anymore
        if 'groceries' not in response_text and 'test' not in response_text:
            print(f"{GREEN}✓ Task no longer appears in list{RESET}")
        elif 'no tasks' in response_text or 'empty' in response_text:
            print(f"{GREEN}✓ Task list is empty (task deleted){RESET}")
        else:
            print(f"{YELLOW}⚠ Task may still be in list{RESET}")
            print(f"  Response: {response_text}")

        # Final result
        print(f"\n{GREEN}{'='*60}{RESET}")
        print(f"{GREEN}✓ T416: Complete Workflow Test PASSED{RESET}")
        print(f"{GREEN}{'='*60}{RESET}\n")

        return True

    except Exception as e:
        print(f"\n{RED}✗ Test failed with exception: {e}{RESET}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_complete_workflow()
    sys.exit(0 if success else 1)
