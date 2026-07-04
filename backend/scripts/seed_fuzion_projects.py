from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import Building, Organization


@dataclass(frozen=True)
class FuzionProject:
    job_no: str
    project_name: str
    city: str
    status: str

    @property
    def passport_no(self) -> str:
        return f"FPP-{self.job_no}"

    @property
    def project_status(self) -> str:
        return "Completed / Occupied" if self.status == "completed_occupied" else "Active"

    @property
    def lifecycle_stage(self) -> str:
        return "protect" if self.status == "completed_occupied" else "build"

    @property
    def passport_status(self) -> str:
        return "Active Record" if self.status == "completed_occupied" else "In Progress"

    @property
    def closeout_status(self) -> str:
        return "Archived / Operating" if self.status == "completed_occupied" else "Open"

    @property
    def inspection_status(self) -> str:
        return "Current / Historical" if self.status == "completed_occupied" else "Pending / In Progress"


COMPLETED_OCCUPIED_PROJECTS = [
    FuzionProject("5000", "Parkway Lofts Bldgs A-B-C", "St. Catharines", "completed_occupied"),
    FuzionProject("5002", "Montebello", "St. Catharines", "completed_occupied"),
    FuzionProject("5003", "Picasso Condos", "Richmond Hill", "completed_occupied"),
    FuzionProject("5004", "SOHO Bldgs A & B", "Hamilton", "completed_occupied"),
    FuzionProject("5005", "Gilmore LTC", "Fort Erie", "completed_occupied"),
    FuzionProject("5006", "Heritage Green Ph 2 Bldgs 1-3", "Hamilton", "completed_occupied"),
    FuzionProject("5007", "Maya Stacked Towns", "Brampton", "completed_occupied"),
    FuzionProject("5008", "Urbane Communities", "Niagara Falls", "completed_occupied"),
    FuzionProject("5009", "Women & Children Housing", "Fort Erie", "completed_occupied"),
    FuzionProject("5010", "Radiant Care Pleasant Manor LTC", "NOTL", "completed_occupied"),
    FuzionProject("5011", "Childcare Addition at Banbury Heights School", "Brantford", "completed_occupied"),
    FuzionProject("5012", "Northern Green Dry Room TFO", "Brampton", "completed_occupied"),
    FuzionProject("5013", "Hagersville Library", "Hagersville", "completed_occupied"),
    FuzionProject("5014", "Bldg. 3 Base Bldg. & Site @ 18 Rose Ave", "Welland", "completed_occupied"),
    FuzionProject("5015", "Rosenberg Elementary School & Community Centre", "Kitchener", "completed_occupied"),
    FuzionProject("5017", "MetalWorks Condo PH4", "Guelph", "completed_occupied"),
    FuzionProject("5018", "JBL Building Expansion", "Port Colborne", "completed_occupied"),
    FuzionProject("5020", "Elevate Condos", "Kitchener", "completed_occupied"),
    FuzionProject("5021", "Royal Canadian Polish Legion", "St. Catharines", "completed_occupied"),
    FuzionProject("5025", "North Green CuraLeaf Supply & Install CuraLeaf", "Brampton", "completed_occupied"),
]

ACTIVE_PROJECTS = [
    FuzionProject("5001", "Linhaven LTC", "St. Catharines", "active"),
    FuzionProject("5016", "Stanley Self Storage (Dunkirk)", "St. Catharines", "active"),
    FuzionProject("5019", "Niagara St. Plaza", "Welland", "active"),
    FuzionProject("5022", "Daycare Expansion at Pavillon de la Jeunesse", "Hamilton", "active"),
    FuzionProject("5023", "Ladona River Bldg B", "Niagara Falls", "active"),
    FuzionProject("5024", "320 Geneva Street Phase 1", "St. Catharines", "active"),
    FuzionProject("5026", "HNHC 311 Ramsey Dr", "Dunnville", "active"),
    FuzionProject("5027", "AHI Expansion @ NC", "Welland", "active"),
]

FUZION_PROJECTS = COMPLETED_OCCUPIED_PROJECTS + ACTIVE_PROJECTS
FUZION_JOB_NUMBERS = {project.job_no for project in FUZION_PROJECTS}


def ensure_fuzion_organization(db: Session) -> Organization:
    organization = db.scalar(select(Organization).where(Organization.slug == "fuzion-tech"))
    if organization is None:
        organization = Organization(
            name="Fuzion Tech Inc.",
            slug="fuzion-tech",
            legal_name="Fuzion Tech Inc.",
            organization_type="contractor",
            status="active",
            country="Canada",
            notes="Operational FPP project organization.",
        )
        db.add(organization)
        db.flush()
    return organization


def project_notes(project: FuzionProject) -> str:
    return "\n".join(
        [
            "source=fuzion_active_completed_projects",
            f"jobNo={project.job_no}",
            f"passportNo={project.passport_no}",
            f"projectStatus={project.project_status}",
            f"lifecycleStage={project.lifecycle_stage}",
            f"passportStatus={project.passport_status}",
            f"closeoutStatus={project.closeout_status}",
            f"inspectionStatus={project.inspection_status}",
        ]
    )


def upsert_project(db: Session, organization: Organization, project: FuzionProject) -> Building:
    building = db.scalar(
        select(Building).where(
            Building.organization_id == organization.id,
            Building.code == project.job_no,
        )
    )
    if building is None:
        building = db.scalar(select(Building).where(Building.bpid == project.passport_no))

    values = {
        "organization_id": organization.id,
        "name": project.project_name,
        "code": project.job_no,
        "bpid": project.passport_no,
        "address_line_1": project.city,
        "address_line1": project.city,
        "city": project.city,
        "province_state": "Ontario",
        "region": "Ontario",
        "country": "Canada",
        "building_type": "fuzion_project",
        "occupancy_classification": "operational_placeholder",
        "status": project.status,
        "owner_name": None,
        "property_manager_name": None,
        "notes": project_notes(project),
    }

    if building is None:
        building = Building(**values)
        db.add(building)
    else:
        for key, value in values.items():
            setattr(building, key, value)
        building.deleted_at = None
    return building


def archive_non_fuzion_seed_buildings(db: Session, organization: Organization) -> int:
    archived = 0
    _ = organization
    buildings = db.scalars(select(Building).where(Building.deleted_at.is_(None))).all()
    for building in buildings:
        if building.code in FUZION_JOB_NUMBERS:
            continue
        if building.bpid in {f"FPP-{job_no}" for job_no in FUZION_JOB_NUMBERS}:
            continue
        building.status = "archived"
        building.deleted_at = datetime.now(timezone.utc)
        building.notes = "\n".join(part for part in [building.notes, "Soft-archived by Fuzion active/completed project seed."] if part)
        archived += 1
    return archived


def seed_fuzion_projects() -> dict[str, int]:
    db = SessionLocal()
    try:
        organization = ensure_fuzion_organization(db)
        for project in FUZION_PROJECTS:
            upsert_project(db, organization, project)
        archived = archive_non_fuzion_seed_buildings(db, organization)
        db.commit()
        return {"upserted": len(FUZION_PROJECTS), "archived": archived}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    result = seed_fuzion_projects()
    print(f"Fuzion project seed complete: {result['upserted']} upserted, {result['archived']} archived")
