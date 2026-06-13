# =============================================================================
# KRONOS — ENTERPRISE RESERVE SIMULATOR
# File: src/provisioning/reserve_simulator.py
# =============================================================================

import pandas as pd
import numpy as np

from src.provisioning.provisioning_engine import calculate_ecl
from src.shared.config import RESERVE_STRESS_SCENARIOS

# =============================================================================
# MACRO STRESS SCENARIOS
# =============================================================================

STRESS_SCENARIOS = RESERVE_STRESS_SCENARIOS


def normalize_ifrs_stage(stage):
    """
    Normalize legacy and current IFRS9 stage labels.
    """

    stage_text = str(stage).replace("_", " ").upper()

    if stage_text in {"STAGE 1", "STAGE 2", "STAGE 3"}:

        return stage_text

    return "STAGE 1"


def row_ifrs_stage(row):
    """
    Read IFRS9 stage from reserve-simulation input rows.
    """

    return normalize_ifrs_stage(
        row.get(
            "current_stage",
            row.get(
                "ifrs_stage",
                "STAGE 1"
            )
        )
    )

# =============================================================================
# STRESSED ECL
# =============================================================================

def stressed_ecl(
    pd_score,
    lgd,
    ead,
    scenario,
    stage="STAGE 1"
):
    """
    Calculate stressed Expected Credit Loss.
    """

    stress = STRESS_SCENARIOS.get(
        scenario,
        STRESS_SCENARIOS["BASELINE"]
    )

    stressed_pd = (
        pd_score
        * stress["pd_multiplier"]
    )

    stressed_lgd = (
        lgd
        * stress["lgd_multiplier"]
    )

    stressed_ead = (
        ead
        * stress["ead_multiplier"]
    )

    stressed_pd = min(
        stressed_pd,
        1.0
    )

    stressed_lgd = min(
        stressed_lgd,
        1.0
    )

    ecl = calculate_ecl(
        stressed_pd,
        stressed_lgd,
        stressed_ead,
        normalize_ifrs_stage(stage)
    )

    return round(
        float(ecl),
        2
    )

# =============================================================================
# RESERVE INFLATION
# =============================================================================

def reserve_inflation(
    baseline_ecl,
    stressed_ecl_value
):
    """
    Calculate reserve inflation percentage.
    """

    if baseline_ecl <= 0:

        return 0

    inflation = (
        (
            stressed_ecl_value
            - baseline_ecl
        )
        / baseline_ecl
    ) * 100

    return round(
        inflation,
        2
    )

# =============================================================================
# RESERVE ADEQUACY
# =============================================================================

def reserve_adequacy(
    reserve_inflation_pct
):
    """
    Determine reserve adequacy pressure.
    """

    if reserve_inflation_pct < 20:

        return "ADEQUATE RESERVES"

    elif reserve_inflation_pct < 60:

        return "MODERATE RESERVE PRESSURE"

    elif reserve_inflation_pct < 120:

        return "HIGH RESERVE PRESSURE"

    return "CRITICAL CAPITAL PRESSURE"

# =============================================================================
# CAPITAL IMPACT
# =============================================================================

def capital_impact(
    reserve_inflation_pct
):
    """
    Determine capital stress impact.
    """

    if reserve_inflation_pct < 20:

        return "LOW CAPITAL IMPACT"

    elif reserve_inflation_pct < 60:

        return "MODERATE CAPITAL IMPACT"

    elif reserve_inflation_pct < 120:

        return "SEVERE CAPITAL IMPACT"

    return "SYSTEMIC CAPITAL STRESS"

# =============================================================================
# SCENARIO RISK GRADE
# =============================================================================

def scenario_risk_grade(
    reserve_growth
):
    """
    Portfolio reserve stress grade.
    """

    if reserve_growth < 25:

        return "A"

    elif reserve_growth < 75:

        return "B"

    elif reserve_growth < 150:

        return "C"

    return "D"

# =============================================================================
# IMPAIRMENT SHOCK LEVEL
# =============================================================================

def impairment_shock_level(
    stressed_ecl_value
):
    """
    Classify impairment severity.
    """

    if stressed_ecl_value < 5000:

        return "LOW IMPAIRMENT SHOCK"

    elif stressed_ecl_value < 20000:

        return "MODERATE IMPAIRMENT SHOCK"

    elif stressed_ecl_value < 50000:

        return "HIGH IMPAIRMENT SHOCK"

    return "SEVERE IMPAIRMENT SHOCK"

# =============================================================================
# EXECUTIVE STRESS NARRATIVE
# =============================================================================

def generate_stress_narrative(
    scenario,
    reserve_pressure,
    capital_stress
):
    """
    Generate executive stress commentary.
    """

    narrative = (
        f"Scenario '{scenario}' indicates "
        f"{reserve_pressure.lower()} with "
        f"{capital_stress.lower()} across "
        "the portfolio reserve structure."
    )

    return narrative

# =============================================================================
# PORTFOLIO STRESS NARRATIVE
# =============================================================================

def portfolio_stress_narrative(
    scenario,
    reserve_growth,
    grade
):
    """
    Executive stress summary.
    """

    return (
        f"Under the {scenario} scenario, "
        f"portfolio reserves increase by "
        f"{reserve_growth}% resulting in "
        f"a stress grade of {grade}."
    )

# =============================================================================
# RUN STRESS SCENARIO
# =============================================================================

def run_reserve_stress_test(
    portfolio_df,
    scenario
):
    """
    Run enterprise reserve stress simulation.
    """

    print("\n" + "=" * 80)
    print(f"[KRONOS] RUNNING STRESS SCENARIO: {scenario}")
    print("=" * 80)

    portfolio_df = portfolio_df.copy()

    # -------------------------------------------------------------------------
    # BASELINE ECL
    # -------------------------------------------------------------------------

    portfolio_df["baseline_ecl"] = (
        portfolio_df.apply(
            lambda row:
            calculate_ecl(
                row["pd_score"],
                row["lgd"],
                row["ead"],
                row_ifrs_stage(row),
            ),
            axis=1
        )
    )

    # -------------------------------------------------------------------------
    # STRESSED ECL
    # -------------------------------------------------------------------------

    portfolio_df["stressed_ecl"] = (
        portfolio_df.apply(
            lambda row:
            stressed_ecl(
                row["pd_score"],
                row["lgd"],
                row["ead"],
                scenario,
                row_ifrs_stage(row),
            ),
            axis=1
        )
    )

    # -------------------------------------------------------------------------
    # RESERVE INFLATION
    # -------------------------------------------------------------------------

    portfolio_df["reserve_inflation_pct"] = (
        portfolio_df.apply(
            lambda row:
            reserve_inflation(
                row["baseline_ecl"],
                row["stressed_ecl"],
            ),
            axis=1
        )
    )

    # -------------------------------------------------------------------------
    # RESERVE PRESSURE
    # -------------------------------------------------------------------------

    portfolio_df["reserve_pressure"] = (
        portfolio_df["reserve_inflation_pct"]
        .apply(reserve_adequacy)
    )

    # -------------------------------------------------------------------------
    # CAPITAL IMPACT
    # -------------------------------------------------------------------------

    portfolio_df["capital_impact"] = (
        portfolio_df["reserve_inflation_pct"]
        .apply(capital_impact)
    )

    # -------------------------------------------------------------------------
    # STRESS GRADE
    # -------------------------------------------------------------------------

    portfolio_df["stress_grade"] = (
        portfolio_df["reserve_inflation_pct"]
        .apply(
            scenario_risk_grade
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
    )

    # -------------------------------------------------------------------------
    # IMPAIRMENT SHOCK
    # -------------------------------------------------------------------------

    portfolio_df["impairment_shock"] = (
        portfolio_df["stressed_ecl"]
        .apply(impairment_shock_level)
    )

    # -------------------------------------------------------------------------
    # EXECUTIVE NARRATIVE
    # -------------------------------------------------------------------------

    portfolio_df["executive_narrative"] = (
        portfolio_df.apply(
            lambda row:
            generate_stress_narrative(
                scenario,
                row["reserve_pressure"],
                row["capital_impact"],
            ),
            axis=1
        )
    )

    return portfolio_df

# =============================================================================
# PORTFOLIO STRESS SUMMARY
# =============================================================================

def stress_summary(
    stressed_df,
    scenario
):
    """
    Generate enterprise stress summary.
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

    reserve_growth = reserve_inflation(
        baseline_total,
        stressed_total
    )

    capital_stress_grade = scenario_risk_grade(
        reserve_growth
    )

    if reserve_growth >= 150:

        capital_warning = "CRITICAL"

    elif reserve_growth >= 75:

        capital_warning = "ELEVATED"

    else:

        capital_warning = "NORMAL"

    narrative = portfolio_stress_narrative(
        scenario,
        reserve_growth,
        capital_stress_grade
    )

    largest_stressed_exposure = round(
        float(
            stressed_df[
                "stressed_ecl"
            ].max()
        ),
        2
    )

    if stressed_total == 0:

        reserve_concentration = 0

    else:

        reserve_concentration = round(
            (
                largest_stressed_exposure
                / stressed_total
            ) * 100,
            2
        )

    if reserve_concentration >= 50:

        concentration_risk = "HIGH"

    elif reserve_concentration >= 25:

        concentration_risk = "MODERATE"

    else:

        concentration_risk = "LOW"

    summary = {

        "scenario":
            scenario,

        "baseline_portfolio_ecl":
            baseline_total,

        "stressed_portfolio_ecl":
            stressed_total,

        "portfolio_reserve_growth_pct":
            reserve_growth,

        "average_reserve_inflation_pct":
            round(
                float(
                    stressed_df[
                        "reserve_inflation_pct"
                    ].mean()
                ),
                2
            ),

        "max_stressed_ecl":
            round(
                float(
                    stressed_df[
                        "stressed_ecl"
                    ].max()
                ),
                2
            ),

        "capital_stress_grade":
            capital_stress_grade,

        "capital_warning":
            capital_warning,

        "executive_narrative":
            narrative,

        "largest_stressed_exposure":
            largest_stressed_exposure,

        "reserve_concentration":
            reserve_concentration,

        "concentration_risk":
            concentration_risk,

    }

    return summary

# =============================================================================
# TOP STRESS EXPOSURES
# =============================================================================

def top_stress_exposures(
    stressed_df,
    top_n=10
):
    """
    Extract highest stressed reserve exposures.
    """

    top_df = stressed_df.sort_values(
        by="stressed_ecl",
        ascending=False
    )

    return top_df.head(top_n)[
        [
            "borrower_id",
            "stress_rank",
            "baseline_ecl",
            "stressed_ecl",
            "reserve_inflation_pct",
            "reserve_pressure",
            "capital_impact",
            "impairment_shock",
        ]
    ]

# =============================================================================
# FULL RESERVE SIMULATION PIPELINE
# =============================================================================

def run_reserve_simulation(
    portfolio_df,
    scenario="SEVERE RECESSION"
):
    """
    Run enterprise reserve stress simulation.
    """

    stressed_df = run_reserve_stress_test(
        portfolio_df,
        scenario
    )

    summary = stress_summary(
        stressed_df,
        scenario
    )

    top_exposures = top_stress_exposures(
        stressed_df
    )

    stage_impact = stage_stress_impact(
        stressed_df,
        scenario
    )

    # -------------------------------------------------------------------------
    # REPORTING
    # -------------------------------------------------------------------------

    print("\n[KRONOS] RESERVE STRESS SUMMARY\n")

    for key, value in summary.items():

        print(f"{key}: {value}")

    print("\n" + "-" * 80)

    print("\nTOP STRESSED EXPOSURES\n")

    print(top_exposures)

    print("\n" + "-" * 80)

    print("\nPORTFOLIO STRESS DETAILS\n")

    print(
        stressed_df[
            [
                "borrower_id",
                "baseline_ecl",
                "stressed_ecl",
                "reserve_inflation_pct",
                "reserve_pressure",
                "capital_impact",
                "stress_grade",
            ]
        ]
    )

    print("=" * 80)

    if stage_impact is not None:

        print("\n" + "-" * 80)

        print("\nSTAGE LEVEL STRESS IMPACT\n")

        print(stage_impact)

    return {
        "portfolio_results":
            stressed_df,

        "summary":
            summary,

        "top_stress_exposures":
            top_exposures,

        "stage_stress_impact":
            stage_impact,
    }

# =============================================================================
# STAGE-LEVEL STRESS IMPACT
# =============================================================================

def stage_stress_impact(
    stressed_df,
    scenario
):
    """
    Report stressed ECL broken down by IFRS 9 stage.
    Requires 'current_stage' column in portfolio.
    """

    if "current_stage" not in stressed_df.columns:

        return None

    stage_summary = (
        stressed_df
        .groupby("current_stage")
        .agg(
            stage_baseline_ecl=(
                "baseline_ecl",
                "sum"
            ),
            stage_stressed_ecl=(
                "stressed_ecl",
                "sum"
            ),
            borrower_count=(
                "borrower_id",
                "count"
            ),
        )
        .reset_index()
    )

    stage_summary["stage_reserve_inflation_pct"] = (
        stage_summary.apply(
            lambda row:
            reserve_inflation(
                row["stage_baseline_ecl"],
                row["stage_stressed_ecl"],
            ),
            axis=1
        )
    )

    stage_summary["scenario"] = scenario

    stage_summary = stage_summary.rename(
        columns={
            "current_stage": "stage"
        }
    )

    stage_summary = stage_summary[
        [
            "scenario",
            "stage",
            "borrower_count",
            "stage_baseline_ecl",
            "stage_stressed_ecl",
            "stage_reserve_inflation_pct",
        ]
    ].sort_values("stage")

    return stage_summary

# =============================================================================
# SCENARIO COMPARISON TABLE
# =============================================================================

def run_all_scenarios(
    portfolio_df
):
    """
    Run all macro stress scenarios and produce
    a side-by-side comparison dataframe.
    """

    print("\n" + "=" * 80)
    print("[KRONOS] RUNNING ALL SCENARIO COMPARISON")
    print("=" * 80)

    comparison_rows = []

    for scenario in STRESS_SCENARIOS.keys():

        stressed_df = run_reserve_stress_test(
            portfolio_df,
            scenario
        )

        summary = stress_summary(
            stressed_df,
            scenario
        )

        comparison_rows.append(summary)

    comparison_df = pd.DataFrame(comparison_rows)

    display_cols = [
        "scenario",
        "baseline_portfolio_ecl",
        "stressed_portfolio_ecl",
        "portfolio_reserve_growth_pct",
        "capital_stress_grade",
        "capital_warning",
        "concentration_risk",
        "largest_stressed_exposure",
    ]

    print("\n[KRONOS] SCENARIO COMPARISON TABLE\n")

    print(comparison_df[display_cols])

    scenario_worst_case = comparison_df.loc[
        comparison_df[
            "stressed_portfolio_ecl"
        ].idxmax()
    ]

    print("\nWORST CASE SCENARIO\n")

    print(scenario_worst_case)

    print("\n" + "=" * 80)

    return comparison_df

# =============================================================================
# SAMPLE PORTFOLIO
# =============================================================================

SAMPLE_PORTFOLIO = pd.DataFrame([

    {
        "borrower_id": "B1001",
        "pd_score": 0.05,
        "lgd": 0.25,
        "ead": 14000,
        "current_stage": "STAGE 1",
    },

    {
        "borrower_id": "B1002",
        "pd_score": 0.28,
        "lgd": 0.61,
        "ead": 46000,
        "current_stage": "STAGE 2",
    },

    {
        "borrower_id": "B1003",
        "pd_score": 0.66,
        "lgd": 0.82,
        "ead": 92000,
        "current_stage": "STAGE 3",
    },

    {
        "borrower_id": "B1004",
        "pd_score": 0.14,
        "lgd": 0.37,
        "ead": 28000,
        "current_stage": "STAGE 2",
    },

])

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":

    run_reserve_simulation(
        SAMPLE_PORTFOLIO,
        scenario="SEVERE RECESSION"
    )

    run_all_scenarios(
        SAMPLE_PORTFOLIO
    )

    print("\n[KRONOS] RESERVE SIMULATION COMPLETED")

# =============================================================================
# END OF FILE
# =============================================================================
