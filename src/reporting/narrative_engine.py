# =============================================================================
# KRONOS — NARRATIVE ENGINE
# File: src/reporting/narrative_engine.py
# =============================================================================

import pandas as pd
import numpy as np
from datetime import datetime

# =============================================================================
# ENTERPRISE RISK NARRATIVE
# =============================================================================

def enterprise_risk_narrative(
    enterprise_risk_score
):
    """
    Generate enterprise portfolio-risk commentary.
    """

    if enterprise_risk_score < 25:

        return (
            "KRONOS analysis indicates stable "
            "portfolio conditions with limited "
            "enterprise deterioration pressure."
        )

    elif enterprise_risk_score < 50:

        return (
            "KRONOS detected moderate enterprise "
            "risk escalation requiring enhanced "
            "portfolio monitoring and governance review."
        )

    elif enterprise_risk_score < 75:

        return (
            "KRONOS identified elevated enterprise "
            "stress conditions with material "
            "portfolio deterioration signals."
        )

    return (
        "KRONOS detected critical enterprise "
        "risk escalation with systemic portfolio "
        "instability and severe deterioration pressure."
    )

# =============================================================================
# SYSTEMIC RISK NARRATIVE
# =============================================================================

def systemic_risk_narrative(
    systemic_risk_score
):
    """
    Generate systemic-risk commentary.
    """

    if systemic_risk_score < 25:

        return (
            "Systemic exposure remains within "
            "acceptable enterprise thresholds."
        )

    elif systemic_risk_score < 50:

        return (
            "Elevated interconnected risk detected "
            "across selected portfolio segments."
        )

    elif systemic_risk_score < 75:

        return (
            "High systemic instability identified "
            "with contagion sensitivity increasing "
            "across interconnected exposures."
        )

    return (
        "Critical systemic fragility detected "
        "with elevated cascade-failure risk "
        "across the enterprise network."
    )

# =============================================================================
# CAPITAL ADEQUACY NARRATIVE
# =============================================================================

def capital_adequacy_narrative(
    capital_ratio
):
    """
    Generate capital-position commentary.
    """

    if capital_ratio >= 12:

        return (
            "Enterprise capital reserves remain "
            "strong with stable solvency conditions."
        )

    elif capital_ratio >= 10:

        return (
            "Capital adequacy remains acceptable "
            "but requires enhanced monitoring."
        )

    elif capital_ratio >= 8:

        return (
            "Stress pressure detected within "
            "capital reserves requiring mitigation planning."
        )

    return (
        "Critical capital deterioration identified "
        "with heightened solvency pressure."
    )

# =============================================================================
# REGIME NARRATIVE
# =============================================================================

def regime_narrative(
    regime_classification
):
    """
    Generate macroeconomic regime commentary.
    """

    regime_map = {

        "STABLE ECONOMIC REGIME":
            (
                "Macroeconomic conditions remain stable "
                "with controlled systemic pressure."
            ),

        "ELEVATED RISK REGIME":
            (
                "Moderate macroeconomic deterioration "
                "detected across enterprise indicators."
            ),

        "STRESSED ECONOMIC REGIME":
            (
                "High macroeconomic stress identified "
                "with elevated recession sensitivity."
            ),

        "SYSTEMIC CRISIS REGIME":
            (
                "Systemic crisis conditions detected "
                "with severe enterprise instability."
            ),
    }

    return regime_map.get(
        regime_classification,
        "Macroeconomic monitoring active."
    )

# =============================================================================
# EXECUTIVE ESCALATION NARRATIVE
# =============================================================================

def escalation_narrative(
    escalation_level
):
    """
    Generate governance-escalation commentary.
    """

    escalation_map = {

        "STANDARD MONITORING":
            (
                "No executive escalation required "
                "under current enterprise conditions."
            ),

        "ENTERPRISE RISK ESCALATION":
            (
                "Enterprise governance escalation "
                "recommended for portfolio review."
            ),

        "BOARD RISK COMMITTEE REVIEW":
            (
                "Board-level risk governance review "
                "recommended due to elevated instability."
            ),

        "EXECUTIVE CRISIS MANAGEMENT":
            (
                "Immediate executive crisis-management "
                "intervention required."
            ),
    }

    return escalation_map.get(
        escalation_level,
        "Governance monitoring active."
    )

# =============================================================================
# STRATEGIC RECOMMENDATION NARRATIVE
# =============================================================================

def strategic_recommendation_narrative(
    enterprise_risk_score,
    regime_classification=None,
    stress_score=None
):
    """
    Generate executive strategic recommendation.
    """

    recommendation_score = enterprise_risk_score

    if stress_score is not None:

        recommendation_score = max(
            recommendation_score,
            stress_score
        )

    if (
        regime_classification == "SYSTEMIC CRISIS REGIME"
        or recommendation_score >= 75
    ):

        return (
            "Activate enterprise crisis-management "
            "framework and systemic exposure reduction."
        )

    if recommendation_score < 25:

        return (
            "Maintain current enterprise strategy "
            "and continue standard portfolio governance."
        )

    elif recommendation_score < 50:

        return (
            "Increase monitoring intensity and "
            "review moderate-risk exposure segments."
        )

    elif recommendation_score < 75:

        return (
            "Implement enterprise mitigation strategy "
            "and strengthen governance controls."
        )

# =============================================================================
# AI EXPLAINABILITY NARRATIVE
# =============================================================================

def explainability_narrative(
    enterprise_risk_score,
    systemic_risk_score
):
    """
    Generate explainable AI commentary.
    """

    dominant_driver = max(
        enterprise_risk_score,
        systemic_risk_score
    )

    if dominant_driver == enterprise_risk_score:

        return (
            "Primary deterioration drivers originate "
            "from enterprise portfolio-risk escalation."
        )

    return (
        "Primary deterioration drivers originate "
        "from systemic interconnected-risk escalation."
    )

# =============================================================================
# BOARD-LEVEL SUMMARY
# =============================================================================

def board_level_summary(
    risk_narrative,
    systemic_narrative,
    capital_narrative
):
    """
    Generate executive board summary.
    """

    summary = (
        f"{risk_narrative} "
        f"{systemic_narrative} "
        f"{capital_narrative}"
    )

    return summary

# =============================================================================
# REPORT TIMESTAMP
# =============================================================================

def narrative_timestamp():
    """
    Generate executive-report timestamp.
    """

    return datetime.utcnow().strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )

# =============================================================================
# RUN NARRATIVE ENGINE
# =============================================================================

def run_narrative_engine(
    enterprise_risk_score,
    systemic_risk_score,
    capital_ratio,
    regime_classification,
    escalation_level,
    stress_score=None
):
    """
    Run executive AI narrative workflow.
    """

    print("\n" + "=" * 80)
    print("[KRONOS] RUNNING NARRATIVE ENGINE")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # EXECUTIVE NARRATIVES
    # -------------------------------------------------------------------------

    risk_narrative = enterprise_risk_narrative(
        enterprise_risk_score
    )

    systemic_narrative = systemic_risk_narrative(
        systemic_risk_score
    )

    capital_narrative = capital_adequacy_narrative(
        capital_ratio
    )

    macro_narrative = regime_narrative(
        regime_classification
    )

    escalation_commentary = escalation_narrative(
        escalation_level
    )

    strategy_narrative = (
        strategic_recommendation_narrative(
            enterprise_risk_score,
            regime_classification=regime_classification,
            stress_score=stress_score
        )
    )

    explainability = explainability_narrative(
        enterprise_risk_score,
        systemic_risk_score
    )

    board_summary = board_level_summary(
        risk_narrative,
        systemic_narrative,
        capital_narrative
    )

    timestamp = narrative_timestamp()

    # -------------------------------------------------------------------------
    # FINAL NARRATIVE PACKAGE
    # -------------------------------------------------------------------------

    narrative_results = {

        "enterprise_risk_narrative":
            risk_narrative,

        "systemic_risk_narrative":
            systemic_narrative,

        "capital_adequacy_narrative":
            capital_narrative,

        "macro_regime_narrative":
            macro_narrative,

        "executive_escalation_narrative":
            escalation_commentary,

        "strategic_recommendation":
            strategy_narrative,

        "ai_explainability_narrative":
            explainability,

        "board_level_summary":
            board_summary,

        "report_timestamp":
            timestamp,
    }

    # -------------------------------------------------------------------------
    # REPORTING
    # -------------------------------------------------------------------------

    print("\n[KRONOS] EXECUTIVE NARRATIVE SUMMARY\n")

    for key, value in narrative_results.items():

        print(f"\n{key}:\n{value}")

    print("\n" + "=" * 80)

    return narrative_results

# =============================================================================
# SAMPLE EXECUTION
# =============================================================================

ENTERPRISE_RISK_SCORE = 78

SYSTEMIC_RISK_SCORE = 82

CAPITAL_RATIO = 7.6

REGIME_CLASSIFICATION = (
    "SYSTEMIC CRISIS REGIME"
)

ESCALATION_LEVEL = (
    "EXECUTIVE CRISIS MANAGEMENT"
)

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":

    run_narrative_engine(
        enterprise_risk_score=ENTERPRISE_RISK_SCORE,
        systemic_risk_score=SYSTEMIC_RISK_SCORE,
        capital_ratio=CAPITAL_RATIO,
        regime_classification=REGIME_CLASSIFICATION,
        escalation_level=ESCALATION_LEVEL
    )

    print("\n[KRONOS] NARRATIVE ENGINE COMPLETED")

# =============================================================================
# END OF FILE
# =============================================================================
