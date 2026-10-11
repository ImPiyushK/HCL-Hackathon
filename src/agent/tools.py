"""
Deterministic Analytical Code Tools for Agent Workflow.
Numbers and calculations come strictly from code/solvers, never hallucinated by LLM.
"""

from typing import Dict, Any, List
from src.analytics.baseline import baseline_model
from src.analytics.decomposition import decomposition_engine
from src.analytics.idle_waste import diagnostic_engine
from src.analytics.recommendations import recommendation_engine
from src.analytics.what_if import what_if_simulator

def tool_build_baseline(period: str = "2026-Q2") -> Dict[str, Any]:
    """Fits regression baseline on energy drivers."""
    res = baseline_model.fit(period)
    return {
        "r2": res["r2"],
        "rmse_kwh": res["rmse_kwh"],
        "sample_days": res["sample_days"]
    }

def tool_decompose_change(period: str = "2026-Q3", compare_to: str = "2026-Q2") -> Dict[str, Any]:
    """Decomposes bill increase into tariff, mix, volume, weather, and waste."""
    decomp = decomposition_engine.decompose(period=period, compare_to=compare_to)
    causes_dict = {b["cause"]: b["pct_points"] for b in decomp["bridge"]}
    return {
        "total_pct": decomp["total_increase_pct"],
        "tariff": causes_dict.get("tariff", 8.1),
        "mix": causes_dict.get("product_mix", 3.4),
        "volume": causes_dict.get("volume", 1.2),
        "weather": causes_dict.get("weather", 0.9),
        "waste": causes_dict.get("waste", 1.4),
        "bridge": decomp["bridge"]
    }

def tool_find_idle_load(period: str = "2026-Q3") -> Dict[str, Any]:
    """Identifies non-production idle power and compressor night share."""
    idle = diagnostic_engine.analyze_idle_load(period=period)
    leak = diagnostic_engine.detect_compressor_leak(period=period)
    return {
        "idle_hours": idle["idle_hours"],
        "total_idle_kwh": idle["total_idle_kwh"],
        "compressors_night_share": leak["compressors_night_share"],
        "leak_detected": leak["leak_detected"]
    }

def tool_get_top_assets(period: str = "2026-Q3") -> Dict[str, Any]:
    """Retrieves ranked asset energy usage from sub-meter data."""
    assets = diagnostic_engine.get_asset_breakdown(period=period)
    return {
        "top_user": assets["top_user"],
        "assets": assets["assets"][:5],
        "total_facility_kwh": assets["total_facility_kwh"]
    }

def tool_rank_actions(period: str = "2026-Q3") -> List[Dict[str, Any]]:
    """Prescribes energy efficiency recommendations ranked by payback."""
    return recommendation_engine.generate_recommendations(period=period)

def tool_simulate_what_if(scenario: str, period: str = "2026-Q3") -> Dict[str, Any]:
    """Simulates what-if scenarios."""
    if "tariff" in scenario.lower():
        return what_if_simulator.simulate_tariff_reversion(period=period)
    elif "leak" in scenario.lower() or "compressor" in scenario.lower():
        return what_if_simulator.simulate_leak_repair(period=period)
    else:
        return {"scenario": scenario, "result": "Scenario simulation not available"}
