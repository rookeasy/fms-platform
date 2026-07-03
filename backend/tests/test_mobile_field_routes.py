from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def test_mobile_assigned_jobs_route_delegates_to_service(monkeypatch) -> None:
    job_id = uuid4()

    class FakeMobileFieldService:
        def list_assigned_jobs(self, db, current_user):
            return [
                {
                    "id": job_id,
                    "organization_id": uuid4(),
                    "building_id": uuid4(),
                    "title": "Quarterly inspection",
                    "status": "open",
                    "priority": "medium",
                    "sync_status": "synced",
                }
            ]

    from app.api.v1.routes import mobile

    monkeypatch.setattr(mobile, "mobile_field_service", FakeMobileFieldService())
    response = TestClient(app).get("/api/v1/mobile/assigned-jobs")

    assert response.status_code == 200
    assert response.json()["data"][0]["id"] == str(job_id)


def test_mobile_deficiency_route_delegates_to_service(monkeypatch) -> None:
    job_id = uuid4()
    record_id = uuid4()
    observed = {}

    class FakeMobileFieldService:
        def create_deficiency(self, db, payload, current_user):
            observed["payload"] = payload
            return {
                "sync_status": "synced",
                "synced_at": datetime.now(timezone.utc),
                "technician_id": payload.technician_id,
                "job_id": payload.job_id,
                "customer_site_id": payload.customer_site_id,
                "record_type": "deficiency",
                "record_id": record_id,
            }

    from app.api.v1.routes import mobile

    monkeypatch.setattr(mobile, "mobile_field_service", FakeMobileFieldService())
    response = TestClient(app).post(
        "/api/v1/mobile/deficiencies",
        json={
            "job_id": str(job_id),
            "building_id": str(uuid4()),
            "customer_site_id": str(uuid4()),
            "title": "Missing escutcheon",
            "severity": "low",
            "technician_id": "tech-001",
        },
    )

    assert response.status_code == 200
    assert observed["payload"].job_id == job_id
    assert response.json()["data"]["record_type"] == "deficiency"


def test_mobile_photo_upload_stores_document_and_returns_receipt(monkeypatch) -> None:
    job_id = uuid4()
    building_id = uuid4()
    customer_site_id = uuid4()
    document_id = uuid4()
    observed = {}

    class FakeDocumentService:
        def upload_document(self, db, requested_building_id, payload, current_user, content, filename, content_type, parent_document_id=None):
            observed["building_id"] = requested_building_id
            observed["payload"] = payload
            return SimpleNamespace(id=document_id)

    class FakeMobileFieldService:
        def attach_mobile_document(self, db, document, technician_id, requested_job_id, requested_customer_site_id, record_type):
            assert document.id == document_id
            return {
                "sync_status": "synced",
                "synced_at": datetime.now(timezone.utc),
                "technician_id": technician_id,
                "job_id": requested_job_id,
                "customer_site_id": requested_customer_site_id,
                "record_type": record_type,
                "record_id": document.id,
            }

    from app.api.v1.routes import mobile

    monkeypatch.setattr(mobile, "document_service", FakeDocumentService())
    monkeypatch.setattr(mobile, "mobile_field_service", FakeMobileFieldService())
    response = TestClient(app).post(
        "/api/v1/mobile/photos",
        data={
            "job_id": str(job_id),
            "building_id": str(building_id),
            "customer_site_id": str(customer_site_id),
            "technician_id": "tech-001",
            "caption": "Riser room",
        },
        files={"file": ("field.jpg", b"image-bytes", "image/jpeg")},
    )

    assert response.status_code == 200
    assert observed["building_id"] == building_id
    assert observed["payload"].document_type == "photo"
    assert response.json()["data"]["record_type"] == "photo"
