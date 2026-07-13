# Intelligent Document Upload and Asset Extraction

## Purpose

This MVP lets FOP users upload real project documents, classify them, control Passport/client visibility, and review AI-assisted asset suggestions before any authoritative asset records are created.

The primary production example is SOHO Phase I closeout evidence: drawings, certificates, compliance letters, as-builts, warranties, O&M manuals, and related handover documents.

## Architecture

- Files are stored in local development storage through the existing local storage adapter.
- Document metadata remains in the existing `documents` table with added classification and extraction fields.
- Asset suggestions are stored in `document_asset_suggestions`.
- AI-style extraction is review-first. The current MVP uses deterministic filename and metadata rules when no external AI provider is configured.
- Approved suggestions create or reuse `assets`; unapproved suggestions never create authoritative records.

## Upload Workflow

1. User opens a building document workspace.
2. User selects a file and enters title, document type, evidence category, revision, issue date, status, visibility, and notes.
3. Backend validates file type, upload size, tenant scope, and safe storage path.
4. File is saved under the configured upload root with a collision-safe storage key.
5. Metadata is saved to `documents`.
6. Extraction runs and suggestions are created with `review_required` status when applicable.

## Classification Workflow

Documents can be classified by:

- `document_type`
- `evidence_category`
- `drawing_number`
- `revision`
- `issue_date`
- `status`
- Passport Record flag
- Client Visible flag
- Internal Only flag

Closeout scoring continues to use existing document type, title, description, Passport, and client visibility logic. Evidence category is now available for richer future closeout matching.

## AI Review Workflow

Extraction statuses:

- pending
- processing
- review_required
- approved
- rejected
- failed

The current extraction implementation is deterministic and labeled `rule_based`. It reads filename/title/description metadata and suggests fire protection assets when known system keywords are present.

## Asset Approval Rules

- Suggestions are reviewable before asset creation.
- Approve creates or reuses an asset.
- Reject marks the suggestion rejected and creates no asset.
- Approve All approves every pending suggestion for a document.
- Duplicate prevention matches existing assets by building, asset type, normalized name, and location.
- Approved assets are linked back to the source document through `source_document_id`.

## Closeout Score Interaction

Document upload and classification can affect closeout completion when the uploaded document matches existing closeout score categories or visibility requirements.

Uploading a document does not directly change the Building Health Index by itself. Health and intelligence scores remain driven by the existing scoring services and their broader building, asset, document, deficiency, work order, inspection, and health inputs.

## File Storage Configuration

Environment variables:

```powershell
FOP_UPLOAD_ROOT=storage/documents
FOP_MAX_UPLOAD_MB=50
FOP_ALLOWED_UPLOAD_TYPES=application/pdf,text/plain,text/csv,image/png,image/jpeg
```

The legacy variables remain compatible:

```powershell
LOCAL_STORAGE_ROOT=storage/documents
MAX_UPLOAD_SIZE_BYTES=50000000
```

Local uploads should remain under ignored local storage such as `backend/storage/`, not Git-tracked folders.

## Local Development Setup

Backend:

```powershell
cd C:\Users\Adam\Documents\Projects\fms-platform\backend
.\.venv\Scripts\Activate.ps1
alembic upgrade head
uvicorn app.main:app --reload
```

Frontend:

```powershell
cd C:\Users\Adam\Documents\Projects\fms-platform\frontend
npm run dev
```

## Security Limitations

- Local storage is for development only.
- File type validation is MIME-based and should be strengthened with content inspection for production.
- No OCR at scale is included.
- No production auth/permissions are included beyond the current placeholder role system.
- External AI providers are not configured and no secrets are hardcoded.

## Future Production Storage Roadmap

- Move file storage to cloud object storage.
- Add signed URLs and stronger access controls.
- Add virus/malware scanning.
- Add OCR and drawing text extraction.
- Add structured extraction provider adapters.
- Add reviewer assignment, audit history, and approval comments.
- Add client-facing Passport package generation after reviewed records are ready.
