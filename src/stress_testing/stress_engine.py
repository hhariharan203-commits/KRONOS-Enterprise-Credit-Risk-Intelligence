# # =============================================================================
# KRONOS — ENTERPRISE STRESS TESTING ENGINE
# File: src/stress_testing/stress_engine.py
# # =============================================================================

import pandas as pd
import numpy as np

from src.shared.config import CREDIT_STRESS_SCENARIOS

# # =============================================================================

# STRESS SCENARIOS

# # =============================================================================

STRESS_SCENARIOS = CREDIT_STRESS_SCENARIOS

# # =============================================================================
# STRESSED CREDIT PARAMETERS
# # =============================================================================

def stressed_credit_metrics(
pd_score,
lgd,
ead,
scenario
):
    """
    Apply macro stress scenario to borrower metrics.
    """

    stress = STRESS_SCENARIOS.get(  
        scenario,  
        STRESS_SCENARIOS["BASELINE"]  
    )  

    stressed_pd = min(  
        pd_score * stress["pd_multiplier"],  
        1.0  
    )  

    stressed_lgd = min(  
        lgd * stress["lgd_multiplier"],  
        1.0  
    )  

    stressed_ead = (  
        ead * stress["ead_multiplier"]  
    )  

    return (  
        stressed_pd,  
        stressed_lgd,  
        stressed_ead  
    )

# # =============================================================================

# STRESSED ECL

# # =============================================================================

def calculate_stressed_ecl(
stressed_pd,
stressed_lgd,
stressed_ead
):
    """
    Calculate stressed Expected Credit Loss.
    """

    stressed_ecl = (  
        stressed_pd  
        * stressed_lgd  
        * stressed_ead  
    )  

    return round(  
        float(stressed_ecl),  
        2  
    )

# # =============================================================================
# PORTFOLIO LOSS IMPACT

# # =============================================================================

def portfolio_loss_impact(
baseline_ecl,
stressed_ecl
):
    """
    Calculate stress portfolio deterioration.
    """

    if baseline_ecl <= 0:  

        return 0  

    deterioration = (  
        (  
            stressed_ecl  
            - baseline_ecl  
        )  
        / baseline_ecl  
    ) * 100  

    return round(  
        deterioration,  
        2  
    )

# # =============================================================================

# STRESS SEVERITY

# # =============================================================================

def stress_severity(
loss_impact_pct
):
    """
    Classify portfolio stress severity.
    """

    if loss_impact_pct < 20:  

        return "LOW STRESS"  

    elif loss_impact_pct < 60:  

        return "MODERATE STRESS"  

    elif loss_impact_pct < 120:  

        return "HIGH STRESS"  

    return "EXTREME STRESS"

# # =============================================================================

# CAPITAL PRESSURE

# # =============================================================================

def capital_pressure(
loss_impact_pct
):
    """
    Determine capital deterioration intensity.
    """

    if loss_impact_pct < 20:  

        return "LIMITED CAPITAL IMPACT"  

    elif loss_impact_pct < 60:  

        return "MODERATE CAPITAL PRESSURE"  

    elif loss_impact_pct < 120:  

        return "SEVERE CAPITAL PRESSURE"  

    return "CRITICAL CAPITAL DETERIORATION"

# # =============================================================================

# STRESS WATCHLIST

# # =============================================================================

def stress_watchlist(
stressed_pd
):
    """
    Determine borrower stress escalation.
    """

    if stressed_pd < 0.10:  

        return "LOW RISK"  

    elif stressed_pd < 0.25:  

        return "MODERATE RISK"  

    elif stressed_pd < 0.50:  

        return "HIGH RISK"  

    return "CRITICAL DISTRESS"

# # =============================================================================

# EXECUTIVE STRESS NARRATIVE

# =============================================================================

def generate_stress_narrative(
scenario,
severity,
capital_status
):
    """
    Generate executive stress commentary.
    """

    narrative = (  
        f"Scenario '{scenario}' indicates "  
        f"{severity.lower()} with "  
        f"{capital_status.lower()} across "  
        "the enterprise portfolio."  
    )  

    return narrative

# =============================================================================

# STRESS GRADE

# =============================================================================

def portfolio_stress_grade(
    deterioration_pct
):
    if deterioration_pct < 25:
        return "A"

    elif deterioration_pct < 75:
        return "B"

    elif deterioration_pct < 150:
        return "C"

    return "D"

# =============================================================================

# PORTFOLIO NARRATIVE

# =============================================================================

def portfolio_stress_narrative(
    scenario,
    deterioration_pct,
    stress_grade
):
    return (
        f"Under {scenario}, portfolio loss "
        f"deteriorates by "
        f"{deterioration_pct}% "
        f"resulting in stress grade "
        f"{stress_grade}."
    )

# =============================================================================

# RUN STRESS TEST

# =============================================================================

def run_stress_test(
portfolio_df,
scenario="SEVERE RECESSION"
):
    """
    Run enterprise macro stress simulation.
    """

    print("\n" + "=" * 80)  
    print(f"[KRONOS] RUNNING STRESS TEST: {scenario}")  
    print("=" * 80)  

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
    # STRESSED PARAMETERS  
    # -------------------------------------------------------------------------  

    stressed_results = portfolio_df.apply(  
        lambda row:  
        stressed_credit_metrics(  
            row["pd_score"],  
            row["lgd"],  
            row["ead"],  
            scenario,  
        ),  
        axis=1  
    )  

    portfolio_df[  
        [  
            "stressed_pd",  
            "stressed_lgd",  
            "stressed_ead",  
        ]  
    ] = pd.DataFrame(  
        stressed_results.tolist(),  
        index=portfolio_df.index  
    )  

    # -------------------------------------------------------------------------  
    # STRESSED ECL  
    # -------------------------------------------------------------------------  

    portfolio_df["stressed_ecl"] = (  
        portfolio_df.apply(  
            lambda row:  
            calculate_stressed_ecl(  
                row["stressed_pd"],  
                row["stressed_lgd"],  
                row["stressed_ead"],  
            ),  
            axis=1  
        )  
    )  

    # -------------------------------------------------------------------------  
    # LOSS IMPACT  
    # -------------------------------------------------------------------------  

    portfolio_df["loss_impact_pct"] = (  
        portfolio_df.apply(  
            lambda row:  
            portfolio_loss_impact(  
                row["baseline_ecl"],  
                row["stressed_ecl"],  
            ),  
            axis=1  
        )  
    )  

    # -------------------------------------------------------------------------  
    # STRESS CLASSIFICATIONS  
    # -------------------------------------------------------------------------  

    portfolio_df["stress_severity"] = (  
        portfolio_df["loss_impact_pct"]  
        .apply(stress_severity)  
    )  

    portfolio_df["capital_pressure"] = (  
        portfolio_df["loss_impact_pct"]  
        .apply(capital_pressure)  
    )  

    portfolio_df["stress_watchlist"] = (  
        portfolio_df["stressed_pd"]  
        .apply(stress_watchlist)  
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
    # EXECUTIVE NARRATIVE  
    # -------------------------------------------------------------------------  

    portfolio_df["executive_narrative"] = (  
        portfolio_df.apply(  
            lambda row:  
            generate_stress_narrative(  
                scenario,  
                row["stress_severity"],  
                row["capital_pressure"],  
            ),  
            axis=1  
        )  
    )  

    return portfolio_df

# =============================================================================

# PORTFOLIO STRESS SUMMARY

# =============================================================================

def portfolio_stress_summary(
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

    deterioration_pct = portfolio_loss_impact(  
        baseline_total,  
        stressed_total  
    )  

    largest_stressed_exposure = round(
        float(
            stressed_df[
                "stressed_ecl"
            ].max()
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

    if stress_concentration >= 50:

        concentration_risk = "HIGH"

    elif stress_concentration >= 25:

        concentration_risk = "MODERATE"

    else:

        concentration_risk = "LOW"

    stress_grade = portfolio_stress_grade(
        deterioration_pct
    )

    executive_narrative = (
        portfolio_stress_narrative(
            scenario,
            deterioration_pct,
            stress_grade
        )
    )

    summary = {  

        "scenario":  
            scenario,  

        "baseline_portfolio_loss":  
            baseline_total,  

        "stressed_portfolio_loss":  
            stressed_total,  

        "portfolio_loss_deterioration_pct":  
            deterioration_pct,  

        "average_stressed_pd":  
            round(  
                float(  
                    stressed_df[  
                        "stressed_pd"  
                    ].mean()  
                ),  
                4  
            ),  

        "maximum_stressed_ecl":  
            round(  
                float(  
                    stressed_df[  
                        "stressed_ecl"  
                    ].max()  
                ),  
                2  
            ),

        "largest_stressed_exposure":
            largest_stressed_exposure,

        "stress_concentration":
            stress_concentration,

        "concentration_risk":
            concentration_risk,

        "stress_grade":
            stress_grade,

        "executive_narrative":
            executive_narrative,
    }  

    return summary

# =============================================================================

# TOP STRESS EXPOSURES

# =============================================================================

def top_stressed_accounts(
stressed_df,
top_n=10
):
    """
    Extract highest stressed borrowers.
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
            "loss_impact_pct",  
            "stress_severity",  
            "capital_pressure",
        ]  
    ]

# =============================================================================

# FULL STRESS PIPELINE

# =============================================================================

def run_stress_pipeline(
portfolio_df,
scenario="SEVERE RECESSION"
):
    """
    Run full enterprise stress testing workflow.
    """

    stressed_df = run_stress_test(  
        portfolio_df,  
        scenario  
    )  

    summary = portfolio_stress_summary(  
        stressed_df,  
        scenario  
    )  

    top_accounts = top_stressed_accounts(  
        stressed_df  
    )  

    # -------------------------------------------------------------------------  
    # REPORTING  
    # -------------------------------------------------------------------------  

    print("\n[KRONOS] STRESS TEST SUMMARY\n")  

    for key, value in summary.items():  

        print(f"{key}: {value}")  

    print("\n" + "-" * 80)  

    print("\nTOP STRESSED ACCOUNTS\n")  

    print(top_accounts)  

    print("\n" + "-" * 80)  

    print("\nPORTFOLIO STRESS DETAILS\n")  

    print(  
        stressed_df[  
            [  
                "borrower_id",  
                "baseline_ecl",  
                "stressed_ecl",  
                "loss_impact_pct",  
                "stress_severity",  
                "capital_pressure",  
                "stress_watchlist",
                "stress_rank",
                "executive_narrative",  
            ]  
        ]  
    )  

    print("=" * 80)  

    return {  
        "portfolio_results":  
            stressed_df,  

        "summary":  
            summary,  

        "top_stressed_accounts":  
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
    "ead": 15000,  
},  

{  
    "borrower_id": "B1002",  
    "pd_score": 0.28,  
    "lgd": 0.62,  
    "ead": 48000,  
},  

{  
    "borrower_id": "B1003",  
    "pd_score": 0.65,  
    "lgd": 0.81,  
    "ead": 92000,  
},  

{  
    "borrower_id": "B1004",  
    "pd_score": 0.14,  
    "lgd": 0.36,  
    "ead": 26000,  
},

])

# =============================================================================

# MAIN EXECUTION

# =============================================================================

if __name__ == "__main__":

    run_stress_pipeline(  
        SAMPLE_PORTFOLIO,  
        scenario="SEVERE RECESSION"  
    )  

    print("\n[KRONOS] STRESS ENGINE COMPLETED")

# =============================================================================

# END OF FILE

# =============================================================================
