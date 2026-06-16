# =============================================================================
# KRONOS — FEATURE GOVERNANCE VALIDATION
# File: src/model_validation/feature_governance.py
# =============================================================================

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from src.shared.config import OUTPUTS_DIR


PROHIBITED_IDENTIFIER_FEATURES = (
    "borrower_id",
    "customer_id",
    "account_id",
    "loan_id",
    "application_id",
)

FEATURE_GOVERNANCE_REPORT: Path = (
    OUTPUTS_DIR / "feature_governance_report.json"
)


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def contains_prohibited_identifier(
    feature_name: str
) -> bool:
    """
    Return True when a feature name contains a blocked identifier token.
    """

    normalized_name = str(feature_name).lower()

    return any(
        token in normalized_name
        for token in PROHIBITED_IDENTIFIER_FEATURES
    )


def find_prohibited_features(
    feature_cols: Iterable[str]
) -> list[str]:
    """
    Identify prohibited identifier features in a candidate feature list.
    """

    return [
        str(feature)
        for feature in feature_cols
        if contains_prohibited_identifier(feature)
    ]


def remove_prohibited_identifier_features(
    feature_cols: Iterable[str]
) -> tuple[list[str], list[str]]:
    """
    Remove identifier-like fields before model training feature matrices are built.
    """

    allowed_features: list[str] = []
    excluded_features: list[str] = []

    for feature in feature_cols:
        feature_name = str(feature)

        if contains_prohibited_identifier(feature_name):
            excluded_features.append(feature_name)
        else:
            allowed_features.append(feature_name)

    return allowed_features, excluded_features


def _load_existing_report() -> dict:
    if not FEATURE_GOVERNANCE_REPORT.exists():
        return {
            "report_name": "KRONOS Feature Governance Report",
            "generated_at": _utc_timestamp(),
            "prohibited_identifier_features": list(
                PROHIBITED_IDENTIFIER_FEATURES
            ),
            "models": {},
        }

    try:
        with open(
            FEATURE_GOVERNANCE_REPORT,
            "r",
            encoding="utf-8",
        ) as f:
            report = json.load(f)

        if not isinstance(report, dict):
            return {}

        report.setdefault(
            "report_name",
            "KRONOS Feature Governance Report",
        )
        report.setdefault(
            "prohibited_identifier_features",
            list(PROHIBITED_IDENTIFIER_FEATURES),
        )
        report.setdefault("models", {})
        return report

    except Exception:
        return {
            "report_name": "KRONOS Feature Governance Report",
            "generated_at": _utc_timestamp(),
            "prohibited_identifier_features": list(
                PROHIBITED_IDENTIFIER_FEATURES
            ),
            "models": {},
        }


def _write_report(record: dict) -> None:
    FEATURE_GOVERNANCE_REPORT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    report = _load_existing_report()
    report["generated_at"] = _utc_timestamp()
    report["prohibited_identifier_features"] = list(
        PROHIBITED_IDENTIFIER_FEATURES
    )
    report.setdefault("models", {})
    report["models"][record["model_name"]] = record

    model_records = report["models"].values()
    report["overall_status"] = (
        "FAILED"
        if any(
            item.get("status") == "FAILED"
            for item in model_records
        )
        else "PASSED"
    )

    with open(
        FEATURE_GOVERNANCE_REPORT,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            report,
            f,
            indent=4,
        )


def enforce_feature_governance(
    feature_cols: Iterable[str],
    model_name: str,
    candidate_feature_count: int | None = None,
    excluded_identifier_features: Iterable[str] | None = None,
    write_report: bool = True,
) -> list[str]:
    """
    Validate final model features and fail training when blocked identifiers remain.
    """

    final_features = [
        str(feature)
        for feature in feature_cols
    ]

    excluded_features = [
        str(feature)
        for feature in (excluded_identifier_features or [])
    ]

    violations = find_prohibited_features(
        final_features
    )

    record = {
        "model_name": model_name,
        "validated_at": _utc_timestamp(),
        "status": "FAILED" if violations else "PASSED",
        "candidate_feature_count": (
            candidate_feature_count
            if candidate_feature_count is not None
            else len(final_features) + len(excluded_features)
        ),
        "approved_feature_count": len(final_features),
        "excluded_identifier_features": excluded_features,
        "violating_features": violations,
        "validation_rule": (
            "Training features must not contain borrower_id, customer_id, "
            "account_id, loan_id, or application_id."
        ),
    }

    if write_report:
        _write_report(record)

    if violations:
        raise ValueError(
            "[KRONOS FEATURE GOVERNANCE] Prohibited identifier "
            f"features found in {model_name} training features: "
            f"{violations}"
        )

    return final_features

