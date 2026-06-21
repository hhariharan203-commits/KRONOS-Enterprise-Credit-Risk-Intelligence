from __future__ import annotations

import hashlib
import json
from pathlib import Path

from src.enterprise_data.config import WAREHOUSE_DB
from src.enterprise_data.risk_marts.contracts import (
    MARTS_UNAVAILABLE,
    PHASE4D_SUCCESS,
)
from src.enterprise_data.risk_marts.deployer import deploy_phase4d_views


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_phase4d(
    database_path: Path | str = WAREHOUSE_DB,
) -> dict:
    database = Path(database_path)
    try:
        before_hash = _sha256(database)
        deployment = deploy_phase4d_views(database)
        after_hash = _sha256(database)
        return {
            "status": PHASE4D_SUCCESS,
            "database_path": str(database),
            "warehouse_hash_before": before_hash,
            "warehouse_hash_after": after_hash,
            "warehouse_mode": "READ_ONLY_MIRROR",
            "source_of_truth": "data/processed/scored_portfolio.csv",
            "application_impact": "NONE",
            **deployment,
        }
    except Exception as exc:
        return {
            "status": MARTS_UNAVAILABLE,
            "database_path": str(database),
            "error": f"{type(exc).__name__}: {exc}",
            "application_impact": (
                "NONE; KRONOS application, dashboards, scoring, ETL, and "
                "SAS-Style Analytics remain independent of Phase 4D."
            ),
        }


if __name__ == "__main__":
    print(json.dumps(run_phase4d(), indent=2, default=str))
