# =============================================================================
# KRONOS — CANONICAL PORTFOLIO SCORING PIPELINE
# File: src/credit_risk/portfolio_scoring.py
# =============================================================================

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from uuid import uuid4

import numpy as np
import pandas as pd

from src.credit_risk.credit_engine import (
    approval_decision,
    calculate_credit_score,
    classify_risk_band,
    load_feature_columns as load_pd_feature_columns,
    load_model as load_pd_model,
    load_scaler as load_pd_scaler,
    risk_grade,
)
from src.credit_risk.ead_engine import (
    load_ead_model,
    load_feature_columns as load_ead_feature_columns,
    load_scaler as load_ead_scaler,
)
from src.credit_risk.lgd_engine import (
    load_feature_columns as load_lgd_feature_columns,
    load_lgd_model,
    load_scaler as load_lgd_scaler,
)
from src.shared.config import (
    EAD_MODEL_FILE,
    LGD_MODEL_FILE,
    MERGED_CREDIT_DATA,
    PD_MODEL_FILE,
    SCORED_PORTFOLIO_DATA,
)
from src.shared.utils import legacy_ifrs_stage_label, normalize_ifrs_stage_series


SCORING_STATUS_SCORED = "SCORED"
SCORING_STATUS_FAILED = "FAILED"

CANONICAL_OUTPUT_COLUMNS = [
    "borrower_id",
    "pd_score",
    "lgd",
    "ead",
    "credit_score",
    "risk_band",
    "risk_grade",
    "underwriting_decision",
    "ifrs_stage",
    "timestamp",
    "model_version",
    "run_id",
    "scoring_status",
]


@dataclass(frozen=True)
class PortfolioScoringResult:
    output_path: Path
    row_count: int
    column_count: int
    run_id: str
    timestamp: str
    model_version: str
    scoring_status: str
    errors: list[str]
    columns: list[str]

    def to_dict(self) -> dict:
        return {
            "output_path": str(self.output_path),
            "row_count": self.row_count,
            "column_count": self.column_count,
            "run_id": self.run_id,
            "timestamp": self.timestamp,
            "model_version": self.model_version,
            "scoring_status": self.scoring_status,
            "errors": self.errors,
            "columns": self.columns,
        }


@lru_cache(maxsize=1)
def _load_scoring_artifacts() -> dict:
    artifacts = {
        "pd_model": load_pd_model(),
        "pd_scaler": load_pd_scaler(),
        "pd_features": tuple(load_pd_feature_columns()),
        "lgd_model": load_lgd_model(),
        "lgd_scaler": load_lgd_scaler(),
        "lgd_features": tuple(load_lgd_feature_columns()),
        "ead_model": load_ead_model(),
        "ead_scaler": load_ead_scaler(),
        "ead_features": tuple(load_ead_feature_columns()),
    }

    missing = [
        name
        for name, artifact in artifacts.items()
        if artifact is None or artifact == ()
    ]

    if missing:
        raise RuntimeError(
            "Missing portfolio scoring artifacts: "
            + ", ".join(missing)
        )

    return artifacts


@lru_cache(maxsize=1)
def _model_version() -> str:
    fingerprints = {}

    for label, model_path in {
        "pd": PD_MODEL_FILE,
        "lgd": LGD_MODEL_FILE,
        "ead": EAD_MODEL_FILE,
    }.items():
        path = Path(model_path)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()[:12]
        fingerprints[label] = digest

    payload = json.dumps(
        fingerprints,
        sort_keys=True,
    ).encode("utf-8")

    return hashlib.sha256(payload).hexdigest()[:16]


def _scoring_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_processed_credit_dataset(
    input_path: Path | str = MERGED_CREDIT_DATA,
    max_rows: int | None = None,
) -> pd.DataFrame:
    path = Path(input_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Processed credit dataset not found: {path}"
        )

    return pd.read_csv(
        path,
        nrows=max_rows,
    )


def _prepare_feature_matrix(
    portfolio_df: pd.DataFrame,
    feature_columns: tuple[str, ...],
) -> pd.DataFrame:
    feature_df = portfolio_df.copy()

    if "ifrs_stage" in feature_df.columns:
        feature_df["ifrs_stage"] = normalize_ifrs_stage_series(
            feature_df["ifrs_stage"]
        )

        legacy_stage_features = any(
            column.startswith("ifrs_stage_Stage_")
            for column in feature_columns
        )

        if legacy_stage_features:
            feature_df["ifrs_stage"] = feature_df["ifrs_stage"].apply(
                legacy_ifrs_stage_label
            )

    categorical_columns = [
        column
        for column in (
            "industry",
            "region",
            "risk_profile",
            "ifrs_stage",
        )
        if column in feature_df.columns
    ]

    if categorical_columns:
        feature_df = pd.get_dummies(
            feature_df,
            columns=categorical_columns,
            prefix=categorical_columns,
        )

    feature_df = feature_df.reindex(
        columns=list(feature_columns),
        fill_value=0,
    )

    for column in feature_df.columns:
        feature_df[column] = pd.to_numeric(
            feature_df[column],
            errors="coerce",
        )

    return feature_df.fillna(0)


def _score_pd(
    feature_df: pd.DataFrame,
    artifacts: dict,
) -> np.ndarray:
    scaled = artifacts["pd_scaler"].transform(feature_df)
    pd_scores = artifacts["pd_model"].predict_proba(scaled)[:, 1]
    return np.clip(pd_scores, 0, 1)


def _score_lgd(
    feature_df: pd.DataFrame,
    artifacts: dict,
) -> np.ndarray:
    scaled = artifacts["lgd_scaler"].transform(feature_df)
    lgd_scores = artifacts["lgd_model"].predict(scaled)
    return np.clip(lgd_scores, 0.01, 0.99)


def _score_ead(
    feature_df: pd.DataFrame,
    artifacts: dict,
) -> np.ndarray:
    scaled = artifacts["ead_scaler"].transform(feature_df)
    ead_scores = artifacts["ead_model"].predict(scaled)
    return np.clip(ead_scores, 1000, None)


def score_portfolio(
    input_path: Path | str = MERGED_CREDIT_DATA,
    output_path: Path | str = SCORED_PORTFOLIO_DATA,
    max_rows: int | None = None,
) -> PortfolioScoringResult:
    run_id = uuid4().hex
    timestamp = _scoring_timestamp()
    output = Path(output_path)
    errors: list[str] = []

    portfolio_df = load_processed_credit_dataset(
        input_path=input_path,
        max_rows=max_rows,
    )

    scored_df = portfolio_df.copy()
    scored_df["timestamp"] = timestamp
    scored_df["model_version"] = _model_version()
    scored_df["run_id"] = run_id
    scored_df["scoring_status"] = SCORING_STATUS_SCORED
    scored_df["scoring_error"] = ""

    try:
        artifacts = _load_scoring_artifacts()

        pd_features = _prepare_feature_matrix(
            portfolio_df,
            artifacts["pd_features"],
        )
        lgd_features = _prepare_feature_matrix(
            portfolio_df,
            artifacts["lgd_features"],
        )
        ead_features = _prepare_feature_matrix(
            portfolio_df,
            artifacts["ead_features"],
        )

        pd_scores = _score_pd(pd_features, artifacts)
        lgd_scores = _score_lgd(lgd_features, artifacts)
        ead_scores = _score_ead(ead_features, artifacts)

        scored_df["pd_score"] = np.round(pd_scores.astype(float), 6)
        scored_df["lgd"] = np.round(lgd_scores.astype(float), 6)
        scored_df["ead"] = np.round(ead_scores.astype(float), 2)
        scored_df["credit_score"] = [
            calculate_credit_score(score)
            for score in pd_scores
        ]
        scored_df["risk_band"] = [
            classify_risk_band(score)
            for score in pd_scores
        ]
        scored_df["risk_grade"] = [
            risk_grade(score)
            for score in pd_scores
        ]
        scored_df["underwriting_decision"] = [
            approval_decision(score)
            for score in pd_scores
        ]

    except Exception as exc:
        error_message = f"{type(exc).__name__}: {exc}"
        errors.append(error_message)
        scored_df["pd_score"] = np.nan
        scored_df["lgd"] = np.nan
        scored_df["ead"] = np.nan
        scored_df["credit_score"] = np.nan
        scored_df["risk_band"] = "UNSCORED"
        scored_df["risk_grade"] = "UNSCORED"
        scored_df["underwriting_decision"] = "SCORING FAILED"
        scored_df["scoring_status"] = SCORING_STATUS_FAILED
        scored_df["scoring_error"] = error_message

    if "ifrs_stage" not in scored_df.columns:
        scored_df["ifrs_stage"] = "UNKNOWN"
    else:
        scored_df["ifrs_stage"] = normalize_ifrs_stage_series(
            scored_df["ifrs_stage"]
        )

    ordered_columns = [
        column
        for column in CANONICAL_OUTPUT_COLUMNS
        if column in scored_df.columns
    ]
    remaining_columns = [
        column
        for column in scored_df.columns
        if column not in ordered_columns
    ]
    scored_df = scored_df[
        ordered_columns
        + remaining_columns
    ]

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    scored_df.to_csv(
        output,
        index=False,
    )

    return PortfolioScoringResult(
        output_path=output,
        row_count=len(scored_df),
        column_count=len(scored_df.columns),
        run_id=run_id,
        timestamp=timestamp,
        model_version=scored_df["model_version"].iloc[0],
        scoring_status=(
            SCORING_STATUS_FAILED
            if errors
            else SCORING_STATUS_SCORED
        ),
        errors=errors,
        columns=list(scored_df.columns),
    )


def validate_scored_portfolio(
    output_path: Path | str = SCORED_PORTFOLIO_DATA,
) -> dict:
    output = Path(output_path)

    if not output.exists():
        raise FileNotFoundError(
            f"Scored portfolio dataset not found: {output}"
        )

    scored_df = pd.read_csv(output)
    missing_columns = [
        column
        for column in CANONICAL_OUTPUT_COLUMNS
        if column not in scored_df.columns
    ]

    return {
        "output_path": str(output),
        "row_count": len(scored_df),
        "column_count": len(scored_df.columns),
        "missing_required_columns": missing_columns,
        "scoring_status_counts": (
            scored_df["scoring_status"]
            .value_counts(dropna=False)
            .to_dict()
        ),
        "schema": list(scored_df.columns),
    }


if __name__ == "__main__":
    result = score_portfolio()
    print(json.dumps(result.to_dict(), indent=2))
    print(json.dumps(validate_scored_portfolio(), indent=2))
