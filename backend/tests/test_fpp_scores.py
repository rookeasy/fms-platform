from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def _score(target_id):
    return {
        "protectionScore": 87,
        "complianceScore": 94,
        "readinessScore": 91,
        "intelligenceScore": 78,
        "buildingHealthIndex": 88,
        "scoreDrivers": [
            "Annual sprinkler inspection is current.",
            "2 open deficiencies remain unresolved.",
            "As-built drawings uploaded.",
        ],
        "lastCalculatedAt": datetime.now(timezone.utc),
        "targetType": "building",
        "targetId": target_id,
        "buildingId": target_id,
    }


def test_building_scores_route_delegates_to_service(monkeypatch) -> None:
    building_id = uuid4()
    observed = {}

    class FakeFppScoreService:
        def get_building_scores(self, db, requested_building_id, current_user):
            observed["building_id"] = requested_building_id
            return _score(requested_building_id)

    from app.api.v1.routes import scores

    monkeypatch.setattr(scores, "fpp_score_service", FakeFppScoreService())
    response = TestClient(app).get(f"/api/v1/buildings/{building_id}/scores")

    assert response.status_code == 200
    assert observed["building_id"] == building_id
    assert response.json()["data"]["buildingHealthIndex"] == 88
    assert "2 open deficiencies" in response.json()["data"]["scoreDrivers"][1]


def test_building_health_index_route_delegates_to_service(monkeypatch) -> None:
    building_id = uuid4()

    class FakeFppScoreService:
        def get_building_health_index(self, db, requested_building_id, current_user):
            assert requested_building_id == building_id
            return _score(requested_building_id)

    from app.api.v1.routes import scores

    monkeypatch.setattr(scores, "fpp_score_service", FakeFppScoreService())
    response = TestClient(app).get(f"/api/v1/buildings/{building_id}/health-index")

    assert response.status_code == 200
    assert response.json()["data"]["protectionScore"] == 87


def test_portfolio_scores_route_delegates_to_service(monkeypatch) -> None:
    building_id = uuid4()

    class FakeFppScoreService:
        def get_portfolio_scores(self, db, current_user, organization_id=None):
            return {
                "protectionScore": 87,
                "complianceScore": 94,
                "readinessScore": 91,
                "intelligenceScore": 78,
                "buildingHealthIndex": 88,
                "scoreDrivers": ["1 building(s) included in portfolio scoring."],
                "lastCalculatedAt": datetime.now(timezone.utc),
                "buildingCount": 1,
                "buildings": [
                    {
                        **_score(building_id),
                        "buildingName": "SOHO Phase I / Building A",
                    }
                ],
            }

    from app.api.v1.routes import scores

    monkeypatch.setattr(scores, "fpp_score_service", FakeFppScoreService())
    response = TestClient(app).get("/api/v1/portfolio/scores")

    assert response.status_code == 200
    assert response.json()["data"]["buildingCount"] == 1
    assert response.json()["data"]["buildings"][0]["buildingName"] == "SOHO Phase I / Building A"
