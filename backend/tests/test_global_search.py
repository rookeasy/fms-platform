from fastapi.testclient import TestClient

from app.main import app


def test_global_search_route_delegates_to_service(monkeypatch) -> None:
    observed = {}

    class FakeSearchService:
        def search(self, db, current_user, query, result_type=None, limit=25):
            observed["query"] = query
            observed["result_type"] = result_type
            observed["limit"] = limit
            return [
                {
                    "id": "FMS-BLDG-000001",
                    "type": "building",
                    "title": "SOHO Phase I / Building A",
                    "subtitle": "FMS-BLDG-000001 - 505-517 Highland Road West",
                    "matched_field": "bpid",
                    "url": "/buildings/FMS-BLDG-000001",
                }
            ]

    from app.api.v1.routes import search

    monkeypatch.setattr(search, "search_service", FakeSearchService())
    response = TestClient(app).get("/api/v1/search?q=FMS-BLDG-000001&type=building&limit=10")

    assert response.status_code == 200
    assert observed == {"query": "FMS-BLDG-000001", "result_type": "building", "limit": 10}
    assert response.json()["data"][0]["matched_field"] == "bpid"


def test_global_search_empty_query_returns_empty_results(monkeypatch) -> None:
    class FakeSearchService:
        def search(self, db, current_user, query, result_type=None, limit=25):
            return []

    from app.api.v1.routes import search

    monkeypatch.setattr(search, "search_service", FakeSearchService())
    response = TestClient(app).get("/api/v1/search?q=")

    assert response.status_code == 200
    assert response.json() == {"data": []}
