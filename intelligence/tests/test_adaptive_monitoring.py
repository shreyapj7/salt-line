
import pytest

from intelligence.adaptive_monitoring import (
    calculate_priority,
    rank_candidates,
)


def test_complete_priority_calculation():
    indicators = {
        "R": 0.8,
        "N": 0.6,
        "D": 0.9,
        "M": 0.7,
    }

    result = calculate_priority(indicators)

    # 100 * (0.30*0.8 + 0.20*0.6 + 0.20*0.9 + 0.30*0.7)
    assert result["priority_score"] == 75.0
    assert result["status"] == "calculated"
    assert result["coverage"] == 1.0


def test_missing_indicator_gives_provisional_score():
    indicators = {
        "R": 0.8,
        "N": 0.6,
        "D": None,
        "M": 0.7,
    }

    result = calculate_priority(indicators)

    assert result["priority_score"] is not None
    assert result["status"] == "provisional"
    assert "D" in result["missing_inputs"]


def test_insufficient_coverage_is_not_rankable():
    indicators = {
        "R": 0.8,
        "N": None,
        "D": None,
        "M": None,
    }

    result = calculate_priority(indicators)

    assert result["priority_score"] is None
    assert result["status"] == "not_rankable"


def test_invalid_indicator_value():
    with pytest.raises(ValueError):
        calculate_priority({
            "R": 1.5,
            "N": 0.5,
            "D": 0.5,
            "M": 0.5,
        })


def test_boolean_indicator_is_rejected():
    with pytest.raises(ValueError):
        calculate_priority({
            "R": True,
            "N": 0.5,
            "D": 0.5,
            "M": 0.5,
        })


def test_candidates_are_ranked_by_priority():
    candidates = [
        {
            "location_id": "LOC_001",
            "indicators": {
                "R": 0.3, "N": 0.4, "D": 0.3, "M": 0.4
            },
        },
        {
            "location_id": "LOC_002",
            "indicators": {
                "R": 0.9, "N": 0.8, "D": 0.9, "M": 1.0
            },
        },
    ]

    results = rank_candidates(candidates)

    assert results[0]["location_id"] == "LOC_002"
    assert results[0]["rank"] == 1
    assert results[1]["location_id"] == "LOC_001"
    assert results[1]["rank"] == 2


def test_not_rankable_candidate_goes_last():
    candidates = [
        {
            "location_id": "LOC_001",
            "indicators": {
                "R": None, "N": None, "D": None, "M": None
            },
        },
        {
            "location_id": "LOC_002",
            "indicators": {
                "R": 0.8, "N": 0.7, "D": 0.9, "M": 0.8
            },
        },
    ]

    results = rank_candidates(candidates)

    assert results[0]["location_id"] == "LOC_002"
    assert results[1]["location_id"] == "LOC_001"
    assert results[1]["rank"] is None


def test_duplicate_location_ids_are_rejected():
    candidates = [
        {"location_id": "LOC_001", "indicators": {}},
        {"location_id": "LOC_001", "indicators": {}},
    ]

    with pytest.raises(ValueError):
        rank_candidates(candidates)
