"""
Unit Tests for Energy Baseline Model (R2 & Annex A).
"""

from src.analytics.baseline import baseline_model

def test_baseline_regression_fit():
    metrics = baseline_model.fit("2026-Q2")
    assert metrics["r2"] >= 0.85, f"R2 too low: {metrics['r2']}"
    assert metrics["sample_days"] >= 90
    assert "Product_A" in metrics["coefficients"]
    assert "cooling_degree_days" in metrics["coefficients"]
    assert metrics["rmse_kwh"] > 0
