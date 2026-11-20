
from typing import Optional

from intelligence.risk_engine import calculate_risk
from intelligence.confidence_engine import calculate_confidence
from intelligence.adaptive_monitoring import calculate_priority


def generate_monitoring_recommendation(
    risk: dict,
    confidence: dict,
    monitoring: dict,
    is_simulated: bool = False,
) -> dict:
    """
    Generate a monitoring recommendation using risk, confidence,
    and monitoring priority as separate evidence dimensions.

    Recommendations guide data collection and verification.
    They do not confirm seawater intrusion.
    """

    risk_score = risk.get("score")
    risk_status = risk.get("status")

    confidence_score = confidence.get("score")
    confidence_status = confidence.get("status")

    priority_score = monitoring.get("priority_score")

    # Simulated observations must never generate operational conclusions.
    if is_simulated:
        return {
            "action": "collect_real_world_measurements",
            "urgency": "not_assessed",
            "explanation": (
                "This assessment uses simulated data. Collect verified "
                "field measurements before making operational risk "
                "or monitoring decisions."
            ),
            "basis": [
                "Simulation data is excluded from operational confidence.",
                "No real-world risk conclusion is made.",
            ],
        }

    # Unknown risk is not equivalent to low risk.
    if risk_score is None:
        return {
            "action": "collect_missing_risk_data",
            "urgency": "verification_needed",
            "explanation": (
                "Risk cannot currently be assessed because the available "
                "risk indicators do not meet the required evidence coverage. "
                "This location must not be classified as low risk."
            ),
            "basis": [
                f"Risk status: {risk_status}",
                "Additional valid risk measurements are required.",
            ],
        }

    # Low confidence means the available risk assessment needs verification.
    if confidence_score is None or confidence_score < 40:
        return {
            "action": "verify_and_collect_evidence",
            "urgency": "verification_needed",
            "explanation": (
                "The risk calculation has limited supporting evidence. "
                "Verify existing measurements and collect additional "
                "observations before relying on the risk assessment."
            ),
            "basis": [
                f"Risk score: {risk_score}",
                f"Confidence status: {confidence_status}",
                f"Confidence score: {confidence_score}",
            ],
        }

    # High risk indicator with strong evidence.
    if risk_score > 66 and confidence_score >= 70:
        return {
            "action": "increase_targeted_monitoring",
            "urgency": "high",
            "explanation": (
                "The available indicators show a high risk score with "
                "stronger supporting evidence. Prioritise repeat field "
                "measurements and verification at this location. "
                "This is not confirmation of seawater intrusion."
            ),
            "basis": [
                f"Risk score: {risk_score}",
                f"Confidence score: {confidence_score}",
                f"Monitoring priority: {priority_score}",
            ],
        }

    # Moderate risk indicator.
    if risk_score > 33:
        return {
            "action": "schedule_follow_up_monitoring",
            "urgency": "moderate",
            "explanation": (
                "The available indicators suggest a moderate risk level. "
                "Schedule follow-up measurements and compare them with "
                "future observations to identify changes."
            ),
            "basis": [
                f"Risk score: {risk_score}",
                f"Confidence score: {confidence_score}",
                f"Monitoring priority: {priority_score}",
            ],
        }

    # Low calculated risk, supported by stronger evidence.
    return {
        "action": "continue_routine_monitoring",
        "urgency": "routine",
        "explanation": (
            "The available indicators currently produce a low risk score "
            "with sufficient supporting confidence. Continue routine "
            "monitoring because conditions may change over time."
        ),
        "basis": [
            f"Risk score: {risk_score}",
            f"Confidence score: {confidence_score}",
            "Continue collecting measurements to detect future changes.",
        ],
    }


def assess_location(
    location_id: str,
    risk_indicators: dict[str, Optional[float]],
    confidence_indicators: dict[str, Optional[float]],
    monitoring_indicators: dict[str, Optional[float]],
    minimum_risk_coverage: float = 0.60,
    minimum_confidence_coverage: float = 0.60,
    minimum_monitoring_coverage: float = 0.70,
    is_simulated: bool = False,
) -> dict:
    """
    Run the complete SALT-LINE intelligence pipeline for one location.

    Args:
        location_id:
            Unique location identifier.

        risk_indicators:
            E, G, P, V, C. Normalised values between 0 and 1.

        confidence_indicators:
            Q, F, C, S. Normalised values between 0 and 1.

        monitoring_indicators:
            N, D, M. Normalised values between 0 and 1.
            R is derived internally from the risk result.

        is_simulated:
            True when the assessment uses simulated-only observations.

    Returns:
        A structured dictionary containing separate risk,
        confidence, monitoring, and recommendation results.
    """

    if not isinstance(location_id, str) or not location_id.strip():
        raise ValueError("location_id must be a non-empty string")

    if not isinstance(is_simulated, bool):
        raise ValueError("is_simulated must be a boolean")

    if not isinstance(monitoring_indicators, dict):
        raise TypeError("monitoring_indicators must be a dictionary")

    unknown_monitoring = set(monitoring_indicators) - {"N", "D", "M"}

    if unknown_monitoring:
        raise ValueError(
            f"Unknown monitoring indicators: {sorted(unknown_monitoring)}"
        )
    # R is always derived from the risk engine.
    # Prevent conflicting caller-supplied risk values.
    if "R" in monitoring_indicators:
        raise ValueError(
            "Do not provide R in monitoring_indicators. "
            "The pipeline derives it from the risk assessment."
        )

    risk = calculate_risk(
        indicators=risk_indicators,
        minimum_weight_coverage=minimum_risk_coverage,
    )

    confidence = calculate_confidence(
        indicators=confidence_indicators,
        minimum_weight_coverage=minimum_confidence_coverage,
        is_simulated=is_simulated,
    )

    # Use only an actual available risk score.
    # Do not turn a missing or insufficient risk result into zero.
    risk_score = risk.get("score")

    risk_factor = (
        risk_score / 100
        if risk_score is not None
        else None
    )

    monitoring_inputs = {
        "R": risk_factor,
        "N": monitoring_indicators.get("N"),
        "D": monitoring_indicators.get("D"),
        "M": monitoring_indicators.get("M"),
    }

    monitoring = calculate_priority(
        indicators=monitoring_inputs,
        minimum_weight_coverage=minimum_monitoring_coverage,
    )

    recommendation = generate_monitoring_recommendation(
        risk=risk,
        confidence=confidence,
        monitoring=monitoring,
        is_simulated=is_simulated,
    )

    return {
        "location_id": location_id,
        "assessment_mode": (
            "simulated" if is_simulated else "operational"
        ),
        "risk": risk,
        "confidence": confidence,
        "monitoring": monitoring,
        "recommendation": recommendation,
    }
