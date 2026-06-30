from uuid import UUID

from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
from app.models import AuditLog


class AuditService:
    def record(
        self,
        db: Session,
        *,
        action: str,
        entity_type: str,
        entity_id: UUID,
        organization_id: UUID | None,
        current_user: CurrentUser,
        metadata: dict | None = None,
    ) -> AuditLog:
        user_id = self._parse_user_id(current_user.id)
        audit_log = AuditLog(
            organization_id=organization_id,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata_=metadata,
        )
        db.add(audit_log)
        return audit_log

    @staticmethod
    def _parse_user_id(value: str) -> UUID | None:
        try:
            return UUID(value)
        except ValueError:
            return None


audit_service = AuditService()
