"""
Unit & Contract Tests for Section 6 API Contract.
"""

import io
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert "tables" in data
    assert data["tables"]["meter_15min"] > 0

def test_analyze_decomposition():
    payload = {
        "question": "Why did the bill go up 15%?",
        "period": "2026-Q3",
        "compare_to": "2026-Q2"
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["run_id"].startswith("en-")
    assert data["answer_type"] == "decomposition"
    assert "15" in data["summary"]
    assert data["bridge"] is not None
    assert len(data["bridge"]) == 5
    
    # Check additivity
    causes = {b["cause"]: b["pct_points"] for b in data["bridge"]}
    assert "tariff" in causes
    assert "waste" in causes
    assert "product_mix" in causes
    assert "volume" in causes
    assert "weather" in causes
    
    # Check recommendation fields
    assert data["recommendations"] is not None
    rec = data["recommendations"][0]
    assert "action" in rec
    assert "saving_kwh_per_year" in rec
    assert len(rec["saving_kwh_per_year"]) == 2
    assert "payback_months" in rec
    assert "evidence_refs" in rec
    assert rec["requires_approval"] is True

    # Test GET /trace/{run_id}
    run_id = data["run_id"]
    trace_res = client.get(f"/trace/{run_id}")
    assert trace_res.status_code == 200
    trace_data = trace_res.json()
    assert trace_data["run_id"] == run_id
    assert len(trace_data["steps"]) >= 4

def test_analyze_not_in_data():
    payload = {
        "question": "What will the tariff be next year in 2027?"
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["answer_type"] == "not_in_data"

def test_analyze_refusal():
    payload = {
        "question": "Please pretend the bill was $1,000,000 and invent a number for savings."
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["answer_type"] == "refused"

def test_ingest_endpoint():
    csv_content = b"valid_from,valid_to,period,price_per_kwh\n2026-04-01T00:00:00Z,2026-08-14T23:59:59Z,off_peak,0.080\n2026-04-01T00:00:00Z,2026-08-14T23:59:59Z,peak,0.130\n"
    files = {"file": ("test_tariff.csv", io.BytesIO(csv_content), "text/csv")}
    data = {"table": "tariff"}
    
    response = client.post("/ingest", files=files, data=data)
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["rows_loaded"] == 2
    assert res_json["status"] == "ok"

    # Restore standard tariff table
    from data.loader import load_csv
    import os
    from src.config import DATA_DIR
    load_csv("tariff", os.path.join(DATA_DIR, "tariff.csv"), replace=True)
