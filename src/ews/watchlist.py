# =============================================================================
# KRONOS — ENTERPRISE WATCHLIST ENGINE
# File: src/ews/watchlist.py
# =============================================================================

import pandas as pd
import numpy as np

# =============================================================================
# WATCHLIST CLASSIFICATION
# =============================================================================

def classify_watchlist_level(
    ews_score,
    anomaly_status,
    migration_direction,
    current_rating
):
    """
    Determine enterprise watchlist category.
    """

    # -------------------------------------------------------------------------
    # CRITICAL CONDITIONS
    # -------------------------------------------------------------------------

    if (
        ews_score >= 80
        or current_rating in ["CCC", "DEFAULT"]
    ):

        return "CRITICAL WATCHLIST"

    # -------------------------------------------------------------------------
    # HIGH RISK CONDITIONS
    # -------------------------------------------------------------------------

    if (
        ews_score >= 60
        or anomaly_status == "ANOMALOUS"
        or migration_direction == "DOWNGRADE"
    ):

        return "HIGH RISK WATCHLIST"

    # -------------------------------------------------------------------------
    # MODERATE CONDITIONS
    # -------------------------------------------------------------------------

    if ews_score >= 35:

        return "ENHANCED MONITORING"

    # -------------------------------------------------------------------------
    # LOW RISK
    # -------------------------------------------------------------------------

    return "STANDARD PORTFOLIO"

# =============================================================================
# PRIORITY SCORE
# =============================================================================

def calculate_priority_score(
    ews_score,
    migration_risk_score,
    anomaly_score
):
    """
    Calculate borrower escalation priority.
    """

    anomaly_component = abs(
        anomaly_score
    ) * 100

    priority_score = (
        (ews_score * 0.50)
        + (migration_risk_score * 0.30)
        + (anomaly_component * 0.20)
    )

    priority_score = min(
        round(priority_score, 2),
        100
    )

    return priority_score

# =============================================================================
# ESCALATION ACTIONS
# =============================================================================

def escalation_action(
    watchlist_level
):
    """
    Determine institutional intervention workflow.
    """

    actions = {

        "STANDARD PORTFOLIO":
            "Routine monitoring cycle",

        "ENHANCED MONITORING":
            "Increase review frequency and monitor deterioration trends",

        "HIGH RISK WATCHLIST":
            "Assign analyst review and initiate risk mitigation review",

        "CRITICAL WATCHLIST":
            "Immediate risk committee escalation and intervention planning",
    }

    return actions.get(
        watchlist_level,
        "Standard monitoring"
    )

# =============================================================================
# INTERVENTION CATEGORY
# =============================================================================

def intervention_category(
    watchlist_level
):
    """
    Determine borrower intervention intensity.
    """

    categories = {

        "STANDARD PORTFOLIO":
            "No intervention required",

        "ENHANCED MONITORING":
            "Preventive borrower engagement",

        "HIGH RISK WATCHLIST":
            "Risk mitigation intervention",

        "CRITICAL WATCHLIST":
            "Emergency restructuring review",
    }

    return categories.get(
        watchlist_level,
        "Standard review"
    )

# =============================================================================
# REVIEW FREQUENCY
# =============================================================================

def review_frequency(
    watchlist_level
):
    """
    Determine monitoring cycle.
    """

    mapping = {

        "STANDARD PORTFOLIO":
            "QUARTERLY",

        "ENHANCED MONITORING":
            "MONTHLY",

        "HIGH RISK WATCHLIST":
            "WEEKLY",

        "CRITICAL WATCHLIST":
            "DAILY",
    }

    return mapping.get(
        watchlist_level,
        "MONTHLY"
    )

# =============================================================================
# WATCHLIST NARRATIVE
# =============================================================================

def generate_watchlist_narrative(
    borrower_row,
    watchlist_level
):
    """
    Generate executive borrower monitoring narrative.
    """

    borrower_id = borrower_row.get(
        "borrower_id",
        "UNKNOWN"
    )

    if watchlist_level == "STANDARD PORTFOLIO":

        narrative = (
            f"Borrower {borrower_id} remains stable "
            "with limited deterioration indicators."
        )

    elif watchlist_level == "ENHANCED MONITORING":

        narrative = (
            f"Borrower {borrower_id} exhibits moderate "
            "deterioration requiring enhanced monitoring."
        )

    elif watchlist_level == "HIGH RISK WATCHLIST":

        narrative = (
            f"Borrower {borrower_id} demonstrates elevated "
            "risk signals requiring analyst escalation."
        )

    else:

        narrative = (
            f"Borrower {borrower_id} exhibits critical "
            "distress indicators requiring immediate intervention."
        )

    return narrative

# =============================================================================
# BUILD WATCHLIST
# =============================================================================

def build_watchlist(
    portfolio_df
):
    """
    Build enterprise borrower watchlist.
    """

    print("\n" + "=" * 80)
    print("[KRONOS] BUILDING ENTERPRISE WATCHLIST")
    print("=" * 80)

    portfolio_df = portfolio_df.copy()

    # -------------------------------------------------------------------------
    # WATCHLIST LEVELS
    # -------------------------------------------------------------------------

    portfolio_df["watchlist_level"] = (
        portfolio_df.apply(
            lambda row:
            classify_watchlist_level(
                row.get("ews_score", 0),
                row.get("anomaly_status", "NORMAL"),
                row.get("migration_direction", "STABLE"),
                row.get("current_rating", "A"),
            ),
            axis=1
        )
    )

    # -------------------------------------------------------------------------
    # PRIORITY SCORES
    # -------------------------------------------------------------------------

    portfolio_df["priority_score"] = (
        portfolio_df.apply(
            lambda row:
            calculate_priority_score(
                row.get("ews_score", 0),
                row.get("migration_risk_score", 0),
                row.get("anomaly_score", 0),
            ),
            axis=1
        )
    )

    # -------------------------------------------------------------------------
    # ESCALATION ACTIONS
    # -------------------------------------------------------------------------

    portfolio_df["escalation_action"] = (
        portfolio_df["watchlist_level"]
        .apply(escalation_action)
    )

   # -------------------------------------------------------------------------
    # INTERVENTION CATEGORIES
    # -------------------------------------------------------------------------

    portfolio_df["intervention_category"] = (
        portfolio_df["watchlist_level"]
        .apply(
            intervention_category
        )
    )

    # -------------------------------------------------------------------------
    # REVIEW FREQUENCY
    # -------------------------------------------------------------------------

    portfolio_df["review_frequency"] = (
        portfolio_df["watchlist_level"]
        .apply(
            review_frequency
        )
    )

    # -------------------------------------------------------------------------
    # EXECUTIVE NARRATIVES
    # -------------------------------------------------------------------------

    portfolio_df["executive_narrative"] = (
        portfolio_df.apply(
            lambda row:
            generate_watchlist_narrative(
                row,
                row["watchlist_level"],
            ),
            axis=1
        )
    )

    # -------------------------------------------------------------------------
    # SORT PRIORITY
    # -------------------------------------------------------------------------

    portfolio_df = portfolio_df.sort_values(
        by="priority_score",
        ascending=False
    )

    return portfolio_df

# =============================================================================
# WATCHLIST SUMMARY
# =============================================================================

def watchlist_summary(
    watchlist_df
):
    """
    Generate institutional watchlist statistics.
    """

    summary = (
        watchlist_df["watchlist_level"]
        .value_counts()
        .to_dict()
    )

    summary["total_accounts"] = len(
        watchlist_df
    )

    return summary

# =============================================================================
# PORTFOLIO WATCHLIST RISK INDEX
# =============================================================================

def portfolio_risk_index(
    watchlist_df
):
    """
    Portfolio risk concentration score.
    """

    avg_priority = (
        watchlist_df[
            "priority_score"
        ].mean()
    )

    return round(
        float(avg_priority),
        2
    )

# =============================================================================
# CRITICAL ACCOUNT QUEUE
# =============================================================================

def critical_account_queue(
    watchlist_df
):
    """
    Extract highest-risk borrower queue.
    """

    critical_df = watchlist_df[
        watchlist_df["watchlist_level"]
        .isin([
            "HIGH RISK WATCHLIST",
            "CRITICAL WATCHLIST",
        ])
    ]

    return critical_df[
        [
            "borrower_id",
            "watchlist_level",
            "priority_score",
            "review_frequency",
            "escalation_action",
            "intervention_category",
        ]
    ]

# =============================================================================
# FULL WATCHLIST PIPELINE
# =============================================================================

def run_watchlist_pipeline(
    portfolio_df
):
    """
    Run full enterprise watchlist workflow.
    """

    watchlist_df = build_watchlist(
        portfolio_df
    )

    summary = watchlist_summary(
        watchlist_df
    )

    risk_index = portfolio_risk_index(
        watchlist_df
    )

    critical_queue = critical_account_queue(
        watchlist_df
    )

    # -------------------------------------------------------------------------
    # REPORTING
    # -------------------------------------------------------------------------

    print("\n" + "=" * 80)
    print("[KRONOS] WATCHLIST SUMMARY")
    print("=" * 80)

    for key, value in summary.items():

        print(f"{key}: {value}")

    print(
        f"\nPortfolio Risk Index: "
        f"{risk_index}"
    )

    print("\n" + "-" * 80)

    print("\nCRITICAL ACCOUNT QUEUE\n")

    print(critical_queue)

    print("\n" + "-" * 80)

    print("\nFULL WATCHLIST\n")

    print(
        watchlist_df[
            [
                "borrower_id",
                "watchlist_level",
                "priority_score",
                "review_frequency",
                "escalation_action",
                "intervention_category",
            ]
        ]
    )

    print("=" * 80)

    return {

        "watchlist":
            watchlist_df,

        "summary":
            summary,

        "portfolio_risk_index":
            risk_index,

        "critical_queue":
            critical_queue,
    }

# =============================================================================
# SAMPLE PORTFOLIO
# =============================================================================

SAMPLE_PORTFOLIO = pd.DataFrame([

    {
        "borrower_id": "B1001",
        "ews_score": 22,
        "anomaly_status": "NORMAL",
        "migration_direction": "STABLE",
        "current_rating": "AA",
        "migration_risk_score": 0,
        "anomaly_score": 0.08,
    },

    {
        "borrower_id": "B1002",
        "ews_score": 74,
        "anomaly_status": "ANOMALOUS",
        "migration_direction": "DOWNGRADE",
        "current_rating": "BB",
        "migration_risk_score": 60,
        "anomaly_score": -0.06,
    },

    {
        "borrower_id": "B1003",
        "ews_score": 91,
        "anomaly_status": "ANOMALOUS",
        "migration_direction": "DOWNGRADE",
        "current_rating": "CCC",
        "migration_risk_score": 95,
        "anomaly_score": -0.12,
    },

])

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":

    run_watchlist_pipeline(
        SAMPLE_PORTFOLIO
    )

    print("\n[KRONOS] WATCHLIST ENGINE COMPLETED")

# =============================================================================
# END OF FILE
# =============================================================================