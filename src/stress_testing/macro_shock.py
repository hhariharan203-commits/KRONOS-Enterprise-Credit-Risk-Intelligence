# =============================================================================
# KRONOS — MACROECONOMIC SHOCK ENGINE
# File: src/stress_testing/macro_shock.py
# =============================================================================

import pandas as pd
import numpy as np

from src.shared.config import MACRO_STRESS_SCENARIOS

# =============================================================================
# MACRO SHOCK DEFINITIONS
# =============================================================================

MACRO_SCENARIOS = MACRO_STRESS_SCENARIOS

# =============================================================================
# GDP SHOCK IMPACT
# =============================================================================

def gdp_transmission(
    pd_score,
    gdp_shock
):
    """
    Model GDP deterioration impact on credit risk.
    """

    impact_multiplier = (
        1 + (abs(gdp_shock) * 0.08)
    )

    stressed_pd = (
        pd_score * impact_multiplier
    )

    return min(
        round(stressed_pd, 4),
        1.0
    )

# =============================================================================
# UNEMPLOYMENT SHOCK IMPACT
# =============================================================================

def unemployment_transmission(
    pd_score,
    unemployment_shock
):
    """
    Model unemployment impact on borrower default risk.
    """

    unemployment_multiplier = (
        1 + (unemployment_shock * 0.10)
    )

    stressed_pd = (
        pd_score * unemployment_multiplier
    )

    return min(
        round(stressed_pd, 4),
        1.0
    )

# =============================================================================
# INFLATION SHOCK IMPACT
# =============================================================================

def inflation_transmission(
    lgd,
    inflation_shock
):
    """
    Model inflation impact on recovery deterioration.
    """

    inflation_multiplier = (
        1 + (inflation_shock * 0.06)
    )

    stressed_lgd = (
        lgd * inflation_multiplier
    )

    return min(
        round(stressed_lgd, 4),
        1.0
    )

# =============================================================================
# INTEREST RATE SHOCK IMPACT
# =============================================================================

def interest_rate_transmission(
    ead,
    interest_rate_shock
):
    """
    Model interest-rate impact on exposure growth.
    """

    exposure_multiplier = (
        1 + (interest_rate_shock * 0.05)
    )

    stressed_ead = (
        ead * exposure_multiplier
    )

    return round(
        stressed_ead,
        2
    )

# =============================================================================
# MARKET VOLATILITY IMPACT
# =============================================================================

def market_volatility_transmission(
    pd_score,
    volatility_shock
):
    """
    Model market volatility contagion impact.
    """

    volatility_multiplier = (
        1 + (volatility_shock * 0.015)
    )

    stressed_pd = (
        pd_score * volatility_multiplier
    )

    return min(
        round(stressed_pd, 4),
        1.0
    )

# =============================================================================
# SYSTEMIC STRESS SCORE
# =============================================================================

def systemic_stress_score(
    scenario_data
):
    """
    Calculate systemic macroeconomic stress intensity.
    """

    score = (

        abs(scenario_data["gdp_shock"]) * 6
        + scenario_data["unemployment_shock"] * 7
        + scenario_data["inflation_shock"] * 5
        + scenario_data["interest_rate_shock"] * 5
        + scenario_data["market_volatility_shock"] * 0.8
    )

    return min(
        round(score, 2),
        100
    )

# =============================================================================
# REGIME CLASSIFICATION
# =============================================================================

def regime_classification(
    stress_score
):
    """
    Determine macroeconomic regime severity.
    """

    if stress_score < 20:

        return "STABLE REGIME"

    elif stress_score < 45:

        return "ELEVATED RISK REGIME"

    elif stress_score < 75:

        return "HIGH STRESS REGIME"

    return "SYSTEMIC CRISIS REGIME"

# =============================================================================
# PORTFOLIO SENSITIVITY
# =============================================================================

def portfolio_sensitivity(
    baseline_ecl,
    stressed_ecl
):
    """
    Measure portfolio macro sensitivity.
    """

    if baseline_ecl <= 0:

        return 0

    sensitivity = (
        (
            stressed_ecl
            - baseline_ecl
        )
        / baseline_ecl
    ) * 100

    return round(
        sensitivity,
        2
    )

# =============================================================================
# EXECUTIVE MACRO NARRATIVE
# =============================================================================

def generate_macro_narrative(
    scenario,
    regime,
    sensitivity
):
    """
    Generate executive macroeconomic commentary.
    """

    narrative = (
        f"Scenario '{scenario}' produced "
        f"{regime.lower()} conditions with "
        f"{sensitivity}% portfolio sensitivity "
        "to macroeconomic deterioration."
    )

    return narrative

# =============================================================================
# RUN MACRO SHOCK ANALYSIS
# =============================================================================

def run_macro_shock_analysis(
    portfolio_df,
    scenario="SEVERE RECESSION"
):
    """
    Run enterprise macro shock transmission analysis.
    """

    print("\n" + "=" * 80)
    print(f"[KRONOS] RUNNING MACRO SHOCK: {scenario}")
    print("=" * 80)

    scenario_data = MACRO_SCENARIOS.get(
        scenario,
        MACRO_SCENARIOS["BASELINE"]
    )

    portfolio_df = portfolio_df.copy()

    # -------------------------------------------------------------------------
    # BASELINE ECL
    # -------------------------------------------------------------------------

    portfolio_df["baseline_ecl"] = (

        portfolio_df["pd_score"]
        * portfolio_df["lgd"]
        * portfolio_df["ead"]
    )

    # -------------------------------------------------------------------------
    # GDP TRANSMISSION
    # -------------------------------------------------------------------------

    portfolio_df["gdp_stressed_pd"] = (
        portfolio_df["pd_score"]
        .apply(
            lambda x:
            gdp_transmission(
                x,
                scenario_data["gdp_shock"]
            )
        )
    )

    # -------------------------------------------------------------------------
    # UNEMPLOYMENT TRANSMISSION
    # -------------------------------------------------------------------------

    portfolio_df["unemployment_stressed_pd"] = (
        portfolio_df["gdp_stressed_pd"]
        .apply(
            lambda x:
            unemployment_transmission(
                x,
                scenario_data["unemployment_shock"]
            )
        )
    )

    # -------------------------------------------------------------------------
    # VOLATILITY TRANSMISSION
    # -------------------------------------------------------------------------

    portfolio_df["final_stressed_pd"] = (
        portfolio_df["unemployment_stressed_pd"]
        .apply(
            lambda x:
            market_volatility_transmission(
                x,
                scenario_data[
                    "market_volatility_shock"
                ]
            )
        )
    )

    # -------------------------------------------------------------------------
    # LGD TRANSMISSION
    # -------------------------------------------------------------------------

    portfolio_df["stressed_lgd"] = (
        portfolio_df["lgd"]
        .apply(
            lambda x:
            inflation_transmission(
                x,
                scenario_data["inflation_shock"]
            )
        )
    )

    # -------------------------------------------------------------------------
    # EAD TRANSMISSION
    # -------------------------------------------------------------------------

    portfolio_df["stressed_ead"] = (
        portfolio_df["ead"]
        .apply(
            lambda x:
            interest_rate_transmission(
                x,
                scenario_data[
                    "interest_rate_shock"
                ]
            )
        )
    )

    # -------------------------------------------------------------------------
    # STRESSED ECL
    # -------------------------------------------------------------------------

    portfolio_df["stressed_ecl"] = (

        portfolio_df["final_stressed_pd"]
        * portfolio_df["stressed_lgd"]
        * portfolio_df["stressed_ead"]
    )

    # -------------------------------------------------------------------------
    # PORTFOLIO SENSITIVITY
    # -------------------------------------------------------------------------

    portfolio_df["portfolio_sensitivity_pct"] = (
        portfolio_df.apply(
            lambda row:
            portfolio_sensitivity(
                row["baseline_ecl"],
                row["stressed_ecl"],
            ),
            axis=1
        )
    )

    # -------------------------------------------------------------------------
    # STRESS RANK
    # -------------------------------------------------------------------------

    portfolio_df["stress_rank"] = (
        portfolio_df["stressed_ecl"]
        .rank(
            ascending=False,
            method="dense"
        )
        .astype(int)
    )

    # -------------------------------------------------------------------------
    # SYSTEMIC STRESS
    # -------------------------------------------------------------------------

    stress_score = systemic_stress_score(
        scenario_data
    )

    regime = regime_classification(
        stress_score
    )

    portfolio_df["macro_regime"] = regime

    portfolio_df["systemic_stress_score"] = (
        stress_score
    )

    # -------------------------------------------------------------------------
    # EXECUTIVE NARRATIVE
    # -------------------------------------------------------------------------

    portfolio_df["executive_narrative"] = (
        portfolio_df["portfolio_sensitivity_pct"]
        .apply(
            lambda x:
            generate_macro_narrative(
                scenario,
                regime,
                x
            )
        )
    )

    return (
        portfolio_df,
        stress_score,
        regime
    )

# =============================================================================
# PORTFOLIO MACRO SUMMARY
# =============================================================================

def macro_summary(
    stressed_df,
    scenario,
    stress_score,
    regime
):
    """
    Generate macroeconomic portfolio summary.
    """

    baseline_total = round(
        float(
            stressed_df["baseline_ecl"].sum()
        ),
        2
    )

    stressed_total = round(
        float(
            stressed_df["stressed_ecl"].sum()
        ),
        2
    )

    largest_stressed_exposure = round(
        float(
            stressed_df["stressed_ecl"].max()
        ),
        2
    )

    stress_concentration = round(
        (
            largest_stressed_exposure
            / stressed_total
        ) * 100,
        2
    )

    portfolio_sensitivity_pct = (
        portfolio_sensitivity(
            baseline_total,
            stressed_total
        )
    )

    summary = {

        "scenario":
            scenario,

        "macro_regime":
            regime,

        "systemic_stress_score":
            stress_score,

        "baseline_portfolio_ecl":
            baseline_total,

        "stressed_portfolio_ecl":
            stressed_total,

        "portfolio_sensitivity_pct":
            portfolio_sensitivity_pct,

        "average_stressed_pd":
            round(
                float(
                    stressed_df[
                        "final_stressed_pd"
                    ].mean()
                ),
                4
            ),

        "largest_stressed_exposure":
            largest_stressed_exposure,

        "stress_concentration":
            stress_concentration,
    }

    return summary

# =============================================================================
# TOP MACRO SENSITIVE ACCOUNTS
# =============================================================================

def top_macro_sensitive_accounts(
    stressed_df,
    top_n=10
):
    """
    Extract most macro-sensitive borrowers.
    """

    top_df = stressed_df.sort_values(
        by="portfolio_sensitivity_pct",
        ascending=False
    )

    return top_df.head(top_n)[
        [
            "borrower_id",
            "stress_rank",
            "baseline_ecl",
            "stressed_ecl",
            "portfolio_sensitivity_pct",
            "macro_regime",
        ]
    ]

# =============================================================================
# FULL MACRO SHOCK PIPELINE
# =============================================================================

def run_macro_pipeline(
    portfolio_df,
    scenario="SEVERE RECESSION"
):
    """
    Run enterprise macro shock workflow.
    """

    (
        stressed_df,
        stress_score,
        regime
    ) = run_macro_shock_analysis(
        portfolio_df,
        scenario
    )

    summary = macro_summary(
        stressed_df,
        scenario,
        stress_score,
        regime
    )

    top_accounts = top_macro_sensitive_accounts(
        stressed_df
    )

    # -------------------------------------------------------------------------
    # REPORTING
    # -------------------------------------------------------------------------

    print("\n[KRONOS] MACRO SHOCK SUMMARY\n")

    for key, value in summary.items():

        print(f"{key}: {value}")

    print("\n" + "-" * 80)

    print("\nTOP MACRO-SENSITIVE ACCOUNTS\n")

    print(top_accounts)

    print("\n" + "-" * 80)

    print("\nMACRO SHOCK DETAILS\n")

    print(
        stressed_df[
            [
                "borrower_id",
                "baseline_ecl",
                "stressed_ecl",
                "portfolio_sensitivity_pct",
                "macro_regime",
                "systemic_stress_score",
            ]
        ]
    )

    print("=" * 80)

    return {
        "portfolio_results":
            stressed_df,

        "summary":
            summary,

        "top_macro_accounts":
            top_accounts,
    }

# =============================================================================
# SAMPLE PORTFOLIO
# =============================================================================

SAMPLE_PORTFOLIO = pd.DataFrame([

    {
        "borrower_id": "B1001",
        "pd_score": 0.05,
        "lgd": 0.25,
        "ead": 16000,
    },

    {
        "borrower_id": "B1002",
        "pd_score": 0.31,
        "lgd": 0.64,
        "ead": 52000,
    },

    {
        "borrower_id": "B1003",
        "pd_score": 0.67,
        "lgd": 0.84,
        "ead": 98000,
    },

    {
        "borrower_id": "B1004",
        "pd_score": 0.15,
        "lgd": 0.38,
        "ead": 32000,
    },

])

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":

    run_macro_pipeline(
        SAMPLE_PORTFOLIO,
        scenario="SEVERE RECESSION"
    )

    print("\n[KRONOS] MACRO SHOCK ENGINE COMPLETED")

# =============================================================================
# END OF FILE
# =============================================================================
