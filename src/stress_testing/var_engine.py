# =============================================================================
# KRONOS — VALUE AT RISK (VaR) ENGINE
# File: src/stress_testing/var_engine.py
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
# PORTFOLIO RETURNS
# =============================================================================

def generate_portfolio_returns(
    portfolio_df,
    periods=252
):
    """
    Generate simulated portfolio return distribution.
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
        * 0.25
    )

    returns = np.random.normal(
        loc=-portfolio_loss_ratio,
        scale=volatility,
        size=periods
    )

    return returns

# =============================================================================
# PARAMETRIC VAR
# =============================================================================

def calculate_parametric_var(
    returns,
    confidence_level=0.95
):
    """
    Calculate Parametric Value at Risk.
    """

    mean_return = np.mean(
        returns
    )

    std_dev = np.std(
        returns
    )

    z_score = norm.ppf(
        1 - confidence_level
    )

    var = (
        mean_return
        + (z_score * std_dev)
    )

    return round(
        abs(var),
        4
    )

# =============================================================================
# HISTORICAL VAR
# =============================================================================

def calculate_historical_var(
    returns,
    confidence_level=0.95
):
    """
    Calculate Historical Value at Risk.
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
# MONTE CARLO VAR
# =============================================================================

def calculate_monte_carlo_var(
    returns,
    confidence_level=0.95,
    simulations=10000
):
    """
    Calculate Monte Carlo VaR.
    """

    np.random.seed(42)

    simulated_returns = np.random.choice(
        returns,
        size=simulations,
        replace=True
    )

    percentile = (
        1 - confidence_level
    ) * 100

    var = np.percentile(
        simulated_returns,
        percentile
    )

    return round(
        abs(var),
        4
    )

# =============================================================================
# LOSS DISTRIBUTION METRICS
# =============================================================================

def loss_distribution_metrics(
    returns
):
    """
    Calculate portfolio distribution metrics.
    """

    largest_loss = abs(
        min(returns)
    )

    loss_concentration = round(
        (
            largest_loss
            / abs(np.sum(returns))
        ) * 100,
        2
    )

    metrics = {

        "mean_return":
            round(
                float(np.mean(returns)),
                6
            ),

        "volatility":
            round(
                float(np.std(returns)),
                6
            ),

        "worst_loss":
            round(
                float(np.min(returns)),
                6
            ),

        "best_return":
            round(
                float(np.max(returns)),
                6
            ),

        "skewness":
            round(
                float(
                    pd.Series(returns).skew()
                ),
                6
            ),

        "kurtosis":
            round(
                float(
                    pd.Series(returns).kurtosis()
                ),
                6
            ),

        "loss_concentration":
            loss_concentration,
    }

    return metrics

# =============================================================================
# RISK SEVERITY
# =============================================================================

def var_severity(
    var_value
):
    """
    Classify Value at Risk severity.
    """

    if var_value < 0.05:

        return "LOW RISK"

    elif var_value < 0.12:

        return "MODERATE RISK"

    elif var_value < 0.25:

        return "HIGH RISK"

    return "EXTREME RISK"

# =============================================================================
# CAPITAL AT RISK
# =============================================================================

def capital_at_risk(
    portfolio_value,
    var_value
):
    """
    Estimate capital exposure at risk.
    """

    capital_risk = (
        portfolio_value * var_value
    )

    return round(
        float(capital_risk),
        2
    )

# =============================================================================
# EXECUTIVE VAR NARRATIVE
# =============================================================================

def generate_var_narrative(
    confidence,
    var_value,
    severity
):
    """
    Generate executive VaR commentary.
    """

    narrative = (
        f"At {confidence} confidence level, "
        f"KRONOS estimates a maximum expected "
        f"portfolio downside risk of "
        f"{round(var_value * 100, 2)}% under "
        f"normal market conditions. "
        f"Risk classification: {severity}."
    )

    return narrative

# =============================================================================
# RUN VAR ANALYSIS
# =============================================================================

def run_var_analysis(
    portfolio_df,
    portfolio_value=10000000
):
    """
    Run enterprise Value at Risk analysis.
    """

    print("\n" + "=" * 80)
    print("[KRONOS] RUNNING VALUE AT RISK ENGINE")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # GENERATE RETURNS
    # -------------------------------------------------------------------------

    returns = generate_portfolio_returns(
        portfolio_df
    )

    results = {}

    # -------------------------------------------------------------------------
    # CONFIDENCE LEVEL ANALYSIS
    # -------------------------------------------------------------------------

    for label, confidence in CONFIDENCE_LEVELS.items():

        parametric_var = calculate_parametric_var(
            returns,
            confidence
        )

        historical_var = calculate_historical_var(
            returns,
            confidence
        )

        monte_carlo_var = calculate_monte_carlo_var(
            returns,
            confidence
        )

        severity = var_severity(
            monte_carlo_var
        )

        capital_risk = capital_at_risk(
            portfolio_value,
            monte_carlo_var
        )

        narrative = generate_var_narrative(
            label,
            monte_carlo_var,
            severity
        )

        results[label] = {

            "parametric_var":
                parametric_var,

            "historical_var":
                historical_var,

            "monte_carlo_var":
                monte_carlo_var,

            "var_percentage":
                round(
                    monte_carlo_var * 100,
                    2
                ),

            "portfolio_value":
                portfolio_value,

            "risk_severity":
                severity,

            "capital_at_risk":
                capital_risk,

            "executive_narrative":
                narrative,
        }

    # -------------------------------------------------------------------------
    # DISTRIBUTION ANALYTICS
    # -------------------------------------------------------------------------

    distribution_metrics = (
        loss_distribution_metrics(
            returns
        )
    )

    # -------------------------------------------------------------------------
    # REPORTING
    # -------------------------------------------------------------------------

    print("\n[KRONOS] VALUE AT RISK SUMMARY\n")

    for confidence, metrics in results.items():

        print(f"\nCONFIDENCE LEVEL: {confidence}")

        for key, value in metrics.items():

            print(f"{key}: {value}")

        print("-" * 60)

    print("\nLOSS DISTRIBUTION METRICS\n")

    for key, value in distribution_metrics.items():

        print(f"{key}: {value}")

    print("=" * 80)

    return {

        "var_results":
            results,

        "distribution_metrics":
            distribution_metrics,

        "returns_distribution":
            returns,
    }

# =============================================================================
# SAMPLE PORTFOLIO
# =============================================================================

SAMPLE_PORTFOLIO = pd.DataFrame([

    {
        "borrower_id": "B1001",
        "pd_score": 0.04,
        "lgd": 0.22,
        "ead": 18000,
    },

    {
        "borrower_id": "B1002",
        "pd_score": 0.29,
        "lgd": 0.61,
        "ead": 54000,
    },

    {
        "borrower_id": "B1003",
        "pd_score": 0.68,
        "lgd": 0.83,
        "ead": 104000,
    },

    {
        "borrower_id": "B1004",
        "pd_score": 0.16,
        "lgd": 0.39,
        "ead": 34000,
    },

])

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":

    run_var_analysis(
        SAMPLE_PORTFOLIO,
        portfolio_value=25000000
    )

    print("\n[KRONOS] VAR ENGINE COMPLETED")

# =============================================================================
# END OF FILE
# =============================================================================
