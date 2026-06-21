from __future__ import annotations

import pandas as pd

from src.enterprise_data.sas_analytics.contracts import AnalyticsContractError


RANK_METRICS = {
    "pd": "pd_score",
    "lgd": "lgd",
    "ead": "ead",
    "credit_score": "credit_score",
}


def decile_summary(connection, metric: str) -> pd.DataFrame:
    if metric not in RANK_METRICS:
        raise AnalyticsContractError(
            f"Unsupported PROC-Equivalent rank metric: {metric}"
        )
    expression = RANK_METRICS[metric]
    frame = connection.execute(
        f"""
        WITH ranked AS (
            SELECT
                borrower_key,
                {expression} AS metric_value,
                ead,
                pd_score * lgd * ead AS current_credit_loss_proxy,
                NTILE(10) OVER (
                    ORDER BY {expression}, borrower_key
                ) AS decile
            FROM mart.mart_credit_risk_current
        )
        SELECT
            decile,
            COUNT(*) AS count,
            MIN(metric_value) AS minimum,
            MAX(metric_value) AS maximum,
            AVG(metric_value) AS mean,
            SUM(ead) AS total_ead,
            SUM(current_credit_loss_proxy) AS current_credit_loss_proxy
        FROM ranked
        GROUP BY decile
        ORDER BY decile
        """
    ).fetchdf()
    frame.insert(0, "metric", metric)
    frame["decile"] = frame["decile"].astype(int)
    frame["count"] = frame["count"].astype(int)
    return frame


def run_proc_rank(connection) -> pd.DataFrame:
    return pd.concat(
        [decile_summary(connection, metric) for metric in RANK_METRICS],
        ignore_index=True,
    )
