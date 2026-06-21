from __future__ import annotations

import pandas as pd


MEAN_METRICS = {
    "pd": "pd_score",
    "lgd": "lgd",
    "ead": "ead",
    "credit_score": "credit_score",
    "current_credit_loss_proxy": "pd_score * lgd * ead",
}


def descriptive_statistics(connection, metric: str) -> dict:
    expression = MEAN_METRICS[metric]
    row = connection.execute(
        f"""
        SELECT
            COUNT({expression}) AS n,
            COUNT(*) - COUNT({expression}) AS missing,
            AVG({expression}) AS mean,
            MEDIAN({expression}) AS median,
            MIN({expression}) AS minimum,
            MAX({expression}) AS maximum,
            STDDEV_SAMP({expression}) AS std_dev,
            QUANTILE_CONT({expression}, 0.01) AS p1,
            QUANTILE_CONT({expression}, 0.05) AS p5,
            QUANTILE_CONT({expression}, 0.25) AS p25,
            QUANTILE_CONT({expression}, 0.75) AS p75,
            QUANTILE_CONT({expression}, 0.95) AS p95,
            QUANTILE_CONT({expression}, 0.99) AS p99,
            SUM({expression}) AS sum
        FROM mart.mart_credit_risk_current
        """
    ).fetchone()
    columns = (
        "n",
        "missing",
        "mean",
        "median",
        "minimum",
        "maximum",
        "std_dev",
        "p1",
        "p5",
        "p25",
        "p75",
        "p95",
        "p99",
        "sum",
    )
    result = {"metric": metric}
    result.update(dict(zip(columns, row)))
    result["n"] = int(result["n"])
    result["missing"] = int(result["missing"])
    return result


def run_proc_means(connection) -> pd.DataFrame:
    return pd.DataFrame(
        [
            descriptive_statistics(connection, metric)
            for metric in MEAN_METRICS
        ]
    )
