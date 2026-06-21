from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


FRAMEWORK_NAME = "KRONOS SAS-Style Analytics"
ANALYTICS_UNAVAILABLE = "ANALYTICS_UNAVAILABLE"
TEMPORAL_HISTORY_NOT_AVAILABLE = "TEMPORAL_HISTORY_NOT_AVAILABLE"
CURRENT_LOSS_PROXY = "current_credit_loss_proxy"

PROHIBITED_LABELS = {
    "ifrs9 ecl",
    "ifrs 9 ecl",
    "provision",
    "accounting reserve",
}

TEMPORAL_ANALYSES = {
    "vintage_analysis",
    "migration_analysis",
    "roll_rate_analysis",
    "default_cohort_analysis",
    "recovery_analytics",
    "cure_analysis",
    "historical_trend_analysis",
    "observation_period_analytics",
    "reporting_period_analytics",
    "historical_stage_movement",
    "lifetime_ecl",
}


class AnalyticsContractError(RuntimeError):
    """Raised when an analytics request violates a governed contract."""


@dataclass(frozen=True)
class AnalyticsRunMetadata:
    analytics_run_id: str
    execution_timestamp: str
    source_asset_id: str
    source_hash: str
    published_batch_id: str
    model_version: str
    portfolio_size: int


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def temporal_restriction_response(analysis_name: str) -> dict:
    normalized = analysis_name.strip().lower().replace(" ", "_").replace("-", "_")
    if normalized not in TEMPORAL_ANALYSES:
        raise AnalyticsContractError(
            f"Unknown temporal restriction request: {analysis_name}"
        )
    return {
        "status": TEMPORAL_HISTORY_NOT_AVAILABLE,
        "analysis": normalized,
        "reason": (
            "KRONOS contains one current borrower-level scoring snapshot and "
            "does not contain genuine reporting, vintage, default, cure, or "
            "migration histories."
        ),
    }


def assert_safe_metric_label(label: str) -> None:
    normalized = label.strip().lower()
    if normalized in PROHIBITED_LABELS:
        raise AnalyticsContractError(
            f"Metric label is prohibited in Phase 4C: {label}"
        )
