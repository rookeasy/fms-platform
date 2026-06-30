# FMS-0020 Current Codebase Inventory

Generated from the current repository at `C:\Users\Adam\Documents\Projects\fms-platform`.

Authoritative reference order used for deviation review:

1. FMS-0000 Platform Vision
2. FMS-0010 Master Data Dictionary
3. FMS-0003 Database Schema
4. FMS-0005 API Specification
5. FMS-0002 Architecture
6. FMS-0004 UI/UX
7. FMS-0007 Build Instructions

## Folder Structure

```text
fms-platform/
  backend/
    alembic/
      versions/
    app/
      api/
        v1/
          routes/
      core/
      db/
      models/
      schemas/
    scripts/
    tests/
  docs/
  frontend/
    app/
      buildings/
        [buildingId]/
          passport/
      certificates/
      dashboard/
      deficiencies/
      documents/
      inspections/
      login/
      memberships/
      reports/
      settings/
      users/
      work-orders/
    components/
    lib/
  infrastructure/
```

## Backend Modules

- `backend/app/main.py`: FastAPI app initialization, CORS middleware, error handler registration, `/health`, and `/api/v1` router mount.
- `backend/app/core/config.py`: Pydantic settings for app name, version, environment, API prefix, database URL, and CORS origins.
- `backend/app/core/error_handlers.py`: Standard error response handlers for HTTP, validation, and unhandled errors.
- `backend/app/db/base.py`: SQLAlchemy declarative base.
- `backend/app/db/session.py`: SQLAlchemy engine and session factory.
- `backend/app/api/deps.py`: Database session dependency, placeholder current-user dependency, and placeholder role dependency.
- `backend/app/api/v1/router.py`: Aggregates available API route modules.
- `backend/app/api/v1/routes/`: Placeholder route modules.
- `backend/app/models/mvp.py`: MVP SQLAlchemy model definitions.
- `backend/app/models/__init__.py`: Exports MVP model classes.
- `backend/app/schemas/common.py`: Shared error and placeholder response schemas.
- `backend/scripts/seed_reference_data.py`: Seed script for roles, asset types, and membership plans.
- `backend/tests/test_health.py`: Health, placeholder route, and standard error response tests.

## Frontend Modules

- `frontend/app/layout.tsx`: Root Next.js layout.
- `frontend/app/page.tsx`: Redirects root path to `/dashboard`.
- `frontend/app/globals.css`: Tailwind base styles and global typography/background.
- `frontend/lib/mock-data.ts`: Mock building, dashboard, work order, inspection, and timeline data.
- `frontend/lib/utils.ts`: `cn` class-name helper.
- `frontend/app/*/page.tsx`: Static shell pages for major FMS areas.

## Database Models

Implemented in `backend/app/models/mvp.py`:

- `Organization`
- `User`
- `Role`
- `OrganizationUser`
- `Building`
- `BuildingContact`
- `AssetType`
- `Asset`
- `Document`
- `WorkOrder`
- `InspectionTemplate`
- `InspectionTemplateItem`
- `Inspection`
- `InspectionResponse`
- `Deficiency`
- `Report`
- `Certificate`
- `MembershipPlan`
- `Membership`
- `HealthScore`
- `Notification`
- `AuditLog`

Shared mixins:

- `TimestampMixin`
- `SoftDeleteMixin`

## Alembic Migrations

- `backend/alembic/versions/0001_initial_foundation.py`
  - Empty foundation migration.
- `backend/alembic/versions/0002_mvp_schema.py`
  - Creates the MVP table set.
  - Enables PostgreSQL `pgcrypto`.
  - Uses UUID primary keys with `gen_random_uuid()`.
  - Adds tenant-oriented indexes for many organization-scoped tables.
  - Adds soft-delete columns to selected tables.

## API Routes

Mounted under `/api/v1`:

- `GET /api/v1/auth/me`
- `GET /api/v1/buildings`
- `GET /api/v1/work-orders`
- `GET /api/v1/inspections`
- `GET /api/v1/deficiencies`
- `GET /api/v1/documents`
- `GET /api/v1/reports`
- `GET /api/v1/certificates`
- `GET /api/v1/memberships`
- `GET /api/v1/users`
- `GET /api/v1/settings`

Root utility endpoint:

- `GET /health`

All `/api/v1` routes currently return placeholder responses only.

## UI Components

Reusable components in `frontend/components/`:

- `AppShell`
- `SidebarNavigation`
- `TopBar`
- `DashboardCard`
- `StatusBadge`
- `HealthScoreBadge`
- `DataTable`
- `BuildingCard`
- `PassportSection`
- `Timeline`

Frontend routes currently present:

- `/`
- `/login`
- `/dashboard`
- `/buildings`
- `/buildings/[buildingId]`
- `/buildings/[buildingId]/passport`
- `/work-orders`
- `/inspections`
- `/deficiencies`
- `/documents`
- `/reports`
- `/certificates`
- `/memberships`
- `/users`
- `/settings`

## Remaining TODOs

- Install dependencies and run the backend and frontend test suites.
- Add missing backend application folders required by FMS-0007 Phase 3, especially `services/`.
- Replace placeholder API route responses with spec-aligned request/response schemas and service boundaries.
- Add missing API route groups from FMS-0005.
- Align database models and migrations exactly to FMS-0003 and FMS-0010.
- Replace frontend mock terminology/statuses with values from FMS-0010.
- Connect frontend pages to backend APIs in later phases.
- Add tenant-isolation enforcement beyond placeholder dependencies.
- Add real authentication and role enforcement.
- Add audit logging service and audit events for major actions.
- Add storage abstraction before document upload work.
- Add generated identifiers required by future phases, including BPID, work order number, inspection number, deficiency number, report number, and certificate number.
- Add Prettier configuration if Phase 1 acceptance criteria are being enforced strictly.

## Deviations From FMS Specifications

### FMS-0010 Master Data Dictionary

- Placeholder roles use `admin`, `manager`, `inspector`, and `viewer`, but FMS-0010 defines roles such as `platform_admin`, `organization_admin`, `property_manager`, `building_owner`, `technician`, `engineer`, `readonly_viewer`, and `ahj_viewer`.
- Seed roles in `backend/scripts/seed_reference_data.py` do not match FMS-0010 exactly. Missing seeded roles include `platform_admin`, `organization_admin`, `property_manager`, `building_owner`, `engineer`, `readonly_viewer`, and `ahj_viewer`.
- Frontend mock statuses introduce values not defined in FMS-0010, including `Operational`, `Needs Review`, `At Risk`, `Open`, `In Review`, `High`, `Medium`, `Low`, `Current`, and `Invited` as display/status values without a mapped controlled vocabulary.
- Asset type seed values differ from FMS-0010/FMS-0003. Current seeds include `fire_alarm`, `sprinkler`, `elevator`, `hvac`, and `backflow`; FMS-0003 lists values such as `sprinkler_system`, `standpipe_system`, `fire_pump`, `backflow_preventer`, `fire_alarm_system`, `fire_extinguisher`, `emergency_lighting`, `kitchen_suppression`, `special_hazard_system`, `control_valve`, `riser`, `zone`, `hydrant`, and `fire_department_connection`.
- Membership plan seeds use `starter`, `professional`, and `enterprise`; FMS-0007 later references `Essentials`, `Professional`, and `Enterprise` for the membership engine. This should be reconciled against FMS-0010 before implementation continues.

### FMS-0003 Database Schema

- `organizations` is missing multiple specified fields, including `legal_name`, `organization_type`, phone/email/website fields, address fields, billing contact fields, and `notes`.
- `users` is missing `auth_provider_user_id`, `first_name`, `last_name`, `phone`, `job_title`, and `last_login_at`; it instead uses `full_name`.
- `roles` is missing `is_system_role`.
- `organization_users` is missing `invited_at` and `accepted_at`.
- `buildings` is missing `bpid`, `address_line_2`, `province_state`, latitude/longitude, building attributes, owner/property manager/AHJ/fire department/insurance fields, and `notes`; it uses `code` and `region`, which do not match the FMS-0003 table definition.
- `asset_types` includes `organization_id` and `code`, but FMS-0003 specifies global `name`, `category`, `description`, and `default_inspection_frequency_months`.
- `assets` is missing `asset_tag`, `location_description`, manufacturer/model, warranty, condition, inspection due fields, replacement cost, useful life, and `notes`; it uses `tag` and `installed_on`.
- `work_orders` is missing `work_order_number`, `work_order_type`, scheduling fields, customer approval fields, cost fields, notes, and `created_by_user_id`. Defaults also differ: current status is `open` and priority is `medium`; FMS-0003 defaults are `draft` and `normal`.
- `inspection_templates` does not match FMS-0003. It uses `asset_type_id` and `status`, while FMS-0003 specifies `description`, `inspection_type`, `standard_reference`, `is_system_template`, and `is_active`.
- `inspection_template_items` uses `inspection_template_id` and `label`; FMS-0003 specifies `template_id`, `section_name`, `item_label`, `item_description`, `response_type`, `code_reference`, `requires_photo`, and `creates_deficiency_on_fail`.
- `inspections` is missing `work_order_id`, `inspection_number`, `inspection_type`, performed/reviewed/customer signature fields, `summary`, and `notes`; current naming uses `inspection_template_id` and `inspector_user_id` instead of the FMS-0003 names.
- `inspection_responses` adds `organization_id` and JSON `value`, but FMS-0003 specifies `template_item_id`, `asset_id`, `response_value`, `response_notes`, `is_deficient`, and `created_deficiency_id`.
- Several later tables are present but intentionally shallow. `deficiencies`, `reports`, `certificates`, `health_scores`, `notifications`, and `audit_logs` do not yet include the complete field sets expected by FMS-0003 and later build phases.

### FMS-0005 API Specification

- Missing route groups: `/api/v1/organizations`, `/api/v1/building-contacts`, `/api/v1/assets`, `/api/v1/inspection-templates`, `/api/v1/membership-plans`, `/api/v1/health-scores`, `/api/v1/notifications`, `/api/v1/audit-logs`, and `/api/v1/dashboard`.
- Existing route groups expose only a single placeholder `GET` endpoint each, not the RESTful CRUD endpoints defined in FMS-0005.
- API placeholder responses use `{ module, status, message }`; FMS-0005 standard success responses require `data` and optional `pagination` envelopes.
- Auth placeholder `/api/v1/auth/me` returns a placeholder response rather than the user, organizations, and roles shape defined by FMS-0005.
- Permission checks are placeholders and do not enforce organization membership, role permissions, building access, tenant isolation, or soft-delete filtering.

### FMS-0002 Architecture

- Backend has `api`, `core`, `models`, `schemas`, and `tests`, but does not yet include a `services` layer.
- There is no repository/service boundary yet for tenant-aware business operations.
- No production logging, storage adapter, background jobs, or deployment-ready configuration exists yet.

### FMS-0004 UI/UX

- Frontend is a shell with mock data only and does not yet implement full building profile tabs, connected module states, or the complete Building Protection Passport data structure.
- Mock labels and statuses need to be reconciled against FMS-0010 controlled vocabulary before they become real UI states.
- Responsive layout exists at a basic shell level, but no visual verification has been run.

### FMS-0007 Build Instructions

- Phase 1 requested Prettier; no Prettier config currently exists.
- Phase 3 requested placeholder route files for all major modules; several FMS-0005 route groups are missing.
- Phase 4 requested models that match FMS-0003; the current MVP models create the table names but do not yet match many specified columns and controlled values.
- Python verification and tests have not been run successfully in this Codex environment because `python.exe` has failed to launch with a Windows logon-session error.
