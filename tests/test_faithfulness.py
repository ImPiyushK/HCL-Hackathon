"""
Unit Tests for Number Faithfulness Verifier (R10, Annex A Rule 4).
"""

from src.agent.verifier import faithfulness_verifier

def test_verifier_accepts_faithful_text():
    tool_outputs = {
        "decompose_change": {
            "total_pct": 15.4,
            "tariff": 8.2,
            "mix": 3.4,
            "volume": 1.2,
            "weather": 0.9,
            "waste": 1.7
        }
    }
    text = "The bill rose 15.4%. Tariff explains 8.2 points, mix 3.4 points, volume 1.2 points, and weather 0.9 points. Waste is 1.7 points."
    res = faithfulness_verifier.verify_brief(text, tool_outputs)
    assert res["faithful"] is True
    assert res["faithfulness_score"] == 1.0
    assert len(res["unauthorized_numbers"]) == 0

def test_verifier_catches_hallucinated_number():
    tool_outputs = {
        "decompose_change": {
            "total_pct": 15.4,
            "tariff": 8.2
        }
    }
    text = "The bill rose 15.4%. But old machine pumps leaked $999,999 with 88.5% efficiency."
    res = faithfulness_verifier.verify_brief(text, tool_outputs)
    assert res["faithful"] is False
    assert res["faithfulness_score"] < 1.0
    assert any("999" in token for token in res["unauthorized_numbers"])
