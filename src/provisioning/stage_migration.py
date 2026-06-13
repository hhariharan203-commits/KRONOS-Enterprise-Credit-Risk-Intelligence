# =============================================================================
# KRONOS — IFRS9 STAGE MIGRATION ENGINE
# File: src/provisioning/stage_migration.py
# =============================================================================

import pandas as pd
import numpy as np

# =============================================================================
# IFRS9 STAGE ORDER
# =============================================================================

STAGE_ORDER = [
    "STAGE 1",
    "STAGE 2",
    "STAGE 3",
]

# =============================================================================
# STAGE POSITION
# =============================================================================

def stage_position(
    stage
):
    """
    Convert IFRS9 stage into ordinal position.
    """

    if stage in STAGE_ORDER:

        return STAGE_ORDER.index(
            stage
        )

    return len(STAGE_ORDER)

# =============================================================================
# MIGRATION DIRECTION
# =============================================================================

def stage_migration_direction(
    previous_stage,
    current_stage
):
    """
    Determine IFRS9 migration direction.
    """

    previous_pos = stage_position(
        previous_stage
    )

    current_pos = stage_position(
        current_stage
    )

    if current_pos > previous_pos:

        return "DETERIORATION"

    elif current_pos < previous_pos:

        return "RECOVERY"

    return "STABLE"

# =============================================================================
# MIGRATION SEVERITY
# =============================================================================

def migration_severity(
    previous_stage,
    current_stage
):
    """
    Determine stage migration severity.
    """

    previous_pos = stage_position(
        previous_stage
    )

    current_pos = stage_position(
        current_stage
    )

    movement = abs(
        current_pos - previous_pos
    )

    if movement == 0:

        return "NO MOVEMENT"

    elif movement == 1:

        return "MODERATE MIGRATION"

    return "SEVERE MIGRATION"

# =============================================================================
# MIGRATION RISK GRADE
# =============================================================================

def migration_risk_grade(
    current_stage
):
    """
    IFRS9 migration risk grade.
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
# RESERVE PRESSURE SCORE
# =============================================================================

def reserve_pressure_score(
    current_stage,
    ecl
):
    """
    Calculate reserve pressure intensity.
    """

    stage_multiplier = {

        "STAGE 1": 1.0,
        "STAGE 2": 1.8,
        "STAGE 3": 3.0,
    }

    multiplier = stage_multiplier.get(
        current_stage,
        1.0
    )

    pressure = (
        ecl * multiplier
    ) / 1000

    pressure = min(
        round(pressure, 2),
        100
    )

    return pressure

# =============================================================================
# IMPAIRMENT TREND
# =============================================================================

def impairment_trend(
    previous_ecl,
    current_ecl
):
    """
    Determine impairment trend direction.
    """

    delta = current_ecl - previous_ecl

    if delta < -500:

        return "IMPROVING"

    elif delta < 500:

        return "STABLE"

    elif delta < 5000:

        return "DETERIORATING"

    return "SEVERE DETERIORATION"

# =============================================================================
# STAGE ESCALATION ACTION
# =============================================================================

def escalation_action(
    current_stage,
    migration_direction
):
    """
    Determine reserve governance escalation.
    """

    if current_stage == "STAGE 1":

        return (
            "Maintain standard provisioning review"
        )

    elif current_stage == "STAGE 2":

        return (
            "Increase monitoring and reassess "
            "lifetime reserve assumptions"
        )

    elif current_stage == "STAGE 3":

        return (
            "Escalate impairment governance and "
            "activate recovery management"
        )

    return (
        "Standard reserve monitoring"
    )

# =============================================================================
# EXECUTIVE MIGRATION NARRATIVE
# =============================================================================

def generate_stage_narrative(
    borrower_id,
    previous_stage,
    current_stage,
    migration_direction
):
    """
    Generate executive impairment narrative.
    """

    if migration_direction == "DETERIORATION":

        narrative = (
            f"Borrower {borrower_id} migrated from "
            f"{previous_stage} to {current_stage}, "
            "indicating elevated impairment pressure."
        )

    elif migration_direction == "RECOVERY":

        narrative = (
            f"Borrower {borrower_id} improved from "
            f"{previous_stage} to {current_stage}, "
            "reflecting stabilization in credit quality."
        )

    else:

        narrative = (
            f"Borrower {borrower_id} remains stable in "
            f"{current_stage} with limited stage volatility."
        )

    return narrative

# =============================================================================
# STAGE TRANSITION MATRIX
# =============================================================================

def build_stage_transition_matrix(
    portfolio_df
):
    """
    Build IFRS9 transition matrix.
    """

    matrix = pd.crosstab(
        portfolio_df["previous_stage"],
        portfolio_df["current_stage"]
    )

    return matrix

# =============================================================================
# PORTFOLIO MIGRATION SUMMARY
# =============================================================================

def portfolio_stage_summary(
    portfolio_df
):
    """
    Generate stage migration portfolio statistics.
    """

    deterioration = len(
        portfolio_df[
            portfolio_df["migration_direction"]
            == "DETERIORATION"
        ]
    )

    recovery = len(
        portfolio_df[
            portfolio_df["migration_direction"]
            == "RECOVERY"
        ]
    )

    stable = len(
        portfolio_df[
            portfolio_df["migration_direction"]
            == "STABLE"
        ]
    )

    total = len(
        portfolio_df
    )

    stage3_accounts = len(
        portfolio_df[
            portfolio_df["current_stage"]
            == "STAGE 3"
        ]
    )

    stage3_concentration = round(
        (
            stage3_accounts
            / total
        ) * 100,
        2
    )

    summary = {

        "total_accounts":
            total,

        "deterioration_accounts":
            deterioration,

        "recovery_accounts":
            recovery,

        "stable_accounts":
            stable,

        "deterioration_ratio":
            round(
                (deterioration / total) * 100,
                2
            ),

        "stage3_concentration":
            stage3_concentration,
    }

    return summary

# =============================================================================
# PORTFOLIO STAGE HEALTH
# =============================================================================

def portfolio_stage_health(
    summary
):
    """
    Portfolio impairment health score.
    """

    deterioration_ratio = summary[
        "deterioration_ratio"
    ]

    health_score = max(
        100 - deterioration_ratio,
        0
    )

    return round(
        health_score,
        2
    )

# =============================================================================
# MAIN STAGE MIGRATION ENGINE
# =============================================================================

def run_stage_migration_analysis(
    portfolio_df
):
    """
    Run enterprise IFRS9 migration analysis.
    """

    print("\n" + "=" * 80)
    print("[KRONOS] RUNNING IFRS9 STAGE MIGRATION")
    print("=" * 80)

    portfolio_df = portfolio_df.copy()

    # -------------------------------------------------------------------------
    # STAGE MOVEMENT
    # -------------------------------------------------------------------------

    portfolio_df["migration_direction"] = (
        portfolio_df.apply(
            lambda row:
            stage_migration_direction(
                row["previous_stage"],
                row["current_stage"],
            ),
            axis=1
        )
    )

    portfolio_df["migration_severity"] = (
        portfolio_df.apply(
            lambda row:
            migration_severity(
                row["previous_stage"],
                row["current_stage"],
            ),
            axis=1
        )
    )

    portfolio_df["migration_risk_grade"] = (
        portfolio_df["current_stage"]
        .apply(
            migration_risk_grade
        )
    )

    # -------------------------------------------------------------------------
    # RESERVE PRESSURE
    # -------------------------------------------------------------------------

    portfolio_df["reserve_pressure_score"] = (
        portfolio_df.apply(
            lambda row:
            reserve_pressure_score(
                row["current_stage"],
                row["current_ecl"],
            ),
            axis=1
        )
    )

    # -------------------------------------------------------------------------
    # IMPAIRMENT TREND
    # -------------------------------------------------------------------------

    portfolio_df["impairment_trend"] = (
        portfolio_df.apply(
            lambda row:
            impairment_trend(
                row["previous_ecl"],
                row["current_ecl"],
            ),
            axis=1
        )
    )

    # -------------------------------------------------------------------------
    # ESCALATION ACTIONS
    # -------------------------------------------------------------------------

    portfolio_df["escalation_action"] = (
        portfolio_df.apply(
            lambda row:
            escalation_action(
                row["current_stage"],
                row["migration_direction"],
            ),
            axis=1
        )
    )

    # -------------------------------------------------------------------------
    # EXECUTIVE NARRATIVES
    # -------------------------------------------------------------------------

    portfolio_df["executive_narrative"] = (
        portfolio_df.apply(
            lambda row:
            generate_stage_narrative(
                row["borrower_id"],
                row["previous_stage"],
                row["current_stage"],
                row["migration_direction"],
            ),
            axis=1
        )
    )

    # -------------------------------------------------------------------------
    # TRANSITION MATRIX
    # -------------------------------------------------------------------------

    transition_matrix = build_stage_transition_matrix(
        portfolio_df
    )

    # -------------------------------------------------------------------------
    # PORTFOLIO SUMMARY
    # -------------------------------------------------------------------------

    summary = portfolio_stage_summary(
        portfolio_df
    )

    health_score = portfolio_stage_health(
        summary
    )

    # -------------------------------------------------------------------------
    # REPORTING
    # -------------------------------------------------------------------------

    print("\n[KRONOS] IFRS9 STAGE SUMMARY\n")

    for key, value in summary.items():

        print(f"{key}: {value}")

    print(
        f"\nPortfolio Stage Health: "
        f"{health_score}"
    )

    print("\n" + "-" * 80)

    print("\nIFRS9 TRANSITION MATRIX\n")

    print(transition_matrix)

    print("\n" + "-" * 80)

    print("\nSTAGE MIGRATION DETAILS\n")

    print(
        portfolio_df[
            [
                "borrower_id",
                "previous_stage",
                "current_stage",
                "migration_direction",
                "migration_severity",
                "migration_risk_grade",
                "reserve_pressure_score",
                "impairment_trend",
            ]
        ]
    )

    print("=" * 80)

    return {

        "portfolio_results":
            portfolio_df,

        "summary":
            summary,

        "portfolio_stage_health":
            health_score,

        "transition_matrix":
            transition_matrix,
    }

# =============================================================================
# SAMPLE PORTFOLIO
# =============================================================================

SAMPLE_PORTFOLIO = pd.DataFrame([

    {
        "borrower_id": "B1001",
        "previous_stage": "STAGE 1",
        "current_stage": "STAGE 1",
        "previous_ecl": 900,
        "current_ecl": 1200,
    },

    {
        "borrower_id": "B1002",
        "previous_stage": "STAGE 1",
        "current_stage": "STAGE 2",
        "previous_ecl": 2400,
        "current_ecl": 9200,
    },

    {
        "borrower_id": "B1003",
        "previous_stage": "STAGE 2",
        "current_stage": "STAGE 3",
        "previous_ecl": 11000,
        "current_ecl": 34000,
    },

    {
        "borrower_id": "B1004",
        "previous_stage": "STAGE 2",
        "current_stage": "STAGE 1",
        "previous_ecl": 7200,
        "current_ecl": 1800,
    },

])

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":

    run_stage_migration_analysis(
        SAMPLE_PORTFOLIO
    )

    print("\n[KRONOS] IFRS9 STAGE MIGRATION COMPLETED")

# =============================================================================
# END OF FILE
# =============================================================================