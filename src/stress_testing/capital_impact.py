# =============================================================================
# KRONOS — CAPITAL IMPACT ENGINE
# File: src/stress_testing/capital_impact.py
# =============================================================================

import pandas as pd
import numpy as np

# =============================================================================
# BASEL CAPITAL THRESHOLDS
# =============================================================================

BASEL_THRESHOLDS = {

    "healthy": 12.0,
    "watchlist": 10.5,
    "stressed": 8.0,
    "critical": 6.0,
}

# =============================================================================
# CALCULATE BASELINE CAPITAL RATIO
# =============================================================================

def calculate_capital_ratio(
    total_capital,
    risk_weighted_assets
):
    """
    Calculate capital adequacy ratio.
    """

    if risk_weighted_assets <= 0:

        return 0

    ratio = (
        total_capital
        / risk_weighted_assets
    ) * 100

    return round(
        ratio,
        2
    )

# =============================================================================
# STRESSED CAPITAL POSITION
# =============================================================================

def stressed_capital_position(
    total_capital,
    stressed_losses
):
    """
    Calculate stressed capital after losses.
    """

    print("\n" + "=" * 80)

    print(
        "BASELINE CAPITAL:",
        total_capital
    )

    print(
        "STRESSED LOSSES:",
        stressed_losses
    )

    print(
        "CAPITAL AFTER LOSS:",
        total_capital - stressed_losses
    )

    print("=" * 80)

    stressed_capital = (
        total_capital
        - stressed_losses
    )

    stressed_capital = max(
        stressed_capital,
        0
    )

    return round(
        stressed_capital,
        2
    )

# =============================================================================
# CAPITAL BUFFER EROSION
# =============================================================================

def capital_buffer_erosion(
    baseline_ratio,
    stressed_ratio
):
    """
    Measure capital deterioration.
    """

    erosion = (
        baseline_ratio
        - stressed_ratio
    )

    return round(
        erosion,
        2
    )

# =============================================================================
# CAPITAL ADEQUACY STATUS
# =============================================================================

def capital_adequacy_status(
    capital_ratio
):
    """
    Determine Basel-style capital health.
    """

    if capital_ratio >= BASEL_THRESHOLDS["healthy"]:

        return "STRONG CAPITAL POSITION"

    elif capital_ratio >= BASEL_THRESHOLDS["watchlist"]:

        return "ADEQUATE CAPITAL POSITION"

    elif capital_ratio >= BASEL_THRESHOLDS["stressed"]:

        return "STRESSED CAPITAL POSITION"

    elif capital_ratio >= BASEL_THRESHOLDS["critical"]:

        return "SEVERE CAPITAL DETERIORATION"

    return "CRITICAL SOLVENCY RISK"

# =============================================================================
# SOLVENCY PRESSURE
# =============================================================================

def solvency_pressure(
    erosion_pct
):
    """
    Determine solvency deterioration severity.
    """

    if erosion_pct < 1:

        return "LOW SOLVENCY PRESSURE"

    elif erosion_pct < 3:

        return "MODERATE SOLVENCY PRESSURE"

    elif erosion_pct < 6:

        return "HIGH SOLVENCY PRESSURE"

    return "SYSTEMIC SOLVENCY PRESSURE"

# =============================================================================
# RECOVERY THRESHOLD
# =============================================================================

def recovery_threshold(
    stressed_ratio
):
    """
    Determine recovery intervention threshold.
    """

    if stressed_ratio >= 12:

        return "NO INTERVENTION REQUIRED"

    elif stressed_ratio >= 10:

        return "CAPITAL CONSERVATION REVIEW"

    elif stressed_ratio >= 8:

        return "CAPITAL RESTORATION PLANNING"

    return "EMERGENCY CAPITAL INTERVENTION"

# =============================================================================
# REGULATORY BREACH CHECK
# =============================================================================

def regulatory_breach(
    stressed_ratio
):
    """
    Check Basel regulatory breach.
    """

    if stressed_ratio < 8:

        return "BASEL CAPITAL BREACH"

    return "REGULATORY COMPLIANT"

# =============================================================================
# CAPITAL RESILIENCE SCORE
# =============================================================================

def capital_resilience_score(
    stressed_ratio
):
    """
    Calculate enterprise capital resilience.
    """

    score = min(
        max(
            stressed_ratio * 8,
            0
        ),
        100
    )

    return round(
        score,
        2
    )

# =============================================================================
# EXECUTIVE CAPITAL NARRATIVE
# =============================================================================

def generate_capital_narrative(
    capital_status,
    solvency_status,
    regulatory_status
):
    """
    Generate executive capital commentary.
    """

    narrative = (
        f"KRONOS stress analysis indicates "
        f"{capital_status.lower()} with "
        f"{solvency_status.lower()}. "
        f"Regulatory assessment: "
        f"{regulatory_status.lower()}."
    )

    return narrative

# =============================================================================
# RUN CAPITAL IMPACT ANALYSIS
# =============================================================================

def run_capital_impact_analysis(
    baseline_capital,
    risk_weighted_assets,
    stressed_losses
):
    """
    Run enterprise capital adequacy simulation.
    """

    print("\n" + "=" * 80)
    print("[KRONOS] RUNNING CAPITAL IMPACT ENGINE")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # BASELINE CAPITAL
    # -------------------------------------------------------------------------

    baseline_ratio = calculate_capital_ratio(
        baseline_capital,
        risk_weighted_assets
    )

    # -------------------------------------------------------------------------
    # STRESSED CAPITAL
    # -------------------------------------------------------------------------

    stressed_capital = stressed_capital_position(
        baseline_capital,
        stressed_losses
    )

    stressed_ratio = calculate_capital_ratio(
        stressed_capital,
        risk_weighted_assets
    )

    # -------------------------------------------------------------------------
    # CAPITAL EROSION
    # -------------------------------------------------------------------------

    erosion_pct = capital_buffer_erosion(
        baseline_ratio,
        stressed_ratio
    )

    # -------------------------------------------------------------------------
    # CLASSIFICATIONS
    # -------------------------------------------------------------------------

    capital_status = capital_adequacy_status(
        stressed_ratio
    )

    solvency_status = solvency_pressure(
        erosion_pct
    )

    recovery_action = recovery_threshold(
        stressed_ratio
    )

    regulatory_status = regulatory_breach(
        stressed_ratio
    )

    resilience_score = capital_resilience_score(
        stressed_ratio
    )

    # -------------------------------------------------------------------------
    # CAPITAL LOSS ABSORPTION
    # -------------------------------------------------------------------------

    loss_absorption_pct = round(
        (
            stressed_losses
            / baseline_capital
        ) * 100,
        2
    )

    # -------------------------------------------------------------------------
    # CAPITAL REMAINING
    # -------------------------------------------------------------------------

    capital_remaining_pct = round(
        (
            stressed_capital
            / baseline_capital
        ) * 100,
        2
    )

    # -------------------------------------------------------------------------
    # CAPITAL DEPLETION RISK
    # -------------------------------------------------------------------------

    if capital_remaining_pct >= 80:

        depletion_risk = "LOW"

    elif capital_remaining_pct >= 60:

        depletion_risk = "MODERATE"

    elif capital_remaining_pct >= 40:

        depletion_risk = "HIGH"

    else:

        depletion_risk = "CRITICAL"

    # -------------------------------------------------------------------------
    # EXECUTIVE NARRATIVE
    # -------------------------------------------------------------------------

    narrative = generate_capital_narrative(
        capital_status,
        solvency_status,
        regulatory_status
    )

    # -------------------------------------------------------------------------
    # FINAL RESULTS
    # -------------------------------------------------------------------------

    results = {

        "baseline_capital_ratio":
            baseline_ratio,

        "stressed_capital_ratio":
            stressed_ratio,

        "capital_buffer_erosion_pct":
            erosion_pct,

        "baseline_capital":
            round(
                float(baseline_capital),
                2
            ),

        "stressed_capital":
            stressed_capital,

        "stressed_losses":
            round(
                float(stressed_losses),
                2
            ),

        "loss_absorption_pct":
                loss_absorption_pct,

        "capital_remaining_pct":
            capital_remaining_pct,

        "capital_depletion_risk":
            depletion_risk,

        "capital_status":
            capital_status,

        "solvency_status":
            solvency_status,

        "recovery_action":
            recovery_action,

        "regulatory_status":
            regulatory_status,

        "capital_resilience_score":
            resilience_score,

        "executive_narrative":
            narrative,
    }

    # -------------------------------------------------------------------------
    # REPORTING
    # -------------------------------------------------------------------------

    print("\n[KRONOS] CAPITAL IMPACT SUMMARY\n")

    for key, value in results.items():

        print(f"{key}: {value}")

    print("=" * 80)

    return results

# =============================================================================
# SAMPLE EXECUTION
# =============================================================================

BASELINE_CAPITAL = 180000000

RISK_WEIGHTED_ASSETS = 1400000000

STRESSED_LOSSES = 62000000

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":

    run_capital_impact_analysis(
        baseline_capital=BASELINE_CAPITAL,
        risk_weighted_assets=RISK_WEIGHTED_ASSETS,
        stressed_losses=STRESSED_LOSSES
    )

    print("\n[KRONOS] CAPITAL IMPACT ENGINE COMPLETED")

# =============================================================================
# END OF FILE
# =============================================================================