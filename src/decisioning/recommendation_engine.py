# =============================================================================
# KRONOS — RECOMMENDATION ENGINE
# File: src/decisioning/recommendation_engine.py
# =============================================================================

import pandas as pd
import numpy as np

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

# =============================================================================
# MITIGATION STRATEGIES
# =============================================================================

def mitigation_strategy(
    risk_score
):
    """
    Generate enterprise mitigation strategy.
    """

    if risk_score < 25:

        return (
            "Maintain standard monitoring and "
            "continue normal portfolio servicing."
        )

    elif risk_score < 50:

        return (
            "Increase monitoring frequency and "
            "perform enhanced borrower review."
        )

    elif risk_score < 75:

        return (
            "Initiate risk mitigation program and "
            "apply exposure control measures."
        )

    return (
        "Activate crisis risk management and "
        "reduce portfolio exposure immediately."
    )

# =============================================================================
# RESERVE OPTIMIZATION
# =============================================================================

def reserve_optimization(
    reserve_pressure_score
):
    """
    Generate reserve optimization guidance.
    """

    if reserve_pressure_score < 20:

        return "Current reserve allocation remains adequate."

    elif reserve_pressure_score < 50:

        return (
            "Increase reserve buffers moderately "
            "to improve provisioning resilience."
        )

    elif reserve_pressure_score < 75:

        return (
            "Implement aggressive reserve "
            "strengthening strategy."
        )

    return (
        "Emergency reserve expansion required "
        "to absorb systemic deterioration."
    )

# =============================================================================
# CAPITAL PRESERVATION
# =============================================================================

def capital_preservation_strategy(
    systemic_risk_score
):
    """
    Generate capital protection strategy.
    """

    if systemic_risk_score < 25:

        return "Standard capital allocation permitted."

    elif systemic_risk_score < 50:

        return (
            "Adopt conservative capital allocation "
            "across sensitive exposures."
        )

    elif systemic_risk_score < 75:

        return (
            "Restrict high-risk lending and "
            "prioritize capital preservation."
        )

    return (
        "Activate enterprise capital defense "
        "and systemic exposure reduction."
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
# EXECUTIVE ACTION
# =============================================================================

def executive_action(
    risk_score
):
    """
    Generate executive governance recommendation.
    """

    if risk_score < 25:

        return "No executive intervention required."

    elif risk_score < 50:

        return (
            "Regional credit leadership review "
            "recommended."
        )

    elif risk_score < 75:

        return (
            "Enterprise risk committee escalation "
            "recommended."
        )

    return (
        "Immediate executive crisis-management "
        "intervention required."
    )

# =============================================================================
# EXPOSURE REDUCTION
# =============================================================================

def exposure_reduction_strategy(
    exposure
):
    """
    Generate exposure optimization guidance.
    """

    if exposure < 50000:

        return "Exposure concentration remains acceptable."

    elif exposure < 100000:

        return (
            "Monitor concentration and apply "
            "selective exposure controls."
        )

    elif exposure < 150000:

        return (
            "Reduce concentrated exposure and "
            "tighten portfolio allocation."
        )

    return (
        "Immediate exposure reduction required "
        "to control systemic concentration."
    )

# =============================================================================
# GOVERNANCE RECOMMENDATION
# =============================================================================

def governance_recommendation(
    policy_status
):
    """
    Generate governance escalation guidance.
    """

    if "COMPLIANT" in policy_status:

        return "Maintain standard governance workflow."

    elif "WATCHLIST" in policy_status:

        return (
            "Escalate to enhanced governance "
            "monitoring framework."
        )

    return (
        "Activate executive governance review "
        "and compliance escalation."
    )

# =============================================================================
# AI RECOMMENDATION CONFIDENCE
# =============================================================================

def recommendation_confidence(
    risk_score,
    systemic_risk_score
):
    """
    Estimate AI recommendation reliability.
    """

    confidence = (

        100
        - (
            abs(risk_score - 50)
            * 0.60
        )
        - (
            systemic_risk_score
            * 0.10
        )

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
# EXECUTIVE RECOMMENDATION NARRATIVE
# =============================================================================

def generate_recommendation_narrative(
    borrower_id,
    priority,
    executive_guidance
):
    """
    Generate executive AI recommendation narrative.
    """

    narrative = (
        f"Borrower {borrower_id} requires "
        f"{priority.lower()} with "
        f"recommended governance action: "
        f"{executive_guidance.lower()}"
    )

    return narrative

# =============================================================================
# RUN RECOMMENDATION ENGINE
# =============================================================================

def run_recommendation_engine(
    portfolio_df,
    live_context=None
):
    """
    Run enterprise AI recommendation workflow.
    """

    print("\n" + "=" * 80)
    print("[KRONOS] RUNNING RECOMMENDATION ENGINE")
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

    recommendation_results = []

    # -------------------------------------------------------------------------
    # RECOMMENDATION WORKFLOW
    # -------------------------------------------------------------------------

    for _, borrower in portfolio_df.iterrows():

        borrower_id = borrower["borrower_id"]

        risk_score = borrower.get(
            "aggregated_risk_score",
            35
        )

        base_risk_score = risk_score

        if live_context:

            risk_score = min(
                round(
                    risk_score * 0.75
                    + max(
                        live_macro_score,
                        live_market_score,
                        live_sentiment_stress,
                        live_enterprise_score
                    ) * 0.25,
                    2
                ),
                100
            )

        systemic_risk_score = borrower.get(
            "systemic_risk_score",
            30
        )

        reserve_pressure_score = borrower.get(
            "reserve_pressure_score",
            20
        )

        exposure = borrower.get(
            "ead",
            50000
        )

        policy_status = borrower.get(
            "policy_status",
            "POLICY COMPLIANT"
        )

        # ---------------------------------------------------------------------
        # STRATEGIC RECOMMENDATIONS
        # ---------------------------------------------------------------------

        mitigation = mitigation_strategy(
            risk_score
        )

        reserve_guidance = reserve_optimization(
            reserve_pressure_score
        )

        capital_strategy = (
            capital_preservation_strategy(
                systemic_risk_score
            )
        )

        priority = intervention_priority(
            risk_score
        )

        executive_guidance = executive_action(
            risk_score
        )

        exposure_strategy = (
            exposure_reduction_strategy(
                exposure
            )
        )

        governance_guidance = (
            governance_recommendation(
                policy_status
            )
        )

        confidence = recommendation_confidence(
            risk_score,
            systemic_risk_score
        )

        narrative = generate_recommendation_narrative(
            borrower_id,
            priority,
            executive_guidance
        )

        live_rationale = (
            "Recommendation includes live macro, market, and news intelligence context."
            if live_context
            else "Recommendation based on portfolio and governance inputs."
        )

        recommendation_results.append({

            "borrower_id":
                borrower_id,

            "mitigation_strategy":
                mitigation,

            "base_risk_score":
                base_risk_score,

            "contextual_risk_score":
                risk_score,

            "macro_stress_score":
                live_macro_score,

            "market_stress_score":
                live_market_score,

            "sentiment_stress_score":
                live_sentiment_stress,

            "reserve_optimization":
                reserve_guidance,

            "capital_preservation_strategy":
                capital_strategy,

            "intervention_priority":
                priority,

            "executive_action":
                executive_guidance,

            "exposure_reduction_strategy":
                exposure_strategy,

            "governance_recommendation":
                governance_guidance,

            "recommendation_confidence":
                confidence,

            "executive_narrative":
                narrative,

            "live_intelligence_rationale":
                live_rationale,
        })

    recommendation_df = pd.DataFrame(
        recommendation_results
    )

    # -------------------------------------------------------------------------
    # PORTFOLIO SUMMARY
    # -------------------------------------------------------------------------

    summary = {

        "critical_priority_accounts":
            int(
                (
                    recommendation_df[
                        "intervention_priority"
                    ]
                    == "CRITICAL PRIORITY"
                ).sum()
            ),

        "high_priority_accounts":
            int(
                (
                    recommendation_df[
                        "intervention_priority"
                    ]
                    == "HIGH PRIORITY"
                ).sum()
            ),

        "average_recommendation_confidence":
            round(
                float(
                    recommendation_df[
                        "recommendation_confidence"
                    ].mean()
                ),
                2
            ),

        "executive_escalations":
            int(
                (
                    recommendation_df[
                        "intervention_priority"
                    ]
                    == "CRITICAL PRIORITY"
                ).sum()
            ),

        "average_risk_score":
            round(
                float(
                    portfolio_df[
                        "aggregated_risk_score"
                    ].mean()
                ),
                2
            ),

        "maximum_risk_score":
            round(
                float(
                    portfolio_df[
                        "aggregated_risk_score"
                    ].max()
                ),
                2
            ),

        "policy_breach_accounts":
            int(
                (
                    portfolio_df.get(
                        "policy_status",
                        pd.Series(
                            ["POLICY COMPLIANT"] * len(portfolio_df),
                            index=portfolio_df.index,
                        )
                    )
                    .str.contains(
                        "BREACH",
                        na=False
                    )
                ).sum()
            ),

        "average_systemic_risk":
            round(
                float(
                    portfolio_df.get(
                        "systemic_risk_score",
                        pd.Series(
                            [30] * len(portfolio_df),
                            index=portfolio_df.index,
                        )
                    ).mean()
                ),
                2
            ),
    }

    # -------------------------------------------------------------------------
    # REPORTING
    # -------------------------------------------------------------------------

    print("\n[KRONOS] RECOMMENDATION SUMMARY\n")

    for key, value in summary.items():

        print(f"{key}: {value}")

    print("\n" + "-" * 80)

    print("\nAI RECOMMENDATION ANALYSIS\n")

    print(
        recommendation_df[
            [
                "borrower_id",
                "intervention_priority",
                "executive_action",
                "governance_recommendation",
                "recommendation_confidence",
            ]
        ]
    )

    print("=" * 80)

    return {

        "recommendation_results":
            recommendation_df,

        "summary":
            summary,
    }

# =============================================================================
# SAMPLE PORTFOLIO
# =============================================================================

SAMPLE_PORTFOLIO = pd.DataFrame([

    {
        "borrower_id": "B1001",
        "aggregated_risk_score": 18,
        "systemic_risk_score": 14,
        "reserve_pressure_score": 12,
        "ead": 24000,
        "policy_status": "POLICY COMPLIANT",
    },

    {
        "borrower_id": "B1002",
        "aggregated_risk_score": 48,
        "systemic_risk_score": 52,
        "reserve_pressure_score": 46,
        "ead": 92000,
        "policy_status": "POLICY WATCHLIST",
    },

    {
        "borrower_id": "B1003",
        "aggregated_risk_score": 91,
        "systemic_risk_score": 94,
        "reserve_pressure_score": 88,
        "ead": 210000,
        "policy_status": "POLICY BREACH",
    },

    {
        "borrower_id": "B1004",
        "aggregated_risk_score": 32,
        "systemic_risk_score": 28,
        "reserve_pressure_score": 24,
        "ead": 56000,
        "policy_status": "POLICY COMPLIANT",
    },

])

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":

    run_recommendation_engine(
        SAMPLE_PORTFOLIO
    )

    print("\n[KRONOS] RECOMMENDATION ENGINE COMPLETED")

# =============================================================================
# END OF FILE
# =============================================================================
