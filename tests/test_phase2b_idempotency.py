from __future__ import annotations

from src.temporal_risk.connection import connect_temporal
from src.temporal_risk.historical_ingestion.loader import snapshot_state
from src.temporal_risk.historical_ingestion.pipeline import run_historical_ingestion
from test_phase2b_contracts import shared_observed_ingestion


def test_identical_snapshot_is_skipped_without_duplicates() -> None:
    root, database, result = shared_observed_ingestion()
    manifest = root / "inbound" / "observed" / "snapshot.json"
    repeated = run_historical_ingestion(
        manifest,
        database_path=database,
        runtime_root=root,
        evidence_dir=root / "evidence" / "phase2b",
        capture_protected_hashes=False,
    )
    assert result["snapshot_id"] == repeated["snapshot_id"]
    assert repeated["status"] == "SKIPPED_ALREADY_PUBLISHED"

    connection = connect_temporal(database)
    try:
        persisted = connection.execute(
            """
            SELECT snapshot.source_sha256,
                   ingestion_file.manifest_sha256,
                   snapshot.temporal_contract_version
            FROM core.dim_historical_snapshot AS snapshot
            JOIN control.historical_ingestion_file AS ingestion_file
              ON ingestion_file.ingestion_batch_id = snapshot.ingestion_batch_id
            WHERE snapshot.snapshot_id = ?
            """,
            [result["snapshot_id"]],
        ).fetchone()
        assert snapshot_state(
            connection,
            snapshot_id=result["snapshot_id"],
            source_hash=persisted[0],
            manifest_hash=persisted[1],
            contract_version=persisted[2],
        ) == (True, False)
    finally:
        connection.close()
