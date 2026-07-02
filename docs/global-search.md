# M7A Global Search

## Purpose

Global Search gives FOP/FMS users one search box for finding organizations, properties, campuses, buildings, BPIDs, addresses, municipalities, provinces, documents, assets, and Building Protection Passports.

## Searchable Entities

The MVP searches:

- Organizations
- Properties
- Campuses
- Buildings
- Assets
- Documents
- Building Protection Passports

Search fields include names, titles, BPIDs, record IDs, address lines, city/municipality, province/state, country, document type, filenames, asset tags, and common asset metadata.

## API Route

```http
GET /api/v1/search?q={query}
GET /api/v1/search?q=soho&type=building
```

Optional query parameters:

- `q`: search text. Empty queries return `[]`.
- `type`: one of `organization`, `property`, `campus`, `building`, `asset`, `document`, `passport`.
- `limit`: defaults to `25`, maximum `100`.

## Result Schema

```json
{
  "id": "string",
  "type": "organization | property | campus | building | asset | document | passport",
  "title": "string",
  "subtitle": "string",
  "matched_field": "string",
  "url": "string"
}
```

The route returns:

```json
{
  "data": []
}
```

## Matching Priority

Exact identifier matches are ranked first:

- BPID
- BUP ID / building-like identifiers when available
- Property ID
- Building ID

Then exact name/title matches, identifier contains matches, prefix matches, and general partial matches.

## Frontend Behavior

The global search box appears in the top bar.

Behavior:

- Searches as the user types with debounce.
- Groups results by type.
- Shows result type badge, title, subtitle, and loading/no-results states.
- `Enter` opens the first result.
- `Esc` closes the search panel.
- Clicking a result navigates to the result URL.

Navigation rules:

- Organizations link to `/organizations/{id}`.
- Properties link to `/properties/{id}`.
- Buildings link to `/buildings/{id}`.
- Passports link to `/buildings/{id}/passport`.
- Assets and documents link to the parent building because dedicated asset/document detail pages are not yet implemented.
- Campuses link to their parent property when available.

## Known Limitations

- The MVP uses SQL `ILIKE` matching rather than a full-text search index.
- Passport results are derived from matching building records.
- BUP ID is supported only where an existing identifier field can represent it; there is no dedicated BUP ID column yet.
- Organization detail pages are not currently implemented in the frontend, though the search result URL is reserved.
- Assets and documents do not have dedicated detail pages yet.

## Future Enhancements

- Add PostgreSQL full-text search or trigram indexes.
- Add dedicated BUP ID fields if FOP requires a separate property/building identifier standard.
- Add search analytics and saved recent searches.
- Add keyboard arrow navigation through results.
- Add richer permission-aware snippets and highlighted matched text.
- Add dedicated detail pages for organizations, assets, documents, and campuses.
