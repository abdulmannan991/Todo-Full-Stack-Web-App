---
name: performance-optimizer
description: Optimizes performance across Next.js frontend and FastAPI backend with monitoring and budgets
version: 1.0.0
owner: logic-coordinator
tags: [performance, optimization, monitoring, next.js, fastapi, lighthouse]
---

# Performance Optimizer Skill

## Purpose
Monitor and optimize performance across the full stack with defined budgets, automated profiling, and continuous monitoring.

## Scope
- **Owned By**: @logic-coordinator
- **Technology Stack**: Next.js, FastAPI, Neon Postgres
- **Performance Targets**: Core Web Vitals, API response times, database query optimization

## Performance Budgets

### Frontend (Next.js)

#### Core Web Vitals
- **LCP (Largest Contentful Paint)**: <2.5s
- **FID (First Input Delay)**: <100ms
- **CLS (Cumulative Layout Shift)**: <0.1
- **FCP (First Contentful Paint)**: <1.8s
- **TTI (Time to Interactive)**: <3.8s

#### Bundle Sizes
- **Initial Bundle**: <200KB (gzipped)
- **Total JavaScript**: <500KB (gzipped)
- **CSS**: <50KB (gzipped)
- **Images**: Properly optimized (Next.js Image component)

#### Lighthouse Scores
- **Performance**: >90
- **Accessibility**: >95
- **Best Practices**: >95
- **SEO**: >90

### Backend (FastAPI)

#### API Response Times
- **p50**: <100ms
- **p95**: <300ms
- **p99**: <500ms
- **Timeout**: 30s (hard limit)

#### Database Queries
- **Simple queries**: <50ms
- **Complex queries**: <200ms
- **N+1 queries**: Zero tolerance
- **Connection pool**: Max 20 connections

#### Resource Limits
- **Memory**: <512MB per worker
- **CPU**: <70% average utilization
- **Database connections**: <50% pool utilization

## Optimization Strategies

### 1. Frontend Optimization

#### Code Splitting
```typescript
// app/dashboard/page.tsx
import dynamic from 'next/dynamic'

// Lazy load heavy components
const TodoList = dynamic(() => import('@/components/TodoList'), {
  loading: () => <TodoListSkeleton />,
  ssr: false // Client-side only if needed
})

// Route-based code splitting (automatic with App Router)
export default function DashboardPage() {
  return <TodoList />
}
```

#### Image Optimization
```typescript
// Use Next.js Image component
import Image from 'next/image'

<Image
  src="/avatar.jpg"
  width={48}
  height={48}
  alt="User avatar"
  loading="lazy"
  placeholder="blur"
/>
```

#### Data Fetching Optimization
```typescript
// app/dashboard/page.tsx
import { Suspense } from 'react'

// Server component with streaming
async function TodoList() {
  const todos = await fetch('http://localhost:8000/api/todos', {
    next: { revalidate: 60 } // ISR with 60s cache
  })
  return <div>{/* render todos */}</div>
}

export default function DashboardPage() {
  return (
    <Suspense fallback={<TodoListSkeleton />}>
      <TodoList />
    </Suspense>
  )
}
```

#### React Performance Patterns
```typescript
// Use React.memo for expensive components
import { memo } from 'react'

const TodoItem = memo(({ todo, onToggle, onDelete }) => {
  return <div>{/* todo UI */}</div>
}, (prevProps, nextProps) => {
  // Custom comparison
  return prevProps.todo.id === nextProps.todo.id &&
         prevProps.todo.completed === nextProps.todo.completed
})

// Use useMemo for expensive computations
import { useMemo } from 'react'

function TodoList({ todos }) {
  const sortedTodos = useMemo(() => {
    return [...todos].sort((a, b) =>
      new Date(b.created_at) - new Date(a.created_at)
    )
  }, [todos])

  return <div>{/* render sorted todos */}</div>
}

// Use useCallback for stable function references
import { useCallback } from 'react'

function TodoList({ todos }) {
  const handleToggle = useCallback((id) => {
    // toggle logic
  }, [])

  return todos.map(todo => (
    <TodoItem key={todo.id} todo={todo} onToggle={handleToggle} />
  ))
}
```

### 2. Backend Optimization

#### Database Query Optimization
```python
from sqlmodel import select, Session
from backend.models import Todo, User

# ✅ GOOD: Select only needed columns
def get_todos_efficient(user_id: int, session: Session):
    statement = select(
        Todo.id,
        Todo.title,
        Todo.completed
    ).where(Todo.user_id == user_id)
    return session.exec(statement).all()

# ✅ GOOD: Use pagination
def get_todos_paginated(
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    session: Session = None
):
    statement = (
        select(Todo)
        .where(Todo.user_id == user_id)
        .offset(skip)
        .limit(limit)
    )
    return session.exec(statement).all()

# ✅ GOOD: Eager loading to avoid N+1
def get_todos_with_user(session: Session):
    from sqlmodel import select
    from sqlalchemy.orm import selectinload

    statement = select(Todo).options(
        selectinload(Todo.user)
    )
    return session.exec(statement).all()

# ❌ BAD: N+1 query problem
def get_todos_n_plus_one(session: Session):
    todos = session.exec(select(Todo)).all()
    for todo in todos:
        user = session.exec(
            select(User).where(User.id == todo.user_id)
        ).first()  # This queries once per todo!
```

#### Caching Strategy
```python
from fastapi import Depends
from functools import lru_cache
from redis import Redis

# In-memory cache for static data
@lru_cache(maxsize=128)
def get_settings():
    return Settings()

# Redis cache for dynamic data
redis = Redis(host='localhost', port=6379, decode_responses=True)

@router.get("/todos/{todo_id}")
async def get_todo(todo_id: int, current_user: User = Depends(get_current_user)):
    # Try cache first
    cache_key = f"todo:{current_user.id}:{todo_id}"
    cached = redis.get(cache_key)

    if cached:
        return json.loads(cached)

    # Query database
    todo = get_todo_from_db(todo_id, current_user.id)

    # Cache for 5 minutes
    redis.setex(cache_key, 300, json.dumps(todo.dict()))

    return todo
```

#### Async Database Operations
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Async database engine
engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db",
    echo=False,
    pool_size=20,
    max_overflow=0
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Async route handler
@router.get("/todos")
async def get_todos(current_user: User = Depends(get_current_user)):
    async with AsyncSessionLocal() as session:
        statement = select(Todo).where(Todo.user_id == current_user.id)
        result = await session.execute(statement)
        todos = result.scalars().all()
        return todos
```

#### Response Compression
```python
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI()

# Enable GZIP compression for responses >1KB
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### 3. Database Optimization

#### Indexing Strategy
```sql
-- Index on foreign keys
CREATE INDEX idx_todos_user_id ON todos(user_id);

-- Composite index for common queries
CREATE INDEX idx_todos_user_completed ON todos(user_id, completed);

-- Partial index for active todos
CREATE INDEX idx_todos_active ON todos(user_id) WHERE completed = false;

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM todos WHERE user_id = 1 AND completed = false;
```

#### Connection Pooling
```python
from sqlmodel import create_engine

engine = create_engine(
    DATABASE_URL,
    pool_size=10,          # Core connections
    max_overflow=10,       # Additional connections
    pool_timeout=30,       # Wait timeout
    pool_recycle=3600,     # Recycle after 1 hour
    pool_pre_ping=True     # Validate connections
)
```

## Monitoring & Profiling

### Frontend Monitoring

#### Web Vitals Tracking
```typescript
// app/layout.tsx
import { Analytics } from '@vercel/analytics/react'
import { SpeedInsights } from '@vercel/speed-insights/next'

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <Analytics />
        <SpeedInsights />
      </body>
    </html>
  )
}
```

#### Custom Performance Marks
```typescript
// utils/performance.ts
export function measurePageLoad(pageName: string) {
  if (typeof window !== 'undefined') {
    performance.mark(`${pageName}-start`)

    window.addEventListener('load', () => {
      performance.mark(`${pageName}-end`)
      performance.measure(
        `${pageName}-load`,
        `${pageName}-start`,
        `${pageName}-end`
      )

      const measure = performance.getEntriesByName(`${pageName}-load`)[0]
      console.log(`${pageName} load time: ${measure.duration}ms`)
    })
  }
}
```

### Backend Monitoring

#### Request Timing Middleware
```python
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)

        # Log slow requests
        if process_time > 0.5:
            logger.warning(
                f"Slow request: {request.method} {request.url.path} "
                f"took {process_time:.2f}s"
            )

        return response

app.add_middleware(TimingMiddleware)
```

#### Database Query Logging
```python
import logging
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - conn.info['query_start_time'].pop(-1)
    if total > 0.1:  # Log queries >100ms
        logger.warning(f"Slow query ({total:.2f}s): {statement}")
```

## Automated Performance Testing

### Lighthouse CI
```javascript
// lighthouserc.js
module.exports = {
  ci: {
    collect: {
      url: ['http://localhost:3000', 'http://localhost:3000/dashboard'],
      numberOfRuns: 3,
    },
    assert: {
      assertions: {
        'categories:performance': ['error', { minScore: 0.9 }],
        'categories:accessibility': ['error', { minScore: 0.95 }],
        'first-contentful-paint': ['error', { maxNumericValue: 1800 }],
        'largest-contentful-paint': ['error', { maxNumericValue: 2500 }],
        'cumulative-layout-shift': ['error', { maxNumericValue: 0.1 }],
      },
    },
  },
}
```

### Load Testing (Locust)
```python
# locustfile.py
from locust import HttpUser, task, between

class TodoAppUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # Login
        response = self.client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        self.token = response.json()["access_token"]

    @task(3)
    def get_todos(self):
        self.client.get(
            "/api/todos",
            headers={"Authorization": f"Bearer {self.token}"}
        )

    @task(1)
    def create_todo(self):
        self.client.post(
            "/api/todos",
            json={"title": "Test todo", "completed": False},
            headers={"Authorization": f"Bearer {self.token}"}
        )
```

## Validation Checks

When invoked, this skill will:
1. Run Lighthouse audits on all pages
2. Profile API endpoint response times
3. Analyze database query performance
4. Check bundle sizes against budgets
5. Monitor Core Web Vitals
6. Identify performance bottlenecks
7. Generate optimization recommendations
8. Run load tests

## Usage

```bash
# Run full performance audit
/performance-optimizer

# Frontend only
/performance-optimizer --frontend

# Backend only
/performance-optimizer --backend

# Database query analysis
/performance-optimizer --database

# Load testing
/performance-optimizer --load-test
```

## Success Criteria
- ✅ All Core Web Vitals within budget
- ✅ Lighthouse scores >90
- ✅ API p95 <300ms
- ✅ Database queries optimized (no N+1)
- ✅ Bundle sizes within limits
- ✅ Zero performance regressions in CI/CD

## Integration
This skill integrates with:
- **@logic-coordinator**: Primary owner and executor
- **@ui-auth-expert**: Frontend optimization
- **@fastapi-jwt-guardian**: API performance
- **@database-expert**: Query optimization
- **@qa-automation**: Performance regression testing

## Performance Checklist

### Frontend
- [ ] Code splitting implemented
- [ ] Images optimized with Next.js Image
- [ ] Static generation (SSG) where possible
- [ ] Incremental Static Regeneration (ISR) configured
- [ ] Bundle analysis reviewed
- [ ] Lazy loading for below-the-fold content
- [ ] Font optimization (next/font)
- [ ] Third-party scripts optimized (next/script)

### Backend
- [ ] Database queries indexed
- [ ] N+1 queries eliminated
- [ ] Connection pooling configured
- [ ] Response compression enabled
- [ ] Caching strategy implemented
- [ ] Async operations where beneficial
- [ ] Request/response validation optimized

### Database
- [ ] Indexes on foreign keys
- [ ] Composite indexes for common queries
- [ ] Query plans analyzed (EXPLAIN ANALYZE)
- [ ] Connection pool tuned
- [ ] Vacuum and analyze scheduled
- [ ] Slow query log enabled
