from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import MetaData, Table, and_, create_engine, func, insert, or_, select

from app.core.config import settings


@dataclass
class SeedSummary:
    organizations_created: int = 0
    organizations_reused: int = 0
    buildings_created: int = 0
    buildings_reused: int = 0
    contacts_created: int = 0
    contacts_reused: int = 0
    asset_types_created: int = 0
    asset_types_reused: int = 0
    assets_created: int = 0
    assets_reused: int = 0
    documents_created: int = 0
    documents_reused: int = 0
    organization_id: Any | None = None
    building_id: Any | None = None
    bpid: str | None = None


ORGANIZATION = {
    "name": "Fuzion Fire Inc.",
    "email": "reference-portfolio@example.com",
    "website": "https://www.fuzionfire.ca",
    "phone": "905-000-0000",
    "organization_type": "contractor",
    "status": "active",
    "country": "Canada",
    "notes": "Internal FMS reference organization for digital closeout package demos.",
}


BUILDING = {
    "name": "SOHO Phase I / Building A",
    "code": "soho-phase-i-building-a",
    "address_line_1": "505-517 Highland Road West",
    "address_line1": "505-517 Highland Road West",
    "city": "Stoney Creek",
    "province_state": "Ontario",
    "region": "Ontario",
    "postal_code": "L8J 3P2",
    "country": "Canada",
    "building_type": "mixed_use",
    "occupancy_classification": "residential_mixed_use",
    "number_of_storeys": 8,
    "owner_name": "SOHO Reference Owner",
    "property_manager_name": "SOHO Reference Property Management",
    "fire_department": "Hamilton Fire Department",
    "ahj_name": "Stoney Creek Building Department",
    "status": "active",
    "notes": "\n".join(
        [
            "FMS-0027 Digital Closeout Package Generator MVP building.",
            "Property name: SOHO",
            "Address: 505-517 Highland Road West, Stoney Creek, Ontario",
            "Contractor: Fuzion Fire Inc.",
            "Approving authority: Stoney Creek Building Department",
            "Purpose: Demonstrate closeout package evidence grouping, Passport visibility, and handover readiness.",
        ]
    ),
}


CONTACTS = [
    {
        "contact_type": "property_manager",
        "name": "SOHO Property Manager",
        "company": "SOHO Reference Property Management",
        "job_title": "Property Manager",
        "email": "soho.property@example.com",
        "phone": "905-000-4100",
        "is_primary": True,
        "is_emergency_contact": False,
        "notes": "Safe placeholder contact for FMS-0027 closeout handover.",
    },
    {
        "contact_type": "contractor",
        "name": "Fuzion Fire Closeout Coordinator",
        "company": "Fuzion Fire Inc.",
        "job_title": "Closeout Coordinator",
        "email": "soho.closeout@example.com",
        "phone": "905-000-4200",
        "is_primary": False,
        "is_emergency_contact": False,
        "notes": "Safe placeholder internal closeout contact.",
    },
    {
        "contact_type": "ahj",
        "name": "Stoney Creek Building Department",
        "company": "Stoney Creek Building Department",
        "job_title": "Approving Authority",
        "email": "stoneycreek.ahj@example.com",
        "phone": "905-000-4300",
        "is_primary": False,
        "is_emergency_contact": False,
        "notes": "Safe placeholder approving authority contact.",
    },
]


ASSET_TYPES = {
    "wet_sprinkler_system": ("Wet Sprinkler System", "sprinkler"),
    "dry_sprinkler_system": ("Dry Sprinkler System", "sprinkler"),
    "standpipe_system": ("Standpipe System", "standpipe"),
    "fire_department_connection": ("Fire Department Connection", "water_supply"),
    "fire_alarm_control_panel": ("Fire Alarm Control Panel", "fire_alarm"),
    "garbage_chute_sprinkler": ("Garbage Chute Sprinkler", "sprinkler"),
}


ASSETS = [
    ("Building A Wet Sprinkler System", "wet_sprinkler_system", "Ground floor through MPH"),
    ("Parking Level Dry Sprinkler System", "dry_sprinkler_system", "P1 east and west parking areas"),
    ("Combined Sprinkler / Standpipe System", "standpipe_system", "Building A stair and riser network"),
    ("Garbage Chute Sprinkler System", "garbage_chute_sprinkler", "Building A and Building B garbage chutes"),
    ("Fire Department Connection", "fire_department_connection", "Highland Road West exterior"),
    ("Fire Alarm Interface", "fire_alarm_control_panel", "Main electrical/service room"),
]


CLOSEOUT_SECTIONS = [
    "Building Protection Passport",
    "P.Eng. Compliance Package",
    "NFPA Contractor Compliance Package",
    "Material & Test Certificates",
    "Drawing Register",
    "As-Built Drawings",
    "Asset Register",
    "Warranty Package",
    "Product Data / O&M Manuals",
    "Owner / Property Manager Handover",
    "Fuzion Fire Service ITM Transition",
    "FMS Membership Invitation",
]


CERTIFICATE_RECORDS = [
    "BLD A Ground Floor Wet",
    "BLD A 2nd Floor Wet",
    "BLD A 3rd Floor Wet",
    "BLD A 4th Floor Wet",
    "BLD A 5th Floor Wet",
    "BLD A 6th Floor Wet",
    "BLD A 7th Floor Wet",
    "BLD A 8th Floor Wet",
    "BLD A MPH Wet",
    "BLD A Garbage Chute",
    "BLD B Garbage Chute",
    "BLD B MPH Wet",
    "Dry Ground Floor Amenity",
    "Dry P1 East",
    "Dry P1 West",
    "Dry P1 Standpipe",
    "Wet Combined Sprinkler / Standpipe",
]


SUPPORTING_DOCUMENTS = [
    ("SOHO Building Protection Passport Index", "passport_export", "Building Protection Passport", "Curated Passport index for client handover."),
    ("P.Eng. Compliance Cover Sheet", "engineering_letter", "P.Eng. Compliance Package", "Engineering compliance evidence placeholder."),
    ("NFPA Contractor Closeout Checklist", "other", "NFPA Contractor Compliance Package", "NFPA contractor closeout checklist metadata."),
    ("SOHO Drawing Register", "drawing", "Drawing Register", "Drawing register for closeout evidence review."),
    ("SOHO Building A As-Built Drawing Package", "as_built_drawing", "As-Built Drawings", "As-built drawing package metadata."),
    ("SOHO Building A Asset Register", "other", "Asset Register", "Asset register derived from seeded fire protection assets."),
    ("SOHO Warranty Summary", "warranty", "Warranty Package", "Warranty package metadata for installed fire protection systems."),
    ("SOHO Product Data and O&M Manual Index", "owner_manual", "Product Data / O&M Manuals", "Product and O&M manual index metadata."),
    ("SOHO Owner / Property Manager Handover Notes", "owner_manual", "Owner / Property Manager Handover", "Owner handover meeting and transition notes."),
    ("SOHO Fuzion Fire Service ITM Transition Summary", "service_record", "Fuzion Fire Service ITM Transition", "ITM transition summary for Fuzion Fire Service."),
    ("SOHO FMS Membership Invitation", "other", "FMS Membership Invitation", "FMS membership invitation and Passport value summary."),
]


def payload_for(table: Table, payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if key in table.c}


def first_id(connection, table: Table, *criteria):
    row = connection.execute(select(table.c.id).where(*criteria).limit(1)).first()
    return row[0] if row else None


def find_building_id(connection, buildings: Table, organization_id, names: list[str], addresses: list[str]):
    criteria = [buildings.c.organization_id == organization_id]
    if "deleted_at" in buildings.c:
        criteria.append(buildings.c.deleted_at.is_(None))

    match_criteria = []
    if names:
        match_criteria.append(buildings.c.name.in_(names))
    if "address_line_1" in buildings.c and addresses:
        match_criteria.append(and_(buildings.c.address_line_1.in_(addresses), buildings.c.name.in_(names)))
    if "address_line1" in buildings.c and addresses:
        match_criteria.append(and_(buildings.c.address_line1.in_(addresses), buildings.c.name.in_(names)))
    if not match_criteria:
        return None

    row = connection.execute(
        select(buildings.c.id)
        .where(*criteria, or_(*match_criteria))
        .order_by(buildings.c.created_at if "created_at" in buildings.c else buildings.c.id)
        .limit(1)
    ).first()
    return row[0] if row else None


def generate_bpid(connection, buildings: Table) -> str:
    if "bpid" not in buildings.c:
        return ""
    max_bpid = connection.execute(select(func.max(buildings.c.bpid)).where(buildings.c.bpid.like("FMS-BLDG-%"))).scalar()
    if not max_bpid:
        return "FMS-BLDG-000001"
    return f"FMS-BLDG-{int(str(max_bpid).rsplit('-', 1)[1]) + 1:06d}"


def insert_row(connection, table: Table, payload: dict[str, Any]):
    result = connection.execute(insert(table).values(**payload_for(table, payload)).returning(table.c.id))
    return result.scalar_one()


def ensure_schema(metadata: MetaData) -> None:
    required = {"organizations", "buildings", "building_contacts", "asset_types", "assets", "documents"}
    missing = sorted(required - set(metadata.tables))
    if missing:
        raise RuntimeError(
            "FMS-0027 SOHO closeout seed requires existing MVP database tables. Missing: "
            + ", ".join(missing)
            + ". Run the current database migrations before this seed script."
        )


def safe_slug(value: str) -> str:
    return "".join(character.lower() if character.isalnum() else "-" for character in value).strip("-")


def closeout_description(section: str, evidence_purpose: str, system_location: str) -> str:
    return "\n".join(
        [
            "FMS-0027 Closeout Package Evidence",
            f"Closeout section: {section}",
            f"System/location: {system_location}",
            "Property name: SOHO",
            "Address: 505-517 Highland Road West, Stoney Creek, Ontario",
            "Contractor: Fuzion Fire Inc.",
            "Approving authority: Stoney Creek Building Department",
            f"Evidence purpose: {evidence_purpose}",
            "Client visible: true",
            "Passport record: true",
        ]
    )


def seed_soho_closeout_package() -> SeedSummary:
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    metadata = MetaData()
    metadata.reflect(bind=engine)
    ensure_schema(metadata)

    organizations = metadata.tables["organizations"]
    buildings = metadata.tables["buildings"]
    contacts = metadata.tables["building_contacts"]
    asset_types = metadata.tables["asset_types"]
    assets = metadata.tables["assets"]
    documents = metadata.tables["documents"]
    summary = SeedSummary()

    with engine.begin() as connection:
        organization_id = first_id(connection, organizations, organizations.c.name == ORGANIZATION["name"])
        if organization_id:
            summary.organizations_reused += 1
        else:
            organization_id = insert_row(connection, organizations, ORGANIZATION)
            summary.organizations_created += 1
        summary.organization_id = organization_id

        building_criteria = [buildings.c.organization_id == organization_id]
        if "deleted_at" in buildings.c:
            building_criteria.append(buildings.c.deleted_at.is_(None))
        if "code" in buildings.c:
            building_id = first_id(connection, buildings, *building_criteria, buildings.c.code == BUILDING["code"])
        else:
            building_id = None
        if not building_id:
            building_id = find_building_id(
                connection,
                buildings,
                organization_id,
                [BUILDING["name"], "SOHO Phase I Building A", "SOHO Phase 1 Building A"],
                [BUILDING["address_line_1"], BUILDING["address_line1"]],
            )

        if building_id:
            summary.buildings_reused += 1
            if "bpid" in buildings.c:
                summary.bpid = connection.execute(select(buildings.c.bpid).where(buildings.c.id == building_id)).scalar()
        else:
            building_payload = {**BUILDING, "organization_id": organization_id}
            if "bpid" in buildings.c:
                building_payload["bpid"] = generate_bpid(connection, buildings)
            building_id = insert_row(connection, buildings, building_payload)
            summary.buildings_created += 1
            summary.bpid = building_payload.get("bpid")
        summary.building_id = building_id

        for contact_payload in CONTACTS:
            contact_id = first_id(
                connection,
                contacts,
                contacts.c.organization_id == organization_id,
                contacts.c.building_id == building_id,
                contacts.c.email == contact_payload["email"],
            )
            if contact_id:
                summary.contacts_reused += 1
            else:
                insert_row(connection, contacts, {**contact_payload, "organization_id": organization_id, "building_id": building_id})
                summary.contacts_created += 1

        asset_type_ids = {}
        for code, (name, category) in ASSET_TYPES.items():
            asset_type_id = first_id(connection, asset_types, asset_types.c.code == code)
            if asset_type_id:
                summary.asset_types_reused += 1
            else:
                asset_type_id = insert_row(connection, asset_types, {"organization_id": None, "code": code, "name": name, "category": category})
                summary.asset_types_created += 1
            asset_type_ids[code] = asset_type_id

        for name, type_code, location in ASSETS:
            asset_id = first_id(
                connection,
                assets,
                assets.c.organization_id == organization_id,
                assets.c.building_id == building_id,
                assets.c.name == name,
            )
            if asset_id:
                summary.assets_reused += 1
            else:
                tag = f"SOHO-A-{safe_slug(name)[:32]}"
                insert_row(
                    connection,
                    assets,
                    {
                        "organization_id": organization_id,
                        "building_id": building_id,
                        "asset_type_id": asset_type_ids[type_code],
                        "name": name,
                        "tag": tag,
                        "asset_tag": tag,
                        "location_description": location,
                        "status": "active",
                        "condition_rating": "good",
                        "inspection_frequency_months": 12,
                        "notes": "FMS-0027 representative closeout asset for SOHO Building A.",
                    },
                )
                summary.assets_created += 1

        for title, document_type, section, evidence_purpose in SUPPORTING_DOCUMENTS:
            ensure_document(connection, documents, organization_id, building_id, title, document_type, section, evidence_purpose, section, summary)

        for title in CERTIFICATE_RECORDS:
            ensure_document(
                connection,
                documents,
                organization_id,
                building_id,
                title,
                "contractors_material_test_certificate",
                "Material & Test Certificates",
                "Material and test certificate evidence for closeout, Passport, and owner handover.",
                title,
                summary,
            )

    return summary


def ensure_document(
    connection,
    documents: Table,
    organization_id,
    building_id,
    title: str,
    document_type: str,
    section: str,
    evidence_purpose: str,
    system_location: str,
    summary: SeedSummary,
) -> None:
    document_id = first_id(
        connection,
        documents,
        documents.c.organization_id == organization_id,
        documents.c.building_id == building_id,
        documents.c.name == title,
    )
    if document_id:
        summary.documents_reused += 1
        return

    filename = f"{safe_slug(title)}.txt"
    storage_key = f"soho-closeout/{filename}"
    insert_row(
        connection,
        documents,
        {
            "organization_id": organization_id,
            "building_id": building_id,
            "name": title,
            "title": title,
            "description": closeout_description(section, evidence_purpose, system_location),
            "document_type": document_type,
            "storage_uri": f"local://{storage_key}",
            "storage_bucket": "fms-local-documents",
            "storage_key": storage_key,
            "original_filename": filename,
            "mime_type": "text/plain",
            "file_mime_type": "text/plain",
            "file_size_bytes": 0,
            "version_number": 1,
            "generated_by_system": False,
            "is_public_to_client": True,
            "is_passport_record": True,
        },
    )
    summary.documents_created += 1


def print_summary(summary: SeedSummary) -> None:
    print("FMS-0027 SOHO closeout package seed complete")
    print(f"Organization ID: {summary.organization_id}")
    print(f"Building ID: {summary.building_id}")
    print(f"BPID: {summary.bpid or 'not available in current schema'}")
    for key, value in summary.__dict__.items():
        if key not in {"organization_id", "building_id", "bpid"}:
            print(f"{key}: {value}")


if __name__ == "__main__":
    print_summary(seed_soho_closeout_package())
