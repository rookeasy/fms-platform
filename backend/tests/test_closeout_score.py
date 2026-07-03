from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.services.closeout_score_service import closeout_score_service


def test_building_closeout_score_route_delegates_to_service(monkeypatch) -> None:
    building_id = uuid4()
    observed = {}

    class FakeCloseoutScoreService:
        def get_building_score(self, db, requested_building_id, current_user):
            observed["building_id"] = requested_building_id
            return {
                "completion_percentage": 75,
                "total_required_items": 12,
                "completed_items": 9,
                "missing_items": ["Warranty Package"],
                "ready_for_handover": False,
                "warnings": ["Required closeout evidence is missing."],
                "sections": [
                    {
                        "key": "warranty_package",
                        "label": "Warranty Package",
                        "status": "missing",
                        "completed": False,
                        "required": True,
                        "evidence_count": 0,
                        "evidence_labels": [],
                        "missing_reason": "Missing required closeout evidence.",
                    }
                ],
            }

    from app.api.v1.routes import buildings

    monkeypatch.setattr(buildings, "closeout_score_service", FakeCloseoutScoreService())
    response = TestClient(app).get(f"/api/v1/buildings/{building_id}/closeout/score")

    assert response.status_code == 200
    assert observed["building_id"] == building_id
    assert response.json()["data"]["completion_percentage"] == 75
    assert response.json()["data"]["ready_for_handover"] is False


def test_property_closeout_score_route_delegates_to_service(monkeypatch) -> None:
    property_id = uuid4()

    class FakeCloseoutScoreService:
        def get_property_score(self, db, requested_property_id, current_user):
            assert requested_property_id == property_id
            return {
                "property_id": property_id,
                "property_name": "SOHO Phase I",
                "building_count": 1,
                "ready_building_count": 0,
                "completion_percentage": 92,
                "total_required_items": 12,
                "completed_items": 11,
                "missing_items": ["FMS Membership Invitation"],
                "ready_for_handover": False,
                "warnings": ["Required closeout evidence is missing."],
                "sections": [],
                "buildings": [
                    {
                        "building_id": uuid4(),
                        "building_name": "SOHO Phase I / Building A",
                        "completion_percentage": 92,
                        "completed_items": 11,
                        "total_required_items": 12,
                        "ready_for_handover": False,
                        "missing_items": ["FMS Membership Invitation"],
                    }
                ],
            }

    from app.api.v1.routes import properties

    monkeypatch.setattr(properties, "closeout_score_service", FakeCloseoutScoreService())
    response = TestClient(app).get(f"/api/v1/properties/{property_id}/closeout/score")

    assert response.status_code == 200
    assert response.json()["data"]["property_name"] == "SOHO Phase I"
    assert response.json()["data"]["buildings"][0]["completion_percentage"] == 92


def test_closeout_score_uses_seeded_section_descriptions(monkeypatch) -> None:
    organization_id = uuid4()
    building_id = uuid4()
    building = SimpleNamespace(
        id=building_id,
        organization_id=organization_id,
        name="SOHO Phase I / Building A",
        owner_name="SOHO Reference Owner",
        property_manager_name="SOHO Reference Property Management",
    )
    now = datetime.now(timezone.utc)

    def document(title, document_type, section, is_passport_record=True, is_public_to_client=True):
        return SimpleNamespace(
            id=uuid4(),
            organization_id=organization_id,
            building_id=building_id,
            title=title,
            name=title,
            document_type=document_type,
            description=f"Closeout section: {section}",
            is_passport_record=is_passport_record,
            is_public_to_client=is_public_to_client,
            deleted_at=None,
            created_at=now,
        )

    documents = [
        document("SOHO Building Protection Passport Index", "passport_export", "Building Protection Passport"),
        document("SOHO Drawing Register", "drawing", "Drawing Register"),
        document("SOHO Building A As-Built Drawing Package", "as_built_drawing", "As-Built Drawings"),
        document("P.Eng. Compliance Cover Sheet", "engineering_letter", "P.Eng. Compliance Package"),
        document("NFPA Contractor Closeout Checklist", "other", "NFPA Contractor Compliance Package"),
        document("Certificate", "contractors_material_test_certificate", "Material & Test Certificates"),
        document("SOHO Warranty Summary", "warranty", "Warranty Package"),
        document("SOHO Product Data and O&M Manual Index", "owner_manual", "Product Data / O&M Manuals"),
        document("SOHO Owner / Property Manager Handover Notes", "owner_manual", "Owner / Property Manager Handover"),
        document("SOHO Fuzion Fire Service ITM Transition Summary", "service_record", "Fuzion Fire Service ITM Transition"),
        document("SOHO FMS Membership Invitation", "other", "FMS Membership Invitation"),
    ]
    assets = [SimpleNamespace(id=uuid4())]

    monkeypatch.setattr(closeout_score_service, "_building_documents", lambda db, requested_building: documents)
    monkeypatch.setattr(closeout_score_service, "_building_assets", lambda db, requested_building: assets)
    monkeypatch.setattr(closeout_score_service, "_building_contacts", lambda db, requested_building: [])
    monkeypatch.setattr(closeout_score_service, "_has_active_membership", lambda db, requested_organization_id: False)

    score = closeout_score_service._calculate_building_score(None, building, None)

    assert score.completed_items == 12
    assert score.completion_percentage == 100
    assert score.ready_for_handover is True
