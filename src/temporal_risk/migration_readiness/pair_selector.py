from __future__ import annotations

from src.temporal_risk.migration_readiness.contracts import (
    ALLOWED_STATE_FIELDS,
    PHASE2C_PAIR_CONFLICT,
    PHASE2C_SCOPE_VIOLATION,
    PHASE2C_SOURCE_NOT_ELIGIBLE,
    PHASE2C_SOURCE_NOT_READY,
    Phase2CPairConflictError,
    Phase2CScopeError,
    Phase2CSourceNotEligibleError,
    Phase2CSourceNotReadyError,
    is_prohibited_field_name,
)


def _candidate_query() -> str:
    return """
        SELECT
            snapshot.snapshot_id,
            snapshot.snapshot_date,
            snapshot.history_mode,
            snapshot.evidence_classification,
            snapshot.identity_grain,
            snapshot.source_sha256,
            snapshot.ingestion_batch_id,
            snapshot.source_asset_id,
            asset.source_system,
            registry.snapshot_status,
            mapping.source_column AS state_source_column,
            mapping.source_supplied_flag AS state_source_supplied,
            identity_mapping.source_column AS identity_source_column,
            identity_mapping.source_supplied_flag AS identity_source_supplied,
            date_mapping.source_column AS date_source_column,
            CASE
                WHEN snapshot.snapshot_date_type = 'OBSERVATION_DATE'
                THEN 'observation_date'
                ELSE 'reporting_date'
            END AS date_canonical_field,
            EXISTS (
                SELECT 1
                FROM control.historical_publish_status published
                WHERE published.ingestion_batch_id = snapshot.ingestion_batch_id
                  AND published.new_status = 'PUBLISHED'
            ) AS phase2b_published
        FROM core.dim_historical_snapshot snapshot
        JOIN control.source_asset asset
          ON asset.source_asset_id = snapshot.source_asset_id
        JOIN control.snapshot_registry registry
          ON registry.snapshot_id = snapshot.snapshot_id
        LEFT JOIN control.historical_field_mapping mapping
          ON mapping.ingestion_batch_id = snapshot.ingestion_batch_id
         AND mapping.canonical_column = ?
        LEFT JOIN control.historical_field_mapping date_mapping
          ON date_mapping.ingestion_batch_id = snapshot.ingestion_batch_id
         AND date_mapping.canonical_column = CASE
             WHEN snapshot.snapshot_date_type = 'OBSERVATION_DATE'
             THEN 'observation_date'
             ELSE 'reporting_date'
         END
        LEFT JOIN control.historical_field_mapping identity_mapping
          ON identity_mapping.ingestion_batch_id = snapshot.ingestion_batch_id
         AND identity_mapping.canonical_column = CASE
             WHEN snapshot.identity_grain = 'FACILITY'
             THEN 'source_facility_id'
             ELSE 'source_entity_id'
         END
    """


def _as_record(row) -> dict:
    keys = (
        "snapshot_id",
        "snapshot_date",
        "history_mode",
        "evidence_classification",
        "identity_grain",
        "source_sha256",
        "ingestion_batch_id",
        "source_asset_id",
        "source_system",
        "snapshot_status",
        "state_source_column",
        "state_source_supplied",
        "identity_source_column",
        "identity_source_supplied",
        "date_source_column",
        "date_canonical_field",
        "phase2b_published",
    )
    return dict(zip(keys, row))


def candidates(connection, *, state_field: str) -> list[dict]:
    if state_field not in ALLOWED_STATE_FIELDS:
        raise Phase2CScopeError(PHASE2C_SCOPE_VIOLATION)
    rows = connection.execute(
        _candidate_query()
        + """
        WHERE snapshot.history_mode = 'OBSERVED_TEMPORAL'
          AND snapshot.evidence_classification = 'OBSERVED_SOURCE'
          AND registry.snapshot_status = 'PUBLISHED'
          AND mapping.source_supplied_flag = TRUE
          AND identity_mapping.source_supplied_flag = TRUE
          AND date_mapping.source_supplied_flag = TRUE
        ORDER BY snapshot.snapshot_date, snapshot.snapshot_id
        """,
        [state_field],
    ).fetchall()
    return [
        record
        for record in (_as_record(row) for row in rows)
        if not any(
            is_prohibited_field_name(record.get(name))
            for name in (
                "state_source_column",
                "identity_source_column",
                "date_source_column",
            )
        )
    ]


def load_snapshot(
    connection,
    *,
    snapshot_id: str,
    state_field: str,
) -> dict:
    if state_field not in ALLOWED_STATE_FIELDS:
        raise Phase2CScopeError(PHASE2C_SCOPE_VIOLATION)
    rows = connection.execute(
        _candidate_query() + " WHERE snapshot.snapshot_id = ?",
        [state_field, snapshot_id],
    ).fetchall()
    if len(rows) != 1:
        raise Phase2CSourceNotReadyError(PHASE2C_SOURCE_NOT_READY)
    return _as_record(rows[0])


def _eligible(record: dict) -> bool:
    return (
        record["history_mode"] == "OBSERVED_TEMPORAL"
        and record["evidence_classification"] == "OBSERVED_SOURCE"
        and record["snapshot_status"] == "PUBLISHED"
        and bool(record["phase2b_published"])
        and bool(record["state_source_column"])
        and bool(record["state_source_supplied"])
        and bool(record["date_source_column"])
        and not any(
            is_prohibited_field_name(record.get(name))
            for name in (
                "state_source_column",
                "identity_source_column",
                "date_source_column",
            )
        )
    )


def select_pair(
    connection,
    *,
    state_field: str,
    earlier_snapshot_id: str | None = None,
    later_snapshot_id: str | None = None,
    source_system: str | None = None,
    identity_grain: str | None = None,
) -> tuple[dict, dict]:
    observed = candidates(connection, state_field=state_field)
    if len(observed) < 2:
        raise Phase2CSourceNotReadyError(PHASE2C_SOURCE_NOT_READY)

    explicit = earlier_snapshot_id is not None or later_snapshot_id is not None
    if explicit:
        if not earlier_snapshot_id or not later_snapshot_id:
            raise Phase2CPairConflictError(PHASE2C_PAIR_CONFLICT)
        earlier = load_snapshot(
            connection,
            snapshot_id=earlier_snapshot_id,
            state_field=state_field,
        )
        later = load_snapshot(
            connection,
            snapshot_id=later_snapshot_id,
            state_field=state_field,
        )
        if not _eligible(earlier) or not _eligible(later):
            raise Phase2CSourceNotEligibleError(PHASE2C_SOURCE_NOT_ELIGIBLE)
    else:
        if not source_system or not identity_grain:
            raise Phase2CPairConflictError(PHASE2C_PAIR_CONFLICT)
        filtered = [
            item
            for item in observed
            if item["source_system"] == source_system
            and item["identity_grain"] == identity_grain
        ]
        if len(filtered) < 2:
            raise Phase2CSourceNotReadyError(PHASE2C_SOURCE_NOT_READY)
        earliest_date = min(item["snapshot_date"] for item in filtered)
        latest_date = max(item["snapshot_date"] for item in filtered)
        if earliest_date >= latest_date:
            raise Phase2CPairConflictError(PHASE2C_PAIR_CONFLICT)
        earliest = sorted(
            (item for item in filtered if item["snapshot_date"] == earliest_date),
            key=lambda item: item["snapshot_id"],
        )
        latest = sorted(
            (item for item in filtered if item["snapshot_date"] == latest_date),
            key=lambda item: item["snapshot_id"],
        )
        if len(earliest) != 1 or len(latest) != 1:
            raise Phase2CPairConflictError(PHASE2C_PAIR_CONFLICT)
        earlier, later = earliest[0], latest[0]

    if (
        earlier["snapshot_id"] == later["snapshot_id"]
        or earlier["snapshot_date"] >= later["snapshot_date"]
        or earlier["source_system"] != later["source_system"]
        or earlier["identity_grain"] != later["identity_grain"]
    ):
        raise Phase2CPairConflictError(PHASE2C_PAIR_CONFLICT)
    return earlier, later
