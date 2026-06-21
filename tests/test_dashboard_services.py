from __future__ import annotations

import pandas as pd

from app.risk_pulse_service import build_risk_pulse_view_model
from app.stress_lab_service import SCENARIOS, build_stress_view_model


def test_stress_view_model_keeps_engine_orchestration_out_of_ui() -> None:
    portfolio = pd.DataFrame([{"borrower_id": "B1"}])

    def run_stress(frame, scenario):
        multiplier = SCENARIOS.index(scenario) + 1
        return {
            "portfolio_results": frame.assign(scenario=scenario),
            "summary": {
                "baseline_portfolio_loss": 100.0,
                "stressed_portfolio_loss": 100.0 * multiplier,
                "average_stressed_pd": 0.05 * multiplier,
                "portfolio_loss_deterioration_pct": 25.0 * multiplier,
                "stress_grade": f"G{multiplier}",
                "stress_concentration": 10.0 * multiplier,
            },
        }

    result = build_stress_view_model(
        portfolio,
        "SEVERE RECESSION",
        run_stress=run_stress,
        run_macro=lambda frame, scenario: {
            "portfolio_results": frame.assign(scenario=scenario),
            "summary": {"systemic_stress_score": 50.0},
        },
        run_var=lambda frame: {"var": len(frame)},
        run_cvar=lambda frame: {"cvar": len(frame)},
        run_capital=lambda **kwargs: {
            "capital_resilience_score": 60.0,
            "stressed_capital_ratio": 10.0,
            **kwargs,
        },
    )

    assert len(result["comparison_df"]) == len(SCENARIOS)
    assert result["worst_case"]["Scenario"] == "FINANCIAL CRISIS"
    assert result["enterprise_status"] in {
        "MODERATE RISK",
        "HIGH RISK",
        "CRITICAL RISK",
    }
    assert "Review capital adequacy planning." in result[
        "executive_recommendations"
    ]


def test_risk_pulse_view_model_builds_engine_contracts() -> None:
    portfolio = pd.DataFrame(
        [
            {
                "borrower_id": "B1",
                "pd_score": 0.25,
                "early_warning_score": 30.0,
                "risk_migration_score": 20.0,
            }
        ]
    )
    live_context = {
        "summary": {
            "macro_stress_score": 40.0,
            "market_stress_score": 50.0,
            "sentiment_stress_score": 60.0,
            "enterprise_live_risk_score": 50.0,
        },
        "macro_intelligence": {
            "inflation_rate": 3.0,
            "unemployment_rate": 4.0,
        },
        "market_intelligence": {"volatility_score": 35.0},
        "news_intelligence": {"headline_count": 10},
    }

    def run_pulse(frame, **kwargs):
        return {
            "risk_pulse_results": frame[
                ["borrower_id"]
            ].assign(live_risk_pulse_score=55.0),
            "summary": {"status": "PASS"},
        }

    def run_regime(frame, **kwargs):
        return {
            "regime_results": frame.assign(
                executive_cycle_regime="WATCH"
            ),
            "summary": {"status": "PASS"},
        }

    def run_alerts(frame, **kwargs):
        return {
            "live_alert_results": frame.assign(
                executive_alert_level="WATCH"
            ),
            "summary": {"status": "PASS"},
        }

    result = build_risk_pulse_view_model(
        portfolio,
        live_context,
        run_pulse=run_pulse,
        run_regime=run_regime,
        run_alerts=run_alerts,
    )

    assert result["portfolio"]["stress_score"].iloc[0] == 50.0
    assert result["pulse_df"]["live_risk_pulse_score"].iloc[0] == 55.0
    assert result["regime_df"].iloc[-1]["period"] == "LIVE-CURRENT"
    assert result["alert_df"]["executive_alert_level"].iloc[0] == "WATCH"
