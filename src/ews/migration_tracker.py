# =============================================================================
# KRONOS — ENTERPRISE MIGRATION TRACKER
# File: src/ews/migration_tracker.py
# =============================================================================

import pandas as pd
import numpy as np

# =============================================================================
# CREDIT RATING SCALE
# =============================================================================

RATING_ORDER = [
    "AAA",
    "AA",
    "A",
    "BBB",
    "BB",
    "B",
    "CCC",
    "DEFAULT",
]

# =============================================================================
# RATING TO SCORE
# =============================================================================

def rating_position(
    rating
):
    """
    Convert rating into ordinal position.
    """

    if rating in RATING_ORDER:

        return RATING_ORDER.index(
            rating
        )

    return len(RATING_ORDER)

# =============================================================================
# MIGRATION DIRECTION
# =============================================================================

def migration_direction(
    previous_rating,
    current_rating
):
    """
    Determine rating migration direction.
    """

    previous_pos = rating_position(
        previous_rating
    )

    current_pos = rating_position(
        current_rating
    )

    if current_pos < previous_pos:

        return "UPGRADE"

    elif current_pos > previous_pos:

        return "DOWNGRADE"

    else:

        return "STABLE"

# =============================================================================
# MIGRATION SEVERITY
# =============================================================================

def migration_severity(
    previous_rating,
    current_rating
):
    """
    Determine severity of migration.
    """

    previous_pos = rating_position(
        previous_rating
    )

    current_pos = rating_position(
        current_rating
    )

    movement = abs(
        current_pos - previous_pos
    )

    if movement == 0:

        return "NO MOVEMENT"

    elif movement == 1:

        return "MINOR MIGRATION"

    elif movement == 2:

        return "MODERATE MIGRATION"

    else:

        return "SEVERE MIGRATION"

# =============================================================================
# MIGRATION RISK SCORE
# =============================================================================

def migration_risk_score(
    previous_rating,
    current_rating
):
    """
    Calculate migration deterioration score.
    """

    previous_pos = rating_position(
        previous_rating
    )

    current_pos = rating_position(
        current_rating
    )

    movement = current_pos - previous_pos

    if movement <= 0:

        return 0

    risk_score = min(
        movement * 25,
        100
    )

    return risk_score

# =============================================================================
# WATCHLIST ESCALATION
# =============================================================================

def watchlist_escalation(
    current_rating,
    migration_score
):
    """
    Determine institutional escalation level.
    """

    if current_rating in ["AAA", "AA"]:

        return "STANDARD MONITORING"

    elif current_rating in ["A", "BBB"]:

        if migration_score >= 50:

            return "ENHANCED REVIEW"

        return "MODERATE MONITORING"

    elif current_rating in ["BB", "B"]:

        return "WATCHLIST ESCALATION"

    else:

        return "CRITICAL RISK COMMITTEE REVIEW"

# =============================================================================
# IFRS9 STAGE MIGRATION
# =============================================================================

def ifrs_stage_migration(
    current_rating
):
    """
    Map borrower rating to IFRS9 stage.
    """

    if current_rating in [
        "AAA",
        "AA",
        "A"
    ]:

        return "STAGE_1"

    elif current_rating in [
        "BBB",
        "BB"
    ]:

        return "STAGE_2"

    else:

        return "STAGE_3"

# =============================================================================
# TRANSITION MATRIX
# =============================================================================

def build_transition_matrix(
    portfolio_df
):
    """
    Build institutional migration matrix.
    """

    matrix = pd.crosstab(
        portfolio_df["previous_rating"],
        portfolio_df["current_rating"]
    )

    return matrix

# =============================================================================
# PORTFOLIO MIGRATION SUMMARY
# =============================================================================

def portfolio_migration_summary(
    portfolio_df
):
    """
    Generate migration portfolio statistics.
    """

    upgrades = len(
        portfolio_df[
            portfolio_df["migration_direction"]
            == "UPGRADE"
        ]
    )

    downgrades = len(
        portfolio_df[
            portfolio_df["migration_direction"]
            == "DOWNGRADE"
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

    summary = {
        "total_accounts":
            total,

        "upgrades":
            upgrades,

        "downgrades":
            downgrades,

        "stable_accounts":
            stable,

        "downgrade_ratio":
            round(
                (downgrades / total) * 100,
                2
            ),
    }

    return summary

# =============================================================================
# PORTFOLIO HEALTH SCORE
# =============================================================================

def portfolio_health_score(
    summary
):
    """
    Portfolio migration health.
    """

    downgrade_ratio = summary[
        "downgrade_ratio"
    ]

    score = max(
        100 - downgrade_ratio,
        0
    )

    return round(score, 2)

# =============================================================================
# MIGRATION ANALYSIS ENGINE
# =============================================================================

def run_migration_analysis(
    portfolio_df
):
    """
    Run enterprise migration analysis.
    """

    print("\n" + "=" * 80)
    print("[KRONOS] RUNNING MIGRATION TRACKER")
    print("=" * 80)

    portfolio_df = portfolio_df.copy()

    # -------------------------------------------------------------------------
    # MIGRATION ANALYSIS
    # -------------------------------------------------------------------------

    portfolio_df["migration_direction"] = (
        portfolio_df.apply(
            lambda row:
            migration_direction(
                row["previous_rating"],
                row["current_rating"],
            ),
            axis=1
        )
    )

    portfolio_df["migration_severity"] = (
        portfolio_df.apply(
            lambda row:
            migration_severity(
                row["previous_rating"],
                row["current_rating"],
            ),
            axis=1
        )
    )

    portfolio_df["migration_risk_score"] = (
        portfolio_df.apply(
            lambda row:
            migration_risk_score(
                row["previous_rating"],
                row["current_rating"],
            ),
            axis=1
        )
    )

    portfolio_df["watchlist_action"] = (
        portfolio_df.apply(
            lambda row:
            watchlist_escalation(
                row["current_rating"],
                row["migration_risk_score"],
            ),
            axis=1
        )
    )

    portfolio_df["ifrs9_stage"] = (
        portfolio_df["current_rating"]
        .apply(
            ifrs_stage_migration
        )
    )

    # -------------------------------------------------------------------------
    # PORTFOLIO SUMMARY
    # -------------------------------------------------------------------------

    summary = portfolio_migration_summary(
        portfolio_df
    )

    health_score = portfolio_health_score(
        summary
    )

    # -------------------------------------------------------------------------
    # TRANSITION MATRIX
    # -------------------------------------------------------------------------

    transition_matrix = build_transition_matrix(
        portfolio_df
    )

    # -------------------------------------------------------------------------
    # REPORTING
    # -------------------------------------------------------------------------

    print("\n[KRONOS] MIGRATION SUMMARY\n")

    for key, value in summary.items():

        print(f"{key}: {value}")

    print(
        f"\nPortfolio Health Score: "
        f"{health_score}"
    )

    print("\n" + "-" * 80)

    print("\nTRANSITION MATRIX\n")

    print(transition_matrix)

    print("\n" + "-" * 80)

    print("\nBORROWER MIGRATION DETAILS\n")

    print(
        portfolio_df[
            [
                "borrower_id",
                "previous_rating",
                "current_rating",
                "migration_direction",
                "migration_severity",
                "migration_risk_score",
                "ifrs9_stage",
                "watchlist_action",
            ]
        ]
    )

    print("=" * 80)

    return {

        "portfolio_results":
            portfolio_df,

        "summary":
            summary,

        "portfolio_health_score":
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
        "previous_rating": "AA",
        "current_rating": "A",
    },

    {
        "borrower_id": "B1002",
        "previous_rating": "BBB",
        "current_rating": "BB",
    },

    {
        "borrower_id": "B1003",
        "previous_rating": "A",
        "current_rating": "A",
    },

    {
        "borrower_id": "B1004",
        "previous_rating": "BB",
        "current_rating": "CCC",
    },

    {
        "borrower_id": "B1005",
        "previous_rating": "AAA",
        "current_rating": "AA",
    },

])

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":

    run_migration_analysis(
        SAMPLE_PORTFOLIO
    )

    print("\n[KRONOS] MIGRATION TRACKER COMPLETED")

# =============================================================================
# END OF FILE
# =============================================================================