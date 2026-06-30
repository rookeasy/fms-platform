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
    {"name": "Sprinkler System", "code": "sprinkler_system", "description": "Sprinkler systems and connected equipment."},
    {"name": "Standpipe System", "code": "standpipe_system", "description": "Standpipe systems."},
    {"name": "Fire Pump", "code": "fire_pump", "description": "Fire pump equipment."},
    {"name": "Backflow Preventer", "code": "backflow_preventer", "description": "Backflow prevention assemblies and devices."},
    {"name": "Fire Alarm System", "code": "fire_alarm_system", "description": "Fire alarm panels, devices, and related systems."},
    {"name": "Fire Extinguisher", "code": "fire_extinguisher", "description": "Portable fire extinguishers."},
    {"name": "Emergency Lighting", "code": "emergency_lighting", "description": "Emergency lighting equipment."},
    {"name": "Kitchen Suppression", "code": "kitchen_suppression", "description": "Kitchen suppression systems."},
    {"name": "Special Hazard System", "code": "special_hazard_system", "description": "Special hazard suppression systems."},
    {"name": "Control Valve", "code": "control_valve", "description": "Fire protection control valves."},
    {"name": "Riser", "code": "riser", "description": "Fire protection risers."},
    {"name": "Zone", "code": "zone", "description": "Fire protection zones."},
    {"name": "Hydrant", "code": "hydrant", "description": "Hydrants."},
    {"name": "Fire Department Connection", "code": "fire_department_connection", "description": "Fire department connections."},
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
