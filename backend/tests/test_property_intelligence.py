from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def test_property_intelligence_route_returns_rollup(monkeypatch) -> None:
    property_id = uuid4()
    organization_id = uuid4()

    class FakePropertyIntelligenceService:
        def get_intelligence(self, db, requested_property_id, current_user):
            assert requested_property_id == property_id
            return {
                "property": SimpleNamespace(
                    id=property_id,
                    organization_id=organization_id,
                    name="SOHO Phase I",
                    property_type="multi_building_residential_development",
                    status="active",
                    address_line_1="505-517 Highland Road West",
                    address_line_2=None,
                    city="Stoney Creek",
                    province_state="Ontario",
                    postal_code=None,
                    country="Canada",
                    owner_name=None,
                    property_manager_name=None,
                    notes=None,
                    campus_count=1,
                    building_count=3,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                ),
                "calculated_at": datetime.now(timezone.utc),
                "health": {"score": 95, "label": "Property Health", "status": "strong", "drivers": []},
                "confidence": {"score": 100, "label": "Property Confidence Index", "status": "strong", "drivers": []},
                "risk": {"score": 0, "label": "Property Risk", "status": "low", "drivers": []},
                "readiness": {"score": 100, "label": "Property Readiness", "status": "strong", "drivers": []},
                "passport": {"score": 100, "label": "Property Passport", "status": "strong", "drivers": []},
                "executive_summary": "SOHO Phase I intelligence summary.",
                "counts": [{"label": "Buildings", "value": 2, "status": "neutral"}],
                "buildings": [],
                "passport_summary": {"passport_records": 10},
                "capital_summary": {"replacement_cost_estimate": 0},
                "deficiency_summary": {"open": 0},
                "readiness_checklist": [{"label": "Assets are registered", "complete": True}],
                "executive_review": {"status": "placeholder"},
            }

    from app.api.v1.routes import property_intelligence

    monkeypatch.setattr(property_intelligence, "property_intelligence_service", FakePropertyIntelligenceService())
    response = TestClient(app).get(f"/api/v1/properties/{property_id}/intelligence")

    assert response.status_code == 200
    assert response.json()["data"]["property"]["name"] == "SOHO Phase I"
    assert response.json()["data"]["health"]["score"] == 95
