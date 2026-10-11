"""
Unit Tests for Prescriptive Recommendations (R8, R9, Annex A).
"""

from src.analytics.recommendations import recommendation_engine

def test_recommendation_ranges_and_ranking():
    recs = recommendation_engine.generate_recommendations("2026-Q3")
    assert len(recs) >= 3

    # Verify ranking: payback months ascending
    paybacks = [r["payback_months"][0] for r in recs]
    assert paybacks == sorted(paybacks), f"Recommendations not sorted by payback: {paybacks}"

    # Verify schema compliance for each recommendation
    for r in recs:
        assert isinstance(r["action"], str)
        assert len(r["saving_kwh_per_year"]) == 2
        assert r["saving_kwh_per_year"][0] <= r["saving_kwh_per_year"][1]
        
        assert len(r["saving_money_per_year"]) == 2
        assert r["saving_money_per_year"][0] <= r["saving_money_per_year"][1]
        
        assert len(r["saving_co2e_t_per_year"]) == 2
        assert r["saving_co2e_t_per_year"][0] <= r["saving_co2e_t_per_year"][1]
        
        assert len(r["payback_months"]) == 2
        assert r["payback_months"][0] <= r["payback_months"][1]
        
        assert r["ease"] in ("easy", "medium", "hard")
        assert len(r["evidence_refs"]) > 0
        assert r["confidence"] in ("high", "medium", "low")
        assert r["requires_approval"] is True
