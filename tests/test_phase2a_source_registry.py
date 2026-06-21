from __future__ import annotations

from src.temporal_risk.config import SCORED_PORTFOLIO
from src.temporal_risk.source_registry import profile_source


def test_source_profile_is_evidence_driven() -> None:
    profile = profile_source(SCORED_PORTFOLIO)
    assert profile["row_count"] > 0
    assert profile["column_count"] == len(profile["columns"])
    assert profile["sha256_before"] == profile["sha256_after"]
    assert profile["distinct_borrower_count"] == profile["row_count"]
    assert profile["all_timestamps_parseable"] is True
    assert profile["all_timestamps_timezone_aware"] is True
