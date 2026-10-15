import pytest
from starlette.testclient import TestClient
from app.main import app
from app.database.db import init_db

@pytest.fixture(autouse=True)
def setup_database():
    init_db()

def test_health_endpoint():
    with TestClient(app) as client:
        res = client.get("/api/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert "Undergold" in data["competitors"]
        assert "Clement" in data["competitors"]

def test_root_serves_html():
    with TestClient(app) as client:
        res = client.get("/")
        assert res.status_code == 200
        assert "text/html" in res.headers.get("content-type", "")
        assert "PriceHunter" in res.text

def test_search_validation_empty_query():
    with TestClient(app) as client:
        res = client.post("/api/search", json={"query": "a", "competitors": ["Undergold"]})
        assert res.status_code in [400, 422]


def test_search_demo_mode():
    with TestClient(app) as client:
        payload = {
            "query": "Black oversized T-shirt",
            "competitors": ["Undergold", "Clement"],
            "demo_mode": True
        }
        res = client.post("/api/search", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["demo_mode_active"] is True
        assert len(data["products"]) > 0
        assert all(p["data_source"] == "DEMO" for p in data["products"])
        assert data["summary"]["is_comparable"] is True

def test_manual_entry_and_history():
    with TestClient(app) as client:
        # Add manual product
        manual_payload = {
            "query": "oversized test",
            "competitor": "Undergold",
            "title": "Camiseta Test Manual",
            "price_cop": 210000.0,
            "url": "https://undergoldapparel.com/test",
            "color": "Negro",
            "sizes": ["M", "L"]
        }
        res_manual = client.post("/api/manual", json=manual_payload)
        assert res_manual.status_code == 200
        
        # Check history
        res_hist = client.get("/api/history")
        assert res_hist.status_code == 200
        assert isinstance(res_hist.json(), list)

def test_csv_export():
    with TestClient(app) as client:
        prods = [
            {
                "id": "exp-1",
                "competitor": "Undergold",
                "title": "Camiseta Exportable",
                "url": "https://undergoldapparel.com",
                "price_cop": 250000.0,
                "timestamp": "2026-10-14T12:00:00",
                "sizes": ["S", "M"],
                "color": "Negro",
                "data_source": "LIVE",
                "match_confidence": "ALTA",
                "similarity_score": 90.0,
                "match_explanation": "Coincidencia de prueba"
            }
        ]
        res = client.post("/api/export/csv", json=prods)
        assert res.status_code == 200
        assert "text/csv" in res.headers.get("content-type", "")
        # Should contain CSV header columns
        content = res.content.decode("utf-8-sig")
        assert "Ranking Precio" in content
        assert "Camiseta Exportable" in content
