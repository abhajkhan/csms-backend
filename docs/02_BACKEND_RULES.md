# BACKEND_RULES.md

# Backend Development Rules

**Version:** 2.1

This document defines **how the backend must be implemented**.

All business rules, workflows, database design, APIs, and module responsibilities are defined in **CSMS_SPEC.md**.

If this document conflicts with **CSMS_SPEC.md**, the specification always takes precedence.

---

# 1. Technology Stack

The backend must use:

| Component        | Technology             |
| ---------------- | ---------------------- |
| Language         | Python 3.12+           |
| Framework        | FastAPI                |
| Database         | PostgreSQL             |
| ORM              | SQLAlchemy 2.x (Async) |
| Migration        | Alembic                |
| Validation       | Pydantic v2            |
| Authentication   | JWT                    |
| Password Hashing | BCrypt                 |
| Testing          | Pytest                 |

No alternative frameworks or libraries may be introduced without approval.

---

# 2. Architecture

The backend follows Layered Architecture.

```
API
 ↓
Service
 ↓
Repository
 ↓
Database
```

Each layer has exactly one responsibility.

Business logic must never bypass the Service layer.

---

# 3. Layer Responsibilities

## API Layer

Responsible for:

* HTTP routing
* Request validation
* Authentication
* Authorization
* Calling services
* Returning HTTP responses

Must never:

* Execute SQL
* Contain business logic
* Manage transactions

---

## Service Layer

Responsible for:

* Business logic
* Business validation
* Coordinating repositories
* Transaction management
* Raising business exceptions

Services may coordinate multiple repositories.

Must never:

* Return HTTP responses
* Access request objects
* Execute raw SQL directly

---

## Repository Layer

Responsible for:

* Database access
* CRUD operations
* Query construction
* Filtering
* Pagination

Must never:

* Contain business rules
* Perform authorization
* Commit or rollback transactions
* Call other repositories

Repositories should only mutate database state through requests initiated by Services.

---

## Model Layer

Responsible for:

* Database schema
* Relationships
* Constraints

Models must not contain business logic.

---

## Schema Layer

Responsible for:

* Request DTOs
* Response DTOs
* Validation

Only Pydantic schemas are exposed outside the Service layer.

---

# 4. Async Development

The application uses asynchronous execution throughout.

* Use AsyncSession.
* Endpoints must be async.
* Services must be async.
* Repositories must be async.
* Never mix synchronous and asynchronous SQLAlchemy sessions.

---

# 5. Dependency Injection

Use FastAPI dependency injection for:

* Database session
* Current user
* Authentication
* Authorization
* Pagination
* Application services (where appropriate)

Infrastructure dependencies must not be instantiated manually.

---

# 6. Repository Pattern

Every business module follows:

```
Repository
 ↓
Service
 ↓
Endpoint
```

Repositories own all ORM interaction.

---

# 7. Transactions

Transactions are managed exclusively in the Service layer.

Repositories must never call:

* commit()
* rollback()

Each business operation should execute within a single transaction unless CSMS_SPEC.md specifies otherwise.

Transactions must either:

* Commit completely
* Roll back completely

---

# 8. Atomic Operations

Business operations defined as atomic in **CSMS_SPEC.md** must always execute within a single transaction.

Partial updates are never allowed.

---

# 9. Authentication

Authentication uses JWT.

Protected endpoints must verify:

* Access token
* Active account
* User identity

Refresh-token behavior follows CSMS_SPEC.md.

Never trust client-provided identity or roles.

---

# 10. Authorization

Authorization is role-based.

Endpoint access should be validated before business execution.

Business-level authorization rules belong in the Service layer.

Repositories must never perform authorization.

---

# 11. Validation

Validation occurs in three stages.

### Request Validation

Handled by Pydantic.

Examples:

* Required fields
* Length
* Format
* Numeric ranges

### Business Validation

Handled by Services.

Examples:

* Business state
* Duplicate prevention
* Resource ownership
* Domain rules

### Database Validation

Handled using:

* Constraints
* Foreign Keys
* Unique Indexes

---

# 12. Exception Handling

Business failures use custom exceptions.

Services must never raise HTTPException.

The API layer converts business exceptions into HTTP responses.

---

# 13. Response Format

All endpoints must return the response format defined in **CSMS_SPEC.md**.

Do not invent alternate response structures.

---

# 14. Pagination

All list endpoints should support pagination where appropriate.

Recommended parameters:

* page
* page_size

Optional:

* search
* sorting
* filtering

---

# 15. Logging

Log:

* Authentication failures
* Authorization failures
* Transaction failures
* Unexpected exceptions
* Critical business events

Never log:

* Passwords
* Tokens
* Secrets
* Sensitive personal data

---

# 16. Soft Delete

Use soft delete only where explicitly defined in CSMS_SPEC.md.

Do not introduce soft delete without specification approval.

---

# 17. Naming Conventions

## Database

* snake_case tables
* snake_case columns

## Python

Classes

* PascalCase

Functions

* snake_case

Variables

* snake_case

Constants

* UPPER_CASE

---

# 18. SQLAlchemy Rules

Use:

* SQLAlchemy 2.x ORM
* Typed models
* Relationships
* Appropriate eager/lazy loading

Avoid:

* Raw SQL unless justified
* Duplicate queries

---

# 19. API Design

Follow REST conventions.

Use:

* GET
* POST
* PUT
* PATCH
* DELETE

Resources should:

* Use plural nouns
* Avoid verbs
* Follow endpoint definitions in CSMS_SPEC.md

---

# 20. Testing

Every completed feature should include appropriate:

* Unit tests
* Repository tests
* API tests

Business rules should primarily be tested at the Service layer.

Critical transactional workflows should include transaction tests.

---

# 21. Performance

Avoid:

* N+1 queries
* Duplicate database calls
* Unnecessary commits

Optimize only when measurable benefits exist.

---

# 22. Configuration

Application configuration must come from environment variables.

Do not hardcode:

* Secrets
* Database credentials
* JWT keys
* API keys

---

# 23. Database Migrations

Every schema change must include an Alembic migration.

Do not modify production schemas manually.

---

# 24. Idempotency

Operations that may be retried or submitted multiple times must prevent unintended duplicate effects where required by CSMS_SPEC.md.

---

# 25. Existing Code

Before creating new code:

1. Inspect the existing implementation.
2. Reuse existing abstractions where appropriate.
3. Prefer minimal refactoring over rewriting.
4. Remove duplicate business logic.
5. If implementation conflicts with CSMS_SPEC.md, explain the conflict and perform the minimum refactor required.

Do not preserve incorrect behavior simply because it already exists.

---

# 26. AI Agent Rules

AI agents must never:

* Invent business rules
* Invent workflows
* Invent user roles
* Invent APIs
* Invent database schema
* Change architecture
* Change dependencies
* Bypass Services
* Bypass Repositories

When requirements are unclear:

* Stop.
* Explain the ambiguity.
* Request clarification before implementation.

---

# 27. Source of Truth

Documents are authoritative in this order:

1. CSMS_SPEC.md
2. BACKEND_RULES.md
3. requirements.txt

---

# 28. Documentation Policy

When implementation changes require documentation updates:

* Update CSMS_SPEC.md for functional changes.
* Update requirements.txt for dependency changes.
* Generate Alembic migrations for schema changes.

Keep documentation synchronized with implementation.

---

# 29. Definition of Done

A feature is complete only when:

* It complies with CSMS_SPEC.md.
* It follows BACKEND_RULES.md.
* Business rules are satisfied.
* Authorization and validation are complete.
* Required tests pass.
* Required migrations are included.
* Documentation is updated where applicable.
