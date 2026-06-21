from __future__ import annotations

from collections.abc import Callable

import numpy as np
import pandas as pd


MACRO_REGIME_BASELINE = (
    ("2025-Q1", -1.2, 2.5, 3.0, 18, 20),
    ("2025-Q2", -2.0, 3.5, 4.0, 25, 25),
    ("2025-Q3", -3.5, 5.2, 5.8, 45, 40),
    ("2025-Q4", -4.5, 6.8, 7.2, 60, 55),
    ("2026-Q1", -2.0, 4.0, 5.0, 35, 40),
)


def build_risk_pulse_view_model(
    portfolio: pd.DataFrame,
    live_context: dict,
    *,
    run_pulse: Callable,
    run_regime: Callable,
    run_alerts: Callable,
) -> dict:
    portfolio = portfolio.copy()
    live_summary = live_context.get("summary", {})
    macro_intelligence = live_context.get("macro_intelligence", {})
    market_intelligence = live_context.get("market_intelligence", {})
    news_intelligence = live_context.get("news_intelligence", {})

    portfolio["systemic_risk_score"] = portfolio["pd_score"] * 100
    portfolio["reserve_pressure_score"] = portfolio["early_warning_score"]
    portfolio["stress_score"] = portfolio["early_warning_score"]
    portfolio["macro_stress_score"] = live_summary.get(
        "macro_stress_score",
        0,
    )
    portfolio["market_stress_score"] = live_summary.get(
        "market_stress_score",
        0,
    )
    portfolio["sentiment_stress_score"] = live_summary.get(
        "sentiment_stress_score",
        0,
    )
    portfolio["enterprise_live_risk_score"] = live_summary.get(
        "enterprise_live_risk_score",
        0,
    )
    portfolio["stress_score"] = np.maximum(
        portfolio["stress_score"],
        (
            portfolio["macro_stress_score"]
            + portfolio["market_stress_score"]
            + portfolio["sentiment_stress_score"]
        )
        / 3,
    )
    portfolio["previous_pulse_score"] = portfolio["risk_migration_score"]

    pulse_results = run_pulse(
        portfolio,
        live_context=live_context,
    )
    pulse_df = pulse_results["risk_pulse_results"]

    macro_df = pd.DataFrame(
        [
            {
                "period": period,
                "gdp_stress": gdp,
                "inflation_stress": inflation,
                "unemployment_stress": unemployment,
                "market_volatility": volatility,
                "previous_regime_score": previous,
            }
            for (
                period,
                gdp,
                inflation,
                unemployment,
                volatility,
                previous,
            ) in MACRO_REGIME_BASELINE
        ]
    )
    live_macro_row = pd.DataFrame(
        [
            {
                "period": "LIVE-CURRENT",
                "gdp_stress": -(
                    live_summary.get("macro_stress_score", 0) / 10
                ),
                "inflation_stress": (
                    macro_intelligence.get("inflation_rate", 0) or 0
                ),
                "unemployment_stress": (
                    macro_intelligence.get("unemployment_rate", 0) or 0
                ),
                "market_volatility": market_intelligence.get(
                    "volatility_score",
                    0,
                ),
                "previous_regime_score": live_summary.get(
                    "enterprise_live_risk_score",
                    0,
                ),
                "credit_stress_score": live_summary.get(
                    "enterprise_live_risk_score",
                    0,
                ),
            }
        ]
    )
    macro_df = pd.concat([macro_df, live_macro_row], ignore_index=True)
    regime_results = run_regime(
        macro_df,
        live_context=live_context,
    )

    alert_input = portfolio.merge(
        pulse_df[["borrower_id", "live_risk_pulse_score"]],
        on="borrower_id",
        how="left",
    )
    alert_input["previous_risk_score"] = alert_input[
        "previous_pulse_score"
    ]
    alert_results = run_alerts(
        alert_input,
        live_context=live_context,
    )

    return {
        "portfolio": portfolio,
        "live_summary": live_summary,
        "macro_intelligence": macro_intelligence,
        "market_intelligence": market_intelligence,
        "news_intelligence": news_intelligence,
        "pulse_df": pulse_df,
        "pulse_summary": pulse_results["summary"],
        "regime_df": regime_results["regime_results"],
        "regime_summary": regime_results["summary"],
        "alert_df": alert_results["live_alert_results"],
        "alert_summary": alert_results["summary"],
    }
