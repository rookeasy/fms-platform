from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import Building
from scripts.seed_fuzion_projects import FUZION_PROJECTS, ensure_fuzion_organization, upsert_project

PASSPORT_STATUS_NOT_STARTED = "Not Started"
PASSPORT_STATUS_BUILDING_REGISTERED = "Building Registered"
PASSPORT_STATUS_CLOSEOUT_INCOMPLETE = "Closeout Incomplete"


def existing_building(db: Session, organization_id, project) -> Building | None:
    building = db.scalar(
        select(Building).where(
            Building.organization_id == organization_id,
            Building.code == project.job_no,
        )
    )
    if building is None:
        building = db.scalar(select(Building).where(Building.bpid == project.passport_no))
    return building


def update_passport_onboarding(building: Building, project) -> bool:
    values = {
        "project_classification": project.project_classification,
        "passport_eligible": project.passport_eligible,
        "passport_status": project.onboarding_passport_status if project.passport_eligible else PASSPORT_STATUS_NOT_STARTED,
        "passport_issue_date": None,
        "passport_version": "v0.1" if project.passport_eligible else None,
        "client_handover_status": PASSPORT_STATUS_CLOSEOUT_INCOMPLETE if project.passport_eligible else PASSPORT_STATUS_NOT_STARTED,
    }
    changed = False
    for key, value in values.items():
        if getattr(building, key) != value:
            setattr(building, key, value)
            changed = True
    return changed


def needs_passport_update(building: Building, project) -> bool:
    expected = {
        "project_classification": project.project_classification,
        "passport_eligible": project.passport_eligible,
        "passport_status": project.onboarding_passport_status if project.passport_eligible else PASSPORT_STATUS_NOT_STARTED,
        "passport_issue_date": None,
        "passport_version": "v0.1" if project.passport_eligible else None,
        "client_handover_status": PASSPORT_STATUS_CLOSEOUT_INCOMPLETE if project.passport_eligible else PASSPORT_STATUS_NOT_STARTED,
    }
    return any(getattr(building, key) != value for key, value in expected.items())


def onboard_completed_fuzion_projects() -> dict[str, int]:
    db = SessionLocal()
    counts = {
        "created": 0,
        "reused": 0,
        "updated": 0,
        "passport_eligible": 0,
        "skipped": 0,
    }
    try:
        organization = ensure_fuzion_organization(db)
        for project in FUZION_PROJECTS:
            found = existing_building(db, organization.id, project)
            should_count_update = found is not None and needs_passport_update(found, project)
            building = upsert_project(db, organization, project)
            db.flush()
            if found is None:
                counts["created"] += 1
            else:
                counts["reused"] += 1

            if update_passport_onboarding(building, project) or should_count_update:
                counts["updated"] += 1

            if project.passport_eligible:
                counts["passport_eligible"] += 1
            else:
                counts["skipped"] += 1

        db.commit()
        return counts
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    result = onboard_completed_fuzion_projects()
    print(
        "Completed Fuzion project onboarding complete: "
        f"{result['created']} created, "
        f"{result['reused']} reused, "
        f"{result['updated']} updated, "
        f"{result['passport_eligible']} passport eligible, "
        f"{result['skipped']} skipped"
    )
