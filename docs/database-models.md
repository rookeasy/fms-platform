# Database Models and Migrations

FMS-0007 Phase 4 creates the MVP SQLAlchemy model layer, Alembic migration, and reference-data seed script.

## Scope

- UUID primary keys
- PostgreSQL-compatible column types
- Tenant isolation through `organization_id` on tenant-scoped tables
- `created_at` and `updated_at` timestamps
- Soft-delete `deleted_at` fields on mutable resource tables
- SQLAlchemy relationships for core model navigation
- Alembic migration for MVP tables
- Seed script for roles, global asset types, and membership plans

## MVP Tables

- organizations
- users
- roles
- organization_users
- buildings
- building_contacts
- asset_types
- assets
- documents
- work_orders
- inspection_templates
- inspection_template_items
- inspections
- inspection_responses
- deficiencies
- reports
- certificates
- membership_plans
- memberships
- health_scores
- notifications
- audit_logs

## Out of Scope

- Optional future tables
- Business workflows
- API CRUD behavior
- Production data retention policies
