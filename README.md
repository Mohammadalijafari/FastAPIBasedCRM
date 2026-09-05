# CRM System — Full Architecture

## Why this architecture?

The system is split into 4 distinct layers, each with a single responsibility:

```
Request → API (endpoints) → Service (business logic) → Repository (data access) → Database
                                    ↓
                          Schema (Pydantic) for input/output validation
```

| Layer | Responsibility | Example |
|---|---|---|
| `api/` | HTTP only: parse request, delegate to Service, return response | `deals.py` |
| `services/` | Business rules, transactions, orchestration | "A closed deal cannot be edited" |
| `repositories/` | Pure SQL — no business logic | Filtering, pagination, aggregation |
| `models/` | Database table structure (SQLAlchemy) | `Deal`, `Contact`, `Stage` |
| `schemas/` | API input/output validation (Pydantic) | `DealCreate`, `DealRead` |

## Key architectural decisions

**1. Row-level multi-tenancy**
Every table has an `organization_id`. `BaseRepository.list()` automatically applies this filter so no organization's data ever leaks into another's. Alternatives (schema-per-tenant or database-per-tenant) suit much larger scale but add operational complexity.

**2. Soft delete**
Customer data is never actually deleted (`is_deleted=True`). Losing the history of a Contact or Deal is not something a business can recover from.

**3. Pipeline stage history (`DealStageHistory`)**
An append-only table that logs every stage change — the foundation for reports like "average time spent per stage" and "conversion rate."

**4. Celery for async work**
Emails and notifications shouldn't slow down the API response. These jobs go to a Redis queue instead.

**5. JWT without database sessions**
`organization_id` and `role` are embedded directly in the token → every request can be authenticated without an extra query against `users`. For instant logout, you'd need a token blacklist in Redis (not included here — see below).

**6. RBAC via dependency injection**
```python
@router.delete(..., dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.OWNER))])
```

## Project structure

```
app/
  core/          Settings, security (JWT, password hashing)
  models/        SQLAlchemy models
  schemas/       Pydantic models
  repositories/  Raw SQL queries
  services/      Business logic
  api/v1/        FastAPI endpoints
  tasks/         Celery tasks
  db/            Database connection
alembic/         Database migrations
tests/           Unit tests
```

## Data model (core entities)

```
Organization (the company that owns the CRM)
  └── User (salesperson/team member)
  └── Company (customer's company)
        └── Contact (person associated with the company)
              └── Deal (sales opportunity)
                    └── Stage (position in a Pipeline)
                    └── Activity (call/meeting/task)
```

## Running locally (Development)

```bash
cp .env.example .env
docker compose up --build

# In a new terminal:
docker compose exec api alembic revision --autogenerate -m "init"
docker compose exec api alembic upgrade head
```

The service comes up at `http://localhost:8000/docs` (Swagger UI).

## Running tests

```bash
pytest tests/ -v
```

## What's still needed for real production use

This implementation is the architectural core, not a finished product. The following are intentionally out of scope here:

- [ ] Full CRUD endpoints for `Contact`, `Company`, `Activity`, `Pipeline` (follow the pattern in `deals.py`)
- [ ] Refresh token rotation + Redis blacklist for real logout
- [ ] Rate limiting (via `slowapi` or at the API gateway level)
- [ ] Full-text search (Postgres `tsvector` or Elasticsearch/Meilisearch)
- [ ] Full audit log (who changed what field, and when)
- [ ] Webhooks for external integrations (Zapier, email marketing tools)
- [ ] Import/export (CSV/Excel) for data migration
- [ ] Analytics/reporting (pipeline conversion rates, sales forecasting)
- [ ] Integration tests against a real database (testcontainers)
- [ ] Observability: Sentry for errors, Prometheus/Grafana for metrics

## A note on the word "perfect"

No architecture is ever truly "perfect" — there's always a trade-off between simplicity, scalability, and development speed. What's built here is a solid, industry-standard foundation (following patterns similar to what Salesforce/HubSpot/Pipedrive use in various forms) that:
- Is tested and actually runs (not just illustrative code)
- Can be extended without rewriting the lower layers
- Has critical business rules (tenant isolation, closed-deal locking) covered by tests

Happy to go deeper on any of the items above — for example, finishing the Contact/Company endpoints, or building out reporting.
