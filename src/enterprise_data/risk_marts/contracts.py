from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


PHASE4D_SUCCESS = "PHASE4D_SUCCESS"
MARTS_UNAVAILABLE = "MARTS_UNAVAILABLE"

EXPECTED_PORTFOLIO_COUNT = 50_000
EXPECTED_TOTAL_EAD = 837_946_260.46
EXPECTED_WATCHLIST_COUNT = 16_378
EXPECTED_STAGE_TOTAL = 50_000

EXPECTED_DIMENSION_COUNTS = {
    "INDUSTRY": 10,
    "REGION": 5,
    "RISK_BAND": 5,
    "RISK_GRADE": 7,
}

EXPECTED_EXISTING_MART_ROWS = {
    "mart_credit_risk_current": 50_000,
    "mart_ifrs9_stage_current": 3,
    "mart_ews_current": 50_000,
    "mart_executive_current": 1,
}

MINIMUM_HISTORY_MART_ROWS = {
    "mart_model_risk": 3,
    "mart_data_quality": 25,
}


class Phase4DContractError(RuntimeError):
    """Raised when a Phase 4D warehouse contract is not satisfied."""


@dataclass(frozen=True)
class ViewDefinition:
    view_name: str
    sql_path: Path
    source_objects: tuple[str, ...]
