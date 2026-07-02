from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy import String, or_, select
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
from app.models import Asset, Building, Campus, Document, Organization, Property
from app.services.tenant import ensure_organization_access


SEARCH_TYPES = {"organization", "property", "campus", "building", "asset", "document", "passport"}
IDENTIFIER_FIELDS = {"id", "bpid", "bup_id", "property_id", "building_id"}
TYPE_PRIORITY = {
    "building": 0,
    "property": 1,
    "passport": 2,
    "campus": 3,
    "organization": 4,
    "asset": 5,
    "document": 6,
}


@dataclass
class SearchHit:
    id: str
    type: str
    title: str
    subtitle: str
    matched_field: str
    url: str
    rank: int

    def as_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "type": self.type,
            "title": self.title,
            "subtitle": self.subtitle,
            "matched_field": self.matched_field,
            "url": self.url,
        }


class SearchService:
    def search(self, db: Session, current_user: CurrentUser, query: str | None, result_type: str | None = None, limit: int = 25) -> list[dict[str, str]]:
        term = (query or "").strip()
        if not term:
            return []
        if result_type and result_type not in SEARCH_TYPES:
            return []

        organization_id = self._scoped_organization_id(current_user)
        hits: list[SearchHit] = []

        if result_type in {None, "organization"}:
            hits.extend(self._search_organizations(db, current_user, term, organization_id))
        if result_type in {None, "property"}:
            hits.extend(self._search_properties(db, current_user, term, organization_id))
        if result_type in {None, "campus"}:
            hits.extend(self._search_campuses(db, current_user, term, organization_id))
        if result_type in {None, "building"}:
            hits.extend(self._search_buildings(db, current_user, term, organization_id))
        if result_type in {None, "asset"}:
            hits.extend(self._search_assets(db, current_user, term, organization_id))
        if result_type in {None, "document"}:
            hits.extend(self._search_documents(db, current_user, term, organization_id))
        if result_type in {None, "passport"}:
            hits.extend(self._search_passports(db, current_user, term, organization_id))

        unique_hits = {}
        for hit in hits:
            key = (hit.type, hit.id, hit.url, hit.matched_field)
            existing = unique_hits.get(key)
            if existing is None or hit.rank < existing.rank:
                unique_hits[key] = hit

        ordered = sorted(unique_hits.values(), key=lambda hit: (hit.rank, TYPE_PRIORITY.get(hit.type, 99), hit.title.lower()))
        return [hit.as_dict() for hit in ordered[:limit]]

    def _scoped_organization_id(self, current_user: CurrentUser) -> UUID | None:
        if current_user.is_platform_admin or not current_user.current_organization_id:
            return None
        return UUID(current_user.current_organization_id)

    def _rank(self, query: str, matched_field: str, value: Any) -> int:
        candidate = str(value or "").strip()
        query_lower = query.lower()
        candidate_lower = candidate.lower()
        if matched_field in IDENTIFIER_FIELDS and candidate_lower == query_lower:
            return 0
        if candidate_lower == query_lower:
            return 1
        if matched_field in IDENTIFIER_FIELDS and query_lower in candidate_lower:
            return 4
        if candidate_lower.startswith(query_lower):
            return 3
        return 5

    def _first_match(self, query: str, fields: list[tuple[str, Any]]) -> tuple[str, int]:
        best_field = "keyword"
        best_rank = 9
        for field, value in fields:
            value_text = str(value or "")
            if query.lower() in value_text.lower():
                rank = self._rank(query, field, value)
                if rank < best_rank:
                    best_field = field
                    best_rank = rank
        return best_field, best_rank

    def _address(self, *parts: Any) -> str:
        return ", ".join(str(part) for part in parts if part)

    def _search_organizations(self, db: Session, current_user: CurrentUser, query: str, organization_id: UUID | None) -> list[SearchHit]:
        criteria = [Organization.deleted_at.is_(None)]
        if organization_id:
            ensure_organization_access(current_user, organization_id)
            criteria.append(Organization.id == organization_id)
        like = f"%{query}%"
        rows = db.scalars(
            select(Organization)
            .where(
                *criteria,
                or_(
                    Organization.name.ilike(like),
                    Organization.id.cast(String).ilike(like),
                    Organization.legal_name.ilike(like),
                    Organization.email.ilike(like),
                    Organization.city.ilike(like),
                    Organization.province_state.ilike(like),
                    Organization.country.ilike(like),
                ),
            )
            .limit(50)
        ).all()
        hits = []
        for row in rows:
            field, rank = self._first_match(
                query,
                [
                    ("id", row.id),
                    ("name", row.name),
                    ("legal_name", row.legal_name),
                    ("email", row.email),
                    ("city", row.city),
                    ("province_state", row.province_state),
                    ("country", row.country),
                ],
            )
            hits.append(SearchHit(str(row.id), "organization", row.name, self._address(row.city, row.province_state, row.country), field, f"/organizations/{row.id}", rank))
        return hits

    def _search_properties(self, db: Session, current_user: CurrentUser, query: str, organization_id: UUID | None) -> list[SearchHit]:
        criteria = [Property.deleted_at.is_(None)]
        if organization_id:
            ensure_organization_access(current_user, organization_id)
            criteria.append(Property.organization_id == organization_id)
        like = f"%{query}%"
        rows = db.scalars(
            select(Property)
            .where(
                *criteria,
                or_(
                    Property.id.cast(String).ilike(like),
                    Property.name.ilike(like),
                    Property.address_line_1.ilike(like),
                    Property.city.ilike(like),
                    Property.province_state.ilike(like),
                    Property.country.ilike(like),
                    Property.property_type.ilike(like),
                ),
            )
            .limit(50)
        ).all()
        hits = []
        for row in rows:
            field, rank = self._first_match(
                query,
                [
                    ("property_id", row.id),
                    ("name", row.name),
                    ("address_line_1", row.address_line_1),
                    ("city", row.city),
                    ("province_state", row.province_state),
                    ("country", row.country),
                    ("property_type", row.property_type),
                ],
            )
            hits.append(SearchHit(str(row.id), "property", row.name, self._address(row.address_line_1, row.city, row.province_state), field, f"/properties/{row.id}", rank))
        return hits

    def _search_campuses(self, db: Session, current_user: CurrentUser, query: str, organization_id: UUID | None) -> list[SearchHit]:
        criteria = [Campus.deleted_at.is_(None)]
        if organization_id:
            ensure_organization_access(current_user, organization_id)
            criteria.append(Campus.organization_id == organization_id)
        like = f"%{query}%"
        rows = db.scalars(
            select(Campus)
            .where(
                *criteria,
                or_(
                    Campus.id.cast(String).ilike(like),
                    Campus.name.ilike(like),
                    Campus.address_line_1.ilike(like),
                    Campus.city.ilike(like),
                    Campus.province_state.ilike(like),
                    Campus.country.ilike(like),
                    Campus.campus_type.ilike(like),
                ),
            )
            .limit(50)
        ).all()
        hits = []
        for row in rows:
            field, rank = self._first_match(query, [("id", row.id), ("name", row.name), ("address_line_1", row.address_line_1), ("city", row.city), ("province_state", row.province_state), ("country", row.country), ("campus_type", row.campus_type)])
            url = f"/properties/{row.property_id}" if row.property_id else "/properties"
            hits.append(SearchHit(str(row.id), "campus", row.name, self._address(row.address_line_1, row.city, row.province_state), field, url, rank))
        return hits

    def _search_buildings(self, db: Session, current_user: CurrentUser, query: str, organization_id: UUID | None) -> list[SearchHit]:
        criteria = [Building.deleted_at.is_(None)]
        if organization_id:
            ensure_organization_access(current_user, organization_id)
            criteria.append(Building.organization_id == organization_id)
        like = f"%{query}%"
        rows = db.scalars(
            select(Building)
            .where(
                *criteria,
                or_(
                    Building.id.cast(String).ilike(like),
                    Building.bpid.ilike(like),
                    Building.name.ilike(like),
                    Building.code.ilike(like),
                    Building.address_line_1.ilike(like),
                    Building.address_line1.ilike(like),
                    Building.city.ilike(like),
                    Building.province_state.ilike(like),
                    Building.region.ilike(like),
                    Building.country.ilike(like),
                    Building.building_type.ilike(like),
                ),
            )
            .limit(50)
        ).all()
        hits = []
        for row in rows:
            field, rank = self._first_match(query, [("building_id", row.id), ("bpid", row.bpid), ("name", row.name), ("bup_id", row.code), ("address_line_1", row.address_line_1 or row.address_line1), ("city", row.city), ("province_state", row.province_state or row.region), ("country", row.country), ("building_type", row.building_type)])
            subtitle = f"{row.bpid or 'No BPID'} - {self._address(row.address_line_1 or row.address_line1, row.city, row.province_state or row.region)}"
            hits.append(SearchHit(str(row.id), "building", row.name, subtitle, field, f"/buildings/{row.id}", rank))
        return hits

    def _search_assets(self, db: Session, current_user: CurrentUser, query: str, organization_id: UUID | None) -> list[SearchHit]:
        criteria = [Asset.deleted_at.is_(None)]
        if organization_id:
            ensure_organization_access(current_user, organization_id)
            criteria.append(Asset.organization_id == organization_id)
        like = f"%{query}%"
        rows = db.scalars(
            select(Asset)
            .where(
                *criteria,
                or_(
                    Asset.id.cast(String).ilike(like),
                    Asset.name.ilike(like),
                    Asset.tag.ilike(like),
                    Asset.asset_tag.ilike(like),
                    Asset.location_description.ilike(like),
                    Asset.manufacturer.ilike(like),
                    Asset.model.ilike(like),
                    Asset.serial_number.ilike(like),
                ),
            )
            .limit(50)
        ).all()
        hits = []
        for row in rows:
            field, rank = self._first_match(query, [("id", row.id), ("name", row.name), ("asset_tag", row.asset_tag or row.tag), ("location_description", row.location_description), ("manufacturer", row.manufacturer), ("model", row.model), ("serial_number", row.serial_number)])
            hits.append(SearchHit(str(row.id), "asset", row.name, row.location_description or row.asset_tag or row.tag or "Asset", field, f"/buildings/{row.building_id}", rank))
        return hits

    def _search_documents(self, db: Session, current_user: CurrentUser, query: str, organization_id: UUID | None) -> list[SearchHit]:
        criteria = [Document.deleted_at.is_(None)]
        if organization_id:
            ensure_organization_access(current_user, organization_id)
            criteria.append(Document.organization_id == organization_id)
        like = f"%{query}%"
        rows = db.scalars(
            select(Document)
            .where(
                *criteria,
                or_(
                    Document.id.cast(String).ilike(like),
                    Document.name.ilike(like),
                    Document.title.ilike(like),
                    Document.description.ilike(like),
                    Document.document_type.ilike(like),
                    Document.original_filename.ilike(like),
                    Document.storage_key.ilike(like),
                ),
            )
            .limit(50)
        ).all()
        hits = []
        for row in rows:
            title = row.title or row.name
            field, rank = self._first_match(query, [("id", row.id), ("title", title), ("description", row.description), ("document_type", row.document_type), ("original_filename", row.original_filename), ("storage_key", row.storage_key)])
            hits.append(SearchHit(str(row.id), "document", title, row.document_type, field, f"/buildings/{row.building_id}", rank))
        return hits

    def _search_passports(self, db: Session, current_user: CurrentUser, query: str, organization_id: UUID | None) -> list[SearchHit]:
        building_hits = self._search_buildings(db, current_user, query, organization_id)
        passport_hits = []
        for hit in building_hits:
            passport_hits.append(
                SearchHit(
                    hit.id,
                    "passport",
                    f"{hit.title} Passport",
                    hit.subtitle,
                    hit.matched_field,
                    f"/buildings/{hit.id}/passport",
                    hit.rank + 1,
                )
            )
        return passport_hits


search_service = SearchService()
