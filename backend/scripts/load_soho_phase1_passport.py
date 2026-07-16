from __future__ import annotations

import argparse
import json
import mimetypes
from collections.abc import Iterable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import Building, Document, DocumentAssetSuggestion, Organization, Property
from scripts.seed_fuzion_projects import ensure_fuzion_organization

SOURCE_TAG = "source=soho_phase1_production_passport"
PROPERTY_NAME = "SOHO Phase I"
SUPPORTED_EXTENSIONS = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".csv", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".txt"}

SOHO_RECORDS = {
    "building_a": {
        "label": "Building A",
        "name": "SOHO Phase I - Building A",
        "code": "SOHO-PH1-A",
        "bpid": "FPP-SOHO-PH1-A",
        "building_type": "building",
    },
    "building_b": {
        "label": "Building B",
        "name": "SOHO Phase I - Building B",
        "code": "SOHO-PH1-B",
        "bpid": "FPP-SOHO-PH1-B",
        "building_type": "building",
    },
    "shared_fire_protection": {
        "label": "Shared Fire Protection Infrastructure",
        "name": "SOHO Phase I - Shared Fire Protection Infrastructure",
        "code": "SOHO-PH1-SHARED-FP",
        "bpid": "FPP-SOHO-PH1-SHARED-FP",
        "building_type": "shared_infrastructure",
    },
    "common_parking_garage": {
        "label": "Common Parking Garage",
        "name": "SOHO Phase I - Common Parking Garage",
        "code": "SOHO-PH1-GARAGE",
        "bpid": "FPP-SOHO-PH1-GARAGE",
        "building_type": "shared_infrastructure",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Load or report SOHO Phase I Passport readiness records.")
    parser.add_argument("--dry-run", action="store_true", help="Inspect and print intended changes without writing.")
    parser.add_argument("--report-only", action="store_true", help="Print current SOHO readiness and do not write.")
    parser.add_argument("--cleanup-duplicates", action="store_true", help="Soft-archive duplicate SOHO records after canonical records are identified.")
    parser.add_argument("--reclassify-existing", action="store_true", help="Conservatively reclassify existing SOHO documents from filenames and metadata.")
    parser.add_argument("--building-a-path", type=Path, help="Folder of Building A evidence files.")
    parser.add_argument("--building-b-path", type=Path, help="Folder of Building B evidence files.")
    parser.add_argument("--shared-path", type=Path, help="Folder of shared fire protection evidence files.")
    parser.add_argument("--property-path", type=Path, help="Folder of property-level or parking/common evidence files.")
    return parser.parse_args()


def load_soho_phase1_passport(args: argparse.Namespace) -> dict[str, Any]:
    db = SessionLocal()
    should_write = not args.dry_run and not args.report_only
    counts: dict[str, Any] = {
        "properties_reused": 0,
        "properties_created": 0,
        "buildings_reused": 0,
        "buildings_created": 0,
        "buildings_archived": 0,
        "documents_loaded": 0,
        "documents_reused": 0,
        "documents_reclassified": 0,
        "documents_archived": 0,
        "assets_suggested": 0,
        "assets_approved": 0,
        "assets_reused": 0,
        "evidence_categories_complete": 0,
        "evidence_categories_missing": 0,
        "passport_status": "Not Started",
        "protected_state_status": "review_required",
        "blocking_items": [],
    }
    try:
        existing_property = find_existing_soho_property(db)
        organization = existing_property.organization if existing_property else get_organization(db, should_write)
        if organization is None:
            counts["blocking_items"].append("No Fuzion organization is available. Run the reference/Fuzion seed before loading SOHO.")
            return counts

        property_record = existing_property or get_property(db, organization, should_write, counts)
        if property_record is None:
            counts["blocking_items"].append("SOHO Phase I property is not present and report-only/dry-run mode prevented creation.")
            return counts
        if existing_property:
            counts["properties_reused"] += 1

        records = ensure_records(db, organization, property_record, should_write, counts)
        if args.cleanup_duplicates:
            cleanup_duplicates(db, organization, property_record, records, should_write, counts)
            cleanup_duplicate_properties(db, property_record, should_write, counts)

        path_map = {
            "building_a": args.building_a_path,
            "building_b": args.building_b_path,
            "shared_fire_protection": args.shared_path,
            "common_parking_garage": args.property_path,
        }
        for role, folder in path_map.items():
            if folder and role in records:
                load_documents(db, property_record, records[role], role, folder, should_write, counts)

        if args.reclassify_existing:
            reclassify_existing_documents(db, records.values(), should_write, counts)

        summarize_state(db, records.values(), counts)
        if should_write:
            db.commit()
        else:
            db.rollback()
        return counts
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_organization(db: Session, should_write: bool) -> Organization | None:
    organization = db.scalar(select(Organization).where(Organization.slug == "fuzion-tech"))
    if organization or not should_write:
        return organization
    return ensure_fuzion_organization(db)


def find_existing_soho_property(db: Session) -> Property | None:
    return db.scalar(
        select(Property)
        .where(
            Property.name == PROPERTY_NAME,
            Property.deleted_at.is_(None),
        )
        .order_by(Property.created_at.asc())
    )


def get_property(db: Session, organization: Organization, should_write: bool, counts: dict[str, Any]) -> Property | None:
    property_record = db.scalar(
        select(Property).where(
            Property.organization_id == organization.id,
            Property.name == PROPERTY_NAME,
            Property.deleted_at.is_(None),
        )
    )
    if property_record:
        counts["properties_reused"] += 1
        return property_record
    if not should_write:
        return None
    property_record = Property(
        organization_id=organization.id,
        name=PROPERTY_NAME,
        property_type="multi_building",
        status="active",
        country="Canada",
        notes=SOURCE_TAG,
    )
    db.add(property_record)
    db.flush()
    counts["properties_created"] += 1
    return property_record


def ensure_records(
    db: Session,
    organization: Organization,
    property_record: Property,
    should_write: bool,
    counts: dict[str, Any],
) -> dict[str, Building]:
    records: dict[str, Building] = {}
    for role, definition in SOHO_RECORDS.items():
        building = find_record(db, organization, role, definition)
        if building:
            counts["buildings_reused"] += 1
            if should_write:
                update_record(building, property_record, role, definition)
                clear_role_from_other_records(db, organization, role, building)
            records[role] = building
            continue
        if not should_write:
            continue
        building = Building(
            organization_id=organization.id,
            property_id=property_record.id,
            name=definition["name"],
            code=definition["code"],
            bpid=definition["bpid"],
            address_line_1=property_record.address_line_1 or "SOHO Phase I",
            address_line1=property_record.address_line_1 or "SOHO Phase I",
            city=property_record.city or "Hamilton",
            province_state=property_record.province_state or "Ontario",
            region=property_record.province_state or "Ontario",
            country=property_record.country or "Canada",
            postal_code=property_record.postal_code,
            building_type=definition["building_type"],
            status="completed",
            project_classification="completed",
            passport_eligible=True,
            passport_status="Building Registered",
            passport_version="v0.1",
            client_handover_status="Closeout Incomplete",
            notes=record_notes(role),
        )
        db.add(building)
        db.flush()
        records[role] = building
        counts["buildings_created"] += 1
    return records


def find_record(db: Session, organization: Organization, role: str, definition: dict[str, str]) -> Building | None:
    notes_marker = f"soho_role={role}"
    candidates = list(
        db.scalars(
            select(Building)
            .where(
                Building.organization_id == organization.id,
            )
            .order_by(Building.created_at.asc(), Building.name.asc())
        ).all()
    )
    for building in candidates:
        if building.code == definition["code"] or building.bpid == definition["bpid"]:
            return building
    for building in candidates:
        if building.name.lower() == definition["name"].lower():
            return building
    global_exact_candidates = list(
        db.scalars(
            select(Building)
            .where(
                (Building.code == definition["code"]) | (Building.bpid == definition["bpid"]) | (func.lower(Building.name) == definition["name"].lower()),
            )
            .order_by(Building.created_at.asc(), Building.name.asc())
        ).all()
    )
    if global_exact_candidates:
        return global_exact_candidates[0]
    for building in candidates:
        if notes_marker in (building.notes or ""):
            return building
    for building in candidates:
        if role_matches_legacy_record(building, role):
            return building
    global_candidates = list(
        db.scalars(
            select(Building)
            .where(
                (Building.code == definition["code"]) | (Building.bpid == definition["bpid"]) | Building.notes.contains(f"soho_role={role}"),
            )
            .order_by(Building.created_at.asc(), Building.name.asc())
        ).all()
    )
    if global_candidates:
        return global_candidates[0]
    return None


def update_record(building: Building, property_record: Property, role: str, definition: dict[str, str]) -> None:
    building.organization_id = property_record.organization_id
    building.property_id = property_record.id
    building.name = building.name or definition["name"]
    building.code = building.code or definition["code"]
    building.bpid = building.bpid or definition["bpid"]
    building.building_type = building.building_type or definition["building_type"]
    building.status = "completed"
    building.project_classification = building.project_classification or "completed"
    building.passport_eligible = True
    if building.passport_status == "Not Started":
        building.passport_status = "Building Registered"
    building.passport_version = building.passport_version or "v0.1"
    building.client_handover_status = building.client_handover_status or "Closeout Incomplete"
    building.deleted_at = None
    building.notes = merge_note(building.notes, record_notes(role))


def clear_role_from_other_records(db: Session, organization: Organization, role: str, canonical: Building) -> None:
    marker = f"soho_role={role}"
    buildings = list(
        db.scalars(
            select(Building).where(
                Building.organization_id == organization.id,
                Building.id != canonical.id,
                Building.notes.contains(marker),
            )
        ).all()
    )
    for building in buildings:
        lines = [line for line in (building.notes or "").splitlines() if line != marker]
        building.notes = "\n".join(lines) or None


def cleanup_duplicates(
    db: Session,
    organization: Organization,
    property_record: Property,
    records: dict[str, Building],
    should_write: bool,
    counts: dict[str, Any],
) -> None:
    canonical_ids = {building.id for building in records.values()}
    candidates = list(
        db.scalars(
            select(Building)
            .where(
                Building.organization_id == organization.id,
                Building.deleted_at.is_(None),
            )
            .order_by(Building.created_at.asc(), Building.name.asc())
        ).all()
    )
    for building in candidates:
        if building.id in canonical_ids:
            continue
        if not is_soho_candidate(building, property_record):
            continue
        counts["buildings_archived"] += 1
        if should_write:
            building.status = "archived"
            building.deleted_at = datetime.now(timezone.utc)
            building.notes = merge_note(building.notes, "Soft-archived by SOHO Phase I Passport loader as duplicate/unclassified legacy record.")


def cleanup_duplicate_properties(db: Session, canonical_property: Property, should_write: bool, counts: dict[str, Any]) -> None:
    duplicate_properties = list(
        db.scalars(
            select(Property)
            .where(
                Property.name == PROPERTY_NAME,
                Property.id != canonical_property.id,
                Property.deleted_at.is_(None),
            )
            .order_by(Property.created_at.asc())
        ).all()
    )
    for property_record in duplicate_properties:
        counts["properties_archived"] = counts.get("properties_archived", 0) + 1
        duplicate_buildings = list(
            db.scalars(
                select(Building).where(
                    Building.property_id == property_record.id,
                    Building.deleted_at.is_(None),
                )
            ).all()
        )
        counts["buildings_archived"] += len(duplicate_buildings)
        if should_write:
            property_record.status = "archived"
            property_record.deleted_at = datetime.now(timezone.utc)
            property_record.notes = merge_note(property_record.notes, "Soft-archived by SOHO Phase I Passport loader as duplicate property.")
            for building in duplicate_buildings:
                building.status = "archived"
                building.deleted_at = datetime.now(timezone.utc)
                building.notes = merge_note(building.notes, "Soft-archived with duplicate SOHO Phase I property.")


def load_documents(
    db: Session,
    property_record: Property,
    building: Building,
    role: str,
    folder: Path,
    should_write: bool,
    counts: dict[str, Any],
) -> None:
    if not folder.exists() or not folder.is_dir():
        counts["blocking_items"].append(f"{folder} is not a readable folder.")
        return
    for file_path in iter_supported_files(folder):
        storage_uri = str(file_path.resolve())
        existing = db.scalar(
            select(Document).where(
                Document.organization_id == building.organization_id,
                Document.building_id == building.id,
                Document.storage_uri == storage_uri,
                Document.deleted_at.is_(None),
            )
        )
        if existing:
            counts["documents_reused"] += 1
            continue
        classification = classify_document(file_path)
        counts["documents_loaded"] += 1
        if not should_write:
            continue
        mime_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
        document = Document(
            organization_id=building.organization_id,
            property_id=property_record.id,
            building_id=building.id,
            name=file_path.stem[:255],
            title=file_path.stem[:255],
            description=f"SOHO Phase I intake file for {SOHO_RECORDS[role]['label']}.",
            document_type=classification["document_type"],
            evidence_category=classification["evidence_category"],
            status="review_required",
            storage_uri=storage_uri,
            storage_bucket="local_soho_intake",
            storage_key=str(file_path.relative_to(folder)),
            original_filename=file_path.name,
            mime_type=mime_type,
            file_mime_type=mime_type,
            file_size_bytes=file_path.stat().st_size,
            is_public_to_client=False,
            is_passport_record=classification["passport_record"],
            internal_only=True,
            extraction_status="review_required",
            extraction_source="soho_phase1_loader",
            extraction_summary={"classification_confidence": classification["confidence"], "source_path": str(folder)},
            notes=SOURCE_TAG,
        )
        db.add(document)
        if building.passport_status in {"Not Started", "Building Registered"}:
            building.passport_status = "Documents Imported"


def reclassify_existing_documents(db: Session, buildings: Iterable[Building], should_write: bool, counts: dict[str, Any]) -> None:
    for building in buildings:
        documents = list(
            db.scalars(
                select(Document).where(
                    Document.organization_id == building.organization_id,
                    Document.building_id == building.id,
                    Document.deleted_at.is_(None),
                    Document.archived_at.is_(None),
                )
            ).all()
        )
        for document in documents:
            classification = classify_document(Path(document.original_filename or document.title or document.name))
            if classification["confidence"] == "review":
                continue
            if document.document_type == classification["document_type"] and document.evidence_category == classification["evidence_category"]:
                continue
            counts["documents_reclassified"] += 1
            if should_write:
                document.document_type = classification["document_type"]
                document.evidence_category = classification["evidence_category"]
                document.is_passport_record = document.is_passport_record or classification["passport_record"]
                document.extraction_status = "review_required"
                document.notes = merge_note(document.notes, "Conservatively reclassified by SOHO Phase I Passport loader.")


def summarize_state(db: Session, buildings: Iterable[Building], counts: dict[str, Any]) -> None:
    complete = 0
    missing = 0
    passport_statuses = set()
    blockers = set(counts["blocking_items"])
    for building in buildings:
        passport_statuses.add(building.passport_status)
        documents = list(
            db.scalars(
                select(Document).where(
                    Document.organization_id == building.organization_id,
                    Document.building_id == building.id,
                    Document.deleted_at.is_(None),
                    Document.archived_at.is_(None),
                )
            ).all()
        )
        suggestions = list(
            db.scalars(
                select(DocumentAssetSuggestion).where(
                    DocumentAssetSuggestion.organization_id == building.organization_id,
                    DocumentAssetSuggestion.building_id == building.id,
                )
            ).all()
        )
        counts["assets_suggested"] += sum(1 for suggestion in suggestions if suggestion.review_status == "review_required")
        counts["assets_approved"] += sum(1 for suggestion in suggestions if suggestion.review_status == "approved")
        categories = {document.evidence_category for document in documents if document.evidence_category}
        for expected in {"as_built_drawings", "material_test_certificates", "asset_register", "owner_property_manager_handover", "itm_transition"}:
            if expected in categories:
                complete += 1
            else:
                missing += 1
                blockers.add(f"{building.name}: {expected} evidence is missing.")
    counts["evidence_categories_complete"] = complete
    counts["evidence_categories_missing"] = missing
    counts["passport_status"] = passport_statuses.pop() if len(passport_statuses) == 1 else "Mixed" if passport_statuses else "Not Started"
    counts["protected_state_status"] = "review_required"
    counts["blocking_items"] = sorted(blockers)


def classify_document(file_path: Path) -> dict[str, str | bool]:
    haystack = file_path.name.lower()
    rules = [
        (("as-built", "as built"), "as_built_drawing", "as_built_drawings", True),
        (("drawing", "shop drawing"), "drawing", "drawing_register", False),
        (("p.eng", "engineer", "engineering"), "engineering_letter", "peng_compliance_package", True),
        (("nfpa", "contractor"), "contractors_material_test_certificate", "nfpa_contractor_compliance_package", True),
        (("material", "test certificate", "sprinkler", "standpipe", "backflow", "fire pump", "alarm verification"), "material_test_certificate", "material_test_certificates", True),
        (("asset", "equipment"), "asset_register", "asset_register", False),
        (("warranty",), "warranty", "warranty_package", True),
        (("manual", "o&m", "operation"), "owner_manual", "product_data_om_manuals", True),
        (("handover", "turnover"), "owner_manual", "owner_property_manager_handover", True),
        (("itm", "inspection testing maintenance", "service transition"), "service_record", "itm_transition", True),
        (("passport",), "passport_export", "building_protection_passport", True),
    ]
    for markers, document_type, evidence_category, passport_record in rules:
        if any(marker in haystack for marker in markers):
            return {
                "document_type": document_type,
                "evidence_category": evidence_category,
                "passport_record": passport_record,
                "confidence": "filename",
            }
    return {
        "document_type": "closeout_document",
        "evidence_category": "review_required",
        "passport_record": False,
        "confidence": "review",
    }


def iter_supported_files(folder: Path) -> Iterable[Path]:
    for file_path in sorted(folder.rglob("*")):
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            yield file_path


def record_notes(role: str) -> str:
    return "\n".join([SOURCE_TAG, f"soho_role={role}", "passport_load_status=production_readiness"])


def merge_note(existing: str | None, note: str) -> str:
    parts = [part for part in [existing, note] if part]
    seen: list[str] = []
    for part in "\n".join(parts).splitlines():
        if part and part not in seen:
            seen.append(part)
    return "\n".join(seen)


def is_soho_candidate(building: Building, property_record: Property) -> bool:
    haystack = " ".join([building.name or "", building.code or "", building.bpid or "", building.notes or ""]).lower()
    return building.property_id == property_record.id or "soho" in haystack or building.code == "5004" or building.bpid == "FPP-5004"


def role_matches_legacy_record(building: Building, role: str) -> bool:
    haystack = " ".join([building.name or "", building.code or "", building.bpid or "", building.notes or ""]).lower()
    if role == "building_a":
        return "soho" in haystack and ("building a" in haystack or "bldg a" in haystack)
    if role == "building_b":
        return "soho" in haystack and ("building b" in haystack or "bldg b" in haystack)
    if role == "shared_fire_protection":
        return "soho" in haystack and ("shared fire" in haystack or "fire protection" in haystack)
    if role == "common_parking_garage":
        return "soho" in haystack and ("parking garage" in haystack or "common infrastructure" in haystack)
    return False


def main() -> None:
    result = load_soho_phase1_passport(parse_args())
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
