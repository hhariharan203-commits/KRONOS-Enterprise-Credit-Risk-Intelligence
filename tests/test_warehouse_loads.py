from __future__ import annotations

from src.enterprise_data.config import CSV_SOURCES, WAREHOUSE_DB
from src.enterprise_data.connection import connect_warehouse


def test_source_to_staging_loads_and_credit_snapshot() -> None:
    connection = connect_warehouse(WAREHOUSE_DB, read_only=True)
    try:
        registered_csv_sources = connection.execute(
            """
            SELECT COUNT(*)
            FROM control.source_asset
            WHERE file_type = 'CSV' AND is_current
            """
        ).fetchone()[0]
        assert registered_csv_sources == len(CSV_SOURCES)

        for source in CSV_SOURCES:
            source_row = connection.execute(
                """
                SELECT source_asset_id, row_count
                FROM control.source_asset
                WHERE relative_path = ?
                  AND is_current
                ORDER BY last_seen_at DESC
                LIMIT 1
                """,
                [source.relative_path],
            ).fetchone()
            assert source_row is not None
            source_asset_id, expected_rows = source_row
            actual_rows = connection.execute(
                f"""
                SELECT COUNT(*) FROM staging.{source.staging_table}
                WHERE source_asset_id = ?
                """,
                [source_asset_id],
            ).fetchone()[0]
            assert actual_rows == expected_rows

        assert connection.execute(
            "SELECT COUNT(*) FROM core.fact_credit_risk_snapshot"
        ).fetchone()[0] == 50_000
        assert connection.execute(
            "SELECT COUNT(*) FROM core.dim_borrower"
        ).fetchone()[0] == 50_000
        assert connection.execute(
            "SELECT COUNT(*) FROM core.dim_credit_facility"
        ).fetchone()[0] == 50_000
    finally:
        connection.close()
