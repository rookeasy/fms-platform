from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
from app.models import Asset, AssetType, Document, DocumentAssetSuggestion
from app.schemas.core import DocumentAssetSuggestionUpdate
from app.services.exceptions import not_found, validation_error
from app.services.tenant import ensure_organization_access

EXTRACTION_STATUSES = {"pending", "processing", "review_required", "approved", "rejected", "failed"}
SUGGESTION_REVIEW_STATUSES = {"review_required", "approved", "rejected"}


@dataclass(frozen=True)
class AssetPattern:
    asset_type: str
    code_candidates: tuple[str, ...]
    keywords: tuple[str, ...]
    default_name: str


ASSET_PATTERNS = [
    AssetPattern("Fire Pump", ("fire_pump",), ("fire pump", "pump room"), "Fire Pump"),
    AssetPattern("Jockey Pump", ("jockey_pump", "fire_pump"), ("jockey pump",), "Jockey Pump"),
    AssetPattern("Backflow Preventer", ("backflow", "backflow_preventer"), ("backflow",), "Backflow Preventer"),
    AssetPattern("Fire Department Connection", ("fire_department_connection", "standpipe"), ("fdc", "fire department connection"), "Fire Department Connection"),
    AssetPattern("Wet Sprinkler System", ("wet_sprinkler_system", "sprinkler"), ("wet sprinkler", "wet system", "sprinkler"), "Wet Sprinkler System"),
    AssetPattern("Dry Sprinkler System", ("dry_sprinkler_system", "sprinkler"), ("dry sprinkler", "dry system"), "Dry Sprinkler System"),
    AssetPattern("Standpipe System", ("standpipe_system", "standpipe"), ("standpipe",), "Standpipe System"),
    AssetPattern("Combined Sprinkler/Standpipe System", ("combined_sprinkler_standpipe", "standpipe"), ("combined sprinkler", "sprinkler/standpipe"), "Combined Sprinkler/Standpipe System"),
    AssetPattern("Zone Control Assembly", ("zone_control_assembly", "valve"), ("zone control", "zca"), "Zone Control Assembly"),
    AssetPattern("Riser", ("riser", "sprinkler"), ("riser",), "Riser"),
    AssetPattern("Flow Switch", ("flow_switch", "fire_alarm"), ("flow switch", "waterflow"), "Flow Switch"),
    AssetPattern("Main Control Valve", ("main_control_valve", "valve"), ("main control valve", "control valve"), "Main Control Valve"),
    AssetPattern("Inspector's Test", ("inspectors_test", "sprinkler"), ("inspector", "test connection"), "Inspector's Test"),
    AssetPattern("Underground Fire Main", ("underground_fire_main", "water_supply"), ("underground", "fire main"), "Underground Fire Main"),
    AssetPattern("Garbage Chute Sprinkler System", ("garbage_chute_sprinkler", "sprinkler"), ("garbage chute", "chute sprinkler"), "Garbage Chute Sprinkler System"),
    AssetPattern("Mechanical Penthouse System", ("mechanical_penthouse_system", "sprinkler"), ("mechanical penthouse", "penthouse"), "Mechanical Penthouse System"),
]


class DocumentExtractionService:
    def run_extraction(self, db: Session, document: Document) -> list[DocumentAssetSuggestion]:
        document.extraction_status = "processing"
        document.extraction_source = "rule_based"
        summary = self.extract_metadata(document)
        for key, value in summary.items():
            if getattr(document, key, None) in {None, ""} and key in {"drawing_number", "revision", "evidence_category"}:
                setattr(document, key, value)
        document.extraction_summary = {
            "source": "rule_based",
            "message": "Deterministic filename metadata extraction; no external AI provider configured.",
            **summary,
        }

        suggestions = self._suggest_assets(db, document)
        document.extraction_status = "review_required" if suggestions else "approved"
        return suggestions

    def extract_metadata(self, document: Document) -> dict[str, str]:
        filename = document.original_filename or document.title or document.name
        stem = Path(filename).stem
        normalized = self._normalize(stem)
        metadata: dict[str, str] = {}
        drawing_match = re.search(r"\b([A-Z]{1,4}[-_ ]?\d{1,4}(?:\.\d+)?)\b", stem, flags=re.IGNORECASE)
        revision_match = re.search(r"\b(?:rev(?:ision)?|r)[-_ ]?([A-Z0-9]+)\b", stem, flags=re.IGNORECASE)
        if drawing_match:
            metadata["drawing_number"] = drawing_match.group(1).replace(" ", "-").upper()
        if revision_match:
            metadata["revision"] = revision_match.group(1).upper()
        metadata["evidence_category"] = self._classify_evidence(normalized, document.document_type)
        return metadata

    def list_suggestions(self, db: Session, document_id: UUID, current_user: CurrentUser) -> list[DocumentAssetSuggestion]:
        document = self._get_document(db, document_id, current_user)
        return list(
            db.scalars(
                select(DocumentAssetSuggestion)
                .where(DocumentAssetSuggestion.document_id == document.id)
                .order_by(DocumentAssetSuggestion.created_at.desc())
            ).all()
        )

    def approve_suggestion(
        self,
        db: Session,
        document_id: UUID,
        suggestion_id: UUID,
        current_user: CurrentUser,
        payload: DocumentAssetSuggestionUpdate | None = None,
    ) -> DocumentAssetSuggestion:
        document = self._get_document(db, document_id, current_user)
        suggestion = self._get_suggestion(db, document, suggestion_id)
        if payload is not None:
            self._apply_suggestion_update(suggestion, payload)
        if suggestion.review_status == "approved":
            return suggestion
        if document.building_id is None:
            raise validation_error("Asset suggestions require a building assignment before approval.")

        asset_type = self._resolve_asset_type(db, suggestion, document.organization_id)
        asset = self._find_matching_asset(db, document.building_id, asset_type.id, suggestion)
        if asset is None:
            asset = Asset(
                organization_id=document.organization_id,
                building_id=document.building_id,
                asset_type_id=asset_type.id,
                source_document_id=document.id,
                name=suggestion.suggested_name,
                tag=None,
                asset_tag=None,
                location_description=suggestion.location_description,
                manufacturer=suggestion.manufacturer,
                model=suggestion.model,
                status="active",
                condition_rating="unknown",
                notes=f"Created from reviewed document suggestion {suggestion.id}.",
            )
            db.add(asset)
            db.flush()
        elif asset.source_document_id is None:
            asset.source_document_id = document.id

        suggestion.asset_type_id = asset_type.id
        suggestion.approved_asset_id = asset.id
        suggestion.review_status = "approved"
        suggestion.reviewed_at = datetime.now(timezone.utc)
        self._sync_document_status(db, document)
        db.commit()
        db.refresh(suggestion)
        return suggestion

    def reject_suggestion(self, db: Session, document_id: UUID, suggestion_id: UUID, current_user: CurrentUser) -> DocumentAssetSuggestion:
        document = self._get_document(db, document_id, current_user)
        suggestion = self._get_suggestion(db, document, suggestion_id)
        suggestion.review_status = "rejected"
        suggestion.reviewed_at = datetime.now(timezone.utc)
        self._sync_document_status(db, document)
        db.commit()
        db.refresh(suggestion)
        return suggestion

    def approve_all(self, db: Session, document_id: UUID, current_user: CurrentUser) -> list[DocumentAssetSuggestion]:
        document = self._get_document(db, document_id, current_user)
        suggestions = list(
            db.scalars(
                select(DocumentAssetSuggestion).where(
                    DocumentAssetSuggestion.document_id == document.id,
                    DocumentAssetSuggestion.review_status == "review_required",
                )
            ).all()
        )
        approved = []
        for suggestion in suggestions:
            approved.append(self.approve_suggestion(db, document.id, suggestion.id, current_user))
        return approved

    def _suggest_assets(self, db: Session, document: Document) -> list[DocumentAssetSuggestion]:
        if document.building_id is None:
            return []
        haystack = self._normalize(" ".join([document.original_filename or "", document.title or "", document.description or ""]))
        existing = {
            item.suggested_asset_type.lower()
            for item in db.scalars(select(DocumentAssetSuggestion).where(DocumentAssetSuggestion.document_id == document.id)).all()
        }
        suggestions: list[DocumentAssetSuggestion] = []
        for pattern in ASSET_PATTERNS:
            if pattern.asset_type.lower() in existing:
                continue
            if not any(keyword in haystack for keyword in pattern.keywords):
                continue
            location = self._extract_location(haystack)
            suggestion = DocumentAssetSuggestion(
                organization_id=document.organization_id,
                document_id=document.id,
                building_id=document.building_id,
                asset_type_id=self._find_asset_type_id(db, document.organization_id, pattern),
                suggested_asset_type=pattern.asset_type,
                suggested_name=f"{location} {pattern.default_name}".strip() if location else pattern.default_name,
                location_description=location,
                confidence=72 if location else 64,
                evidence_snippet=document.original_filename or document.title or document.name,
                extraction_source="rule_based",
                review_status="review_required",
            )
            db.add(suggestion)
            suggestions.append(suggestion)
        db.flush()
        return suggestions

    def _sync_document_status(self, db: Session, document: Document) -> None:
        statuses = list(
            db.scalars(
                select(DocumentAssetSuggestion.review_status).where(DocumentAssetSuggestion.document_id == document.id)
            ).all()
        )
        if statuses and all(status == "approved" for status in statuses):
            document.extraction_status = "approved"
        elif statuses and all(status in {"approved", "rejected"} for status in statuses):
            document.extraction_status = "approved"
        elif statuses:
            document.extraction_status = "review_required"
        else:
            document.extraction_status = "approved"

    @staticmethod
    def _apply_suggestion_update(suggestion: DocumentAssetSuggestion, payload: DocumentAssetSuggestionUpdate) -> None:
        values = payload.model_dump(exclude_unset=True)
        for key, value in values.items():
            setattr(suggestion, key, value)

    @staticmethod
    def _get_document(db: Session, document_id: UUID, current_user: CurrentUser) -> Document:
        document = db.get(Document, document_id)
        if document is None or document.deleted_at is not None:
            raise not_found("Document not found.")
        ensure_organization_access(current_user, document.organization_id)
        return document

    @staticmethod
    def _get_suggestion(db: Session, document: Document, suggestion_id: UUID) -> DocumentAssetSuggestion:
        suggestion = db.get(DocumentAssetSuggestion, suggestion_id)
        if suggestion is None or suggestion.document_id != document.id:
            raise not_found("Asset suggestion not found.")
        return suggestion

    def _resolve_asset_type(self, db: Session, suggestion: DocumentAssetSuggestion, organization_id: UUID) -> AssetType:
        if suggestion.asset_type_id:
            asset_type = db.get(AssetType, suggestion.asset_type_id)
            if asset_type is not None and asset_type.deleted_at is None:
                return asset_type
        pattern = next((item for item in ASSET_PATTERNS if item.asset_type == suggestion.suggested_asset_type), None)
        asset_type_id = self._find_asset_type_id(db, organization_id, pattern) if pattern else None
        if asset_type_id:
            asset_type = db.get(AssetType, asset_type_id)
            if asset_type is not None:
                return asset_type
        fallback = db.scalar(select(AssetType).where(AssetType.code == "other", AssetType.deleted_at.is_(None)).limit(1))
        if fallback is None:
            raise validation_error("No matching asset type is available for this suggestion.")
        return fallback

    @staticmethod
    def _find_matching_asset(db: Session, building_id: UUID, asset_type_id: UUID, suggestion: DocumentAssetSuggestion) -> Asset | None:
        normalized_name = suggestion.suggested_name.strip().lower()
        normalized_location = (suggestion.location_description or "").strip().lower()
        assets = db.scalars(
            select(Asset).where(
                Asset.building_id == building_id,
                Asset.asset_type_id == asset_type_id,
                Asset.deleted_at.is_(None),
            )
        ).all()
        for asset in assets:
            if asset.name.strip().lower() == normalized_name:
                return asset
            if normalized_location and (asset.location_description or "").strip().lower() == normalized_location:
                return asset
        return None

    @staticmethod
    def _find_asset_type_id(db: Session, organization_id: UUID, pattern: AssetPattern | None) -> UUID | None:
        if pattern is None:
            return None
        for code in pattern.code_candidates:
            asset_type = db.scalar(
                select(AssetType)
                .where(
                    AssetType.code == code,
                    AssetType.deleted_at.is_(None),
                    (AssetType.organization_id.is_(None)) | (AssetType.organization_id == organization_id),
                )
                .limit(1)
            )
            if asset_type:
                return asset_type.id
        return None

    @staticmethod
    def _classify_evidence(normalized: str, document_type: str) -> str:
        if "as built" in normalized or document_type == "as_built_drawing":
            return "As-Built Drawings"
        if "warranty" in normalized or document_type == "warranty":
            return "Warranty Package"
        if "manual" in normalized or "o&m" in normalized or document_type in {"owner_manual", "manufacturer_data"}:
            return "Product Data / O&M Manuals"
        if "certificate" in normalized or "test" in normalized or document_type.endswith("_test_report"):
            return "Material & Test Certificates"
        if "engineering" in normalized or document_type == "engineering_letter":
            return "P.Eng. Compliance Package"
        if "passport" in normalized:
            return "Building Protection Passport"
        return "Drawing Register" if "drawing" in document_type else "Building Protection Passport"

    @staticmethod
    def _extract_location(normalized: str) -> str | None:
        for label, keywords in {
            "P1 East": ("p1 east", "parking east"),
            "P1 West": ("p1 west", "parking west"),
            "Parking Garage": ("garage", "parking"),
            "Amenity": ("amenity",),
            "Mechanical Penthouse": ("mechanical penthouse", "penthouse"),
            "Building A": ("building a", "bldg a"),
            "Building B": ("building b", "bldg b"),
        }.items():
            if any(keyword in normalized for keyword in keywords):
                return label
        return None

    @staticmethod
    def _normalize(value: str) -> str:
        return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


document_extraction_service = DocumentExtractionService()
