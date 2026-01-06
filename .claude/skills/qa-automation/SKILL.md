---
name: qa-automation
description: Automates comprehensive testing across frontend, backend, and integration layers
version: 1.0.0
owner: logic-coordinator
tags: [testing, qa, automation, pytest, jest, playwright, ci/cd]
---

# QA Automation Skill

## Purpose
Provide comprehensive automated testing coverage across the full stack (Next.js frontend, FastAPI backend, database layer) with integration testing and end-to-end validation.

## Scope
- **Owned By**: @logic-coordinator
- **Technology Stack**: pytest (backend), Jest/React Testing Library (frontend), Playwright (E2E)
- **Coverage Target**: >80% code coverage across all layers

## Testing Layers

### 1. Backend Unit Tests (pytest)

#### Model Tests
```python
# tests/test_models.py
import pytest
from backend.models import Todo, User
from datetime import datetime

def test_todo_creation():
    """Test Todo model creation."""
    todo = Todo(
        title="Test Todo",
        user_id=1,
        completed=False,
        created_at=datetime.utcnow()
    )
    assert todo.title == "Test Todo"
    assert todo.completed is False
    assert todo.user_id == 1

def test_todo_validation():
    """Test Todo model validation."""
    with pytest.raises(ValueError):
        Todo(title="", user_id=1)  # Empty title should fail
```

#### API Endpoint Tests
```python
# tests/test_todos_api.py
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

@pytest.fixture
def auth_headers(test_user):
    """Fixture to get authenticated headers."""
    token = create_access_token(test_user.id)
    return {"Authorization": f"Bearer {token}"}

def test_get_todos_requires_auth():
    """Test that /todos requires authentication."""
    response = client.get("/api/todos")
    assert response.status_code == 401

def test_get_todos_authenticated(auth_headers):
    """Test getting todos with valid auth."""
    response = client.get("/api/todos", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_todo(auth_headers):
    """Test creating a new todo."""
    todo_data = {
        "title": "Test Todo",
        "completed": False
    }
    response = client.post(
        "/api/todos",
        json=todo_data,
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Todo"
    assert data["completed"] is False

def test_user_isolation(auth_headers, other_user_todo):
    """Test that users can only access their own todos."""
    # Try to get another user's todo
    response = client.get(
        f"/api/todos/{other_user_todo.id}",
        headers=auth_headers
    )
    assert response.status_code == 404  # Should not find
```

#### Database Tests
```python
# tests/test_database.py
import pytest
from sqlmodel import Session, select
from backend.database import engine
from backend.models import Todo, User

@pytest.fixture
def db_session():
    """Create a test database session."""
    with Session(engine) as session:
        yield session
        session.rollback()

def test_user_todo_relationship(db_session):
    """Test user-todo relationship."""
    user = User(email="test@example.com", password_hash="hash")
    db_session.add(user)
    db_session.commit()

    todo = Todo(title="Test", user_id=user.id)
    db_session.add(todo)
    db_session.commit()

    # Query todos by user
    todos = db_session.exec(
        select(Todo).where(Todo.user_id == user.id)
    ).all()
    assert len(todos) == 1
    assert todos[0].title == "Test"
```

### 2. Frontend Unit Tests (Jest + React Testing Library)

#### Component Tests
```typescript
// __tests__/components/TodoItem.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import TodoItem from '@/components/TodoItem'

describe('TodoItem', () => {
  const mockTodo = {
    id: 1,
    title: 'Test Todo',
    completed: false,
    user_id: 1,
    created_at: new Date().toISOString()
  }

  it('renders todo item', () => {
    render(<TodoItem todo={mockTodo} />)
    expect(screen.getByText('Test Todo')).toBeInTheDocument()
  })

  it('toggles completion status', async () => {
    const onToggle = jest.fn()
    render(<TodoItem todo={mockTodo} onToggle={onToggle} />)

    const checkbox = screen.getByRole('checkbox')
    fireEvent.click(checkbox)

    expect(onToggle).toHaveBeenCalledWith(1)
  })

  it('handles delete action', () => {
    const onDelete = jest.fn()
    render(<TodoItem todo={mockTodo} onDelete={onDelete} />)

    const deleteButton = screen.getByRole('button', { name: /delete/i })
    fireEvent.click(deleteButton)

    expect(onDelete).toHaveBeenCalledWith(1)
  })
})
```

#### Hook Tests
```typescript
// __tests__/hooks/useTodos.test.ts
import { renderHook, waitFor } from '@testing-library/react'
import { useTodos } from '@/hooks/useTodos'

describe('useTodos', () => {
  it('fetches todos on mount', async () => {
    const { result } = renderHook(() => useTodos())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.todos).toBeDefined()
  })

  it('handles authentication errors', async () => {
    // Mock 401 response
    global.fetch = jest.fn(() =>
      Promise.resolve({
        status: 401,
        json: () => Promise.resolve({ detail: 'Unauthorized' })
      })
    )

    const { result } = renderHook(() => useTodos())

    await waitFor(() => {
      expect(result.current.error).toBe('Unauthorized')
    })
  })
})
```

### 3. Integration Tests (Playwright E2E)

#### Authentication Flow
```typescript
// e2e/auth.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Authentication', () => {
  test('login flow', async ({ page }) => {
    await page.goto('http://localhost:3000/login')

    await page.fill('input[name="email"]', 'test@example.com')
    await page.fill('input[name="password"]', 'password123')
    await page.click('button[type="submit"]')

    await expect(page).toHaveURL('http://localhost:3000/dashboard')
    await expect(page.locator('h1')).toContainText('My Todos')
  })

  test('requires authentication for protected pages', async ({ page }) => {
    await page.goto('http://localhost:3000/dashboard')

    // Should redirect to login
    await expect(page).toHaveURL(/\/login/)
  })
})
```

#### Todo CRUD Flow
```typescript
// e2e/todos.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Todo Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('http://localhost:3000/login')
    await page.fill('input[name="email"]', 'test@example.com')
    await page.fill('input[name="password"]', 'password123')
    await page.click('button[type="submit"]')
    await page.waitForURL('**/dashboard')
  })

  test('create new todo', async ({ page }) => {
    await page.fill('input[placeholder="Add a new todo"]', 'Buy groceries')
    await page.click('button:has-text("Add")')

    await expect(page.locator('text=Buy groceries')).toBeVisible()
  })

  test('toggle todo completion', async ({ page }) => {
    const todoItem = page.locator('[data-testid="todo-item"]').first()
    const checkbox = todoItem.locator('input[type="checkbox"]')

    await checkbox.click()

    await expect(todoItem).toHaveClass(/completed/)
  })

  test('delete todo', async ({ page }) => {
    const todoText = 'Todo to delete'
    await page.fill('input[placeholder="Add a new todo"]', todoText)
    await page.click('button:has-text("Add")')

    const todoItem = page.locator(`text=${todoText}`).first()
    await todoItem.hover()
    await page.click('[data-testid="delete-button"]')

    await expect(page.locator(`text=${todoText}`)).not.toBeVisible()
  })
})
```

#### Responsive Testing
```typescript
// e2e/responsive.spec.ts
import { test, expect, devices } from '@playwright/test'

const viewports = [
  { name: 'Mobile', ...devices['iPhone 12'] },
  { name: 'Tablet', ...devices['iPad'] },
  { name: 'Desktop', viewport: { width: 1920, height: 1080 } }
]

viewports.forEach(({ name, ...config }) => {
  test.describe(`Responsive - ${name}`, () => {
    test.use(config)

    test('todo list is functional', async ({ page }) => {
      await page.goto('http://localhost:3000/dashboard')

      // Test that UI is visible and functional
      await expect(page.locator('input[placeholder*="todo"]')).toBeVisible()
      await expect(page.locator('button:has-text("Add")')).toBeVisible()
    })
  })
})
```

## Test Configuration

### pytest.ini
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --cov=backend
    --cov-report=html
    --cov-report=term
    --cov-fail-under=80
```

### jest.config.js
```javascript
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
}
```

### playwright.config.ts
```typescript
import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
})
```

## Execution Commands

### Run All Tests
```bash
# Backend tests
cd backend && pytest

# Frontend tests
cd frontend && npm test

# E2E tests
cd frontend && npm run test:e2e

# Full suite
npm run test:all
```

### Coverage Reports
```bash
# Backend coverage
cd backend && pytest --cov-report=html
open backend/htmlcov/index.html

# Frontend coverage
cd frontend && npm test -- --coverage
open frontend/coverage/index.html
```

## Validation Checks

When invoked, this skill will:
1. Run full test suite across all layers
2. Generate coverage reports
3. Identify untested code paths
4. Flag security vulnerabilities in dependencies
5. Validate test quality (assertions, fixtures)
6. Check for test isolation issues
7. Generate consolidated test report

## Usage

```bash
# Run all tests
/qa-automation

# Run specific layer
/qa-automation --layer backend
/qa-automation --layer frontend
/qa-automation --layer e2e

# Generate coverage report
/qa-automation --coverage

# Security audit
/qa-automation --security
```

## Success Criteria
- ✅ >80% code coverage on backend
- ✅ >80% code coverage on frontend
- ✅ All E2E critical paths tested
- ✅ Zero failing tests in CI/CD
- ✅ Test execution time <5 minutes
- ✅ All security vulnerabilities addressed

## Integration
This skill integrates with:
- **@logic-coordinator**: Primary owner and executor
- **@ui-auth-expert**: Frontend test validation
- **@fastapi-jwt-guardian**: API security testing
- **@database-expert**: Database test fixtures
- **@performance-optimizer**: Performance regression testing

## CI/CD Integration
```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run backend tests
        run: cd backend && pytest --cov

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run frontend tests
        run: cd frontend && npm test -- --coverage

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run E2E tests
        run: cd frontend && npm run test:e2e
```
