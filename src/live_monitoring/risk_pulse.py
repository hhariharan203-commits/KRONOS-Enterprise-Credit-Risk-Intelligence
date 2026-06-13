# =============================================================================
# KRONOS — LIVE RISK PULSE ENGINE
# File: src/live_monitoring/risk_pulse.py
# =============================================================================

import pandas as pd
import numpy as np
from datetime import datetime

# =============================================================================
# RISK PULSE THRESHOLDS
# =============================================================================

RISK_PULSE_THRESHOLDS = {

    "LOW": 25,
    "MODERATE": 50,
    "HIGH": 75,
    "CRITICAL": 90,
}

# =============================================================================
# LIVE PORTFOLIO RISK SCORE
# =============================================================================

def live_portfolio_risk_score(
    pd_score,
    systemic_risk_score,
    stress_score,
    reserve_pressure
):
    """
    Aggregate real-time enterprise risk signals.
    """

    pulse_score = (

        (pd_score * 100 * 0.35)
        + (systemic_risk_score * 0.25)
        + (stress_score * 0.25)
        + (reserve_pressure * 0.15)

    )

    return min(
        round(pulse_score, 2),
        100
    )

# =============================================================================
# SYSTEMIC DETERIORATION SIGNAL
# =============================================================================

def systemic_deterioration_signal(
    pulse_score
):
    """
    Detect systemic deterioration intensity.
    """

    if pulse_score < 25:

        return "STABLE CONDITIONS"

    elif pulse_score < 50:

        return "ELEVATED RISK CONDITIONS"

    elif pulse_score < 75:

        return "HIGH SYSTEMIC STRESS"

    return "CRITICAL SYSTEMIC DETERIORATION"

# =============================================================================
# LIVE RISK TREND
# =============================================================================

def risk_trend_signal(
    current_score,
    previous_score
):
    """
    Detect enterprise risk trend movement.
    """

    delta = current_score - previous_score

    if delta <= -10:

        return "RAPID IMPROVEMENT"

    elif delta < 0:

        return "IMPROVING CONDITIONS"

    elif delta < 10:

        return "STABLE RISK TREND"

    elif delta < 20:

        return "RISK ESCALATION"

    return "SEVERE RISK ESCALATION"

# =============================================================================
# PORTFOLIO HEALTH STATUS
# =============================================================================

def portfolio_health_status(
    pulse_score
):
    """
    Determine portfolio stability condition.
    """

    if pulse_score < 25:

        return "HEALTHY PORTFOLIO"

    elif pulse_score < 50:

        return "MODERATE PORTFOLIO RISK"

    elif pulse_score < 75:

        return "HIGH PORTFOLIO STRESS"

    return "CRITICAL PORTFOLIO INSTABILITY"

# =============================================================================
# EXECUTIVE ESCALATION LEVEL
# =============================================================================

def executive_escalation_level(
    pulse_score
):
    """
    Determine executive escalation severity.
    """

    if pulse_score < 25:

        return "NO ESCALATION REQUIRED"

    elif pulse_score < 50:

        return "REGIONAL RISK REVIEW"

    elif pulse_score < 75:

        return "ENTERPRISE RISK COMMITTEE"

    return "EXECUTIVE CRISIS ESCALATION"

# =============================================================================
# LIVE CAPITAL PRESSURE
# =============================================================================

def live_capital_pressure(
    stress_score,
    reserve_pressure
):
    """
    Estimate real-time capital pressure.
    """

    pressure = (
        (stress_score * 0.60)
        + (reserve_pressure * 0.40)
    )

    if pressure < 25:

        return "LOW CAPITAL PRESSURE"

    elif pressure < 50:

        return "MODERATE CAPITAL PRESSURE"

    elif pressure < 75:

        return "HIGH CAPITAL PRESSURE"

    return "CRITICAL CAPITAL DETERIORATION"

# =============================================================================
# ENTERPRISE RESILIENCE SCORE
# =============================================================================

def enterprise_resilience(
    pulse_score
):
    """
    Estimate enterprise resilience strength.
    """

    resilience = (
        100 - pulse_score
    )

    return max(
        round(resilience, 2),
        0
    )

# =============================================================================
# EXECUTIVE RISK NARRATIVE
# =============================================================================

def generate_risk_pulse_narrative(
    borrower_id,
    health_status,
    escalation
):
    """
    Generate executive live-risk commentary.
    """

    narrative = (
        f"Borrower {borrower_id} currently exhibits "
        f"{health_status.lower()} with "
        f"recommended escalation path: "
        f"{escalation.lower()}."
    )

    return narrative

# =============================================================================
# LIVE RISK TIMESTAMP
# =============================================================================

def current_timestamp():
    """
    Generate enterprise monitoring timestamp.
    """

    return datetime.utcnow().strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )

# =============================================================================
# RUN LIVE RISK PULSE
# =============================================================================

def run_risk_pulse_engine(
    portfolio_df
):
    """
    Run enterprise live-risk pulse workflow.
    """

    print("\n" + "=" * 80)
    print("[KRONOS] RUNNING LIVE RISK PULSE")
    print("=" * 80)

    portfolio_df = portfolio_df.copy()

    pulse_results = []

    # -------------------------------------------------------------------------
    # LIVE RISK ANALYSIS
    # -------------------------------------------------------------------------

    for _, borrower in portfolio_df.iterrows():

        borrower_id = borrower["borrower_id"]

        pd_score = borrower["pd_score"]

        systemic_risk_score = borrower.get(
            "systemic_risk_score",
            30
        )

        stress_score = borrower.get(
            "stress_score",
            25
        )

        reserve_pressure = borrower.get(
            "reserve_pressure_score",
            20
        )

        previous_pulse = borrower.get(
            "previous_pulse_score",
            35
        )

        # ---------------------------------------------------------------------
        # LIVE PULSE SCORE
        # ---------------------------------------------------------------------

        pulse_score = live_portfolio_risk_score(
            pd_score,
            systemic_risk_score,
            stress_score,
            reserve_pressure
        )

        deterioration = systemic_deterioration_signal(
            pulse_score
        )

        trend = risk_trend_signal(
            pulse_score,
            previous_pulse
        )

        health_status = portfolio_health_status(
            pulse_score
        )

        escalation = executive_escalation_level(
            pulse_score
        )

        capital_pressure = live_capital_pressure(
            stress_score,
            reserve_pressure
        )

        resilience = enterprise_resilience(
            pulse_score
        )

        narrative = generate_risk_pulse_narrative(
            borrower_id,
            health_status,
            escalation
        )

        timestamp = current_timestamp()

        pulse_results.append({

            "borrower_id":
                borrower_id,

            "live_risk_pulse_score":
                pulse_score,

            "systemic_risk_score":
                systemic_risk_score,

            "systemic_deterioration":
                deterioration,

            "risk_trend":
                trend,

            "portfolio_health":
                health_status,

            "executive_escalation":
                escalation,

            "capital_pressure":
                capital_pressure,

            "enterprise_resilience":
                resilience,

            "monitoring_timestamp":
                timestamp,

            "executive_narrative":
                narrative,
        })

    pulse_df = pd.DataFrame(
        pulse_results
    )

    # -------------------------------------------------------------------------
    # PORTFOLIO LIVE SUMMARY
    # -------------------------------------------------------------------------

    summary = {

        "average_live_risk_pulse":
            round(
                float(
                    pulse_df[
                        "live_risk_pulse_score"
                    ].mean()
                ),
                2
            ),

        "highest_live_risk":
            round(
                float(
                    pulse_df[
                        "live_risk_pulse_score"
                    ].max()
                ),
                2
            ),

        "lowest_live_risk":
            round(
                float(
                    pulse_df[
                        "live_risk_pulse_score"
                    ].min()
                ),
                2
            ),

        "critical_escalations":
            int(
                (
                    pulse_df[
                        "executive_escalation"
                    ]
                    == "EXECUTIVE CRISIS ESCALATION"
                ).sum()
            ),

        "high_risk_accounts":
            int(
                (
                    pulse_df[
                        "live_risk_pulse_score"
                    ] >= 75
                ).sum()
            ),

        "average_enterprise_resilience":
            round(
                float(
                    pulse_df[
                        "enterprise_resilience"
                    ].mean()
                ),
                2
            ),

        "maximum_resilience":
            round(
                float(
                    pulse_df[
                        "enterprise_resilience"
                    ].max()
                ),
                2
            ),

        "minimum_resilience":
            round(
                float(
                    pulse_df[
                        "enterprise_resilience"
                    ].min()
                ),
                2
            ),
    }

    # -------------------------------------------------------------------------
    # REPORTING
    # -------------------------------------------------------------------------

    print("\n[KRONOS] LIVE RISK PULSE SUMMARY\n")

    for key, value in summary.items():

        print(f"{key}: {value}")

    print("\n" + "-" * 80)

    print("\nLIVE RISK MONITORING\n")

    print(
        pulse_df[
            [
                "borrower_id",
                "live_risk_pulse_score",
                "systemic_deterioration",
                "risk_trend",
                "portfolio_health",
                "executive_escalation",
                "capital_pressure",
                "enterprise_resilience",
            ]
        ]
    )

    print("=" * 80)

    return {

        "risk_pulse_results":
            pulse_df,

        "summary":
            summary,
    }

# =============================================================================
# SAMPLE LIVE PORTFOLIO
# =============================================================================

SAMPLE_PORTFOLIO = pd.DataFrame([

    {
        "borrower_id": "B1001",
        "pd_score": 0.05,
        "systemic_risk_score": 18,
        "stress_score": 22,
        "reserve_pressure_score": 15,
        "previous_pulse_score": 28,
    },

    {
        "borrower_id": "B1002",
        "pd_score": 0.34,
        "systemic_risk_score": 52,
        "stress_score": 48,
        "reserve_pressure_score": 40,
        "previous_pulse_score": 46,
    },

    {
        "borrower_id": "B1003",
        "pd_score": 0.78,
        "systemic_risk_score": 92,
        "stress_score": 88,
        "reserve_pressure_score": 85,
        "previous_pulse_score": 70,
    },

    {
        "borrower_id": "B1004",
        "pd_score": 0.16,
        "systemic_risk_score": 30,
        "stress_score": 28,
        "reserve_pressure_score": 22,
        "previous_pulse_score": 34,
    },

])

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":

    run_risk_pulse_engine(
        SAMPLE_PORTFOLIO
    )

    print("\n[KRONOS] LIVE RISK PULSE COMPLETED")

# =============================================================================
# END OF FILE
# =============================================================================