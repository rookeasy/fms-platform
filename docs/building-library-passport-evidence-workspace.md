# Building Library Passport Evidence Workspace

## Purpose

The Building Library replaces the generic customer-facing Documents experience with an evidence workspace for the Building Protection Passport.

Users are adding evidence, not merely uploading files. Each evidence item strengthens closeout readiness, Passport completion, and the long-term building record.

## Terminology

- Building Library: the portfolio and building-level evidence workspace.
- Evidence: uploaded or curated records that support the building Passport.
- Evidence Item: a single document metadata record or uploaded file.
- Add Evidence: the primary upload/classification action.
- Build Passport: the guided readiness workflow for reviewing evidence before a future Passport export.

Backend table, schema, and service names can continue to use document terminology where they are implementation details.

## Portfolio Library

The existing `/documents` route remains compatible, but it now presents the Building Library index.

The index shows one row per building with:

- Building and property name
- Job number
- Passport number / BPID
- Total evidence items
- Passport completion percentage
- Missing evidence count
- Last updated date
- Closeout readiness status
- BUILD / ADVISE / PROTECT lifecycle stage
- View Library and Build Passport actions

## Building Library

The building-level route is:

`/buildings/<building-id>/library`

The page shows:

- Building name
- Property name
- Job number
- BPID / Passport number
- Passport completion
- Closeout readiness
- Last updated date
- Add Evidence, Build Passport, Open Closeout, and Open Passport actions

## Evidence Categories

The MVP category set is:

- Building Protection Passport
- Drawings
- As-Built Drawings
- P.Eng. Compliance
- NFPA Contractor Compliance
- Material & Test Certificates
- Asset Register
- Warranty
- Product Data
- O&M Manuals
- Photos
- Handover
- ITM Transition
- Membership
- Other

Each category card shows item count, completion state, latest revision/date where available, Add Evidence, and View Evidence actions.

## Build Passport Workflow

The Build Passport action opens a guided evidence workflow. It does not generate the final Passport PDF.

MVP workflow steps:

1. Select or upload files.
2. Review document classification.
3. Assign property, building, or shared infrastructure.
4. Review Passport Record and Client Visible settings.
5. Review AI metadata and asset suggestions.
6. Approve evidence.
7. Recalculate closeout and Passport completion.
8. Show remaining missing items.

## AI Classification Workflow

The Building Library reuses the existing document extraction and asset suggestion pipeline.

Uploaded evidence can show:

- AI extraction status
- Suggested asset associations
- Confidence
- Review required status

AI suggestions remain reviewable. The MVP does not silently create authoritative assets.

## Closeout Interaction

Closeout sections link to the Building Library with the related evidence category preselected. After evidence is uploaded, reclassified, toggled as a Passport Record, toggled as Client Visible, superseded, or archived, the Building Library reloads its rollups from existing backend scoring and document services.

Building Health Index is not increased solely because evidence was uploaded.

## Passport Completion Logic

Passport completion currently follows the existing closeout scoring service. Missing item counts come from the closeout score. Category completeness is computed from existing document evidence category, document type, Passport Record, and Client Visible flags.

## SOHO Routing Rules

SOHO Phase I should be organized as:

- Building A drawings/certificates: Building A
- Building B drawings/certificates: Building B
- P1 East, P1 West, Standpipe, Amenity, Fire Pump, and Backflow: Common Parking Garage / Shared Fire Protection Infrastructure when represented as a building/shared-infrastructure record
- Property-level compliance and handover documents: SOHO Phase I Property

The MVP does not invent missing SOHO records. It routes through existing building/property assignments.

## MVP Limitations

- Final Passport PDF generation is not implemented.
- Browser folder upload is not implemented.
- Multi-file upload uses the existing single-file backend upload endpoint once per selected file.
- Shared infrastructure is supported only where represented by existing property/building records.
- Category completion is heuristic and based on current document metadata.
- Production auth, e-signatures, cloud object storage migration, autonomous asset creation, billing integration, and folder upload are future phases.

## Future Roadmap

- Dedicated bulk upload endpoint with per-file progress persistence.
- Folder upload after browser/backend support is reliable.
- First-class closeout package and evidence models.
- Dedicated shared infrastructure evidence routes.
- Formal evidence approval workflow.
- Generated Passport packages and final PDF exports.
