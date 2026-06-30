# Building Registry Frontend/Backend Integration

FMS Phase 6 connects the frontend Building Registry to the Phase 5 backend APIs.

## Scope

- Buildings list
- Add building form
- Building detail/profile page
- Building contacts
- Organization selection for building creation and filtering
- API client functions
- Loading, empty, and error states

## API Coverage

- `GET /api/v1/organizations`
- `GET /api/v1/buildings`
- `POST /api/v1/buildings`
- `GET /api/v1/buildings/{building_id}`
- `PATCH /api/v1/buildings/{building_id}`
- `GET /api/v1/buildings/{building_id}/contacts`
- `POST /api/v1/buildings/{building_id}/contacts`
- `PATCH /api/v1/building-contacts/{contact_id}`
- `DELETE /api/v1/building-contacts/{contact_id}`

## Out of Scope

- Inspections
- Deficiencies
- Certificates
- Reports
- Memberships
- Document uploads
- Asset management
