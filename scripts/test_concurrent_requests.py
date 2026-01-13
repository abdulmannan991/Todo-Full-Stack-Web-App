"""
End-to-End Test: Concurrent Requests (T419)

Tests that multiple simultaneous messages are handled correctly with optimistic locking:
1. Send multiple concurrent requests to the same conversation
2. Verify optimistic locking prevents race conditions
3. Confirm all requests eventually succeed (with automatic retries)
4. Verify no data loss or corruption

Requirements:
- Backend server running on http://localhost:8000
- Valid JWT token (set TOKEN variable below)
- Database connected

Usage:
    python scripts/test_concurrent_requests.py
"""

import requests
import json
import sys
import time
import asyncio
import aiohttp
from typing import Optional, Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
BASE_URL = "http://localhost:8000"
TOKEN = None  # Set this to your JWT token or get from environment
NUM_CONCURRENT_REQUESTS = 5

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


def send_chat_message_sync(conversation_id: Optional[int], message: str, token: str, request_id: int) -> Dict[str, Any]:
    """Send a chat message synchronously (for threading)."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "conversation_id": conversation_id,
        "message": message
    }

    start_time = time.time()
    print(f"{BLUE}[Request {request_id}] → Sending: {message}{RESET}")

    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json=payload,
            headers=headers,
            timeout=10
        )

        elapsed = time.time() - start_time

        if response.status_code == 200:
            data = response.json()
            print(f"{GREEN}[Request {request_id}] ✓ Success ({elapsed:.2f}s){RESET}")
            return {
                'success': True,
                'request_id': request_id,
                'status_code': 200,
                'data': data,
                'elapsed': elapsed
            }
        else:
            print(f"{RED}[Request {request_id}] ✗ Failed: {response.status_code} ({elapsed:.2f}s){RESET}")
            return {
                'success': False,
                'request_id': request_id,
                'status_code': response.status_code,
                'error': response.text,
                'elapsed': elapsed
            }

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"{RED}[Request {request_id}] ✗ Exception: {e} ({elapsed:.2f}s){RESET}")
        return {
            'success': False,
            'request_id': request_id,
            'error': str(e),
            'elapsed': elapsed
        }


async def send_chat_message_async(session: aiohttp.ClientSession, conversation_id: Optional[int],
                                   message: str, token: str, request_id: int) -> Dict[str, Any]:
    """Send a chat message asynchronously."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "conversation_id": conversation_id,
        "message": message
    }

    start_time = time.time()
    print(f"{BLUE}[Request {request_id}] → Sending: {message}{RESET}")

    try:
        async with session.post(
            f"{BASE_URL}/api/chat",
            json=payload,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=10)
        ) as response:
            elapsed = time.time() - start_time

            if response.status == 200:
                data = await response.json()
                print(f"{GREEN}[Request {request_id}] ✓ Success ({elapsed:.2f}s){RESET}")
                return {
                    'success': True,
                    'request_id': request_id,
                    'status_code': 200,
                    'data': data,
                    'elapsed': elapsed
                }
            else:
                error_text = await response.text()
                print(f"{RED}[Request {request_id}] ✗ Failed: {response.status} ({elapsed:.2f}s){RESET}")
                return {
                    'success': False,
                    'request_id': request_id,
                    'status_code': response.status,
                    'error': error_text,
                    'elapsed': elapsed
                }

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"{RED}[Request {request_id}] ✗ Exception: {e} ({elapsed:.2f}s){RESET}")
        return {
            'success': False,
            'request_id': request_id,
            'error': str(e),
            'elapsed': elapsed
        }


def test_concurrent_requests_threading():
    """Test concurrent requests using threading (synchronous requests)."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}T419: Concurrent Requests Test (Threading){RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

    token = get_auth_token()

    # Step 1: Create initial conversation
    print(f"{YELLOW}Step 1: Create Initial Conversation{RESET}")
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={"conversation_id": None, "message": "Start concurrent test"},
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    )

    if response.status_code != 200:
        print(f"{RED}✗ Failed to create conversation{RESET}")
        return False

    conversation_id = response.json()['conversation_id']
    print(f"{GREEN}✓ Conversation ID: {conversation_id}{RESET}\n")

    time.sleep(1)

    # Step 2: Send concurrent requests
    print(f"{YELLOW}Step 2: Send {NUM_CONCURRENT_REQUESTS} Concurrent Requests{RESET}")

    messages = [
        f"Add task concurrent-{i}" for i in range(1, NUM_CONCURRENT_REQUESTS + 1)
    ]

    results = []
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=NUM_CONCURRENT_REQUESTS) as executor:
        futures = [
            executor.submit(send_chat_message_sync, conversation_id, msg, token, i)
            for i, msg in enumerate(messages, 1)
        ]

        for future in as_completed(futures):
            results.append(future.result())

    total_elapsed = time.time() - start_time

    # Step 3: Analyze results
    print(f"\n{YELLOW}Step 3: Analyze Results{RESET}")

    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]

    print(f"Total requests: {len(results)}")
    print(f"Successful: {GREEN}{len(successful)}{RESET}")
    print(f"Failed: {RED}{len(failed)}{RESET}")
    print(f"Total time: {total_elapsed:.2f}s")
    print(f"Average time per request: {sum(r['elapsed'] for r in results) / len(results):.2f}s")

    # Check for 409 conflicts (should be handled by retry logic)
    conflicts = [r for r in results if r.get('status_code') == 409]
    if conflicts:
        print(f"{YELLOW}⚠ {len(conflicts)} requests returned 409 (should have been retried){RESET}")

    # All requests should eventually succeed
    if len(successful) == NUM_CONCURRENT_REQUESTS:
        print(f"{GREEN}✓ All concurrent requests succeeded{RESET}")
    else:
        print(f"{RED}✗ Some requests failed{RESET}")
        for r in failed:
            print(f"  Request {r['request_id']}: {r.get('error', 'Unknown error')}")
        return False

    # Step 4: Verify data integrity
    print(f"\n{YELLOW}Step 4: Verify Data Integrity{RESET}")

    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={"conversation_id": conversation_id, "message": "Show my tasks"},
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    )

    if response.status_code != 200:
        print(f"{RED}✗ Failed to verify tasks{RESET}")
        return False

    response_text = response.json()['message']['content']

    # Count how many concurrent tasks appear in the list
    concurrent_tasks_found = sum(1 for i in range(1, NUM_CONCURRENT_REQUESTS + 1)
                                  if f"concurrent-{i}" in response_text.lower())

    print(f"Tasks found in list: {concurrent_tasks_found}/{NUM_CONCURRENT_REQUESTS}")

    if concurrent_tasks_found == NUM_CONCURRENT_REQUESTS:
        print(f"{GREEN}✓ All tasks created successfully (no data loss){RESET}")
    else:
        print(f"{RED}✗ Some tasks missing (data loss detected){RESET}")
        return False

    print(f"\n{GREEN}{'='*60}{RESET}")
    print(f"{GREEN}✓ T419: Concurrent Requests Test PASSED (Threading){RESET}")
    print(f"{GREEN}{'='*60}{RESET}\n")

    return True


async def test_concurrent_requests_async():
    """Test concurrent requests using asyncio (truly asynchronous)."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}T419: Concurrent Requests Test (Async){RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

    token = get_auth_token()

    # Step 1: Create initial conversation
    print(f"{YELLOW}Step 1: Create Initial Conversation{RESET}")

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BASE_URL}/api/chat",
            json={"conversation_id": None, "message": "Start async concurrent test"},
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        ) as response:
            if response.status != 200:
                print(f"{RED}✗ Failed to create conversation{RESET}")
                return False

            data = await response.json()
            conversation_id = data['conversation_id']
            print(f"{GREEN}✓ Conversation ID: {conversation_id}{RESET}\n")

        await asyncio.sleep(1)

        # Step 2: Send concurrent requests
        print(f"{YELLOW}Step 2: Send {NUM_CONCURRENT_REQUESTS} Concurrent Requests (Async){RESET}")

        messages = [
            f"Add task async-concurrent-{i}" for i in range(1, NUM_CONCURRENT_REQUESTS + 1)
        ]

        start_time = time.time()

        tasks = [
            send_chat_message_async(session, conversation_id, msg, token, i)
            for i, msg in enumerate(messages, 1)
        ]

        results = await asyncio.gather(*tasks)

        total_elapsed = time.time() - start_time

        # Step 3: Analyze results
        print(f"\n{YELLOW}Step 3: Analyze Results{RESET}")

        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]

        print(f"Total requests: {len(results)}")
        print(f"Successful: {GREEN}{len(successful)}{RESET}")
        print(f"Failed: {RED}{len(failed)}{RESET}")
        print(f"Total time: {total_elapsed:.2f}s")
        print(f"Average time per request: {sum(r['elapsed'] for r in results) / len(results):.2f}s")

        # All requests should eventually succeed
        if len(successful) == NUM_CONCURRENT_REQUESTS:
            print(f"{GREEN}✓ All concurrent requests succeeded{RESET}")
        else:
            print(f"{RED}✗ Some requests failed{RESET}")
            for r in failed:
                print(f"  Request {r['request_id']}: {r.get('error', 'Unknown error')}")
            return False

        # Step 4: Verify data integrity
        print(f"\n{YELLOW}Step 4: Verify Data Integrity{RESET}")

        async with session.post(
            f"{BASE_URL}/api/chat",
            json={"conversation_id": conversation_id, "message": "Show my tasks"},
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        ) as response:
            if response.status != 200:
                print(f"{RED}✗ Failed to verify tasks{RESET}")
                return False

            data = await response.json()
            response_text = data['message']['content']

        # Count how many concurrent tasks appear in the list
        concurrent_tasks_found = sum(1 for i in range(1, NUM_CONCURRENT_REQUESTS + 1)
                                      if f"async-concurrent-{i}" in response_text.lower())

        print(f"Tasks found in list: {concurrent_tasks_found}/{NUM_CONCURRENT_REQUESTS}")

        if concurrent_tasks_found == NUM_CONCURRENT_REQUESTS:
            print(f"{GREEN}✓ All tasks created successfully (no data loss){RESET}")
        else:
            print(f"{RED}✗ Some tasks missing (data loss detected){RESET}")
            return False

    print(f"\n{GREEN}{'='*60}{RESET}")
    print(f"{GREEN}✓ T419: Concurrent Requests Test PASSED (Async){RESET}")
    print(f"{GREEN}{'='*60}{RESET}\n")

    return True


if __name__ == "__main__":
    print(f"{BLUE}Running concurrent request tests...{RESET}\n")

    # Test 1: Threading approach
    success_threading = test_concurrent_requests_threading()

    time.sleep(2)

    # Test 2: Async approach
    success_async = asyncio.run(test_concurrent_requests_async())

    # Final result
    if success_threading and success_async:
        print(f"\n{GREEN}{'='*60}{RESET}")
        print(f"{GREEN}✓ ALL CONCURRENT REQUEST TESTS PASSED{RESET}")
        print(f"{GREEN}{'='*60}{RESET}\n")
        sys.exit(0)
    else:
        print(f"\n{RED}{'='*60}{RESET}")
        print(f"{RED}✗ SOME CONCURRENT REQUEST TESTS FAILED{RESET}")
        print(f"{RED}{'='*60}{RESET}\n")
        sys.exit(1)
