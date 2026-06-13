from __future__ import annotations

import pandas as pd

from src.shared.config import SCORED_PORTFOLIO_DATA


REQUIRED_COLUMNS = {
    "borrower_id",
    "pd_score",
    "lgd",
    "ead",
    "credit_score",
    "risk_band",
    "risk_grade",
    "underwriting_decision",
    "ifrs_stage",
    "timestamp",
    "model_version",
    "run_id",
    "scoring_status",
}


def test_scored_portfolio_schema_and_rows() -> None:
    portfolio = pd.read_csv(SCORED_PORTFOLIO_DATA)
    assert len(portfolio) > 0
    assert REQUIRED_COLUMNS.issubset(portfolio.columns)
    assert portfolio["borrower_id"].notna().all()
    assert portfolio["scoring_status"].eq("SCORED").all()


def test_scored_portfolio_numeric_contracts() -> None:
    portfolio = pd.read_csv(SCORED_PORTFOLIO_DATA, usecols=["pd_score", "lgd", "ead"])
    for column in ["pd_score", "lgd", "ead"]:
        numeric = pd.to_numeric(portfolio[column], errors="coerce")
        assert numeric.notna().all()
    assert portfolio["pd_score"].between(0, 1).all()
    assert portfolio["lgd"].between(0, 1).all()
    assert (portfolio["ead"] >= 0).all()

