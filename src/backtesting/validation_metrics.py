# =============================================================================
# KRONOS — VALIDATION METRICS ENGINE
# File: src/backtesting/validation_metrics.py
# =============================================================================

import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.metrics import roc_auc_score

# =============================================================================
# VALIDATION INPUT CLEANING
# =============================================================================

def _clean_numeric_array(values):
    array = pd.to_numeric(
        pd.Series(values),
        errors="coerce"
    ).replace([np.inf, -np.inf], np.nan)

    return array.dropna().to_numpy(dtype=float)


def _clean_aligned_arrays(
    actual,
    predicted_scores
):
    frame = pd.DataFrame({
        "actual": actual,
        "score": predicted_scores,
    })
    frame = frame.replace([np.inf, -np.inf], np.nan).dropna()

    return (
        frame["actual"].to_numpy(dtype=float),
        frame["score"].to_numpy(dtype=float),
    )

# =============================================================================
# ROC-AUC CALCULATION
# =============================================================================

def roc_auc_score_manual(
    actual,
    predicted_scores
):
    """
    Simplified ROC-AUC approximation.
    """

    actual, predicted_scores = _clean_aligned_arrays(
        actual,
        predicted_scores
    )

    if len(actual) == 0 or len(np.unique(actual)) < 2:

        return 0.0

    try:

        auc = roc_auc_score(
            actual,
            predicted_scores
        )

    except ValueError:

        return 0.0

    return round(
        float(auc),
        4
    )

# =============================================================================
# KS-STATISTIC
# =============================================================================

def ks_statistic(
    actual,
    predicted_scores
):
    """
    Compute KS-statistic.
    """

    actual, predicted_scores = _clean_aligned_arrays(
        actual,
        predicted_scores
    )

    if len(actual) == 0 or len(np.unique(actual)) < 2:

        return 0.0

    df = pd.DataFrame({

        "actual":
            actual,

        "score":
            predicted_scores
    })

    df = df.sort_values(
        by="score"
    )

    positive_total = np.sum(
        df["actual"] == 1
    )

    negative_total = np.sum(
        df["actual"] == 0
    )

    if positive_total == 0 or negative_total == 0:

        return 0.0

    df["cum_positive"] = (
        (df["actual"] == 1)
        .cumsum()
    )

    df["cum_negative"] = (
        (df["actual"] == 0)
        .cumsum()
    )

    df["tpr"] = (
        df["cum_positive"] /
        positive_total
    )

    df["fpr"] = (
        df["cum_negative"] /
        negative_total
    )

    ks = np.max(
        np.abs(
            df["tpr"] -
            df["fpr"]
        )
    )

    return round(
        float(ks),
        4
    )

# =============================================================================
# CALIBRATION ERROR
# =============================================================================

def calibration_error(
    actual,
    predicted_scores
):
    """
    Compute average calibration error.
    """

    actual, predicted_scores = _clean_aligned_arrays(
        actual,
        predicted_scores
    )

    if len(actual) == 0:

        return 0.0

    error = np.mean(
        np.abs(
            actual -
            predicted_scores
        )
    )

    return round(
        float(error),
        4
    )

# =============================================================================
# POPULATION STABILITY INDEX
# =============================================================================

def population_stability_index(
    expected,
    actual
):
    """
    Compute PSI metric.
    """

    expected = _clean_numeric_array(expected)
    actual = _clean_numeric_array(actual)

    if len(expected) == 0 or len(actual) == 0:

        return 0.0

    min_length = min(len(expected), len(actual))
    expected = expected[:min_length]
    actual = actual[:min_length]

    expected_sum = np.sum(expected)
    actual_sum = np.sum(actual)

    if expected_sum <= 0 or actual_sum <= 0:

        return 0.0

    expected_perc = (
        expected /
        expected_sum
    )

    actual_perc = (
        actual /
        actual_sum
    )

    psi_values = (

        (
            expected_perc -
            actual_perc
        ) *

        np.log(
            (
                expected_perc +
                1e-10
            ) /
            (
                actual_perc +
                1e-10
            )
        )
    )

    psi = np.sum(
        psi_values
    )

    return round(
        float(psi),
        4
    )

# =============================================================================
# FEATURE DRIFT ANALYSIS
# =============================================================================

def feature_drift_analysis(
    training_mean,
    production_mean
):
    """
    Measure feature drift.
    """

    training = _clean_numeric_array([training_mean])
    production = _clean_numeric_array([production_mean])

    if len(training) == 0 or len(production) == 0:

        return {

            "drift_value":
                0.0,

            "drift_status":
                "UNAVAILABLE",
        }

    drift = abs(
        production[0] -
        training[0]
    )

    if drift < 0.10:

        drift_status = (
            "STABLE"
        )

    elif drift < 0.25:

        drift_status = (
            "MODERATE DRIFT"
        )

    else:

        drift_status = (
            "CRITICAL DRIFT"
        )

    return {

        "drift_value":
            round(
                float(drift),
                4
            ),

        "drift_status":
            drift_status,
    }

# =============================================================================
# VALIDATION GOVERNANCE
# =============================================================================

def governance_assessment(
    auc,
    ks,
    psi
):
    """
    Enterprise validation governance.
    """

    if (
        auc >= 0.85 and
        ks >= 0.40 and
        psi < 0.10
    ):

        return (
            "MODEL STABLE"
        )

    elif (
        auc >= 0.75 and
        ks >= 0.25 and
        psi < 0.25
    ):

        return (
            "MODEL MONITORING"
        )

    return (
        "MODEL ESCALATION REQUIRED"
    )

# =============================================================================
# VALIDATION SUMMARY
# =============================================================================

def model_validation_summary(
    auc,
    ks,
    calibration,
    psi,
    governance
):
    """
    Build an executive model-validation summary.
    """

    return {

        "model_validation_status":
            governance,

        "discrimination_quality":
            (
                "STRONG"
                if auc >= 0.85
                else "ADEQUATE"
                if auc >= 0.75
                else "WEAK"
            ),

        "separation_quality":
            (
                "STRONG"
                if ks >= 0.40
                else "ADEQUATE"
                if ks >= 0.25
                else "WEAK"
            ),

        "calibration_status":
            (
                "CONTROLLED"
                if calibration <= 0.25
                else "ELEVATED ERROR"
            ),

        "population_stability_status":
            (
                "STABLE"
                if psi < 0.10
                else "MODERATE DRIFT"
                if psi < 0.25
                else "CRITICAL DRIFT"
            ),
    }

# =============================================================================
# BACKTEST SUMMARY
# =============================================================================

def backtest_result_summary(
    backtest_results
):
    """
    Normalize backtest results for governance reporting.
    """

    if not backtest_results:

        return {

            "backtest_status":
                "NOT PROVIDED",

            "summary":
                "No backtest results were attached to this validation run.",
        }

    return {

        "backtest_status":
            backtest_results.get(
                "governance_status",
                "UNKNOWN"
            ),

        "accuracy":
            backtest_results.get(
                "accuracy"
            ),

        "precision":
            backtest_results.get(
                "precision"
            ),

        "recall":
            backtest_results.get(
                "recall"
            ),

        "f1_score":
            backtest_results.get(
                "f1_score"
            ),
    }

# =============================================================================
# MONITORING UTILITIES
# =============================================================================

def model_performance_monitoring(
    validation_results
):
    """
    Create a lightweight monitoring view for validation results.
    """

    return {

        "monitoring_status":
            validation_results.get(
                "governance_status",
                "UNKNOWN"
            ),

        "validation_confidence":
            validation_results.get(
                "validation_confidence"
            ),

        "roc_auc":
            validation_results.get(
                "roc_auc"
            ),

        "ks_statistic":
            validation_results.get(
                "ks_statistic"
            ),

        "population_stability_index":
            validation_results.get(
                "population_stability_index"
            ),
    }


def drift_detection_placeholder(
    feature_name="portfolio_feature_set"
):
    """
    Declare the drift-monitoring contract for future production feeds.
    """

    return {

        "feature_name":
            feature_name,

        "monitoring_state":
            "PLACEHOLDER",

        "required_inputs":
            [
                "training_distribution",
                "production_distribution",
                "monitoring_window",
            ],

        "implementation_note":
            (
                "Production drift detection is ready for integration when "
                "time-windowed production feature distributions are available."
            ),
    }

# =============================================================================
# VALIDATION REPORTING LAYER
# =============================================================================

def validation_reporting_layer(
    validation_results,
    backtest_results=None
):
    """
    Assemble validation, backtesting, and monitoring summaries.
    """

    return {

        "model_validation_summary":
            validation_results.get(
                "model_validation_summary",
                {}
            ),

        "backtest_result_summary":
            backtest_result_summary(
                backtest_results
            ),

        "model_performance_monitoring":
            model_performance_monitoring(
                validation_results
            ),

        "drift_detection":
            drift_detection_placeholder(),
    }

# =============================================================================
# VALIDATION ENGINE
# =============================================================================

def run_validation_engine(
    actual,
    predicted_scores,
    expected_distribution,
    actual_distribution,
    training_mean,
    production_mean
):
    """
    Master enterprise validation workflow.
    """

    print("\n" + "=" * 80)
    print("[KRONOS] RUNNING VALIDATION METRICS ENGINE")
    print("=" * 80)

    actual, predicted_scores = _clean_aligned_arrays(
        actual,
        predicted_scores
    )

    # -------------------------------------------------------------------------
    # ROC-AUC
    # -------------------------------------------------------------------------

    auc = roc_auc_score_manual(

        actual,

        predicted_scores
    )

    # -------------------------------------------------------------------------
    # KS-STATISTIC
    # -------------------------------------------------------------------------

    ks = ks_statistic(

        actual,

        predicted_scores
    )

    # -------------------------------------------------------------------------
    # CALIBRATION ERROR
    # -------------------------------------------------------------------------

    calibration = calibration_error(

        actual,

        predicted_scores
    )

    # -------------------------------------------------------------------------
    # PSI ANALYSIS
    # -------------------------------------------------------------------------

    psi = population_stability_index(

        expected_distribution,

        actual_distribution
    )

    # -------------------------------------------------------------------------
    # GINI COEFFICIENT
    # -------------------------------------------------------------------------

    gini_coefficient = round(

        (2 * auc) - 1,

        4
    )

    # -------------------------------------------------------------------------
    # BRIER SCORE
    # -------------------------------------------------------------------------

    brier_score = (
        round(
            float(
                np.mean(
                    (
                        actual -
                        predicted_scores
                    ) ** 2
                )
            ),
            4
        )
        if len(actual) > 0
        else 0.0
    )

    # -------------------------------------------------------------------------
    # VALIDATION CONFIDENCE
    # -------------------------------------------------------------------------

    validation_confidence = round(

        (
            auc * 40
            + ks * 30
            + (
                1 - min(psi, 1)
            ) * 30
        ),

        2
    )

    # -------------------------------------------------------------------------
    # FEATURE DRIFT
    # -------------------------------------------------------------------------

    drift_analysis = (
        feature_drift_analysis(

            training_mean,

            production_mean
        )
    )

    # -------------------------------------------------------------------------
    # GOVERNANCE
    # -------------------------------------------------------------------------

    governance = governance_assessment(

        auc,

        ks,

        psi
    )

    validation_summary = model_validation_summary(

        auc,

        ks,

        calibration,

        psi,

        governance
    )

    # -------------------------------------------------------------------------
    # RESULTS PACKAGE
    # -------------------------------------------------------------------------

    results = {

        "roc_auc":
            auc,

        "ks_statistic":
            ks,

        "calibration_error":
            calibration,

        "population_stability_index":
            psi,

        "gini_coefficient":
            gini_coefficient,

        "brier_score":
            brier_score,

        "validation_confidence":
            validation_confidence,

        "validation_observations":
            int(len(actual)),

        "validation_warnings":
            [
                warning
                for warning in [
                    (
                        "No aligned validation observations available."
                        if len(actual) == 0
                        else ""
                    ),
                    (
                        "ROC-AUC and KS require at least two observed classes."
                        if len(actual) > 0 and len(np.unique(actual)) < 2
                        else ""
                    ),
                ]
                if warning
            ],

        "feature_drift_analysis":
            drift_analysis,

        "governance_status":
            governance,

        "model_validation_summary":
            validation_summary,

        "validation_timestamp":
            datetime.utcnow().strftime(
                "%Y-%m-%d %H:%M:%S UTC"
            ),
    }

    results["validation_report"] = validation_reporting_layer(
        results
    )

    # -------------------------------------------------------------------------
    # REPORTING
    # -------------------------------------------------------------------------

    print("\n[KRONOS] VALIDATION RESULTS\n")

    for key, value in results.items():

        print(f"\n{key}:\n{value}")

    print("\n" + "=" * 80)

    return results

# =============================================================================
# SAMPLE DATA
# =============================================================================

ACTUAL_VALUES = np.array([

    1, 0, 1, 1, 0,
    1, 0, 0, 1, 1,
    0, 1, 0, 1, 0

])

PREDICTED_SCORES = np.array([

    0.88, 0.16, 0.79, 0.83, 0.24,
    0.91, 0.12, 0.18, 0.72, 0.81,
    0.21, 0.86, 0.28, 0.76, 0.19

])

EXPECTED_DISTRIBUTION = np.array([

    120, 240, 310, 280, 150

])

ACTUAL_DISTRIBUTION = np.array([

    128, 226, 324, 264, 158

])

TRAINING_MEAN = 0.42

PRODUCTION_MEAN = 0.58

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":

    run_validation_engine(

        actual=
            ACTUAL_VALUES,

        predicted_scores=
            PREDICTED_SCORES,

        expected_distribution=
            EXPECTED_DISTRIBUTION,

        actual_distribution=
            ACTUAL_DISTRIBUTION,

        training_mean=
            TRAINING_MEAN,

        production_mean=
            PRODUCTION_MEAN
    )

    print(
        "\n[KRONOS] VALIDATION METRICS ENGINE COMPLETED"
    )

# =============================================================================
# END OF FILE
# =============================================================================
