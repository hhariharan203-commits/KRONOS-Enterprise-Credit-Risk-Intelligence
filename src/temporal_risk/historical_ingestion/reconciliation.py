from __future__ import annotations

from src.temporal_risk.audit import stable_id, utc_now


def _record(
    connection,
    *,
    ingestion_batch_id: str,
    snapshot_id: str,
    name: str,
    source_value,
    target_value,
    status: str | None = None,
    details: str = "",
) -> dict:
    if status is None:
        status = "PASS" if str(source_value) == str(target_value) else "FAIL"
    result_id = stable_id(ingestion_batch_id, snapshot_id, name)
    difference = (
        float(source_value) - float(target_value)
        if status != "NOT_APPLICABLE"
        and isinstance(source_value, (int, float))
        and isinstance(target_value, (int, float))
        else 0.0
    )
    connection.execute(
        """
        INSERT INTO control.historical_reconciliation_result (
            historical_reconciliation_id, ingestion_batch_id, snapshot_id,
            reconciliation_name, source_value, target_value, difference,
            tolerance, status, details, reconciled_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?)
        """,
        [
            result_id,
            ingestion_batch_id,
            snapshot_id,
            name,
            str(source_value),
            str(target_value),
            difference,
            status,
            details,
            utc_now(),
        ],
    )
    return {"name": name, "status": status}


def run_reconciliations(
    connection,
    *,
    ingestion_batch_id: str,
    snapshot_id: str,
    source_rows: int,
    accepted_rows: int,
    rejected_source_rows: int,
    distinct_entities: int,
    distinct_facilities: int,
    source_hash: str,
    schema_hash: str,
    snapshot_date: str,
    source_event_count: int,
    source_ead_sum: float | None,
    source_default_count: int | None,
) -> dict:
    staging_rows = connection.execute(
        "SELECT COUNT(*) FROM staging.stg_historical_snapshot_row WHERE ingestion_batch_id = ?",
        [ingestion_batch_id],
    ).fetchone()[0]
    fact_rows = connection.execute(
        "SELECT COUNT(*) FROM core.fact_historical_credit_observation WHERE snapshot_id = ?",
        [snapshot_id],
    ).fetchone()[0]
    fact_entities = connection.execute(
        "SELECT COUNT(DISTINCT entity_key) FROM core.fact_historical_credit_observation WHERE snapshot_id = ?",
        [snapshot_id],
    ).fetchone()[0]
    fact_facilities = connection.execute(
        "SELECT COUNT(DISTINCT facility_key) FROM core.fact_historical_credit_observation WHERE snapshot_id = ? AND facility_key IS NOT NULL",
        [snapshot_id],
    ).fetchone()[0]
    snapshot = connection.execute(
        """
        SELECT COUNT(*), MIN(source_sha256), MIN(canonical_schema_hash),
               MIN(CAST(snapshot_date AS VARCHAR))
        FROM core.dim_historical_snapshot WHERE snapshot_id = ?
        """,
        [snapshot_id],
    ).fetchone()
    staged_events = connection.execute(
        "SELECT COUNT(*) FROM staging.stg_historical_event_row WHERE ingestion_batch_id = ?",
        [ingestion_batch_id],
    ).fetchone()[0]
    fact_events = connection.execute(
        "SELECT COUNT(*) FROM core.fact_historical_credit_event WHERE snapshot_id = ?",
        [snapshot_id],
    ).fetchone()[0]
    results = [
        _record(connection, ingestion_batch_id=ingestion_batch_id, snapshot_id=snapshot_id, name="source_to_staging_rows", source_value=source_rows, target_value=staging_rows),
        _record(connection, ingestion_batch_id=ingestion_batch_id, snapshot_id=snapshot_id, name="staging_to_accepted_plus_rejected", source_value=staging_rows, target_value=accepted_rows + rejected_source_rows),
        _record(connection, ingestion_batch_id=ingestion_batch_id, snapshot_id=snapshot_id, name="accepted_to_observation_fact", source_value=accepted_rows, target_value=fact_rows),
        _record(connection, ingestion_batch_id=ingestion_batch_id, snapshot_id=snapshot_id, name="entity_population", source_value=distinct_entities, target_value=fact_entities),
        _record(connection, ingestion_batch_id=ingestion_batch_id, snapshot_id=snapshot_id, name="facility_population", source_value=distinct_facilities, target_value=fact_facilities),
        _record(connection, ingestion_batch_id=ingestion_batch_id, snapshot_id=snapshot_id, name="snapshot_dimension_count", source_value=1, target_value=snapshot[0]),
        _record(connection, ingestion_batch_id=ingestion_batch_id, snapshot_id=snapshot_id, name="source_hash", source_value=source_hash, target_value=snapshot[1]),
        _record(connection, ingestion_batch_id=ingestion_batch_id, snapshot_id=snapshot_id, name="schema_hash", source_value=schema_hash, target_value=snapshot[2]),
        _record(connection, ingestion_batch_id=ingestion_batch_id, snapshot_id=snapshot_id, name="snapshot_date", source_value=snapshot_date, target_value=snapshot[3]),
        _record(connection, ingestion_batch_id=ingestion_batch_id, snapshot_id=snapshot_id, name="source_to_staged_events", source_value=source_event_count, target_value=staged_events),
        _record(connection, ingestion_batch_id=ingestion_batch_id, snapshot_id=snapshot_id, name="staged_to_fact_events", source_value=staged_events, target_value=fact_events),
    ]
    if source_ead_sum is None and source_default_count is None:
        results.append(
            _record(
                connection,
                ingestion_batch_id=ingestion_batch_id,
                snapshot_id=snapshot_id,
                name="optional_ead_default_aggregate",
                source_value="NOT_APPLICABLE",
                target_value="NOT_APPLICABLE",
                status="NOT_APPLICABLE",
            )
        )
    else:
        fact_values = connection.execute(
            """
            SELECT COALESCE(SUM(ead), 0),
                   COALESCE(SUM(CASE WHEN LOWER(COALESCE(default_outcome, '')) IN
                       ('1','true','default','defaulted','yes') THEN 1 ELSE 0 END), 0)
            FROM core.fact_historical_credit_observation WHERE snapshot_id = ?
            """,
            [snapshot_id],
        ).fetchone()
        expected = (
            round(source_ead_sum or 0.0, 8),
            int(source_default_count or 0),
        )
        actual = (round(float(fact_values[0]), 8), int(fact_values[1]))
        results.append(
            _record(
                connection,
                ingestion_batch_id=ingestion_batch_id,
                snapshot_id=snapshot_id,
                name="optional_ead_default_aggregate",
                source_value=expected,
                target_value=actual,
            )
        )
    return {
        "reconciliation_count": len(results),
        "failure_count": sum(item["status"] == "FAIL" for item in results),
        "status": "PASS"
        if not any(item["status"] == "FAIL" for item in results)
        else "FAIL",
        "results": results,
    }
