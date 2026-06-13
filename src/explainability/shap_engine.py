# =============================================================================
# KRONOS — ADVANCED SHAP EXPLAINABILITY ENGINE
# File: src/explainability/shap_engine.py
# =============================================================================

import json
import joblib
import shap
import pandas as pd
import matplotlib.pyplot as plt

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
    Load feature column list.
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
# PREPARE BORROWER INPUT
# =============================================================================

def prepare_input(
    borrower_data,
    feature_cols
):
    """
    Prepare borrower dataframe.
    """

    borrower_df = pd.DataFrame([borrower_data])

    for col in feature_cols:

        if col not in borrower_df.columns:

            borrower_df[col] = 0

    borrower_df = borrower_df[feature_cols]

    borrower_df = borrower_df.fillna(0)

    return borrower_df

# =============================================================================
# BUILD SHAP EXPLAINER
# =============================================================================

def build_shap_explainer(model):
    """
    Build SHAP explainer object.
    """

    try:

        # VotingClassifier handling
        if hasattr(model, "estimators_"):

            base_model = model.estimators_[0]

        else:

            base_model = model

        explainer = shap.TreeExplainer(base_model)

        print("[KRONOS] SHAP explainer initialized")

        return explainer

    except Exception as e:

        print("[KRONOS ERROR] Failed building SHAP explainer")
        print(e)

        return None

# =============================================================================
# GENERATE SHAP VALUES
# =============================================================================

def generate_shap_values(
    borrower_data
):
    """
    Generate borrower-level SHAP values.
    """

    print("\n" + "=" * 80)
    print("[KRONOS] GENERATING SHAP VALUES")
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

        return None

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

    scaled_df = pd.DataFrame(
        scaled_input,
        columns=feature_cols
    )

    # -------------------------------------------------------------------------
    # BUILD EXPLAINER
    # -------------------------------------------------------------------------

    explainer = build_shap_explainer(model)

    if explainer is None:

        return None

    # -------------------------------------------------------------------------
    # SHAP VALUES
    # -------------------------------------------------------------------------

    shap_values = explainer.shap_values(scaled_df)

    print("[KRONOS] SHAP values generated")

    return (
        explainer,
        shap_values,
        scaled_df
    )

# =============================================================================
# LOCAL SHAP EXPLANATION
# =============================================================================

def local_explanation(
    explainer,
    shap_values,
    scaled_df
):
    """
    Generate local borrower explanation.
    """

    print("\n[KRONOS] LOCAL SHAP EXPLANATION")

    feature_impacts = {}

    if isinstance(shap_values, list):

        values = shap_values[1][0]

    else:

        values = shap_values[0]

    for idx, feature in enumerate(
        scaled_df.columns
    ):

        feature_impacts[feature] = round(
            float(values[idx]),
            4
        )

    sorted_impacts = sorted(
        feature_impacts.items(),
        key=lambda x: abs(x[1]),
        reverse=True
    )

    top_drivers = sorted_impacts[:10]

    for feature, impact in top_drivers:

        print(
            f"{feature}: "
            f"{impact}"
        )

    return top_drivers

# =============================================================================
# GLOBAL FEATURE IMPORTANCE
# =============================================================================

def global_feature_importance(
    shap_values,
    scaled_df
):
    """
    Generate global SHAP importance ranking.
    """

    if isinstance(shap_values, list):

        importance_values = abs(
            shap_values[1][0]
        )

    else:

        importance_values = abs(
            shap_values[0]
        )

    importance_df = pd.DataFrame({

        "feature":
            scaled_df.columns,

        "importance":
            importance_values.flatten(),
    })

    importance_df = (
        importance_df
        .sort_values(
            by="importance",
            ascending=False
        )
        .reset_index(
            drop=True
        )
    )

    return importance_df

# =============================================================================
# EXECUTIVE SHAP SUMMARY
# =============================================================================

def executive_shap_summary(
    importance_df
):
    """
    Generate executive SHAP narrative.
    """

    top_features = (
        importance_df
        .head(5)["feature"]
        .tolist()
    )

    summary = (
        "Primary default-risk drivers are: "
        + ", ".join(top_features)
        + "."
    )

    print(
        "\n[KRONOS] EXECUTIVE SHAP SUMMARY"
    )

    print(summary)

    return summary

# =============================================================================
# SHAP SUMMARY PLOT
# =============================================================================

def generate_summary_plot(
    shap_values,
    scaled_df
):
    """
    Generate SHAP summary visualization.
    """

    try:

        plt.figure(figsize=(12, 6))

        shap.summary_plot(
            shap_values,
            scaled_df,
            show=False
        )

        plt.tight_layout()

        print("[KRONOS] SHAP summary plot generated")

    except Exception as e:

        print("[KRONOS ERROR] Failed generating SHAP plot")
        print(e)

# =============================================================================
# FORCE PLOT
# =============================================================================

def generate_force_plot(
    explainer,
    shap_values,
    scaled_df
):
    """
    Generate local SHAP force plot.
    """

    try:

        force_plot = shap.force_plot(
            explainer.expected_value,
            shap_values[0],
            scaled_df.iloc[0],
            matplotlib=True,
            show=False,
        )

        print("[KRONOS] SHAP force plot generated")

        return force_plot

    except Exception as e:

        print("[KRONOS ERROR] Failed generating force plot")
        print(e)

        return None

# =============================================================================
# FULL SHAP PIPELINE
# =============================================================================

def run_shap_pipeline(
    borrower_data
):
    """
    Run full enterprise SHAP workflow.
    """

    results = generate_shap_values(
        borrower_data
    )

    if results is None:

        return None

    (
        explainer,
        shap_values,
        scaled_df
    ) = results

    # -------------------------------------------------------------------------
    # LOCAL EXPLANATION
    # -------------------------------------------------------------------------

    top_drivers = local_explanation(
        explainer,
        shap_values,
        scaled_df
    )

    # -------------------------------------------------------------------------
    # GLOBAL IMPORTANCE
    # -------------------------------------------------------------------------

    importance_df = global_feature_importance(
        shap_values,
        scaled_df
    )

    executive_summary = (
        executive_shap_summary(
            importance_df
        )
    )

    # -------------------------------------------------------------------------
    # VISUALIZATIONS
    # -------------------------------------------------------------------------

    generate_summary_plot(
        shap_values,
        scaled_df
    )

    generate_force_plot(
        explainer,
        shap_values,
        scaled_df
    )

    print(
        "\n[KRONOS] SHAP PIPELINE COMPLETED"
    )

    return {

        "top_drivers":
            top_drivers,

        "importance_df":
            importance_df,

        "executive_summary":
            executive_summary,
    }

# =============================================================================
# SAMPLE BORROWER
# =============================================================================

SAMPLE_BORROWER = {
    "dti_ratio": 0.45,
    "credit_utilization": 0.71,
    "payment_burden_ratio": 0.38,
    "total_delinquency": 2,
    "high_delinquency_flag": 1,
    "loan_to_income_ratio": 0.62,
    "young_borrower_flag": 0,
    "senior_borrower_flag": 0,
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":

    run_shap_pipeline(
        SAMPLE_BORROWER
    )

# =============================================================================
# END OF FILE
# =============================================================================