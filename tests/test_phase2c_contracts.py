from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

from src.temporal_risk.historical_ingestion.pipeline import (
    run_historical_ingestion,
)
from src.temporal_risk.migration_readiness.contracts import (
    RISK_BAND_CONTRACT,
    RISK_BAND_VALUES,
    RISK_GRADE_CONTRACT,
    RISK_GRADE_VALUES,
    governance_score,
)
from src.temporal_risk.migration_readiness.pipeline import (
    deploy_phase2c_schema,
    evaluate_migration_readiness,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_phase2b_contracts import deployed_phase2b, write_manifest  # noqa: E402


_SHARED = None


def deployed_phase2c() -> tuple[Path, Path]:
    root, database = deployed_phase2b()
    result = deploy_phase2c_schema(
        database,
        runtime_root=root,
        evidence_dir=root / "evidence" / "phase2c",
        capture_protected_hashes=False,
    )
    assert result["status"] == "PHASE2C_SCHEMA_READY"
    return root, database


def write_controlled_manifest(
    root: Path,
    *,
    snapshot_date: str,
    source_name: str,
    state_field: str = "risk_grade",
    values: list[str] | None = None,
) -> Path:
    manifest = write_manifest(
        root,
        snapshot_date=snapshot_date,
        source_name=source_name,
    )
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    source = root / payload["source_file"]
    frame = pd.read_csv(source)
    if state_field == "risk_grade":
        frame["grade"] = values or ["AAA", "BBB", "CCC"]
    else:
        frame["band"] = values or ["PRIME", "MODERATE RISK", "DEFAULT RISK"]
        payload["field_mapping"]["risk_band"] = "band"
    frame.to_csv(source, index=False)
    payload["source_file_sha256"] = hashlib.sha256(
        source.read_bytes()
    ).hexdigest().upper()
    manifest.write_text(json.dumps(payload), encoding="utf-8")
    return manifest


def two_snapshot_environment(
    *,
    state_field: str = "risk_grade",
    later_values: list[str] | None = None,
) -> tuple[Path, Path, list[str]]:
    root, database = deployed_phase2c()
    snapshot_ids = []
    for snapshot_date, source_name, values in (
        ("2025-01-31", "earlier.csv", None),
        ("2025-02-28", "later.csv", later_values),
    ):
        manifest = write_controlled_manifest(
            root,
            snapshot_date=snapshot_date,
            source_name=source_name,
            state_field=state_field,
            values=values,
        )
        result = run_historical_ingestion(
            manifest,
            database_path=database,
            runtime_root=root,
            evidence_dir=root / "evidence" / "phase2b",
            capture_protected_hashes=False,
        )
        assert result["status"] == "PHASE2B_INGESTION_SUCCESS"
        snapshot_ids.append(result["snapshot_id"])
    return root, database, snapshot_ids


def shared_published_readiness():
    global _SHARED
    if _SHARED is None:
        root, database, snapshot_ids = two_snapshot_environment()
        result = evaluate_migration_readiness(
            state_field="risk_grade",
            earlier_snapshot_id=snapshot_ids[0],
            later_snapshot_id=snapshot_ids[1],
            database_path=database,
            runtime_root=root,
            evidence_dir=root / "evidence" / "phase2c",
            capture_protected_hashes=False,
        )
        _SHARED = (root, database, snapshot_ids, result)
    return _SHARED


def test_controlled_domain_contracts_are_exact_and_case_sensitive() -> None:
    assert RISK_GRADE_CONTRACT.ordered_allowed_values == RISK_GRADE_VALUES
    assert RISK_BAND_CONTRACT.ordered_allowed_values == RISK_BAND_VALUES
    assert "aaa" not in RISK_GRADE_VALUES
    assert "prime" not in RISK_BAND_VALUES


def test_governance_score_rounding_and_zero_denominator() -> None:
    assert str(governance_score(2, 3)) == "66.67"
    assert governance_score(0, 0) is None
