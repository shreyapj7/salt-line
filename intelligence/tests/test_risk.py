
from intelligence.risk_engine import calculate_risk


def test_complete_risk_calculation():
    result = calculate_risk(
        {"E": 0.8, "G": 0.6, "P": 0.4, "V": 0.5, "C": 0.7},
        minimum_weight_coverage=0.6,
    )

    assert result["score"] == 64.0
    assert result["status"] == "calculated"


def test_missing_inputs():
    result = calculate_risk(
        {"E": 0.8, "G": None, "P": None, "V": None, "C": None},
        minimum_weight_coverage=0.6,
    )

    assert result["score"] is None
    assert result["status"] == "insufficient_data"


def test_invalid_value():
    try:
        calculate_risk(
            {"E": 1.5, "G": 0.5, "P": 0.5, "V": 0.5, "C": 0.5},
            minimum_weight_coverage=0.6,
        )
    except ValueError:
        return

    raise AssertionError("Expected ValueError")


def test_partial_coverage():
    result = calculate_risk(
        {"E": 0.8, "G": 0.6, "P": 0.4, "V": None, "C": None},
        minimum_weight_coverage=0.6,
    )

    assert result["status"] == "provisional"
    assert result["coverage"] == 0.8
