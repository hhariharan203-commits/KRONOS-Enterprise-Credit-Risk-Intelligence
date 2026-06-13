from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

from src.shared.config import (
    EAD_METRICS_FILE,
    EAD_MODEL_FILE,
    LGD_METRICS_FILE,
    LGD_MODEL_FILE,
    MODEL_METRICS_FILE,
    OUTPUTS_DIR,
    PD_MODEL_FILE,
    SCORED_PORTFOLIO_DATA,
)


@dataclass(frozen=True)
class GovernanceContext:
    dashboard_name: str
    created_at: str


def create_governance_context(dashboard_name: str) -> GovernanceContext:
    return GovernanceContext(
        dashboard_name=dashboard_name,
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def _artifact_record(path: Path) -> dict[str, Any]:
    return {
        "path": str(path),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else 0,
    }


def _load_json_record(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _artifact_version(path: Path) -> str:
    if not path.exists():
        return "UNAVAILABLE"

    digest = _artifact_hash(path)
    if digest != "UNAVAILABLE":
        return digest[:12]

    return "UNAVAILABLE"


def _artifact_hash(path: Path) -> str:
    if not path.exists():
        return "UNAVAILABLE"

    try:
        return sha256(path.read_bytes()).hexdigest()
    except OSError:
        return "UNAVAILABLE"


def _artifact_timestamp(path: Path) -> str:
    if not path.exists():
        return "UNAVAILABLE"

    try:
        modified_at = datetime.fromtimestamp(
            path.stat().st_mtime,
            tz=timezone.utc,
        )
    except OSError:
        return "UNAVAILABLE"

    return modified_at.date().isoformat()


def _performance_status(metrics: dict[str, Any], model_family: str) -> str:
    if not metrics:
        return "PERFORMANCE NOT AVAILABLE"

    if model_family == "PD":
        auc = float(metrics.get("roc_auc", 0))
        health = float(metrics.get("model_health_score", 0))

        if auc >= 0.85 and health >= 0.75:
            return "MODEL STABLE"

        if auc >= 0.75:
            return "MODEL MONITORING"

        return "MODEL ESCALATION REQUIRED"

    r2_score = float(metrics.get("r2_score", 0))

    if r2_score >= 0.90:
        return "MODEL STABLE"

    if r2_score >= 0.75:
        return "MODEL MONITORING"

    return "MODEL ESCALATION REQUIRED"


def _model_registry_entry(
    *,
    model_key: str,
    model_name: str,
    model_family: str,
    artifact_path: Path,
    metrics_path: Path,
    designation: str,
    active: bool,
) -> dict[str, Any]:
    metrics = _load_json_record(metrics_path)
    artifact_hash = _artifact_hash(artifact_path)
    lifecycle_date = _artifact_timestamp(artifact_path)

    return {
        "model_key": model_key,
        "model_name": model_name,
        "model_family": model_family,
        "active": active,
        "designation": designation,
        "version": _artifact_version(artifact_path),
        "sha256_model_hash": artifact_hash,
        "model_owner": "KRONOS Model Risk Governance",
        "approval_status": "APPROVED FOR PORTFOLIO DEMO",
        "validation_date": lifecycle_date,
        "promotion_date": lifecycle_date,
        "retirement_status": "ACTIVE" if active else "RETIRED",
        "champion_designation": designation == "CHAMPION",
        "challenger_designation": designation == "CHALLENGER",
        "artifact": _artifact_record(artifact_path),
        "metrics_path": str(metrics_path),
        "performance_tracking": {
            "metrics": metrics,
            "status": _performance_status(metrics, model_family),
        },
    }


def artifact_lineage() -> dict[str, dict[str, Any]]:
    return {
        "pd_model": _artifact_record(PD_MODEL_FILE),
        "lgd_model": _artifact_record(LGD_MODEL_FILE),
        "ead_model": _artifact_record(EAD_MODEL_FILE),
        "scored_portfolio": _artifact_record(SCORED_PORTFOLIO_DATA),
    }


def model_registry() -> dict[str, Any]:
    models = {
        "pd_model": _model_registry_entry(
            model_key="pd_model",
            model_name="Probability of Default Model",
            model_family="PD",
            artifact_path=PD_MODEL_FILE,
            metrics_path=MODEL_METRICS_FILE,
            designation="CHAMPION",
            active=True,
        ),
        "lgd_model": _model_registry_entry(
            model_key="lgd_model",
            model_name="Loss Given Default Model",
            model_family="LGD",
            artifact_path=LGD_MODEL_FILE,
            metrics_path=LGD_METRICS_FILE,
            designation="CHAMPION",
            active=True,
        ),
        "ead_model": _model_registry_entry(
            model_key="ead_model",
            model_name="Exposure at Default Model",
            model_family="EAD",
            artifact_path=EAD_MODEL_FILE,
            metrics_path=EAD_METRICS_FILE,
            designation="CHAMPION",
            active=True,
        ),
    }

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "active_models": [
            key for key, model in models.items() if model["active"]
        ],
        "models": models,
        "champion_challenger": champion_challenger_framework(models),
    }


def champion_challenger_framework(
    models: dict[str, dict[str, Any]] | None = None
) -> dict[str, Any]:
    registered_models = models if models is not None else model_registry()["models"]

    champions = {
        key: model
        for key, model in registered_models.items()
        if model["designation"] == "CHAMPION"
    }

    challengers = {
        key: model
        for key, model in registered_models.items()
        if model["designation"] == "CHALLENGER"
    }

    return {
        "champions": list(champions),
        "challengers": list(challengers),
        "evaluation_policy": (
            "Challenger models must outperform the active champion on "
            "validated performance and governance metrics before promotion."
        ),
    }


def model_performance_tracking() -> dict[str, Any]:
    registry = model_registry()
    return {
        key: {
            "model_name": model["model_name"],
            "designation": model["designation"],
            "version": model["version"],
            "performance_tracking": model["performance_tracking"],
        }
        for key, model in registry["models"].items()
    }


def write_model_registry() -> Path:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    registry_path = OUTPUTS_DIR / "model_registry.json"
    registry_path.write_text(
        json.dumps(model_registry(), indent=2),
        encoding="utf-8",
    )
    return registry_path


def write_artifact_lineage() -> Path:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = OUTPUTS_DIR / "artifact_lineage.json"
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "artifacts": artifact_lineage(),
        "model_registry": model_registry(),
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )
    return manifest_path
