from __future__ import annotations

import pandas as pd

from src.enterprise_data.sas_analytics.contracts import AnalyticsContractError


CONCENTRATION_DIMENSIONS = {
    "industry": "industry",
    "region": "region",
}


def concentration_detail(connection, dimension: str) -> pd.DataFrame:
    if dimension not in CONCENTRATION_DIMENSIONS:
        raise AnalyticsContractError(
            f"Unsupported concentration dimension: {dimension}"
        )
    column = CONCENTRATION_DIMENSIONS[dimension]
    frame = connection.execute(
        f"""
        WITH grouped AS (
            SELECT
                {column} AS category,
                COUNT(*) AS count,
                SUM(ead) AS total_ead,
                AVG(pd_score) AS average_pd,
                AVG(lgd) AS average_lgd
            FROM mart.mart_credit_risk_current
            GROUP BY {column}
        )
        SELECT
            category,
            count,
            total_ead,
            total_ead / SUM(total_ead) OVER () AS exposure_share,
            POWER(total_ead / SUM(total_ead) OVER (), 2) AS hhi_contribution,
            average_pd,
            average_lgd
        FROM grouped
        ORDER BY total_ead DESC, category
        """
    ).fetchdf()
    frame.insert(0, "dimension", dimension)
    return frame


def concentration_summary(connection, dimension: str) -> pd.DataFrame:
    detail = concentration_detail(connection, dimension)
    return pd.DataFrame(
        [
            {
                "dimension": dimension,
                "category_count": int(len(detail)),
                "hhi": float(detail["hhi_contribution"].sum()),
                "largest_exposure_share": float(detail["exposure_share"].max()),
                "top_3_exposure_share": float(
                    detail["exposure_share"].head(3).sum()
                ),
                "total_ead": float(detail["total_ead"].sum()),
            }
        ]
    )


def top_exposure_concentration(connection) -> pd.DataFrame:
    return connection.execute(
        """
        WITH ranked AS (
            SELECT
                borrower_key,
                facility_key,
                ead,
                ROW_NUMBER() OVER (ORDER BY ead DESC, borrower_key) AS exposure_rank,
                ead / SUM(ead) OVER () AS exposure_share
            FROM mart.mart_credit_risk_current
        )
        SELECT
            exposure_rank,
            borrower_key,
            facility_key,
            ead,
            exposure_share,
            SUM(exposure_share) OVER (
                ORDER BY exposure_rank
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) AS cumulative_exposure_share
        FROM ranked
        WHERE exposure_rank <= 25
        ORDER BY exposure_rank
        """
    ).fetchdf()


def run_concentration_analytics(connection) -> dict[str, pd.DataFrame]:
    details = [
        concentration_detail(connection, dimension)
        for dimension in CONCENTRATION_DIMENSIONS
    ]
    summaries = [
        concentration_summary(connection, dimension)
        for dimension in CONCENTRATION_DIMENSIONS
    ]
    return {
        "concentration_detail": pd.concat(details, ignore_index=True),
        "concentration_summary": pd.concat(summaries, ignore_index=True),
        "top_exposure_concentration": top_exposure_concentration(connection),
    }
