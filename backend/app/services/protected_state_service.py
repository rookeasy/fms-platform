from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
from app.models import Asset, Building, BuildingContact, Deficiency, ProtectedStateCertification
from app.schemas.core import ProtectedStateAction, ProtectedStateCriterion, ProtectedStateEvaluationRead
from app.services.audit_log import audit_service
from app.services.building_service import building_service
from app.services.closeout_score_service import closeout_score_service
from app.services.exceptions import validation_error

EVALUATION_VERSION = "protected-state-mvp-001"
PASSPORT_ISSUED_STATUSES = {"Passport Issued", "Passport Delivered"}
HANDOVER_COMPLETE_STATUSES = {"complete", "completed", "delivered", "handover complete", "client handover complete"}
ACTIVE_DEFICIENCY_STATUSES = {"open", "new", "in_progress", "pending", "unresolved"}
CRITICAL_DEFICIENCY_SEVERITIES = {"critical", "life_safety", "high"}
FINAL_STATUSES = {"approved", "suspended", "revoked"}


@dataclass(frozen=True)
class CriterionResult:
    key: str
    label: str
    status: str
    message: str


class ProtectedStateService:
    def get_state(self, db: Session, building_id: UUID, current_user: CurrentUser) -> ProtectedStateEvaluationRead:
        building = building_service.get_building(db, building_id, current_user)
        certification = self._get_certification(db, building)
        if certification and certification.criteria_snapshot:
            return self._response_from_snapshot(building, certification)
        return self._evaluate(db, building, current_user, certification, persist=False)

    def evaluate(self, db: Session, building_id: UUID, current_user: CurrentUser) -> ProtectedStateEvaluationRead:
        building = building_service.get_building(db, building_id, current_user)
        certification = self._get_or_create_certification(db, building)
        result = self._evaluate(db, building, current_user, certification, persist=True)
        db.commit()
        db.refresh(certification)
        return result

    def approve(self, db: Session, building_id: UUID, payload: ProtectedStateAction, current_user: CurrentUser) -> ProtectedStateEvaluationRead:
        building = building_service.get_building(db, building_id, current_user)
        certification = self._get_or_create_certification(db, building)
        result = self._evaluate(db, building, current_user, certification, persist=True)
        if result.criteria_failed or result.criteria_unknown or result.protected_state_status != "eligible":
            raise validation_error("Protected State cannot be approved until all criteria pass.")
        now = datetime.now(timezone.utc)
        certification.status = "approved"
        certification.approved_at = now
        certification.approved_by = current_user.email
        certification.suspended_at = None
        certification.revoked_at = None
        certification.reason = payload.reason
        certification.notes = payload.notes
        certification.criteria_snapshot = {
            **(certification.criteria_snapshot or {}),
            "protected_state_status": "approved",
            "halo_eligible": True,
        }
        self._audit(db, "protected_state_approved", certification, current_user)
        db.commit()
        db.refresh(certification)
        return self._response_from_snapshot(building, certification)

    def suspend(self, db: Session, building_id: UUID, payload: ProtectedStateAction, current_user: CurrentUser) -> ProtectedStateEvaluationRead:
        return self._terminal_action(db, building_id, payload, current_user, "suspended", "protected_state_suspended")

    def revoke(self, db: Session, building_id: UUID, payload: ProtectedStateAction, current_user: CurrentUser) -> ProtectedStateEvaluationRead:
        return self._terminal_action(db, building_id, payload, current_user, "revoked", "protected_state_revoked")

    def _terminal_action(
        self,
        db: Session,
        building_id: UUID,
        payload: ProtectedStateAction,
        current_user: CurrentUser,
        status: str,
        audit_action: str,
    ) -> ProtectedStateEvaluationRead:
        building = building_service.get_building(db, building_id, current_user)
        certification = self._get_or_create_certification(db, building)
        now = datetime.now(timezone.utc)
        certification.status = status
        if status == "suspended":
            certification.suspended_at = now
        if status == "revoked":
            certification.revoked_at = now
        certification.reason = payload.reason
        certification.notes = payload.notes
        snapshot = certification.criteria_snapshot or {}
        certification.criteria_snapshot = {**snapshot, "protected_state_status": status, "halo_eligible": False}
        self._audit(db, audit_action, certification, current_user)
        db.commit()
        db.refresh(certification)
        return self._response_from_snapshot(building, certification)

    def _evaluate(
        self,
        db: Session,
        building: Building,
        current_user: CurrentUser,
        certification: ProtectedStateCertification | None,
        *,
        persist: bool,
    ) -> ProtectedStateEvaluationRead:
        now = datetime.now(timezone.utc)
        criteria = self._criteria(db, building, current_user)
        failed = [item for item in criteria if item.status == "failed"]
        unknown = [item for item in criteria if item.status == "unknown"]
        passed = [item for item in criteria if item.status == "passed"]
        evaluated_status = "eligible" if not failed and not unknown else "review_required" if unknown else "not_eligible"
        record_status = certification.status if certification and certification.status in FINAL_STATUSES else evaluated_status
        halo_eligible = bool(certification and certification.status == "approved" and evaluated_status == "eligible")
        snapshot = {
            "protected_state_status": record_status,
            "evaluated_status": evaluated_status,
            "halo_eligible": halo_eligible,
            "criteria": [item.__dict__ for item in criteria],
            "blocking_items": [item.message for item in [*failed, *unknown]],
            "warnings": [item.message for item in unknown],
        }
        if persist and certification:
            certification.property_id = building.property_id
            certification.evaluation_version = EVALUATION_VERSION
            certification.evaluated_at = now
            certification.evaluated_by = current_user.email
            if certification.status not in FINAL_STATUSES:
                certification.status = evaluated_status
            certification.criteria_snapshot = snapshot
            self._audit(db, "protected_state_evaluated", certification, current_user)
        return self._response(building.id, certification, record_status, halo_eligible, criteria, now)

    def _criteria(self, db: Session, building: Building, current_user: CurrentUser) -> list[CriterionResult]:
        closeout = closeout_score_service.get_building_score(db, building.id, current_user)
        section_by_key = {section.key: section for section in closeout.sections}
        assets = list(db.scalars(select(Asset).where(Asset.building_id == building.id, Asset.deleted_at.is_(None))).all())
        contacts = list(db.scalars(select(BuildingContact).where(BuildingContact.building_id == building.id, BuildingContact.deleted_at.is_(None))).all())
        critical_deficiencies = list(
            db.scalars(
                select(Deficiency).where(
                    Deficiency.building_id == building.id,
                    Deficiency.deleted_at.is_(None),
                    Deficiency.status.in_(ACTIVE_DEFICIENCY_STATUSES),
                    Deficiency.severity.in_(CRITICAL_DEFICIENCY_SEVERITIES),
                )
            ).all()
        )

        def closeout_section(key: str, label: str) -> CriterionResult:
            section = section_by_key.get(key)
            if section and section.completed:
                return CriterionResult(key, label, "passed", f"{label} evidence is present.")
            return CriterionResult(key, label, "failed", f"{label} evidence is missing.")

        handover_status = (building.client_handover_status or "").strip().lower()
        has_handover_contact = bool(building.owner_name or building.property_manager_name or any(contact.contact_type in {"owner", "property_manager", "site_contact"} for contact in contacts))
        handover_complete = handover_status in HANDOVER_COMPLETE_STATUSES

        criteria = [
            CriterionResult(
                "passport_lifecycle",
                "Passport lifecycle",
                "passed" if building.passport_status in PASSPORT_ISSUED_STATUSES else "failed",
                "Passport is Issued or Delivered." if building.passport_status in PASSPORT_ISSUED_STATUSES else "Passport has not been Issued or Delivered.",
            ),
            CriterionResult(
                "closeout_readiness",
                "Closeout readiness",
                "passed" if closeout.ready_for_handover and closeout.completion_percentage >= 100 and not closeout.missing_items else "failed",
                "Closeout is ready for handover." if closeout.ready_for_handover and not closeout.missing_items else "Closeout is not fully ready for handover.",
            ),
            closeout_section("peng_compliance_package", "P.Eng. Compliance Package"),
            closeout_section("nfpa_contractor_compliance_package", "NFPA Contractor Compliance Package"),
            closeout_section("material_test_certificates", "Material & Test Certificates"),
            CriterionResult(
                "asset_register",
                "Core assets registered",
                "passed" if assets else "failed",
                f"{len(assets)} asset(s) are registered." if assets else "No core fire-protection assets are registered.",
            ),
            CriterionResult(
                "handover",
                "Owner / property manager handover",
                "passed" if has_handover_contact and handover_complete else "unknown" if has_handover_contact else "failed",
                "Handover contact and complete status are available." if has_handover_contact and handover_complete else "Handover status is not confirmed complete." if has_handover_contact else "No owner/property manager handover contact is available.",
            ),
            closeout_section("itm_transition", "Fuzion Fire Service ITM Transition"),
            CriterionResult(
                "critical_deficiencies",
                "Critical deficiencies",
                "passed" if not critical_deficiencies else "failed",
                "No unresolved critical deficiencies are recorded." if not critical_deficiencies else f"{len(critical_deficiencies)} unresolved critical/high deficiency item(s) block certification.",
            ),
        ]
        return criteria

    def _response_from_snapshot(self, building: Building, certification: ProtectedStateCertification) -> ProtectedStateEvaluationRead:
        snapshot = certification.criteria_snapshot or {}
        criteria = [
            CriterionResult(
                key=item.get("key", "unknown"),
                label=item.get("label", "Unknown criterion"),
                status=item.get("status", "unknown"),
                message=item.get("message", "Criterion status is unknown."),
            )
            for item in snapshot.get("criteria", [])
        ]
        return self._response(
            building.id,
            certification,
            snapshot.get("protected_state_status", certification.status),
            bool(snapshot.get("halo_eligible", False)) and certification.status == "approved",
            criteria,
            certification.evaluated_at or datetime.now(timezone.utc),
            blocking_items=snapshot.get("blocking_items"),
            warnings=snapshot.get("warnings"),
        )

    @staticmethod
    def _response(
        building_id: UUID,
        certification: ProtectedStateCertification | None,
        status: str,
        halo_eligible: bool,
        criteria: list[CriterionResult],
        evaluated_at: datetime,
        blocking_items: list[str] | None = None,
        warnings: list[str] | None = None,
    ) -> ProtectedStateEvaluationRead:
        failed = [item for item in criteria if item.status == "failed"]
        unknown = [item for item in criteria if item.status == "unknown"]
        return ProtectedStateEvaluationRead(
            building_id=building_id,
            protected_state_status=status,
            halo_eligible=halo_eligible and status == "approved",
            criteria_total=len(criteria),
            criteria_passed=sum(1 for item in criteria if item.status == "passed"),
            criteria_failed=len(failed),
            criteria_unknown=len(unknown),
            criteria=[ProtectedStateCriterion(**item.__dict__) for item in criteria],
            blocking_items=blocking_items if blocking_items is not None else [item.message for item in [*failed, *unknown]],
            warnings=warnings if warnings is not None else [item.message for item in unknown],
            evaluated_at=evaluated_at,
            evaluation_version=certification.evaluation_version if certification else EVALUATION_VERSION,
            certification_record_id=certification.id if certification else None,
            approved_at=certification.approved_at if certification else None,
            approved_by=certification.approved_by if certification else None,
        )

    @staticmethod
    def _get_certification(db: Session, building: Building) -> ProtectedStateCertification | None:
        return db.scalar(select(ProtectedStateCertification).where(ProtectedStateCertification.building_id == building.id))

    def _get_or_create_certification(self, db: Session, building: Building) -> ProtectedStateCertification:
        certification = self._get_certification(db, building)
        if certification:
            return certification
        certification = ProtectedStateCertification(
            organization_id=building.organization_id,
            building_id=building.id,
            property_id=building.property_id,
            status="review_required",
            evaluation_version=EVALUATION_VERSION,
        )
        db.add(certification)
        db.flush()
        return certification

    @staticmethod
    def _audit(db: Session, action: str, certification: ProtectedStateCertification, current_user: CurrentUser) -> None:
        audit_service.record(
            db,
            action=action,
            entity_type="protected_state_certification",
            entity_id=certification.id,
            organization_id=certification.organization_id,
            current_user=current_user,
            metadata={"building_id": str(certification.building_id), "status": certification.status},
        )


protected_state_service = ProtectedStateService()
