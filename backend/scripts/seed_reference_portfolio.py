from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import MetaData, Table, create_engine, func, insert, select

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
    building_ids: dict[str, Any] | None = None


ORGANIZATION = {
    "name": "Fuzion Fire Inc.",
    "email": "reference-portfolio@example.com",
    "website": "https://www.fuzionfire.ca",
    "phone": "905-000-0000",
    "organization_type": "contractor",
    "status": "active",
    "address_line_1": "Reference office address",
    "city": "Niagara Falls",
    "province_state": "ON",
    "postal_code": "L2E 0A0",
    "country": "Canada",
    "notes": "Internal FMS-0023 reference organization for development, demos, and training.",
}


ASSET_TYPES = {
    "wet_sprinkler_system": ("Wet Sprinkler System", "sprinkler"),
    "dry_sprinkler_system": ("Dry Sprinkler System", "sprinkler"),
    "standpipe_system": ("Standpipe System", "standpipe"),
    "fire_alarm_control_panel": ("Fire Alarm Control Panel", "fire_alarm"),
    "fire_department_connection": ("Fire Department Connection", "water_supply"),
    "fire_pump": ("Fire Pump", "fire_pump"),
    "backflow_preventer": ("Backflow Preventer", "backflow"),
    "special_suppression_system": ("Special Suppression System", "suppression"),
    "emergency_lighting": ("Emergency Lighting", "life_safety"),
    "fire_extinguishers": ("Fire Extinguishers", "life_safety"),
}


COMMON_DOCUMENTS = [
    ("Building Protection Passport Summary", "passport_export", True, True),
    ("Approved Fire Protection Drawings", "shop_drawing", True, True),
    ("Hydraulic Calculation Package", "hydraulic_calculation", True, True),
    ("Owner Training Handoff Notes", "owner_manual", False, False),
]


REFERENCE_BUILDINGS = [
    {
        "name": "Linhaven Long-Term Care",
        "address_line_1": "403 Ontario Street",
        "city": "St. Catharines",
        "province_state": "ON",
        "postal_code": "L2N 1L5",
        "building_type": "long_term_care",
        "occupancy_classification": "care_occupancy",
        "number_of_storeys": 5,
        "owner_name": "Reference Care Owner",
        "property_manager_name": "Reference LTC Operations",
        "fire_department": "St. Catharines Fire Services",
        "ahj_name": "City of St. Catharines",
        "notes": "FMS-0023 reference LTC site for Passport demonstrations, training, and internal knowledge capture.",
        "assets": [
            ("Wet Sprinkler System - Resident Areas", "wet_sprinkler_system", "Resident floors"),
            ("Class III Standpipe System", "standpipe_system", "Exit stairs"),
            ("Fire Pump", "fire_pump", "Fire pump room"),
            ("Fire Alarm Control Panel", "fire_alarm_control_panel", "Main entrance vestibule"),
            ("Fire Department Connection", "fire_department_connection", "Ontario Street exterior"),
            ("Backflow Preventer", "backflow_preventer", "Service room"),
        ],
        "documents": [("Contractor Material and Test Certificate", "contractors_material_test_certificate", True, True)],
    },
    {
        "name": "Gilmore Lodge LTC",
        "address_line_1": "50 Gilmore Road",
        "city": "Fort Erie",
        "province_state": "ON",
        "postal_code": "L2A 2M1",
        "building_type": "long_term_care",
        "occupancy_classification": "care_occupancy",
        "number_of_storeys": 4,
        "owner_name": "Reference Care Owner",
        "property_manager_name": "Reference LTC Operations",
        "fire_department": "Fort Erie Fire Department",
        "ahj_name": "Town of Fort Erie",
        "notes": "Reference LTC profile for comparing care occupancy Passport records and sales walkthroughs.",
        "assets": [
            ("Wet Sprinkler System - Care Wings", "wet_sprinkler_system", "Care wings"),
            ("Standpipe System", "standpipe_system", "Exit stairs"),
            ("Fire Alarm Control Panel", "fire_alarm_control_panel", "Main lobby"),
            ("Fire Department Connection", "fire_department_connection", "Gilmore Road exterior"),
            ("Fire Extinguisher Program", "fire_extinguishers", "Building-wide"),
        ],
        "documents": [("Care Occupancy Fire Safety Plan Metadata", "other", True, True)],
    },
    {
        "name": "SOHO Phase 1",
        "address_line_1": "91 South Service Road",
        "city": "Grimsby",
        "province_state": "ON",
        "postal_code": "L3M 0A1",
        "building_type": "mixed_use_residential",
        "occupancy_classification": "residential_mixed_use",
        "number_of_storeys": 8,
        "owner_name": "Reference Condominium Corporation",
        "property_manager_name": "Reference Condo Management",
        "fire_department": "Grimsby Fire Department",
        "ahj_name": "Town of Grimsby",
        "notes": "Reference high-rise phase used to demonstrate multi-building portfolio navigation.",
        "assets": [
            ("Wet Sprinkler System - Tower", "wet_sprinkler_system", "Tower and amenity areas"),
            ("Standpipe System", "standpipe_system", "Exit stairs"),
            ("Fire Alarm Control Panel", "fire_alarm_control_panel", "Lobby annunciator"),
            ("Fire Department Connection", "fire_department_connection", "South Service Road exterior"),
        ],
        "documents": [("Condo Turnover Drawing Index", "as_built_drawing", True, True)],
    },
    {
        "name": "SOHO Phase 2",
        "address_line_1": "99 South Service Road",
        "city": "Grimsby",
        "province_state": "ON",
        "postal_code": "L3M 0A2",
        "building_type": "mixed_use_residential",
        "occupancy_classification": "residential_mixed_use",
        "number_of_storeys": 8,
        "owner_name": "Reference Condominium Corporation",
        "property_manager_name": "Reference Condo Management",
        "fire_department": "Grimsby Fire Department",
        "ahj_name": "Town of Grimsby",
        "notes": "Second SOHO phase for demonstrating related-building Passport comparisons.",
        "assets": [
            ("Wet Sprinkler System - Tower", "wet_sprinkler_system", "Tower and amenity areas"),
            ("Dry Sprinkler System - Parking", "dry_sprinkler_system", "Parking garage"),
            ("Fire Alarm Control Panel", "fire_alarm_control_panel", "Main lobby"),
            ("Backflow Preventer", "backflow_preventer", "Mechanical room"),
        ],
        "documents": [("Parking Garage Fire Protection Summary", "as_built_drawing", True, True)],
    },
    {
        "name": "Montebello Condominiums",
        "address_line_1": "50 Herrick Avenue",
        "city": "St. Catharines",
        "province_state": "ON",
        "postal_code": "L2P 2S4",
        "building_type": "condominium",
        "occupancy_classification": "residential",
        "number_of_storeys": 6,
        "owner_name": "Reference Condominium Corporation",
        "property_manager_name": "Reference Condo Management",
        "fire_department": "St. Catharines Fire Services",
        "ahj_name": "City of St. Catharines",
        "notes": "Condominium reference building for owner-facing Passport demonstrations.",
        "assets": [
            ("Wet Sprinkler System", "wet_sprinkler_system", "Residential floors"),
            ("Fire Alarm Control Panel", "fire_alarm_control_panel", "Main entrance"),
            ("Fire Department Connection", "fire_department_connection", "Exterior wall"),
            ("Emergency Lighting", "emergency_lighting", "Common corridors"),
        ],
        "documents": [("Condominium Client Handoff Package", "owner_manual", False, False)],
    },
    {
        "name": "Marbella Condominiums",
        "address_line_1": "7549 Kalar Road",
        "city": "Niagara Falls",
        "province_state": "ON",
        "postal_code": "L2H 0Y6",
        "building_type": "condominium",
        "occupancy_classification": "residential",
        "number_of_storeys": 6,
        "owner_name": "Reference Condominium Corporation",
        "property_manager_name": "Reference Condo Management",
        "fire_department": "Niagara Falls Fire Department",
        "ahj_name": "City of Niagara Falls",
        "notes": "Reference condominium used to demo client-visible document filtering.",
        "assets": [
            ("Wet Sprinkler System", "wet_sprinkler_system", "Residential floors"),
            ("Standpipe System", "standpipe_system", "Stair shafts"),
            ("Fire Alarm Control Panel", "fire_alarm_control_panel", "Front vestibule"),
            ("Backflow Preventer", "backflow_preventer", "Mechanical room"),
        ],
        "documents": [("Residential Riser Diagram", "drawing", True, True)],
    },
    {
        "name": "Parkway Lofts",
        "address_line_1": "257 Millen Road",
        "city": "Hamilton",
        "province_state": "ON",
        "postal_code": "L8E 2H1",
        "building_type": "residential",
        "occupancy_classification": "residential",
        "number_of_storeys": 5,
        "owner_name": "Reference Residential Owner",
        "property_manager_name": "Reference Property Management",
        "fire_department": "Hamilton Fire Department",
        "ahj_name": "City of Hamilton",
        "notes": "Residential loft reference site for training on compact building profiles.",
        "assets": [
            ("Wet Sprinkler System", "wet_sprinkler_system", "Residential areas"),
            ("Fire Alarm Control Panel", "fire_alarm_control_panel", "Lobby"),
            ("Fire Department Connection", "fire_department_connection", "Exterior"),
            ("Fire Extinguisher Program", "fire_extinguishers", "Common areas"),
        ],
        "documents": [("Residential Fire Protection Drawing Set", "shop_drawing", True, True)],
    },
    {
        "name": "Gates of Thornhill Building C",
        "address_line_1": "7850 Dufferin Street",
        "city": "Vaughan",
        "province_state": "ON",
        "postal_code": "L4K 0B1",
        "building_type": "condominium",
        "occupancy_classification": "residential",
        "number_of_storeys": 12,
        "owner_name": "Reference Condominium Corporation",
        "property_manager_name": "Reference Condo Management",
        "fire_department": "Vaughan Fire and Rescue Service",
        "ahj_name": "City of Vaughan",
        "notes": "High-rise condominium reference profile for sales demonstrations with a larger asset mix.",
        "assets": [
            ("Wet Sprinkler System - Tower", "wet_sprinkler_system", "Tower floors"),
            ("Dry Sprinkler System - Garage", "dry_sprinkler_system", "Parking levels"),
            ("Standpipe System", "standpipe_system", "Exit stairs"),
            ("Fire Pump", "fire_pump", "Pump room"),
            ("Fire Alarm Control Panel", "fire_alarm_control_panel", "Concierge desk"),
        ],
        "documents": [("High-Rise Fire Protection Matrix", "engineering_letter", True, True)],
    },
    {
        "name": "Waterloo Avenue Public School",
        "address_line_1": "24 Waterloo Avenue",
        "city": "Guelph",
        "province_state": "ON",
        "postal_code": "N1H 3H3",
        "building_type": "school",
        "occupancy_classification": "assembly_education",
        "number_of_storeys": 2,
        "owner_name": "Reference District School Board",
        "property_manager_name": "Reference Facilities Department",
        "fire_department": "Guelph Fire Department",
        "ahj_name": "City of Guelph",
        "notes": "Education-sector reference site for internal demos and board-facing Passport workflows.",
        "assets": [
            ("Wet Sprinkler System", "wet_sprinkler_system", "School-wide"),
            ("Fire Alarm Control Panel", "fire_alarm_control_panel", "Main office"),
            ("Fire Department Connection", "fire_department_connection", "Front elevation"),
            ("Emergency Lighting", "emergency_lighting", "Corridors and gym"),
        ],
        "documents": [("School Fire Safety Reference Package", "other", True, True)],
    },
    {
        "name": "Niagara Falls CES",
        "address_line_1": "7771 St. Michael Avenue",
        "city": "Niagara Falls",
        "province_state": "ON",
        "postal_code": "L2H 2Y6",
        "building_type": "school",
        "occupancy_classification": "assembly_education",
        "number_of_storeys": 2,
        "owner_name": "Reference Catholic School Board",
        "property_manager_name": "Reference Facilities Department",
        "fire_department": "Niagara Falls Fire Department",
        "ahj_name": "City of Niagara Falls",
        "notes": "Catholic elementary school reference profile for education portfolio demonstrations.",
        "assets": [
            ("Wet Sprinkler System", "wet_sprinkler_system", "School-wide"),
            ("Fire Alarm Control Panel", "fire_alarm_control_panel", "Administration area"),
            ("Fire Department Connection", "fire_department_connection", "Front driveway"),
            ("Fire Extinguisher Program", "fire_extinguishers", "Classroom corridors"),
        ],
        "documents": [("Elementary School Drawing Index", "drawing", True, True)],
    },
    {
        "name": "CS Viamonde Elementary School",
        "address_line_1": "600 River Road",
        "city": "Welland",
        "province_state": "ON",
        "postal_code": "L3B 5N4",
        "building_type": "school",
        "occupancy_classification": "assembly_education",
        "number_of_storeys": 2,
        "owner_name": "Reference French Public School Board",
        "property_manager_name": "Reference Facilities Department",
        "fire_department": "Welland Fire and Emergency Services",
        "ahj_name": "City of Welland",
        "notes": "French-language school reference site for training and sales discovery examples.",
        "assets": [
            ("Wet Sprinkler System", "wet_sprinkler_system", "School-wide"),
            ("Fire Alarm Control Panel", "fire_alarm_control_panel", "Main office"),
            ("Emergency Lighting", "emergency_lighting", "Corridors"),
            ("Backflow Preventer", "backflow_preventer", "Service room"),
        ],
        "documents": [("Bilingual Client Handoff Notes", "owner_manual", False, False)],
    },
    {
        "name": "Griffin Way Industrial",
        "address_line_1": "10 Griffin Way",
        "city": "Chelsea",
        "province_state": "MA",
        "postal_code": "02150",
        "country": "United States",
        "building_type": "industrial",
        "occupancy_classification": "industrial",
        "number_of_storeys": 1,
        "owner_name": "Reference Industrial Owner",
        "property_manager_name": "Reference Industrial Management",
        "fire_department": "Chelsea Fire Department",
        "ahj_name": "City of Chelsea",
        "notes": "Industrial reference building for demonstrating non-Canadian and warehouse-style profiles.",
        "assets": [
            ("Wet Sprinkler System - Warehouse", "wet_sprinkler_system", "Warehouse"),
            ("Fire Pump", "fire_pump", "Pump room"),
            ("Fire Alarm Control Panel", "fire_alarm_control_panel", "Shipping office"),
            ("Fire Department Connection", "fire_department_connection", "Truck court"),
            ("Backflow Preventer", "backflow_preventer", "Water entry"),
        ],
        "documents": [("Industrial Warehouse Fire Protection Overview", "engineering_letter", True, True)],
    },
    {
        "name": "Prologis DC1 Halton Hills",
        "address_line_1": "8450 Boston Church Road",
        "city": "Halton Hills",
        "province_state": "ON",
        "postal_code": "L0P 1E0",
        "building_type": "warehouse_distribution",
        "occupancy_classification": "storage",
        "number_of_storeys": 1,
        "owner_name": "Reference Logistics Owner",
        "property_manager_name": "Reference Logistics Management",
        "fire_department": "Halton Hills Fire Department",
        "ahj_name": "Town of Halton Hills",
        "notes": "Distribution-centre reference site for sales demos with high-value sprinkler assets.",
        "assets": [
            ("ESFR Wet Sprinkler System", "wet_sprinkler_system", "Warehouse ceiling"),
            ("Fire Pump", "fire_pump", "Pump house"),
            ("Backflow Preventer", "backflow_preventer", "Water entry"),
            ("Fire Alarm Control Panel", "fire_alarm_control_panel", "Security office"),
            ("Fire Department Connection", "fire_department_connection", "Truck court"),
        ],
        "documents": [("Distribution Centre Hydraulic Design Narrative", "hydraulic_calculation", True, True)],
    },
    {
        "name": "Darling Ingredients",
        "address_line_1": "1000 Heritage Road",
        "city": "Burlington",
        "province_state": "ON",
        "postal_code": "L7L 4X9",
        "building_type": "industrial",
        "occupancy_classification": "industrial_processing",
        "number_of_storeys": 2,
        "owner_name": "Reference Industrial Owner",
        "property_manager_name": "Reference Plant Operations",
        "fire_department": "Burlington Fire Department",
        "ahj_name": "City of Burlington",
        "notes": "Industrial processing reference profile for specialized system demonstrations.",
        "assets": [
            ("Wet Sprinkler System - Processing Areas", "wet_sprinkler_system", "Processing floor"),
            ("Special Suppression System", "special_suppression_system", "Process equipment area"),
            ("Fire Pump", "fire_pump", "Pump room"),
            ("Fire Alarm Control Panel", "fire_alarm_control_panel", "Control room"),
            ("Fire Extinguisher Program", "fire_extinguishers", "Plant-wide"),
        ],
        "documents": [("Special Suppression System Data Sheet", "manufacturer_data", True, True)],
    },
    {
        "name": "2700 Aquitaine Avenue",
        "address_line_1": "2700 Aquitaine Avenue",
        "city": "Mississauga",
        "province_state": "ON",
        "postal_code": "L5N 3J6",
        "building_type": "residential",
        "occupancy_classification": "residential",
        "number_of_storeys": 10,
        "owner_name": "Reference Residential Owner",
        "property_manager_name": "Reference Property Management",
        "fire_department": "Mississauga Fire and Emergency Services",
        "ahj_name": "City of Mississauga",
        "notes": "Residential tower reference building for Passport demonstrations with older-building assumptions.",
        "assets": [
            ("Wet Sprinkler System", "wet_sprinkler_system", "Residential floors"),
            ("Standpipe System", "standpipe_system", "Exit stairs"),
            ("Fire Alarm Control Panel", "fire_alarm_control_panel", "Lobby"),
            ("Fire Department Connection", "fire_department_connection", "Aquitaine Avenue exterior"),
        ],
        "documents": [("Residential Tower Passport Intake Notes", "other", False, False)],
    },
    {
        "name": "5500 North Service Road",
        "address_line_1": "5500 North Service Road",
        "city": "Burlington",
        "province_state": "ON",
        "postal_code": "L7L 6W6",
        "building_type": "commercial_office",
        "occupancy_classification": "business_personal_services",
        "number_of_storeys": 4,
        "owner_name": "Reference Commercial Owner",
        "property_manager_name": "Reference Commercial Management",
        "fire_department": "Burlington Fire Department",
        "ahj_name": "City of Burlington",
        "notes": "Commercial office reference site for internal operations and client-facing sales demos.",
        "assets": [
            ("Wet Sprinkler System", "wet_sprinkler_system", "Office floors"),
            ("Fire Alarm Control Panel", "fire_alarm_control_panel", "Main lobby"),
            ("Fire Department Connection", "fire_department_connection", "North Service Road exterior"),
            ("Emergency Lighting", "emergency_lighting", "Exit paths"),
        ],
        "documents": [("Commercial Office Fire Protection Summary", "building_health_report", True, True)],
    },
]


def payload_for(table: Table, payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if key in table.c}


def first_id(connection, table: Table, *criteria):
    row = connection.execute(select(table.c.id).where(*criteria).limit(1)).first()
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
            "FMS-0023 reference portfolio seed requires existing MVP database tables. Missing: "
            + ", ".join(missing)
            + ". Run the current database migrations before this seed script."
        )


def safe_slug(value: str) -> str:
    return "".join(character.lower() if character.isalnum() else "-" for character in value).strip("-")


def contact_payloads(building: dict[str, Any]) -> list[dict[str, Any]]:
    slug = safe_slug(building["name"])
    city = str(building["city"]).replace(" ", "")
    return [
        {
            "contact_type": "property_manager",
            "name": f"{building['property_manager_name']} Contact",
            "company": building["property_manager_name"],
            "job_title": "Property Manager",
            "email": f"{slug}.property@example.com",
            "phone": "905-000-1000",
            "is_primary": True,
            "is_emergency_contact": False,
            "notes": "Safe placeholder contact for the FMS-0023 reference portfolio.",
        },
        {
            "contact_type": "site_contact",
            "name": "Reference Site Contact",
            "company": building["name"],
            "job_title": "Site Contact",
            "email": f"{slug}.site@example.com",
            "phone": "905-000-2000",
            "is_primary": False,
            "is_emergency_contact": True,
            "notes": "Safe placeholder site contact for demonstrations and training.",
        },
        {
            "contact_type": "ahj",
            "name": "Reference Fire Prevention Office",
            "company": building["fire_department"],
            "job_title": "Fire Prevention",
            "email": f"fireprevention.{city.lower()}@example.com",
            "phone": "905-000-3000",
            "is_primary": False,
            "is_emergency_contact": False,
            "notes": "Safe placeholder AHJ contact for Passport demos.",
        },
    ]


def document_payloads(building: dict[str, Any]) -> list[tuple[str, str, bool, bool]]:
    return [*COMMON_DOCUMENTS, *building["documents"]]


def seed_reference_portfolio() -> SeedSummary:
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
    summary = SeedSummary(building_ids={})

    with engine.begin() as connection:
        organization_id = first_id(connection, organizations, organizations.c.name == ORGANIZATION["name"])
        if organization_id:
            summary.organizations_reused += 1
        else:
            organization_id = insert_row(connection, organizations, ORGANIZATION)
            summary.organizations_created += 1
        summary.organization_id = organization_id

        asset_type_ids = {}
        for code, (name, category) in ASSET_TYPES.items():
            asset_type_id = first_id(connection, asset_types, asset_types.c.code == code)
            if asset_type_id:
                summary.asset_types_reused += 1
            else:
                asset_type_id = insert_row(
                    connection,
                    asset_types,
                    {"organization_id": None, "code": code, "name": name, "category": category},
                )
                summary.asset_types_created += 1
            asset_type_ids[code] = asset_type_id

        for building in REFERENCE_BUILDINGS:
            building_id = first_id(
                connection,
                buildings,
                buildings.c.organization_id == organization_id,
                buildings.c.name == building["name"],
            )
            if building_id:
                summary.buildings_reused += 1
            else:
                building_payload = {
                    **building,
                    "organization_id": organization_id,
                    "address_line1": building["address_line_1"],
                    "region": building["province_state"],
                    "status": "active",
                    "country": building.get("country", "Canada"),
                }
                if "bpid" in buildings.c:
                    building_payload["bpid"] = generate_bpid(connection, buildings)
                building_id = insert_row(connection, buildings, building_payload)
                summary.buildings_created += 1
            summary.building_ids[building["name"]] = building_id

            for contact_payload in contact_payloads(building):
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
                    insert_row(
                        connection,
                        contacts,
                        {**contact_payload, "organization_id": organization_id, "building_id": building_id},
                    )
                    summary.contacts_created += 1

            for asset_name, type_code, location in building["assets"]:
                asset_id = first_id(
                    connection,
                    assets,
                    assets.c.organization_id == organization_id,
                    assets.c.building_id == building_id,
                    assets.c.name == asset_name,
                )
                if asset_id:
                    summary.assets_reused += 1
                else:
                    tag = f"FMS0023-{safe_slug(building['name'])[:24]}-{safe_slug(asset_name)[:24]}"
                    insert_row(
                        connection,
                        assets,
                        {
                            "organization_id": organization_id,
                            "building_id": building_id,
                            "asset_type_id": asset_type_ids[type_code],
                            "name": asset_name,
                            "tag": tag,
                            "asset_tag": tag,
                            "location_description": location,
                            "status": "active",
                            "condition_rating": "good",
                            "inspection_frequency_months": 12,
                            "notes": "Representative FMS-0023 reference asset for demos and training.",
                        },
                    )
                    summary.assets_created += 1

            for title, document_type, is_passport_record, is_public_to_client in document_payloads(building):
                document_id = first_id(
                    connection,
                    documents,
                    documents.c.organization_id == organization_id,
                    documents.c.building_id == building_id,
                    documents.c.name == title,
                )
                if document_id:
                    summary.documents_reused += 1
                else:
                    filename = f"{safe_slug(building['name'])}-{safe_slug(title)}.txt"
                    storage_key = f"reference-portfolio/{safe_slug(building['name'])}/{filename}"
                    insert_row(
                        connection,
                        documents,
                        {
                            "organization_id": organization_id,
                            "building_id": building_id,
                            "name": title,
                            "title": title,
                            "description": (
                                f"FMS-0023 reference metadata for {building['name']}. "
                                "No real document file is attached in local seed data."
                            ),
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
                            "is_public_to_client": is_public_to_client,
                            "is_passport_record": is_passport_record,
                        },
                    )
                    summary.documents_created += 1

    return summary


def print_summary(summary: SeedSummary) -> None:
    print("FMS-0023 Reference Portfolio seed complete")
    print(f"Organization ID: {summary.organization_id}")
    print(f"Reference buildings: {len(summary.building_ids or {})}")
    for key, value in summary.__dict__.items():
        if key not in {"organization_id", "building_ids"}:
            print(f"{key}: {value}")
    print("Buildings:")
    for name, building_id in (summary.building_ids or {}).items():
        print(f"- {name}: {building_id}")


if __name__ == "__main__":
    print_summary(seed_reference_portfolio())
