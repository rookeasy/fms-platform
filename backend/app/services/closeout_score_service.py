from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
from app.models import Asset, Building, BuildingContact, Document, Membership
from app.schemas.core import (
    CloseoutScore,
    CloseoutSectionStatus,
    PropertyCloseoutBuildingScore,
    PropertyCloseoutScore,
)
from app.services.building_service import building_service
from app.services.property_service import property_service


@dataclass(frozen=True)
class CloseoutCategory:
    key: str
    label: str
    document_types: set[str]
    keywords: tuple[str, ...] = ()
    requires_passport_record: bool = False
    requires_client_visible: bool = False


CLOSEOUT_CATEGORIES = [
    CloseoutCategory(
        key="building_protection_passport",
        label="Building Protection Passport",
        document_types={"passport_export", "building_protection_certificate"},
        keywords=("building protection passport", "passport"),
        requires_passport_record=True,
    ),
    CloseoutCategory(
        key="drawing_register",
        label="Drawing Register",
        document_types={"drawing", "shop_drawing"},
        keywords=("drawing register",),
    ),
    CloseoutCategory(
        key="as_built_drawings",
        label="As-Built Drawings",
        document_types={"as_built_drawing"},
        keywords=("as-built", "as built"),
    ),
    CloseoutCategory(
        key="peng_compliance_package",
        label="P.Eng. Compliance Package",
        document_types={"engineering_letter"},
        keywords=("p.eng", "professional engineer", "engineering compliance"),
    ),
    CloseoutCategory(
        key="nfpa_contractor_compliance_package",
        label="NFPA Contractor Compliance Package",
        document_types={"contractors_material_test_certificate"},
        keywords=("nfpa", "contractor closeout"),
    ),
    CloseoutCategory(
        key="material_test_certificates",
        label="Material & Test Certificates",
        document_types={
            "material_test_certificate",
            "contractors_material_test_certificate",
            "certificate",
            "backflow_test_report",
            "fire_pump_test_report",
            "sprinkler_test_report",
            "standpipe_test_report",
            "alarm_verification_report",
        },
        keywords=("material", "test certificate", "contractor's material"),
    ),
    CloseoutCategory(
        key="asset_register",
        label="Asset Register",
        document_types=set(),
        keywords=("asset register",),
    ),
    CloseoutCategory(
        key="warranty_package",
        label="Warranty Package",
        document_types={"warranty"},
        keywords=("warranty",),
    ),
    CloseoutCategory(
        key="product_data_om_manuals",
        label="Product Data / O&M Manuals",
        document_types={"manufacturer_data", "owner_manual"},
        keywords=("product data", "o&m", "operation and maintenance", "manual"),
    ),
    CloseoutCategory(
        key="owner_property_manager_handover",
        label="Owner / Property Manager Handover",
        document_types={"owner_manual"},
        keywords=("owner handover", "property manager handover", "handover notes"),
        requires_client_visible=True,
    ),
    CloseoutCategory(
        key="itm_transition",
        label="Fuzion Fire Service ITM Transition",
        document_types={"service_record"},
        keywords=("itm transition", "inspection testing maintenance", "service transition"),
    ),
    CloseoutCategory(
        key="fms_membership_invitation",
        label="FMS Membership Invitation",
        document_types=set(),
        keywords=("membership invitation", "fms membership"),
    ),
]


class CloseoutScoreService:
    def get_building_score(self, db: Session, building_id: UUID, current_user: CurrentUser) -> CloseoutScore:
        building = building_service.get_building(db, building_id, current_user)
        return self._calculate_building_score(db, building, current_user)

    def get_property_score(self, db: Session, property_id: UUID, current_user: CurrentUser) -> PropertyCloseoutScore:
        property_record = property_service.get_property(db, property_id, current_user)
        buildings = list(
            db.scalars(
                select(Building)
                .where(
                    Building.property_id == property_record.id,
                    Building.organization_id == property_record.organization_id,
                    Building.deleted_at.is_(None),
                )
                .order_by(Building.name)
            ).all()
        )
        building_scores = [self._calculate_building_score(db, building, current_user) for building in buildings]
        total_required = sum(score.total_required_items for score in building_scores)
        completed = sum(score.completed_items for score in building_scores)
        ready_count = sum(1 for score in building_scores if score.ready_for_handover)
        completion = round((completed / total_required) * 100) if total_required else 0
        missing_items = sorted({item for score in building_scores for item in score.missing_items})
        warnings = [warning for score in building_scores for warning in score.warnings]
        if not buildings:
            warnings.append("No active buildings are assigned to this property.")

        sections = []
        for category in CLOSEOUT_CATEGORIES:
            category_scores = [score for score in building_scores for score in score.sections if score.key == category.key]
            completed_count = sum(1 for score in category_scores if score.completed)
            evidence_count = sum(score.evidence_count for score in category_scores)
            complete = bool(category_scores) and completed_count == len(category_scores)
            sections.append(
                CloseoutSectionStatus(
                    key=category.key,
                    label=category.label,
                    status="complete" if complete else "missing",
                    completed=complete,
                    evidence_count=evidence_count,
                    evidence_labels=[f"{completed_count}/{len(category_scores)} buildings complete"] if category_scores else [],
                    missing_reason=None if complete else "One or more buildings are missing this required closeout evidence.",
                )
            )

        return PropertyCloseoutScore(
            property_id=property_record.id,
            property_name=property_record.name,
            building_count=len(buildings),
            ready_building_count=ready_count,
            completion_percentage=completion,
            total_required_items=total_required,
            completed_items=completed,
            missing_items=missing_items,
            ready_for_handover=bool(buildings) and ready_count == len(buildings),
            warnings=warnings,
            sections=sections,
            buildings=[
                PropertyCloseoutBuildingScore(
                    building_id=building.id,
                    building_name=building.name,
                    completion_percentage=score.completion_percentage,
                    completed_items=score.completed_items,
                    total_required_items=score.total_required_items,
                    ready_for_handover=score.ready_for_handover,
                    missing_items=score.missing_items,
                )
                for building, score in zip(buildings, building_scores, strict=False)
            ],
        )

    def _calculate_building_score(self, db: Session, building: Building, current_user: CurrentUser) -> CloseoutScore:
        documents = self._building_documents(db, building)
        assets = self._building_assets(db, building)
        contacts = self._building_contacts(db, building)
        has_active_membership = self._has_active_membership(db, building.organization_id)
        section_scores = [
            self._section_status(category, building, documents, assets, contacts, has_active_membership)
            for category in CLOSEOUT_CATEGORIES
        ]
        total_required = len(section_scores)
        completed = sum(1 for section in section_scores if section.completed)
        missing_items = [section.label for section in section_scores if not section.completed]
        warnings = self._warnings(building, documents, assets, contacts, missing_items)
        return CloseoutScore(
            completion_percentage=round((completed / total_required) * 100) if total_required else 0,
            total_required_items=total_required,
            completed_items=completed,
            missing_items=missing_items,
            ready_for_handover=completed == total_required and not warnings,
            warnings=warnings,
            sections=section_scores,
        )

    @staticmethod
    def _building_documents(db: Session, building: Building) -> list[Document]:
        return list(
            db.scalars(
                select(Document)
                .where(
                    Document.building_id == building.id,
                    Document.organization_id == building.organization_id,
                    Document.deleted_at.is_(None),
                )
                .order_by(Document.created_at.desc())
            ).all()
        )

    @staticmethod
    def _building_assets(db: Session, building: Building) -> list[Asset]:
        return list(
            db.scalars(
                select(Asset).where(
                    Asset.building_id == building.id,
                    Asset.organization_id == building.organization_id,
                    Asset.deleted_at.is_(None),
                )
            ).all()
        )

    @staticmethod
    def _building_contacts(db: Session, building: Building) -> list[BuildingContact]:
        return list(
            db.scalars(
                select(BuildingContact).where(
                    BuildingContact.building_id == building.id,
                    BuildingContact.organization_id == building.organization_id,
                    BuildingContact.deleted_at.is_(None),
                )
            ).all()
        )

    @staticmethod
    def _has_active_membership(db: Session, organization_id: UUID) -> bool:
        return (
            db.scalar(
                select(Membership.id)
                .where(
                    Membership.organization_id == organization_id,
                    Membership.status == "active",
                    Membership.deleted_at.is_(None),
                )
                .limit(1)
            )
            is not None
        )

    def _section_status(
        self,
        category: CloseoutCategory,
        building: Building,
        documents: list[Document],
        assets: list[Asset],
        contacts: list[BuildingContact],
        has_active_membership: bool,
    ) -> CloseoutSectionStatus:
        evidence = self._matching_documents(category, documents)
        extra_labels: list[str] = []
        missing_reason = "Missing required closeout evidence."

        if category.key == "asset_register" and assets:
            extra_labels.append(f"{len(assets)} registered asset(s)")
        if category.key == "owner_property_manager_handover" and self._has_handover_contacts(building, contacts):
            extra_labels.append("Owner/property manager details available")
        if category.key == "fms_membership_invitation" and has_active_membership:
            extra_labels.append("Active organization membership")

        completed = bool(evidence or extra_labels)
        if category.requires_passport_record and not any(document.is_passport_record for document in evidence):
            completed = False
            missing_reason = "No Passport-visible evidence is available."
        if category.requires_client_visible and not any(document.is_public_to_client for document in evidence) and not extra_labels:
            completed = False
            missing_reason = "No client-visible handover evidence is available."

        evidence_labels = [document.title or document.name for document in evidence] + extra_labels
        return CloseoutSectionStatus(
            key=category.key,
            label=category.label,
            status="complete" if completed else "missing",
            completed=completed,
            evidence_count=len(evidence_labels),
            evidence_labels=evidence_labels[:5],
            missing_reason=None if completed else missing_reason,
        )

    def _matching_documents(self, category: CloseoutCategory, documents: list[Document]) -> list[Document]:
        return [
            document
            for document in documents
            if document.document_type in category.document_types or self._document_mentions_category(document, category)
        ]

    @staticmethod
    def _document_mentions_category(document: Document, category: CloseoutCategory) -> bool:
        haystack = " ".join(
            [
                document.title or "",
                document.name or "",
                document.description or "",
            ]
        ).lower()
        exact_section = f"closeout section: {category.label.lower()}"
        return exact_section in haystack or any(keyword in haystack for keyword in category.keywords)

    @staticmethod
    def _has_handover_contacts(building: Building, contacts: list[BuildingContact]) -> bool:
        if building.owner_name or building.property_manager_name:
            return True
        return any(contact.contact_type in {"owner", "property_manager", "site_contact"} for contact in contacts)

    @staticmethod
    def _warnings(
        building: Building,
        documents: list[Document],
        assets: list[Asset],
        contacts: list[BuildingContact],
        missing_items: list[str],
    ) -> list[str]:
        warnings = []
        if missing_items:
            warnings.append("Required closeout evidence is missing.")
        if not documents:
            warnings.append("No closeout documents are attached to this building.")
        if not assets:
            warnings.append("No assets are registered for ITM transition.")
        if not contacts and not (building.owner_name or building.property_manager_name):
            warnings.append("No owner or property manager handover contact is available.")
        return warnings


closeout_score_service = CloseoutScoreService()
