from datetime import datetime, timezone
import re
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
from app.core.constants import ORGANIZATION_TYPES, USER_STATUSES
from app.models import Organization
from app.schemas.core import OrganizationCreate, OrganizationUpdate
from app.services.exceptions import not_found, validation_error
from app.services.tenant import ensure_organization_access


class OrganizationService:
    def list_organizations(self, db: Session, current_user: CurrentUser) -> list[Organization]:
        query = select(Organization).where(Organization.deleted_at.is_(None))
        if not current_user.is_platform_admin and current_user.current_organization_id:
            query = query.where(Organization.id == UUID(current_user.current_organization_id))
        return list(db.scalars(query.order_by(Organization.name)).all())

    def get_organization(self, db: Session, organization_id: UUID, current_user: CurrentUser) -> Organization:
        ensure_organization_access(current_user, organization_id)
        organization = db.scalar(
            select(Organization).where(
                Organization.id == organization_id,
                Organization.deleted_at.is_(None),
            )
        )
        if organization is None:
            raise not_found("Organization not found.")
        return organization

    def create_organization(self, db: Session, payload: OrganizationCreate) -> Organization:
        self._validate_organization_type(payload.organization_type)
        self._validate_status(payload.status)
        organization = Organization(**payload.model_dump(), slug=self._unique_slug(db, payload.name))
        db.add(organization)
        db.commit()
        db.refresh(organization)
        return organization

    def update_organization(
        self,
        db: Session,
        organization_id: UUID,
        payload: OrganizationUpdate,
        current_user: CurrentUser,
    ) -> Organization:
        organization = self.get_organization(db, organization_id, current_user)
        values = payload.model_dump(exclude_unset=True)
        if "organization_type" in values:
            self._validate_organization_type(values["organization_type"])
        if "status" in values:
            self._validate_status(values["status"])
        for key, value in values.items():
            setattr(organization, key, value)
        db.commit()
        db.refresh(organization)
        return organization

    def soft_delete_organization(self, db: Session, organization_id: UUID, current_user: CurrentUser) -> None:
        organization = self.get_organization(db, organization_id, current_user)
        organization.deleted_at = datetime.now(timezone.utc)
        organization.status = "deleted"
        db.commit()

    @staticmethod
    def _validate_organization_type(value: str) -> None:
        if value not in ORGANIZATION_TYPES:
            raise validation_error("Organization type is not defined in FMS-0010.")

    @staticmethod
    def _validate_status(value: str) -> None:
        if value not in USER_STATUSES:
            raise validation_error("Organization status is not defined in FMS-0010.")

    @staticmethod
    def _slugify(value: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
        return slug or "organization"

    def _unique_slug(self, db: Session, value: str) -> str:
        base_slug = self._slugify(value)
        slug = base_slug
        counter = 2
        while db.scalar(select(Organization).where(Organization.slug == slug)) is not None:
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug


organization_service = OrganizationService()
