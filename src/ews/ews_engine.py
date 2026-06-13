# =============================================================================
# KRONOS — EARLY WARNING SYSTEM (EWS) ENGINE
# File: src/ews/ews_engine.py
# =============================================================================

import pandas as pd
import numpy as np

# =============================================================================
# DETERIORATION VELOCITY
# =============================================================================

def calculate_deterioration_velocity(
    current_pd,
    previous_pd
):
    """
    Calculate borrower deterioration velocity.
    """

    velocity = current_pd - previous_pd

    return round(
        float(velocity),
        4
    )

# =============================================================================
# DELINQUENCY STRESS SCORE
# =============================================================================

def delinquency_stress_score(
    total_delinquency,
    high_delinquency_flag
):
    """
    Calculate delinquency severity score.
    """

    score = (
        (total_delinquency * 15)
        + (high_delinquency_flag * 25)
    )

    return min(
        round(score, 2),
        100
    )

# =============================================================================
# UTILIZATION STRESS SCORE
# =============================================================================

def utilization_stress_score(
    credit_utilization
):
    """
    Calculate utilization pressure score.
    """

    utilization_pct = (
        credit_utilization * 100
    )

    if utilization_pct < 30:

        return 10

    elif utilization_pct < 60:

        return 35

    elif utilization_pct < 85:

        return 70

    else:

        return 95

# =============================================================================
# PAYMENT BURDEN SCORE
# =============================================================================

def payment_burden_score(
    payment_burden_ratio
):
    """
    Evaluate affordability pressure.
    """

    burden_pct = (
        payment_burden_ratio * 100
    )

    if burden_pct < 20:

        return 10

    elif burden_pct < 35:

        return 40

    elif burden_pct < 50:

        return 75

    else:

        return 95

# =============================================================================
# COMPOSITE EWS SCORE
# =============================================================================

def calculate_ews_score(
    borrower_data
):
    """
    Calculate overall borrower deterioration score.
    """

    # -------------------------------------------------------------------------
    # INPUTS
    # -------------------------------------------------------------------------

    current_pd = borrower_data.get(
        "current_pd",
        0.10
    )

    previous_pd = borrower_data.get(
        "previous_pd",
        0.08
    )

    total_delinquency = borrower_data.get(
        "total_delinquency",
        0
    )

    high_delinquency_flag = borrower_data.get(
        "high_delinquency_flag",
        0
    )

    credit_utilization = borrower_data.get(
        "credit_utilization",
        0.30
    )

    payment_burden_ratio = borrower_data.get(
        "payment_burden_ratio",
        0.20
    )

    # -------------------------------------------------------------------------
    # COMPONENT SCORES
    # -------------------------------------------------------------------------

    velocity = calculate_deterioration_velocity(
        current_pd,
        previous_pd
    )

    velocity_score = min(
        abs(velocity) * 500,
        100
    )

    delinquency_score = delinquency_stress_score(
        total_delinquency,
        high_delinquency_flag
    )

    utilization_score = utilization_stress_score(
        credit_utilization
    )

    affordability_score = payment_burden_score(
        payment_burden_ratio
    )

    # -------------------------------------------------------------------------
    # WEIGHTED COMPOSITE
    # -------------------------------------------------------------------------

    ews_score = (
        (velocity_score * 0.35)
        + (delinquency_score * 0.30)
        + (utilization_score * 0.20)
        + (affordability_score * 0.15)
    )

    ews_score = min(
        round(ews_score, 2),
        100
    )

    # -------------------------------------------------------------------------
    # COMPONENT BREAKDOWN
    # -------------------------------------------------------------------------

    components = {
        "velocity_score":
            round(velocity_score, 2),

        "delinquency_score":
            round(delinquency_score, 2),

        "utilization_score":
            round(utilization_score, 2),

        "affordability_score":
            round(affordability_score, 2),
    }

    return (
        ews_score,
        components
    )

# =============================================================================
# TRAFFIC LIGHT CLASSIFICATION
# =============================================================================

def classify_ews_alert(
    ews_score
):
    """
    Classify borrower deterioration severity.
    """

    if ews_score < 30:

        return "GREEN"

    elif ews_score < 60:

        return "AMBER"

    elif ews_score < 80:

        return "RED"

    else:

        return "CRITICAL"

# =============================================================================
# EWS RISK GRADE
# =============================================================================

def ews_risk_grade(
    ews_score
):
    """
    Institutional EWS risk grade.
    """

    if ews_score < 20:

        return "A"

    elif ews_score < 40:

        return "B"

    elif ews_score < 60:

        return "C"

    elif ews_score < 80:

        return "D"

    else:

        return "E"

# =============================================================================
# WATCHLIST PRIORITY
# =============================================================================

def watchlist_priority(
    ews_score
):
    """
    Determine monitoring intensity.
    """

    if ews_score < 30:

        return "STANDARD MONITORING"

    elif ews_score < 60:

        return "ENHANCED MONITORING"

    elif ews_score < 80:

        return "WATCHLIST REVIEW"

    else:

        return "IMMEDIATE RISK ESCALATION"

# =============================================================================
# ESCALATION ACTION
# =============================================================================

def escalation_action(
    ews_score
):
    """
    Risk intervention recommendation.
    """

    if ews_score < 30:

        return "NO ACTION"

    elif ews_score < 60:

        return "INCREASE MONITORING"

    elif ews_score < 80:

        return "WATCHLIST ESCALATION"

    else:

        return "IMMEDIATE CREDIT REVIEW"

# =============================================================================
# DETERIORATION TREND
# =============================================================================

def deterioration_trend(
    current_pd,
    previous_pd
):
    """
    Identify borrower risk trend.
    """

    delta = current_pd - previous_pd

    if delta < -0.03:

        return "IMPROVING"

    elif delta < 0.03:

        return "STABLE"

    elif delta < 0.10:

        return "DETERIORATING"

    else:

        return "RAPID DETERIORATION"

# =============================================================================
# EWS EXECUTIVE NARRATIVE
# =============================================================================

def generate_ews_narrative(
    ews_score,
    alert_level,
    trend
):
    """
    Generate executive deterioration summary.
    """

    if alert_level == "GREEN":

        narrative = (
            "Borrower remains financially stable with "
            "limited deterioration risk signals."
        )

    elif alert_level == "AMBER":

        narrative = (
            "Borrower exhibits moderate deterioration "
            "requiring enhanced monitoring."
        )

    elif alert_level == "RED":

        narrative = (
            "Borrower demonstrates elevated deterioration "
            "risk requiring watchlist escalation."
        )

    else:

        narrative = (
            "Borrower exhibits severe distress signals "
            "requiring immediate risk intervention."
        )

    narrative += f" Current trend classification: {trend}."

    return narrative

# =============================================================================
# MAIN EWS ENGINE
# =============================================================================

def run_ews_engine(
    borrower_data
):
    """
    Run full enterprise EWS workflow.
    """

    print("\n" + "=" * 80)
    print("[KRONOS] RUNNING EARLY WARNING SYSTEM")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # EWS SCORE
    # -------------------------------------------------------------------------

    (
        ews_score,
        components
    ) = calculate_ews_score(
        borrower_data
    )

    # -------------------------------------------------------------------------
    # CLASSIFICATIONS
    # -------------------------------------------------------------------------

    alert_level = classify_ews_alert(
        ews_score
    )

    monitoring_priority = watchlist_priority(
        ews_score
    )

    risk_grade = ews_risk_grade(
        ews_score
    )

    recommended_action = escalation_action(
        ews_score
    )

    trend = deterioration_trend(
        borrower_data.get(
            "current_pd",
            0.10
        ),
        borrower_data.get(
            "previous_pd",
            0.08
        ),
    )

    narrative = generate_ews_narrative(
        ews_score,
        alert_level,
        trend
    )

    # -------------------------------------------------------------------------
    # FINAL RESULT
    # -------------------------------------------------------------------------

    result = {

        "ews_score":
            ews_score,

        "risk_grade":
            risk_grade,

        "alert_level":
            alert_level,

        "monitoring_priority":
            monitoring_priority,

        "recommended_action":
            recommended_action,

        "trend":
            trend,

        "component_breakdown":
            components,

        "executive_narrative":
            narrative,
    }

    # -------------------------------------------------------------------------
    # REPORTING
    # -------------------------------------------------------------------------

    print("\n[KRONOS] EWS ANALYSIS")

    for key, value in result.items():

        print(f"{key}: {value}")

    print("=" * 80)

    return result

# =============================================================================
# SAMPLE BORROWER
# =============================================================================

SAMPLE_BORROWER = {
    "current_pd": 0.28,
    "previous_pd": 0.12,
    "credit_utilization": 0.87,
    "payment_burden_ratio": 0.44,
    "total_delinquency": 3,
    "high_delinquency_flag": 1,
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":

    run_ews_engine(
        SAMPLE_BORROWER
    )

    print("\n[KRONOS] EWS ENGINE COMPLETED")

# =============================================================================
# END OF FILE
# =============================================================================