# =============================================================================
# KRONOS — BORROWER AI EXPLAINABILITY ENGINE
# File: src/explainability/explainability.py
# =============================================================================

import json
import joblib
import pandas as pd
import numpy as np

from src.shared.config import (
    PD_MODEL_FILE,
    SCALER_FILE,
    FEATURE_COLUMNS_FILE,
)

# =============================================================================
# LOAD MODEL
# =============================================================================

def load_model():
    """
    Load trained PD model.
    """

    try:

        model = joblib.load(PD_MODEL_FILE)

        print("[KRONOS] PD model loaded")

        return model

    except Exception as e:

        print("[KRONOS ERROR] Failed loading model")
        print(e)

        return None

# =============================================================================
# LOAD SCALER
# =============================================================================

def load_scaler():
    """
    Load trained scaler.
    """

    try:

        scaler = joblib.load(SCALER_FILE)

        print("[KRONOS] Scaler loaded")

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
    Load trained feature list.
    """

    try:

        with open(FEATURE_COLUMNS_FILE, "r") as f:

            feature_cols = json.load(f)

        print("[KRONOS] Feature columns loaded")

        return feature_cols

    except Exception as e:

        print("[KRONOS ERROR] Failed loading feature columns")
        print(e)

        return []

# =============================================================================
# PREPARE INPUT DATA
# =============================================================================

def prepare_input(
    borrower_data,
    feature_cols
):
    """
    Prepare borrower input for explainability.
    """

    borrower_df = pd.DataFrame([borrower_data])

    for col in feature_cols:

        if col not in borrower_df.columns:

            borrower_df[col] = 0

    borrower_df = borrower_df[feature_cols]

    borrower_df = borrower_df.fillna(0)

    return borrower_df

# =============================================================================
# FEATURE CONTRIBUTION ENGINE
# =============================================================================

def calculate_feature_contributions(
    borrower_df
):
    """
    Generate simplified feature contribution logic.
    """

    contributions = {}

    for col in borrower_df.columns:

        value = float(
            borrower_df[col].values[0]
        )

        if value > 0:

            contributions[col] = {
                "value":
                    round(
                        value,
                        4
                    ),

                "direction":
                    "INCREASES RISK"
            }

        else:

            contributions[col] = {
                "value":
                    round(
                        abs(value),
                        4
                    ),

                "direction":
                    "REDUCES RISK"
            }

    return contributions

# =============================================================================
# TOP RISK DRIVERS
# =============================================================================

def top_risk_drivers(
    contributions,
    top_n=5
):
    """
    Identify top borrower risk drivers.
    """

    sorted_features = sorted(
        contributions.items(),
        key=lambda x: x[1]["value"],
        reverse=True
    )

    top_features = sorted_features[
        :top_n
    ]

    return top_features

# =============================================================================
# BORROWER RISK NARRATIVE
# =============================================================================

def generate_risk_narrative(
    pd_probability,
    top_features
):
    """
    Generate executive borrower explanation.
    """

    narrative = []

    # -------------------------------------------------------------------------
    # Risk Level
    # -------------------------------------------------------------------------

    if pd_probability < 0.10:

        narrative.append(
            "Borrower demonstrates strong credit quality with low default probability."
        )

    elif pd_probability < 0.30:

        narrative.append(
            "Borrower exhibits moderate credit risk requiring periodic monitoring."
        )

    else:

        narrative.append(
            "Borrower exhibits elevated default risk requiring enhanced review."
        )

    # -------------------------------------------------------------------------
    # Feature Drivers
    # -------------------------------------------------------------------------

    feature_text = ", ".join(
        [
            feature
            for feature, info in top_features
        ]
    )

    narrative.append(
        f"Primary risk drivers include: {feature_text}."
    )

    return " ".join(
        narrative
    )

# =============================================================================
# EXPLAIN BORROWER
# =============================================================================

def explain_borrower(
    borrower_data
):
    """
    Run borrower explainability engine.
    """

    print("\n" + "=" * 80)
    print("[KRONOS] RUNNING BORROWER EXPLAINABILITY")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # LOAD ARTIFACTS
    # -------------------------------------------------------------------------

    model = load_model()

    scaler = load_scaler()

    feature_cols = load_feature_columns()

    if (
        model is None
        or scaler is None
        or not feature_cols
    ):

        print("[KRONOS ERROR] Missing model artifacts")

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
    # PD PREDICTION
    # -------------------------------------------------------------------------

    probabilities = model.predict_proba(
        scaled_input
    )[0]

    pd_probability = probabilities[1]

    confidence = round(
        max(
            probabilities
        ) * 100,
        2
    )

    # -------------------------------------------------------------------------
    # FEATURE CONTRIBUTIONS
    # -------------------------------------------------------------------------

    contributions = calculate_feature_contributions(
        borrower_df
    )

    top_features = top_risk_drivers(
        contributions
    )

    narrative = generate_risk_narrative(
        pd_probability,
        top_features
    )

    # -------------------------------------------------------------------------
    # FINAL RESULT
    # -------------------------------------------------------------------------

    result = {

        "probability_of_default":
            round(
                float(pd_probability),
                4
            ),

        "explainability_confidence":
            confidence,

        "top_risk_drivers":
            top_features,

        "risk_narrative":
            narrative,
    }

    print("\n[KRONOS] BORROWER EXPLANATION")

    print(
        f"PD Probability: "
        f"{result['probability_of_default']}"
    )

    print(
        f"Explainability Confidence: "
        f"{result['explainability_confidence']}%"
    )

    print("\nTop Risk Drivers:")

    for feature, info in top_features:

        print(
            f"{feature}: "
            f"{info['value']} "
            f"({info['direction']})"
        )

    print("\nNarrative:")

    print(
        result["risk_narrative"]
    )

    print("=" * 80)

    return result

# =============================================================================
# SAMPLE BORROWER
# =============================================================================

SAMPLE_BORROWER = {
    "dti_ratio": 0.42,
    "credit_utilization": 0.68,
    "payment_burden_ratio": 0.33,
    "total_delinquency": 2,
    "high_delinquency_flag": 1,
    "loan_to_income_ratio": 0.57,
    "young_borrower_flag": 0,
    "senior_borrower_flag": 0,
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":

    explain_borrower(SAMPLE_BORROWER)

    print("\n[KRONOS] EXPLAINABILITY ENGINE COMPLETED")

# =============================================================================
# END OF FILE
# =============================================================================