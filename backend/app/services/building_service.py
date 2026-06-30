from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
from app.core.constants import BUILDING_CONTACT_TYPES, BUILDING_CREATED, BUILDING_STATUSES, BUILDING_UPDATED
from app.models import Building, BuildingContact, Organization
from app.schemas.core import BuildingContactCreate, BuildingContactUpdate, BuildingCreate, BuildingUpdate
from app.services.audit_log import audit_service
from app.services.exceptions import not_found, validation_error
from app.services.tenant import ensure_organization_access


class BuildingService:
    def list_buildings(self, db: Session, current_user: CurrentUser, organization_id: UUID | None = None) -> list[Building]:
        query = select(Building).where(Building.deleted_at.is_(None))
        if organization_id is not None:
            ensure_organization_access(current_user, organization_id)
            query = query.where(Building.organization_id == organization_id)
        elif not current_user.is_platform_admin and current_user.current_organization_id:
            query = query.where(Building.organization_id == UUID(current_user.current_organization_id))
        return list(db.scalars(query.order_by(Building.name)).all())

    def get_building(self, db: Session, building_id: UUID, current_user: CurrentUser) -> Building:
        building = db.scalar(select(Building).where(Building.id == building_id, Building.deleted_at.is_(None)))
        if building is None:
            raise not_found("Building not found.")
        ensure_organization_access(current_user, building.organization_id)
        return building

    def create_building(self, db: Session, payload: BuildingCreate, current_user: CurrentUser) -> Building:
        ensure_organization_access(current_user, payload.organization_id)
        self._validate_building_status(payload.status)
        organization = db.get(Organization, payload.organization_id)
        if organization is None or organization.deleted_at is not None:
            raise not_found("Organization not found.")
        building = Building(
            **payload.model_dump(),
            address_line1=payload.address_line_1,
            region=payload.province_state,
            bpid=self.generate_bpid(db),
        )
        db.add(building)
        db.flush()
        audit_service.record(
            db,
            action=BUILDING_CREATED,
            entity_type="building",
            entity_id=building.id,
            organization_id=building.organization_id,
            current_user=current_user,
            metadata={"bpid": building.bpid},
        )
        db.commit()
        db.refresh(building)
        return building

    def update_building(self, db: Session, building_id: UUID, payload: BuildingUpdate, current_user: CurrentUser) -> Building:
        building = self.get_building(db, building_id, current_user)
        values = payload.model_dump(exclude_unset=True)
        if "status" in values:
            self._validate_building_status(values["status"])
        for key, value in values.items():
            setattr(building, key, value)
            if key == "address_line_1":
                building.address_line1 = value
            if key == "province_state":
                building.region = value
        audit_service.record(
            db,
            action=BUILDING_UPDATED,
            entity_type="building",
            entity_id=building.id,
            organization_id=building.organization_id,
            current_user=current_user,
            metadata={"bpid": building.bpid},
        )
        db.commit()
        db.refresh(building)
        return building

    def soft_delete_building(self, db: Session, building_id: UUID, current_user: CurrentUser) -> None:
        building = self.get_building(db, building_id, current_user)
        building.deleted_at = datetime.now(timezone.utc)
        building.status = "archived"
        audit_service.record(
            db,
            action=BUILDING_UPDATED,
            entity_type="building",
            entity_id=building.id,
            organization_id=building.organization_id,
            current_user=current_user,
            metadata={"soft_deleted": True, "bpid": building.bpid},
        )
        db.commit()

    def list_contacts(self, db: Session, building_id: UUID, current_user: CurrentUser) -> list[BuildingContact]:
        building = self.get_building(db, building_id, current_user)
        return list(
            db.scalars(
                select(BuildingContact)
                .where(
                    BuildingContact.building_id == building.id,
                    BuildingContact.organization_id == building.organization_id,
                    BuildingContact.deleted_at.is_(None),
                )
                .order_by(BuildingContact.name)
            ).all()
        )

    def create_contact(
        self,
        db: Session,
        building_id: UUID,
        payload: BuildingContactCreate,
        current_user: CurrentUser,
    ) -> BuildingContact:
        building = self.get_building(db, building_id, current_user)
        self._validate_contact_type(payload.contact_type)
        contact = BuildingContact(
            **payload.model_dump(),
            building_id=building.id,
            organization_id=building.organization_id,
        )
        db.add(contact)
        db.commit()
        db.refresh(contact)
        return contact

    def get_contact(self, db: Session, contact_id: UUID, current_user: CurrentUser) -> BuildingContact:
        contact = db.scalar(
            select(BuildingContact).where(
                BuildingContact.id == contact_id,
                BuildingContact.deleted_at.is_(None),
            )
        )
        if contact is None:
            raise not_found("Building contact not found.")
        ensure_organization_access(current_user, contact.organization_id)
        return contact

    def update_contact(
        self,
        db: Session,
        contact_id: UUID,
        payload: BuildingContactUpdate,
        current_user: CurrentUser,
    ) -> BuildingContact:
        contact = self.get_contact(db, contact_id, current_user)
        values = payload.model_dump(exclude_unset=True)
        if "contact_type" in values:
            self._validate_contact_type(values["contact_type"])
        for key, value in values.items():
            setattr(contact, key, value)
        db.commit()
        db.refresh(contact)
        return contact

    def soft_delete_contact(self, db: Session, contact_id: UUID, current_user: CurrentUser) -> None:
        contact = self.get_contact(db, contact_id, current_user)
        contact.deleted_at = datetime.now(timezone.utc)
        db.commit()

    def generate_bpid(self, db: Session) -> str:
        max_bpid = db.scalar(select(func.max(Building.bpid)).where(Building.bpid.like("FMS-BLDG-%")))
        if not max_bpid:
            return "FMS-BLDG-000001"
        sequence = int(max_bpid.rsplit("-", 1)[1]) + 1
        return f"FMS-BLDG-{sequence:06d}"

    @staticmethod
    def _validate_building_status(value: str) -> None:
        if value not in BUILDING_STATUSES:
            raise validation_error("Building status is not defined in FMS-0010/FMS-0013.")

    @staticmethod
    def _validate_contact_type(value: str) -> None:
        if value not in BUILDING_CONTACT_TYPES:
            raise validation_error("Building contact type is not defined in FMS-0010.")


building_service = BuildingService()
