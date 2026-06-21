from __future__ import annotations

import pandas as pd

from src.enterprise_data.sas_analytics.proc_summary import grouped_summary


def portfolio_summary(connection) -> pd.DataFrame:
    return connection.execute(
        """
        SELECT
            COUNT(*) AS portfolio_size,
            SUM(ead) AS total_ead,
            AVG(pd_score) AS average_pd,
            AVG(lgd) AS average_lgd,
            SUM(pd_score * ead) / NULLIF(SUM(ead), 0) AS weighted_pd,
            SUM(lgd * ead) / NULLIF(SUM(ead), 0) AS weighted_lgd,
            SUM(pd_score * lgd * ead) AS current_credit_loss_proxy,
            SUM(CASE WHEN watchlist_flag = 1 THEN 1 ELSE 0 END) AS watchlist_count,
            SUM(CASE WHEN ifrs_stage = 'STAGE 2' THEN 1 ELSE 0 END) AS stage_2_count,
            SUM(CASE WHEN ifrs_stage = 'STAGE 3' THEN 1 ELSE 0 END) AS stage_3_count,
            SUM(CASE WHEN risk_band IN ('HIGH RISK', 'DEFAULT RISK')
                     THEN 1 ELSE 0 END) AS high_risk_count
        FROM mart.mart_credit_risk_current
        """
    ).fetchdf()


def watchlist_analytics(connection) -> pd.DataFrame:
    return connection.execute(
        """
        SELECT
            CASE WHEN watchlist_flag = 1
                 THEN 'WATCHLIST' ELSE 'NON-WATCHLIST' END AS watchlist_status,
            COUNT(*) AS count,
            SUM(ead) AS total_ead,
            AVG(pd_score) AS average_pd,
            AVG(lgd) AS average_lgd,
            SUM(pd_score * ead) / NULLIF(SUM(ead), 0) AS weighted_pd,
            SUM(lgd * ead) / NULLIF(SUM(ead), 0) AS weighted_lgd,
            SUM(pd_score * lgd * ead) AS current_credit_loss_proxy
        FROM mart.mart_credit_risk_current
        GROUP BY watchlist_flag
        ORDER BY watchlist_flag
        """
    ).fetchdf()


def top_exposure_analytics(connection, limit: int = 25) -> pd.DataFrame:
    limit = max(1, min(int(limit), 100))
    return connection.execute(
        f"""
        SELECT
            borrower_key,
            facility_key,
            ead,
            ead / SUM(ead) OVER () AS exposure_share,
            pd_score,
            lgd,
            pd_score * lgd * ead AS current_credit_loss_proxy,
            risk_band,
            risk_grade,
            industry,
            region,
            ifrs_stage,
            underwriting_decision
        FROM mart.mart_credit_risk_current
        ORDER BY ead DESC, borrower_key
        LIMIT {limit}
        """
    ).fetchdf()


def loss_proxy_analytics(connection) -> pd.DataFrame:
    return grouped_summary(connection, "risk_band")[
        [
            "dimension",
            "category",
            "count",
            "total_ead",
            "current_credit_loss_proxy",
        ]
    ]


def portfolio_quality_analytics(connection) -> pd.DataFrame:
    return connection.execute(
        """
        SELECT
            COUNT(*) AS portfolio_size,
            SUM(CASE WHEN scoring_status = 'SCORED' THEN 1 ELSE 0 END)
                AS scored_count,
            SUM(CASE WHEN days_past_due > 0 THEN 1 ELSE 0 END)
                AS delinquent_count,
            AVG(days_past_due) AS average_days_past_due,
            AVG(total_delinquency) AS average_total_delinquency,
            AVG(credit_utilization) AS average_credit_utilization,
            AVG(payment_burden_ratio) AS average_payment_burden,
            AVG(loan_to_income_ratio) AS average_loan_to_income,
            AVG(early_warning_score) AS average_early_warning_score,
            SUM(CASE WHEN pd_score IS NULL OR lgd IS NULL OR ead IS NULL
                     THEN 1 ELSE 0 END) AS incomplete_risk_rows
        FROM mart.mart_credit_risk_current
        """
    ).fetchdf()


def run_portfolio_analytics(connection) -> dict[str, pd.DataFrame]:
    return {
        "portfolio_summary": portfolio_summary(connection),
        "watchlist_analytics": watchlist_analytics(connection),
        "top_exposure_analytics": top_exposure_analytics(connection),
        "current_credit_loss_proxy": loss_proxy_analytics(connection),
        "portfolio_quality": portfolio_quality_analytics(connection),
    }
