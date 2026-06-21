from __future__ import annotations

from src.temporal_risk.historical_ingestion.pipeline import (
    run_historical_ingestion,
)
from src.temporal_risk.migration_readiness.config import ROOT_DIR
from test_phase2c_contracts import deployed_phase2c, write_controlled_manifest


def test_phase2b_ingestion_remains_operational_after_upgrade() -> None:
    root, database = deployed_phase2c()
    manifest = write_controlled_manifest(
        root,
        snapshot_date="2025-01-31",
        source_name="compatibility.csv",
    )
    result = run_historical_ingestion(
        manifest,
        database_path=database,
        runtime_root=root,
        evidence_dir=root / "evidence" / "phase2b",
        capture_protected_hashes=False,
    )
    assert result["status"] == "PHASE2B_INGESTION_SUCCESS"


def test_phase2c_is_not_an_application_or_enterprise_dependency() -> None:
    application = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT_DIR / "app").glob("*.py")
    )
    enterprise = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT_DIR / "src" / "enterprise_data").rglob("*.py")
    )
    assert "migration_readiness" not in application
    assert "migration_readiness" not in enterprise
