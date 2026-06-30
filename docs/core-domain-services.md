# Core Domain Services and CRUD APIs

FMS-0007 Phase 5 implements the first backend vertical slice:

- Organizations
- Users
- Roles
- Organization users
- Buildings
- Building contacts

## Implementation Notes

- FastAPI route handlers remain thin.
- Business rules live in service modules.
- Tenant-aware filtering is applied through service methods.
- Soft-deleted records are excluded by default.
- BPID generation happens server-side in `BuildingService`.
- Building creation, update, and soft delete create audit log records.
- Frontend integration is intentionally out of scope.

## Route Groups

- `/api/v1/auth`
- `/api/v1/organizations`
- `/api/v1/users`
- `/api/v1/roles`
- `/api/v1/organization-users`
- `/api/v1/buildings`
- `/api/v1/building-contacts`

## Out of Scope

- Inspections
- Deficiencies
- Certificates
- Reports
- Memberships
- Production authentication
- Frontend integration
