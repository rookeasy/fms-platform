# Building Protection Passport Foundation

Phase 7 introduces the first real Building Protection Passport functionality:
assets, document metadata, local document storage, secure download routes, document versioning, and a live Passport summary.

## Backend

- Asset CRUD is implemented through `AssetService`.
- Document metadata, multipart upload, secure download, soft delete, and versioning are implemented through `DocumentService`.
- Passport summary composition is implemented through `PassportService`.
- Local file storage is isolated behind a storage adapter so future Azure Blob or S3 providers can replace the MVP local adapter.
- Asset creation and document upload write audit log records.

## Frontend

- Building profiles now include Overview, Assets, Documents, and Contacts tabs.
- The Assets tab supports list, add, edit, soft delete, and detail review.
- The Documents tab supports upload, filters, preview metadata, download links, and version history.
- The Building Protection Passport page now uses the backend Passport API instead of mock data.

## Limitations

- Authentication and authorization remain MVP placeholders.
- Local file storage is for development only.
- Health Score and Membership are read-only placeholders until later phases.
- Backend tests require dependencies from `backend/requirements.txt`, including `python-multipart`.
