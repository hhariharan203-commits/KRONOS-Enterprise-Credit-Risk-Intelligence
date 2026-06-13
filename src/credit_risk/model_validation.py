# =============================================================================
# KRONOS — ENTERPRISE MODEL VALIDATION ENGINE
# File: src/credit_risk/model_validation.py
# =============================================================================

import json
import joblib
import pandas as pd
import numpy as np

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)

from sklearn.model_selection import train_test_split

from scipy.stats import ks_2samp

from src.shared.config import (
    MERGED_CREDIT_DATA,
    PD_MODEL_FILE,
    SCALER_FILE,
    FEATURE_COLUMNS_FILE,
    MODEL_METRICS_FILE,
    RANDOM_STATE,
    TEST_SIZE,
)

# =============================================================================
# LOAD MODEL ARTIFACTS
# =============================================================================

def load_artifacts():
    """
    Load KRONOS model artifacts.
    """

    model = joblib.load(PD_MODEL_FILE)

    scaler = joblib.load(SCALER_FILE)

    with open(FEATURE_COLUMNS_FILE, "r") as f:

        feature_cols = json.load(f)

    return model, scaler, feature_cols

# =============================================================================
# LOAD DATASET
# =============================================================================

def load_dataset():
    """
    Load merged credit dataset.
    """

    df = pd.read_csv(MERGED_CREDIT_DATA)

    print("\n" + "=" * 80)
    print("[KRONOS] VALIDATION DATASET LOADED")
    print("=" * 80)

    print(f"Shape: {df.shape}")

    return df

# =============================================================================
# PREPARE VALIDATION DATA
# =============================================================================

def prepare_validation_data(
    df,
    scaler,
    feature_cols
):
    """
    Prepare validation dataset.
    """

    for col in feature_cols:

        if col not in df.columns:

            df[col] = 0

    X = df[feature_cols].copy()

    y = df["target_default"].copy()

    X = X.fillna(0)

    X_scaled = scaler.transform(
        X
    )

    return train_test_split(
        X_scaled,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

# =============================================================================
# KS STATISTIC
# =============================================================================

def calculate_ks_statistic(
    y_true,
    y_prob
):
    """
    Calculate Kolmogorov–Smirnov statistic.
    """

    good = y_prob[y_true == 0]

    bad = y_prob[y_true == 1]

    ks_stat = ks_2samp(
        good,
        bad
    ).statistic

    return round(float(ks_stat), 4)

# =============================================================================
# POPULATION STABILITY INDEX
# =============================================================================

def calculate_psi(
    expected,
    actual,
    buckets=10
):
    """
    Population Stability Index.
    """

    expected_percents = np.histogram(
        expected,
        bins=buckets
    )[0] / len(expected)

    actual_percents = np.histogram(
        actual,
        bins=buckets
    )[0] / len(actual)

    psi = np.sum(
        (
            expected_percents
            - actual_percents
        )
        * np.log(
            (
                expected_percents + 1e-6
            )
            /
            (
                actual_percents + 1e-6
            )
        )
    )

    return round(
        float(psi),
        4
    )

# =============================================================================
# OVERFITTING DETECTION
# =============================================================================

def detect_overfitting(
    train_auc,
    test_auc
):
    """
    Detect model overfitting risk.
    """

    gap = abs(train_auc - test_auc)

    if gap < 0.03:

        return "LOW OVERFITTING RISK"

    elif gap < 0.07:

        return "MODERATE OVERFITTING RISK"

    else:

        return "HIGH OVERFITTING RISK"

# =============================================================================
# MODEL DRIFT CLASSIFICATION
# =============================================================================

def classify_model_drift(
    psi
):
    """
    Detect model drift.
    """

    if psi < 0.10:

        return "NO DRIFT"

    elif psi < 0.25:

        return "MODERATE DRIFT"

    else:

        return "SEVERE DRIFT"

# =============================================================================
# MODEL HEALTH SCORE
# =============================================================================

def calculate_model_health(
    auc_score,
    f1,
    ks_stat
):
    """
    Generate institutional model health score.
    """

    health_score = (
        (auc_score * 0.5)
        + (f1 * 0.3)
        + (ks_stat * 0.2)
    ) * 100

    return round(health_score, 2)

# =============================================================================
# VALIDATION ENGINE
# =============================================================================

def validate_model():
    """
    Run full enterprise validation framework.
    """

    print("\n" + "=" * 80)
    print("[KRONOS] RUNNING MODEL VALIDATION")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # LOAD ARTIFACTS
    # -------------------------------------------------------------------------

    model, scaler, feature_cols = load_artifacts()

    df = load_dataset()

    (
        X_train,
        X_test,
        y_train,
        y_test
    ) = prepare_validation_data(
        df,
        scaler,
        feature_cols
    )

    # -------------------------------------------------------------------------
    # TRAIN PREDICTIONS
    # -------------------------------------------------------------------------

    train_prob = model.predict_proba(X_train)[:, 1]

    train_pred = model.predict(X_train)

    train_auc = roc_auc_score(
        y_train,
        train_prob
    )

    # -------------------------------------------------------------------------
    # TEST PREDICTIONS
    # -------------------------------------------------------------------------

    test_prob = model.predict_proba(X_test)[:, 1]

    test_pred = model.predict(X_test)

    # -------------------------------------------------------------------------
    # VALIDATION METRICS
    # -------------------------------------------------------------------------

    accuracy = accuracy_score(
        y_test,
        test_pred
    )

    precision = precision_score(
        y_test,
        test_pred
    )

    recall = recall_score(
        y_test,
        test_pred
    )

    f1 = f1_score(
        y_test,
        test_pred
    )

    auc_score = roc_auc_score(
        y_test,
        test_prob
    )

    ks_stat = calculate_ks_statistic(
        y_test.values,
        test_prob
    )
    
    psi = calculate_psi(
        train_prob,
        test_prob
    )

    drift_status = classify_model_drift(
        psi
    )

    # -------------------------------------------------------------------------
    # GOVERNANCE METRICS
    # -------------------------------------------------------------------------

    overfitting_risk = detect_overfitting(
        train_auc,
        auc_score
    )

    model_health = calculate_model_health(
        auc_score,
        f1,
        ks_stat
    )

    # -------------------------------------------------------------------------
    # VALIDATION SUMMARY
    # -------------------------------------------------------------------------

    validation_results = {

        "accuracy":
            round(
                float(accuracy),
                4
            ),

        "precision":
            round(
                float(precision),
                4
            ),

        "recall":
            round(
                float(recall),
                4
            ),

        "f1_score":
            round(
                float(f1),
                4
            ),

        "roc_auc":
            round(
                float(auc_score),
                4
            ),

        "ks_statistic":
            round(
                float(ks_stat),
                4
            ),

        "population_stability_index":
            psi,

        "psi":
            psi,

        "model_drift":
            drift_status,

        "train_auc":
            round(
                float(train_auc),
                4
            ),

        "overfitting_risk":
            overfitting_risk,

        "model_health_score":
            model_health,
    }

    print("\n" + "=" * 80)
    print("[KRONOS] MODEL VALIDATION SUMMARY")
    print("=" * 80)

    for key, value in validation_results.items():

        print(
            f"{key}: {value}"
        )

    print("=" * 80)

    # -------------------------------------------------------------------------
    # CONFUSION MATRIX
    # -------------------------------------------------------------------------

    print("\n[KRONOS] CONFUSION MATRIX")

    print(confusion_matrix(
        y_test,
        test_pred
    ))

    return validation_results

# =============================================================================
# SAVE VALIDATION REPORT
# =============================================================================

def save_validation_report(results):
    """
    Save validation results.
    """

    with open(MODEL_METRICS_FILE, "w") as f:

        json.dump(
            results,
            f,
            indent=4
        )

    print("\n[KRONOS] Validation report saved")

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":

    results = validate_model()

    save_validation_report(results)

    print("\n[KRONOS] MODEL VALIDATION COMPLETED")

# =============================================================================
# END OF FILE
# =============================================================================
