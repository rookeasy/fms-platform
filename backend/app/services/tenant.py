from uuid import UUID

from app.api.deps import CurrentUser
from app.services.exceptions import permission_denied


def ensure_organization_access(current_user: CurrentUser, organization_id: UUID) -> None:
    if current_user.is_platform_admin:
        return
    if current_user.current_organization_id != str(organization_id):
        raise permission_denied("You do not have permission to access this organization.")
