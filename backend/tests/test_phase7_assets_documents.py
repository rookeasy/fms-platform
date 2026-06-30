from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.main import app


def asset_record(asset_id=None, organization_id=None, building_id=None):
    return SimpleNamespace(
        id=asset_id or uuid4(),
        organization_id=organization_id or uuid4(),
        building_id=building_id or uuid4(),
        asset_type_id=uuid4(),
        asset_type=SimpleNamespace(
            id=uuid4(),
            name="Wet Sprinkler System",
            code="wet_sprinkler_system",
            category="sprinkler",
            description=None,
            default_inspection_frequency_months=None,
        ),
        name="Main wet system",
        asset_tag="A-100",
        location_description="Mechanical room",
        manufacturer=None,
        model=None,
        serial_number=None,
        status="active",
        installation_date=None,
        warranty_expiry_date=None,
        condition_rating="good",
        inspection_frequency_months=None,
        last_inspected_at=None,
        next_inspection_due_at=None,
        replacement_cost_estimate=None,
        remaining_useful_life_years=None,
        notes=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def document_record(document_id=None, building_id=None, is_passport_record=True, version_number=1, parent_document_id=None):
    organization_id = uuid4()
    return SimpleNamespace(
        id=document_id or uuid4(),
        organization_id=organization_id,
        building_id=building_id or uuid4(),
        asset_id=None,
        document_type="drawing",
        title="Riser drawing",
        description=None,
        original_filename="riser.pdf",
        storage_bucket="fms-local-documents",
        storage_key="buildings/riser.pdf",
        file_mime_type="application/pdf",
        file_size_bytes=12,
        version_number=version_number,
        parent_document_id=parent_document_id,
        generated_by_system=False,
        effective_date=None,
        expiry_date=None,
        is_public_to_client=False,
        is_passport_record=is_passport_record,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def test_asset_crud_routes_delegate_to_asset_service(monkeypatch) -> None:
    created_asset = asset_record()
    calls = []

    class FakeAssetService:
        def list_assets(self, db, current_user, organization_id=None, building_id=None):
            calls.append(("list", building_id))
            return [created_asset]

        def create_asset(self, db, building_id, payload, current_user):
            calls.append(("create", building_id, payload.name))
            return created_asset

        def update_asset(self, db, asset_id, payload, current_user):
            calls.append(("update", asset_id, payload.status))
            return created_asset

        def soft_delete_asset(self, db, asset_id, current_user):
            calls.append(("delete", asset_id))

    from app.api.v1.routes import assets

    monkeypatch.setattr(assets, "asset_service", FakeAssetService())
    client = TestClient(app)
    building_id = uuid4()
    asset_id = UUID(str(created_asset.id))

    assert client.get(f"/api/v1/buildings/{building_id}/assets").status_code == 200
    assert client.post(
        f"/api/v1/buildings/{building_id}/assets",
        json={"asset_type_id": str(created_asset.asset_type_id), "name": "Main wet system", "status": "active"},
    ).status_code == 200
    assert client.patch(f"/api/v1/assets/{asset_id}", json={"status": "inactive"}).status_code == 200
    assert client.delete(f"/api/v1/assets/{asset_id}").status_code == 204
    assert calls[0] == ("list", building_id)
    assert calls[1] == ("create", building_id, "Main wet system")
    assert calls[2] == ("update", asset_id, "inactive")
    assert calls[3] == ("delete", asset_id)


def test_document_metadata_crud_routes_delegate_to_document_service(monkeypatch) -> None:
    document = document_record()
    calls = []

    class FakeDocumentService:
        def list_documents(self, db, current_user, organization_id=None, building_id=None, **filters):
            calls.append(("list", building_id, filters.get("is_passport_record")))
            return [document]

        def create_metadata(self, db, building_id, payload, current_user):
            calls.append(("create", building_id, payload.title))
            return document

        def update_document(self, db, document_id, payload, current_user):
            calls.append(("update", document_id, payload.title))
            return document

        def soft_delete_document(self, db, document_id, current_user):
            calls.append(("delete", document_id))

    from app.api.v1.routes import documents

    monkeypatch.setattr(documents, "document_service", FakeDocumentService())
    client = TestClient(app)
    building_id = UUID(str(document.building_id))
    document_id = UUID(str(document.id))

    assert client.get(f"/api/v1/buildings/{building_id}/documents?is_passport_record=true").status_code == 200
    assert client.post(
        f"/api/v1/buildings/{building_id}/documents",
        json={"document_type": "drawing", "title": "Riser drawing", "is_passport_record": True},
    ).status_code == 200
    assert client.patch(f"/api/v1/documents/{document_id}", json={"title": "Updated drawing"}).status_code == 200
    assert client.delete(f"/api/v1/documents/{document_id}").status_code == 204
    assert calls[0] == ("list", building_id, True)
    assert calls[1] == ("create", building_id, "Riser drawing")
    assert calls[2] == ("update", document_id, "Updated drawing")
    assert calls[3] == ("delete", document_id)


def test_passport_endpoint_includes_passport_documents(monkeypatch) -> None:
    building_id = uuid4()
    passport_document = document_record(building_id=building_id, is_passport_record=True)

    class FakePassportService:
        def get_passport(self, db, requested_building_id, current_user):
            assert requested_building_id == building_id
            return {
                "building": {
                    "id": str(building_id),
                    "organization_id": str(uuid4()),
                    "bpid": "FMS-BLDG-000001",
                    "name": "Demo",
                    "address_line_1": "1 Main",
                    "city": "Toronto",
                    "province_state": "ON",
                    "country": "Canada",
                    "building_type": "commercial",
                    "status": "active",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                },
                "contacts": [],
                "assets": [],
                "documents": [passport_document],
                "timeline": [],
                "health_score": {"status": "not_calculated", "score": None},
                "membership": {"status": "not_configured", "plan": None},
            }

    from app.api.v1.routes import passport

    monkeypatch.setattr(passport, "passport_service", FakePassportService())
    response = TestClient(app).get(f"/api/v1/buildings/{building_id}/passport")

    assert response.status_code == 200
    assert response.json()["data"]["documents"][0]["is_passport_record"] is True


def test_document_list_passes_tenant_scoping_inputs(monkeypatch) -> None:
    organization_id = uuid4()
    observed = {}

    class FakeDocumentService:
        def list_documents(self, db, current_user, organization_id=None, building_id=None, **filters):
            observed["organization_id"] = organization_id
            observed["building_id"] = building_id
            return []

    from app.api.v1.routes import documents

    monkeypatch.setattr(documents, "document_service", FakeDocumentService())
    response = TestClient(app).get(f"/api/v1/documents?organization_id={organization_id}")

    assert response.status_code == 200
    assert observed == {"organization_id": organization_id, "building_id": None}


def test_document_version_upload_preserves_parent_family(monkeypatch, tmp_path) -> None:
    parent = document_record()
    child = document_record(parent_document_id=parent.id, version_number=2)
    observed = {}

    class FakeDocumentService:
        def get_document(self, db, document_id, current_user):
            return parent

        def upload_document(self, db, building_id, payload, current_user, content, filename, content_type, parent_document_id=None):
            observed["parent_document_id"] = parent_document_id
            observed["building_id"] = building_id
            return child

    from app.api.v1.routes import documents

    monkeypatch.setattr(documents, "document_service", FakeDocumentService())
    upload_path = tmp_path / "replacement.pdf"
    upload_path.write_bytes(b"replacement")
    with upload_path.open("rb") as upload:
        response = TestClient(app).post(
            f"/api/v1/documents/{parent.id}/new-version",
            data={"title": "Riser drawing", "document_type": "drawing"},
            files={"file": ("replacement.pdf", upload, "application/pdf")},
        )

    assert response.status_code == 200
    assert response.json()["data"]["version_number"] == 2
    assert observed == {"parent_document_id": parent.id, "building_id": parent.building_id}
