# =============================================================================
# KRONOS — CONDITIONAL VALUE AT RISK (CVaR) ENGINE
# File: src/stress_testing/cvar_engine.py
# =============================================================================

import pandas as pd
import numpy as np

from scipy.stats import norm

# =============================================================================
# CONFIDENCE LEVELS
# =============================================================================

CONFIDENCE_LEVELS = {
    "90%": 0.90,
    "95%": 0.95,
    "99%": 0.99,
}

# =============================================================================
# GENERATE LOSS DISTRIBUTION
# =============================================================================

def generate_loss_distribution(
    portfolio_df,
    periods=10000
):
    """
    Generate simulated portfolio loss distribution.
    """

    np.random.seed(42)

    portfolio_loss = (

        portfolio_df["pd_score"]
        * portfolio_df["lgd"]
        * portfolio_df["ead"]

    ).sum()

    portfolio_value = (
        portfolio_df["ead"].sum()
    )

    if portfolio_value <= 0:

        portfolio_loss_ratio = 0

    else:

        portfolio_loss_ratio = (
            portfolio_loss
            / portfolio_value
        )

    volatility = (
        portfolio_df["pd_score"].mean()
        * 0.30
    )

    simulated_returns = np.random.normal(
        loc=-portfolio_loss_ratio,
        scale=volatility,
        size=periods
    )

    return simulated_returns

# =============================================================================
# VALUE AT RISK
# =============================================================================

def calculate_var(
    returns,
    confidence_level
):
    """
    Calculate Value at Risk threshold.
    """

    percentile = (
        1 - confidence_level
    ) * 100

    var = np.percentile(
        returns,
        percentile
    )

    return round(
        abs(var),
        4
    )

# =============================================================================
# CONDITIONAL VALUE AT RISK
# =============================================================================

def calculate_cvar(
    returns,
    confidence_level
):
    """
    Calculate Conditional Value at Risk (Expected Shortfall).
    """

    percentile = (
        1 - confidence_level
    ) * 100

    var_threshold = np.percentile(
        returns,
        percentile
    )

    tail_losses = returns[
        returns <= var_threshold
    ]

    cvar = np.mean(
        tail_losses
    )

    return round(
        abs(cvar),
        4
    )

# =============================================================================
# TAIL LOSS RATIO
# =============================================================================

def tail_loss_ratio(
    var_value,
    cvar_value
):
    """
    Measure tail-risk amplification.
    """

    if var_value <= 0:

        return 0

    ratio = (
        cvar_value / var_value
    )

    return round(
        ratio,
        2
    )

# =============================================================================
# EXTREME LOSS SEVERITY
# =============================================================================

def extreme_loss_severity(
    cvar_value
):
    """
    Classify extreme downside severity.
    """

    if cvar_value < 0.08:

        return "LOW EXTREME LOSS RISK"

    elif cvar_value < 0.18:

        return "MODERATE EXTREME LOSS RISK"

    elif cvar_value < 0.35:

        return "HIGH EXTREME LOSS RISK"

    return "SYSTEMIC EXTREME LOSS RISK"

# =============================================================================
# BLACK SWAN SENSITIVITY
# =============================================================================

def black_swan_sensitivity(
    tail_ratio
):
    """
    Determine systemic tail-risk sensitivity.
    """

    if tail_ratio < 1.10:

        return "LOW BLACK SWAN SENSITIVITY"

    elif tail_ratio < 1.35:

        return "MODERATE BLACK SWAN SENSITIVITY"

    elif tail_ratio < 1.70:

        return "HIGH BLACK SWAN SENSITIVITY"

    return "SEVERE SYSTEMIC TAIL EXPOSURE"

# =============================================================================
# CAPITAL PRESERVATION STATUS
# =============================================================================

def capital_preservation_status(
    cvar_value
):
    """
    Determine capital preservation pressure.
    """

    if cvar_value < 0.08:

        return "CAPITAL POSITION STABLE"

    elif cvar_value < 0.18:

        return "MODERATE CAPITAL DETERIORATION"

    elif cvar_value < 0.35:

        return "SEVERE CAPITAL DETERIORATION"

    return "CRITICAL CAPITAL IMPAIRMENT"

# =============================================================================
# TAIL DISTRIBUTION ANALYTICS
# =============================================================================

def tail_distribution_metrics(
    returns
):
    """
    Calculate tail-risk distribution analytics.
    """

    negative_tail = returns[
        returns < np.percentile(
            returns,
            5
        )
    ]

    metrics = {

        "tail_mean":
            round(
                float(np.mean(negative_tail)),
                6
            ),

        "tail_volatility":
            round(
                float(np.std(negative_tail)),
                6
            ),

        "worst_tail_loss":
            round(
                float(np.min(negative_tail)),
                6
            ),

        "tail_skewness":
            round(
                float(
                    pd.Series(
                        negative_tail
                    ).skew()
                ),
                6
            ),
    }

    return metrics

# =============================================================================
# EXECUTIVE CVAR NARRATIVE
# =============================================================================

def generate_cvar_narrative(
    confidence,
    cvar_value,
    severity
):
    """
    Generate executive tail-risk commentary.
    """

    narrative = (
        f"At {confidence} confidence level, "
        f"KRONOS estimates an expected tail-loss "
        f"severity of {round(cvar_value * 100, 2)}% "
        f"once VaR thresholds are breached. "
        f"Tail-risk classification: {severity}."
    )

    return narrative

# =============================================================================
# RUN CVAR ANALYSIS
# =============================================================================

def run_cvar_analysis(
    portfolio_df,
    portfolio_value=10000000
):
    """
    Run enterprise Conditional Value at Risk analysis.
    """

    print("\n" + "=" * 80)
    print("[KRONOS] RUNNING CONDITIONAL VAR ENGINE")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # LOSS DISTRIBUTION
    # -------------------------------------------------------------------------

    returns = generate_loss_distribution(
        portfolio_df
    )

    results = {}

    # -------------------------------------------------------------------------
    # CONFIDENCE ANALYSIS
    # -------------------------------------------------------------------------

    for label, confidence in CONFIDENCE_LEVELS.items():

        var_value = calculate_var(
            returns,
            confidence
        )

        cvar_value = calculate_cvar(
            returns,
            confidence
        )

        tail_ratio = tail_loss_ratio(
            var_value,
            cvar_value
        )

        severity = extreme_loss_severity(
            cvar_value
        )

        black_swan = black_swan_sensitivity(
            tail_ratio
        )

        capital_status = capital_preservation_status(
            cvar_value
        )

        tail_capital_loss = (
            portfolio_value
            * cvar_value
        )

        narrative = generate_cvar_narrative(
            label,
            cvar_value,
            severity
        )

        results[label] = {

            "value_at_risk":
                var_value,

            "conditional_var":
                cvar_value,

            "cvar_percentage":
                round(
                    cvar_value * 100,
                    2
                ),

            "portfolio_value":
                portfolio_value,

            "tail_loss_ratio":
                tail_ratio,

            "tail_capital_loss":
                round(
                    float(tail_capital_loss),
                    2
                ),

            "extreme_loss_severity":
                severity,

            "black_swan_sensitivity":
                black_swan,

            "capital_preservation_status":
                capital_status,

            "risk_gap":
                round(
                    (
                        cvar_value
                        - var_value
                    ) * 100,
                    2
                ),

            "tail_loss_amplification":
                round(
                    (
                        tail_ratio
                        - 1
                    ) * 100,
                    2
                ),

            "portfolio_loss_capacity":
                round(
                    (
                        tail_capital_loss
                        / portfolio_value
                    ) * 100,
                    2
                ),

            "executive_narrative":
                narrative,
        }

    # -------------------------------------------------------------------------
    # TAIL ANALYTICS
    # -------------------------------------------------------------------------

    tail_metrics = tail_distribution_metrics(
        returns
    )

    # -------------------------------------------------------------------------
    # REPORTING
    # -------------------------------------------------------------------------

    print("\n[KRONOS] CONDITIONAL VAR SUMMARY\n")

    for confidence, metrics in results.items():

        print(f"\nCONFIDENCE LEVEL: {confidence}")

        for key, value in metrics.items():

            print(f"{key}: {value}")

        print("-" * 60)

    print("\nTAIL DISTRIBUTION METRICS\n")

    for key, value in tail_metrics.items():

        print(f"{key}: {value}")

    print("=" * 80)

    return {

        "cvar_results":
            results,

        "tail_metrics":
            tail_metrics,

        "loss_distribution":
            returns,
    }

# =============================================================================
# SAMPLE PORTFOLIO
# =============================================================================

SAMPLE_PORTFOLIO = pd.DataFrame([

    {
        "borrower_id": "B1001",
        "pd_score": 0.05,
        "lgd": 0.24,
        "ead": 20000,
    },

    {
        "borrower_id": "B1002",
        "pd_score": 0.32,
        "lgd": 0.65,
        "ead": 62000,
    },

    {
        "borrower_id": "B1003",
        "pd_score": 0.72,
        "lgd": 0.86,
        "ead": 118000,
    },

    {
        "borrower_id": "B1004",
        "pd_score": 0.18,
        "lgd": 0.41,
        "ead": 36000,
    },

])

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":

    run_cvar_analysis(
        SAMPLE_PORTFOLIO,
        portfolio_value=30000000
    )

    print("\n[KRONOS] CVAR ENGINE COMPLETED")

# =============================================================================
# END OF FILE
# =============================================================================
