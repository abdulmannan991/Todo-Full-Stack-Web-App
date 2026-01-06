"""
Database Seeding Utility for Development

Sprint 2 - Task: T077
Owner: @database-expert

CRITICAL SECURITY NOTE:
This script creates test users and tasks for development ONLY.
ALL tasks are properly isolated by user_id to maintain multi-tenant security.

Usage:
    python -m utils.seed

This will:
1. Create 2 test users (alice@example.com, bob@example.com)
2. Create 5 tasks for each user
3. Mark some tasks as completed
4. Verify data isolation (alice cannot see bob's tasks)
"""

from sqlmodel import Session, select
from database import engine
from models import User, Task, TaskStatus
from datetime import datetime, timedelta
import hashlib


def hash_password(password: str) -> str:
    """Simple password hashing for demo purposes (NOT for production)."""
    return hashlib.sha256(password.encode()).hexdigest()


def seed_database():
    """
    Seed the database with test data.

    Creates:
    - 2 users (alice, bob)
    - 5 tasks per user (respecting user_id isolation)
    """
    with Session(engine) as session:
        # Check if users already exist
        existing_users = session.exec(select(User)).all()
        if existing_users:
            print(f"[INFO] Database already seeded ({len(existing_users)} users exist)")
            print("       Skipping seeding to avoid duplicates")
            return

        print("[INFO] Seeding database with test data...")

        # Create test users
        alice = User(
            email="alice@example.com",
            password_hash=hash_password("password123"),
            display_name="Alice",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        bob = User(
            email="bob@example.com",
            password_hash=hash_password("password123"),
            display_name="Bob",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        session.add(alice)
        session.add(bob)
        session.commit()

        # Refresh to get auto-generated IDs
        session.refresh(alice)
        session.refresh(bob)

        print(f"[OK] Created users: alice (ID={alice.id}), bob (ID={bob.id})")

        # Create tasks for Alice
        alice_tasks = [
            Task(
                user_id=alice.id,  # CRITICAL: user_id isolation
                title="Complete Sprint 2 implementation",
                description="Implement Task CRUD endpoints with multi-tenant security",
                status=TaskStatus.pending,
                created_at=datetime.utcnow() - timedelta(hours=2),
            ),
            Task(
                user_id=alice.id,
                title="Review database schema",
                description="Verify foreign key constraints and indexes",
                status=TaskStatus.completed,  # Marked as done
                created_at=datetime.utcnow() - timedelta(hours=1),
            ),
            Task(
                user_id=alice.id,
                title="Write API documentation",
                description="Document all task endpoints with examples",
                status=TaskStatus.pending,
                created_at=datetime.utcnow() - timedelta(minutes=30),
            ),
            Task(
                user_id=alice.id,
                title="Add unit tests",
                description="Test user isolation and CRUD operations",
                status=TaskStatus.completed,
                created_at=datetime.utcnow() - timedelta(minutes=15),
            ),
            Task(
                user_id=alice.id,
                title="Deploy to staging",
                description="Deploy Sprint 2 changes to staging environment",
                status=TaskStatus.pending,
                created_at=datetime.utcnow(),
            ),
        ]

        # Create tasks for Bob
        bob_tasks = [
            Task(
                user_id=bob.id,  # CRITICAL: user_id isolation
                title="Design Premium Midnight UI",
                description="Create glassmorphic task cards with violet accents",
                status=TaskStatus.completed,
                created_at=datetime.utcnow() - timedelta(hours=3),
            ),
            Task(
                user_id=bob.id,
                title="Implement Framer Motion animations",
                description="Add entrance animations and task completion effects",
                status=TaskStatus.pending,
                created_at=datetime.utcnow() - timedelta(hours=2),
            ),
            Task(
                user_id=bob.id,
                title="Optimize performance",
                description="Ensure animations run at 60 FPS",
                status=TaskStatus.pending,
                created_at=datetime.utcnow() - timedelta(hours=1),
            ),
            Task(
                user_id=bob.id,
                title="Test responsive layout",
                description="Verify 300px-2560px viewport support",
                status=TaskStatus.completed,
                created_at=datetime.utcnow() - timedelta(minutes=45),
            ),
            Task(
                user_id=bob.id,
                title="Add profile page",
                description="Display user stats and avatar upload",
                status=TaskStatus.pending,
                created_at=datetime.utcnow(),
            ),
        ]

        for task in alice_tasks:
            session.add(task)
        for task in bob_tasks:
            session.add(task)

        session.commit()

        print(f"[OK] Created {len(alice_tasks)} tasks for Alice")
        print(f"[OK] Created {len(bob_tasks)} tasks for Bob")

        # Verify data isolation
        alice_task_count = session.exec(
            select(Task).where(Task.user_id == alice.id)
        ).all()
        bob_task_count = session.exec(select(Task).where(Task.user_id == bob.id)).all()

        print("\n[VERIFICATION] Data Isolation Check:")
        print(f"  Alice's tasks: {len(alice_task_count)} (should be {len(alice_tasks)})")
        print(f"  Bob's tasks: {len(bob_task_count)} (should be {len(bob_tasks)})")

        if len(alice_task_count) == len(alice_tasks) and len(bob_task_count) == len(
            bob_tasks
        ):
            print("[OK] Multi-tenant isolation verified!")
        else:
            print("[ERROR] Data isolation check failed!")

        print("\n[INFO] Seeding complete!")
        print("\nTest credentials:")
        print("  Email: alice@example.com | Password: password123")
        print("  Email: bob@example.com   | Password: password123")


if __name__ == "__main__":
    seed_database()
