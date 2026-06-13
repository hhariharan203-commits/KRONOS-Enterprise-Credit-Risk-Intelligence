# =============================================================================
# KRONOS — POLICY RULES ENGINE
# File: src/decisioning/policy_rules.py
# =============================================================================

import pandas as pd
import numpy as np

# =============================================================================
# ENTERPRISE POLICY LIMITS
# =============================================================================

POLICY_LIMITS = {

    "max_pd_score": 0.85,
    "max_systemic_risk": 90,
    "max_reserve_pressure": 90,
    "max_ead": 200000,
}

# =============================================================================
# PD POLICY VALIDATION
# =============================================================================

def validate_pd_policy(
    pd_score
):
    """
    Validate borrower PD threshold.
    """

    if pd_score > POLICY_LIMITS["max_pd_score"]:

        return "PD POLICY BREACH"

    elif pd_score > 0.70:

        return "PD POLICY WATCHLIST"

    return "PD POLICY COMPLIANT"

# =============================================================================
# SYSTEMIC RISK VALIDATION
# =============================================================================

def validate_systemic_risk(
    systemic_risk_score
):
    """
    Validate systemic exposure threshold.
    """

    if systemic_risk_score > POLICY_LIMITS[
        "max_systemic_risk"
    ]:

        return "SYSTEMIC RISK BREACH"

    elif systemic_risk_score > 75:

        return "SYSTEMIC WATCHLIST"

    return "SYSTEMIC COMPLIANT"

# =============================================================================
# RESERVE PRESSURE VALIDATION
# =============================================================================

def validate_reserve_pressure(
    reserve_pressure_score
):
    """
    Validate reserve adequacy threshold.
    """

    if reserve_pressure_score > POLICY_LIMITS[
        "max_reserve_pressure"
    ]:

        return "RESERVE BREACH"

    elif reserve_pressure_score > 75:

        return "RESERVE WATCHLIST"

    return "RESERVE COMPLIANT"

# =============================================================================
# EXPOSURE LIMIT VALIDATION
# =============================================================================

def validate_exposure_limit(
    exposure
):
    """
    Validate exposure concentration threshold.
    """

    if exposure > POLICY_LIMITS["max_ead"]:

        return "EXPOSURE LIMIT BREACH"

    elif exposure > 100000:

        return "EXPOSURE WATCHLIST"

    return "EXPOSURE COMPLIANT"

# =============================================================================
# GOVERNANCE ESCALATION
# =============================================================================

def governance_escalation(
    violations
):
    """
    Determine enterprise escalation workflow.
    """

    violation_count = len(violations)

    if violation_count == 0:

        return "STANDARD APPROVAL WORKFLOW"

    elif violation_count == 1:

        return "SENIOR ANALYST REVIEW"

    elif violation_count == 2:

        return "RISK COMMITTEE ESCALATION"

    return "EXECUTIVE GOVERNANCE ESCALATION"

# =============================================================================
# POLICY BREACH SEVERITY
# =============================================================================

def breach_severity(
    violation_count
):
    """
    Classify governance breach severity.
    """

    if violation_count == 0:

        return "NO POLICY BREACH"

    elif violation_count == 1:

        return "LOW GOVERNANCE RISK"

    elif violation_count == 2:

        return "HIGH GOVERNANCE RISK"

    return "CRITICAL GOVERNANCE BREACH"

# =============================================================================
# APPROVAL ELIGIBILITY
# =============================================================================

def approval_eligibility(
    violation_count
):
    """
    Determine underwriting eligibility.
    """

    if violation_count == 0:

        return "AUTO APPROVAL ELIGIBLE"

    elif violation_count == 1:

        return "MANUAL REVIEW REQUIRED"

    elif violation_count == 2:

        return "RESTRICTED APPROVAL"
    
    elif violation_count >= 3:
   
        return "APPROVAL DENIED"

# =============================================================================
# POLICY ALIGNMENT SCORE
# =============================================================================

def policy_alignment_score(
    violation_count
):
    """
    Calculate enterprise policy alignment.
    """

    alignment = (
        100 - (violation_count * 25)
    )

    return max(
        alignment,
        0
    )

# =============================================================================
# AI GOVERNANCE CONFIDENCE
# =============================================================================

def governance_confidence(
    alignment_score
):
    """
    Estimate governance reliability.
    """

    confidence = (
        alignment_score * 0.95
    )

    return round(
        confidence,
        2
    )

# =============================================================================
# EXECUTIVE POLICY NARRATIVE
# =============================================================================

def generate_policy_narrative(
    borrower_id,
    escalation,
    severity
):
    """
    Generate executive governance commentary.
    """

    narrative = (
        f"Borrower {borrower_id} triggered "
        f"{severity.lower()} with "
        f"governance workflow: "
        f"{escalation.lower()}."
    )

    return narrative

# =============================================================================
# RUN POLICY ENGINE
# =============================================================================

def run_policy_engine(
    portfolio_df
):
    """
    Run enterprise policy governance workflow.
    """

    print("\n" + "=" * 80)
    print("[KRONOS] RUNNING POLICY RULES ENGINE")
    print("=" * 80)

    portfolio_df = portfolio_df.copy()

    policy_results = []

    # -------------------------------------------------------------------------
    # POLICY VALIDATION
    # -------------------------------------------------------------------------

    for _, borrower in portfolio_df.iterrows():

        borrower_id = borrower["borrower_id"]

        pd_score = borrower["pd_score"]

        systemic_risk = borrower.get(
            "systemic_risk_score",
            30
        )

        reserve_pressure = borrower.get(
            "reserve_pressure_score",
            20
        )

        exposure = borrower.get(
            "ead",
            50000
        )

        # ---------------------------------------------------------------------
        # POLICY CHECKS
        # ---------------------------------------------------------------------

        pd_validation = validate_pd_policy(
            pd_score
        )

        systemic_validation = (
            validate_systemic_risk(
                systemic_risk
            )
        )

        reserve_validation = (
            validate_reserve_pressure(
                reserve_pressure
            )
        )

        exposure_validation = (
            validate_exposure_limit(
                exposure
            )
        )

        # ---------------------------------------------------------------------
        # BREACH DETECTION
        # ---------------------------------------------------------------------

        violations = []

        validations = [

            pd_validation,
            systemic_validation,
            reserve_validation,
            exposure_validation,
        ]

        for validation in validations:

            if "BREACH" in validation:

                violations.append(
                    validation
                )

        violation_count = len(
            violations
        )

        # ---------------------------------------------------------------------
        # GOVERNANCE LOGIC
        # ---------------------------------------------------------------------

        escalation = governance_escalation(
            violations
        )

        severity = breach_severity(
            violation_count
        )

        approval_status = approval_eligibility(
            violation_count
        )

        alignment_score = (
            policy_alignment_score(
                violation_count
            )
        )

        confidence = governance_confidence(
            alignment_score
        )

        narrative = generate_policy_narrative(
            borrower_id,
            escalation,
            severity
        )

        policy_results.append({

            "borrower_id":
                borrower_id,

            "pd_policy_status":
                pd_validation,

            "systemic_policy_status":
                systemic_validation,

            "reserve_policy_status":
                reserve_validation,

            "exposure_policy_status":
                exposure_validation,

            "violation_count":
                violation_count,

            "governance_escalation":
                escalation,

            "breach_severity":
                severity,

            "approval_eligibility":
                approval_status,

            "policy_alignment_score":
                alignment_score,

            "governance_confidence":
                confidence,

            "executive_narrative":
                narrative,
        })

    policy_df = pd.DataFrame(
        policy_results
    )

    # -------------------------------------------------------------------------
    # PORTFOLIO SUMMARY
    # -------------------------------------------------------------------------

    summary = {

        "total_policy_breaches":
            int(
                (
                    policy_df[
                        "violation_count"
                    ] > 0
                ).sum()
            ),

        "critical_governance_breaches":
            int(
                (
                    policy_df[
                        "breach_severity"
                    ]
                    == "CRITICAL GOVERNANCE BREACH"
                ).sum()
            ),

        "average_policy_alignment":
            round(
                float(
                    policy_df[
                        "policy_alignment_score"
                    ].mean()
                ),
                2
            ),

        "average_governance_confidence":
            round(
                float(
                    policy_df[
                        "governance_confidence"
                    ].mean()
                ),
                2
            ),

        "approval_denials":
            int(
                (
                    policy_df[
                        "approval_eligibility"
                    ]
                    == "APPROVAL DENIED"
                ).sum()
            ),

        "manual_reviews":
            int(
                (
                    policy_df[
                        "approval_eligibility"
                    ]
                    == "MANUAL REVIEW REQUIRED"
                ).sum()
            ),

        "average_violation_count":
            round(
                float(
                    policy_df[
                        "violation_count"
                    ].mean()
                ),
                2
            ),

        "maximum_violation_count":
            int(
                policy_df[
                    "violation_count"
                ].max()
            ),
    }

    # -------------------------------------------------------------------------
    # REPORTING
    # -------------------------------------------------------------------------

    print("\n[KRONOS] POLICY GOVERNANCE SUMMARY\n")

    for key, value in summary.items():

        print(f"{key}: {value}")

    print("\n" + "-" * 80)

    print("\nPOLICY VALIDATION ANALYSIS\n")

    print(
        policy_df[
            [
                "borrower_id",
                "violation_count",
                "governance_escalation",
                "breach_severity",
                "approval_eligibility",
                "policy_alignment_score",
                "governance_confidence",
            ]
        ]
    )

    print("=" * 80)

    return {

        "policy_results":
            policy_df,

        "summary":
            summary,
    }

# =============================================================================
# SAMPLE PORTFOLIO
# =============================================================================

SAMPLE_PORTFOLIO = pd.DataFrame([

    {
        "borrower_id": "B1001",
        "pd_score": 0.04,
        "systemic_risk_score": 18,
        "reserve_pressure_score": 12,
        "ead": 24000,
    },

    {
        "borrower_id": "B1002",
        "pd_score": 0.36,
        "systemic_risk_score": 58,
        "reserve_pressure_score": 46,
        "ead": 92000,
    },

    {
        "borrower_id": "B1003",
        "pd_score": 0.82,
        "systemic_risk_score": 91,
        "reserve_pressure_score": 88,
        "ead": 180000,
    },

    {
        "borrower_id": "B1004",
        "pd_score": 0.22,
        "systemic_risk_score": 32,
        "reserve_pressure_score": 24,
        "ead": 54000,
    },

])

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":

    run_policy_engine(
        SAMPLE_PORTFOLIO
    )

    print("\n[KRONOS] POLICY RULES ENGINE COMPLETED")

# =============================================================================
# END OF FILE
# =============================================================================