from __future__ import annotations

import argparse
from uuid import UUID

from sqlalchemy import select

from app.api.deps import CurrentUser
from app.db.session import SessionLocal
from app.models import Building, ProtectedStateCertification
from app.services.protected_state_service import protected_state_service


def evaluate_protected_state(building_id: UUID | None = None, dry_run: bool = False) -> dict[str, int]:
    db = SessionLocal()
    current_user = CurrentUser(id="placeholder-user", email="placeholder@fms.local", roles=["platform_admin"])
    counts = {
        "buildings_evaluated": 0,
        "eligible": 0,
        "review_required": 0,
        "not_eligible": 0,
        "failed": 0,
        "records_created": 0,
        "records_reused": 0,
    }
    try:
        query = select(Building).where(Building.deleted_at.is_(None), Building.status.in_(["active", "completed_occupied"]))
        if building_id:
            query = query.where(Building.id == building_id)
        buildings = list(db.scalars(query.order_by(Building.name)).all())
        for building in buildings:
            had_record = db.scalar(select(ProtectedStateCertification.id).where(ProtectedStateCertification.building_id == building.id)) is not None
            try:
                if dry_run:
                    certification = protected_state_service._get_certification(db, building)
                    result = protected_state_service._evaluate(db, building, current_user, certification, persist=False)
                else:
                    result = protected_state_service.evaluate(db, building.id, current_user)
                counts["buildings_evaluated"] += 1
                if result.protected_state_status in {"eligible", "approved"}:
                    counts["eligible"] += 1
                elif result.protected_state_status == "not_eligible":
                    counts["not_eligible"] += 1
                else:
                    counts["review_required"] += 1
                if had_record:
                    counts["records_reused"] += 1
                else:
                    counts["records_created"] += 1
            except Exception:
                db.rollback()
                counts["failed"] += 1
        return counts
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate protected-state certification eligibility.")
    parser.add_argument("--building-id", type=UUID, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    counts = evaluate_protected_state(building_id=args.building_id, dry_run=args.dry_run)
    print("Protected-state evaluation complete:")
    for key, value in counts.items():
        print(f"{key}={value}")


if __name__ == "__main__":
    main()
