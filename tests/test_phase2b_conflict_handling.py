from __future__ import annotations

import hashlib
import json

import pandas as pd

from src.temporal_risk.connection import connect_temporal
from src.temporal_risk.historical_ingestion.loader import snapshot_state
from src.temporal_risk.historical_ingestion.pipeline import (
    run_historical_ingestion,
    run_historical_ingestion_safe,
)
from test_phase2b_contracts import deployed_phase2b, write_manifest


def _published_snapshot():
    root, database = deployed_phase2b()
    manifest = write_manifest(root)
    published = run_historical_ingestion(
        manifest,
        database_path=database,
        runtime_root=root,
        evidence_dir=root / "evidence" / "phase2b",
        capture_protected_hashes=False,
    )
    return root, database, manifest, published


def _persisted_key(database, snapshot_id):
    connection = connect_temporal(database)
    try:
        return connection.execute(
            """
            SELECT snapshot.source_sha256,
                   ingestion_file.manifest_sha256,
                   snapshot.temporal_contract_version
            FROM core.dim_historical_snapshot AS snapshot
            JOIN control.historical_ingestion_file AS ingestion_file
              ON ingestion_file.ingestion_batch_id = snapshot.ingestion_batch_id
            WHERE snapshot.snapshot_id = ?
            """,
            [snapshot_id],
        ).fetchone()
    finally:
        connection.close()


def test_changed_manifest_for_same_source_and_snapshot_is_rejected() -> None:
    root, database, manifest, published = _published_snapshot()
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["created_at"] = "2026-06-21T00:00:00Z"
    manifest.write_text(json.dumps(payload), encoding="utf-8")
    result = run_historical_ingestion_safe(
        manifest,
        database_path=database,
        runtime_root=root,
        evidence_dir=root / "evidence" / "phase2b",
        capture_protected_hashes=False,
    )
    assert result["status"] == "SNAPSHOT_VERSION_CONFLICT"


def test_changed_source_with_same_manifest_hash_is_a_conflict() -> None:
    _, database, _, published = _published_snapshot()
    persisted = _persisted_key(database, published["snapshot_id"])
    connection = connect_temporal(database)
    try:
        assert snapshot_state(
            connection,
            snapshot_id=published["snapshot_id"],
            source_hash="A" * 64,
            manifest_hash=persisted[1],
            contract_version=persisted[2],
        ) == (False, True)
    finally:
        connection.close()


def test_changed_source_and_manifest_for_same_snapshot_is_rejected() -> None:
    root, database, manifest, _ = _published_snapshot()
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    source = root / payload["source_file"]
    frame = pd.read_csv(source)
    frame.loc[0, "ead"] = 999
    frame.to_csv(source, index=False)
    payload["source_file_sha256"] = hashlib.sha256(source.read_bytes()).hexdigest().upper()
    manifest.write_text(json.dumps(payload), encoding="utf-8")
    result = run_historical_ingestion_safe(
        manifest,
        database_path=database,
        runtime_root=root,
        evidence_dir=root / "evidence" / "phase2b",
        capture_protected_hashes=False,
    )
    assert result["status"] == "SNAPSHOT_VERSION_CONFLICT"


def test_changed_source_and_manifest_hashes_are_a_conflict() -> None:
    _, database, _, published = _published_snapshot()
    persisted = _persisted_key(database, published["snapshot_id"])
    connection = connect_temporal(database)
    try:
        assert snapshot_state(
            connection,
            snapshot_id=published["snapshot_id"],
            source_hash="A" * 64,
            manifest_hash="B" * 64,
            contract_version=persisted[2],
        ) == (False, True)
    finally:
        connection.close()


def test_changed_contract_version_is_a_conflict() -> None:
    _, database, _, published = _published_snapshot()
    persisted = _persisted_key(database, published["snapshot_id"])
    connection = connect_temporal(database)
    try:
        assert snapshot_state(
            connection,
            snapshot_id=published["snapshot_id"],
            source_hash=persisted[0],
            manifest_hash=persisted[1],
            contract_version="DIFFERENT_VERSION",
        ) == (False, True)
    finally:
        connection.close()
