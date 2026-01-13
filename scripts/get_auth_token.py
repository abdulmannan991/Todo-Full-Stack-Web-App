"""
Helper script to get a fresh JWT token for testing.

Usage:
    python scripts/get_auth_token.py <email> <password>

Example:
    python scripts/get_auth_token.py test@example.com password123
"""

import requests
import sys
import json

# Fix Windows console encoding
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE_URL = "http://localhost:8000"

def get_token(email: str, password: str) -> str:
    """Login and get JWT token."""

    # Try to login
    response = requests.post(
        f"{BASE_URL}/api/auth/sign-in/email",
        json={"email": email, "password": password}
    )

    if response.status_code == 200:
        data = response.json()
        token = data.get('token')
        print(f"✓ Login successful!")
        print(f"✓ User: {data['user']['email']}")
        print(f"✓ Token: {token}")
        return token
    elif response.status_code == 401:
        print(f"✗ Login failed: Invalid credentials")
        print(f"  Try signing up first or check your password")
        return None
    else:
        print(f"✗ Login failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return None


def signup(email: str, password: str, name: str = None) -> str:
    """Sign up and get JWT token."""

    payload = {"email": email, "password": password}
    if name:
        payload["name"] = name

    response = requests.post(
        f"{BASE_URL}/api/auth/sign-up/email",
        json=payload
    )

    if response.status_code == 200:
        data = response.json()
        token = data.get('token')
        print(f"✓ Signup successful!")
        print(f"✓ User: {data['user']['email']}")
        print(f"✓ Token: {token}")
        return token
    elif response.status_code == 400:
        print(f"✗ Signup failed: Email already registered")
        print(f"  Try logging in instead")
        return None
    else:
        print(f"✗ Signup failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return None


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/get_auth_token.py <email> <password> [--signup]")
        print("Example: python scripts/get_auth_token.py test@example.com password123")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]
    is_signup = "--signup" in sys.argv

    print(f"\n{'Signing up' if is_signup else 'Logging in'} as: {email}")
    print(f"Backend: {BASE_URL}\n")

    if is_signup:
        token = signup(email, password)
    else:
        token = get_token(email, password)

    if token:
        print(f"\n{'='*60}")
        print("To use this token in tests, run:")
        print(f"export AUTH_TOKEN='{token}'")
        print(f"{'='*60}\n")
        sys.exit(0)
    else:
        sys.exit(1)
