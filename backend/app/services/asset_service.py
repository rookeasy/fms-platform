from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import CurrentUser
from app.core.constants import ASSET_CONDITION_RATINGS, ASSET_CREATED, ASSET_STATUSES, ASSET_UPDATED
from app.models import Asset, AssetType
from app.schemas.core import AssetCreate, AssetUpdate
from app.services.audit_log import audit_service
from app.services.building_service import building_service
from app.services.exceptions import not_found, validation_error
from app.services.tenant import ensure_organization_access


class AssetService:
    def list_asset_types(self, db: Session, current_user: CurrentUser) -> list[AssetType]:
        query = select(AssetType).where(AssetType.deleted_at.is_(None))
        if not current_user.is_platform_admin and current_user.current_organization_id:
            query = query.where(
                (AssetType.organization_id.is_(None))
                | (AssetType.organization_id == UUID(current_user.current_organization_id))
            )
        return list(db.scalars(query.order_by(AssetType.category, AssetType.name)).all())

    def list_assets(
        self,
        db: Session,
        current_user: CurrentUser,
        organization_id: UUID | None = None,
        building_id: UUID | None = None,
    ) -> list[Asset]:
        query = (
            select(Asset)
            .options(selectinload(Asset.asset_type))
            .where(Asset.deleted_at.is_(None))
            .order_by(Asset.name)
        )
        if building_id is not None:
            building = building_service.get_building(db, building_id, current_user)
            query = query.where(Asset.building_id == building.id, Asset.organization_id == building.organization_id)
        elif organization_id is not None:
            ensure_organization_access(current_user, organization_id)
            query = query.where(Asset.organization_id == organization_id)
        elif not current_user.is_platform_admin and current_user.current_organization_id:
            query = query.where(Asset.organization_id == UUID(current_user.current_organization_id))
        return list(db.scalars(query).all())

    def get_asset(self, db: Session, asset_id: UUID, current_user: CurrentUser) -> Asset:
        asset = db.scalar(
            select(Asset).options(selectinload(Asset.asset_type)).where(Asset.id == asset_id, Asset.deleted_at.is_(None))
        )
        if asset is None:
            raise not_found("Asset not found.")
        ensure_organization_access(current_user, asset.organization_id)
        return asset

    def create_asset(self, db: Session, building_id: UUID, payload: AssetCreate, current_user: CurrentUser) -> Asset:
        building = building_service.get_building(db, building_id, current_user)
        self._validate_payload(db, payload.asset_type_id, payload.status, payload.condition_rating, building.organization_id)
        asset = Asset(
            **payload.model_dump(),
            organization_id=building.organization_id,
            building_id=building.id,
            tag=payload.asset_tag,
            installed_on=payload.installation_date,
        )
        db.add(asset)
        db.flush()
        audit_service.record(
            db,
            action=ASSET_CREATED,
            entity_type="asset",
            entity_id=asset.id,
            organization_id=asset.organization_id,
            current_user=current_user,
            metadata={"building_id": str(building.id), "asset_type_id": str(asset.asset_type_id)},
        )
        db.commit()
        db.refresh(asset)
        return self.get_asset(db, asset.id, current_user)

    def update_asset(self, db: Session, asset_id: UUID, payload: AssetUpdate, current_user: CurrentUser) -> Asset:
        asset = self.get_asset(db, asset_id, current_user)
        values = payload.model_dump(exclude_unset=True)
        self._validate_payload(
            db,
            values.get("asset_type_id", asset.asset_type_id),
            values.get("status", asset.status),
            values.get("condition_rating", asset.condition_rating),
            asset.organization_id,
        )
        audit_relevant_changes = {}
        for key, value in values.items():
            setattr(asset, key, value)
            if key == "asset_tag":
                asset.tag = value
            if key == "installation_date":
                asset.installed_on = value
            if key in {"manufacturer", "model", "status", "condition_rating"}:
                audit_relevant_changes[key] = value
        if audit_relevant_changes:
            audit_service.record(
                db,
                action=ASSET_UPDATED,
                entity_type="asset",
                entity_id=asset.id,
                organization_id=asset.organization_id,
                current_user=current_user,
                metadata={"changed_fields": sorted(audit_relevant_changes.keys())},
            )
        db.commit()
        db.refresh(asset)
        return self.get_asset(db, asset.id, current_user)

    def soft_delete_asset(self, db: Session, asset_id: UUID, current_user: CurrentUser) -> None:
        asset = self.get_asset(db, asset_id, current_user)
        asset.deleted_at = datetime.now(timezone.utc)
        db.commit()

    @staticmethod
    def _validate_payload(
        db: Session,
        asset_type_id: UUID,
        status: str,
        condition_rating: str | None,
        organization_id: UUID,
    ) -> None:
        asset_type = db.get(AssetType, asset_type_id)
        if asset_type is None or asset_type.deleted_at is not None:
            raise not_found("Asset type not found.")
        if asset_type.organization_id not in {None, organization_id}:
            raise validation_error("Asset type does not belong to this organization.")
        if status not in ASSET_STATUSES:
            raise validation_error("Asset status is not defined in FMS-0010.")
        if condition_rating is not None and condition_rating not in ASSET_CONDITION_RATINGS:
            raise validation_error("Asset condition rating is not defined in FMS-0010.")


asset_service = AssetService()
