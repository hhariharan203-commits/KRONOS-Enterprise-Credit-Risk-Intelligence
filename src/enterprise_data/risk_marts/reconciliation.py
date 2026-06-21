from __future__ import annotations

import math

from src.enterprise_data.risk_marts.contracts import Phase4DContractError


def _record(
    name: str,
    source_value,
    view_value,
    *,
    tolerance: float = 0.0,
) -> dict:
    difference = abs(float(source_value) - float(view_value))
    return {
        "reconciliation_name": name,
        "source_value": source_value,
        "view_value": view_value,
        "absolute_difference": difference,
        "tolerance": tolerance,
        "status": "PASS" if difference <= tolerance else "FAIL",
    }


def reconcile_phase4d(connection) -> dict:
    source = connection.execute(
        """
        SELECT
            COUNT(*),
            SUM(ead),
            SUM(CASE WHEN watchlist_flag = 1 THEN 1 ELSE 0 END),
            SUM(CASE WHEN ifrs_stage IN ('STAGE 1', 'STAGE 2', 'STAGE 3')
                     THEN 1 ELSE 0 END)
        FROM mart.mart_credit_risk_current
        """
    ).fetchone()
    quality = connection.execute(
        """
        SELECT
            portfolio_count,
            total_ead,
            watchlist_count,
            stage_1_count + stage_2_count + stage_3_count
        FROM mart.vw_portfolio_quality_current
        """
    ).fetchone()
    enterprise = connection.execute(
        """
        SELECT portfolio_count, total_ead, watchlist_count
        FROM mart.vw_enterprise_risk_summary_current
        """
    ).fetchone()

    records = [
        _record("portfolio_count", source[0], quality[0]),
        _record("portfolio_total_ead", source[1], quality[1], tolerance=0.01),
        _record("portfolio_watchlist_count", source[2], quality[2]),
        _record("portfolio_stage_total", source[3], quality[3]),
        _record("enterprise_portfolio_count", source[0], enterprise[0]),
        _record(
            "enterprise_total_ead",
            source[1],
            enterprise[1],
            tolerance=0.01,
        ),
        _record("enterprise_watchlist_count", source[2], enterprise[2]),
    ]

    concentration = connection.execute(
        """
        SELECT dimension_type, SUM(total_ead), SUM(exposure_share)
        FROM mart.vw_concentration_risk_current
        GROUP BY dimension_type
        ORDER BY dimension_type
        """
    ).fetchall()
    for dimension, total_ead, exposure_share in concentration:
        records.append(
            _record(
                f"concentration_total_ead:{dimension}",
                source[1],
                total_ead,
                tolerance=0.01,
            )
        )
        records.append(
            _record(
                f"concentration_exposure_share:{dimension}",
                1.0,
                exposure_share,
                tolerance=1e-10,
            )
        )

    watchlist_rows = connection.execute(
        """
        SELECT COUNT(*), MIN(priority_rank), MAX(priority_rank)
        FROM mart.vw_watchlist_intelligence_current
        """
    ).fetchone()
    records.extend(
        [
            _record("watchlist_row_count", source[2], watchlist_rows[0]),
            _record("watchlist_min_rank", 1, watchlist_rows[1]),
            _record("watchlist_max_rank", source[2], watchlist_rows[2]),
        ]
    )

    model_count = int(
        connection.execute(
            "SELECT COUNT(*) FROM mart.vw_model_governance_current"
        ).fetchone()[0]
    )
    records.append(_record("model_family_count", 3, model_count))

    failures = [record for record in records if record["status"] == "FAIL"]
    if failures:
        raise Phase4DContractError(
            f"Phase 4D reconciliation failed: {failures}"
        )
    return {
        "status": "PASS",
        "reconciliation_count": len(records),
        "failure_count": 0,
        "records": records,
    }
