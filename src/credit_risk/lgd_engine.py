# =============================================================================
# KRONOS — REAL-TIME LGD ENGINE
# File: src/credit_risk/lgd_engine.py
# =============================================================================

import json
import joblib
import pandas as pd
import numpy as np

from src.shared.config import (
    LGD_FEATURE_COLUMNS_FILE as LGD_FEATURE_FILE,
    LGD_MODEL_FILE,
    LGD_SCALER_FILE,
)

# =============================================================================
# LOAD LGD MODEL
# =============================================================================

def load_lgd_model():
    """
    Load trained LGD model.
    """

    try:

        model = joblib.load(
            LGD_MODEL_FILE
        )

        print("[KRONOS] LGD model loaded")

        return model

    except Exception as e:

        print("[KRONOS ERROR] Failed loading LGD model")
        print(e)

        return None

# =============================================================================
# LOAD SCALER
# =============================================================================

def load_scaler():
    """
    Load LGD scaler.
    """

    try:

        scaler = joblib.load(
            LGD_SCALER_FILE
        )

        print("[KRONOS] LGD scaler loaded")

        return scaler

    except Exception as e:

        print("[KRONOS ERROR] Failed loading scaler")
        print(e)

        return None

# =============================================================================
# LOAD FEATURE COLUMNS
# =============================================================================

def load_feature_columns():
    """
    Load LGD feature columns.
    """

    try:

        with open(
            LGD_FEATURE_FILE,
            "r"
        ) as f:

            feature_cols = json.load(f)

        print("[KRONOS] LGD feature columns loaded")

        return feature_cols

    except Exception as e:

        print("[KRONOS ERROR] Failed loading feature columns")
        print(e)

        return []

# =============================================================================
# PREPARE BORROWER INPUT
# =============================================================================

def prepare_input(
    borrower_data,
    feature_cols
):
    """
    Prepare borrower input dataframe.
    """

    borrower_df = pd.DataFrame(
        [borrower_data]
    )

    for col in feature_cols:

        if col not in borrower_df.columns:

            borrower_df[col] = 0

    borrower_df = borrower_df[
        feature_cols
    ]

    borrower_df = borrower_df.fillna(0)

    return borrower_df

# =============================================================================
# RECOVERY RATE ESTIMATION
# =============================================================================

def estimate_recovery_rate(
    lgd
):
    """
    Estimate expected recovery rate.
    """

    recovery_rate = 1 - lgd

    return round(
        recovery_rate * 100,
        2
    )

# =============================================================================
# LGD RISK BAND
# =============================================================================

def classify_lgd_risk(
    lgd
):
    """
    Classify LGD severity.
    """

    if lgd < 0.20:

        return "LOW LOSS SEVERITY"

    elif lgd < 0.40:

        return "MODERATE LOSS SEVERITY"

    elif lgd < 0.60:

        return "HIGH LOSS SEVERITY"

    else:

        return "SEVERE LOSS RISK"

# =============================================================================
# RECOVERY CATEGORY
# =============================================================================

def classify_recovery_strength(
    recovery_rate
):
    """
    Classify borrower recovery profile.
    """

    if recovery_rate >= 80:

        return "STRONG RECOVERY"

    elif recovery_rate >= 60:

        return "MODERATE RECOVERY"

    elif recovery_rate >= 40:

        return "WEAK RECOVERY"

    else:

        return "DISTRESSED RECOVERY"

# =============================================================================
# PROVISIONING SEVERITY
# =============================================================================

def provisioning_severity(
    lgd
):
    """
    Determine reserve severity.
    """

    if lgd < 0.20:

        return "LOW PROVISIONING"

    elif lgd < 0.50:

        return "MEDIUM PROVISIONING"

    else:

        return "HIGH PROVISIONING"

# =============================================================================
# LGD PREDICTION ENGINE
# =============================================================================

def predict_lgd(
    borrower_data
):
    """
    Run real-time LGD prediction.
    """

    print("\n" + "=" * 80)
    print("[KRONOS] RUNNING LGD ENGINE")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # LOAD ARTIFACTS
    # -------------------------------------------------------------------------

    model = load_lgd_model()

    scaler = load_scaler()

    feature_cols = load_feature_columns()

    if (
        model is None
        or scaler is None
        or not feature_cols
    ):

        print("[KRONOS ERROR] Missing LGD artifacts")

        return {}

    # -------------------------------------------------------------------------
    # PREPARE INPUT
    # -------------------------------------------------------------------------

    borrower_df = prepare_input(
        borrower_data,
        feature_cols
    )

    scaled_input = scaler.transform(
        borrower_df
    )

    # -------------------------------------------------------------------------
    # LGD PREDICTION
    # -------------------------------------------------------------------------

    lgd_prediction = model.predict(
        scaled_input
    )[0]

    lgd_prediction = np.clip(
        lgd_prediction,
        0.01,
        0.99
    )

    prediction_confidence = round(
        max(
            0,
            100 - abs(
                0.50 - lgd_prediction
            ) * 100
        ),
        2
    )

    # -------------------------------------------------------------------------
    # RECOVERY ESTIMATION
    # -------------------------------------------------------------------------

    recovery_rate = estimate_recovery_rate(
        lgd_prediction
    )

    # -------------------------------------------------------------------------
    # CLASSIFICATIONS
    # -------------------------------------------------------------------------

    lgd_risk_band = classify_lgd_risk(
        lgd_prediction
    )

    recovery_category = classify_recovery_strength(
        recovery_rate
    )

    reserve_severity = provisioning_severity(
        lgd_prediction
    )

    expected_loss_factor = round(
        float(
            lgd_prediction * 100
        ),
        2
    )

    # -------------------------------------------------------------------------
    # FINAL RESULT
    # -------------------------------------------------------------------------

    result = {

        "lgd":
            round(
                float(lgd_prediction),
                4
            ),

        "lgd_percent":
            round(
                float(
                    lgd_prediction * 100
                ),
                2
            ),

        "recovery_rate":
            recovery_rate,

        "lgd_risk_band":
            lgd_risk_band,

        "recovery_category":
            recovery_category,

        "provisioning_severity":
            reserve_severity,

        "model_confidence":
            prediction_confidence,

        "expected_loss_factor":
            expected_loss_factor,
    }

    # -------------------------------------------------------------------------
    # REPORTING
    # -------------------------------------------------------------------------

    print("\n[KRONOS] LGD ANALYSIS")

    for key, value in result.items():

        print(f"{key}: {value}")

    print("=" * 80)

    return result

# =============================================================================
# SAMPLE BORROWER
# =============================================================================

SAMPLE_BORROWER = {
    "dti_ratio": 0.48,
    "credit_utilization": 0.76,
    "payment_burden_ratio": 0.39,
    "loan_to_income_ratio": 0.67,
    "total_delinquency": 3,
    "high_delinquency_flag": 1,
    "young_borrower_flag": 0,
    "senior_borrower_flag": 0,
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":

    predict_lgd(
        SAMPLE_BORROWER
    )

    print("\n[KRONOS] LGD ENGINE COMPLETED")

# =============================================================================
# END OF FILE
# =============================================================================
