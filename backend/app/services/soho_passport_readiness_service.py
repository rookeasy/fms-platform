from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
from app.models import Asset, Building, BuildingContact, Document, DocumentAssetSuggestion
from app.schemas.core import (
    BuildingRead,
    PropertyRead,
    SohoPassportReadinessRead,
    SohoReadinessCategory,
    SohoReadinessHandover,
    SohoReadinessRecord,
)
from app.services.closeout_score_service import closeout_score_service
from app.services.property_service import property_service
from app.services.protected_state_service import protected_state_service


@dataclass(frozen=True)
class SohoExpectedRecord:
    role: str
    label: str
    name_markers: tuple[str, ...]
    type_markers: tuple[str, ...] = ()


EXPECTED_RECORDS = [
    SohoExpectedRecord("building_a", "Building A", ("building a", "bldg a", "bldgs a")),
    SohoExpectedRecord("building_b", "Building B", ("building b", "bldg b", "bldgs b")),
    SohoExpectedRecord(
        "shared_fire_protection",
        "Shared Fire Protection Infrastructure",
        ("shared fire", "fire pump", "backflow", "standpipe", "shared riser"),
        ("shared_infrastructure",),
    ),
    SohoExpectedRecord(
        "common_parking_garage",
        "Common Parking Garage",
        ("common parking", "parking garage", "garage"),
        ("shared_infrastructure",),
    ),
]


class SohoPassportReadinessService:
    def get_readiness(self, db: Session, property_id: UUID, current_user: CurrentUser) -> SohoPassportReadinessRead:
        property_record = property_service.get_property(db, property_id, current_user)
        buildings = list(
            db.scalars(
                select(Building)
                .where(
                    Building.property_id == property_record.id,
                    Building.organization_id == property_record.organization_id,
                    Building.deleted_at.is_(None),
                )
                .order_by(Building.created_at.asc(), Building.name.asc())
            ).all()
        )

        used_ids: set[UUID] = set()
        records = []
        for expected in EXPECTED_RECORDS:
            candidates = [building for building in buildings if self._matches_role(building, expected)]
            canonical = candidates[0] if candidates else None
            if canonical:
                used_ids.add(canonical.id)
            records.append(self._record(db, expected, canonical, max(len(candidates) - 1, 0), current_user))

        for building in buildings:
            if building.id not in used_ids and self._looks_like_soho(building):
                records.append(self._record(db, SohoExpectedRecord("unclassified_soho_record", "Unclassified SOHO Record", ()), building, 0, current_user))

        category_complete = sum(1 for record in records for category in record.evidence_categories if category.status == "complete")
        category_missing = sum(1 for record in records for category in record.evidence_categories if category.status != "complete")
        blocking_items = sorted({item for record in records for item in record.missing_items})
        missing_items = sorted({item for item in blocking_items if item})
        present_records = sum(1 for record in records if record.present and record.expected)
        duplicate_records = sum(record.duplicate_count for record in records)
        client_visible_evidence = sum(record.client_visible_evidence_count for record in records)
        closeout_score = round(sum(record.closeout_score for record in records if record.expected) / len(EXPECTED_RECORDS)) if records else 0
        passport_status = self._rollup_passport_status(records)
        protected_state_status = self._rollup_protected_state(records)
        readiness_state = self._rollup_readiness_state(records, duplicate_records)
        next_action = self._rollup_next_action(readiness_state, records, duplicate_records)

        return SohoPassportReadinessRead(
            property=PropertyRead.model_validate(property_record),
            readiness_state=readiness_state,
            closeout_score=closeout_score,
            expected_records=len(EXPECTED_RECORDS),
            records_present=present_records,
            duplicate_records=duplicate_records,
            evidence_categories_complete=category_complete,
            evidence_categories_missing=category_missing,
            client_visible_evidence_count=client_visible_evidence,
            passport_status=passport_status,
            protected_state_status=protected_state_status,
            blocking_items=blocking_items,
            missing_items=missing_items,
            next_action=next_action,
            records=records,
        )

    def _record(
        self,
        db: Session,
        expected: SohoExpectedRecord,
        building: Building | None,
        duplicate_count: int,
        current_user: CurrentUser,
    ) -> SohoReadinessRecord:
        if building is None:
            return SohoReadinessRecord(
                role=expected.role,
                label=expected.label,
                expected=True,
                present=False,
                duplicate_count=duplicate_count,
                completion_status="Missing",
                missing_items=[f"{expected.label} record is missing."],
                readiness_state="Not Ready",
                next_action=f"Create or map the {expected.label} record from confirmed SOHO source data.",
            )

        documents = self._documents(db, building)
        assets_count = self._count(db, Asset, building)
        contacts_count = self._count(db, BuildingContact, building)
        suggestions = self._asset_suggestions(db, building)
        closeout = closeout_score_service.get_building_score(db, building.id, current_user)
        protected_state = protected_state_service.get_state(db, building.id, current_user)
        passport_records = [document for document in documents if document.is_passport_record]
        client_visible = [document for document in documents if document.is_public_to_client]
        categories = [
            SohoReadinessCategory(
                key=section.key,
                label=section.label,
                status=section.status,
                evidence_count=section.evidence_count,
                missing_reason=section.missing_reason,
            )
            for section in closeout.sections
        ]
        handover = SohoReadinessHandover(
            owner_property_manager_recipient=building.property_manager_name or building.owner_name,
            delivery_status=building.client_handover_status,
            delivery_date=None,
            portal_access_status="Not Configured",
            notes=building.notes,
            next_itm_action="Confirm Fuzion Fire Service ITM transition." if "Fuzion Fire Service ITM Transition" in closeout.missing_items else "Maintain next scheduled ITM action.",
            client_visible_evidence_count=len(client_visible),
            passport_version=building.passport_version,
        )
        readiness_state = self._building_readiness_state(building, closeout.ready_for_handover, protected_state.protected_state_status, duplicate_count)
        return SohoReadinessRecord(
            role=expected.role,
            label=expected.label,
            building=BuildingRead.model_validate(building),
            expected=expected.role != "unclassified_soho_record",
            present=True,
            duplicate_count=duplicate_count,
            completion_status="Ready for handover" if closeout.ready_for_handover else "Closeout incomplete",
            closeout_score=closeout.completion_percentage,
            documents_count=len(documents),
            passport_record_count=len(passport_records),
            client_visible_evidence_count=len(client_visible),
            assets_count=assets_count,
            asset_suggestions_pending=sum(1 for suggestion in suggestions if suggestion.review_status == "review_required"),
            asset_suggestions_approved=sum(1 for suggestion in suggestions if suggestion.review_status == "approved"),
            contacts_count=contacts_count,
            missing_items=closeout.missing_items,
            evidence_categories=categories,
            passport_status=building.passport_status,
            passport_eligible=building.passport_eligible,
            protected_state_status=protected_state.protected_state_status,
            halo_eligible=protected_state.halo_eligible,
            readiness_state=readiness_state,
            next_action=self._building_next_action(building, closeout.missing_items, closeout.ready_for_handover, duplicate_count),
            library_url=f"/buildings/{building.id}/library",
            passport_url=f"/buildings/{building.id}/passport",
            protected_state_url=f"/buildings/{building.id}/protected-state",
            handover=handover,
        )

    @staticmethod
    def _matches_role(building: Building, expected: SohoExpectedRecord) -> bool:
        notes = (building.notes or "").lower()
        haystack = " ".join([building.name or "", building.code or "", building.bpid or "", building.building_type or "", notes]).lower()
        if f"soho_role={expected.role}" in notes:
            return True
        return any(marker in haystack for marker in expected.name_markers) or (
            bool(expected.type_markers) and any(marker == (building.building_type or "") for marker in expected.type_markers) and expected.label.lower() in haystack
        )

    @staticmethod
    def _looks_like_soho(building: Building) -> bool:
        haystack = " ".join([building.name or "", building.code or "", building.bpid or "", building.notes or ""]).lower()
        return "soho" in haystack or building.code == "5004" or building.bpid == "FPP-5004"

    @staticmethod
    def _documents(db: Session, building: Building) -> list[Document]:
        return list(
            db.scalars(
                select(Document)
                .where(
                    Document.organization_id == building.organization_id,
                    Document.building_id == building.id,
                    Document.deleted_at.is_(None),
                    Document.archived_at.is_(None),
                )
                .order_by(Document.created_at.desc())
            ).all()
        )

    @staticmethod
    def _count(db: Session, model: type[Asset] | type[BuildingContact], building: Building) -> int:
        return int(
            db.scalar(
                select(func.count(model.id)).where(
                    model.organization_id == building.organization_id,
                    model.building_id == building.id,
                    model.deleted_at.is_(None),
                )
            )
            or 0
        )

    @staticmethod
    def _asset_suggestions(db: Session, building: Building) -> list[DocumentAssetSuggestion]:
        return list(
            db.scalars(
                select(DocumentAssetSuggestion).where(
                    DocumentAssetSuggestion.organization_id == building.organization_id,
                    DocumentAssetSuggestion.building_id == building.id,
                )
            ).all()
        )

    @staticmethod
    def _building_readiness_state(building: Building, ready_for_handover: bool, protected_state_status: str, duplicate_count: int) -> str:
        if duplicate_count:
            return "Review Required"
        if protected_state_status == "approved":
            return "Ready for Protected-State Review"
        if ready_for_handover and building.passport_status in {"Passport Issued", "Passport Delivered"}:
            return "Ready for Protected-State Review"
        if ready_for_handover:
            return "Ready for Passport"
        if building.passport_status != "Not Started" or building.passport_eligible:
            return "Review Required"
        return "Not Ready"

    @staticmethod
    def _building_next_action(building: Building, missing_items: list[str], ready_for_handover: bool, duplicate_count: int) -> str:
        if duplicate_count:
            return "Resolve duplicate SOHO records before issuing a Passport."
        if missing_items:
            return f"Review Evidence: {missing_items[0]}"
        if not ready_for_handover:
            return "Review closeout evidence and handover contacts."
        if building.passport_status not in {"Passport Issued", "Passport Delivered"}:
            return "Prepare Passport."
        if building.passport_status == "Passport Issued":
            return "Deliver Passport after client handover confirmation."
        return "Evaluate Protected State."

    @staticmethod
    def _rollup_passport_status(records: list[SohoReadinessRecord]) -> str:
        statuses = {record.passport_status for record in records if record.present and record.expected}
        if not statuses:
            return "Not Started"
        if len(statuses) == 1:
            return statuses.pop()
        if statuses <= {"Passport Issued", "Passport Delivered"}:
            return "Passport Issued"
        return "Mixed"

    @staticmethod
    def _rollup_protected_state(records: list[SohoReadinessRecord]) -> str:
        statuses = {record.protected_state_status for record in records if record.present and record.expected}
        if not statuses:
            return "review_required"
        if "not_eligible" in statuses:
            return "not_eligible"
        if "review_required" in statuses:
            return "review_required"
        if "eligible" in statuses:
            return "eligible"
        if statuses == {"approved"}:
            return "approved"
        return "review_required"

    @staticmethod
    def _rollup_readiness_state(records: list[SohoReadinessRecord], duplicate_records: int) -> str:
        expected = [record for record in records if record.expected]
        if duplicate_records:
            return "Review Required"
        if any(not record.present for record in expected):
            return "Not Ready"
        states = {record.readiness_state for record in expected}
        if states == {"Ready for Protected-State Review"}:
            return "Ready for Protected-State Review"
        if states <= {"Ready for Passport", "Ready for Protected-State Review"}:
            return "Ready for Passport"
        if "Review Required" in states:
            return "Review Required"
        return "Not Ready"

    @staticmethod
    def _rollup_next_action(readiness_state: str, records: list[SohoReadinessRecord], duplicate_records: int) -> str:
        if duplicate_records:
            return "Resolve duplicate SOHO records using the cleanup review path."
        for record in records:
            if record.expected and not record.present:
                return record.next_action
        for record in records:
            if record.expected and record.missing_items:
                return record.next_action
        if readiness_state == "Ready for Passport":
            return "Prepare Passport."
        if readiness_state == "Ready for Protected-State Review":
            return "Evaluate Protected State."
        return "Review Evidence."


soho_passport_readiness_service = SohoPassportReadinessService()
