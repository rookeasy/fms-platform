# FMS-0023 Reference Portfolio

The FMS-0023 Reference Portfolio seeds local development with representative Fuzion Fire portfolio data for internal knowledge, product demonstrations, training, and future Building Protection Passport workflows.

## What the Script Creates

- Reuses or creates the `Fuzion Fire Inc.` organization.
- Reuses or creates 9 Fuzion completed or active reference building profiles:
  - Linhaven Long-Term Care
  - Gilmore Lodge LTC
  - SOHO Phase 1
  - SOHO Phase 2
  - Montebello Condominiums
  - Marbella Condominiums
  - Parkway Lofts
  - Gates of Thornhill Building C
  - Darling Ingredients
- Adds 3 representative placeholder contacts for each building: property manager, site contact, and AHJ/fire prevention.
- Adds 3 to 6 representative fire protection assets for each building.
- Adds 5 document metadata records for each building.
- Marks selected document metadata as Passport Records and Client Visible.
- Adds notes on each building explaining the internal demonstration or training use case.

The script is idempotent. It looks up existing records by building name or address before inserting and does not overwrite fields on reused records, which protects real local data and avoids duplicate Building records during future seed runs.

## How to Run

```powershell
cd C:\Users\Adam\Documents\Projects\fms-platform\backend
.\.venv\Scripts\Activate.ps1
python -m scripts.seed_reference_portfolio
```

## How to Verify

Open:

- http://localhost:8000/api/v1/buildings
- http://localhost:3000/buildings

Run the script a second time and confirm the printed summary reports reused records rather than creating duplicates.

## Cleanup Removed Placeholder Records

Earlier local demo databases may contain placeholder reference buildings that are no longer part of the Fuzion reference portfolio:

- 2700 Aquitaine Avenue
- 5500 North Service Road
- CS Viamonde Elementary School
- Griffin Way Industrial
- Niagara Falls CES
- Prologis DC1 Halton Hills
- Waterloo Avenue Public School

To safely remove only those placeholder records from a local database, run:

```powershell
cd C:\Users\Adam\Documents\Projects\fms-platform\backend
.\.venv\Scripts\Activate.ps1
python -m scripts.seed_reference_portfolio --cleanup-placeholders
```

The cleanup command is scoped to the `Fuzion Fire Inc.` organization, the removed placeholder building names, and seed-like markers such as reference portfolio document storage keys, FMS-0023 asset tags, or reference notes. It soft-deletes matching placeholder buildings and their seeded contacts, assets, and document metadata. It does not target Linhaven Long-Term Care or SOHO Phase I / Building A.

## Cleanup Duplicate Linhaven or SOHO Records

If local seed history created duplicate Linhaven or SOHO Building A records, run:

```powershell
cd C:\Users\Adam\Documents\Projects\fms-platform\backend
.\.venv\Scripts\Activate.ps1
python -m scripts.seed_reference_portfolio --cleanup-duplicates
```

The duplicate cleanup command only evaluates:

- Linhaven records matching `Linhaven LTC`, `Linhaven Long-Term Care`, or `403 Ontario Street`
- SOHO Building A records matching `SOHO Phase I / Building A`, close variants of that name, or `505-517 Highland Road West`

For each group, it keeps the oldest Building Protection Passport record by lowest BPID first, then earliest created record. It soft-deletes only the duplicate building records and their child contacts, assets, and document metadata. It does not target SOHO Phase 1 at Grimsby or any non-matching SOHO portfolio building.

## Known Limitations

- Addresses and contact details are representative where exact data is unavailable.
- Document rows are metadata only; the script does not create real uploaded files.
- Existing matching rows are reused without being updated, so pre-existing records with different visibility flags are left unchanged.
- Placeholder cleanup is conservative and only soft-deletes records that match the removed placeholder names under the Fuzion Fire reference organization.
- Duplicate cleanup is limited to Linhaven and SOHO Building A match groups and keeps the lowest BPID or earliest created building.
- The seed does not create inspections, deficiencies, work orders, reports, certificates, memberships, AI workflows, or auth changes.
- The portfolio is intended for local development and demonstration use, not production import.

## Internal Operations and Sales Demonstrations

The portfolio gives Fuzion Fire a repeatable set of completed or active reference buildings across long-term care, condominium, residential, and industrial contexts. It supports internal onboarding by showing how building profiles, assets, contacts, and Passport document metadata relate to one another.

For sales demonstrations, the seeded buildings make it possible to show portfolio navigation, client-visible records, Passport filtering, and future Building Protection Passport workflows without using customer data.
