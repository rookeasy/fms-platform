from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
from app.core.constants import ORGANIZATION_USER_STATUSES, USER_ROLES, USER_STATUSES
from app.models import Organization, OrganizationUser, Role, User
from app.schemas.core import OrganizationUserCreate, OrganizationUserUpdate, UserCreate, UserInvite, UserUpdate
from app.services.exceptions import conflict, not_found, validation_error
from app.services.tenant import ensure_organization_access


class UserService:
    def list_users(self, db: Session, current_user: CurrentUser, organization_id: UUID | None = None) -> list[User]:
        query = select(User).where(User.deleted_at.is_(None))
        if organization_id is not None:
            ensure_organization_access(current_user, organization_id)
            query = query.join(OrganizationUser).where(OrganizationUser.organization_id == organization_id)
        return list(db.scalars(query.order_by(User.email)).unique().all())

    def get_user(self, db: Session, user_id: UUID) -> User:
        user = db.scalar(select(User).where(User.id == user_id, User.deleted_at.is_(None)))
        if user is None:
            raise not_found("User not found.")
        return user

    def create_user(self, db: Session, payload: UserCreate) -> User:
        self._validate_user_status(payload.status)
        existing_user = db.scalar(select(User).where(User.email == payload.email, User.deleted_at.is_(None)))
        if existing_user is not None:
            raise conflict("User email already exists.")
        user = User(**payload.model_dump(), full_name=self._full_name(payload.first_name, payload.last_name))
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def invite_user(self, db: Session, payload: UserInvite, current_user: CurrentUser) -> User:
        ensure_organization_access(current_user, payload.organization_id)
        self._validate_role_name(payload.role)
        organization = db.get(Organization, payload.organization_id)
        if organization is None or organization.deleted_at is not None:
            raise not_found("Organization not found.")

        user = db.scalar(select(User).where(User.email == payload.email, User.deleted_at.is_(None)))
        if user is None:
            user = User(
                email=payload.email,
                first_name=payload.first_name,
                last_name=payload.last_name,
                full_name=self._full_name(payload.first_name, payload.last_name),
                status="invited",
            )
            db.add(user)
            db.flush()

        role = db.scalar(select(Role).where(Role.name == payload.role))
        if role is None:
            raise not_found("Role not found.")

        existing_membership = db.scalar(
            select(OrganizationUser).where(
                OrganizationUser.organization_id == payload.organization_id,
                OrganizationUser.user_id == user.id,
                OrganizationUser.role_id == role.id,
            )
        )
        if existing_membership is None:
            db.add(
                OrganizationUser(
                    organization_id=payload.organization_id,
                    user_id=user.id,
                    role_id=role.id,
                    status="invited",
                    invited_at=datetime.now(timezone.utc),
                )
            )
        db.commit()
        db.refresh(user)
        return user

    def update_user(self, db: Session, user_id: UUID, payload: UserUpdate) -> User:
        user = self.get_user(db, user_id)
        values = payload.model_dump(exclude_unset=True)
        if "status" in values:
            self._validate_user_status(values["status"])
        for key, value in values.items():
            setattr(user, key, value)
        if "first_name" in values or "last_name" in values:
            user.full_name = self._full_name(user.first_name, user.last_name)
        db.commit()
        db.refresh(user)
        return user

    def soft_delete_user(self, db: Session, user_id: UUID) -> None:
        user = self.get_user(db, user_id)
        user.deleted_at = datetime.now(timezone.utc)
        user.status = "deleted"
        db.commit()

    def list_roles(self, db: Session) -> list[Role]:
        return list(db.scalars(select(Role).order_by(Role.name)).all())

    def list_organization_users(
        self,
        db: Session,
        current_user: CurrentUser,
        organization_id: UUID | None = None,
    ) -> list[OrganizationUser]:
        query = select(OrganizationUser).where(OrganizationUser.status != "deleted")
        if organization_id is not None:
            ensure_organization_access(current_user, organization_id)
            query = query.where(OrganizationUser.organization_id == organization_id)
        elif not current_user.is_platform_admin and current_user.current_organization_id:
            query = query.where(OrganizationUser.organization_id == UUID(current_user.current_organization_id))
        return list(db.scalars(query.order_by(OrganizationUser.created_at)).all())

    def assign_organization_user(self, db: Session, payload: OrganizationUserCreate, current_user: CurrentUser) -> OrganizationUser:
        ensure_organization_access(current_user, payload.organization_id)
        self._validate_organization_user_status(payload.status)
        organization = db.get(Organization, payload.organization_id)
        user = db.get(User, payload.user_id)
        role = db.get(Role, payload.role_id)
        if organization is None or organization.deleted_at is not None:
            raise not_found("Organization not found.")
        if user is None or user.deleted_at is not None:
            raise not_found("User not found.")
        if role is None:
            raise not_found("Role not found.")

        existing_membership = db.scalar(
            select(OrganizationUser).where(
                OrganizationUser.organization_id == payload.organization_id,
                OrganizationUser.user_id == payload.user_id,
                OrganizationUser.role_id == payload.role_id,
            )
        )
        if existing_membership is not None:
            if existing_membership.status == "deleted":
                existing_membership.status = payload.status
                db.commit()
                db.refresh(existing_membership)
            return existing_membership

        membership = OrganizationUser(**payload.model_dump())
        db.add(membership)
        db.commit()
        db.refresh(membership)
        return membership

    def update_organization_user(
        self,
        db: Session,
        organization_user_id: UUID,
        payload: OrganizationUserUpdate,
        current_user: CurrentUser,
    ) -> OrganizationUser:
        membership = self.get_organization_user(db, organization_user_id, current_user)
        values = payload.model_dump(exclude_unset=True)
        if "status" in values:
            self._validate_organization_user_status(values["status"])
        for key, value in values.items():
            setattr(membership, key, value)
        db.commit()
        db.refresh(membership)
        return membership

    def remove_organization_user(self, db: Session, organization_user_id: UUID, current_user: CurrentUser) -> None:
        membership = self.get_organization_user(db, organization_user_id, current_user)
        membership.status = "deleted"
        db.commit()

    def get_organization_user(self, db: Session, organization_user_id: UUID, current_user: CurrentUser) -> OrganizationUser:
        membership = db.get(OrganizationUser, organization_user_id)
        if membership is None:
            raise not_found("Organization user not found.")
        ensure_organization_access(current_user, membership.organization_id)
        return membership

    @staticmethod
    def _validate_user_status(value: str) -> None:
        if value not in USER_STATUSES:
            raise validation_error("User status is not defined in FMS-0010.")

    @staticmethod
    def _validate_organization_user_status(value: str) -> None:
        if value not in ORGANIZATION_USER_STATUSES:
            raise validation_error("Organization user status is not defined in FMS-0010.")

    @staticmethod
    def _validate_role_name(value: str) -> None:
        if value not in USER_ROLES:
            raise validation_error("Role is not defined in FMS-0010.")

    @staticmethod
    def _full_name(first_name: str | None, last_name: str | None) -> str | None:
        return " ".join(part for part in [first_name, last_name] if part) or None


user_service = UserService()
