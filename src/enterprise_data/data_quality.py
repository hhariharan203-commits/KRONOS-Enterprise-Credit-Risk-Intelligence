from __future__ import annotations

import hashlib
from datetime import datetime, timezone


def _record(
    connection,
    batch_id: str,
    source_asset_id: str | None,
    check_name: str,
    scope: str,
    status: str,
    actual,
    expected,
    details: str = "",
) -> dict:
    result_id = hashlib.sha256(
        f"{batch_id}|{source_asset_id}|{check_name}".encode("utf-8")
    ).hexdigest()[:32]
    now = datetime.now(timezone.utc)
    connection.execute(
        """
        INSERT INTO control.data_quality_result (
            quality_result_id, etl_batch_id, source_asset_id, check_name,
            check_scope, status, actual_value, expected_value, details, checked_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            result_id,
            batch_id,
            source_asset_id,
            check_name,
            scope,
            status,
            str(actual),
            str(expected),
            details,
            now,
        ],
    )
    return {
        "check_name": check_name,
        "status": status,
        "actual": actual,
        "expected": expected,
    }


def run_data_quality(
    connection,
    batch_id: str,
    source_results: list[dict],
) -> list[dict]:
    results = []
    for source in source_results:
        table = source["staging_table"]
        count = connection.execute(
            f"SELECT COUNT(*) FROM {table} WHERE source_asset_id = ?",
            [source["source_asset_id"]],
        ).fetchone()[0]
        results.append(
            _record(
                connection,
                batch_id,
                source["source_asset_id"],
                f"{source['relative_path']}:row_parity",
                "SOURCE_TO_STAGING",
                "PASS" if count == source["row_count"] else "FAIL",
                count,
                source["row_count"],
            )
        )

    scored = next(
        source for source in source_results
        if source["relative_path"] == "data/processed/scored_portfolio.csv"
    )
    asset_id = scored["source_asset_id"]
    table = scored["staging_table"]
    checks = (
        (
            "scored_portfolio:borrower_not_null",
            connection.execute(
                f"SELECT COUNT(*) FROM {table} WHERE borrower_id IS NULL AND source_asset_id = ?",
                [asset_id],
            ).fetchone()[0],
            0,
        ),
        (
            "scored_portfolio:borrower_unique",
            connection.execute(
                f"""
                SELECT COUNT(*) - COUNT(DISTINCT borrower_id)
                FROM {table} WHERE source_asset_id = ?
                """,
                [asset_id],
            ).fetchone()[0],
            0,
        ),
        (
            "scored_portfolio:pd_bounds",
            connection.execute(
                f"""
                SELECT COUNT(*) FROM {table}
                WHERE source_asset_id = ? AND (pd_score < 0 OR pd_score > 1 OR pd_score IS NULL)
                """,
                [asset_id],
            ).fetchone()[0],
            0,
        ),
        (
            "scored_portfolio:lgd_bounds",
            connection.execute(
                f"""
                SELECT COUNT(*) FROM {table}
                WHERE source_asset_id = ? AND (lgd < 0 OR lgd > 1 OR lgd IS NULL)
                """,
                [asset_id],
            ).fetchone()[0],
            0,
        ),
        (
            "scored_portfolio:ead_non_negative",
            connection.execute(
                f"""
                SELECT COUNT(*) FROM {table}
                WHERE source_asset_id = ? AND (ead < 0 OR ead IS NULL)
                """,
                [asset_id],
            ).fetchone()[0],
            0,
        ),
        (
            "scored_portfolio:ifrs_stage_contract",
            connection.execute(
                f"""
                SELECT COUNT(*) FROM {table}
                WHERE source_asset_id = ?
                  AND UPPER(REPLACE(ifrs_stage, '_', ' ')) NOT IN ('STAGE 1', 'STAGE 2', 'STAGE 3')
                """,
                [asset_id],
            ).fetchone()[0],
            0,
        ),
    )
    for name, actual, expected in checks:
        results.append(
            _record(
                connection,
                batch_id,
                asset_id,
                name,
                "SCORED_PORTFOLIO",
                "PASS" if actual == expected else "FAIL",
                actual,
                expected,
            )
        )

    run_count = connection.execute(
        f"SELECT COUNT(DISTINCT run_id) FROM {table} WHERE source_asset_id = ?",
        [asset_id],
    ).fetchone()[0]
    results.append(
        _record(
            connection,
            batch_id,
            asset_id,
            "scored_portfolio:historical_run_depth",
            "TEMPORAL_READINESS",
            "WARN" if run_count < 2 else "PASS",
            run_count,
            ">=2 for migration analytics",
            "One scoring run is valid for Phase 4A current-state mirroring but not historical migration analysis.",
        )
    )
    return results


def publish_data_quality_fact(connection, batch_id: str) -> int:
    connection.execute(
        """
        INSERT INTO core.fact_data_quality
        SELECT
            quality_result_id, etl_batch_id, source_asset_id, check_name,
            status, actual_value, expected_value, checked_at
        FROM control.data_quality_result source
        WHERE source.etl_batch_id = ?
          AND NOT EXISTS (
              SELECT 1 FROM core.fact_data_quality target
              WHERE target.quality_result_id = source.quality_result_id
          )
        """,
        [batch_id],
    )
    return int(
        connection.execute(
            "SELECT COUNT(*) FROM core.fact_data_quality WHERE etl_batch_id = ?",
            [batch_id],
        ).fetchone()[0]
    )
