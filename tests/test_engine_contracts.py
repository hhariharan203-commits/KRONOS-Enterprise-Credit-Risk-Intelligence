from __future__ import annotations

import pandas as pd

from src.decisioning.decision_terminal import run_decision_engine
from src.ews.ews_engine import run_ews_engine
from src.live_monitoring.risk_pulse import run_risk_pulse_engine
from src.provisioning.ecl_calculator import run_ecl_pipeline
from src.stress_testing.stress_engine import run_stress_pipeline


def _sample_portfolio() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"borrower_id": "T001", "pd_score": 0.05, "lgd": 0.24, "ead": 25_000, "current_stage": "STAGE 1"},
            {"borrower_id": "T002", "pd_score": 0.32, "lgd": 0.58, "ead": 75_000, "current_stage": "STAGE 2"},
            {"borrower_id": "T003", "pd_score": 0.71, "lgd": 0.82, "ead": 120_000, "current_stage": "STAGE 3"},
        ]
    )


def test_provisioning_contract() -> None:
    result = run_ecl_pipeline(_sample_portfolio())
    assert {"portfolio_results", "summary", "top_reserve_exposures"}.issubset(result)
    assert len(result["portfolio_results"]) == 3


def test_stress_contract() -> None:
    result = run_stress_pipeline(_sample_portfolio(), "SEVERE RECESSION")
    assert {"portfolio_results", "summary", "top_stressed_accounts"}.issubset(result)
    assert len(result["portfolio_results"]) == 3


def test_decision_contract() -> None:
    frame = _sample_portfolio().assign(
        systemic_risk_score=[20, 55, 88],
        reserve_pressure_score=[15, 45, 85],
        ews_score=[20, 50, 90],
    )
    result = run_decision_engine(frame)
    assert {"decision_results", "summary"}.issubset(result)
    assert len(result["decision_results"]) == 3


def test_risk_pulse_contract() -> None:
    frame = _sample_portfolio().assign(
        systemic_risk_score=[20, 55, 88],
        stress_score=[15, 50, 90],
        reserve_pressure_score=[10, 45, 85],
        previous_pulse_score=[20, 45, 70],
    )
    result = run_risk_pulse_engine(frame)
    assert {"risk_pulse_results", "summary"}.issubset(result)
    assert len(result["risk_pulse_results"]) == 3


def test_ews_scalar_contract() -> None:
    result = run_ews_engine(
        {
            "current_pd": 0.42,
            "previous_pd": 0.24,
            "credit_utilization": 0.72,
            "payment_burden_ratio": 0.45,
            "loan_to_income_ratio": 0.58,
            "total_delinquency": 2,
        }
    )
    assert {"ews_score", "alert_level", "monitoring_priority", "executive_narrative"}.issubset(result)

