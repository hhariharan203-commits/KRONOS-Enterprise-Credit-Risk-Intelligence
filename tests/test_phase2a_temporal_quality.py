from __future__ import annotations

from src.temporal_risk.temporal_quality import baseline_temporal_assessment


def test_baseline_is_not_historically_eligible() -> None:
    assessment = baseline_temporal_assessment()
    assert assessment["history_mode"] == "PROCESS_TIME_ONLY"
    assert assessment["evidence_classification"] == "SYNTHETIC_BASELINE"
    assert assessment["identity_continuity_status"] == "NOT_ESTABLISHED"
    assert assessment["historical_analytics_eligible"] is False
    assert assessment["observation_date_available"] is False
