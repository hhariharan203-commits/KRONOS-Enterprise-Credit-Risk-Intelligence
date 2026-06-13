# =============================================================================
# KRONOS — SYSTEMIC RISK ENGINE
# File: src/contagion/systemic_risk.py
# =============================================================================

import pandas as pd
import numpy as np

# =============================================================================
# SYSTEMIC RISK THRESHOLDS
# =============================================================================

SYSTEMIC_THRESHOLDS = {

    "LOW": 20,
    "MODERATE": 40,
    "HIGH": 65,
    "CRITICAL": 85,
}

# =============================================================================
# SYSTEMIC FRAGILITY SCORE
# =============================================================================

def systemic_fragility_score(
    pd_score,
    exposure_concentration,
    contagion_risk
):
    """
    Calculate systemic fragility intensity.
    """

    fragility = (

        (pd_score * 100 * 0.40)
        + (exposure_concentration * 0.35)
        + (contagion_risk * 100 * 0.25)

    )

    return min(
        round(fragility, 2),
        100
    )

# =============================================================================
# SYSTEMIC COLLAPSE PROBABILITY
# =============================================================================

def systemic_collapse_probability(
    fragility_score
):
    """
    Estimate probability of systemic instability.
    """

    probability = (
        fragility_score / 100
    )

    return round(
        probability,
        4
    )

# =============================================================================
# NETWORK INSTABILITY
# =============================================================================

def network_instability(
    collapse_probability
):
    """
    Determine systemic network condition.
    """

    if collapse_probability < 0.20:

        return "STABLE FINANCIAL NETWORK"

    elif collapse_probability < 0.40:

        return "ELEVATED SYSTEMIC RISK"

    elif collapse_probability < 0.65:

        return "HIGH NETWORK INSTABILITY"

    return "CRITICAL SYSTEMIC INSTABILITY"

# =============================================================================
# CONCENTRATION SYSTEMICITY
# =============================================================================

def concentration_systemicity(
    exposure_concentration
):
    """
    Classify systemic concentration pressure.
    """

    if exposure_concentration < 10:

        return "LOW CONCENTRATION RISK"

    elif exposure_concentration < 20:

        return "MODERATE CONCENTRATION RISK"

    elif exposure_concentration < 35:

        return "HIGH CONCENTRATION RISK"

    return "SYSTEMIC CONCENTRATION RISK"

# =============================================================================
# ENTERPRISE RESILIENCE SCORE
# =============================================================================

def enterprise_resilience_score(
    fragility_score
):
    """
    Estimate enterprise resilience capacity.
    """

    resilience = (
        100 - fragility_score
    )

    return max(
        round(resilience, 2),
        0
    )

# =============================================================================
# SYSTEMIC RISK CLASSIFICATION
# =============================================================================

def systemic_risk_classification(
    fragility_score
):
    """
    Determine systemic risk severity.
    """

    if fragility_score < SYSTEMIC_THRESHOLDS["LOW"]:

        return "LOW SYSTEMIC RISK"

    elif fragility_score < SYSTEMIC_THRESHOLDS["MODERATE"]:

        return "MODERATE SYSTEMIC RISK"

    elif fragility_score < SYSTEMIC_THRESHOLDS["HIGH"]:

        return "HIGH SYSTEMIC RISK"

    return "CRITICAL SYSTEMIC RISK"

# =============================================================================
# FINANCIAL STABILITY STATUS
# =============================================================================

def financial_stability_status(
    resilience_score
):
    """
    Determine financial system resilience.
    """

    if resilience_score >= 80:

        return "HIGHLY RESILIENT SYSTEM"

    elif resilience_score >= 60:

        return "MODERATELY RESILIENT SYSTEM"

    elif resilience_score >= 35:

        return "FRAGILE FINANCIAL SYSTEM"

    return "SEVERELY DISTRESSED SYSTEM"

# =============================================================================
# SYSTEMIC IMPORTANCE INDEX
# =============================================================================

def systemic_importance_index(
    fragility_score,
    concentration_score
):
    """
    Calculate enterprise systemic importance.
    """

    importance = (

        fragility_score * 0.60
        + concentration_score * 0.40

    )

    return min(
        round(importance, 2),
        100
    )

# =============================================================================
# EXECUTIVE SYSTEMIC NARRATIVE
# =============================================================================

def generate_systemic_narrative(
    borrower_id,
    risk_classification,
    stability_status
):
    """
    Generate executive systemic-risk commentary.
    """

    narrative = (
        f"Borrower {borrower_id} exhibits "
        f"{risk_classification.lower()} within a "
        f"{stability_status.lower()} environment."
    )

    return narrative

# =============================================================================
# RUN SYSTEMIC RISK ANALYSIS
# =============================================================================

def run_systemic_risk_analysis(
    portfolio_df
):
    """
    Run enterprise systemic-risk intelligence workflow.
    """

    print("\n" + "=" * 80)
    print("[KRONOS] RUNNING SYSTEMIC RISK ENGINE")
    print("=" * 80)

    portfolio_df = (
        portfolio_df.copy()
    )

    print(
        f"Portfolio Rows Before Filter: "
        f"{len(portfolio_df):,}"
    )

    portfolio_df = (
        portfolio_df
        .nlargest(
            500,
            "ead"
        )
        .reset_index(
            drop=True
        )
    )

    print(
        f"Portfolio Rows After Filter: "
        f"{len(portfolio_df):,}"
    )

    total_portfolio_exposure = (
        portfolio_df["ead"]
        .sum()
    )

    systemic_results = []

    # -------------------------------------------------------------------------
    # SYSTEMIC ANALYSIS
    # -------------------------------------------------------------------------

    for _, borrower in portfolio_df.iterrows():

        borrower_id = borrower["borrower_id"]

        pd_score = borrower["pd_score"]

        exposure = borrower["ead"]

        contagion_risk = borrower.get(
            "contagion_risk",
            0.20
        )

        # ---------------------------------------------------------------------
        # CONCENTRATION
        # ---------------------------------------------------------------------

        concentration = (
            exposure
            / total_portfolio_exposure
        ) * 100

        concentration = round(
            concentration,
            2
        )

        # ---------------------------------------------------------------------
        # FRAGILITY
        # ---------------------------------------------------------------------

        fragility = systemic_fragility_score(
            pd_score,
            concentration,
            contagion_risk
        )

        collapse_probability = (
            systemic_collapse_probability(
                fragility
            )
        )

        instability = network_instability(
            collapse_probability
        )

        concentration_risk = (
            concentration_systemicity(
                concentration
            )
        )

        resilience = (
            enterprise_resilience_score(
                fragility
            )
        )

        systemic_risk = (
            systemic_risk_classification(
                fragility
            )
        )

        stability_status = (
            financial_stability_status(
                resilience
            )
        )

        systemic_importance = (
            systemic_importance_index(
                fragility,
                concentration
            )
        )

        narrative = generate_systemic_narrative(
            borrower_id,
            systemic_risk,
            stability_status
        )

        systemic_results.append({

            "borrower_id":
                borrower_id,

            "systemic_fragility_score":
                fragility,

            "collapse_probability":
                collapse_probability,

            "network_instability":
                instability,

            "concentration_risk":
                concentration_risk,

            "enterprise_resilience_score":
                resilience,

            "systemic_risk_classification":
                systemic_risk,

            "financial_stability_status":
                stability_status,

            "systemic_importance_index":
                systemic_importance,

            "executive_narrative":
                narrative,
        })

    systemic_df = pd.DataFrame(
        systemic_results
    )

    # -------------------------------------------------------------------------
    # PORTFOLIO SYSTEMIC SUMMARY
    # -------------------------------------------------------------------------

    average_fragility = round(
        float(
            systemic_df[
                "systemic_fragility_score"
            ].mean()
        ),
        2
    )

    average_resilience = round(
        float(
            systemic_df[
                "enterprise_resilience_score"
            ].mean()
        ),
        2
    )

    portfolio_instability = network_instability(
        average_fragility / 100
    )

    summary = {

        "average_systemic_fragility":
            average_fragility,

        "average_enterprise_resilience":
            average_resilience,

        "portfolio_network_instability":
            portfolio_instability,

        "maximum_systemic_importance":
            round(
                float(
                    systemic_df[
                        "systemic_importance_index"
                    ].max()
                ),
                2
            ),

        "average_systemic_importance":
            round(
                float(
                    systemic_df[
                        "systemic_importance_index"
                    ].mean()
                ),
                2
            ),

        "maximum_collapse_probability":
            round(
                float(
                    systemic_df[
                        "collapse_probability"
                    ].max()
                ),
                4
            ),

        "average_collapse_probability":
            round(
                float(
                    systemic_df[
                        "collapse_probability"
                    ].mean()
                ),
                4
            ),

        "critical_systemic_entities":
            int(
                (
                    systemic_df[
                        "systemic_risk_classification"
                    ]
                    == "CRITICAL SYSTEMIC RISK"
                ).sum()
            ),
    }

    # -------------------------------------------------------------------------
    # REPORTING
    # -------------------------------------------------------------------------

    print("\n[KRONOS] SYSTEMIC RISK SUMMARY\n")

    for key, value in summary.items():

        print(f"{key}: {value}")

    print("\n" + "-" * 80)

    print("\nSYSTEMIC RISK ANALYSIS\n")

    print(
        systemic_df[
            [
                "borrower_id",
                "systemic_fragility_score",
                "collapse_probability",
                "network_instability",
                "enterprise_resilience_score",
                "systemic_risk_classification",
                "systemic_importance_index",
            ]
        ].head(25)
    )

    print("=" * 80)

    return {

        "systemic_results":
            systemic_df,

        "summary":
            summary,
    }

# =============================================================================
# SAMPLE PORTFOLIO
# =============================================================================

SAMPLE_PORTFOLIO = pd.DataFrame([

    {
        "borrower_id": "B1001",
        "pd_score": 0.05,
        "ead": 26000,
        "contagion_risk": 0.12,
    },

    {
        "borrower_id": "B1002",
        "pd_score": 0.33,
        "ead": 82000,
        "contagion_risk": 0.38,
    },

    {
        "borrower_id": "B1003",
        "pd_score": 0.76,
        "ead": 160000,
        "contagion_risk": 0.72,
    },

    {
        "borrower_id": "B1004",
        "pd_score": 0.19,
        "ead": 52000,
        "contagion_risk": 0.24,
    },

])

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":

    run_systemic_risk_analysis(
        SAMPLE_PORTFOLIO
    )

    print("\n[KRONOS] SYSTEMIC RISK ENGINE COMPLETED")

# =============================================================================
# END OF FILE
# =============================================================================