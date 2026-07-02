# M7 Property Intelligence Platform

## Purpose

M7 adds property-level intelligence to FOP/FMS. It turns the M6 Property / Campus structure into an executive-ready operating view that rolls up buildings, shared infrastructure, assets, documents, deficiencies, work orders, health scores, capital exposure, and Passport evidence into one property dashboard.

The first reference implementation is SOHO Phase I:

- Building A
- Building B
- Common Parking Garage / Shared Fire Protection Infrastructure

## Data Model

M7 builds on the existing hierarchy:

```text
Organization
Property / Campus
Buildings / Shared Infrastructure
Assets / Documents / Operational Records
Property Intelligence Rollups
```

Existing source models used by M7:

- `Property`
- `Campus`
- `Building`
- `Asset`
- `Document`
- `HealthScore`
- `Deficiency`
- `WorkOrder`
- `Inspection`

M7 adds persisted intelligence support:

- `PropertyIntelligenceSnapshot`
- `PropertyIntelligenceFactor`

Snapshots store calculated scores, counts, capital exposure, and summary metadata. Factors capture the score drivers used for Health, Confidence, Risk, Readiness, and Passport rollups.

## API Routes

Primary dashboard route:

```http
GET /api/v1/properties/{property_id}/intelligence
```

Recalculate and persist a new snapshot:

```http
POST /api/v1/properties/{property_id}/intelligence/recalculate
```

Focused summary routes:

```http
GET /api/v1/properties/{property_id}/intelligence/health
GET /api/v1/properties/{property_id}/intelligence/confidence
GET /api/v1/properties/{property_id}/intelligence/risk
GET /api/v1/properties/{property_id}/intelligence/readiness
GET /api/v1/properties/{property_id}/intelligence/passport
GET /api/v1/properties/{property_id}/intelligence/capital
GET /api/v1/properties/{property_id}/intelligence/deficiencies
```

Legacy-compatible executive dashboard route:

```http
GET /api/v1/properties/{property_id}/executive-dashboard
```

## Rollup Logic

Property Intelligence is calculated from records assigned to buildings under the property.

Health combines:

- Latest building health scores, when available
- Property Confidence
- Property Readiness
- Property Passport completeness
- Inverse Property Risk

Confidence measures:

- Buildings with usable address data
- Assets with condition ratings
- Documents that are Passport records or client visible
- Data gaps across building, asset, and document records

Risk measures:

- Open deficiencies
- Critical/high deficiencies
- Overdue work orders
- Expired documents
- Poor or critical asset conditions

Passport measures:

- Passport record count
- Client-visible record count
- Coverage across buildings and shared infrastructure

Capital summary measures:

- Asset replacement cost exposure
- Near-term asset renewal count
- Assets missing replacement cost data
- Capital exposure by building/shared infrastructure

Deficiency summary measures:

- Open deficiencies
- Critical/high deficiencies
- Counts by severity
- Counts by status
- Counts by building/shared infrastructure

## Readiness Rules

Property Readiness is based on whether the property has:

- Related building records
- Shared infrastructure represented
- Registered assets
- Passport records available
- No open critical/high deficiencies
- No overdue open work orders

The dashboard marks the property as ready for handover when readiness is strong and no critical readiness blockers are present.

## Property Dashboard Behavior

The property detail workspace displays:

- Executive Dashboard score cards
- Property Health
- Property Confidence
- Property Risk
- Property Readiness
- Buildings summary table
- Deficiency / Capital summary
- Passport status summary
- Executive Review status placeholder

Frontend components live under:

```text
frontend/components/properties/intelligence
```

The existing `/properties` page and building profile pages continue to work. Building detail pages still link back to the related property/campus where available.

## Known Limitations

- Executive Review is currently a placeholder, not a generated review workflow.
- Property-level documents are still represented through building/shared-infrastructure records.
- Shared infrastructure is represented as a building-like record with `building_type = shared_infrastructure`.
- Capital exposure depends on populated asset replacement cost estimates.
- Deficiency and work-order value depends on operational data being seeded or implemented in later modules.
- Scoring rules are MVP formulas and should be reviewed before customer-facing production use.
- No PDF generation, approvals, signatures, CRM integration, or email delivery is included in M7.

## How To Run

From the backend:

```powershell
cd C:\Users\Adam\Documents\Projects\fms-platform\backend
.\.venv\Scripts\Activate.ps1
alembic upgrade head
python -m scripts.seed_soho_phase1_property
```

From the frontend:

```powershell
cd C:\Users\Adam\Documents\Projects\fms-platform\frontend
npm run typecheck
npm run dev
```

## How To Verify

Backend:

```text
http://localhost:8000/api/v1/properties/{property_id}/intelligence
http://localhost:8000/api/v1/properties/{property_id}/intelligence/health
http://localhost:8000/api/v1/properties/{property_id}/intelligence/risk
http://localhost:8000/api/v1/properties/{property_id}/intelligence/readiness
```

Frontend:

```text
http://localhost:3000/properties
http://localhost:3000/properties/{property_id}
```

For SOHO Phase I, run the seed script and use the printed `property_id` in the property detail URL.

## Next Recommended Phase

M8 Portfolio Intelligence.

M8 should roll multiple properties into portfolio-level intelligence, including:

- Portfolio Health
- Portfolio Confidence
- Portfolio Risk
- Portfolio Readiness
- Portfolio Passport coverage
- Capital exposure by property
- Deficiency trends by property
- Executive portfolio dashboard
- Cross-property prioritization for service, sales, and capital planning
