# FMS-0023 Reference Portfolio

The FMS-0023 Reference Portfolio seeds local development with representative Fuzion Fire portfolio data for internal knowledge, product demonstrations, training, and future Building Protection Passport workflows.

## What the Script Creates

- Reuses or creates the `Fuzion Fire Inc.` organization.
- Reuses or creates 16 reference building profiles:
  - Linhaven Long-Term Care
  - Gilmore Lodge LTC
  - SOHO Phase 1
  - SOHO Phase 2
  - Montebello Condominiums
  - Marbella Condominiums
  - Parkway Lofts
  - Gates of Thornhill Building C
  - Waterloo Avenue Public School
  - Niagara Falls CES
  - CS Viamonde Elementary School
  - Griffin Way Industrial
  - Prologis DC1 Halton Hills
  - Darling Ingredients
  - 2700 Aquitaine Avenue
  - 5500 North Service Road
- Adds 3 representative placeholder contacts for each building: property manager, site contact, and AHJ/fire prevention.
- Adds 3 to 6 representative fire protection assets for each building.
- Adds 5 document metadata records for each building.
- Marks selected document metadata as Passport Records and Client Visible.
- Adds notes on each building explaining the internal demonstration or training use case.

The script is idempotent. It looks up existing records before inserting and does not overwrite fields on reused records, which protects real local data.

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

## Known Limitations

- Addresses and contact details are representative where exact data is unavailable.
- Document rows are metadata only; the script does not create real uploaded files.
- Existing matching rows are reused without being updated, so pre-existing records with different visibility flags are left unchanged.
- The seed does not create inspections, deficiencies, work orders, reports, certificates, memberships, AI workflows, or auth changes.
- The portfolio is intended for local development and demonstration use, not production import.

## Internal Operations and Sales Demonstrations

The portfolio gives Fuzion Fire a broad, repeatable set of buildings across long-term care, condominium, school, industrial, warehouse, residential, and commercial office contexts. It supports internal onboarding by showing how building profiles, assets, contacts, and Passport document metadata relate to one another.

For sales demonstrations, the seeded buildings make it possible to show portfolio navigation, client-visible records, Passport filtering, and future Building Protection Passport workflows without using customer data.
