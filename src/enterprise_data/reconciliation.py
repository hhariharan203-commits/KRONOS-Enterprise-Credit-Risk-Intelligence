from __future__ import annotations

import hashlib
from datetime import datetime, timezone

import pandas as pd

from src.enterprise_data.config import ROOT_DIR
from src.enterprise_data.source_registry import file_sha256, source_asset_id


def _record(
    connection,
    batch_id: str,
    source_asset_id: str,
    name: str,
    source_value: float,
    warehouse_value: float,
    tolerance: float,
) -> dict:
    difference = abs(float(source_value) - float(warehouse_value))
    status = "PASS" if difference <= tolerance else "FAIL"
    reconciliation_id = hashlib.sha256(
        f"{batch_id}|{source_asset_id}|{name}".encode("utf-8")
    ).hexdigest()[:32]
    connection.execute(
        """
        INSERT INTO control.reconciliation_result (
            reconciliation_id, etl_batch_id, source_asset_id,
            reconciliation_name, source_value, warehouse_value,
            absolute_difference, tolerance, status, reconciled_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            reconciliation_id,
            batch_id,
            source_asset_id,
            name,
            float(source_value),
            float(warehouse_value),
            difference,
            tolerance,
            status,
            datetime.now(timezone.utc),
        ],
    )
    return {
        "name": name,
        "source_value": float(source_value),
        "warehouse_value": float(warehouse_value),
        "difference": difference,
        "tolerance": tolerance,
        "status": status,
    }


def run_reconciliation(
    connection,
    batch_id: str,
    scored_source: dict,
) -> list[dict]:
    source = pd.read_csv(ROOT_DIR / scored_source["relative_path"])
    asset_id = scored_source["source_asset_id"]
    warehouse = connection.execute(
        """
        SELECT *
        FROM core.fact_credit_risk_snapshot
        WHERE source_asset_id = ?
        """,
        [asset_id],
    ).fetchdf()

    metric_specs = (
        ("portfolio_count", len(source), len(warehouse), 0),
        ("total_ead", source["ead"].sum(), warehouse["ead"].sum(), 0.01),
        ("average_pd", source["pd_score"].mean(), warehouse["pd_score"].mean(), 1e-6),
        ("average_lgd", source["lgd"].mean(), warehouse["lgd"].mean(), 1e-6),
        ("watchlist_accounts", source["watchlist_flag"].sum(), warehouse["watchlist_flag"].sum(), 0),
    )
    results = [
        _record(connection, batch_id, asset_id, name, src, wh, tolerance)
        for name, src, wh, tolerance in metric_specs
    ]

    for stage in ("STAGE 1", "STAGE 2", "STAGE 3"):
        source_count = int(
            source["ifrs_stage"]
            .astype(str)
            .str.replace("_", " ", regex=False)
            .str.upper()
            .eq(stage)
            .sum()
        )
        warehouse_count = int((warehouse["ifrs_stage"] == stage).sum())
        results.append(
            _record(
                connection,
                batch_id,
                asset_id,
                f"ifrs_stage:{stage}",
                source_count,
                warehouse_count,
                0,
            )
        )

    for band, source_count in source["risk_band"].value_counts().items():
        warehouse_count = int((warehouse["risk_band"] == band).sum())
        results.append(
            _record(
                connection,
                batch_id,
                asset_id,
                f"risk_band:{band}",
                int(source_count),
                warehouse_count,
                0,
            )
        )

    mart_count = connection.execute(
        "SELECT portfolio_count FROM mart.mart_executive_current"
    ).fetchone()[0]
    results.append(
        _record(
            connection,
            batch_id,
            asset_id,
            "executive_mart:portfolio_count",
            len(source),
            mart_count,
            0,
        )
    )
    return results


def run_phase4b_reconciliation(
    connection,
    batch_id: str,
    job_id: str | None,
) -> dict:
    source_path = ROOT_DIR / "data" / "processed" / "scored_portfolio.csv"
    current_hash = file_sha256(source_path)
    asset_id = source_asset_id(source_path, current_hash)
    source_count = int(len(pd.read_csv(source_path, usecols=["borrower_id"])))
    staging_count = int(
        connection.execute(
            """
            SELECT COUNT(*)
            FROM staging.stg_scored_portfolio
            WHERE source_asset_id = ?
            """,
            [asset_id],
        ).fetchone()[0]
    )
    core_count = int(
        connection.execute(
            """
            SELECT COUNT(*)
            FROM core.fact_credit_risk_snapshot
            WHERE source_asset_id = ?
            """,
            [asset_id],
        ).fetchone()[0]
    )
    mart_count = int(
        connection.execute(
            "SELECT COUNT(*) FROM mart.mart_credit_risk_current"
        ).fetchone()[0]
    )
    counts = [source_count, staging_count, core_count, mart_count]
    variance = float(max(counts) - min(counts))
    status = "PASS" if variance == 0 else "FAIL"
    reconciliation_id = hashlib.sha256(
        f"{batch_id}|PHASE4B|END_TO_END_ROW_PARITY".encode("utf-8")
    ).hexdigest()[:32]
    connection.execute(
        """
        INSERT OR REPLACE INTO control.reconciliation_result (
            reconciliation_id, etl_batch_id, source_asset_id,
            reconciliation_name, source_value, warehouse_value,
            absolute_difference, tolerance, status, reconciled_at,
            job_id, source_count, staging_count, core_count, mart_count,
            variance
        ) VALUES (?, ?, ?, 'phase4b:end_to_end_row_parity', ?, ?, ?, 0, ?, ?,
                  ?, ?, ?, ?, ?, ?)
        """,
        [
            reconciliation_id,
            batch_id,
            asset_id,
            float(source_count),
            float(mart_count),
            variance,
            status,
            datetime.now(timezone.utc),
            job_id,
            source_count,
            staging_count,
            core_count,
            mart_count,
            variance,
        ],
    )
    return {
        "source_asset_id": asset_id,
        "source_count": source_count,
        "staging_count": staging_count,
        "core_count": core_count,
        "mart_count": mart_count,
        "variance": variance,
        "status": status,
    }
