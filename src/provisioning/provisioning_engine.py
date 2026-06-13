# =============================================================================
# KRONOS — IFRS9 PROVISIONING ENGINE
# File: src/provisioning/provisioning_engine.py
# =============================================================================

import pandas as pd
import numpy as np

# =============================================================================
# IFRS9 STAGE CLASSIFICATION
# =============================================================================

def classify_ifrs9_stage(
    pd_score,
    ews_score,
    delinquency_count,
    current_rating
):
    """
    Assign IFRS9 impairment stage.
    """

    # -------------------------------------------------------------------------
    # STAGE 3 — CREDIT IMPAIRED
    # -------------------------------------------------------------------------

    if (
        pd_score >= 0.50
        or delinquency_count >= 4
        or current_rating in ["CCC", "DEFAULT"]
    ):

        return "STAGE 3"

    # -------------------------------------------------------------------------
    # STAGE 2 — SIGNIFICANT RISK INCREASE
    # -------------------------------------------------------------------------

    elif (
        pd_score >= 0.20
        or ews_score >= 60
        or delinquency_count >= 2
    ):

        return "STAGE 2"

    # -------------------------------------------------------------------------
    # STAGE 1 — PERFORMING
    # -------------------------------------------------------------------------

    return "STAGE 1"

# =============================================================================
# PROVISIONING HORIZON
# =============================================================================

def provisioning_horizon(
    stage
):
    """
    Determine IFRS9 loss horizon.
    """

    horizons = {

        "STAGE 1":
            "12-MONTH ECL",

        "STAGE 2":
            "LIFETIME ECL",

        "STAGE 3":
            "LIFETIME ECL",
    }

    return horizons.get(
        stage,
        "UNKNOWN"
    )

# =============================================================================
# IMPAIRMENT SEVERITY
# =============================================================================

def impairment_severity(
    stage,
    ecl_value
):
    """
    Classify reserve severity.
    """

    if stage == "STAGE 1":

        return "LOW IMPAIRMENT"

    elif stage == "STAGE 2":

        if ecl_value < 10000:

            return "MODERATE IMPAIRMENT"

        return "HIGH IMPAIRMENT"

    else:

        return "SEVERE IMPAIRMENT"

# =============================================================================
# RESERVE RISK GRADE
# =============================================================================

def reserve_risk_grade(
    stage
):
    """
    IFRS9 reserve grade.
    """

    mapping = {

        "STAGE 1": "A",

        "STAGE 2": "B",

        "STAGE 3": "C",
    }

    return mapping.get(
        stage,
        "UNKNOWN"
    )

# =============================================================================
# CALCULATE EXPECTED CREDIT LOSS
# =============================================================================

def calculate_ecl(
    pd_score,
    lgd,
    ead,
    stage
):
    """
    Calculate IFRS9 Expected Credit Loss.
    """

    if stage == "STAGE 1":

        horizon_factor = 1.0

    elif stage == "STAGE 2":

        horizon_factor = 1.5

    else:

        horizon_factor = 2.0

    ecl = (
        pd_score
        * lgd
        * ead
        * horizon_factor
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
# COVERAGE BAND
# =============================================================================

def coverage_band(
    coverage_ratio
):
    """
    Coverage quality classification.
    """

    if coverage_ratio < 5:

        return "LOW COVERAGE"

    elif coverage_ratio < 15:

        return "MODERATE COVERAGE"

    elif coverage_ratio < 30:

        return "HIGH COVERAGE"

    else:

        return "SEVERE COVERAGE"

# =============================================================================
# PROVISIONING ACTION
# =============================================================================

def provisioning_action(
    stage,
    impairment
):
    """
    Determine institutional reserve action.
    """

    if stage == "STAGE 1":

        return (
            "Maintain performing reserve coverage"
        )

    elif stage == "STAGE 2":

        return (
            "Increase reserve allocation and "
            "enhance borrower monitoring"
        )

    return (
        "Escalate impairment review and "
        "initiate recovery strategy"
    )

# =============================================================================
# EXECUTIVE PROVISIONING NARRATIVE
# =============================================================================

def generate_provisioning_narrative(
    borrower_id,
    stage,
    ecl
):
    """
    Generate executive reserve narrative.
    """

    if stage == "STAGE 1":

        narrative = (
            f"Borrower {borrower_id} remains within "
            "performing portfolio thresholds with "
            "limited reserve pressure."
        )

    elif stage == "STAGE 2":

        narrative = (
            f"Borrower {borrower_id} demonstrates "
            "significant risk deterioration requiring "
            "lifetime expected loss provisioning."
        )

    else:

        narrative = (
            f"Borrower {borrower_id} is classified as "
            "credit-impaired requiring elevated reserve "
            "coverage and recovery intervention."
        )

    narrative += f" Estimated ECL: ${ecl:,.2f}."

    return narrative

# =============================================================================
# MAIN PROVISIONING ENGINE
# =============================================================================

def run_provisioning_engine(
    borrower_data
):
    """
    Run enterprise IFRS9 provisioning workflow.
    """

    print("\n" + "=" * 80)
    print("[KRONOS] RUNNING IFRS9 PROVISIONING ENGINE")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # INPUTS
    # -------------------------------------------------------------------------

    borrower_id = borrower_data.get(
        "borrower_id",
        "UNKNOWN"
    )

    pd_score = borrower_data.get(
        "pd_score",
        0.05
    )

    lgd = borrower_data.get(
        "lgd",
        0.30
    )

    ead = borrower_data.get(
        "ead",
        10000
    )

    ews_score = borrower_data.get(
        "ews_score",
        20
    )

    delinquency_count = borrower_data.get(
        "total_delinquency",
        0
    )

    current_rating = borrower_data.get(
        "current_rating",
        "A"
    )

    # -------------------------------------------------------------------------
    # IFRS9 STAGE
    # -------------------------------------------------------------------------

    stage = classify_ifrs9_stage(
        pd_score,
        ews_score,
        delinquency_count,
        current_rating
    )

    # -------------------------------------------------------------------------
    # ECL CALCULATION
    # -------------------------------------------------------------------------

    ecl = calculate_ecl(
        pd_score,
        lgd,
        ead,
        stage
    )

    # -------------------------------------------------------------------------
    # RESERVE ANALYTICS
    # -------------------------------------------------------------------------

    horizon = provisioning_horizon(
        stage
    )

    impairment = impairment_severity(
        stage,
        ecl
    )

    coverage_ratio = reserve_coverage_ratio(
        ecl,
        ead
    )

    coverage_class = coverage_band(
        coverage_ratio
    )

    reserve_grade = reserve_risk_grade(
        stage
    )

    action = provisioning_action(
        stage,
        impairment
    )

    narrative = generate_provisioning_narrative(
        borrower_id,
        stage,
        ecl
    )

    # -------------------------------------------------------------------------
    # FINAL RESULT
    # -------------------------------------------------------------------------

    result = {

        "borrower_id":
            borrower_id,

        "ifrs9_stage":
            stage,

        "provisioning_horizon":
            horizon,

        "expected_credit_loss":
            ecl,

        "reserve_coverage_ratio":
            coverage_ratio,

        "coverage_band":
            coverage_class,

        "reserve_risk_grade":
            reserve_grade,

        "impairment_severity":
            impairment,

        "recommended_action":
            action,

        "executive_narrative":
            narrative,
    }

    # -------------------------------------------------------------------------
    # REPORTING
    # -------------------------------------------------------------------------

    print("\n[KRONOS] PROVISIONING ANALYSIS\n")

    for key, value in result.items():

        print(f"{key}: {value}")

    print("=" * 80)

    return result

# =============================================================================
# SAMPLE BORROWER
# =============================================================================

SAMPLE_BORROWER = {

    "borrower_id": "B1002",

    "pd_score": 0.34,

    "lgd": 0.58,

    "ead": 42000,

    "ews_score": 71,

    "total_delinquency": 3,

    "current_rating": "BB",
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":

    run_provisioning_engine(
        SAMPLE_BORROWER
    )

    print("\n[KRONOS] PROVISIONING ENGINE COMPLETED")

# =============================================================================
# END OF FILE
# =============================================================================