
import pytest

from intelligence.assessment_pipeline import assess_location


def complete_inputs():
    return {
        "location_id": "LOC_001",
        "risk_indicators": {
            "E": 0.8,
            "G": 0.6,
            "P": 0.4,
            "V": 0.5,
            "C": 0.7,
        },
        "confidence_indicators": {
            "Q": 0.9,
            "F": 0.8,
            "C": 1.0,
            "S": 0.6,
        },
        "monitoring_indicators": {
            "N": 0.6,
            "D": 0.9,
            "M": 0.7,
        },
    }


def test_complete_assessment():
    result = assess_location(**complete_inputs())

    assert result["location_id"] == "LOC_001"
    assert result["risk"]["score"] == 64.0
    assert result["confidence"]["score"] == 86.0
    assert result["monitoring"]["priority_score"] == 70.2

    assert result["risk"] is not result["confidence"]
    assert result["recommendation"]["action"] == (
        "schedule_follow_up_monitoring"
    )


def test_unknown_risk_is_not_treated_as_low():
    inputs = complete_inputs()
    inputs["risk_indicators"] = {
        "E": None,
        "G": None,
        "P": None,
        "V": None,
        "C": None,
    }

    result = assess_location(**inputs)

    assert result["risk"]["score"] is None
    assert result["risk"]["status"] == "insufficient_data"

    assert result["recommendation"]["action"] == (
        "collect_missing_risk_data"
    )
    assert result["recommendation"]["urgency"] == (
        "verification_needed"
    )


def test_risk_and_confidence_remain_separate():
    result = assess_location(**complete_inputs())

    assert "score" in result["risk"]
    assert "score" in result["confidence"]

    assert result["risk"]["score"] != result["confidence"]["score"]
    assert result["risk"]["band"] == "moderate"
    assert result["confidence"]["level"] == "high"


def test_high_risk_and_high_confidence_recommend_targeted_monitoring():
    inputs = complete_inputs()
    inputs["risk_indicators"] = {
        "E": 1.0,
        "G": 1.0,
        "P": 1.0,
        "V": 1.0,
        "C": 1.0,
    }

    result = assess_location(**inputs)

    assert result["risk"]["score"] == 100.0
    assert result["confidence"]["score"] == 86.0
    assert result["recommendation"]["action"] == (
        "increase_targeted_monitoring"
    )


def test_low_confidence_recommends_verification():
    inputs = complete_inputs()
    inputs["confidence_indicators"] = {
        "Q": 0.0,
        "F": 0.0,
        "C": 0.0,
        "S": 0.0,
    }

    result = assess_location(**inputs)

    assert result["risk"]["score"] == 64.0
    assert result["confidence"]["score"] == 0.0
    assert result["recommendation"]["action"] == (
        "verify_and_collect_evidence"
    )


def test_simulated_assessment_is_not_operational():
    inputs = complete_inputs()

    result = assess_location(
        **inputs,
        is_simulated=True,
    )

    assert result["assessment_mode"] == "simulated"
    assert result["confidence"]["status"] == "simulation_only"
    assert result["confidence"]["operational"] is False
    assert result["recommendation"]["action"] == (
        "collect_real_world_measurements"
    )


def test_pipeline_derives_risk_factor_internally():
    inputs = complete_inputs()
    result = assess_location(**inputs)

    # Risk score 64 becomes R = 0.64.
    # Monitoring coverage is 1.0 because R, N, D, and M are available.
    assert result["monitoring"]["coverage"] == 1.0


def test_caller_cannot_override_risk_factor():
    inputs = complete_inputs()
    inputs["monitoring_indicators"]["R"] = 0.1

    with pytest.raises(ValueError):
        assess_location(**inputs)


def test_invalid_location_id_is_rejected():
    inputs = complete_inputs()
    inputs["location_id"] = ""

    with pytest.raises(ValueError):
        assess_location(**inputs)
