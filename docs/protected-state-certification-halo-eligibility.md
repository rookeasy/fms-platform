# Protected-State Certification & Halo Eligibility

Protected State is the auditable milestone that allows a building to display the Living F halo.

The halo is not decoration. It means FOP has an approved backend certification record showing that the building has enough evidence to be treated as protected.

## Purpose

This phase moves halo eligibility from frontend visual inference to a backend-backed certification workflow.

The frontend may show the halo only when:

- the protected-state certification status is `approved`
- `halo_eligible` is true
- the certification is not suspended or revoked

Passport progress, closeout progress, and frontend percentages do not activate the halo.

## Protected-State Meaning

Protected State means the building has passed the MVP evidence checks for:

- issued or delivered Building Protection Passport
- complete closeout readiness
- required compliance evidence
- registered core fire-protection assets
- owner or property manager handover
- ITM transition evidence
- no unresolved critical/high deficiency blockers

## Eligibility Criteria

The MVP evaluator uses current available data only.

Criteria are recorded as `passed`, `failed`, or `unknown`.

Unknown criteria block approval. FOP does not fabricate missing facts.

## Approval Requirement

Eligibility alone does not activate the halo.

A reviewer must explicitly approve Protected State through the backend action:

`POST /api/v1/buildings/{building_id}/protected-state/approve`

Approval records the reviewer placeholder, approval timestamp, reason, notes, and criteria snapshot.

## Suspended And Revoked

Suspended and revoked certifications never show the halo.

Suspension is for temporary exceptions.

Revocation is for loss of protected-state confidence.

Both actions preserve timestamp, reason, notes, and the prior criteria snapshot.

## Audit Expectations

Each evaluation and reviewer action writes an audit log entry.

The certification record preserves:

- evaluation version
- evaluated timestamp and reviewer placeholder
- approved/suspended/revoked timestamps
- reason and notes
- criteria snapshot

## Frontend Integration

The frontend consumes:

`GET /api/v1/buildings/{building_id}/protected-state`

Relevant pages render no operational halo if the endpoint is unavailable.

Building Profile shows the reviewer workflow.

Building Protection Passport shows certification status and approval metadata.

Passport Onboarding shows Protected State status and counts approved protected records.

## Mission Control Counting Rule

Mission Control counts Buildings Under Protection™ from approved protected-state certifications with `halo_eligible = true`.

It does not count visual progress, Passport-ready records, or issued Passports that have not been approved for Protected State.

## Seed And Backfill

Run the idempotent evaluator:

```powershell
cd C:\Users\Adam\Documents\Projects\fms-platform\backend
.\.venv\Scripts\Activate.ps1
python -m scripts.evaluate_protected_state
```

The script creates or reuses certification records and never auto-approves a building.

Optional:

```powershell
python -m scripts.evaluate_protected_state --building-id <building-id>
python -m scripts.evaluate_protected_state --dry-run
```

## Known MVP Limitations

- This is not a legal certification system.
- Production RBAC, MFA, signatures, public registries, insurer workflows, and AHJ integrations are not included.
- Handover completeness relies on current lightweight building metadata.
- Jurisdiction-specific asset requirements are not modeled yet.
- Non-critical deficiency acceptance is not yet a structured approval workflow.

## Future Governance

Future phases should add role-governed certification authority, explicit waivers, jurisdictional criteria, owner acknowledgements, cryptographic signatures, public verification, and insurer/AHJ integration.
