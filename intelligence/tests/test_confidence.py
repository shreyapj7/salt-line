
from intelligence.confidence_engine import calculate_confidence


def test_complete_confidence():
    result = calculate_confidence(
        {"Q": 0.9, "F": 0.8, "C": 1.0, "S": 0.6},
        minimum_weight_coverage=0.6,
    )

    assert result["score"] == 86.0
    assert result["status"] == "calculated"
    assert result["operational"] is True


def test_missing_components():
    result = calculate_confidence(
        {"Q": 0.9, "F": None, "C": None, "S": None},
        minimum_weight_coverage=0.6,
    )

    assert result["score"] is None
    assert result["status"] == "insufficient_data"


def test_simulated_data_excluded():
    result = calculate_confidence(
        {"Q": 1.0, "F": 1.0, "C": 1.0, "S": 1.0},
        minimum_weight_coverage=0.6,
        is_simulated=True,
    )

    assert result["score"] is None
    assert result["status"] == "simulation_only"
    assert result["operational"] is False


def test_partial_confidence():
    result = calculate_confidence(
        {"Q": 0.9, "F": 0.8, "C": 1.0, "S": None},
        minimum_weight_coverage=0.6,
    )

    assert result["status"] == "provisional"
    assert result["coverage"] == 0.85


def test_invalid_value():
    try:
        calculate_confidence(
            {"Q": 1.5, "F": 0.8, "C": 1.0, "S": 0.6},
            minimum_weight_coverage=0.6,
        )
    except ValueError:
        return

    raise AssertionError("Expected ValueError")
