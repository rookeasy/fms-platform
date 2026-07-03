# Base44 Mobile Field Layer

## Purpose

Base44 is the FOP mobile companion for technicians and field users. Fuzion Operating Platform remains the central system of record for customers, sites, work orders, inspections, deficiencies, documents, and closeout evidence.

The mobile app should collect field evidence quickly, cache work during poor signal, and sync every submission back to the FOP backend.

## Architecture

- FOP web/admin remains the primary operating platform.
- Base44 mobile acts as the technician interface.
- The FOP backend owns validation, persistence, tenant access, and downstream reporting.
- Base44 should call FOP APIs instead of duplicating business rules.
- Every mobile submission includes technician ID, job ID, customer/site ID, timestamps, and sync status.

## Mobile App Structure

The Base44 mobile app structure is captured in `docs/base44-mobile-app-structure.json`.

Required screens:

1. Technician Login
2. Today's Assigned Work
3. Service Work Order
4. Inspection Checklist
5. Deficiency Capture
6. Photo Upload
7. Customer Signature
8. Site Notes
9. Material Used
10. Completion Status
11. Sync to FOP

## Project Atlas Styling

Use the Fuzion Tech Inc. identity throughout:

- Product: Fuzion Operating Platform
- Short name: FOP
- Tagline: BUILD - ADVISE - PROTECT
- Background: `#050A18`
- Surface: `#0B1224`
- Elevated surface: `#111827`
- Accent: coral from the Fuzion Tech mark
- Status language: Saved locally, Syncing, Synced, Failed

Mobile cards, buttons, badges, forms, and headers should match the Project Atlas dark enterprise SaaS system used by FOP.

## FOP API Endpoints

The MVP mobile endpoint group is mounted under `/api/v1/mobile`.

| Workflow | Endpoint | Result |
| --- | --- | --- |
| Today's assigned work | `GET /api/v1/mobile/assigned-jobs` | Returns active work orders for mobile use. |
| Work order detail | `GET /api/v1/mobile/work-orders/{work_order_id}` | Returns the selected mobile job. |
| Inspection forms | `GET /api/v1/mobile/work-orders/{work_order_id}/inspection-forms` | Returns available inspection checklists for the job building. |
| Inspection response | `POST /api/v1/mobile/inspection-responses` | Upserts an inspection response. |
| Deficiency capture | `POST /api/v1/mobile/deficiencies` | Creates a FOP deficiency record. |
| Photo upload | `POST /api/v1/mobile/photos` | Stores the field photo as a FOP document. |
| Customer signature | `POST /api/v1/mobile/signatures` | Stores the customer signature as a service record document. |
| Site notes | `POST /api/v1/mobile/site-notes` | Appends a Base44 field note to the work order. |
| Material used | `POST /api/v1/mobile/materials-used` | Appends a material-used note to the work order. |
| Completion status | `POST /api/v1/mobile/completion-status` | Updates work order status and completion timestamp. |

## Data Mapping

| Base44 concept | FOP record |
| --- | --- |
| Assigned job | `WorkOrder` |
| Work order detail | `WorkOrder` with building/site context |
| Inspection checklist | `Inspection`, `InspectionTemplate`, `InspectionTemplateItem` |
| Checklist answer | `InspectionResponse` |
| Deficiency | `Deficiency` |
| Field photo | `Document` with `document_type=photo` |
| Customer signature | `Document` with `document_type=service_record` |
| Site notes | `WorkOrder.description` MVP field note |
| Material used | `WorkOrder.description` MVP field note |
| Completion status | `WorkOrder.status`, `WorkOrder.completed_at` |

## Offline and Poor Signal

Base44 should cache assigned jobs and active job detail locally. Field submissions can be saved as drafts and queued for sync.

Recommended sync queue fields:

- `localDraftId`
- `technicianId`
- `jobId`
- `customerSiteId`
- `recordType`
- `payload`
- `createdAt`
- `updatedAt`
- `syncStatus`
- `lastSyncAttemptAt`
- `lastSyncError`

Sync status values:

- Saved locally
- Syncing
- Synced
- Failed

## MVP Limitations

- Base44 app deployment is represented as an implementation contract in this repository; the actual Base44 workspace must be configured with these screens and endpoints.
- Authentication is still placeholder-aligned with the current FOP MVP.
- Site notes and materials are appended to work order descriptions until dedicated field activity tables are added.
- Signature files are stored as service record documents.
- Rich technician assignment filtering depends on future user and dispatch models.

## Future Enhancements

- Dedicated mobile sync queue table with idempotency keys.
- Dedicated work order notes and materials tables.
- Technician assignment and dispatch calendar.
- Offline conflict resolution and retry telemetry.
- Push notifications for new assignments and failed syncs.
- Production SSO/auth integration shared between FOP and Base44.
