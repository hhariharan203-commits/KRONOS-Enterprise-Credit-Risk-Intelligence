# =============================================================================
# KRONOS — REAL-TIME EAD ENGINE
# File: src/credit_risk/ead_engine.py
# =============================================================================

import json
import joblib
import pandas as pd
import numpy as np

# =============================================================================
# CONFIG IMPORTS
# =============================================================================

from src.shared.config import (
    EAD_FEATURE_COLUMNS_FILE as EAD_FEATURE_FILE,
    EAD_MODEL_FILE,
    EAD_SCALER_FILE,
)

# =============================================================================
# LOAD EAD MODEL
# =============================================================================

def load_ead_model():
    """
    Load trained EAD model.
    """

    try:

        model = joblib.load(
            EAD_MODEL_FILE
        )

        print("[KRONOS] EAD model loaded")

        return model

    except Exception as e:

        print("[KRONOS ERROR] Failed loading EAD model")
        print(e)

        return None

# =============================================================================
# LOAD SCALER
# =============================================================================

def load_scaler():
    """
    Load EAD scaler.
    """

    try:

        scaler = joblib.load(
            EAD_SCALER_FILE
        )

        print("[KRONOS] EAD scaler loaded")

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
    Load EAD feature columns.
    """

    try:

        with open(
            EAD_FEATURE_FILE,
            "r"
        ) as f:

            feature_cols = json.load(f)

        print("[KRONOS] EAD feature columns loaded")

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
# UTILIZATION ESTIMATION
# =============================================================================

def estimate_utilization_rate(
    exposure,
    credit_limit
):
    """
    Estimate facility utilization.
    """

    if credit_limit <= 0:

        return 0

    utilization = exposure / credit_limit

    utilization = np.clip(
        utilization,
        0,
        1.5
    )

    return round(
        utilization * 100,
        2
    )

# =============================================================================
# EAD RISK BAND
# =============================================================================

def classify_exposure_risk(
    exposure
):
    """
    Classify exposure severity.
    """

    if exposure < 5000:

        return "LOW EXPOSURE"

    elif exposure < 15000:

        return "MODERATE EXPOSURE"

    elif exposure < 30000:

        return "HIGH EXPOSURE"

    else:

        return "SEVERE EXPOSURE"

# =============================================================================
# UTILIZATION CATEGORY
# =============================================================================

def classify_utilization(
    utilization_rate
):
    """
    Classify borrower utilization profile.
    """

    if utilization_rate < 30:

        return "LOW UTILIZATION"

    elif utilization_rate < 60:

        return "MODERATE UTILIZATION"

    elif utilization_rate < 85:

        return "HIGH UTILIZATION"

    else:

        return "MAXED FACILITY"

# =============================================================================
# FACILITY STRESS LEVEL
# =============================================================================

def facility_stress_level(
    utilization_rate
):
    """
    Determine facility stress severity.
    """

    if utilization_rate < 40:

        return "LOW STRESS"

    elif utilization_rate < 70:

        return "MODERATE STRESS"

    else:

        return "HIGH FACILITY STRESS"

# =============================================================================
# EAD PREDICTION ENGINE
# =============================================================================

def predict_ead(
    borrower_data,
    credit_limit=25000
):
    """
    Run real-time EAD prediction.
    """

    print("\n" + "=" * 80)
    print("[KRONOS] RUNNING EAD ENGINE")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # LOAD ARTIFACTS
    # -------------------------------------------------------------------------

    model = load_ead_model()

    scaler = load_scaler()

    feature_cols = load_feature_columns()

    if (
        model is None
        or scaler is None
        or not feature_cols
    ):

        print("[KRONOS ERROR] Missing EAD artifacts")

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
    # EAD PREDICTION
    # -------------------------------------------------------------------------

    predicted_ead = model.predict(
        scaled_input
    )[0]

    predicted_ead = np.clip(
        predicted_ead,
        1000,
        None
    )

    # -------------------------------------------------------------------------
    # UTILIZATION ANALYSIS
    # -------------------------------------------------------------------------

    utilization_rate = estimate_utilization_rate(
        predicted_ead,
        credit_limit
    )

    # -------------------------------------------------------------------------
    # CLASSIFICATIONS
    # -------------------------------------------------------------------------

    exposure_band = classify_exposure_risk(
        predicted_ead
    )

    utilization_category = classify_utilization(
        utilization_rate
    )

    stress_level = facility_stress_level(
        utilization_rate
    )

    model_confidence = round(
        min(
            utilization_rate,
            99.0
        ),
        2
    )

    # -------------------------------------------------------------------------
    # FINAL RESULT
    # -------------------------------------------------------------------------

    result = {
        "predicted_ead":
            round(
                float(predicted_ead),
                2
            ),

        "credit_limit":
            round(
                float(credit_limit),
                2
            ),

        "utilization_rate":
            utilization_rate,

        "exposure_band":
            exposure_band,

        "utilization_category":
            utilization_category,

        "facility_stress_level":
            stress_level,

        "model_confidence":
            model_confidence,

        "ead_percent_of_limit":
            utilization_rate,
    }

    # -------------------------------------------------------------------------
    # REPORTING
    # -------------------------------------------------------------------------

    print("\n[KRONOS] EAD ANALYSIS")

    for key, value in result.items():

        print(f"{key}: {value}")

    print("=" * 80)

    return result

# =============================================================================
# SAMPLE BORROWER
# =============================================================================

SAMPLE_BORROWER = {
    "dti_ratio": 0.44,
    "credit_utilization": 0.81,
    "payment_burden_ratio": 0.41,
    "loan_to_income_ratio": 0.63,
    "total_delinquency": 2,
    "high_delinquency_flag": 1,
    "young_borrower_flag": 0,
    "senior_borrower_flag": 0,
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":

    predict_ead(
        SAMPLE_BORROWER,
        credit_limit=30000
    )

    print("\n[KRONOS] EAD ENGINE COMPLETED")

# =============================================================================
# END OF FILE
# =============================================================================
