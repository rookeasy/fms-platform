# Backend Application Shell

FMS-0007 Phase 3 creates the backend application shell without implementing business logic.

## Scope

- FastAPI `/api/v1` router structure
- Root `/health` endpoint
- Configuration management through Pydantic settings
- SQLAlchemy session dependency
- Placeholder current-user dependency
- Placeholder role permission dependency
- Standard error response envelope
- CORS for local frontend development
- Placeholder route files for major FMS modules

## API Route Groups

- `/api/v1/auth`
- `/api/v1/buildings`
- `/api/v1/work-orders`
- `/api/v1/inspections`
- `/api/v1/deficiencies`
- `/api/v1/documents`
- `/api/v1/reports`
- `/api/v1/certificates`
- `/api/v1/memberships`
- `/api/v1/users`
- `/api/v1/settings`

## Out of Scope

- Real authentication
- Authorization policy enforcement
- Domain models
- Database queries
- Business workflows
