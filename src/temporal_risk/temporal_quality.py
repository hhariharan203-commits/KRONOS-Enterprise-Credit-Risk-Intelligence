from __future__ import annotations

from src.temporal_risk.contracts import (
    NOT_ESTABLISHED,
    PROCESS_TIME_ONLY,
    SYNTHETIC_BASELINE,
)


def baseline_temporal_assessment() -> dict:
    return {
        "history_mode": PROCESS_TIME_ONLY,
        "evidence_classification": SYNTHETIC_BASELINE,
        "identity_continuity_status": NOT_ESTABLISHED,
        "historical_analytics_eligible": False,
        "observation_date_available": False,
        "reporting_date_available": False,
        "origination_date_available": False,
        "temporal_quality": "PROCESS_TIMESTAMP_NOT_OBSERVATION_TIME",
    }
