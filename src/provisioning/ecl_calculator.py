# =============================================================================
# KRONOS — ENTERPRISE ECL CALCULATOR
# File: src/provisioning/ecl_calculator.py
# =============================================================================

import pandas as pd
import numpy as np

# =============================================================================
# BORROWER ECL CALCULATION
# =============================================================================

def calculate_borrower_ecl(
    pd_score,
    lgd,
    ead,
    current_stage
):
    """
    Calculate borrower-level Expected Credit Loss.
    """

    stage_multiplier = {

        "STAGE 1": 1.0,

        "STAGE 2": 1.5,

        "STAGE 3": 2.0,
    }

    multiplier = stage_multiplier.get(
        current_stage,
        1.0
    )

    ecl = (
        pd_score
        * lgd
        * ead
        * multiplier
    )

    return round(
        float(ecl),
        2
    )

# =============================================================================
# RESERVE COVERAGE RATIO
# =============================================================================

def reserve_coverage_ratio(
    ecl,
    ead
):
    """
    Calculate reserve coverage percentage.
    """

    if ead <= 0:

        return 0

    ratio = (
        ecl / ead
    ) * 100

    return round(
        ratio,
        2
    )

# =============================================================================
# ECL RISK SEGMENT
# =============================================================================

def classify_ecl_segment(
    ecl
):
    """
    Classify reserve severity segment.
    """

    if ecl < 1000:

        return "LOW EXPECTED LOSS"

    elif ecl < 5000:

        return "MODERATE EXPECTED LOSS"

    elif ecl < 20000:

        return "HIGH EXPECTED LOSS"

    else:

        return "SEVERE EXPECTED LOSS"

# =============================================================================
# PORTFOLIO RESERVE CONCENTRATION
# =============================================================================

def reserve_concentration(
    borrower_ecl,
    portfolio_ecl
):
    """
    Calculate borrower reserve concentration.
    """

    if portfolio_ecl <= 0:

        return 0

    concentration = (
        borrower_ecl / portfolio_ecl
    ) * 100

    return round(
        concentration,
        2
    )

# =============================================================================
# IMPAIRMENT CATEGORY
# =============================================================================

def impairment_category(
    current_stage
):
    """
    Determine impairment category.
    """

    mapping = {

        "STAGE 1":
            "PERFORMING",

        "STAGE 2":
            "UNDERPERFORMING",

        "STAGE 3":
            "CREDIT IMPAIRED",
    }

    return mapping.get(
        current_stage,
        "UNKNOWN"
    )

# =============================================================================
# RESERVE RISK GRADE
# =============================================================================

def reserve_risk_grade(
    current_stage
):
    """
    Reserve severity grade.
    """

    mapping = {

        "STAGE 1": "A",

        "STAGE 2": "B",

        "STAGE 3": "C",
    }

    return mapping.get(
        current_stage,
        "UNKNOWN"
    )

# =============================================================================
# EXECUTIVE ECL NARRATIVE
# =============================================================================

def generate_ecl_narrative(
    borrower_id,
    ecl_segment,
    stage
):
    """
    Generate executive ECL narrative.
    """

    if stage == "STAGE 1":

        narrative = (
            f"Borrower {borrower_id} remains within "
            "performing reserve thresholds with "
            "limited expected impairment exposure."
        )

    elif stage == "STAGE 2":

        narrative = (
            f"Borrower {borrower_id} demonstrates "
            "elevated reserve pressure requiring "
            "lifetime expected loss coverage."
        )

    else:

        narrative = (
            f"Borrower {borrower_id} is classified "
            "as credit-impaired with severe "
            "expected loss exposure."
        )

    narrative += f" Risk classification: {ecl_segment}."

    return narrative

# =============================================================================
# CALCULATE PORTFOLIO ECL
# =============================================================================

def calculate_portfolio_ecl(
    portfolio_df
):
    """
    Calculate enterprise portfolio ECL.
    """

    portfolio_df = portfolio_df.copy()

    # -------------------------------------------------------------------------
    # BORROWER ECL
    # -------------------------------------------------------------------------

    portfolio_df["expected_credit_loss"] = (
        portfolio_df.apply(
            lambda row:
            calculate_borrower_ecl(
                row["pd_score"],
                row["lgd"],
                row["ead"],
                row["current_stage"],
            ),
            axis=1
        )
    )

    # -------------------------------------------------------------------------
    # TOTAL PORTFOLIO ECL
    # -------------------------------------------------------------------------

    total_portfolio_ecl = (
        portfolio_df["expected_credit_loss"]
        .sum()
    )

    # -------------------------------------------------------------------------
    # COVERAGE RATIOS
    # -------------------------------------------------------------------------

    portfolio_df["reserve_coverage_ratio"] = (
        portfolio_df.apply(
            lambda row:
            reserve_coverage_ratio(
                row["expected_credit_loss"],
                row["ead"],
            ),
            axis=1
        )
    )

    # -------------------------------------------------------------------------
    # ECL SEGMENTS
    # -------------------------------------------------------------------------

    portfolio_df["ecl_segment"] = (
        portfolio_df["expected_credit_loss"]
        .apply(classify_ecl_segment)
    )

    # -------------------------------------------------------------------------
    # RESERVE CONCENTRATION
    # -------------------------------------------------------------------------

    portfolio_df["reserve_concentration"] = (
        portfolio_df["expected_credit_loss"]
        .apply(
            lambda x:
            reserve_concentration(
                x,
                total_portfolio_ecl
            )
        )
    )

    # -------------------------------------------------------------------------
    # IMPAIRMENT CATEGORY
    # -------------------------------------------------------------------------

    portfolio_df["impairment_category"] = (
        portfolio_df["current_stage"]
        .apply(impairment_category)
    )

    # -------------------------------------------------------------------------
    # RESERVE RISK GRADE
    # -------------------------------------------------------------------------

    portfolio_df["reserve_risk_grade"] = (
        portfolio_df["current_stage"]
        .apply(
            reserve_risk_grade
        )
    )

    # -------------------------------------------------------------------------
    # EXECUTIVE NARRATIVES
    # -------------------------------------------------------------------------

    portfolio_df["executive_narrative"] = (
        portfolio_df.apply(
            lambda row:
            generate_ecl_narrative(
                row["borrower_id"],
                row["ecl_segment"],
                row["current_stage"],
            ),
            axis=1
        )
    )

    return (
        portfolio_df,
        total_portfolio_ecl
    )

# =============================================================================
# PORTFOLIO ECL SUMMARY
# =============================================================================

def portfolio_ecl_summary(
    portfolio_df,
    total_ecl
):
    """
    Generate enterprise reserve summary.
    """

    # -------------------------------------------------------------------------
    # STAGE DISTRIBUTION
    # -------------------------------------------------------------------------

    stage_distribution = (
        portfolio_df["current_stage"]
        .value_counts()
        .to_dict()
    )

    # -------------------------------------------------------------------------
    # ECL SEGMENT DISTRIBUTION
    # -------------------------------------------------------------------------

    segment_distribution = (
        portfolio_df["ecl_segment"]
        .value_counts()
        .to_dict()
    )

    # -------------------------------------------------------------------------
    # STAGE ECL DISTRIBUTION
    # -------------------------------------------------------------------------

    stage_ecl = (
        portfolio_df
        .groupby("current_stage")["expected_credit_loss"]
        .sum()
        .to_dict()
    )

    stage_ecl_distribution = {

        stage: round(
            float(value / total_ecl) * 100,
            2
        )

        for stage, value in stage_ecl.items()
    }

    # -------------------------------------------------------------------------
    # STAGE 3 ECL AMOUNT
    # -------------------------------------------------------------------------

    stage3_ecl_amount = round(
        float(
            stage_ecl.get(
                "STAGE 3",
                0
            )
        ),
        2
    )

    # -------------------------------------------------------------------------
    # STAGE 3 CONCENTRATION
    # -------------------------------------------------------------------------

    stage3_ecl_concentration = (
        stage_ecl_distribution.get(
            "STAGE 3",
            0
        )
    )

    # -------------------------------------------------------------------------
    # RESERVE CONCENTRATION
    # -------------------------------------------------------------------------

    largest_concentration = round(
        float(
            portfolio_df[
                "reserve_concentration"
            ].max()
        ),
        2
    )

    # -------------------------------------------------------------------------
    # CONCENTRATION RISK
    # -------------------------------------------------------------------------

    if largest_concentration >= 50:

        concentration_risk = "HIGH"

    elif largest_concentration >= 25:

        concentration_risk = "MODERATE"

    else:

        concentration_risk = "LOW"

    # -------------------------------------------------------------------------
    # PORTFOLIO COVERAGE RATIO
    # -------------------------------------------------------------------------

    total_ead = (
        portfolio_df["ead"]
        .sum()
    )

    portfolio_coverage_ratio = round(
        (total_ecl / total_ead) * 100,
        2
    )

    # -------------------------------------------------------------------------
    # EXECUTIVE NARRATIVE
    # -------------------------------------------------------------------------

    narrative = portfolio_ecl_narrative(
        largest_concentration,
        concentration_risk
    )

    # -------------------------------------------------------------------------
    # SUMMARY
    # -------------------------------------------------------------------------

    summary = {

        "total_accounts":
            len(portfolio_df),

        "total_portfolio_ecl":
            round(
                float(total_ecl),
                2
            ),

        "average_borrower_ecl":
            round(
                float(
                    portfolio_df[
                        "expected_credit_loss"
                    ].mean()
                ),
                2
            ),

        "max_borrower_ecl":
            round(
                float(
                    portfolio_df[
                        "expected_credit_loss"
                    ].max()
                ),
                2
            ),

        "portfolio_coverage_ratio":
            portfolio_coverage_ratio,

        "largest_reserve_concentration":
            largest_concentration,

        "concentration_risk":
            concentration_risk,

        "stage_distribution":
            stage_distribution,

        "stage_ecl_distribution":
            stage_ecl_distribution,

        "stage3_ecl_amount":
            stage3_ecl_amount,

        "stage3_ecl_concentration":
            stage3_ecl_concentration,

        "ecl_segment_distribution":
            segment_distribution,

        "executive_narrative":
            narrative,
    }

    return summary

# =============================================================================
# TOP RESERVE CONCENTRATION
# =============================================================================

def top_reserve_exposures(
    portfolio_df,
    top_n=10
):
    """
    Extract largest reserve concentrations.
    """

    top_df = portfolio_df.sort_values(
        by="expected_credit_loss",
        ascending=False
    )

    return top_df.head(top_n)[
        [
            "borrower_id",
            "current_stage",
            "expected_credit_loss",
            "reserve_coverage_ratio",
            "reserve_risk_grade",
            "impairment_category",
            "ecl_segment",
            "reserve_concentration",
        ]
    ]

# =============================================================================
# PORTFOLIO ECL NARRATIVE
# =============================================================================

def portfolio_ecl_narrative(
    largest_concentration,
    concentration_risk
):
    """
    Executive reserve narrative.
    """

    return (
        f"KRONOS portfolio reserves show "
        f"{concentration_risk.lower()} concentration risk. "
        f"The largest borrower contributes "
        f"{largest_concentration}% of total expected credit loss."
    )

# =============================================================================
# FULL ECL PIPELINE
# =============================================================================

def run_ecl_pipeline(
    portfolio_df
):
    """
    Run enterprise ECL workflow.
    """

    print("\n" + "=" * 80)
    print("[KRONOS] RUNNING ECL CALCULATOR")
    print("=" * 80)

    (
        portfolio_results,
        total_ecl
    ) = calculate_portfolio_ecl(
        portfolio_df
    )

    summary = portfolio_ecl_summary(
        portfolio_results,
        total_ecl
    )

    top_exposures = top_reserve_exposures(
        portfolio_results
    )

    # -------------------------------------------------------------------------
    # REPORTING
    # -------------------------------------------------------------------------

    print("\n[KRONOS] PORTFOLIO ECL SUMMARY\n")

    for key, value in summary.items():

        print(f"{key}: {value}")

    print("\n" + "-" * 80)

    print("\nTOP RESERVE EXPOSURES\n")

    print(top_exposures)

    print("\n" + "-" * 80)

    print("\nBORROWER ECL DETAILS\n")

    print(
        portfolio_results[
            [
                "borrower_id",
                "current_stage",
                "expected_credit_loss",
                "reserve_coverage_ratio",
                "reserve_risk_grade",
                "impairment_category",
                "ecl_segment",
                "reserve_concentration",
            ]
        ]
    )

    print("=" * 80)

    return {
        "portfolio_results":
            portfolio_results,

        "summary":
            summary,

        "top_reserve_exposures":
            top_exposures,
    }

# =============================================================================
# SAMPLE PORTFOLIO
# =============================================================================

SAMPLE_PORTFOLIO = pd.DataFrame([

    {
        "borrower_id": "B1001",
        "pd_score": 0.04,
        "lgd": 0.22,
        "ead": 12000,
        "current_stage": "STAGE 1",
    },

    {
        "borrower_id": "B1002",
        "pd_score": 0.26,
        "lgd": 0.58,
        "ead": 42000,
        "current_stage": "STAGE 2",
    },

    {
        "borrower_id": "B1003",
        "pd_score": 0.63,
        "lgd": 0.77,
        "ead": 78000,
        "current_stage": "STAGE 3",
    },

    {
        "borrower_id": "B1004",
        "pd_score": 0.14,
        "lgd": 0.35,
        "ead": 26000,
        "current_stage": "STAGE 2",
    },

])

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":

    run_ecl_pipeline(
        SAMPLE_PORTFOLIO
    )

    print("\n[KRONOS] ECL CALCULATOR COMPLETED")

# =============================================================================
# END OF FILE
# =============================================================================