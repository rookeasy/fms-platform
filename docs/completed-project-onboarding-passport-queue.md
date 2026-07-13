# Completed Project Onboarding Passport Queue

This phase converts the canonical Fuzion active/completed project portfolio into a controlled Passport onboarding queue.

The queue is sourced from `backend/scripts/seed_fuzion_projects.py`. It does not invent missing project data, does not generate final PDFs, and does not replace existing building, closeout, document, or Passport routes.

## Scope

- Classify canonical Fuzion projects as `active`, `completed`, `service-only`, `design-only`, or `archived`.
- Mark only completed prime contracts as Passport Eligible by default.
- Add lightweight Building Protection Passport lifecycle metadata to existing building records.
- Provide an idempotent onboarding script for completed Fuzion projects.
- Provide a live frontend queue at `/passports/onboarding`.

## Passport Lifecycle Statuses

- Not Started
- Building Registered
- Documents Imported
- Assets Verified
- Closeout Incomplete
- Ready for Passport
- Passport Issued
- Passport Delivered

## Building Metadata Added

- `project_classification`
- `passport_eligible`
- `passport_status`
- `passport_issue_date`
- `passport_version`
- `client_handover_status`

## Onboarding Script

Run from the backend folder:

```powershell
cd C:\Users\Adam\Documents\Projects\fms-platform\backend
.\.venv\Scripts\Activate.ps1
alembic upgrade head
python -m scripts.onboard_completed_fuzion_projects
```

The script reuses existing buildings by organization/code or Passport number, creates missing canonical Fuzion buildings through the existing seed upsert path, and prints created/reused/updated/passport eligible/skipped counts.

## Queue

Open:

- `http://localhost:3000/passports/onboarding`
- `http://localhost:3000/buildings`
- `http://localhost:3000/properties`

The queue shows project, property, building, completion status, closeout score, missing items, Passport status, next action, and links to the related building closeout and Passport pages.

## Known Limitations

- The current phase stores Passport lifecycle metadata on `buildings`; there is not yet a dedicated Passport lifecycle table.
- The queue is limited to canonical Fuzion project records marked with `source=fuzion_active_completed_projects`.
- Service-only and design-only classifications are supported as metadata values, but the current canonical Fuzion list only contains active and completed project statuses.
- Final Passport PDFs are intentionally not generated in this phase.
- Missing closeout evidence is reported from existing closeout scoring rules; the script does not create document records for unavailable evidence.
