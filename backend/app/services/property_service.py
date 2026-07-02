from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
from app.models import Building, Campus, Organization, Property
from app.schemas.core import BuildingAssignment, CampusCreate, CampusUpdate, PropertyCreate, PropertyUpdate
from app.services.exceptions import not_found, validation_error
from app.services.tenant import ensure_organization_access


PROPERTY_STATUSES = {"active", "inactive", "archived"}
PROPERTY_TYPES = {
    "single_site",
    "campus",
    "portfolio",
    "mixed_use",
    "multi_building_residential_development",
    "industrial",
    "residential",
    "commercial",
    "institutional",
    "other",
}
CAMPUS_TYPES = {"campus", "phase", "complex", "site", "zone", "other"}


class PropertyService:
    def list_properties(self, db: Session, current_user: CurrentUser, organization_id: UUID | None = None) -> list[Property]:
        query = select(Property).where(Property.deleted_at.is_(None))
        if organization_id is not None:
            ensure_organization_access(current_user, organization_id)
            query = query.where(Property.organization_id == organization_id)
        elif not current_user.is_platform_admin and current_user.current_organization_id:
            query = query.where(Property.organization_id == UUID(current_user.current_organization_id))
        properties = list(db.scalars(query.order_by(Property.name)).all())
        self._attach_property_counts(db, properties)
        return properties

    def get_property(self, db: Session, property_id: UUID, current_user: CurrentUser) -> Property:
        property_record = db.scalar(select(Property).where(Property.id == property_id, Property.deleted_at.is_(None)))
        if property_record is None:
            raise not_found("Property not found.")
        ensure_organization_access(current_user, property_record.organization_id)
        self._attach_property_counts(db, [property_record])
        return property_record

    def create_property(self, db: Session, payload: PropertyCreate, current_user: CurrentUser) -> Property:
        ensure_organization_access(current_user, payload.organization_id)
        self._validate_property(payload.property_type, payload.status)
        organization = db.get(Organization, payload.organization_id)
        if organization is None or organization.deleted_at is not None:
            raise not_found("Organization not found.")
        property_record = Property(**payload.model_dump())
        db.add(property_record)
        db.commit()
        db.refresh(property_record)
        self._attach_property_counts(db, [property_record])
        return property_record

    def update_property(self, db: Session, property_id: UUID, payload: PropertyUpdate, current_user: CurrentUser) -> Property:
        property_record = self.get_property(db, property_id, current_user)
        values = payload.model_dump(exclude_unset=True)
        self._validate_property(values.get("property_type"), values.get("status"))
        for key, value in values.items():
            setattr(property_record, key, value)
        db.commit()
        db.refresh(property_record)
        self._attach_property_counts(db, [property_record])
        return property_record

    def soft_delete_property(self, db: Session, property_id: UUID, current_user: CurrentUser) -> None:
        property_record = self.get_property(db, property_id, current_user)
        property_record.deleted_at = datetime.now(timezone.utc)
        property_record.status = "archived"
        db.commit()

    def list_campuses(
        self,
        db: Session,
        current_user: CurrentUser,
        organization_id: UUID | None = None,
        property_id: UUID | None = None,
    ) -> list[Campus]:
        query = select(Campus).where(Campus.deleted_at.is_(None))
        if property_id is not None:
            property_record = self.get_property(db, property_id, current_user)
            query = query.where(Campus.property_id == property_record.id)
        elif organization_id is not None:
            ensure_organization_access(current_user, organization_id)
            query = query.where(Campus.organization_id == organization_id)
        elif not current_user.is_platform_admin and current_user.current_organization_id:
            query = query.where(Campus.organization_id == UUID(current_user.current_organization_id))
        campuses = list(db.scalars(query.order_by(Campus.name)).all())
        self._attach_campus_counts(db, campuses)
        return campuses

    def create_campus(self, db: Session, payload: CampusCreate, current_user: CurrentUser) -> Campus:
        ensure_organization_access(current_user, payload.organization_id)
        self._validate_campus(payload.campus_type, payload.status)
        if payload.property_id is not None:
            property_record = self.get_property(db, payload.property_id, current_user)
            if property_record.organization_id != payload.organization_id:
                raise validation_error("Campus property must belong to the same organization.")
        campus = Campus(**payload.model_dump())
        db.add(campus)
        db.commit()
        db.refresh(campus)
        self._attach_campus_counts(db, [campus])
        return campus

    def get_campus(self, db: Session, campus_id: UUID, current_user: CurrentUser) -> Campus:
        campus = db.scalar(select(Campus).where(Campus.id == campus_id, Campus.deleted_at.is_(None)))
        if campus is None:
            raise not_found("Campus not found.")
        ensure_organization_access(current_user, campus.organization_id)
        self._attach_campus_counts(db, [campus])
        return campus

    def update_campus(self, db: Session, campus_id: UUID, payload: CampusUpdate, current_user: CurrentUser) -> Campus:
        campus = self.get_campus(db, campus_id, current_user)
        values = payload.model_dump(exclude_unset=True)
        self._validate_campus(values.get("campus_type"), values.get("status"))
        if "property_id" in values and values["property_id"] is not None:
            property_record = self.get_property(db, values["property_id"], current_user)
            if property_record.organization_id != campus.organization_id:
                raise validation_error("Campus property must belong to the same organization.")
        for key, value in values.items():
            setattr(campus, key, value)
        db.commit()
        db.refresh(campus)
        self._attach_campus_counts(db, [campus])
        return campus

    def soft_delete_campus(self, db: Session, campus_id: UUID, current_user: CurrentUser) -> None:
        campus = self.get_campus(db, campus_id, current_user)
        campus.deleted_at = datetime.now(timezone.utc)
        campus.status = "archived"
        db.commit()

    def assign_building(self, db: Session, building_id: UUID, payload: BuildingAssignment, current_user: CurrentUser) -> Building:
        building = db.scalar(select(Building).where(Building.id == building_id, Building.deleted_at.is_(None)))
        if building is None:
            raise not_found("Building not found.")
        ensure_organization_access(current_user, building.organization_id)
        property_id = payload.property_id
        campus_id = payload.campus_id

        if campus_id is not None:
            campus = self.get_campus(db, campus_id, current_user)
            if campus.organization_id != building.organization_id:
                raise validation_error("Campus must belong to the same organization as the building.")
            if property_id is None:
                property_id = campus.property_id
            elif campus.property_id is not None and campus.property_id != property_id:
                raise validation_error("Campus must belong to the selected property.")

        if property_id is not None:
            property_record = self.get_property(db, property_id, current_user)
            if property_record.organization_id != building.organization_id:
                raise validation_error("Property must belong to the same organization as the building.")

        building.property_id = property_id
        building.campus_id = campus_id
        db.commit()
        db.refresh(building)
        return building

    def get_summary(self, db: Session, current_user: CurrentUser, organization_id: UUID | None = None) -> dict:
        building_query = select(Building).where(Building.deleted_at.is_(None))
        property_query = select(Property).where(Property.deleted_at.is_(None))
        campus_query = select(Campus).where(Campus.deleted_at.is_(None))
        if organization_id is not None:
            ensure_organization_access(current_user, organization_id)
            building_query = building_query.where(Building.organization_id == organization_id)
            property_query = property_query.where(Property.organization_id == organization_id)
            campus_query = campus_query.where(Campus.organization_id == organization_id)
        elif not current_user.is_platform_admin and current_user.current_organization_id:
            current_org = UUID(current_user.current_organization_id)
            building_query = building_query.where(Building.organization_id == current_org)
            property_query = property_query.where(Property.organization_id == current_org)
            campus_query = campus_query.where(Campus.organization_id == current_org)

        properties = db.scalar(select(func.count()).select_from(property_query.subquery())) or 0
        campuses = db.scalar(select(func.count()).select_from(campus_query.subquery())) or 0
        assigned_buildings = db.scalar(select(func.count()).select_from(building_query.where(Building.property_id.is_not(None)).subquery())) or 0
        unassigned_buildings = db.scalar(select(func.count()).select_from(building_query.where(Building.property_id.is_(None)).subquery())) or 0
        return {
            "properties": properties,
            "campuses": campuses,
            "assigned_buildings": assigned_buildings,
            "unassigned_buildings": unassigned_buildings,
        }

    def _attach_property_counts(self, db: Session, properties: list[Property]) -> None:
        for property_record in properties:
            property_record.campus_count = db.scalar(
                select(func.count(Campus.id)).where(Campus.property_id == property_record.id, Campus.deleted_at.is_(None))
            ) or 0
            property_record.building_count = db.scalar(
                select(func.count(Building.id)).where(Building.property_id == property_record.id, Building.deleted_at.is_(None))
            ) or 0

    def _attach_campus_counts(self, db: Session, campuses: list[Campus]) -> None:
        for campus in campuses:
            campus.building_count = db.scalar(
                select(func.count(Building.id)).where(Building.campus_id == campus.id, Building.deleted_at.is_(None))
            ) or 0

    @staticmethod
    def _validate_property(property_type: str | None, status: str | None) -> None:
        if property_type is not None and property_type not in PROPERTY_TYPES:
            raise validation_error("Property type is not defined for M6.")
        if status is not None and status not in PROPERTY_STATUSES:
            raise validation_error("Property status is not defined for M6.")

    @staticmethod
    def _validate_campus(campus_type: str | None, status: str | None) -> None:
        if campus_type is not None and campus_type not in CAMPUS_TYPES:
            raise validation_error("Campus type is not defined for M6.")
        if status is not None and status not in PROPERTY_STATUSES:
            raise validation_error("Campus status is not defined for M6.")


property_service = PropertyService()
