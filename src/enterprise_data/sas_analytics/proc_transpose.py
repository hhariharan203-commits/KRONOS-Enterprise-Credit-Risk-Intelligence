from __future__ import annotations

import pandas as pd

from src.enterprise_data.sas_analytics.contracts import AnalyticsContractError
from src.enterprise_data.sas_analytics.proc_summary import grouped_summary


TRANSPOSE_DIMENSIONS = (
    "risk_band",
    "ifrs9_stage",
    "industry",
    "region",
    "underwriting_decision",
)

TRANSPOSE_SOURCE_DIMENSIONS = {
    "risk_band": "risk_band",
    "ifrs9_stage": "ifrs9_stage",
    "industry": "industry",
    "region": "region",
}


def _decision_summary(connection) -> pd.DataFrame:
    frame = connection.execute(
        """
        SELECT
            underwriting_decision AS category,
            COUNT(*) AS count,
            SUM(ead) AS total_ead,
            SUM(pd_score * lgd * ead) AS current_credit_loss_proxy
        FROM mart.mart_credit_risk_current
        GROUP BY underwriting_decision
        ORDER BY underwriting_decision
        """
    ).fetchdf()
    total = pd.DataFrame(
        [
            {
                "category": "TOTAL",
                "count": int(frame["count"].sum()),
                "total_ead": float(frame["total_ead"].sum()),
                "current_credit_loss_proxy": float(
                    frame["current_credit_loss_proxy"].sum()
                ),
            }
        ]
    )
    return pd.concat([frame, total], ignore_index=True)


def transpose_summary(connection, dimension: str) -> pd.DataFrame:
    if dimension not in TRANSPOSE_DIMENSIONS:
        raise AnalyticsContractError(
            f"Unsupported PROC-Equivalent transpose dimension: {dimension}"
        )
    if dimension == "underwriting_decision":
        summary = _decision_summary(connection)
    else:
        summary = grouped_summary(
            connection,
            TRANSPOSE_SOURCE_DIMENSIONS[dimension],
        )
    measures = ("count", "total_ead", "current_credit_loss_proxy")
    rows = []
    for measure in measures:
        row = {"dimension": dimension, "measure": measure}
        for record in summary[["category", measure]].to_dict("records"):
            row[str(record["category"])] = record[measure]
        rows.append(row)
    return pd.DataFrame(rows)


def run_proc_transpose(connection) -> dict[str, pd.DataFrame]:
    return {
        dimension: transpose_summary(connection, dimension)
        for dimension in TRANSPOSE_DIMENSIONS
    }
