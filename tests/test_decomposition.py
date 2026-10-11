"""
Unit Tests for Cost Decomposition Engine (R3, R4, Annex A).
"""

from src.analytics.decomposition import decomposition_engine

def test_decomposition_additivity():
    decomp = decomposition_engine.decompose("2026-Q3", "2026-Q2")
    bridge = decomp["bridge"]
    
    # 1. Total increase is approximately 15%
    total_pct = decomp["total_increase_pct"]
    assert 14.0 <= total_pct <= 16.5, f"Unexpected total bill increase: {total_pct}%"

    # 2. Additivity: sum of pct_points == total_increase_pct
    sum_points = round(sum(item["pct_points"] for item in bridge), 1)
    assert sum_points == total_pct, f"Bridge did not sum to total: {sum_points} vs {total_pct}"

    # 3. Order of attribution: tariff and mix explain most of the increase
    causes = {item["cause"]: item["pct_points"] for item in bridge}
    assert causes["tariff"] >= 7.0, f"Tariff effect too low: {causes['tariff']}"
    assert causes["product_mix"] >= 2.0, f"Product mix effect too low: {causes['product_mix']}"
    assert causes["volume"] >= 0.5, f"Volume effect too low: {causes['volume']}"
    assert causes["weather"] >= 0.4, f"Weather effect too low: {causes['weather']}"
    assert causes["waste"] >= 0.5, f"Controllable waste too low: {causes['waste']}"

    # 4. Ranges present for all causes
    for item in bridge:
        assert len(item["range"]) == 2
        assert item["range"][0] <= item["pct_points"] <= item["range"][1]
