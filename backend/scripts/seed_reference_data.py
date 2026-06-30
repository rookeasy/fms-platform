from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import AssetType, MembershipPlan, Role

ROLES = [
    {"name": "platform_admin", "description": "Full access across the entire platform.", "is_system_role": True},
    {"name": "organization_admin", "description": "Full administrative access within an organization.", "is_system_role": True},
    {"name": "property_manager", "description": "Operational access to assigned buildings.", "is_system_role": True},
    {"name": "building_owner", "description": "Client-side owner access to building records.", "is_system_role": True},
    {"name": "technician", "description": "Completes assigned work orders and field tasks."},
    {"name": "engineer", "description": "Technical reviewer for drawings, reports, calculations, and letters.", "is_system_role": True},
    {"name": "readonly_viewer", "description": "Limited view-only access.", "is_system_role": True},
    {"name": "ahj_viewer", "description": "Limited compliance verification access for AHJ users.", "is_system_role": True},
]

ASSET_TYPES = [
    {"name": "Wet Sprinkler System", "code": "wet_sprinkler_system", "category": "sprinkler"},
    {"name": "Dry Sprinkler System", "code": "dry_sprinkler_system", "category": "sprinkler"},
    {"name": "Preaction System", "code": "preaction_system", "category": "sprinkler"},
    {"name": "Deluge System", "code": "deluge_system", "category": "sprinkler"},
    {"name": "Antifreeze System", "code": "antifreeze_system", "category": "sprinkler"},
    {"name": "Residential Sprinkler System", "code": "residential_sprinkler_system", "category": "sprinkler"},
    {"name": "Standpipe System", "code": "standpipe_system", "category": "standpipe"},
    {"name": "Fire Pump", "code": "fire_pump", "category": "fire_pump"},
    {"name": "Jockey Pump", "code": "jockey_pump", "category": "fire_pump"},
    {"name": "Fire Pump Controller", "code": "fire_pump_controller", "category": "fire_pump"},
    {"name": "Fire Pump Transfer Switch", "code": "fire_pump_transfer_switch", "category": "fire_pump"},
    {"name": "Backflow Preventer", "code": "backflow_preventer", "category": "backflow"},
    {"name": "Double Check Valve Assembly", "code": "double_check_valve_assembly", "category": "backflow"},
    {"name": "Reduced Pressure Principle Assembly", "code": "reduced_pressure_principle_assembly", "category": "backflow"},
    {"name": "Control Valve", "code": "control_valve", "category": "valve"},
    {"name": "Zone Valve", "code": "zone_valve", "category": "valve"},
    {"name": "Sectional Valve", "code": "sectional_valve", "category": "valve"},
    {"name": "Inspector's Test Connection", "code": "inspectors_test_connection", "category": "sprinkler"},
    {"name": "Main Drain", "code": "main_drain", "category": "sprinkler"},
    {"name": "Riser", "code": "riser", "category": "sprinkler"},
    {"name": "Sprinkler Zone", "code": "sprinkler_zone", "category": "sprinkler"},
    {"name": "Fire Department Connection", "code": "fire_department_connection", "category": "water_supply"},
    {"name": "Private Hydrant", "code": "private_hydrant", "category": "hydrant"},
    {"name": "Water Storage Tank", "code": "water_storage_tank", "category": "water_supply"},
    {"name": "Fire Alarm System", "code": "fire_alarm_system", "category": "fire_alarm"},
    {"name": "Fire Alarm Panel", "code": "fire_alarm_panel", "category": "fire_alarm"},
    {"name": "Supervisory Device", "code": "supervisory_device", "category": "fire_alarm"},
    {"name": "Kitchen Suppression System", "code": "kitchen_suppression_system", "category": "suppression"},
    {"name": "Clean Agent System", "code": "clean_agent_system", "category": "suppression"},
    {"name": "Foam System", "code": "foam_system", "category": "suppression"},
    {"name": "Special Hazard System", "code": "special_hazard_system", "category": "suppression"},
    {"name": "Portable Extinguisher", "code": "portable_extinguisher", "category": "life_safety"},
    {"name": "Emergency Lighting", "code": "emergency_lighting", "category": "life_safety"},
    {"name": "Exit Sign", "code": "exit_sign", "category": "life_safety"},
    {"name": "Other", "code": "other", "category": "other"},
]

MEMBERSHIP_PLANS = [
    {"name": "Essentials", "code": "essentials", "description": "Entry Protection Plan for small portfolios.", "monthly_price": 0},
    {"name": "Professional", "code": "professional", "description": "Operational plan for active portfolios.", "monthly_price": 199},
    {"name": "Enterprise", "code": "enterprise", "description": "Advanced plan for large organizations.", "monthly_price": 499},
]


def get_or_create_role(db: Session, payload: dict) -> None:
    role = db.scalar(select(Role).where(Role.name == payload["name"]))
    if role is None:
        db.add(Role(**payload))
    else:
        for key, value in payload.items():
            setattr(role, key, value)


def get_or_create_asset_type(db: Session, payload: dict) -> None:
    asset_type = db.scalar(
        select(AssetType).where(
            AssetType.organization_id.is_(None),
            AssetType.code == payload["code"],
        )
    )
    if asset_type is None:
        db.add(AssetType(organization_id=None, **payload))
    else:
        for key, value in payload.items():
            setattr(asset_type, key, value)


def get_or_create_membership_plan(db: Session, payload: dict) -> None:
    plan = db.scalar(select(MembershipPlan).where(MembershipPlan.code == payload["code"]))
    if plan is None:
        db.add(MembershipPlan(**payload))


def seed_reference_data() -> None:
    db = SessionLocal()
    try:
        for role in ROLES:
            get_or_create_role(db, role)
        for asset_type in ASSET_TYPES:
            get_or_create_asset_type(db, asset_type)
        for plan in MEMBERSHIP_PLANS:
            get_or_create_membership_plan(db, plan)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_reference_data()
