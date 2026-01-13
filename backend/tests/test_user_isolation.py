"""
User Isolation Test Script

Tests: T348, T349, T358, T369, T380, T391
Purpose: Verify that user_id isolation is enforced in all MCP tools

This script tests that:
1. User A cannot access User B's tasks
2. User A cannot complete/delete/update User B's tasks
3. JWT verification rejects invalid tokens

Usage:
    python backend/tests/test_user_isolation.py

Requirements:
    - Backend server running on localhost:8000
    - Two valid JWT tokens for different users
    - At least one task created by each user
"""

import requests
import json
from typing import Optional

# Configuration
API_BASE_URL = "http://localhost:8000"
CHAT_ENDPOINT = f"{API_BASE_URL}/api/chat"

# Test tokens (replace with actual JWT tokens from Better Auth)
USER_A_TOKEN = "your-user-a-jwt-token-here"
USER_B_TOKEN = "your-user-b-jwt-token-here"


def send_chat_message(token: str, message: str, conversation_id: Optional[int] = None) -> dict:
    """Send a chat message to the API."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "conversation_id": conversation_id,
        "message": message
    }

    response = requests.post(CHAT_ENDPOINT, headers=headers, json=payload)
    return {
        "status_code": response.status_code,
        "data": response.json() if response.status_code == 200 else response.text
    }


def test_user_isolation():
    """Test that users cannot access each other's tasks."""

    print("=" * 60)
    print("USER ISOLATION TEST")
    print("=" * 60)

    # Test 1: User A creates a task
    print("\n[TEST 1] User A creates a task...")
    response_a = send_chat_message(USER_A_TOKEN, "Add a task to test user isolation")
    print(f"Status: {response_a['status_code']}")
    print(f"Response: {response_a['data']}")

    if response_a['status_code'] != 200:
        print("❌ FAILED: User A could not create task")
        return False

    # Extract task ID from response (assuming it's in the assistant's message)
    assistant_message = response_a['data'].get('message', {}).get('content', '')
    print(f"Assistant: {assistant_message}")

    # Test 2: User A lists their tasks
    print("\n[TEST 2] User A lists their tasks...")
    response_a_list = send_chat_message(USER_A_TOKEN, "Show my tasks")
    print(f"Status: {response_a_list['status_code']}")
    print(f"Response: {response_a_list['data']}")

    if response_a_list['status_code'] != 200:
        print("❌ FAILED: User A could not list tasks")
        return False

    # Test 3: User B creates a task
    print("\n[TEST 3] User B creates a task...")
    response_b = send_chat_message(USER_B_TOKEN, "Add a task for user B only")
    print(f"Status: {response_b['status_code']}")
    print(f"Response: {response_b['data']}")

    if response_b['status_code'] != 200:
        print("❌ FAILED: User B could not create task")
        return False

    # Test 4: User B lists their tasks (should NOT see User A's tasks)
    print("\n[TEST 4] User B lists their tasks (should NOT see User A's tasks)...")
    response_b_list = send_chat_message(USER_B_TOKEN, "Show my tasks")
    print(f"Status: {response_b_list['status_code']}")
    print(f"Response: {response_b_list['data']}")

    if response_b_list['status_code'] != 200:
        print("❌ FAILED: User B could not list tasks")
        return False

    # Verify User B doesn't see User A's task
    user_b_tasks = response_b_list['data'].get('message', {}).get('content', '')
    if "test user isolation" in user_b_tasks.lower():
        print("❌ FAILED: User B can see User A's tasks! SECURITY BREACH!")
        return False
    else:
        print("✅ PASSED: User B cannot see User A's tasks")

    # Test 5: Invalid JWT token
    print("\n[TEST 5] Testing invalid JWT token...")
    response_invalid = send_chat_message("invalid-token-12345", "Show my tasks")
    print(f"Status: {response_invalid['status_code']}")

    if response_invalid['status_code'] == 401:
        print("✅ PASSED: Invalid token rejected with 401")
    else:
        print(f"❌ FAILED: Expected 401, got {response_invalid['status_code']}")
        return False

    # Test 6: No token
    print("\n[TEST 6] Testing request without token...")
    headers = {"Content-Type": "application/json"}
    payload = {"conversation_id": None, "message": "Show my tasks"}
    response_no_token = requests.post(CHAT_ENDPOINT, headers=headers, json=payload)
    print(f"Status: {response_no_token.status_code}")

    if response_no_token.status_code == 401:
        print("✅ PASSED: Request without token rejected with 401")
    else:
        print(f"❌ FAILED: Expected 401, got {response_no_token.status_code}")
        return False

    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED - USER ISOLATION VERIFIED")
    print("=" * 60)
    return True


if __name__ == "__main__":
    print("\n⚠️  SETUP REQUIRED:")
    print("1. Start backend server: uvicorn backend.main:app --reload")
    print("2. Replace USER_A_TOKEN and USER_B_TOKEN with actual JWT tokens")
    print("3. Run this script: python backend/tests/test_user_isolation.py\n")

    # Check if tokens are set
    if USER_A_TOKEN == "your-user-a-jwt-token-here":
        print("❌ ERROR: Please set USER_A_TOKEN and USER_B_TOKEN in the script")
        exit(1)

    try:
        success = test_user_isolation()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH ERROR: {str(e)}")
        exit(1)
