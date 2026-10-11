"""
Unit Tests for Asset Breakdown, Idle Load, and Leak Detection (R5, R6, R7).
"""

from src.analytics.idle_waste import diagnostic_engine

def test_asset_breakdown():
    res = diagnostic_engine.get_asset_breakdown("2026-Q3")
    assert res["total_facility_kwh"] > 0
    assert len(res["assets"]) >= 6
    assert res["top_user"] in [a["asset"] for a in res["assets"]]
    assert 0 <= res["unmetered_share_pct"] <= 7.0

def test_compressor_leak_detection():
    leak_res = diagnostic_engine.detect_compressor_leak("2026-Q3")
    assert leak_res["leak_detected"] is True
    # Night share in Q3 indicates leak
    assert 0.30 <= leak_res["compressors_night_share"] <= 0.45
    assert leak_res["annual_wasted_kwh_range"][0] > 0
    assert "evidence" in leak_res["location_evidence"].lower() or "meter" in leak_res["location_evidence"].lower()

def test_idle_load_analysis():
    idle_res = diagnostic_engine.analyze_idle_load("2026-Q3")
    assert idle_res["idle_hours"] > 0
    assert idle_res["total_idle_kwh"] > 0
    assert len(idle_res["idle_by_asset"]) > 0
