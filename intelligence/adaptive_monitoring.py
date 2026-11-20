
import math
from typing import Optional


PRIORITY_WEIGHTS = {
    "R": 0.30,
    "N": 0.20,
    "D": 0.20,
    "M": 0.30,
}

FACTOR_DESCRIPTIONS = {
    "R": "Existing risk indicator",
    "N": "Nearby-well evidence",
    "D": "Monitoring-station gap",
    "M": "Missing or outdated data need",
}


def calculate_priority(
    indicators: dict[str, Optional[float]],
    minimum_weight_coverage: float = 0.70,
) -> dict:
    """
    Calculate a location's adaptive monitoring priority.

    All indicators must be normalised to [0, 1].
    Missing indicators are excluded, never treated as zero.
    """

    if not isinstance(indicators, dict):
        raise TypeError("indicators must be a dictionary")

    if (
        isinstance(minimum_weight_coverage, bool)
        or not isinstance(minimum_weight_coverage, (int, float))
        or not math.isfinite(minimum_weight_coverage)
        or not 0 < minimum_weight_coverage <= 1
    ):
        raise ValueError(
            "minimum_weight_coverage must be greater than 0 and at most 1"
        )

    unknown = set(indicators) - set(PRIORITY_WEIGHTS)
    if unknown:
        raise ValueError(f"Unknown indicators: {sorted(unknown)}")

    available = {}
    missing = []

    for key in PRIORITY_WEIGHTS:
        value = indicators.get(key)

        if value is None:
            missing.append(key)
            continue

        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            or not 0 <= value <= 1
        ):
            raise ValueError(
                f"{key} must be a finite number between 0 and 1, or None"
            )

        available[key] = float(value)

    coverage = sum(PRIORITY_WEIGHTS[key] for key in available)

    reasons = [
        f"{FACTOR_DESCRIPTIONS[key]} contributes "
        f"{available[key]:.2f} to the normalised assessment."
        for key in available
    ]

    if not available or coverage < minimum_weight_coverage:
        return {
            "priority_score": None,
            "status": "not_rankable",
            "coverage": round(coverage, 4),
            "missing_inputs": missing,
            "reasons": reasons + [
                "Insufficient indicator coverage to rank this location."
            ],
        }

    weighted_total = sum(
        PRIORITY_WEIGHTS[key] * value
        for key, value in available.items()
    )

    # Reweight only the available indicators.
    score = (weighted_total / coverage) * 100

    status = "provisional" if missing else "calculated"

    if missing:
        reasons.append(
            "This is a provisional priority because some indicators are missing."
        )

    return {
        "priority_score": round(score, 2),
        "status": status,
        "coverage": round(coverage, 4),
        "missing_inputs": missing,
        "reasons": reasons,
    }


def rank_candidates(
    candidates: list[dict],
    minimum_weight_coverage: float = 0.70,
) -> list[dict]:
    """
    Rank monitoring candidates by priority.

    Expected candidate format:
    {
        "location_id": "LOC_001",
        "indicators": {"R": 0.7, "N": 0.5, "D": 0.8, "M": 0.9}
    }

    Not-rankable locations are placed after rankable locations.
    """

    results = []
    seen_ids = set()

    for candidate in candidates:
        if not isinstance(candidate, dict):
            raise TypeError("Each candidate must be a dictionary")

        location_id = candidate.get("location_id")

        if not isinstance(location_id, str) or not location_id.strip():
            raise ValueError("Every candidate needs a non-empty location_id")

        if location_id in seen_ids:
            raise ValueError(f"Duplicate location_id: {location_id}")

        seen_ids.add(location_id)

        result = calculate_priority(
            candidate.get("indicators", {}),
            minimum_weight_coverage=minimum_weight_coverage,
        )

        results.append({
            "location_id": location_id,
            **result,
        })

    # Rank calculated and provisional locations first.
    # Break ties deterministically using location_id.
    results.sort(
        key=lambda item: (
            item["priority_score"] is None,
            -(item["priority_score"] or 0),
            item["location_id"],
        )
    )

    rank = 0
    for result in results:
        if result["priority_score"] is not None:
            rank += 1
            result["rank"] = rank
        else:
            result["rank"] = None

    return results
