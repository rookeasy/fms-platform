# M7B Property Intelligence

## Purpose

M7B adds the first Property Intelligence MVP for FOP/FMS. It rolls building-level records up to the property level so users can understand site health, confidence, risk, readiness, Passport completeness, capital exposure, and executive-review readiness.

## Current MVP Approach

Property Intelligence is computed from existing records. It does not add new database tables in M7B.

Inputs:

- Property
- Related buildings and shared infrastructure
- Assets
- Documents
- Passport records
- Deficiencies
- Work orders
- Inspections

Deficiency, work order, and inspection APIs are still early/placeholder modules, but their database models are included in the rollup so future operational data automatically improves the intelligence output.

## API Endpoints

```http
GET /api/v1/properties/{property_id}/intelligence
GET /api/v1/properties/{property_id}/executive-dashboard
```

Both endpoints return the same MVP payload.

## Scores

### Property Health

Overall score combining Passport completeness, readiness, confidence, and inverse risk.

### Property Confidence Index

Measures data completeness across building addresses, asset condition records, and visible/Passport document metadata.

### Property Risk

Measures risk pressure from open deficiencies, critical/high deficiencies, overdue work orders, expired documents, and poor/critical asset conditions.

### Property Readiness

Measures whether the property has related buildings, assets, documents, shared infrastructure, and a minimum Passport completeness threshold.

### Property Passport

Measures Passport record completeness across property buildings and shared infrastructure.

## Frontend

The property detail page now includes a Property Intelligence panel with:

- Health / Confidence / Risk / Readiness / Passport score cards
- Building intelligence table
- Readiness checklist
- Capital and deficiency summary
- Executive Review placeholder

## Executive Review Placeholder

M7B includes a placeholder object for executive review status and messaging. It does not generate reports, PDFs, signatures, or approvals.

## Known Limitations

- Scores are computed live and are not stored historically.
- Capital exposure depends on populated asset replacement values.
- Deficiency and work-order summaries depend on future implementation of those operational modules.
- Property-level assets and documents are not first-class records yet; shared infrastructure remains represented as a building-like record.
- No PDF, email, CRM, AI, or approval workflow is included.

## Future Enhancements

- Add `property_intelligence_snapshots` for trend history.
- Add configurable score rules.
- Add property-level assets/documents.
- Add executive review generation.
- Add capital planning workflows.
- Add trend charts and risk drill-down pages.
