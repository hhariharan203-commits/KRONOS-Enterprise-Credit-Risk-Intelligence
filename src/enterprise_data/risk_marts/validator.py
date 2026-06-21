from __future__ import annotations

import math

from src.enterprise_data.risk_marts.contracts import (
    EXPECTED_DIMENSION_COUNTS,
    EXPECTED_EXISTING_MART_ROWS,
    EXPECTED_PORTFOLIO_COUNT,
    EXPECTED_STAGE_TOTAL,
    EXPECTED_TOTAL_EAD,
    EXPECTED_WATCHLIST_COUNT,
    MINIMUM_HISTORY_MART_ROWS,
    Phase4DContractError,
)
from src.enterprise_data.risk_marts.source_catalog import (
    VIEW_NAMES,
    existing_mart_row_counts,
    phase4d_view_row_counts,
)


def _check(checks: list[dict], name: str, passed: bool, actual, expected) -> None:
    checks.append(
        {
            "check_name": name,
            "status": "PASS" if passed else "FAIL",
            "actual": actual,
            "expected": expected,
        }
    )


def validate_phase4d(
    connection,
    expected_existing_mart_rows: dict[str, int] | None = None,
) -> dict:
    checks: list[dict] = []
    available_views = {
        str(row[0])
        for row in connection.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'mart' AND table_type = 'VIEW'
            """
        ).fetchall()
    }
    for view in VIEW_NAMES:
        _check(
            checks,
            f"view_exists:{view}",
            view in available_views,
            view in available_views,
            True,
        )

    mart_rows = existing_mart_row_counts(connection)
    for mart, expected in EXPECTED_EXISTING_MART_ROWS.items():
        _check(
            checks,
            f"existing_mart_rows:{mart}",
            mart_rows[mart] == expected,
            mart_rows[mart],
            expected,
        )
    for mart, minimum in MINIMUM_HISTORY_MART_ROWS.items():
        _check(
            checks,
            f"history_mart_minimum:{mart}",
            mart_rows[mart] >= minimum,
            mart_rows[mart],
            f">={minimum}",
        )
    if expected_existing_mart_rows is not None:
        for mart, expected in expected_existing_mart_rows.items():
            _check(
                checks,
                f"preserved_mart_rows:{mart}",
                mart_rows[mart] == expected,
                mart_rows[mart],
                expected,
            )

    portfolio = connection.execute(
        """
        SELECT portfolio_count, total_ead, watchlist_count,
               stage_1_count + stage_2_count + stage_3_count
        FROM mart.vw_portfolio_quality_current
        """
    ).fetchone()
    _check(
        checks,
        "portfolio_count",
        int(portfolio[0]) == EXPECTED_PORTFOLIO_COUNT,
        int(portfolio[0]),
        EXPECTED_PORTFOLIO_COUNT,
    )
    _check(
        checks,
        "total_ead",
        math.isclose(
            float(portfolio[1]),
            EXPECTED_TOTAL_EAD,
            abs_tol=0.01,
        ),
        round(float(portfolio[1]), 2),
        EXPECTED_TOTAL_EAD,
    )
    _check(
        checks,
        "watchlist_count",
        int(portfolio[2]) == EXPECTED_WATCHLIST_COUNT,
        int(portfolio[2]),
        EXPECTED_WATCHLIST_COUNT,
    )
    _check(
        checks,
        "ifrs9_stage_total",
        int(portfolio[3]) == EXPECTED_STAGE_TOTAL,
        int(portfolio[3]),
        EXPECTED_STAGE_TOTAL,
    )

    dimension_rows = connection.execute(
        """
        SELECT
            dimension_type,
            COUNT(*) AS category_count,
            SUM(exposure_share) AS exposure_share
        FROM mart.vw_concentration_risk_current
        GROUP BY dimension_type
        ORDER BY dimension_type
        """
    ).fetchall()
    dimensions = {
        str(row[0]): (int(row[1]), float(row[2]))
        for row in dimension_rows
    }
    for dimension, expected_count in EXPECTED_DIMENSION_COUNTS.items():
        actual_count, exposure_share = dimensions.get(dimension, (0, 0.0))
        _check(
            checks,
            f"dimension_count:{dimension}",
            actual_count == expected_count,
            actual_count,
            expected_count,
        )
        _check(
            checks,
            f"exposure_share:{dimension}",
            math.isclose(exposure_share, 1.0, abs_tol=1e-10),
            exposure_share,
            1.0,
        )

    watchlist_count = int(
        connection.execute(
            "SELECT COUNT(*) FROM mart.vw_watchlist_intelligence_current"
        ).fetchone()[0]
    )
    _check(
        checks,
        "watchlist_view_count",
        watchlist_count == EXPECTED_WATCHLIST_COUNT,
        watchlist_count,
        EXPECTED_WATCHLIST_COUNT,
    )

    model_families = {
        str(row[0])
        for row in connection.execute(
            """
            SELECT model_family
            FROM mart.vw_model_governance_current
            """
        ).fetchall()
    }
    _check(
        checks,
        "model_families",
        model_families == {"PD", "LGD", "EAD"},
        sorted(model_families),
        ["EAD", "LGD", "PD"],
    )

    enterprise_count = int(
        connection.execute(
            "SELECT COUNT(*) FROM mart.vw_enterprise_risk_summary_current"
        ).fetchone()[0]
    )
    _check(
        checks,
        "enterprise_summary_rows",
        enterprise_count == 1,
        enterprise_count,
        1,
    )

    failures = [check for check in checks if check["status"] == "FAIL"]
    if failures:
        raise Phase4DContractError(
            f"Phase 4D validation failed: {failures}"
        )
    return {
        "status": "PASS",
        "check_count": len(checks),
        "failure_count": 0,
        "checks": checks,
        "existing_mart_row_counts": mart_rows,
        "phase4d_view_row_counts": phase4d_view_row_counts(connection),
    }
