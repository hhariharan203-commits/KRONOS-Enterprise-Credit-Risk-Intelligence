# =============================================================================
# KRONOS — REGIME DETECTOR
# File: src/live_monitoring/regime_detector.py
# =============================================================================

import pandas as pd
import numpy as np
from datetime import datetime

# =============================================================================
# MACRO REGIME THRESHOLDS
# =============================================================================

REGIME_THRESHOLDS = {

    "STABLE": 25,
    "ELEVATED": 50,
    "STRESSED": 75,
    "CRISIS": 90,
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


def executive_cycle_regime(
    regime_score
):
    """
    Classify the enterprise credit cycle regime.
    """

    if regime_score < 15:

        return "EXPANSION"

    elif regime_score < 35:

        return "NORMAL"

    elif regime_score < 55:

        return "SLOWDOWN"

    elif regime_score < 75:

        return "RISK-OFF"

    elif regime_score < 90:

        return "STRESS"

    return "CRISIS"

# =============================================================================
# REGIME SCORE
# =============================================================================

def macro_regime_score(
    gdp_stress,
    inflation_stress,
    unemployment_stress,
    market_volatility
):
    """
    Aggregate macroeconomic regime stress.
    """

    gdp_component = min(
        abs(gdp_stress) * 10,
        100
    )

    inflation_component = min(
        inflation_stress * 8,
        100
    )

    unemployment_component = min(
        unemployment_stress * 8,
        100
    )

    volatility_component = min(
        market_volatility,
        100
    )

    regime_score = (

        gdp_component * 0.30
        + inflation_component * 0.20
        + unemployment_component * 0.25
        + volatility_component * 0.25

    )

    return min(
        round(
            regime_score,
            2
        ),
        100
    )

# =============================================================================
# REGIME CLASSIFICATION
# =============================================================================

def regime_classification(
    regime_score
):
    """
    Classify enterprise macro regime.
    """

    if regime_score < 25:

        return "STABLE ECONOMIC REGIME"

    elif regime_score < 50:

        return "ELEVATED RISK REGIME"

    elif regime_score < 75:

        return "STRESSED ECONOMIC REGIME"

    return "SYSTEMIC CRISIS REGIME"

# =============================================================================
# REGIME TRANSITION
# =============================================================================

def regime_transition(
    current_score,
    previous_score
):
    """
    Detect macroeconomic regime transition.
    """

    delta = current_score - previous_score

    if delta <= -15:

        return "STRONG REGIME RECOVERY"

    elif delta < 0:

        return "GRADUAL REGIME IMPROVEMENT"

    elif delta < 10:

        return "STABLE REGIME CONDITIONS"

    elif delta < 25:

        return "RISK REGIME ESCALATION"

    return "SEVERE REGIME DETERIORATION"

# =============================================================================
# SYSTEMIC ENVIRONMENT
# =============================================================================

def systemic_environment(
    regime_score
):
    """
    Determine enterprise systemic environment.
    """

    if regime_score < 25:

        return "LOW SYSTEMIC PRESSURE"

    elif regime_score < 50:

        return "MODERATE SYSTEMIC PRESSURE"

    elif regime_score < 75:

        return "HIGH SYSTEMIC PRESSURE"

    return "CRITICAL SYSTEMIC PRESSURE"

# =============================================================================
# MARKET STABILITY
# =============================================================================

def market_stability(
    market_volatility
):
    """
    Determine financial-market stability.
    """

    if market_volatility < 20:

        return "STABLE MARKET CONDITIONS"

    elif market_volatility < 40:

        return "ELEVATED MARKET VOLATILITY"

    elif market_volatility < 70:

        return "HIGH MARKET INSTABILITY"

    return "SYSTEMIC MARKET DISLOCATION"

# =============================================================================
# RECESSION PROBABILITY
# =============================================================================

def recession_probability(
    regime_score
):
    """
    Estimate macroeconomic recession probability.
    """

    probability = (
        regime_score / 100
    )

    return round(
        probability,
        4
    )

# =============================================================================
# ENTERPRISE RESILIENCE
# =============================================================================

def enterprise_resilience(
    regime_score
):
    """
    Estimate resilience against macro deterioration.
    """

    resilience = (
        100 - regime_score
    )

    return max(
        round(resilience, 2),
        0
    )

# =============================================================================
# REGIME ESCALATION
# =============================================================================

def regime_escalation(
    regime_score
):
    """
    Trigger executive macro escalation.
    """

    if regime_score < 25:

        return "STANDARD MONITORING"

    elif regime_score < 50:

        return "MACRO RISK REVIEW"

    elif regime_score < 75:

        return "ENTERPRISE RISK ESCALATION"

    return "EXECUTIVE CRISIS MANAGEMENT"

# =============================================================================
# REGIME CONFIDENCE
# =============================================================================

def regime_confidence(
    regime_score,
    volatility
):
    """
    Estimate regime classification confidence.
    """

    confidence = (

        100
        - abs(regime_score - volatility)
        * 0.40

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
# EXECUTIVE REGIME NARRATIVE
# =============================================================================

def generate_regime_narrative(
    regime,
    transition,
    escalation
):
    """
    Generate executive macro-regime commentary.
    """

    narrative = (
        f"KRONOS detected {regime.lower()} with "
        f"{transition.lower()} requiring "
        f"{escalation.lower()}."
    )

    return narrative

# =============================================================================
# REGIME TIMESTAMP
# =============================================================================

def regime_timestamp():
    """
    Generate live macro-monitoring timestamp.
    """

    return datetime.utcnow().strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )

# =============================================================================
# RUN REGIME DETECTOR
# =============================================================================

def run_regime_detector(
    macro_df,
    live_context=None
):
    """
    Run enterprise macro-regime intelligence workflow.
    """

    print("\n" + "=" * 80)
    print("[KRONOS] RUNNING REGIME DETECTOR")
    print("=" * 80)

    macro_df = macro_df.copy()

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

    regime_results = []

    # -------------------------------------------------------------------------
    # REGIME ANALYSIS
    # -------------------------------------------------------------------------

    for _, row in macro_df.iterrows():

        period = row["period"]

        gdp_stress = row.get(
            "gdp_stress",
            -1.5
        )

        inflation_stress = row.get(
            "inflation_stress",
            2.5
        )

        unemployment_stress = row.get(
            "unemployment_stress",
            3.0
        )

        market_volatility = row.get(
            "market_volatility",
            25
        )

        previous_regime_score = row.get(
            "previous_regime_score",
            35
        )

        # ---------------------------------------------------------------------
        # REGIME SCORE
        # ---------------------------------------------------------------------

        base_regime_score = macro_regime_score(
            gdp_stress,
            inflation_stress,
            unemployment_stress,
            market_volatility
        )

        credit_conditions_score = float(
            row.get(
                "credit_stress_score",
                row.get(
                    "enterprise_risk_score",
                    live_enterprise_score
                )
            )
            or 0
        )

        if live_context:

            regime_score = min(
                round(
                    base_regime_score * 0.40
                    + live_macro_score * 0.25
                    + live_market_score * 0.15
                    + live_sentiment_stress * 0.10
                    + credit_conditions_score * 0.10,
                    2
                ),
                100
            )

        else:

            regime_score = base_regime_score

        regime = regime_classification(
            regime_score
        )

        executive_regime = executive_cycle_regime(
            regime_score
        )

        transition = regime_transition(
            regime_score,
            previous_regime_score
        )

        environment = systemic_environment(
            regime_score
        )

        market_state = market_stability(
            market_volatility
        )

        recession_risk = recession_probability(
            regime_score
        )

        resilience = enterprise_resilience(
            regime_score
        )

        escalation = regime_escalation(
            regime_score
        )

        confidence = regime_confidence(
            regime_score,
            market_volatility
        )

        timestamp = regime_timestamp()

        narrative = generate_regime_narrative(
            regime,
            transition,
            escalation
        )

        regime_results.append({

            "period":
                period,

            "macro_regime_score":
                regime_score,

            "base_macro_regime_score":
                base_regime_score,

            "macro_conditions_score":
                live_macro_score,

            "market_conditions_score":
                live_market_score,

            "sentiment_conditions_score":
                live_sentiment_stress,

            "credit_conditions_score":
                credit_conditions_score,

            "regime_classification":
                regime,

            "executive_cycle_regime":
                executive_regime,

            "regime_transition":
                transition,

            "systemic_environment":
                environment,

            "market_stability":
                market_state,

            "recession_probability":
                recession_risk,

            "enterprise_resilience":
                resilience,

            "executive_escalation":
                escalation,

            "regime_confidence":
                confidence,

            "monitoring_timestamp":
                timestamp,

            "executive_narrative":
                narrative,
        })

    regime_df = pd.DataFrame(
        regime_results
    )

    # -------------------------------------------------------------------------
    # PORTFOLIO REGIME SUMMARY
    # -------------------------------------------------------------------------

    summary = {

        "average_regime_score":
            round(
                float(
                    regime_df[
                        "macro_regime_score"
                    ].mean()
                ),
                2
            ),

        "highest_regime_score":
            round(
                float(
                    regime_df[
                        "macro_regime_score"
                    ].max()
                ),
                2
            ),

        "lowest_regime_score":
            round(
                float(
                    regime_df[
                        "macro_regime_score"
                    ].min()
                ),
                2
            ),

        "average_recession_probability":
            round(
                float(
                    regime_df[
                        "recession_probability"
                    ].mean()
                ),
                4
            ),

        "maximum_recession_probability":
            round(
                float(
                    regime_df[
                        "recession_probability"
                    ].max()
                ),
                4
            ),

        "crisis_regime_periods":
            int(
                (
                    regime_df[
                        "regime_classification"
                    ]
                    == "SYSTEMIC CRISIS REGIME"
                ).sum()
            ),

        "stressed_regime_periods":
            int(
                (
                    regime_df[
                        "regime_classification"
                    ]
                    == "STRESSED ECONOMIC REGIME"
                ).sum()
            ),

        "executive_crisis_escalations":
            int(
                (
                    regime_df[
                        "executive_escalation"
                    ]
                    == "EXECUTIVE CRISIS MANAGEMENT"
                ).sum()
            ),

        "average_enterprise_resilience":
            round(
                float(
                    regime_df[
                        "enterprise_resilience"
                    ].mean()
                ),
                2
            ),

        "average_regime_confidence":
            round(
                float(
                    regime_df[
                        "regime_confidence"
                    ].mean()
                ),
                2
            ),

        "dominant_executive_cycle_regime":
            (
                regime_df[
                    "executive_cycle_regime"
                ]
                .mode()
                .iloc[0]
                if not regime_df.empty
                else "UNAVAILABLE"
            ),
    }

    # -------------------------------------------------------------------------
    # REPORTING
    # -------------------------------------------------------------------------

    print("\n[KRONOS] REGIME DETECTOR SUMMARY\n")

    for key, value in summary.items():

        print(f"{key}: {value}")

    print("\n" + "-" * 80)

    print("\nMACRO REGIME ANALYSIS\n")

    print(
        regime_df[
            [
                "period",
                "macro_regime_score",
                "regime_classification",
                "regime_transition",
                "systemic_environment",
                "market_stability",
                "recession_probability",
                "executive_escalation",
                "regime_confidence",
            ]
        ]
    )

    print("=" * 80)

    return {

        "regime_results":
            regime_df,

        "summary":
            summary,
    }

# =============================================================================
# SAMPLE MACRO DATA
# =============================================================================

SAMPLE_MACRO_DATA = pd.DataFrame([

    {
        "period": "2026-Q1",
        "gdp_stress": -1.2,
        "inflation_stress": 2.5,
        "unemployment_stress": 3.2,
        "market_volatility": 18,
        "previous_regime_score": 20,
    },

    {
        "period": "2026-Q2",
        "gdp_stress": -3.8,
        "inflation_stress": 5.6,
        "unemployment_stress": 6.5,
        "market_volatility": 48,
        "previous_regime_score": 42,
    },

    {
        "period": "2026-Q3",
        "gdp_stress": -7.5,
        "inflation_stress": 8.8,
        "unemployment_stress": 10.2,
        "market_volatility": 86,
        "previous_regime_score": 68,
    },

    {
        "period": "2026-Q4",
        "gdp_stress": -2.0,
        "inflation_stress": 3.1,
        "unemployment_stress": 4.0,
        "market_volatility": 28,
        "previous_regime_score": 38,
    },

])

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":

    run_regime_detector(
        SAMPLE_MACRO_DATA
    )

    print("\n[KRONOS] REGIME DETECTOR COMPLETED")

# =============================================================================
# END OF FILE
# =============================================================================
