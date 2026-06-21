from __future__ import annotations

from collections.abc import Callable

import pandas as pd


SCENARIOS = (
    "BASELINE",
    "MILD RECESSION",
    "SEVERE RECESSION",
    "FINANCIAL CRISIS",
)


def build_stress_view_model(
    portfolio: pd.DataFrame,
    scenario: str,
    *,
    run_stress: Callable,
    run_macro: Callable,
    run_var: Callable,
    run_cvar: Callable,
    run_capital: Callable,
) -> dict:
    stress_results = run_stress(portfolio, scenario)
    stress_summary = stress_results["summary"]
    macro_results = run_macro(portfolio, scenario)
    macro_summary = macro_results["summary"]
    var_results = run_var(portfolio)
    cvar_results = run_cvar(portfolio)

    capital_results = run_capital(
        baseline_capital=750_000_000,
        risk_weighted_assets=5_000_000_000,
        stressed_losses=stress_summary["stressed_portfolio_loss"],
    )

    comparison_rows = []
    for stress_scenario in SCENARIOS:
        scenario_summary = run_stress(portfolio, stress_scenario)["summary"]
        comparison_rows.append(
            {
                "Scenario": stress_scenario,
                "Stressed Loss": round(
                    scenario_summary["stressed_portfolio_loss"],
                    2,
                ),
                "Average PD": round(
                    scenario_summary["average_stressed_pd"] * 100,
                    2,
                ),
                "Deterioration %": round(
                    scenario_summary["portfolio_loss_deterioration_pct"],
                    2,
                ),
                "Stress Grade": scenario_summary["stress_grade"],
                "Concentration %": round(
                    scenario_summary["stress_concentration"],
                    2,
                ),
            }
        )

    comparison_df = pd.DataFrame(comparison_rows)
    worst_case = comparison_df.loc[
        comparison_df["Stressed Loss"].idxmax()
    ]

    deterioration_pct = stress_summary["portfolio_loss_deterioration_pct"]
    stress_concentration = stress_summary["stress_concentration"]
    resilience_score = capital_results["capital_resilience_score"]
    enterprise_risk_score = min(
        round(
            (deterioration_pct * 0.35)
            + (stress_concentration * 0.20)
            + (macro_summary["systemic_stress_score"] * 0.25)
            + ((100 - resilience_score) * 0.20),
            2,
        ),
        100,
    )

    if enterprise_risk_score >= 80:
        enterprise_status = "CRITICAL RISK"
    elif enterprise_risk_score >= 60:
        enterprise_status = "HIGH RISK"
    elif enterprise_risk_score >= 40:
        enterprise_status = "MODERATE RISK"
    else:
        enterprise_status = "LOW RISK"

    recommendations = []
    if deterioration_pct > 100:
        recommendations.append("Increase credit provisioning reserves.")
    if stress_concentration > 25:
        recommendations.append("Reduce portfolio concentration risk.")
    if capital_results["stressed_capital_ratio"] < 12:
        recommendations.append("Review capital adequacy planning.")
    if enterprise_risk_score > 60:
        recommendations.append("Escalate portfolio review to CRO.")
    if not recommendations:
        recommendations.append(
            "Portfolio remains resilient under current scenario."
        )

    return {
        "stressed_df": stress_results["portfolio_results"],
        "stress_summary": stress_summary,
        "macro_df": macro_results["portfolio_results"],
        "macro_summary": macro_summary,
        "var_results": var_results,
        "cvar_results": cvar_results,
        "capital_results": capital_results,
        "comparison_df": comparison_df,
        "worst_case": worst_case,
        "baseline_loss": stress_summary["baseline_portfolio_loss"],
        "stressed_loss": stress_summary["stressed_portfolio_loss"],
        "deterioration_pct": deterioration_pct,
        "avg_stressed_pd": stress_summary["average_stressed_pd"],
        "stress_grade": stress_summary["stress_grade"],
        "stress_concentration": stress_concentration,
        "resilience_score": resilience_score,
        "enterprise_risk_score": enterprise_risk_score,
        "enterprise_status": enterprise_status,
        "executive_recommendations": recommendations,
    }
