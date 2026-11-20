
from typing import Optional

RISK_WEIGHTS = {
    "E": 0.35,
    "G": 0.30,
    "P": 0.15,
    "V": 0.10,
    "C": 0.10,
}

INDICATOR_NAMES = {
    "E": "electrical_conductivity_anomaly",
    "G": "groundwater_head_decline",
    "P": "rainfall_deficit",
    "V": "vegetation_stress",
    "C": "coastal_susceptibility",
}


def calculate_risk(
    indicators: dict[str, Optional[float]],
    minimum_weight_coverage: float,
) -> dict:
    """
    Calculate a provisional relative groundwater vulnerability score.

    All indicators must be normalised between 0 and 1.
    Missing values are excluded, never replaced with zero.

    minimum_weight_coverage is an explicit project policy parameter.
    It must be agreed upon before operational use.
    """

    if not 0 < minimum_weight_coverage <= 1:
        raise ValueError(
            "minimum_weight_coverage must be greater than 0 and <= 1"
        )

    available = {}
    missing = []

    for key in RISK_WEIGHTS:
        value = indicators.get(key)

        if value is None:
            missing.append(INDICATOR_NAMES[key])
            continue

        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError(f"{key} must be numeric or None")

        if not 0 <= value <= 1:
            raise ValueError(f"{key} must be between 0 and 1")

        available[key] = float(value)

    available_weight = sum(
        RISK_WEIGHTS[key] for key in available
    )

    if available_weight == 0:
        return {
            "score": None,
            "status": "insufficient_data",
            "coverage": 0.0,
            "missing_inputs": missing,
            "reasons": ["No valid risk indicators available"],
        }

    provisional_score = 100 * sum(
        RISK_WEIGHTS[key] * value
        for key, value in available.items()
    ) / available_weight

    if available_weight < minimum_weight_coverage:
        return {
            "score": None,
            "provisional_score": round(provisional_score, 2),
            "status": "insufficient_data",
            "coverage": round(available_weight, 2),
            "missing_inputs": missing,
            "reasons": [
                "Available indicator coverage is below the configured minimum"
            ],
        }

    if available_weight < 1:
        status = "provisional"
    else:
        status = "calculated"

    if provisional_score <= 33:
        band = "lower"
    elif provisional_score <= 66:
        band = "moderate"
    else:
        band = "higher"

    return {
        "score": round(provisional_score, 2),
        "status": status,
        "band": band,
        "coverage": round(available_weight, 2),
        "missing_inputs": missing,
        "reasons": [
            f"{INDICATOR_NAMES[key]} contributed "
            f"{value:.2f} to the calculation"
            for key, value in available.items()
        ],
    }
