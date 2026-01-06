---
name: schema-enforcer
description: Enforces SQLModel schemas and mandatory user-id isolation on all database queries
version: 1.0.0
owner: database-expert
tags: [database, security, sqlmodel, neon, postgres, isolation]
---

# Schema Enforcer Skill

## Purpose
Automatically enforce database schema integrity and mandatory user-id isolation to prevent data leakage between users in multi-tenant applications.

## Scope
- **Owned By**: @database-expert
- **Technology Stack**: SQLModel, Neon Postgres, FastAPI
- **Security Mandate**: User-id isolation on EVERY query

## Mandatory Requirements

### 1. Schema Validation
- [ ] All models inherit from SQLModel base
- [ ] All user-owned tables have `user_id: int` foreign key
- [ ] Indexes exist on `user_id` columns
- [ ] Cascading deletes configured properly
- [ ] Timestamps (`created_at`, `updated_at`) on all tables
- [ ] Soft delete pattern implemented where needed

### 2. User Isolation Rules
**CRITICAL**: Every SELECT, UPDATE, DELETE query MUST filter by `user_id`

```python
# ✅ CORRECT - User isolation enforced
todos = session.exec(
    select(Todo).where(Todo.user_id == current_user.id)
).all()

# ❌ INCORRECT - Data leakage risk
todos = session.exec(select(Todo)).all()
```

### 3. Enforcement Patterns

#### Create Operations
```python
def create_todo(todo: TodoCreate, current_user: User):
    db_todo = Todo(
        **todo.model_dump(),
        user_id=current_user.id  # ✅ Mandatory
    )
    session.add(db_todo)
    session.commit()
```

#### Read Operations
```python
def get_todos(current_user: User):
    return session.exec(
        select(Todo)
        .where(Todo.user_id == current_user.id)  # ✅ Mandatory
    ).all()
```

#### Update Operations
```python
def update_todo(todo_id: int, data: TodoUpdate, current_user: User):
    todo = session.exec(
        select(Todo)
        .where(Todo.id == todo_id)
        .where(Todo.user_id == current_user.id)  # ✅ Mandatory
    ).first()
    if not todo:
        raise HTTPException(404, "Todo not found")
    # ... update logic
```

#### Delete Operations
```python
def delete_todo(todo_id: int, current_user: User):
    todo = session.exec(
        select(Todo)
        .where(Todo.id == todo_id)
        .where(Todo.user_id == current_user.id)  # ✅ Mandatory
    ).first()
    if not todo:
        raise HTTPException(404, "Todo not found")
    session.delete(todo)
    session.commit()
```

### 4. Schema Migration Standards
- Migrations tracked in version control
- Rollback plan for every migration
- Test migrations on staging before production
- Never drop columns without deprecation period

## Validation Checks

When invoked, this skill will:
1. Scan all SQLModel definitions in `backend/models/`
2. Analyze all database queries in `backend/routers/` and `backend/services/`
3. Flag any query missing `user_id` filter
4. Verify foreign key constraints exist
5. Check for proper indexing on `user_id` columns
6. Generate security audit report

## Automatic Fixes

The skill can automatically:
- Add missing `user_id` filters to queries
- Generate migration files for missing indexes
- Add timestamp fields to models
- Implement soft delete pattern

## Usage

```bash
# Validate all queries
/schema-enforcer

# Audit specific model
/schema-enforcer --model Todo

# Generate migration for missing indexes
/schema-enforcer --fix-indexes

# Security audit report
/schema-enforcer --security-audit
```

## Success Criteria
- ✅ Zero queries without user-id isolation
- ✅ All models have proper schema definition
- ✅ Foreign keys and indexes in place
- ✅ Migration history is clean and reversible

## Integration
This skill integrates with:
- **@database-expert**: Primary owner and executor
- **@api-expert**: Validates query patterns in endpoints
- **@auth-guard**: Ensures authentication precedes data access
- **@qa-automation**: Automated security testing

## Security Principles
1. **Zero Trust**: Never trust user input or session data
2. **Defense in Depth**: Multiple layers of isolation checks
3. **Fail Secure**: Deny access if user_id is missing or invalid
4. **Audit Trail**: Log all data access with user context
