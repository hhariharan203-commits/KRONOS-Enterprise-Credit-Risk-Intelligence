# =============================================================================
# KRONOS — BACKTESTING ENGINE
# File: src/backtesting/backtesting.py
# =============================================================================

import pandas as pd
import numpy as np
from datetime import datetime

# =============================================================================
# BACKTESTING CONFIGURATION
# =============================================================================

DEFAULT_PD_THRESHOLD = 0.50

# =============================================================================
# CLASSIFICATION ACCURACY
# =============================================================================

def classification_accuracy(
    actual,
    predicted
):
    """
    Compute classification accuracy.
    """

    actual = np.array(actual)
    predicted = np.array(predicted)

    accuracy = np.mean(
        actual == predicted
    )

    return round(
        float(accuracy),
        4
    )

# =============================================================================
# PRECISION SCORE
# =============================================================================

def precision_score(
    actual,
    predicted
):
    """
    Compute precision score.
    """

    actual = np.array(actual)
    predicted = np.array(predicted)

    true_positive = np.sum(
        (actual == 1) &
        (predicted == 1)
    )

    false_positive = np.sum(
        (actual == 0) &
        (predicted == 1)
    )

    if (
        true_positive +
        false_positive
    ) == 0:

        return 0.0

    precision = (
        true_positive /
        (
            true_positive +
            false_positive
        )
    )

    return round(
        float(precision),
        4
    )

# =============================================================================
# RECALL SCORE
# =============================================================================

def recall_score(
    actual,
    predicted
):
    """
    Compute recall score.
    """

    actual = np.array(actual)
    predicted = np.array(predicted)

    true_positive = np.sum(
        (actual == 1) &
        (predicted == 1)
    )

    false_negative = np.sum(
        (actual == 1) &
        (predicted == 0)
    )

    if (
        true_positive +
        false_negative
    ) == 0:

        return 0.0

    recall = (
        true_positive /
        (
            true_positive +
            false_negative
        )
    )

    return round(
        float(recall),
        4
    )

# =============================================================================
# F1 SCORE
# =============================================================================

def f1_score_metric(
    precision,
    recall
):
    """
    Compute F1 score.
    """

    if (
        precision +
        recall
    ) == 0:

        return 0.0

    f1 = (
        2 *
        (
            precision *
            recall
        )
    ) / (
        precision +
        recall
    )

    return round(
        float(f1),
        4
    )

# =============================================================================
# CONFUSION MATRIX
# =============================================================================

def confusion_matrix_metrics(
    actual,
    predicted
):
    """
    Compute confusion matrix metrics.
    """

    actual = np.array(actual)
    predicted = np.array(predicted)

    true_positive = np.sum(
        (actual == 1) &
        (predicted == 1)
    )

    true_negative = np.sum(
        (actual == 0) &
        (predicted == 0)
    )

    false_positive = np.sum(
        (actual == 0) &
        (predicted == 1)
    )

    false_negative = np.sum(
        (actual == 1) &
        (predicted == 0)
    )

    return {

        "true_positive":
            int(true_positive),

        "true_negative":
            int(true_negative),

        "false_positive":
            int(false_positive),

        "false_negative":
            int(false_negative),
    }

# =============================================================================
# PORTFOLIO DETERIORATION ANALYSIS
# =============================================================================

def portfolio_deterioration_analysis(
    pd_scores
):
    """
    Analyze enterprise deterioration intensity.
    """

    average_pd = np.mean(
        pd_scores
    )

    if average_pd < 0.10:

        deterioration = (
            "STABLE"
        )

    elif average_pd < 0.25:

        deterioration = (
            "ELEVATED RISK"
        )

    elif average_pd < 0.50:

        deterioration = (
            "HIGH RISK"
        )

    else:

        deterioration = (
            "CRITICAL DETERIORATION"
        )

    return {

        "average_pd":
            round(
                float(average_pd),
                4
            ),

        "deterioration_status":
            deterioration,
    }

# =============================================================================
# STRESS BACKTESTING
# =============================================================================

def stress_backtesting(
    pd_scores,
    stress_multiplier=1.5
):
    """
    Simulate stressed probability-of-default.
    """

    stressed_pd = np.array(
        pd_scores
    ) * stress_multiplier

    stressed_pd = np.clip(
        stressed_pd,
        0,
        1
    )

    return stressed_pd

# =============================================================================
# BACKTESTING ENGINE
# =============================================================================

def run_backtesting(
    actual_defaults,
    predicted_pd_scores,
    threshold=DEFAULT_PD_THRESHOLD
):
    """
    Master enterprise backtesting workflow.
    """

    print("\n" + "=" * 80)
    print("[KRONOS] RUNNING BACKTESTING ENGINE")
    print("=" * 80)

    actual_defaults = np.array(
        actual_defaults
    )

    predicted_pd_scores = np.array(
        predicted_pd_scores
    )

    # -------------------------------------------------------------------------
    # CLASSIFICATION THRESHOLD
    # -------------------------------------------------------------------------

    predicted_classes = np.where(

        predicted_pd_scores >= threshold,

        1,

        0
    )

    # -------------------------------------------------------------------------
    # PERFORMANCE METRICS
    # -------------------------------------------------------------------------

    accuracy = classification_accuracy(

        actual_defaults,

        predicted_classes
    )

    precision = precision_score(

        actual_defaults,

        predicted_classes
    )

    recall = recall_score(

        actual_defaults,

        predicted_classes
    )

    f1 = f1_score_metric(

        precision,

        recall
    )

    # -------------------------------------------------------------------------
    # CONFUSION MATRIX
    # -------------------------------------------------------------------------

    confusion = confusion_matrix_metrics(

        actual_defaults,

        predicted_classes
    )

    # -------------------------------------------------------------------------
    # DETERIORATION ANALYSIS
    # -------------------------------------------------------------------------

    deterioration_analysis = (
        portfolio_deterioration_analysis(

            predicted_pd_scores
        )
    )

    # -------------------------------------------------------------------------
    # STRESS BACKTESTING
    # -------------------------------------------------------------------------

    stressed_pd = stress_backtesting(

        predicted_pd_scores
    )

    stressed_average_pd = round(

        float(np.mean(stressed_pd)),

        4
    )

    # -------------------------------------------------------------------------
    # GOVERNANCE ASSESSMENT
    # -------------------------------------------------------------------------

    if accuracy >= 0.85:

        governance_status = (
            "MODEL STABLE"
        )

    elif accuracy >= 0.70:

        governance_status = (
            "MODEL MONITORING"
        )

    else:

        governance_status = (
            "MODEL ESCALATION REQUIRED"
        )

    # -------------------------------------------------------------------------
    # RESULTS PACKAGE
    # -------------------------------------------------------------------------

    results = {

        "accuracy":
            accuracy,

        "precision":
            precision,

        "recall":
            recall,

        "f1_score":
            f1,

        "confusion_matrix":
            confusion,

        "deterioration_analysis":
            deterioration_analysis,

        "stressed_average_pd":
            stressed_average_pd,

        "governance_status":
            governance_status,

        "timestamp":
            datetime.utcnow().strftime(
                "%Y-%m-%d %H:%M:%S UTC"
            ),
    }

    # -------------------------------------------------------------------------
    # REPORTING
    # -------------------------------------------------------------------------

    print("\n[KRONOS] BACKTESTING RESULTS\n")

    for key, value in results.items():

        print(f"\n{key}:\n{value}")

    print("\n" + "=" * 80)

    return results

# =============================================================================
# SAMPLE TEST DATA
# =============================================================================

ACTUAL_DEFAULTS = np.array([

    0, 0, 1, 0, 1,
    1, 0, 0, 1, 1,
    0, 1, 0, 0, 1

])

PREDICTED_PD_SCORES = np.array([

    0.12, 0.18, 0.82, 0.34, 0.76,
    0.91, 0.28, 0.22, 0.68, 0.73,
    0.16, 0.88, 0.26, 0.31, 0.79

])

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":

    run_backtesting(

        actual_defaults=
            ACTUAL_DEFAULTS,

        predicted_pd_scores=
            PREDICTED_PD_SCORES,

        threshold=0.50
    )

    print(
        "\n[KRONOS] BACKTESTING ENGINE COMPLETED"
    )

# =============================================================================
# END OF FILE
# =============================================================================