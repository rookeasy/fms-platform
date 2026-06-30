from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import AssetType, MembershipPlan, Role

ROLES = [
    {"name": "admin", "description": "Full organization administration access."},
    {"name": "manager", "description": "Manages buildings, work, inspections, and documents."},
    {"name": "technician", "description": "Completes assigned work orders and field tasks."},
    {"name": "inspector", "description": "Performs inspections and records deficiencies."},
    {"name": "viewer", "description": "Read-only access to assigned organization data."},
]

ASSET_TYPES = [
    {"name": "Fire Alarm System", "code": "fire_alarm", "description": "Fire alarm panels, devices, and related systems."},
    {"name": "Sprinkler System", "code": "sprinkler", "description": "Sprinkler risers, valves, and connected equipment."},
    {"name": "Elevator", "code": "elevator", "description": "Passenger, service, and freight elevators."},
    {"name": "HVAC", "code": "hvac", "description": "Heating, ventilation, and air conditioning equipment."},
    {"name": "Backflow Preventer", "code": "backflow", "description": "Backflow prevention assemblies and devices."},
]

MEMBERSHIP_PLANS = [
    {"name": "Starter", "code": "starter", "description": "Entry plan for small portfolios.", "monthly_price": 0},
    {"name": "Professional", "code": "professional", "description": "Operational plan for active portfolios.", "monthly_price": 199},
    {"name": "Enterprise", "code": "enterprise", "description": "Advanced plan for large organizations.", "monthly_price": 499},
]


def get_or_create_role(db: Session, payload: dict) -> None:
    role = db.scalar(select(Role).where(Role.name == payload["name"]))
    if role is None:
        db.add(Role(**payload))


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
