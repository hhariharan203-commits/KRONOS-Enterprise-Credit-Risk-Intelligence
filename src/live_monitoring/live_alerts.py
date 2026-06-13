# =============================================================================
# KRONOS — LIVE ALERT ENGINE
# File: src/live_monitoring/live_alerts.py
# =============================================================================

import pandas as pd
import numpy as np
from datetime import datetime

# =============================================================================
# ALERT THRESHOLDS
# =============================================================================

ALERT_THRESHOLDS = {

    "risk_pulse_critical": 85,
    "stress_critical": 80,
    "systemic_critical": 75,
    "reserve_critical": 70,
}

# =============================================================================
# LIVE INTELLIGENCE CONTEXT
# =============================================================================

def _live_summary(
    live_context
):
    if not live_context:
        return {}

    return live_context.get(
        "summary",
        {}
    )


def _live_score(
    live_context,
    key,
    default=0
):
    summary = _live_summary(
        live_context
    )

    return float(
        summary.get(
            key,
            default
        ) or default
    )


def _macro_intelligence(
    live_context
):
    if not live_context:
        return {}

    return live_context.get(
        "macro_intelligence",
        {}
    )


def executive_alert_level(
    alert_score
):
    """
    Convert a combined alert score into an executive level.
    """

    if alert_score < 25:

        return "INFORMATION"

    elif alert_score < 50:

        return "WARNING"

    elif alert_score < 75:

        return "HIGH RISK"

    elif alert_score < 90:

        return "CRITICAL"

    return "EXECUTIVE ACTION REQUIRED"


def condition_alert(
    condition_score,
    label
):
    """
    Generate a live external condition alert.
    """

    level = executive_alert_level(
        condition_score
    )

    return f"{label.upper()} {level}"


def yield_curve_alert(
    yield_curve_spread
):
    """
    Generate a yield-curve signal.
    """

    if yield_curve_spread is None:

        return "YIELD CURVE UNAVAILABLE"

    if yield_curve_spread < 0:

        return "YIELD CURVE INVERSION WARNING"

    if yield_curve_spread < 0.5:

        return "YIELD CURVE FLATTENING"

    return "YIELD CURVE NORMAL"

# =============================================================================
# ALERT PRIORITY
# =============================================================================

def alert_priority(
    risk_pulse
):
    """
    Determine enterprise alert severity.
    """

    if risk_pulse < 25:

        return "LOW PRIORITY ALERT"

    elif risk_pulse < 50:

        return "MODERATE PRIORITY ALERT"

    elif risk_pulse < 75:

        return "HIGH PRIORITY ALERT"

    return "CRITICAL PRIORITY ALERT"

# =============================================================================
# RISK DETERIORATION ALERT
# =============================================================================

def deterioration_alert(
    current_risk,
    previous_risk
):
    """
    Detect live deterioration movement.
    """

    delta = current_risk - previous_risk

    if delta < 5:

        return "NO MATERIAL DETERIORATION"

    elif delta < 15:

        return "EARLY RISK ESCALATION"

    elif delta < 30:

        return "SIGNIFICANT RISK DETERIORATION"

    return "SEVERE ENTERPRISE DETERIORATION"

# =============================================================================
# SYSTEMIC ALERT
# =============================================================================

def systemic_alert(
    systemic_risk_score
):
    """
    Generate systemic instability alert.
    """

    if systemic_risk_score < 25:

        return "STABLE SYSTEMIC CONDITIONS"

    elif systemic_risk_score < 50:

        return "ELEVATED SYSTEMIC RISK"

    elif systemic_risk_score < 75:

        return "HIGH SYSTEMIC INSTABILITY"

    return "CRITICAL SYSTEMIC ALERT"

# =============================================================================
# RESERVE BREACH ALERT
# =============================================================================

def reserve_breach_alert(
    reserve_pressure
):
    """
    Detect reserve deterioration pressure.
    """

    if reserve_pressure < 25:

        return "RESERVE POSITION STABLE"

    elif reserve_pressure < 50:

        return "MODERATE RESERVE PRESSURE"

    elif reserve_pressure < 75:

        return "HIGH RESERVE DETERIORATION"

    return "CRITICAL RESERVE BREACH"

# =============================================================================
# STRESS ESCALATION ALERT
# =============================================================================

def stress_escalation_alert(
    stress_score
):
    """
    Detect enterprise stress escalation.
    """

    if stress_score < 25:

        return "LOW STRESS CONDITIONS"

    elif stress_score < 50:

        return "MODERATE STRESS ESCALATION"

    elif stress_score < 75:

        return "HIGH STRESS ESCALATION"

    return "CRITICAL ENTERPRISE STRESS"

# =============================================================================
# EXECUTIVE ESCALATION
# =============================================================================

def executive_escalation(
    risk_pulse,
    systemic_risk
):
    """
    Trigger enterprise escalation workflow.
    """

    if (
        risk_pulse >= 92
        or systemic_risk >= 92
    ):

        return "EXECUTIVE CRISIS ESCALATION"

    elif (
        risk_pulse >= 80
        or systemic_risk >= 80
    ):

        return "ENTERPRISE RISK COMMITTEE"

    elif (
        risk_pulse >= 50
        or systemic_risk >= 50
    ):

        return "SENIOR RISK REVIEW"

    return "STANDARD MONITORING"

# =============================================================================
# GOVERNANCE BREACH DETECTION
# =============================================================================

def governance_breach(
    reserve_pressure,
    systemic_risk,
    stress_score
):
    """
    Detect institutional governance violations.
    """

    breaches = []

    if reserve_pressure >= 85:

        breaches.append(
            "RESERVE GOVERNANCE BREACH"
        )

    if systemic_risk >= 90:

        breaches.append(
            "SYSTEMIC GOVERNANCE BREACH"
        )

    if stress_score >= 90:

        breaches.append(
            "STRESS GOVERNANCE BREACH"
        )

    if len(breaches) == 0:

        return "NO GOVERNANCE BREACH"

    return " | ".join(breaches)

# =============================================================================
# ALERT CONFIDENCE
# =============================================================================

def alert_confidence(
    risk_pulse,
    systemic_risk
):
    """
    Estimate live-alert confidence.
    """

    confidence = (

        100
        - abs(risk_pulse - systemic_risk)
        * 0.50

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
# ALERT TIMESTAMP
# =============================================================================

def alert_timestamp():
    """
    Generate live enterprise timestamp.
    """

    return datetime.utcnow().strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )

# =============================================================================
# EXECUTIVE ALERT NARRATIVE
# =============================================================================

def generate_alert_narrative(
    borrower_id,
    escalation,
    deterioration
):
    """
    Generate executive alert commentary.
    """

    narrative = (
        f"Borrower {borrower_id} triggered "
        f"{deterioration.lower()} with "
        f"escalation status: "
        f"{escalation.lower()}."
    )

    return narrative

# =============================================================================
# RUN LIVE ALERT ENGINE
# =============================================================================

def run_live_alert_engine(
    portfolio_df,
    live_context=None
):
    """
    Run enterprise real-time alert workflow.
    """

    print("\n" + "=" * 80)
    print("[KRONOS] RUNNING LIVE ALERT ENGINE")
    print("=" * 80)

    portfolio_df = portfolio_df.copy()

    live_macro_score = _live_score(
        live_context,
        "macro_stress_score"
    )

    live_market_score = _live_score(
        live_context,
        "market_stress_score"
    )

    live_sentiment_stress = _live_score(
        live_context,
        "sentiment_stress_score"
    )

    live_enterprise_score = _live_score(
        live_context,
        "enterprise_live_risk_score"
    )

    yield_curve_spread = _macro_intelligence(
        live_context
    ).get(
        "yield_curve_spread"
    )

    alert_results = []

    # -------------------------------------------------------------------------
    # LIVE ALERT ANALYSIS
    # -------------------------------------------------------------------------

    for _, borrower in portfolio_df.iterrows():

        borrower_id = borrower["borrower_id"]

        risk_pulse = borrower.get(
            "live_risk_pulse_score",
            35
        )

        previous_risk = borrower.get(
            "previous_risk_score",
            30
        )

        systemic_risk = borrower.get(
            "systemic_risk_score",
            25
        )

        reserve_pressure = borrower.get(
            "reserve_pressure_score",
            20
        )

        stress_score = borrower.get(
            "stress_score",
            25
        )

        if live_context:

            stress_score = max(
                stress_score,
                live_macro_score,
                live_market_score,
                live_sentiment_stress
            )

        # ---------------------------------------------------------------------
        # ALERT GENERATION
        # ---------------------------------------------------------------------

        priority = alert_priority(
            risk_pulse
        )

        deterioration = deterioration_alert(
            risk_pulse,
            previous_risk
        )

        systemic_status = systemic_alert(
            systemic_risk
        )

        reserve_alert = reserve_breach_alert(
            reserve_pressure
        )

        stress_alert = stress_escalation_alert(
            stress_score
        )

        escalation = executive_escalation(
            risk_pulse,
            systemic_risk
        )

        governance_status = governance_breach(
            reserve_pressure,
            systemic_risk,
            stress_score
        )

        combined_alert_score = max(
            risk_pulse,
            systemic_risk,
            stress_score,
            live_enterprise_score if live_context else 0
        )

        macro_alert = condition_alert(
            live_macro_score,
            "Macro"
        )

        market_alert = condition_alert(
            live_market_score,
            "Market"
        )

        news_alert = condition_alert(
            live_sentiment_stress,
            "News Sentiment"
        )

        curve_alert = yield_curve_alert(
            yield_curve_spread
        )

        confidence = alert_confidence(
            risk_pulse,
            systemic_risk
        )

        timestamp = alert_timestamp()

        narrative = generate_alert_narrative(
            borrower_id,
            escalation,
            deterioration
        )

        alert_results.append({

            "borrower_id":
                borrower_id,

            "alert_priority":
                priority,

            "risk_deterioration":
                deterioration,

            "systemic_alert":
                systemic_status,

            "reserve_alert":
                reserve_alert,

            "stress_alert":
                stress_alert,

            "macro_deterioration_alert":
                macro_alert,

            "market_stress_alert":
                market_alert,

            "negative_news_sentiment_alert":
                news_alert,

            "yield_curve_alert":
                curve_alert,

            "executive_alert_level":
                executive_alert_level(
                    combined_alert_score
                ),

            "executive_escalation":
                escalation,

            "governance_breach":
                governance_status,

            "alert_confidence":
                confidence,

            "alert_timestamp":
                timestamp,

            "executive_narrative":
                narrative,
        })

    alert_df = pd.DataFrame(
        alert_results
    )

    # -------------------------------------------------------------------------
    # PORTFOLIO ALERT SUMMARY
    # -------------------------------------------------------------------------

    summary = {

        "critical_priority_alerts":
            int(
                (
                    alert_df[
                        "alert_priority"
                    ]
                    == "CRITICAL PRIORITY ALERT"
                ).sum()
            ),

        "high_priority_alerts":
            int(
                (
                    alert_df[
                        "alert_priority"
                    ]
                    == "HIGH PRIORITY ALERT"
                ).sum()
            ),

        "executive_crisis_escalations":
            int(
                (
                    alert_df[
                        "executive_escalation"
                    ]
                    == "EXECUTIVE CRISIS ESCALATION"
                ).sum()
            ),

        "governance_breaches":
            int(
                (
                    alert_df[
                        "governance_breach"
                    ]
                    != "NO GOVERNANCE BREACH"
                ).sum()
            ),

        "average_alert_confidence":
            round(
                float(
                    alert_df[
                        "alert_confidence"
                    ].mean()
                ),
                2
            ),

        "maximum_alert_confidence":
            round(
                float(
                    alert_df[
                        "alert_confidence"
                    ].max()
                ),
                2
            ),

        "minimum_alert_confidence":
            round(
                float(
                    alert_df[
                        "alert_confidence"
                    ].min()
                ),
                2
            ),

        "systemic_alert_accounts":
            int(
                (
                    alert_df[
                        "systemic_alert"
                    ]
                    == "CRITICAL SYSTEMIC ALERT"
                ).sum()
            ),

        "executive_action_required_alerts":
            int(
                (
                    alert_df[
                        "executive_alert_level"
                    ]
                    == "EXECUTIVE ACTION REQUIRED"
                ).sum()
            ),

        "average_live_macro_stress":
            round(
                float(live_macro_score),
                2
            ),

        "average_live_market_stress":
            round(
                float(live_market_score),
                2
            ),
    }

    # -------------------------------------------------------------------------
    # REPORTING
    # -------------------------------------------------------------------------

    print("\n[KRONOS] LIVE ALERT SUMMARY\n")

    for key, value in summary.items():

        print(f"{key}: {value}")

    print("\n" + "-" * 80)

    print("\nLIVE ALERT ANALYSIS\n")

    print(
        alert_df[
            [
                "borrower_id",
                "alert_priority",
                "risk_deterioration",
                "systemic_alert",
                "stress_alert",
                "executive_escalation",
                "governance_breach",
                "alert_confidence",
            ]
        ]
    )

    print("=" * 80)

    return {

        "live_alert_results":
            alert_df,

        "summary":
            summary,
    }

# =============================================================================
# SAMPLE LIVE MONITORING DATA
# =============================================================================

SAMPLE_PORTFOLIO = pd.DataFrame([

    {
        "borrower_id": "B1001",
        "live_risk_pulse_score": 22,
        "previous_risk_score": 18,
        "systemic_risk_score": 20,
        "reserve_pressure_score": 15,
        "stress_score": 18,
    },

    {
        "borrower_id": "B1002",
        "live_risk_pulse_score": 58,
        "previous_risk_score": 42,
        "systemic_risk_score": 55,
        "reserve_pressure_score": 48,
        "stress_score": 52,
    },

    {
        "borrower_id": "B1003",
        "live_risk_pulse_score": 94,
        "previous_risk_score": 70,
        "systemic_risk_score": 92,
        "reserve_pressure_score": 88,
        "stress_score": 90,
    },

    {
        "borrower_id": "B1004",
        "live_risk_pulse_score": 38,
        "previous_risk_score": 35,
        "systemic_risk_score": 30,
        "reserve_pressure_score": 24,
        "stress_score": 28,
    },

])

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":

    run_live_alert_engine(
        SAMPLE_PORTFOLIO
    )

    print("\n[KRONOS] LIVE ALERT ENGINE COMPLETED")

# =============================================================================
# END OF FILE
# =============================================================================
