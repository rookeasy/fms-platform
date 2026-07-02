from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from typing import Any

from sqlalchemy import MetaData, Table, and_, create_engine, func, insert, or_, select, update

from app.core.config import settings


ORGANIZATION_NAME = "Fuzion Fire Inc."
SOHO_ADDRESS = "505-517 Highland Road West"
SOHO_CITY = "Stoney Creek"
SOHO_PROVINCE = "Ontario"
SOHO_POSTAL_CODE = "L8J 3P2"

PROPERTY = {
    "name": "SOHO Phase I",
    "property_type": "multi_building_residential_development",
    "status": "active",
    "address_line_1": SOHO_ADDRESS,
    "city": SOHO_CITY,
    "province_state": SOHO_PROVINCE,
    "postal_code": SOHO_POSTAL_CODE,
    "country": "Canada",
    "owner_name": "SOHO Reference Owner",
    "property_manager_name": "SOHO Reference Property Management",
    "notes": "M6 reference property/campus for SOHO Phase I Building A, Building B, and shared parking/fire protection infrastructure.",
}

CAMPUS = {
    "name": "SOHO Phase I Property / Campus",
    "campus_type": "campus",
    "status": "active",
    "address_line_1": SOHO_ADDRESS,
    "city": SOHO_CITY,
    "province_state": SOHO_PROVINCE,
    "postal_code": SOHO_POSTAL_CODE,
    "country": "Canada",
    "notes": "M6 campus grouping for SOHO Phase I closeout and Building Protection Passport workflows.",
}

BUILDING_A_ALIASES = [
    "SOHO Phase I / Building A",
    "SOHO Phase I Building A",
    "SOHO Phase 1 Building A",
    "SOHO Phase I - Building A",
    "SOHO Phase 1 - Building A",
]

BUILDING_A = {
    "name": "SOHO Phase I / Building A",
    "code": "soho-phase-i-building-a",
    "address_line_1": SOHO_ADDRESS,
    "address_line1": SOHO_ADDRESS,
    "city": SOHO_CITY,
    "province_state": SOHO_PROVINCE,
    "region": SOHO_PROVINCE,
    "postal_code": SOHO_POSTAL_CODE,
    "country": "Canada",
    "building_type": "mixed_use",
    "occupancy_classification": "residential_mixed_use",
    "number_of_storeys": 8,
    "owner_name": "SOHO Reference Owner",
    "property_manager_name": "SOHO Reference Property Management",
    "fire_department": "Hamilton Fire Department",
    "ahj_name": "Stoney Creek Building Department",
    "status": "active",
    "notes": "Canonical Building Protection Passport for SOHO Phase I Building A.",
}

BUILDING_B = {
    "name": "SOHO Phase I / Building B",
    "code": "soho-phase-i-building-b",
    "address_line_1": SOHO_ADDRESS,
    "address_line1": SOHO_ADDRESS,
    "city": SOHO_CITY,
    "province_state": SOHO_PROVINCE,
    "region": SOHO_PROVINCE,
    "postal_code": SOHO_POSTAL_CODE,
    "country": "Canada",
    "building_type": "mixed_use",
    "occupancy_classification": "residential_mixed_use",
    "number_of_storeys": 8,
    "owner_name": "SOHO Reference Owner",
    "property_manager_name": "SOHO Reference Property Management",
    "fire_department": "Hamilton Fire Department",
    "ahj_name": "Stoney Creek Building Department",
    "status": "active",
    "notes": "M6 Building Protection Passport record for SOHO Phase I Building B.",
}

COMMON_INFRASTRUCTURE = {
    "name": "Common Parking Garage / Shared Fire Protection Infrastructure",
    "code": "soho-phase-i-common-infrastructure",
    "address_line_1": SOHO_ADDRESS,
    "address_line1": SOHO_ADDRESS,
    "city": SOHO_CITY,
    "province_state": SOHO_PROVINCE,
    "region": SOHO_PROVINCE,
    "postal_code": SOHO_POSTAL_CODE,
    "country": "Canada",
    "building_type": "shared_infrastructure",
    "occupancy_classification": "parking_shared_infrastructure",
    "owner_name": "SOHO Reference Owner",
    "property_manager_name": "SOHO Reference Property Management",
    "fire_department": "Hamilton Fire Department",
    "ahj_name": "Stoney Creek Building Department",
    "status": "active",
    "notes": "M6 shared infrastructure Passport record for SOHO Phase I parking garage, dry systems, and common fire protection evidence.",
}

BUILDING_A_DOCUMENTS = {
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
}

BUILDING_B_DOCUMENTS = {
    "BLD B Garbage Chute",
    "BLD B MPH Wet",
}

COMMON_DOCUMENTS = {
    "Dry Ground Floor Amenity",
    "Dry P1 East",
    "Dry P1 West",
    "Dry P1 Standpipe",
    "Wet Combined Sprinkler / Standpipe",
}

BUILDING_A_ASSETS = {
    "Building A Wet Sprinkler System",
}

COMMON_ASSETS = {
    "Parking Level Dry Sprinkler System",
    "Combined Sprinkler / Standpipe System",
    "Garbage Chute Sprinkler System",
    "Fire Department Connection",
    "Fire Alarm Interface",
}


@dataclass
class CleanupSummary:
    organizations_created: int = 0
    organizations_reused: int = 0
    properties_created: int = 0
    properties_reused: int = 0
    campuses_created: int = 0
    campuses_reused: int = 0
    buildings_created: int = 0
    buildings_reused: int = 0
    buildings_archived: int = 0
    asset_types_created: int = 0
    asset_types_reused: int = 0
    assets_created: int = 0
    assets_reused: int = 0
    documents_created: int = 0
    documents_reused: int = 0
    documents_reassigned: int = 0
    assets_reassigned: int = 0
    duplicates_archived: int = 0
    organization_id: Any | None = None
    property_id: Any | None = None
    campus_id: Any | None = None
    building_a_id: Any | None = None
    building_b_id: Any | None = None
    common_infrastructure_id: Any | None = None


ASSET_TYPES = {
    "wet_sprinkler_system": ("Wet Sprinkler System", "sprinkler"),
    "dry_sprinkler_system": ("Dry Sprinkler System", "sprinkler"),
    "standpipe_system": ("Standpipe System", "standpipe"),
    "fire_pump": ("Fire Pump", "water_supply"),
    "jockey_pump": ("Jockey Pump", "water_supply"),
    "backflow_preventer": ("Backflow Preventer", "water_supply"),
    "fire_department_connection": ("Fire Department Connection", "water_supply"),
    "underground_fire_main": ("Underground Fire Main", "water_supply"),
    "garbage_chute_sprinkler": ("Garbage Chute Sprinkler", "sprinkler"),
}

SEEDED_ASSETS = {
    "building_a": [
        ("Building A Wet Sprinkler System", "wet_sprinkler_system", "Building A riser and floor wet systems"),
        ("Building A Garbage Chute Sprinkler System", "garbage_chute_sprinkler", "Building A garbage chute"),
        ("Building A Mechanical Penthouse Wet System", "wet_sprinkler_system", "Building A mechanical penthouse"),
        ("Building A Floor Wet Systems", "wet_sprinkler_system", "Building A ground floor through level 8"),
    ],
    "building_b": [
        ("Building B Wet Sprinkler System", "wet_sprinkler_system", "Building B riser and floor wet systems"),
        ("Building B Garbage Chute Sprinkler System", "garbage_chute_sprinkler", "Building B garbage chute"),
        ("Building B Mechanical Penthouse Wet System", "wet_sprinkler_system", "Building B mechanical penthouse"),
    ],
    "common": [
        ("Fire Pump", "fire_pump", "Common fire pump room"),
        ("Jockey Pump", "jockey_pump", "Common fire pump room"),
        ("6 inch Backflow Preventer", "backflow_preventer", "Incoming fire service"),
        ("Fire Department Connection", "fire_department_connection", "Highland Road West exterior"),
        ("Common Standpipe System", "standpipe_system", "Shared standpipe infrastructure"),
        ("Dry Parking Garage System", "dry_sprinkler_system", "Common parking garage"),
        ("Underground Fire Main", "underground_fire_main", "SOHO Phase I site service"),
    ],
}

SEEDED_DOCUMENTS = {
    "building_a": [(title, "contractors_material_test_certificate", title) for title in sorted(BUILDING_A_DOCUMENTS)],
    "building_b": [(title, "contractors_material_test_certificate", title) for title in sorted(BUILDING_B_DOCUMENTS)],
    "common": [(title, "contractors_material_test_certificate", title) for title in sorted(COMMON_DOCUMENTS)],
}


def payload_for(table: Table, payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if key in table.c}


def first_id(connection, table: Table, *criteria):
    row = connection.execute(select(table.c.id).where(*criteria).limit(1)).first()
    return row[0] if row else None


def insert_row(connection, table: Table, payload: dict[str, Any]):
    result = connection.execute(insert(table).values(**payload_for(table, payload)).returning(table.c.id))
    return result.scalar_one()


def active_criteria(table: Table) -> list[Any]:
    if "deleted_at" not in table.c:
        return []
    return [table.c.deleted_at.is_(None)]


def generate_bpid(connection, buildings: Table) -> str:
    if "bpid" not in buildings.c:
        return ""
    existing = connection.execute(select(buildings.c.bpid).where(buildings.c.bpid.like("FMS-BLDG-%"))).scalars().all()
    numbers = [bpid_number(value) for value in existing]
    return f"FMS-BLDG-{(max(numbers) if numbers else 0) + 1:06d}"


def bpid_number(value: Any) -> int:
    match = re.search(r"(\d+)$", str(value or ""))
    return int(match.group(1)) if match else 999999999


def ensure_schema(metadata: MetaData) -> None:
    required = {"organizations", "properties", "campuses", "buildings", "asset_types", "assets", "documents"}
    missing = sorted(required - set(metadata.tables))
    if missing:
        raise RuntimeError(
            "M6 SOHO Phase I cleanup requires the current property/campus database tables. Missing: "
            + ", ".join(missing)
            + ". Run alembic upgrade head before this cleanup."
        )


def safe_slug(value: str) -> str:
    return "".join(character.lower() if character.isalnum() else "-" for character in value).strip("-")


def ensure_organization(connection, organizations: Table, summary: CleanupSummary):
    organization_id = first_id(connection, organizations, organizations.c.name == ORGANIZATION_NAME)
    if organization_id:
        summary.organizations_reused += 1
        values = payload_for(organizations, {"status": "active", "deleted_at": None})
        if values:
            connection.execute(update(organizations).where(organizations.c.id == organization_id).values(**values))
    else:
        organization_id = insert_row(
            connection,
            organizations,
            {
                "name": ORGANIZATION_NAME,
                "email": "reference-portfolio@example.com",
                "website": "https://www.fuzionfire.ca",
                "phone": "905-000-0000",
                "organization_type": "contractor",
                "status": "active",
                "country": "Canada",
                "notes": "Internal FMS reference organization for property, campus, and Passport demo data.",
            },
        )
        summary.organizations_created += 1
    summary.organization_id = organization_id
    return organization_id


def ensure_property(connection, properties: Table, organization_id, summary: CleanupSummary):
    match = first_id(
        connection,
        properties,
        properties.c.organization_id == organization_id,
        or_(properties.c.name == PROPERTY["name"], properties.c.address_line_1 == SOHO_ADDRESS),
    )
    if match:
        summary.properties_reused += 1
        property_id = match
        values = payload_for(properties, {"status": "active", "deleted_at": None})
        if values:
            connection.execute(update(properties).where(properties.c.id == property_id).values(**values))
    else:
        property_id = insert_row(connection, properties, {**PROPERTY, "organization_id": organization_id})
        summary.properties_created += 1
    summary.property_id = property_id
    return property_id


def ensure_campus(connection, campuses: Table, organization_id, property_id, summary: CleanupSummary):
    match = first_id(
        connection,
        campuses,
        campuses.c.organization_id == organization_id,
        or_(campuses.c.name == CAMPUS["name"], campuses.c.address_line_1 == SOHO_ADDRESS),
    )
    if match:
        summary.campuses_reused += 1
        campus_id = match
        values = payload_for(campuses, {"property_id": property_id, "status": "active", "deleted_at": None})
        if values:
            connection.execute(update(campuses).where(campuses.c.id == campus_id).values(**values))
    else:
        campus_id = insert_row(connection, campuses, {**CAMPUS, "organization_id": organization_id, "property_id": property_id})
        summary.campuses_created += 1
    summary.campus_id = campus_id
    return campus_id


def building_a_duplicate_rows(connection, buildings: Table, organization_id) -> list[Any]:
    criteria = [
        buildings.c.organization_id == organization_id,
        *active_criteria(buildings),
    ]
    matches = []
    if "code" in buildings.c:
        matches.append(buildings.c.code == BUILDING_A["code"])
    matches.append(buildings.c.name.in_(BUILDING_A_ALIASES))
    if "address_line_1" in buildings.c:
        matches.append(and_(buildings.c.address_line_1 == SOHO_ADDRESS, func.lower(buildings.c.name).like("%building a%")))
    if "address_line1" in buildings.c:
        matches.append(and_(buildings.c.address_line1 == SOHO_ADDRESS, func.lower(buildings.c.name).like("%building a%")))

    rows = connection.execute(select(buildings).where(*criteria, or_(*matches))).all()
    return [row._mapping for row in rows]


def canonical_building_a(connection, buildings: Table, organization_id, property_id, campus_id, summary: CleanupSummary):
    rows = building_a_duplicate_rows(connection, buildings, organization_id)
    if rows:
        rows.sort(key=lambda row: (bpid_number(row.get("bpid")), str(row.get("created_at") or ""), str(row["id"])))
        canonical = rows[0]
        building_a_id = canonical["id"]
        summary.buildings_reused += 1
    else:
        payload = {**BUILDING_A, "organization_id": organization_id, "property_id": property_id, "campus_id": campus_id}
        if "bpid" in buildings.c:
            payload["bpid"] = generate_bpid(connection, buildings)
        building_a_id = insert_row(connection, buildings, payload)
        rows = []
        summary.buildings_created += 1

    update_building_assignment(connection, buildings, building_a_id, property_id, campus_id)

    duplicate_ids = []
    for row in rows:
        if row["id"] != building_a_id:
            duplicate_ids.append(row["id"])
    summary.building_a_id = building_a_id
    return building_a_id, duplicate_ids


def find_building_by_code_or_name(connection, buildings: Table, organization_id, payload: dict[str, Any]):
    criteria = [
        buildings.c.organization_id == organization_id,
    ]
    matches = [buildings.c.name == payload["name"]]
    if "code" in buildings.c:
        matches.append(buildings.c.code == payload["code"])
    return first_id(connection, buildings, *criteria, or_(*matches))


def ensure_building(connection, buildings: Table, organization_id, property_id, campus_id, payload: dict[str, Any], summary: CleanupSummary):
    building_id = find_building_by_code_or_name(connection, buildings, organization_id, payload)
    if building_id:
        summary.buildings_reused += 1
    else:
        create_payload = {**payload, "organization_id": organization_id, "property_id": property_id, "campus_id": campus_id}
        if "bpid" in buildings.c:
            create_payload["bpid"] = generate_bpid(connection, buildings)
        building_id = insert_row(connection, buildings, create_payload)
        summary.buildings_created += 1
    update_building_assignment(connection, buildings, building_id, property_id, campus_id)
    return building_id


def update_building_assignment(connection, buildings: Table, building_id, property_id, campus_id) -> None:
    values = payload_for(buildings, {"property_id": property_id, "campus_id": campus_id, "status": "active", "deleted_at": None})
    if values:
        connection.execute(update(buildings).where(buildings.c.id == building_id).values(**values))


def archive_duplicates(connection, buildings: Table, duplicate_ids: list[Any], summary: CleanupSummary) -> None:
    if not duplicate_ids:
        return
    values = payload_for(buildings, {"status": "archived", "deleted_at": func.now()})
    if not values:
        return
    result = connection.execute(update(buildings).where(buildings.c.id.in_(duplicate_ids)).values(**values))
    archived = result.rowcount or 0
    summary.buildings_archived += archived
    summary.duplicates_archived += archived


def ensure_asset_types(connection, asset_types: Table, summary: CleanupSummary) -> dict[str, Any]:
    asset_type_ids = {}
    for code, (name, category) in ASSET_TYPES.items():
        asset_type_id = first_id(connection, asset_types, asset_types.c.code == code, *active_criteria(asset_types))
        if asset_type_id:
            summary.asset_types_reused += 1
        else:
            asset_type_id = insert_row(
                connection,
                asset_types,
                {
                    "organization_id": None,
                    "code": code,
                    "name": name,
                    "category": category,
                    "description": f"M6 SOHO Phase I {name.lower()} asset type.",
                },
            )
            summary.asset_types_created += 1
        asset_type_ids[code] = asset_type_id
    return asset_type_ids


def ensure_seeded_assets(connection, assets: Table, organization_id, building_id, assets_to_seed: list[tuple[str, str, str]], asset_type_ids: dict[str, Any], summary: CleanupSummary) -> None:
    for name, type_code, location in assets_to_seed:
        asset_id = first_id(
            connection,
            assets,
            assets.c.organization_id == organization_id,
            assets.c.building_id == building_id,
            assets.c.name == name,
            *active_criteria(assets),
        )
        if asset_id:
            summary.assets_reused += 1
            continue

        tag = f"SOHO-{safe_slug(name)[:42]}"
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
                "notes": "M6 SOHO Phase I property/campus seed asset.",
            },
        )
        summary.assets_created += 1


def document_description(title: str, evidence_scope: str) -> str:
    return "\n".join(
        [
            "M6 SOHO Phase I Property/Campus Evidence",
            f"Evidence scope: {evidence_scope}",
            f"System/location: {title}",
            "Property name: SOHO Phase I",
            "Address: 505-517 Highland Road West, Stoney Creek, Ontario",
            "Contractor: Fuzion Fire Inc.",
            "Approving authority: Stoney Creek Building Department",
            "Client visible: true",
            "Passport record: true",
        ]
    )


def ensure_seeded_documents(connection, documents: Table, organization_id, building_id, documents_to_seed: list[tuple[str, str, str]], evidence_scope: str, summary: CleanupSummary) -> None:
    for title, document_type, location in documents_to_seed:
        document_id = first_id(
            connection,
            documents,
            documents.c.organization_id == organization_id,
            documents.c.building_id == building_id,
            documents.c.name == title,
            *active_criteria(documents),
        )
        if document_id:
            summary.documents_reused += 1
            continue

        filename = f"{safe_slug(title)}.txt"
        storage_key = f"soho-phase-i/{safe_slug(evidence_scope)}/{filename}"
        insert_row(
            connection,
            documents,
            {
                "organization_id": organization_id,
                "building_id": building_id,
                "name": title,
                "title": title,
                "description": document_description(location, evidence_scope),
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


def document_title(row: Any) -> str:
    mapping = row._mapping
    return str(mapping.get("title") or mapping.get("name") or "")


def target_for_document(title: str, building_a_id, building_b_id, common_id):
    if title in BUILDING_A_DOCUMENTS:
        return building_a_id
    if title in BUILDING_B_DOCUMENTS:
        return building_b_id
    if title in COMMON_DOCUMENTS:
        return common_id
    return None


def reassign_documents(connection, documents: Table, organization_id, source_building_ids: list[Any], building_a_id, building_b_id, common_id, summary: CleanupSummary):
    criteria = [documents.c.organization_id == organization_id, *active_criteria(documents)]
    matches = [documents.c.building_id.in_(source_building_ids)]
    if "storage_key" in documents.c:
        matches.append(documents.c.storage_key.like("soho-closeout/%"))
    rows = connection.execute(select(documents).where(*criteria, or_(*matches))).all()
    for row in rows:
        mapping = row._mapping
        target_id = target_for_document(document_title(row), building_a_id, building_b_id, common_id)
        if target_id and mapping["building_id"] != target_id:
            connection.execute(update(documents).where(documents.c.id == mapping["id"]).values(building_id=target_id))
            summary.documents_reassigned += 1


def target_for_asset(name: str, building_a_id, common_id):
    if name in BUILDING_A_ASSETS:
        return building_a_id
    if name in COMMON_ASSETS:
        return common_id
    return None


def reassign_assets(connection, assets: Table, organization_id, source_building_ids: list[Any], building_a_id, common_id, summary: CleanupSummary):
    criteria = [
        assets.c.organization_id == organization_id,
        assets.c.building_id.in_(source_building_ids),
        *active_criteria(assets),
    ]
    rows = connection.execute(select(assets).where(*criteria)).all()
    for row in rows:
        mapping = row._mapping
        target_id = target_for_asset(str(mapping.get("name") or ""), building_a_id, common_id)
        if target_id and mapping["building_id"] != target_id:
            connection.execute(update(assets).where(assets.c.id == mapping["id"]).values(building_id=target_id))
            summary.assets_reassigned += 1


def cleanup_soho_phase1_property() -> CleanupSummary:
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    metadata = MetaData()
    metadata.reflect(bind=engine)
    ensure_schema(metadata)

    organizations = metadata.tables["organizations"]
    properties = metadata.tables["properties"]
    campuses = metadata.tables["campuses"]
    buildings = metadata.tables["buildings"]
    asset_types = metadata.tables["asset_types"]
    assets = metadata.tables["assets"]
    documents = metadata.tables["documents"]

    summary = CleanupSummary()

    with engine.begin() as connection:
        organization_id = ensure_organization(connection, organizations, summary)
        property_id = ensure_property(connection, properties, organization_id, summary)
        campus_id = ensure_campus(connection, campuses, organization_id, property_id, summary)

        building_a_id, duplicate_ids = canonical_building_a(connection, buildings, organization_id, property_id, campus_id, summary)
        building_b_id = ensure_building(connection, buildings, organization_id, property_id, campus_id, BUILDING_B, summary)
        common_id = ensure_building(connection, buildings, organization_id, property_id, campus_id, COMMON_INFRASTRUCTURE, summary)

        summary.building_b_id = building_b_id
        summary.common_infrastructure_id = common_id

        asset_type_ids = ensure_asset_types(connection, asset_types, summary)

        source_building_ids = list(dict.fromkeys([building_a_id, building_b_id, common_id, *duplicate_ids]))
        reassign_documents(connection, documents, organization_id, source_building_ids, building_a_id, building_b_id, common_id, summary)
        reassign_assets(connection, assets, organization_id, source_building_ids, building_a_id, common_id, summary)
        archive_duplicates(connection, buildings, duplicate_ids, summary)

        ensure_seeded_assets(connection, assets, organization_id, building_a_id, SEEDED_ASSETS["building_a"], asset_type_ids, summary)
        ensure_seeded_assets(connection, assets, organization_id, building_b_id, SEEDED_ASSETS["building_b"], asset_type_ids, summary)
        ensure_seeded_assets(connection, assets, organization_id, common_id, SEEDED_ASSETS["common"], asset_type_ids, summary)
        ensure_seeded_documents(connection, documents, organization_id, building_a_id, SEEDED_DOCUMENTS["building_a"], "Building A", summary)
        ensure_seeded_documents(connection, documents, organization_id, building_b_id, SEEDED_DOCUMENTS["building_b"], "Building B", summary)
        ensure_seeded_documents(connection, documents, organization_id, common_id, SEEDED_DOCUMENTS["common"], "Common Infrastructure", summary)

    return summary


def print_summary(summary: CleanupSummary) -> None:
    print("M6 SOHO Phase I property/campus cleanup complete")
    print(f"organization_id: {summary.organization_id}")
    print(f"property_id: {summary.property_id}")
    print(f"campus_id: {summary.campus_id}")
    print(f"building_a_id: {summary.building_a_id}")
    print(f"building_b_id: {summary.building_b_id}")
    print(f"common_infrastructure_id: {summary.common_infrastructure_id}")
    print(f"properties_created: {summary.properties_created}")
    print(f"properties_reused: {summary.properties_reused}")
    print(f"campuses_created: {summary.campuses_created}")
    print(f"campuses_reused: {summary.campuses_reused}")
    print(f"buildings_created: {summary.buildings_created}")
    print(f"buildings_reused: {summary.buildings_reused}")
    print(f"buildings_archived: {summary.buildings_archived}")
    print(f"asset_types_created: {summary.asset_types_created}")
    print(f"asset_types_reused: {summary.asset_types_reused}")
    print(f"assets_created: {summary.assets_created}")
    print(f"assets_reused: {summary.assets_reused}")
    print(f"documents_created: {summary.documents_created}")
    print(f"documents_reused: {summary.documents_reused}")
    print(f"documents_reassigned: {summary.documents_reassigned}")
    print(f"assets_reassigned: {summary.assets_reassigned}")
    print(f"duplicates_archived: {summary.duplicates_archived}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed and clean up SOHO Phase I property/campus reference records.")
    parser.add_argument("--cleanup-soho", action="store_true", help="Archive duplicate SOHO Building A records and assign evidence to Building A, Building B, and common infrastructure.")
    args = parser.parse_args()

    print_summary(cleanup_soho_phase1_property())


if __name__ == "__main__":
    main()
