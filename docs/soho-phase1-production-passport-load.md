# SOHO Phase I Production Passport Load

This phase converts SOHO Phase I into a controlled production Passport readiness workspace without issuing final Passport PDFs or approving Protected State.

## Purpose

SOHO Phase I is represented as one Protected Property with separate readiness records for:

- Building A
- Building B
- Shared Fire Protection Infrastructure
- Common Parking Garage

The loader reuses existing FOP records where possible, creates only missing canonical records when write mode is enabled, and preserves source uncertainty for review.

## Loader

Run from the backend:

```powershell
cd C:\Users\Adam\Documents\Projects\fms-platform\backend
.\.venv\Scripts\Activate.ps1
alembic upgrade head
python -m scripts.load_soho_phase1_passport
```

Useful modes:

```powershell
python -m scripts.load_soho_phase1_passport --report-only
python -m scripts.load_soho_phase1_passport --dry-run
python -m scripts.load_soho_phase1_passport --cleanup-duplicates
python -m scripts.load_soho_phase1_passport --reclassify-existing
```

Optional intake folders:

```powershell
python -m scripts.load_soho_phase1_passport `
  --building-a-path "C:\path\to\building-a" `
  --building-b-path "C:\path\to\building-b" `
  --shared-path "C:\path\to\shared-fire-protection" `
  --property-path "C:\path\to\property-common"
```

Supported file types are PDF, Word, Excel, CSV, common image formats, and text files. The loader registers metadata for supported files and marks uncertain classification as review required.

## Idempotency Rules

- Reuse the `fuzion-tech` organization.
- Reuse the `SOHO Phase I` property when present.
- Reuse canonical SOHO records by SOHO role marker, code, BPID, or exact name.
- Never hard-delete records.
- Duplicate cleanup is opt-in through `--cleanup-duplicates`.
- Existing Passport, handover, and evidence data are preserved unless a conservative enrichment is explicitly requested.

## Readiness Workspace

The frontend readiness route is:

```text
http://localhost:3000/properties/<soho-property-id>/passport-readiness
```

The page shows:

- property overview
- Building A library readiness
- Building B library readiness
- shared infrastructure readiness
- common parking garage readiness
- closeout score
- missing evidence
- Passport status
- protected-state status
- handover controls
- next action
- links to evidence and Passport pages

## Readiness States

- Not Ready
- Review Required
- Ready for Passport
- Ready for Protected-State Review

Protected State approval remains controlled by the existing backend approval flow. The loader and readiness page do not approve Protected State and do not make the Halo eligible.

## Current Limitations

- Final Passport PDFs are not generated in this phase.
- Missing project facts are not inferred.
- Owner/property-manager recipients, portal access, delivery dates, and ITM transition details remain review fields unless already present in FOP data.
- Folder intake stores local metadata and classification status; it does not copy files to durable object storage.
- System-generated SOHO BPIDs are used only when a canonical record must be created and no existing BPID is available.
