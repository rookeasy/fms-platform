from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import CurrentUser
from app.models import (
    Deficiency,
    Document,
    Inspection,
    InspectionResponse,
    InspectionTemplate,
    InspectionTemplateItem,
    WorkOrder,
)
from app.schemas.mobile import (
    MobileAssignedJobRead,
    MobileCompletionStatusPayload,
    MobileDeficiencyPayload,
    MobileInspectionItemRead,
    MobileInspectionRead,
    MobileInspectionResponsePayload,
    MobileMaterialUsedPayload,
    MobileSyncReceipt,
    MobileWorkOrderNotePayload,
)
from app.services.exceptions import not_found, validation_error
from app.services.tenant import ensure_organization_access


class MobileFieldService:
    def list_assigned_jobs(self, db: Session, current_user: CurrentUser) -> list[MobileAssignedJobRead]:
        query = (
            select(WorkOrder)
            .options(selectinload(WorkOrder.building))
            .where(WorkOrder.deleted_at.is_(None))
            .order_by(WorkOrder.created_at.desc())
        )
        if not current_user.is_platform_admin and current_user.current_organization_id:
            query = query.where(WorkOrder.organization_id == UUID(current_user.current_organization_id))
        work_orders = list(db.scalars(query).all())
        return [self._job_read(work_order) for work_order in work_orders]

    def get_job(self, db: Session, work_order_id: UUID, current_user: CurrentUser) -> MobileAssignedJobRead:
        work_order = self._get_work_order(db, work_order_id, current_user)
        return self._job_read(work_order)

    def list_inspection_forms(self, db: Session, work_order_id: UUID, current_user: CurrentUser) -> list[MobileInspectionRead]:
        work_order = self._get_work_order(db, work_order_id, current_user)
        inspections = list(
            db.scalars(
                select(Inspection)
                .options(selectinload(Inspection.template).selectinload(InspectionTemplate.items))
                .where(
                    Inspection.building_id == work_order.building_id,
                    Inspection.organization_id == work_order.organization_id,
                    Inspection.deleted_at.is_(None),
                )
                .order_by(Inspection.created_at.desc())
            ).all()
        )
        return [self._inspection_read(inspection) for inspection in inspections]

    def submit_inspection_response(
        self,
        db: Session,
        payload: MobileInspectionResponsePayload,
        current_user: CurrentUser,
    ) -> MobileSyncReceipt:
        work_order = self._get_work_order(db, payload.job_id, current_user)
        inspection = db.scalar(
            select(Inspection).where(
                Inspection.id == payload.inspection_id,
                Inspection.organization_id == work_order.organization_id,
                Inspection.building_id == work_order.building_id,
                Inspection.deleted_at.is_(None),
            )
        )
        if inspection is None:
            raise not_found("Inspection not found for this mobile job.")
        item = db.scalar(
            select(InspectionTemplateItem).where(
                InspectionTemplateItem.id == payload.inspection_template_item_id,
                InspectionTemplateItem.organization_id == work_order.organization_id,
                InspectionTemplateItem.deleted_at.is_(None),
            )
        )
        if item is None:
            raise not_found("Inspection checklist item not found.")
        response = db.scalar(
            select(InspectionResponse).where(
                InspectionResponse.inspection_id == inspection.id,
                InspectionResponse.inspection_template_item_id == item.id,
                InspectionResponse.deleted_at.is_(None),
            )
        )
        value = {
            **payload.value,
            "mobile": self._mobile_metadata(payload.technician_id, payload.job_id, payload.customer_site_id, payload.sync_status, payload.captured_at),
        }
        if response is None:
            response = InspectionResponse(
                organization_id=work_order.organization_id,
                inspection_id=inspection.id,
                inspection_template_item_id=item.id,
                value=value,
                notes=payload.notes,
            )
            db.add(response)
        else:
            response.value = value
            response.notes = payload.notes
        inspection.status = "in_progress"
        db.commit()
        db.refresh(response)
        return self._receipt(payload.technician_id, payload.job_id, payload.customer_site_id, "inspection_response", response.id)

    def create_deficiency(self, db: Session, payload: MobileDeficiencyPayload, current_user: CurrentUser) -> MobileSyncReceipt:
        work_order = self._get_work_order(db, payload.job_id, current_user)
        if payload.building_id != work_order.building_id:
            raise validation_error("Deficiency building must match the mobile job building.")
        deficiency = Deficiency(
            organization_id=work_order.organization_id,
            building_id=payload.building_id,
            asset_id=payload.asset_id,
            inspection_id=payload.inspection_id,
            assigned_to_user_id=None,
            title=payload.title,
            severity=payload.severity,
            status=payload.status,
        )
        if payload.notes:
            deficiency.title = f"{payload.title} - {payload.notes[:80]}"
        db.add(deficiency)
        db.commit()
        db.refresh(deficiency)
        return self._receipt(payload.technician_id, payload.job_id, payload.customer_site_id, "deficiency", deficiency.id)

    def add_site_notes(self, db: Session, payload: MobileWorkOrderNotePayload, current_user: CurrentUser) -> MobileSyncReceipt:
        work_order = self._get_work_order(db, payload.job_id, current_user)
        self._append_work_order_note(
            work_order,
            "Site note",
            payload.notes,
            payload.technician_id,
            payload.customer_site_id,
            payload.sync_status,
            payload.captured_at,
        )
        db.commit()
        return self._receipt(payload.technician_id, payload.job_id, payload.customer_site_id, "site_note", work_order.id)

    def add_material_used(self, db: Session, payload: MobileMaterialUsedPayload, current_user: CurrentUser) -> MobileSyncReceipt:
        work_order = self._get_work_order(db, payload.job_id, current_user)
        material_note = f"{payload.material_name} | qty={payload.quantity:g}{(' ' + payload.unit) if payload.unit else ''}"
        if payload.notes:
            material_note = f"{material_note} | {payload.notes}"
        self._append_work_order_note(
            work_order,
            "Material used",
            material_note,
            payload.technician_id,
            payload.customer_site_id,
            payload.sync_status,
            payload.captured_at,
        )
        db.commit()
        return self._receipt(payload.technician_id, payload.job_id, payload.customer_site_id, "material_used", work_order.id)

    def update_completion_status(self, db: Session, payload: MobileCompletionStatusPayload, current_user: CurrentUser) -> MobileSyncReceipt:
        work_order = self._get_work_order(db, payload.job_id, current_user)
        work_order.status = payload.status
        if payload.status in {"completed", "complete", "closed"}:
            work_order.completed_at = payload.completed_at or datetime.now(timezone.utc)
        if payload.notes:
            self._append_work_order_note(
                work_order,
                "Completion status",
                payload.notes,
                payload.technician_id,
                payload.customer_site_id,
                payload.sync_status,
                payload.completed_at,
            )
        db.commit()
        return self._receipt(payload.technician_id, payload.job_id, payload.customer_site_id, "completion_status", work_order.id)

    def attach_mobile_document(
        self,
        db: Session,
        document: Document,
        technician_id: str,
        job_id: UUID,
        customer_site_id: UUID,
        record_type: str,
    ) -> MobileSyncReceipt:
        _ = db
        return self._receipt(technician_id, job_id, customer_site_id, record_type, document.id)

    @staticmethod
    def _job_read(work_order: WorkOrder) -> MobileAssignedJobRead:
        building = work_order.building
        address = None
        if building is not None:
            address = ", ".join(
                value for value in [building.address_line_1 or building.address_line1, building.city, building.province_state, building.postal_code] if value
            )
        return MobileAssignedJobRead(
            id=work_order.id,
            organization_id=work_order.organization_id,
            building_id=work_order.building_id,
            asset_id=work_order.asset_id,
            title=work_order.title,
            description=work_order.description,
            status=work_order.status,
            priority=work_order.priority,
            due_at=work_order.due_at,
            completed_at=work_order.completed_at,
            building_name=building.name if building else None,
            site_address=address,
        )

    @staticmethod
    def _inspection_read(inspection: Inspection) -> MobileInspectionRead:
        template = inspection.template
        items = sorted(template.items, key=lambda item: item.sort_order) if template else []
        return MobileInspectionRead(
            id=inspection.id,
            organization_id=inspection.organization_id,
            building_id=inspection.building_id,
            inspection_template_id=inspection.inspection_template_id,
            status=inspection.status,
            scheduled_at=inspection.scheduled_at,
            completed_at=inspection.completed_at,
            template_name=template.name if template else None,
            items=[
                MobileInspectionItemRead(
                    id=item.id,
                    label=item.label,
                    response_type=item.response_type,
                    sort_order=item.sort_order,
                    is_required=item.is_required,
                )
                for item in items
                if item.deleted_at is None
            ],
        )

    @staticmethod
    def _append_work_order_note(
        work_order: WorkOrder,
        label: str,
        body: str,
        technician_id: str,
        customer_site_id: UUID,
        sync_status: str,
        captured_at: datetime | None,
    ) -> None:
        timestamp = (captured_at or datetime.now(timezone.utc)).isoformat()
        entry = f"[Base44 {label} | {timestamp} | technician={technician_id} | site={customer_site_id} | sync={sync_status}] {body}"
        work_order.description = "\n".join(part for part in [work_order.description, entry] if part)

    @staticmethod
    def _mobile_metadata(
        technician_id: str,
        job_id: UUID,
        customer_site_id: UUID,
        sync_status: str,
        captured_at: datetime | None,
    ) -> dict:
        return {
            "technician_id": technician_id,
            "job_id": str(job_id),
            "customer_site_id": str(customer_site_id),
            "captured_at": (captured_at or datetime.now(timezone.utc)).isoformat(),
            "sync_status": sync_status,
            "source": "base44_mobile",
        }

    @staticmethod
    def _receipt(technician_id: str, job_id: UUID, customer_site_id: UUID, record_type: str, record_id: UUID) -> MobileSyncReceipt:
        return MobileSyncReceipt(
            synced_at=datetime.now(timezone.utc),
            technician_id=technician_id,
            job_id=job_id,
            customer_site_id=customer_site_id,
            record_type=record_type,
            record_id=record_id,
        )

    @staticmethod
    def _get_work_order(db: Session, work_order_id: UUID, current_user: CurrentUser) -> WorkOrder:
        work_order = db.scalar(
            select(WorkOrder)
            .options(selectinload(WorkOrder.building))
            .where(WorkOrder.id == work_order_id, WorkOrder.deleted_at.is_(None))
        )
        if work_order is None:
            raise not_found("Mobile job not found.")
        ensure_organization_access(current_user, work_order.organization_id)
        return work_order


mobile_field_service = MobileFieldService()
