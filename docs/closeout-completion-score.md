# Closeout Completion Score

## Purpose

FMS-0028 adds an MVP readiness score for Digital Closeout Packages. The score helps Fuzion see whether a building or property is ready for handover, billing support, ITM transition, and FMS membership conversion.

## Scoring Categories

The building score uses 12 required checklist categories:

1. Building Protection Passport
2. Drawing Register
3. As-Built Drawings
4. P.Eng. Compliance Package
5. NFPA Contractor Compliance Package
6. Material & Test Certificates
7. Asset Register
8. Warranty Package
9. Product Data / O&M Manuals
10. Owner / Property Manager Handover
11. Fuzion Fire Service ITM Transition
12. FMS Membership Invitation

Each completed category contributes one required item. Completion percentage is:

`completed_items / total_required_items * 100`

## Required Evidence Logic

The MVP calculator is read-only and uses existing records:

- Documents are matched by `document_type`, title, and description.
- Seeded SOHO closeout records are matched through `Closeout section: <category>` descriptions.
- Building Protection Passport requires Passport-visible evidence.
- Drawing Register, As-Built Drawings, P.Eng., NFPA, Material & Test Certificates, Warranty, Product Data / O&M, ITM Transition, and FMS Membership Invitation can be satisfied by matching document evidence.
- Asset Register can be satisfied by registered building assets or matching document evidence.
- Owner / Property Manager Handover can be satisfied by client-visible handover evidence or existing owner/property manager contact data.
- Organization membership can satisfy FMS Membership Invitation when an active membership exists, but document evidence also counts for MVP demo data.

## Ready For Handover Rules

A building is ready for handover only when:

- All 12 required categories are complete.
- No scoring warnings remain.

Warnings are returned when required evidence is missing, when no documents exist, when no assets are registered, or when no owner/property manager handover contact is available.

## Property Rollup

When properties are available, the MVP property score aggregates assigned child buildings:

- `completed_items` is the sum of building completed items.
- `total_required_items` is the sum of building required items.
- `completion_percentage` is calculated from the aggregate totals.
- `ready_for_handover` is true only when every assigned building is ready.
- Section status shows whether every assigned building completed that category.

Shared infrastructure is not modeled separately in this MVP. It is included only when represented as assigned buildings or building assets/documents.

## SOHO Example

The seeded SOHO closeout package includes documents with closeout section labels for the main evidence categories, plus registered assets and handover contact fields. With the current seed set, the SOHO Building A closeout page should show meaningful checklist completion. If a local seed omits Warranty, Product Data / O&M, ITM Transition, or FMS Membership Invitation evidence, those categories remain missing until matching records are added.

## MVP Limitations

- No new workflow tables are introduced.
- Evidence matching is heuristic and based on current document metadata.
- No PDF generation, signatures, email, QR codes, payments, CRM, auth changes, or external integrations are included.
- Property scoring is a simple child-building rollup.
- Readiness does not yet distinguish required vs optional evidence by contract type, jurisdiction, project phase, or customer-specific rule set.

## Future Enhancements

- Configurable closeout templates by project type and jurisdiction.
- Explicit evidence requirements with reviewer assignment and approvals.
- Shared infrastructure closeout sections for campus/property-level systems.
- Customer-facing handover acceptance workflow.
- Billing readiness and FMS conversion workflow integration.
- Closeout export package generation after readiness is reached.
