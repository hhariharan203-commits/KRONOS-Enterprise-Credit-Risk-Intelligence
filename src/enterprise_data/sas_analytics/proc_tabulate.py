from __future__ import annotations

from itertools import product

import pandas as pd

from src.enterprise_data.sas_analytics.contracts import AnalyticsContractError


TABULATE_DIMENSIONS = {
    "industry": "industry",
    "region": "region",
    "risk_band": "risk_band",
    "ifrs9_stage": "ifrs_stage",
    "risk_grade": "risk_grade",
    "decision": "underwriting_decision",
}

TABULATE_SPECS = (
    ("industry", "risk_band"),
    ("industry", "ifrs9_stage"),
    ("region", "risk_band"),
    ("risk_grade", "decision"),
)

DOMAIN_ORDERS = {
    "risk_band": [
        "PRIME",
        "NEAR PRIME",
        "MODERATE RISK",
        "HIGH RISK",
        "DEFAULT RISK",
    ],
    "ifrs9_stage": ["STAGE 1", "STAGE 2", "STAGE 3"],
    "risk_grade": ["AAA", "AA", "A", "BBB", "BB", "B", "CCC"],
    "decision": ["APPROVE", "WATCH", "HIGH RISK REVIEW", "REJECT"],
}


def _domain(connection, dimension: str) -> list[str]:
    column = TABULATE_DIMENSIONS[dimension]
    values = [
        str(row[0])
        for row in connection.execute(
            f"""
            SELECT DISTINCT {column}
            FROM mart.mart_credit_risk_current
            WHERE {column} IS NOT NULL
            ORDER BY {column}
            """
        ).fetchall()
    ]
    configured = DOMAIN_ORDERS.get(dimension)
    if configured is None:
        return values
    return [value for value in configured if value in values]


def dense_table(
    connection,
    row_dimension: str,
    column_dimension: str,
) -> pd.DataFrame:
    if row_dimension not in TABULATE_DIMENSIONS:
        raise AnalyticsContractError(
            f"Unsupported tabulate row dimension: {row_dimension}"
        )
    if column_dimension not in TABULATE_DIMENSIONS:
        raise AnalyticsContractError(
            f"Unsupported tabulate column dimension: {column_dimension}"
        )
    row_column = TABULATE_DIMENSIONS[row_dimension]
    column_column = TABULATE_DIMENSIONS[column_dimension]
    aggregate = connection.execute(
        f"""
        SELECT
            {row_column} AS row_value,
            {column_column} AS column_value,
            COUNT(*) AS count,
            SUM(ead) AS total_ead
        FROM mart.mart_credit_risk_current
        GROUP BY {row_column}, {column_column}
        """
    ).fetchdf()
    grid = pd.DataFrame(
        product(
            _domain(connection, row_dimension),
            _domain(connection, column_dimension),
        ),
        columns=["row_value", "column_value"],
    )
    detail = grid.merge(
        aggregate,
        on=["row_value", "column_value"],
        how="left",
    )
    detail["count"] = detail["count"].fillna(0).astype(int)
    detail["total_ead"] = detail["total_ead"].fillna(0.0)
    detail["cell_type"] = "DETAIL"

    row_totals = (
        detail.groupby("row_value", as_index=False)[["count", "total_ead"]]
        .sum()
    )
    row_totals["column_value"] = "TOTAL"
    row_totals["cell_type"] = "ROW_TOTAL"

    column_totals = (
        detail.groupby("column_value", as_index=False)[["count", "total_ead"]]
        .sum()
    )
    column_totals["row_value"] = "TOTAL"
    column_totals["cell_type"] = "COLUMN_TOTAL"

    grand_total = pd.DataFrame(
        [
            {
                "row_value": "TOTAL",
                "column_value": "TOTAL",
                "count": int(detail["count"].sum()),
                "total_ead": float(detail["total_ead"].sum()),
                "cell_type": "GRAND_TOTAL",
            }
        ]
    )
    result = pd.concat(
        [detail, row_totals, column_totals, grand_total],
        ignore_index=True,
    )
    result.insert(0, "column_dimension", column_dimension)
    result.insert(0, "row_dimension", row_dimension)
    result.insert(0, "table_name", f"{row_dimension}_by_{column_dimension}")
    return result[
        [
            "table_name",
            "row_dimension",
            "row_value",
            "column_dimension",
            "column_value",
            "count",
            "total_ead",
            "cell_type",
        ]
    ]


def run_proc_tabulate(connection) -> pd.DataFrame:
    return pd.concat(
        [
            dense_table(connection, row_dimension, column_dimension)
            for row_dimension, column_dimension in TABULATE_SPECS
        ],
        ignore_index=True,
    )
