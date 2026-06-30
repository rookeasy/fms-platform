from uuid import UUID

from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
from app.schemas.core import (
    AssetRead,
    BuildingContactRead,
    BuildingRead,
    DocumentRead,
    PassportSummary,
    PassportTimelineItem,
)
from app.services.asset_service import asset_service
from app.services.building_service import building_service
from app.services.document_service import document_service


class PassportService:
    def get_passport(self, db: Session, building_id: UUID, current_user: CurrentUser) -> PassportSummary:
        building = building_service.get_building(db, building_id, current_user)
        contacts = building_service.list_contacts(db, building.id, current_user)
        assets = asset_service.list_assets(db, current_user, building_id=building.id)
        documents = document_service.list_documents(db, current_user, building_id=building.id, is_passport_record=True)
        timeline = [
            PassportTimelineItem(
                event_type="asset_created",
                label=f"Asset added: {asset.name}",
                occurred_at=asset.created_at,
                record_id=asset.id,
            )
            for asset in assets
        ] + [
            PassportTimelineItem(
                event_type="document_uploaded",
                label=f"Document uploaded: {document.title or document.name}",
                occurred_at=document.created_at,
                record_id=document.id,
            )
            for document in documents
        ]
        timeline.sort(key=lambda item: item.occurred_at, reverse=True)
        return PassportSummary(
            building=BuildingRead.model_validate(building),
            contacts=[BuildingContactRead.model_validate(contact) for contact in contacts],
            assets=[AssetRead.model_validate(asset) for asset in assets],
            documents=[DocumentRead.model_validate(document) for document in documents],
            timeline=timeline,
            health_score={"status": "not_calculated", "score": None},
            membership={"status": "not_configured", "plan": None},
        )


passport_service = PassportService()
