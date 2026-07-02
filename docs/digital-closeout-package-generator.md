# FMS-0027 Digital Closeout Package Generator

FMS-0027 introduces the MVP Digital Closeout Package Generator for a building, starting with SOHO Phase I / Building A.

The MVP uses existing building, asset, and document metadata models. It does not add database schema, file storage, PDF generation, authentication, signatures, payments, CRM integration, external storage, email, or QR code workflows.

## Purpose

The purpose of this MVP is to prove that FMS can organize closeout evidence for a building into a structured digital handover view.

The closeout package groups uploaded-document metadata into sections that support owner handover, Building Protection Passport readiness, Fuzion Fire Service ITM transition, and FMS membership conversion.

## What Was Added

- A SOHO closeout seed script: `backend/scripts/seed_soho_closeout_package.py`
- A closeout package frontend route: `/buildings/[buildingId]/closeout`
- A SOHO-friendly route target: `/buildings/soho-phase-i-building-a/closeout`
- A closeout package page that loads existing building, asset, and document APIs.
- Document grouping by closeout section using existing document descriptions.
- Readiness display for `Ready for Handover` or `Missing Items`.

## Closeout Sections

The frontend MVP organizes evidence into these sections:

1. Building Protection Passport
2. P.Eng. Compliance Package
3. NFPA Contractor Compliance Package
4. Material & Test Certificates
5. Drawing Register
6. As-Built Drawings
7. Asset Register
8. Warranty Package
9. Product Data / O&M Manuals
10. Owner / Property Manager Handover
11. Fuzion Fire Service ITM Transition
12. FMS Membership Invitation

## SOHO Seed Data

The seed script creates or reuses:

- Organization: `Fuzion Fire Inc.`
- Building: `SOHO Phase I / Building A`
- Representative building contacts
- Representative fire protection assets
- Closeout document metadata

The seed uses metadata only. It does not store actual PDF files.

Certificate metadata records include:

- BLD A Ground Floor Wet
- BLD A 2nd Floor Wet
- BLD A 3rd Floor Wet
- BLD A 4th Floor Wet
- BLD A 5th Floor Wet
- BLD A 6th Floor Wet
- BLD A 7th Floor Wet
- BLD A 8th Floor Wet
- BLD A MPH Wet
- BLD A Garbage Chute
- BLD B Garbage Chute
- BLD B MPH Wet
- Dry Ground Floor Amenity
- Dry P1 East
- Dry P1 West
- Dry P1 Standpipe
- Wet Combined Sprinkler / Standpipe

Each certificate record includes metadata for:

- Document title
- Document type
- System/location
- Property name: SOHO
- Address: 505-517 Highland Road West, Stoney Creek, Ontario
- Contractor: Fuzion Fire Inc.
- Approving authority: Stoney Creek Building Department
- Evidence purpose
- Client visible: true
- Passport record: true

## How to Run

```powershell
cd C:\Users\Adam\Documents\Projects\fms-platform\backend
.\.venv\Scripts\Activate.ps1
python -m scripts.seed_soho_closeout_package
```

The script is idempotent. It checks for existing matching records before inserting and prints created/reused counts.

## How to Verify

Open:

- http://localhost:8000/api/v1/buildings
- http://localhost:3000/buildings
- http://localhost:3000/buildings/soho-phase-i-building-a/closeout

The closeout page should show the SOHO building name, completion status, section checklist, evidence list grouped by section, Client Visible indicators, Passport Record indicators, and a `Ready for Handover` or `Missing Items` state.

## MVP Limitations

- Closeout sections are represented in document metadata descriptions because no dedicated closeout package tables exist yet.
- The seed creates metadata only and does not upload or store PDF files.
- The frontend route resolves `soho-phase-i-building-a` by matching the slugified building name from the building list.
- The view is read-only.
- There is no PDF generation.
- There is no file upload storage added for closeout packages.
- There is no authentication, email sending, CRM integration, signatures, payments, external storage, or QR code workflow.
- The current schema cannot represent full closeout package status, section ownership, formal approvals, signatures, or handover meeting completion as first-class records.

## Future Implementation Notes

A future phase should add dedicated closeout package data models, including package status, closeout sections, evidence records, approvals, handover meetings, owner acknowledgements, generated package exports, and lifecycle conversion tracking.

Once those records exist, the frontend can stop parsing section labels from document descriptions and can show richer workflow status, missing-item ownership, review history, and client handover progress.
