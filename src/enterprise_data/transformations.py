from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

from src.enterprise_data.config import ROOT_DIR


def normalize_identifier(value) -> str:
    if pd.isna(value):
        return ""
    text = str(value)
    if text.endswith(".0"):
        text = text[:-2]
    return text


def normalize_ifrs_stage(value) -> str:
    text = str(value).strip().upper().replace("_", " ").replace("-", " ")
    if text in {"1", "STAGE 1"}:
        return "STAGE 1"
    if text in {"2", "STAGE 2"}:
        return "STAGE 2"
    if text in {"3", "STAGE 3"}:
        return "STAGE 3"
    return "STAGE 1"


def prepare_scored_portfolio(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result["borrower_key"] = result["borrower_id"].map(normalize_identifier)
    result["facility_key"] = result["borrower_key"]
    result["ifrs_stage"] = result["ifrs_stage"].map(normalize_ifrs_stage)
    result["scoring_execution_timestamp"] = pd.to_datetime(
        result.get("timestamp"),
        errors="coerce",
        utc=True,
    )
    result["temporal_basis"] = "SCORING EXECUTION TIME"
    result["temporal_quality"] = "PROCESS TIME ONLY"
    return result


def current_model_composite_version() -> str:
    model_paths = {
        "pd": ROOT_DIR / "models" / "pd_model.pkl",
        "lgd": ROOT_DIR / "models" / "lgd_model.pkl",
        "ead": ROOT_DIR / "models" / "ead_model.pkl",
    }
    fingerprints = {
        label: hashlib.sha256(path.read_bytes()).hexdigest()[:12]
        for label, path in model_paths.items()
        if path.is_file()
    }
    if len(fingerprints) != 3:
        return "UNAVAILABLE"
    return hashlib.sha256(
        json.dumps(fingerprints, sort_keys=True).encode("utf-8")
    ).hexdigest()[:16]


def artifact_role(path: Path) -> tuple[str | None, str]:
    name = path.name.lower()
    family = None
    if name.startswith("pd_") or name in {"pd_model.pkl", "scaler.pkl", "feature_cols.json", "model_metrics.json"}:
        family = "PD"
    elif name.startswith("lgd_"):
        family = "LGD"
    elif name.startswith("ead_"):
        family = "EAD"

    if name.endswith("_model.pkl") or name == "pd_model.pkl":
        role = "MODEL"
    elif "scaler" in name:
        role = "SCALER"
    elif "feature_cols" in name:
        role = "FEATURE_LIST"
    elif "metrics" in name:
        role = "METRICS"
    else:
        role = "SUPPORTING_ARTIFACT"
    return family, role
