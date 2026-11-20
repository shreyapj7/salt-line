
from typing import Optional

CONFIDENCE_WEIGHTS = {
    "Q": 0.30,
    "F": 0.25,
    "C": 0.30,
    "S": 0.15,
}

COMPONENT_NAMES = {
    "Q": "data_quality",
    "F": "freshness",
    "C": "completeness",
    "S": "spatial_coverage",
}


def calculate_confidence(
    indicators: dict[str, Optional[float]],
    minimum_weight_coverage: float,
    is_simulated: bool = False,
) -> dict:
    """
    Calculate evidence confidence.

    All indicators must be normalised between 0 and 1.
    Simulated-only evidence is excluded from operational confidence.
    Missing indicators are not silently replaced with zero.
    """

    if not 0 < minimum_weight_coverage <= 1:
        raise ValueError(
            "minimum_weight_coverage must be greater than 0 and <= 1"
        )

    if is_simulated:
        return {
            "score": None,
            "status": "simulation_only",
            "operational": False,
            "coverage": 0.0,
            "missing_inputs": list(COMPONENT_NAMES.values()),
            "reasons": [
                "Simulated data cannot contribute to real-world "
                "evidence confidence"
            ],
        }

    available = {}
    missing = []

    for key in CONFIDENCE_WEIGHTS:
        value = indicators.get(key)

        if value is None:
            missing.append(COMPONENT_NAMES[key])
            continue

        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError(f"{key} must be numeric or None")

        if not 0 <= value <= 1:
            raise ValueError(f"{key} must be between 0 and 1")

        available[key] = float(value)

    available_weight = sum(
        CONFIDENCE_WEIGHTS[key] for key in available
    )

    if available_weight == 0:
        return {
            "score": None,
            "status": "insufficient_data",
            "operational": False,
            "coverage": 0.0,
            "missing_inputs": missing,
            "reasons": ["No valid confidence components available"],
        }

    provisional_score = 100 * sum(
        CONFIDENCE_WEIGHTS[key] * value
        for key, value in available.items()
    ) / available_weight

    if available_weight < minimum_weight_coverage:
        return {
            "score": None,
            "provisional_score": round(provisional_score, 2),
            "status": "insufficient_data",
            "operational": False,
            "coverage": round(available_weight, 2),
            "missing_inputs": missing,
            "reasons": [
                "Available confidence component coverage "
                "is below the configured minimum"
            ],
        }

    status = (
        "calculated" if available_weight == 1 else "provisional"
    )

    if provisional_score < 40:
        level = "low"
    elif provisional_score < 70:
        level = "moderate"
    else:
        level = "high"

    return {
        "score": round(provisional_score, 2),
        "status": status,
        "level": level,
        "operational": True,
        "coverage": round(available_weight, 2),
        "missing_inputs": missing,
        "reasons": [
            f"{COMPONENT_NAMES[key]} contributed "
            f"{value:.2f} to the calculation"
            for key, value in available.items()
        ],
    }
