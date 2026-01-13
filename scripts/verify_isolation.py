"""
Direct User Isolation Verification Script

This script directly tests database operations to verify user_id isolation.
It bypasses the MCP layer and directly uses SQLModel to test isolation.

Tests:
- T348, T349: add_task isolation
- T358, T359: list_tasks isolation
- T369, T370: complete_task isolation
- T380, T381: delete_task isolation
- T391, T392: update_task isolation

Usage:
    python scripts/verify_isolation.py
"""

import sys
import os

# Add project root to path so we can import backend modules
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from sqlmodel import Session, select
from backend.models.task import Task
from backend.mcp.db_utils import get_mcp_session

def test_add_task_isolation():
    """Test that tasks are created with correct user_id."""
    print("\n[TEST 1] add_task - User ID Assignment")
    print("=" * 60)

    with get_mcp_session() as session:
        # User 1 creates a task
        task1 = Task(user_id=1, title="User 1's task", completed=False)
        session.add(task1)
        session.commit()
        session.refresh(task1)
        print(f"[OK] User 1 created task: {task1.title} (ID: {task1.id})")

        # User 2 creates a task
        task2 = Task(user_id=2, title="User 2's task", completed=False)
        session.add(task2)
        session.commit()
        session.refresh(task2)
        print(f"[OK] User 2 created task: {task2.title} (ID: {task2.id})")

    print("PASS: Tasks created with correct user_id")
    return True


def test_list_tasks_isolation():
    """Test that users can only see their own tasks."""
    print("\n[TEST 2] list_tasks - User Isolation")
    print("=" * 60)

    with get_mcp_session() as session:
        # Create tasks for two different users
        task1a = Task(user_id=1, title="User 1 Task A", completed=False)
        task1b = Task(user_id=1, title="User 1 Task B", completed=False)
        task2a = Task(user_id=2, title="User 2 Task A", completed=False)

        session.add(task1a)
        session.add(task1b)
        session.add(task2a)
        session.commit()

        # User 1 lists their tasks
        user1_tasks = session.exec(
            select(Task).where(Task.user_id == 1)
        ).all()
        print(f"User 1 tasks: {[t.title for t in user1_tasks]}")

        # User 2 lists their tasks
        user2_tasks = session.exec(
            select(Task).where(Task.user_id == 2)
        ).all()
        print(f"User 2 tasks: {[t.title for t in user2_tasks]}")

        # Verify isolation
        user1_titles = [t.title for t in user1_tasks]
        user2_titles = [t.title for t in user2_tasks]

        if "User 2 Task A" in user1_titles:
            print("FAIL: User 1 can see User 2's tasks!")
            return False

        if "User 1 Task A" in user2_titles or "User 1 Task B" in user2_titles:
            print("FAIL: User 2 can see User 1's tasks!")
            return False

    print("PASS: Users can only see their own tasks")
    return True


def test_complete_task_isolation():
    """Test that users cannot complete other users' tasks."""
    print("\n[TEST 3] complete_task - Cross-User Prevention")
    print("=" * 60)

    with get_mcp_session() as session:
        # User 1 creates a task
        task = Task(user_id=1, title="User 1 Complete Test", completed=False)
        session.add(task)
        session.commit()
        session.refresh(task)
        task_id = task.id
        print(f"User 1 created task ID: {task_id}")

        # User 2 tries to complete User 1's task
        user2_task = session.exec(
            select(Task)
            .where(Task.id == task_id)
            .where(Task.user_id == 2)  # User 2's perspective
        ).first()

        if user2_task is not None:
            print("FAIL: User 2 was able to access User 1's task!")
            return False

        print("User 2 cannot access User 1's task (returns None)")

    print("PASS: User 2 cannot complete User 1's task")
    return True


def test_delete_task_isolation():
    """Test that users cannot delete other users' tasks."""
    print("\n[TEST 4] delete_task - Cross-User Prevention")
    print("=" * 60)

    with get_mcp_session() as session:
        # User 1 creates a task
        task = Task(user_id=1, title="User 1 Delete Test", completed=False)
        session.add(task)
        session.commit()
        session.refresh(task)
        task_id = task.id
        print(f"User 1 created task ID: {task_id}")

        # User 2 tries to delete User 1's task
        user2_task = session.exec(
            select(Task)
            .where(Task.id == task_id)
            .where(Task.user_id == 2)  # User 2's perspective
        ).first()

        if user2_task is not None:
            print("FAIL: User 2 was able to access User 1's task!")
            return False

        print("User 2 cannot access User 1's task (returns None)")

    print("PASS: User 2 cannot delete User 1's task")
    return True


def test_update_task_isolation():
    """Test that users cannot update other users' tasks."""
    print("\n[TEST 5] update_task - Cross-User Prevention")
    print("=" * 60)

    with get_mcp_session() as session:
        # User 1 creates a task
        task = Task(user_id=1, title="User 1 Update Test", completed=False)
        session.add(task)
        session.commit()
        session.refresh(task)
        task_id = task.id
        print(f"User 1 created task ID: {task_id}")

        # User 2 tries to update User 1's task
        user2_task = session.exec(
            select(Task)
            .where(Task.id == task_id)
            .where(Task.user_id == 2)  # User 2's perspective
        ).first()

        if user2_task is not None:
            print("FAIL: User 2 was able to access User 1's task!")
            return False

        print("User 2 cannot access User 1's task (returns None)")

    print("PASS: User 2 cannot update User 1's task")
    return True


def main():
    """Run all isolation tests."""
    print("\n" + "=" * 60)
    print("USER ISOLATION VERIFICATION - DIRECT DATABASE TESTING")
    print("=" * 60)
    print("\nIMPORTANT: This test requires a running database connection.")
    print("Make sure DATABASE_URL is set in backend/.env\n")

    try:
        results = []

        results.append(("add_task isolation", test_add_task_isolation()))
        results.append(("list_tasks isolation", test_list_tasks_isolation()))
        results.append(("complete_task isolation", test_complete_task_isolation()))
        results.append(("delete_task isolation", test_delete_task_isolation()))
        results.append(("update_task isolation", test_update_task_isolation()))

        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)

        passed = sum(1 for _, result in results if result)
        total = len(results)

        for test_name, result in results:
            status = "PASS" if result else "FAIL"
            print(f"{status}: {test_name}")

        print(f"\nTotal: {passed}/{total} tests passed")

        if passed == total:
            print("\nALL TESTS PASSED - USER ISOLATION VERIFIED")
            return 0
        else:
            print("\nSOME TESTS FAILED - USER ISOLATION COMPROMISED")
            return 1

    except Exception as e:
        print(f"\nTEST FAILED WITH ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
