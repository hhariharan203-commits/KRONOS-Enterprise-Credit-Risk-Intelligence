from __future__ import annotations

import hashlib
from pathlib import Path

from src.temporal_risk.config import CURRENT_WAREHOUSE, ROOT_DIR, SCORED_PORTFOLIO
from src.temporal_risk.pipeline import (
    current_warehouse_state,
    validate_scope_boundary,
)


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_phase2a_is_not_an_application_or_phase4_dependency() -> None:
    application = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT_DIR / "app").glob("*.py")
    )
    enterprise = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT_DIR / "src" / "enterprise_data").rglob("*.py")
    )
    assert "src.temporal_risk" not in application
    assert "src.temporal_risk" not in enterprise
    assert validate_scope_boundary()["independently_removable"] is True


def test_current_platform_evidence_is_read_only() -> None:
    warehouse_hash = _hash(CURRENT_WAREHOUSE)
    portfolio_hash = _hash(SCORED_PORTFOLIO)
    before = current_warehouse_state()
    after = current_warehouse_state()
    assert before == after
    assert _hash(CURRENT_WAREHOUSE) == warehouse_hash
    assert _hash(SCORED_PORTFOLIO) == portfolio_hash


def test_phase4_artifact_discovery_cannot_reach_temporal_platform() -> None:
    source = (
        ROOT_DIR / "src" / "enterprise_data" / "config.py"
    ).read_text(encoding="utf-8")
    assert "temporal_platform" not in source
    assert "data/historical_warehouse" not in source


def test_failed_preflight_does_not_overwrite_successful_evidence(
    tmp_path,
) -> None:
    import src.temporal_risk.pipeline as pipeline

    root = tmp_path / "temporal_platform"
    evidence = root / "evidence" / "phase2a"
    evidence.mkdir(parents=True)
    marker = evidence / "successful_evidence.json"
    marker.write_text('{"status":"PUBLISHED"}', encoding="utf-8")
    before = marker.read_bytes()

    result = pipeline.run_phase2a_safe(
        database_path=CURRENT_WAREHOUSE,
        runtime_root=root,
        evidence_dir=evidence,
    )
    assert result["status"] == "TEMPORAL_PLATFORM_UNAVAILABLE"
    assert marker.read_bytes() == before
    assert list(evidence.iterdir()) == [marker]
