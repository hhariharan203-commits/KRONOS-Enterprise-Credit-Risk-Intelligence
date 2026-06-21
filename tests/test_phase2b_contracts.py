from __future__ import annotations

import hashlib
import json
import tempfile
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

from src.temporal_risk.audit import stable_id
from src.temporal_risk.connection import connect_temporal
from src.temporal_risk.historical_ingestion.contracts import (
    PHASE2B_SCOPE_VIOLATION,
    Phase2BScopeError,
    enforce_scope,
)
from src.temporal_risk.historical_ingestion.pipeline import (
    deploy_phase2b_schema,
    run_historical_ingestion,
)
from src.temporal_risk.schema_manager import initialize_schema


_SHARED = None


def seed_phase2a_database(root: Path) -> Path:
    database = root / "warehouse" / "kronos_temporal_risk.duckdb"
    connection = connect_temporal(
        database,
        read_only=False,
        deployment_authorized=True,
        runtime_root=root,
    )
    initialize_schema(connection)
    release_id = stable_id("PHASE2A", "2A.TEST")
    connection.execute(
        """
        INSERT INTO control.platform_release VALUES (
            ?, 'PHASE2A', '2A.TEST', ?, '{}', 5, 17, 0,
            'PUBLISHED', ?
        )
        """,
        [release_id, database.as_posix(), datetime.utcnow()],
    )
    connection.close()
    return database


def deployed_phase2b() -> tuple[Path, Path]:
    root = Path(tempfile.mkdtemp()) / "temporal_platform"
    database = seed_phase2a_database(root)
    result = deploy_phase2b_schema(
        database,
        runtime_root=root,
        evidence_dir=root / "evidence" / "phase2b",
        capture_protected_hashes=False,
    )
    assert result["status"] == "PHASE2B_SCHEMA_READY"
    return root, database


def write_manifest(
    root: Path,
    *,
    mode: str = "observed",
    snapshot_date: str = "2025-01-31",
    source_name: str = "snapshot.csv",
) -> Path:
    history_mode = (
        "OBSERVED_TEMPORAL" if mode == "observed" else "SIMULATED_TEMPORAL"
    )
    evidence = "OBSERVED_SOURCE" if mode == "observed" else "SIMULATED_SOURCE"
    contract = (
        "OBSERVED_HISTORICAL_SNAPSHOT_V1"
        if mode == "observed"
        else "SIMULATED_HISTORICAL_SNAPSHOT_V1"
    )
    inbound = root / "inbound" / mode
    inbound.mkdir(parents=True, exist_ok=True)
    source = inbound / source_name
    pd.DataFrame(
        {
            "customer": ["A", "B", "C"],
            "obs_date": [snapshot_date] * 3,
            "pd": [0.1, 0.2, 0.3],
            "lgd": [0.4, 0.5, 0.6],
            "ead": [100.0, 200.0, 300.0],
            "grade": ["A", "B", "C"],
            "run": ["R1"] * 3,
            "model": ["M1"] * 3,
        }
    ).to_csv(source, index=False)
    payload = {
        "manifest_version": "1",
        "contract_name": contract,
        "contract_version": "1",
        "history_mode": history_mode,
        "evidence_classification": evidence,
        "source_system": "TEST_SYSTEM",
        "source_file": f"inbound/{mode}/{source_name}",
        "source_file_sha256": hashlib.sha256(source.read_bytes()).hexdigest().upper(),
        "source_format": "CSV",
        "identity_grain": "BORROWER",
        "entity_id_column": "customer",
        "facility_id_column": None,
        "observation_date_column": "obs_date",
        "reporting_date_column": None,
        "declared_snapshot_date": snapshot_date,
        "source_date_provenance": "SOURCE_COLUMN",
        "field_mapping": {
            "source_entity_id": "customer",
            "observation_date": "obs_date",
            "pd": "pd",
            "lgd": "lgd",
            "ead": "ead",
            "risk_grade": "grade",
            "source_run_id": "run",
            "source_model_version": "model",
        },
        "source_run_id_column": "run",
        "model_version_column": "model",
        "created_at": "2026-06-20T00:00:00Z",
    }
    if mode == "simulated":
        payload.update(
            {
                "simulation_method": "EXTERNAL_FIXED_FIXTURE",
                "simulation_version": "1",
                "simulation_producer": "TEST",
                "simulation_seed": 7,
            }
        )
    manifest = inbound / f"{Path(source_name).stem}.json"
    manifest.write_text(json.dumps(payload), encoding="utf-8")
    return manifest


def shared_observed_ingestion() -> tuple[Path, Path, dict]:
    global _SHARED
    if _SHARED is None:
        root, database = deployed_phase2b()
        manifest = write_manifest(root)
        result = run_historical_ingestion(
            manifest,
            database_path=database,
            runtime_root=root,
            evidence_dir=root / "evidence" / "phase2b",
            capture_protected_hashes=False,
        )
        _SHARED = (root, database, result)
    return _SHARED


def test_phase2b_scope_contract() -> None:
    enforce_scope()
    with pytest.raises(Phase2BScopeError, match=PHASE2B_SCOPE_VIOLATION):
        enforce_scope(("migration matrices",))
