# =============================================================================
# KRONOS — ENTERPRISE CREDIT RISK SCORING ENGINE
# File: src/credit_risk/credit_engine.py
# =============================================================================

import json
import joblib
import numpy as np
import pandas as pd

from src.shared.config import (
    PD_MODEL_FILE,
    SCALER_FILE,
    FEATURE_COLUMNS_FILE,
)

# =============================================================================
# LOAD MODEL ARTIFACTS
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

        print("[KRONOS ERROR] Failed loading PD model")
        print(e)

        return None

# =============================================================================
# LOAD SCALER
# =============================================================================

def load_scaler():
    """
    Load feature scaler.
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
    Load trained feature columns.
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
# RISK BAND CLASSIFICATION
# =============================================================================

def classify_risk_band(pd_probability):
    """
    Convert PD probability into risk category.
    """

    if pd_probability < 0.05:

        return "PRIME"

    elif pd_probability < 0.15:

        return "NEAR PRIME"

    elif pd_probability < 0.30:

        return "MODERATE RISK"

    elif pd_probability < 0.50:

        return "HIGH RISK"

    else:

        return "DEFAULT RISK"

# =============================================================================
# CREDIT SCORE CALCULATION
# =============================================================================

def calculate_credit_score(pd_probability):
    """
    Convert PD probability into 300–850 style score.
    """

    score = 850 - (pd_probability * 550)

    score = max(min(score, 850), 300)

    return round(score)

# =============================================================================
# APPROVAL DECISION LOGIC
# =============================================================================

def approval_decision(pd_probability):
    """
    Generate underwriting recommendation.
    """

    if pd_probability < 0.10:

        return "APPROVE"

    elif pd_probability < 0.25:

        return "WATCH"

    elif pd_probability < 0.45:

        return "HIGH RISK REVIEW"

    else:

        return "REJECT"

# =============================================================================
# RISK GRADE
# =============================================================================

def risk_grade(pd_probability):
    """
    Internal KRONOS risk grade.
    """

    if pd_probability < 0.03:
        return "AAA"

    elif pd_probability < 0.07:
        return "AA"

    elif pd_probability < 0.15:
        return "A"

    elif pd_probability < 0.25:
        return "BBB"

    elif pd_probability < 0.40:
        return "BB"

    elif pd_probability < 0.60:
        return "B"

    else:
        return "CCC"

# =============================================================================
# PORTFOLIO SEGMENT
# =============================================================================

def portfolio_segment(pd_probability):
    """
    Portfolio monitoring segment.
    """

    if pd_probability < 0.10:
        return "PERFORMING"

    elif pd_probability < 0.25:
        return "WATCHLIST"

    elif pd_probability < 0.50:
        return "SPECIAL MENTION"

    else:
        return "DISTRESSED"

# =============================================================================
# EXTERNAL RATING VIEW
# =============================================================================

def expected_rating(pd_probability):
    """
    Approximate external rating category.
    """

    if pd_probability < 0.15:
        return "INVESTMENT GRADE"

    elif pd_probability < 0.40:
        return "NON-INVESTMENT GRADE"

    else:
        return "HIGH YIELD"

# =============================================================================
# DEFAULT ODDS
# =============================================================================

def default_odds(pd_probability):
    """
    Convert PD into odds ratio.
    """

    if pd_probability <= 0:
        return "Extremely Low"

    odds = round(1 / pd_probability, 2)

    return f"1 in {odds}"

# =============================================================================
# PREPARE BORROWER INPUT
# =============================================================================

def prepare_borrower_input(
    borrower_data,
    feature_cols
):
    """
    Prepare borrower data for model scoring.
    """

    borrower_df = pd.DataFrame([borrower_data])

    # Add missing columns
    for col in feature_cols:

        if col not in borrower_df.columns:

            borrower_df[col] = 0

    # Keep correct feature order
    borrower_df = borrower_df[feature_cols]

    borrower_df = borrower_df.fillna(0)

    return borrower_df

# =============================================================================
# SCORE BORROWER
# =============================================================================

def score_borrower(borrower_data):
    """
    Run enterprise borrower scoring.
    """

    print("\n" + "=" * 80)
    print("[KRONOS] RUNNING BORROWER RISK SCORING")
    print("=" * 80)

    # Load artifacts
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

    borrower_df = prepare_borrower_input(
        borrower_data,
        feature_cols
    )

    scaled_input = scaler.transform(
        borrower_df
    )

    # -------------------------------------------------------------------------
    # PD PREDICTION
    # -------------------------------------------------------------------------

    pd_probability = model.predict_proba(
        scaled_input
    )[0][1]

    # -------------------------------------------------------------------------
    # CREDIT INTELLIGENCE
    # -------------------------------------------------------------------------

    risk_band = classify_risk_band(
        pd_probability
    )

    credit_score = calculate_credit_score(
        pd_probability
    )

    decision = approval_decision(
        pd_probability
    )

    grade = risk_grade(
        pd_probability
    )

    segment = portfolio_segment(
        pd_probability
    )

    rating = expected_rating(
        pd_probability
    )

    odds = default_odds(
        pd_probability
    )

    confidence = round(
        max(
            model.predict_proba(
                scaled_input
            )[0]
        ) * 100,
        2
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

        "credit_score":
            credit_score,

        "risk_band":
            risk_band,

        "risk_grade":
            grade,

        "portfolio_segment":
            segment,

        "expected_rating":
            rating,

        "default_odds":
            odds,

        "underwriting_decision":
            decision,

        "model_confidence":
            confidence,
    }

    # -------------------------------------------------------------------------
    # REPORTING
    # -------------------------------------------------------------------------

    print("\n[KRONOS] BORROWER RISK RESULT")

    for key, value in result.items():

        print(f"{key}: {value}")

    print("=" * 80)

    return result

# =============================================================================
# SAMPLE BORROWER
# =============================================================================

SAMPLE_BORROWER = {
    "dti_ratio": 0.32,
    "credit_utilization": 0.48,
    "payment_burden_ratio": 0.25,
    "total_delinquency": 1,
    "high_delinquency_flag": 0,
    "loan_to_income_ratio": 0.45,
    "young_borrower_flag": 0,
    "senior_borrower_flag": 0,
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":

    score_borrower(SAMPLE_BORROWER)

    print("\n[KRONOS] CREDIT ENGINE COMPLETED")

# =============================================================================
# END OF FILE
# =============================================================================