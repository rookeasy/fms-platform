# M6 Property & Campus Management

## Purpose

M6 adds a Property / Campus layer so FMS can represent one owner or customer site that contains multiple buildings, shared fire protection infrastructure, assets, documents, and closeout evidence.

## Data Hierarchy

The MVP hierarchy is:

Organization -> Property / Campus -> Buildings / Shared Infrastructure -> Assets / Documents / Closeout Packages

Properties are the top-level managed sites. Campuses are optional groupings, phases, zones, or complexes under a property. Buildings remain the operational unit for assets, documents, inspections, and Building Protection Passport records.

## SOHO Phase I Modelling Decision

SOHO Phase I is modelled as one property/campus at `505-517 Highland Road West, Stoney Creek, Ontario`.

The property contains:

- SOHO Phase I / Building A
- SOHO Phase I / Building B
- Common Parking Garage / Shared Fire Protection Infrastructure

Building A is not treated as the entire SOHO Phase I site. The seed keeps the oldest / lowest BPID Building A record as the canonical Building A Passport and assigns it to the SOHO Phase I property.

## Shared Infrastructure Rule

Shared infrastructure is represented as a building-like record with `building_type = "shared_infrastructure"`. This preserves the existing building-scoped asset and document model without adding a separate property-asset schema in the MVP.

The SOHO shared infrastructure record carries:

- Fire Pump
- Jockey Pump
- 6 inch Backflow Preventer
- Fire Department Connection
- Common Standpipe System
- Dry Parking Garage System
- Underground Fire Main

## Building Passport Relationship

Each physical building or shared infrastructure record can maintain its own Building Protection Passport. The SOHO Phase I property page rolls those Passport records up into one property view for operational review and sales demonstrations.

## Closeout Package Relationship

Closeout evidence remains document metadata attached to building-like records:

- Building A test certificates attach to Building A.
- Building B test certificates attach to Building B.
- Dry P1 East, Dry P1 West, Dry P1 Standpipe, and Dry Ground Floor Amenity attach to Common Infrastructure.
- Wet Combined Sprinkler / Standpipe attaches to Common Infrastructure in the MVP.

The property detail page summarizes related documents, client-visible records, Passport records, and closeout readiness across the property.

## ITM Relationship

ITM service workflows continue to operate at the building or shared-infrastructure record level. The property/campus layer provides the roll-up needed to understand the full site relationship, including which buildings and shared systems are ready for service transition.

## Backend

M6 adds:

- `properties` table
- `campuses` table
- Optional `property_id` and `campus_id` on buildings
- Property and campus CRUD endpoints
- Building property/campus assignment endpoint

Key endpoints:

- `GET /api/v1/properties/summary`
- `GET /api/v1/properties`
- `POST /api/v1/properties`
- `GET /api/v1/properties/{property_id}`
- `PATCH /api/v1/properties/{property_id}`
- `DELETE /api/v1/properties/{property_id}`
- `GET /api/v1/campuses`
- `POST /api/v1/campuses`
- `GET /api/v1/campuses/{campus_id}`
- `PATCH /api/v1/campuses/{campus_id}`
- `DELETE /api/v1/campuses/{campus_id}`
- `PATCH /api/v1/buildings/{building_id}/property-campus`

## Frontend

M6 adds:

- `/properties`
- `/properties/[propertyId]`
- Building profile property/campus association display

The property detail page shows:

- Property name
- Address
- Organization
- Status
- Related buildings
- Shared infrastructure
- Key assets
- Document/evidence summary
- Closeout readiness state

## Seed Script

Run:

```powershell
cd C:\Users\Adam\Documents\Projects\fms-platform\backend
.\.venv\Scripts\Activate.ps1
python -m scripts.seed_soho_phase1_property
```

The script is idempotent and creates/reuses:

- Organization: Fuzion Fire Inc.
- Property/Campus: SOHO Phase I
- Building A
- Building B
- Common Parking Garage / Shared Fire Protection Infrastructure
- SOHO Phase I representative assets
- SOHO Phase I closeout document metadata

The cleanup command is also supported:

```powershell
python -m scripts.seed_soho_phase1_property --cleanup-soho
```

It archives duplicate SOHO Building A records, keeps the oldest / lowest BPID Building A Passport, reassigns known SOHO documents and assets, and prints a clear created/reused/reassigned/archive summary.

## How to Verify

Open:

- http://localhost:8000/api/v1/buildings
- http://localhost:3000/buildings
- http://localhost:3000/properties
- http://localhost:3000/properties/<property-id>

SOHO Phase I should show Building A, Building B, and Common Parking Garage / Shared Fire Protection Infrastructure as related records.

## Known MVP Limitations

- Documents and assets are still scoped to building-like records, not directly to properties.
- Shared infrastructure is modelled as a special building record.
- The property detail page is a read-focused roll-up, not a full edit workspace.
- There is no map, floor, suite, lease, owner portal, campus drawing, or bulk reassignment workflow.
- Closeout readiness is an MVP visual summary based on available related records, not a formal approval workflow.
- Permissions use the existing role dependency pattern.

## Future Improvements

- Add first-class property assets and property-level documents.
- Add property detail editing and bulk building assignment.
- Add campus drawings, zones, floors, suites, and shared-system topology.
- Add closeout package roll-up approval states.
- Add ITM contract conversion and lifecycle opportunity tracking at property level.
- Add dashboard widgets for property risk, Passport completeness, and service readiness.
