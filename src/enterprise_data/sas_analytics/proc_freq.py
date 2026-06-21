from __future__ import annotations

import pandas as pd

from src.enterprise_data.sas_analytics.contracts import AnalyticsContractError


FREQUENCY_SPECS = {
    "risk_band": {
        "column": "risk_band",
        "order": [
            "PRIME",
            "NEAR PRIME",
            "MODERATE RISK",
            "HIGH RISK",
            "DEFAULT RISK",
        ],
    },
    "risk_grade": {
        "column": "risk_grade",
        "order": ["AAA", "AA", "A", "BBB", "BB", "B", "CCC"],
    },
    "industry": {"column": "industry", "order": None},
    "region": {"column": "region", "order": None},
    "ifrs9_stage": {
        "column": "ifrs_stage",
        "order": ["STAGE 1", "STAGE 2", "STAGE 3"],
    },
    "watchlist_status": {
        "column": "watchlist_flag",
        "order": ["NON-WATCHLIST", "WATCHLIST"],
    },
    "underwriting_decision": {
        "column": "underwriting_decision",
        "order": ["APPROVE", "WATCH", "HIGH RISK REVIEW", "REJECT"],
    },
    "risk_profile": {
        "column": "risk_profile",
        "order": ["PRIME", "NEAR_PRIME", "HIGH_RISK", "SUBPRIME"],
    },
}


def frequency_table(connection, variable: str) -> pd.DataFrame:
    if variable not in FREQUENCY_SPECS:
        raise AnalyticsContractError(
            f"Unsupported PROC-Equivalent frequency variable: {variable}"
        )
    spec = FREQUENCY_SPECS[variable]
    column = spec["column"]
    if variable == "watchlist_status":
        category_expression = (
            "CASE WHEN watchlist_flag = 1 THEN 'WATCHLIST' "
            "ELSE 'NON-WATCHLIST' END"
        )
    else:
        category_expression = column
    frame = connection.execute(
        f"""
        SELECT
            {category_expression} AS category,
            COUNT(*) AS count
        FROM mart.mart_credit_risk_current
        GROUP BY category
        """
    ).fetchdf()
    order = spec["order"]
    if order is None:
        order = sorted(frame["category"].astype(str).tolist())
    domain = pd.DataFrame({"category": order})
    frame = domain.merge(frame, on="category", how="left")
    frame["count"] = frame["count"].fillna(0).astype(int)
    total = int(frame["count"].sum())
    if total <= 0:
        raise AnalyticsContractError(f"Frequency total is zero for {variable}.")
    frame["percentage"] = frame["count"] / total * 100
    frame["cumulative_percentage"] = frame["percentage"].cumsum()
    frame.insert(0, "variable", variable)
    return frame


def run_proc_freq(connection) -> pd.DataFrame:
    frames = [
        frequency_table(connection, variable)
        for variable in FREQUENCY_SPECS
    ]
    return pd.concat(frames, ignore_index=True)
