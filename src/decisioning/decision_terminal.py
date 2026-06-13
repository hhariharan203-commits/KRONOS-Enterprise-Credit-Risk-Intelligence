# =============================================================================
# KRONOS — DECISION TERMINAL
# File: src/decisioning/decision_terminal.py
# =============================================================================

import pandas as pd
import numpy as np
from datetime import datetime
from hashlib import sha256

# =============================================================================
# RISK DECISION THRESHOLDS
# =============================================================================

DECISION_THRESHOLDS = {

    "APPROVE": 25,
    "REVIEW": 50,
    "WATCHLIST": 70,
    "REJECT": 85,
}

# =============================================================================
# AGGREGATED RISK SCORE
# =============================================================================

def aggregated_risk_score(
    pd_score,
    ews_score,
    systemic_risk_score,
    reserve_pressure_score
):
    """
    Aggregate enterprise risk indicators.
    """

    total_score = (

        (pd_score * 100 * 0.35)
        + (ews_score * 0.25)
        + (systemic_risk_score * 0.25)
        + (reserve_pressure_score * 0.15)

    )

    return min(
        round(total_score, 2),
        100
    )

# =============================================================================
# UNDERWRITING DECISION
# =============================================================================

def underwriting_decision(
    risk_score
):
    """
    Generate enterprise underwriting decision.
    """

    if risk_score < DECISION_THRESHOLDS["APPROVE"]:

        return "APPROVED"

    elif risk_score < DECISION_THRESHOLDS["REVIEW"]:

        return "MANUAL REVIEW"

    elif risk_score < DECISION_THRESHOLDS["WATCHLIST"]:

        return "WATCHLIST ESCALATION"

    elif risk_score < DECISION_THRESHOLDS["REJECT"]:

        return "ENHANCED MONITORING"

    else:

        return "REJECTED"

# =============================================================================
# GOVERNANCE ACTION
# =============================================================================

def governance_action(
    decision
):
    """
    Determine enterprise governance workflow.
    """

    actions = {

        "APPROVED":
            "Proceed with standard approval workflow",

        "MANUAL REVIEW":
            "Assign senior credit analyst review",

        "WATCHLIST ESCALATION":
            "Escalate to enterprise risk committee",

        "ENHANCED MONITORING":
            "Activate enhanced monitoring and risk controls",

        "REJECTED":
            "Decline exposure and activate risk controls",
    }

    return actions.get(
        decision,
        "Standard governance review"
    )

# =============================================================================
# INTERVENTION PRIORITY
# =============================================================================

def intervention_priority(
    risk_score
):
    """
    Determine intervention urgency.
    """

    if risk_score < 25:

        return "LOW PRIORITY"

    elif risk_score < 50:

        return "MODERATE PRIORITY"

    elif risk_score < 75:

        return "HIGH PRIORITY"

    return "CRITICAL PRIORITY"

# =============================================================================
# POLICY COMPLIANCE
# =============================================================================

def policy_compliance(
    pd_score,
    systemic_risk_score
):
    """
    Check enterprise risk-policy compliance.
    """

    if (
        pd_score >= 0.70
        or systemic_risk_score >= 80
    ):

        return "POLICY BREACH"

    elif (
        pd_score >= 0.50
        or systemic_risk_score >= 60
    ):

        return "POLICY WATCHLIST"

    return "POLICY COMPLIANT"

# =============================================================================
# CAPITAL ALLOCATION SIGNAL
# =============================================================================

def capital_allocation_signal(
    decision,
    reserve_pressure_score
):
    """
    Estimate capital allocation guidance.
    """

    if decision == "APPROVED":

        return "NORMAL CAPITAL ALLOCATION"

    elif decision == "MANUAL REVIEW":

        return "CONSERVATIVE CAPITAL ALLOCATION"

    elif decision == "WATCHLIST ESCALATION":

        return "RESTRICTED CAPITAL ALLOCATION"

    elif decision == "ENHANCED MONITORING":

        return (
            "ENHANCED CAPITAL MONITORING "
            "AND CONTROLLED ALLOCATION"
        )

    return "CAPITAL PRESERVATION MODE"

# =============================================================================
# EXECUTIVE DECISION NARRATIVE
# =============================================================================

def generate_decision_narrative(
    borrower_id,
    decision,
    governance_action_value
):
    """
    Generate executive decision commentary.
    """

    narrative = (
        f"Borrower {borrower_id} received "
        f"decision status '{decision}' with "
        f"governance directive: "
        f"{governance_action_value.lower()}."
    )

    return narrative

# =============================================================================
# DECISION CONFIDENCE
# =============================================================================

def decision_confidence(
    risk_score
):
    """
    Estimate AI decision confidence.
    """

    confidence = (
        100 - abs(50 - risk_score)
    )

    confidence = max(
        min(confidence, 100),
        0
    )

    return round(
        confidence,
        2
    )

# =============================================================================
# DECISION TRACEABILITY
# =============================================================================

def decision_rationale(
    pd_score,
    ews_score,
    systemic_risk_score,
    reserve_pressure_score,
    risk_score,
    policy_status,
    decision
):
    """
    Build an audit-friendly explanation without changing decision logic.
    """

    return {

        "decision_basis":
            (
                f"Decision {decision} was derived from aggregated risk "
                f"score {risk_score} and policy status {policy_status}."
            ),

        "risk_inputs":
            {
                "pd_score": round(float(pd_score), 4),
                "ews_score": round(float(ews_score), 2),
                "systemic_risk_score": round(float(systemic_risk_score), 2),
                "reserve_pressure_score": round(float(reserve_pressure_score), 2),
            },

        "weighting_model":
            {
                "pd_score": "35%",
                "ews_score": "25%",
                "systemic_risk_score": "25%",
                "reserve_pressure_score": "15%",
            },

        "policy_status":
            policy_status,
    }


def recommendation_traceability(
    decision,
    governance,
    priority,
    capital_signal
):
    """
    Connect the underwriting decision to downstream recommendations.
    """

    return {

        "underwriting_decision":
            decision,

        "governance_action":
            governance,

        "intervention_priority":
            priority,

        "capital_allocation_signal":
            capital_signal,
    }


def build_decision_audit_record(
    borrower_id,
    risk_score,
    decision,
    confidence,
    rationale,
    recommendation_trace
):
    """
    Build a durable decision record for audit review.
    """

    trace_basis = (
        f"{borrower_id}:{risk_score}:{decision}:{confidence}"
    )

    return {

        "decision_trace_id":
            sha256(
                trace_basis.encode("utf-8")
            ).hexdigest()[:16],

        "borrower_id":
            borrower_id,

        "decision_timestamp":
            datetime.utcnow().strftime(
                "%Y-%m-%d %H:%M:%S UTC"
            ),

        "aggregated_risk_score":
            risk_score,

        "underwriting_decision":
            decision,

        "decision_confidence":
            confidence,

        "decision_thresholds":
            DECISION_THRESHOLDS.copy(),

        "decision_rationale":
            rationale,

        "recommendation_trace":
            recommendation_trace,
    }

# =============================================================================
# RUN DECISION ANALYSIS
# =============================================================================

def run_decision_engine(
    portfolio_df
):
    """
    Run enterprise AI decision intelligence workflow.
    """

    print("\n" + "=" * 80)
    print("[KRONOS] RUNNING DECISION TERMINAL")
    print("=" * 80)

    portfolio_df = portfolio_df.copy()

    decision_results = []

    # -------------------------------------------------------------------------
    # DECISION WORKFLOW
    # -------------------------------------------------------------------------

    for _, borrower in portfolio_df.iterrows():

        borrower_id = borrower["borrower_id"]

        pd_score = borrower["pd_score"]

        ews_score = borrower.get(
            "early_warning_score",
            borrower.get("ews_score", 25)
        )

        systemic_risk_score = borrower.get(
            "systemic_risk_score",
            30
        )

        reserve_pressure_score = borrower.get(
            "reserve_pressure_score",
            20
        )

        # ---------------------------------------------------------------------
        # AGGREGATED RISK
        # ---------------------------------------------------------------------

        risk_score = aggregated_risk_score(
            pd_score,
            ews_score,
            systemic_risk_score,
            reserve_pressure_score
        )

        # ---------------------------------------------------------------------
        # DECISION ENGINE
        # ---------------------------------------------------------------------

        decision = underwriting_decision(
            risk_score
        )

        # ---------------------------------------------------------------------
        # POLICY OVERRIDE
        # ---------------------------------------------------------------------

        policy_status = policy_compliance(
            pd_score,
            systemic_risk_score
        )

        if (
            pd_score >= 0.85
            or systemic_risk_score >= 90
            or reserve_pressure_score >= 90
        ):

            decision = "REJECTED"

        # ---------------------------------------------------------------------
        # GOVERNANCE
        # ---------------------------------------------------------------------

        governance = governance_action(
            decision
        )

        priority = intervention_priority(
            risk_score
        )

        capital_signal = capital_allocation_signal(
            decision,
            reserve_pressure_score
        )

        confidence = decision_confidence(
            risk_score
        )

        narrative = generate_decision_narrative(
            borrower_id,
            decision,
            governance
        )

        rationale = decision_rationale(
            pd_score,
            ews_score,
            systemic_risk_score,
            reserve_pressure_score,
            risk_score,
            policy_status,
            decision
        )

        recommendation_trace = recommendation_traceability(
            decision,
            governance,
            priority,
            capital_signal
        )

        audit_record = build_decision_audit_record(
            borrower_id,
            risk_score,
            decision,
            confidence,
            rationale,
            recommendation_trace
        )

        decision_results.append({

            "borrower_id":
                borrower_id,

            "decision_trace_id":
                audit_record["decision_trace_id"],

            "aggregated_risk_score":
                risk_score,

            "underwriting_decision":
                decision,

            "governance_action":
                governance,

            "intervention_priority":
                priority,

            "policy_compliance":
                policy_status,

            "capital_allocation_signal":
                capital_signal,

            "decision_confidence":
                confidence,

            "executive_narrative":
                narrative,

            "decision_rationale":
                rationale,

            "recommendation_trace":
                recommendation_trace,

            "decision_audit_record":
                audit_record,
        })

    # -------------------------------------------------------------------------
    # CONVERT TO DATAFRAME
    # -------------------------------------------------------------------------

    decision_df = pd.DataFrame(
        decision_results
    )

    # -------------------------------------------------------------------------
    # PORTFOLIO SUMMARY
    # -------------------------------------------------------------------------
    
    summary = {

        "approved_accounts":
            int(
                (
                    decision_df[
                        "underwriting_decision"
                    ]
                    == "APPROVED"
                ).sum()
            ),

        "manual_review_accounts":
            int(
                (
                    decision_df[
                        "underwriting_decision"
                    ]
                    == "MANUAL REVIEW"
                ).sum()
            ),

        "watchlist_accounts":
            int(
                (
                    decision_df[
                        "underwriting_decision"
                    ]
                    == "WATCHLIST ESCALATION"
                ).sum()
            ),

        "enhanced_monitoring_accounts":
            int(
                (
                    decision_df[
                        "underwriting_decision"
                    ]
                    == "ENHANCED MONITORING"
                ).sum()
            ),

        "rejected_accounts":
            int(
                (
                    decision_df[
                        "underwriting_decision"
                    ]
                    == "REJECTED"
                ).sum()
            ),

        "average_risk_score":
            round(
                float(
                    decision_df[
                        "aggregated_risk_score"
                    ].mean()
                ),
                2
            ),

        "maximum_risk_score":
            round(
                float(
                    decision_df[
                        "aggregated_risk_score"
                    ].max()
                ),
                2
            ),

        "average_decision_confidence":
            round(
                float(
                    decision_df[
                        "decision_confidence"
                    ].mean()
                ),
                2
            ),
    }

    # -------------------------------------------------------------------------
    # REPORTING
    # -------------------------------------------------------------------------

    print("\n[KRONOS] DECISION TERMINAL SUMMARY\n")

    for key, value in summary.items():

        print(f"{key}: {value}")

    print("\n" + "-" * 80)

    print("\nDECISION ANALYSIS\n")

    print(
        decision_df[
            [
                "borrower_id",
                "aggregated_risk_score",
                "underwriting_decision",
                "governance_action",
                "policy_compliance",
                "capital_allocation_signal",
                "decision_confidence",
            ]
        ]
    )

    print("=" * 80)

    return {

        "decision_results":
            decision_df,

        "summary":
            summary,

        "decision_audit_records":
            decision_df[
                "decision_audit_record"
            ].tolist(),
    }

# =============================================================================
# SAMPLE PORTFOLIO
# =============================================================================

SAMPLE_PORTFOLIO = pd.DataFrame([

    {
        "borrower_id": "B1001",
        "pd_score": 0.04,
        "ews_score": 18,
        "systemic_risk_score": 15,
        "reserve_pressure_score": 10,
    },

    {
        "borrower_id": "B1002",
        "pd_score": 0.32,
        "ews_score": 52,
        "systemic_risk_score": 48,
        "reserve_pressure_score": 35,
    },

    {
        "borrower_id": "B1003",
        "pd_score": 0.74,
        "ews_score": 88,
        "systemic_risk_score": 91,
        "reserve_pressure_score": 82,
    },

    {
        "borrower_id": "B1004",
        "pd_score": 0.18,
        "ews_score": 34,
        "systemic_risk_score": 28,
        "reserve_pressure_score": 22,
    },

])

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":

    run_decision_engine(
        SAMPLE_PORTFOLIO
    )

    print("\n[KRONOS] DECISION TERMINAL COMPLETED")

# =============================================================================
# END OF FILE
# =============================================================================
