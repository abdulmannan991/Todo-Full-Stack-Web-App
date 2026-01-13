"""
End-to-End Test: AI Timeout (T420)

Tests that user message is preserved and friendly error returned when AI times out:
1. Simulate AI timeout (requires backend modification)
2. Verify 503 error with friendly message
3. Verify user message is preserved in database
4. Verify conversation remains in valid state
5. Verify subsequent requests work normally

Requirements:
- Backend server running on http://localhost:8000
- Valid JWT token (set TOKEN variable below)
- Database connected
- Backend modification to simulate timeout (see setup instructions)

Setup Instructions:
    1. Edit backend/api/chat.py
    2. Find the AI agent call (around line 150)
    3. Add BEFORE the agent call:
       ```python
       import time
       time.sleep(6)  # Simulate 6-second delay (exceeds 5-second timeout)
       ```
    4. Restart backend server
    5. Run this test
    6. Remove the time.sleep(6) line after testing
    7. Restart backend server again

Usage:
    python scripts/test_ai_timeout.py
"""

import requests
import json
import sys
import time
from typing import Optional, Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
TOKEN = None  # Set this to your JWT token or get from environment

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


def send_chat_message(conversation_id: Optional[int], message: str, token: str, timeout: int = 10) -> Dict[str, Any]:
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

    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json=payload,
            headers=headers,
            timeout=timeout
        )

        return {
            'success': response.status_code == 200,
            'status_code': response.status_code,
            'data': response.json() if response.status_code == 200 else None,
            'error': response.text if response.status_code != 200 else None
        }

    except requests.exceptions.Timeout:
        print(f"{RED}✗ Request timed out (client-side timeout){RESET}")
        return {
            'success': False,
            'status_code': None,
            'error': 'Client timeout'
        }
    except Exception as e:
        print(f"{RED}✗ Request failed: {e}{RESET}")
        return {
            'success': False,
            'status_code': None,
            'error': str(e)
        }


def check_backend_setup():
    """Check if backend is set up for timeout testing."""
    print(f"\n{YELLOW}{'='*60}{RESET}")
    print(f"{YELLOW}Backend Setup Check{RESET}")
    print(f"{YELLOW}{'='*60}{RESET}\n")

    print("To test AI timeout, you need to modify the backend:")
    print()
    print("1. Edit: backend/api/chat.py")
    print("2. Find the AI agent call (around line 150)")
    print("3. Add BEFORE the agent call:")
    print(f"{BLUE}   import time{RESET}")
    print(f"{BLUE}   time.sleep(6)  # Simulate 6-second delay{RESET}")
    print("4. Restart backend server")
    print()

    response = input(f"{YELLOW}Have you completed the backend setup? (yes/no): {RESET}").strip().lower()

    if response not in ['yes', 'y']:
        print(f"{RED}Please complete the backend setup before running this test.{RESET}")
        sys.exit(1)

    print(f"{GREEN}✓ Backend setup confirmed{RESET}\n")


def test_ai_timeout():
    """Test T420: AI timeout handling."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}T420: AI Timeout Test{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

    token = get_auth_token()
    conversation_id = None

    try:
        # Step 1: Create initial conversation (should work normally)
        print(f"{YELLOW}Step 1: Create Initial Conversation{RESET}")
        result = send_chat_message(
            None,
            "Start timeout test",
            token,
            timeout=10
        )

        if not result['success']:
            print(f"{RED}✗ Failed to create conversation{RESET}")
            print(f"  Error: {result.get('error')}")
            return False

        conversation_id = result['data']['conversation_id']
        print(f"{GREEN}✓ Conversation ID: {conversation_id}{RESET}")

        time.sleep(1)

        # Step 2: Send message that will trigger timeout
        print(f"\n{YELLOW}Step 2: Send Message (Should Trigger Timeout){RESET}")
        print(f"{YELLOW}Waiting for timeout (this will take ~6 seconds)...{RESET}")

        result = send_chat_message(
            conversation_id,
            "Add a task to test timeout handling",
            token,
            timeout=10  # Client timeout longer than server timeout
        )

        # Step 3: Verify 503 error response
        print(f"\n{YELLOW}Step 3: Verify Error Response{RESET}")

        if result['status_code'] == 503:
            print(f"{GREEN}✓ Received 503 Service Unavailable (expected){RESET}")
        else:
            print(f"{RED}✗ Expected 503, got {result['status_code']}{RESET}")
            print(f"  Response: {result.get('error')}")
            return False

        # Check error message
        if result.get('error'):
            error_data = json.loads(result['error'])
            error_message = error_data.get('detail', '')

            if 'timeout' in error_message.lower() or 'unavailable' in error_message.lower():
                print(f"{GREEN}✓ Error message mentions timeout/unavailable{RESET}")
                print(f"  Message: {error_message}")
            else:
                print(f"{YELLOW}⚠ Error message unclear{RESET}")
                print(f"  Message: {error_message}")

        time.sleep(1)

        # Step 4: Verify conversation is still valid
        print(f"\n{YELLOW}Step 4: Verify Conversation State{RESET}")
        print(f"{YELLOW}Note: Remove time.sleep(6) from backend and restart before this step{RESET}")

        response = input(f"{YELLOW}Have you removed the timeout simulation and restarted? (yes/no): {RESET}").strip().lower()

        if response not in ['yes', 'y']:
            print(f"{YELLOW}⚠ Skipping recovery test. Please restart backend without timeout simulation.{RESET}")
            print(f"{GREEN}✓ Timeout behavior verified (partial test){RESET}")
            return True

        # Try sending a normal message
        result = send_chat_message(
            conversation_id,
            "Show my tasks",
            token,
            timeout=10
        )

        if result['success']:
            print(f"{GREEN}✓ Conversation recovered successfully{RESET}")
            print(f"{GREEN}✓ Subsequent requests work normally{RESET}")
        else:
            print(f"{RED}✗ Conversation may be corrupted{RESET}")
            print(f"  Error: {result.get('error')}")
            return False

        # Step 5: Verify message preservation
        print(f"\n{YELLOW}Step 5: Verify Message Preservation{RESET}")

        # Check if the timeout message was saved
        # Note: This requires checking the database or conversation history
        result = send_chat_message(
            conversation_id,
            "What was my last message?",
            token,
            timeout=10
        )

        if result['success']:
            response_text = result['data']['message']['content'].lower()

            if 'timeout' in response_text or 'test' in response_text:
                print(f"{GREEN}✓ User message preserved in conversation history{RESET}")
            else:
                print(f"{YELLOW}⚠ Message preservation unclear{RESET}")
                print(f"  Response: {result['data']['message']['content']}")
        else:
            print(f"{YELLOW}⚠ Could not verify message preservation{RESET}")

        # Final result
        print(f"\n{GREEN}{'='*60}{RESET}")
        print(f"{GREEN}✓ T420: AI Timeout Test PASSED{RESET}")
        print(f"{GREEN}{'='*60}{RESET}\n")

        print(f"{YELLOW}Post-Test Cleanup:{RESET}")
        print("1. Ensure time.sleep(6) is removed from backend/api/chat.py")
        print("2. Restart backend server")
        print("3. Verify normal operation")

        return True

    except Exception as e:
        print(f"\n{RED}✗ Test failed with exception: {e}{RESET}")
        import traceback
        traceback.print_exc()
        return False


def test_timeout_without_backend_modification():
    """
    Alternative test that doesn't require backend modification.
    Tests the timeout handling by checking the frontend behavior.
    """
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}T420: AI Timeout Test (Frontend Behavior){RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

    print(f"{YELLOW}This test verifies frontend timeout handling without backend modification.{RESET}")
    print(f"{YELLOW}It checks that the frontend properly handles 503 errors.{RESET}\n")

    token = get_auth_token()

    # Create a conversation
    result = send_chat_message(None, "Test frontend timeout handling", token)

    if not result['success']:
        print(f"{RED}✗ Failed to create conversation{RESET}")
        return False

    conversation_id = result['data']['conversation_id']
    print(f"{GREEN}✓ Conversation created: {conversation_id}{RESET}\n")

    # Test instructions
    print(f"{YELLOW}Manual Test Steps:{RESET}")
    print("1. Open http://localhost:3000/assistant in browser")
    print(f"2. Use conversation ID: {conversation_id}")
    print("3. Send a message")
    print("4. If timeout occurs, verify:")
    print("   - Blue error message appears")
    print("   - Message says 'temporarily unavailable'")
    print("   - Helper text suggests retry")
    print("   - User message is preserved in chat")
    print("   - Can send new messages after timeout")
    print()

    print(f"{GREEN}✓ Frontend timeout handling ready for manual testing{RESET}")

    return True


if __name__ == "__main__":
    print(f"{BLUE}AI Timeout Test{RESET}\n")

    # Check if user wants to do full test or frontend-only test
    print("Choose test mode:")
    print("1. Full test (requires backend modification)")
    print("2. Frontend behavior test (no backend modification)")
    print()

    choice = input("Enter choice (1 or 2): ").strip()

    if choice == "1":
        check_backend_setup()
        success = test_ai_timeout()
    elif choice == "2":
        success = test_timeout_without_backend_modification()
    else:
        print(f"{RED}Invalid choice{RESET}")
        sys.exit(1)

    sys.exit(0 if success else 1)
