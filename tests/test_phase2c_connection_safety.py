from __future__ import annotations

import pytest

from src.temporal_risk.config import CURRENT_WAREHOUSE
from src.temporal_risk.connection import assert_temporal_target
from src.temporal_risk.contracts import Phase2AValidationError
from src.temporal_risk.migration_readiness.pipeline import (
    evaluate_migration_readiness,
)
from test_phase2c_contracts import deployed_phase2c


def test_current_warehouse_is_never_a_phase2c_target() -> None:
    with pytest.raises(Phase2AValidationError):
        assert_temporal_target(CURRENT_WAREHOUSE)


def test_no_data_preflight_creates_no_readiness_runtime_assets() -> None:
    root, database = deployed_phase2c()
    evidence = root / "evidence" / "phase2c_evaluation"
    backup_count = len(list((root / "backups").glob("*.duckdb")))
    result = evaluate_migration_readiness(
        state_field="risk_grade",
        database_path=database,
        runtime_root=root,
        evidence_dir=evidence,
        capture_protected_hashes=False,
    )
    assert result["status"] == "PHASE2C_SOURCE_NOT_READY"
    assert not evidence.exists()
    assert len(list((root / "backups").glob("*.duckdb"))) == backup_count
