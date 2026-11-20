from intelligence import assess_location

assessment = assess_location(
    location_id="LOC_001",
    risk_indicators={
        "E": 0.8,
        "G": 0.6,
        "P": 0.4,
        "V": 0.5,
        "C": 0.7,
    },
    confidence_indicators={
        "Q": 0.9,
        "F": 0.8,
        "C": 1.0,
        "S": 0.6,
    },
    monitoring_indicators={
        "N": 0.6,
        "D": 0.9,
        "M": 0.7,
    },
)

print(assessment)
