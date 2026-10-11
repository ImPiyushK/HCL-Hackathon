"""
Unit Tests for Section 4.5 Data Validation.
"""

from data.validate_data import validate_dataset
from src.config import DATA_DIR

def test_dataset_validation_passes():
    res = validate_dataset(str(DATA_DIR), tolerance_pct=7.0)
    assert res["passed"] is True, f"Validation failed with errors: {res['errors']}"
    
    check_names = [c["name"] for c in res["checks"]]
    assert any("Row Count" in n for n in check_names)
    assert any("Timestamps" in n for n in check_names)
    assert any("Non-Negative" in n for n in check_names)
    assert any("Tolerance" in n for n in check_names)
    assert any("Tariff" in n for n in check_names)
    assert any("Production" in n for n in check_names)
