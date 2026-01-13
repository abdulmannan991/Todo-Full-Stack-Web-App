"""
T415 - Emoji & Unicode Support Verification

Tests that task titles can contain emojis and special Unicode characters.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables BEFORE importing backend modules
from dotenv import load_dotenv
load_dotenv(project_root / "backend" / ".env")

from backend.models.task import Task
from backend.database import get_session
from datetime import datetime

def test_emoji_support():
    """Test that emojis are stored and retrieved correctly."""

    print("=" * 60)
    print("T415 - EMOJI & UNICODE SUPPORT VERIFICATION")
    print("=" * 60)
    print()

    test_cases = [
        ("Buy 🍕 and 🥤", "Food shopping with emojis"),
        ("Meeting at 3️⃣ PM", "Time with emoji numbers"),
        ("✅ Complete project", "Checkmark emoji"),
        ("日本語タスク", "Japanese characters"),
        ("Café ☕ meeting", "Accented characters with emoji"),
    ]

    passed = 0
    failed = 0

    with next(get_session()) as session:
        for title, description in test_cases:
            try:
                # Create task with special characters
                task = Task(
                    user_id=1,
                    title=title,
                    description=description,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(task)
                session.commit()
                session.refresh(task)

                # Verify retrieval
                retrieved = session.get(Task, task.id)

                if retrieved and retrieved.title == title and retrieved.description == description:
                    print(f"✅ PASS: '{title}'")
                    print(f"   Stored: {len(title.encode('utf-8'))} bytes")
                    passed += 1
                else:
                    print(f"❌ FAIL: '{title}'")
                    print(f"   Expected: {title}")
                    print(f"   Got: {retrieved.title if retrieved else 'None'}")
                    failed += 1

            except Exception as e:
                print(f"❌ FAIL: '{title}'")
                print(f"   Error: {e}")
                failed += 1

    print()
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Passed: {passed}/{len(test_cases)}")
    print(f"Failed: {failed}/{len(test_cases)}")
    print()

    if failed == 0:
        print("✅ ALL TESTS PASSED - EMOJI & UNICODE SUPPORT VERIFIED")
        return 0
    else:
        print("❌ SOME TESTS FAILED - EMOJI SUPPORT NOT FULLY WORKING")
        return 1

if __name__ == "__main__":
    sys.exit(test_emoji_support())
