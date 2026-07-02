from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import MetaData, Table, create_engine, func, insert, or_, select

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
    "email": "info@fuzionfire.ca",
    "website": "https://www.fuzionfire.ca",
    "phone": "905-000-0000",
    "organization_type": "contractor",
    "status": "active",
}

BUILDING = {
    "name": "Linhaven LTC",
    "address_line_1": "403 Ontario Street",
    "address_line1": "403 Ontario Street",
    "city": "St. Catharines",
    "province_state": "ON",
    "region": "ON",
    "country": "Canada",
    "building_type": "long_term_care",
    "occupancy_classification": "care_occupancy",
    "number_of_storeys": 5,
    "status": "active",
    "property_manager_name": "Demo Property Management",
    "fire_department": "St. Catharines Fire Services",
    "notes": "\n".join(
        [
            "Common Name: Linhaven Long-Term Care Home",
            "General Contractor: Buttcon Limited",
            "Fire Protection Contractor: Fuzion Fire Inc.",
            "Sprinkler Standard: NFPA 13 2019",
            "Standpipe Standard: NFPA 14",
            "Fire Extinguisher Standard: NFPA 10",
            "Basement: true",
            "Storeys Above Grade: 5",
            "Mechanical Penthouse: true",
            "Fully Sprinklered: true",
            "First real FMS demo building used to demonstrate the Building Protection Passport.",
        ]
    ),
}

CONTACTS = [
    {
        "contact_type": "property_manager",
        "name": "Sarah Mitchell",
        "company": "Demo Property Management",
        "email": "sarah.mitchell@example.com",
        "phone": "905-000-2000",
        "is_primary": True,
        "is_emergency_contact": True,
    },
    {
        "contact_type": "site_contact",
        "name": "Michael Thompson",
        "company": "Linhaven Long-Term Care",
        "email": "maintenance@example.com",
        "phone": "905-000-3000",
        "is_primary": False,
        "is_emergency_contact": True,
    },
    {
        "contact_type": "ahj",
        "name": "Fire Prevention Office",
        "company": "St. Catharines Fire Services",
        "email": "fireprevention@example.com",
        "phone": "905-000-4000",
        "is_primary": False,
        "is_emergency_contact": False,
    },
]

ASSET_TYPES = {
    "wet_sprinkler_system": ("Wet Sprinkler System", "sprinkler"),
    "standpipe_system": ("Standpipe System", "standpipe"),
    "fire_department_connection": ("Fire Department Connection", "water_supply"),
    "fire_pump": ("Fire Pump", "fire_pump"),
    "backflow_preventer": ("Backflow Preventer", "backflow"),
    "control_valve": ("Control Valve", "valve"),
}

ASSETS = [
    ("Wet Sprinkler System - Floors 1-5", "wet_sprinkler_system", "Building-wide"),
    ("Class III Standpipe System", "standpipe_system", "Stairwells"),
    ("Fire Department Connection", "fire_department_connection", "Exterior"),
    ("Fire Pump", "fire_pump", "Fire Pump Room"),
    ("Backflow Preventer", "backflow_preventer", "Fire Pump Room"),
    ("Main Control Valve", "control_valve", "Fire Pump Room"),
]

DOCUMENTS = [
    ("Linhaven Sprinkler Drawing Package", "shop_drawing", "Approved sprinkler drawing package for Linhaven LTC."),
    ("Riser Diagram", "shop_drawing", "Fire protection riser diagram extracted from sprinkler drawing package."),
    ("Basement Sprinkler Plan", "shop_drawing", None),
    ("Ground Floor Sprinkler Plan", "shop_drawing", None),
    ("Second Floor Sprinkler Plan", "shop_drawing", None),
    ("Third Floor Sprinkler Plan", "shop_drawing", None),
    ("Fourth Floor Sprinkler Plan", "shop_drawing", None),
    ("Fifth Floor Sprinkler Plan", "shop_drawing", None),
    ("Mechanical Penthouse Sprinkler Plan", "shop_drawing", None),
    ("Contractor's Material and Test Certificate", "contractors_material_test_certificate", None),
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
        match_criteria.append(buildings.c.address_line_1.in_(addresses))
    if "address_line1" in buildings.c and addresses:
        match_criteria.append(buildings.c.address_line1.in_(addresses))
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
            "Linhaven seed requires MVP database tables. Missing: "
            + ", ".join(missing)
            + ". Run the database model/migration phases before this seed script."
        )


def seed_linhaven() -> SeedSummary:
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

        building_id = find_building_id(
            connection,
            buildings,
            organization_id,
            ["Linhaven LTC", "Linhaven Long-Term Care"],
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

        summary.organization_id = organization_id
        summary.building_id = building_id

        for contact_payload in CONTACTS:
            contact_id = first_id(
                connection,
                contacts,
                contacts.c.organization_id == organization_id,
                contacts.c.building_id == building_id,
                contacts.c.name == contact_payload["name"],
            )
            if contact_id:
                summary.contacts_reused += 1
                continue
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
                continue
            insert_row(
                connection,
                assets,
                {
                    "organization_id": organization_id,
                    "building_id": building_id,
                    "asset_type_id": asset_type_ids[type_code],
                    "name": name,
                    "location_description": location,
                    "status": "active",
                    "condition_rating": "good",
                },
            )
            summary.assets_created += 1

        for title, document_type, description in DOCUMENTS:
            document_id = first_id(
                connection,
                documents,
                documents.c.organization_id == organization_id,
                documents.c.building_id == building_id,
                documents.c.name == title,
            )
            if document_id:
                summary.documents_reused += 1
                continue
            filename = f"{title.lower().replace(' ', '-')}.txt"
            insert_row(
                connection,
                documents,
                {
                    "organization_id": organization_id,
                    "building_id": building_id,
                    "name": title,
                    "title": title,
                    "description": description,
                    "document_type": document_type,
                    "storage_uri": f"local://linhaven/{filename}",
                    "storage_bucket": "fms-local-documents",
                    "storage_key": f"linhaven/{filename}",
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

    return summary


def print_summary(summary: SeedSummary) -> None:
    print("Linhaven seed complete")
    print(f"Organization ID: {summary.organization_id}")
    print(f"Building ID: {summary.building_id}")
    print(f"BPID: {summary.bpid or 'not available in current schema'}")
    for key, value in summary.__dict__.items():
        if key not in {"organization_id", "building_id", "bpid"}:
            print(f"{key}: {value}")


if __name__ == "__main__":
    print_summary(seed_linhaven())
