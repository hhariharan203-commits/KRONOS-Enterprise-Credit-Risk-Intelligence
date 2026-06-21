from __future__ import annotations

import pandas as pd

from src.enterprise_data.sas_analytics.contracts import AnalyticsContractError


SUMMARY_DIMENSIONS = {
    "industry": "industry",
    "region": "region",
    "risk_band": "risk_band",
    "risk_grade": "risk_grade",
    "ifrs9_stage": "ifrs_stage",
}


def grouped_summary(connection, dimension: str) -> pd.DataFrame:
    if dimension not in SUMMARY_DIMENSIONS:
        raise AnalyticsContractError(
            f"Unsupported PROC-Equivalent summary dimension: {dimension}"
        )
    column = SUMMARY_DIMENSIONS[dimension]
    frame = connection.execute(
        f"""
        SELECT
            {column} AS category,
            COUNT(*) AS count,
            SUM(ead) AS total_ead,
            AVG(pd_score) AS average_pd,
            AVG(lgd) AS average_lgd,
            SUM(pd_score * ead) / NULLIF(SUM(ead), 0) AS weighted_pd,
            SUM(lgd * ead) / NULLIF(SUM(ead), 0) AS weighted_lgd,
            SUM(pd_score * lgd * ead) AS current_credit_loss_proxy
        FROM mart.mart_credit_risk_current
        GROUP BY {column}
        ORDER BY {column}
        """
    ).fetchdf()
    total = connection.execute(
        """
        SELECT
            COUNT(*) AS count,
            SUM(ead) AS total_ead,
            AVG(pd_score) AS average_pd,
            AVG(lgd) AS average_lgd,
            SUM(pd_score * ead) / NULLIF(SUM(ead), 0) AS weighted_pd,
            SUM(lgd * ead) / NULLIF(SUM(ead), 0) AS weighted_lgd,
            SUM(pd_score * lgd * ead) AS current_credit_loss_proxy
        FROM mart.mart_credit_risk_current
        """
    ).fetchone()
    total_row = pd.DataFrame(
        [
            {
                "category": "TOTAL",
                "count": int(total[0]),
                "total_ead": total[1],
                "average_pd": total[2],
                "average_lgd": total[3],
                "weighted_pd": total[4],
                "weighted_lgd": total[5],
                "current_credit_loss_proxy": total[6],
            }
        ]
    )
    frame["count"] = frame["count"].astype(int)
    frame.insert(0, "dimension", dimension)
    total_row.insert(0, "dimension", dimension)
    return pd.concat([frame, total_row], ignore_index=True)


def run_proc_summary(connection) -> pd.DataFrame:
    return pd.concat(
        [
            grouped_summary(connection, dimension)
            for dimension in SUMMARY_DIMENSIONS
        ],
        ignore_index=True,
    )
