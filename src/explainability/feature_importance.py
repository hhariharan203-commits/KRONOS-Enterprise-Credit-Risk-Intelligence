# =============================================================================
# KRONOS — ENTERPRISE FEATURE IMPORTANCE ENGINE
# File: src/explainability/feature_importance.py
# =============================================================================

import json
import joblib
import pandas as pd
import numpy as np

from src.shared.config import (
    PD_MODEL_FILE,
    FEATURE_COLUMNS_FILE,
    MODEL_METRICS_FILE,
)

# =============================================================================
# FEATURE CATEGORY MAPPING
# =============================================================================

FEATURE_CATEGORY_MAP = {

    # -------------------------------------------------------------------------
    # INCOME
    # -------------------------------------------------------------------------

    "annual_income": "INCOME",
    "disposable_income": "INCOME",

    # -------------------------------------------------------------------------
    # EMPLOYMENT
    # -------------------------------------------------------------------------

    "employment_years": "EMPLOYMENT",
    "employment_stability_score": "EMPLOYMENT",
    "income_stability_score": "EMPLOYMENT",

    # -------------------------------------------------------------------------
    # LEVERAGE
    # -------------------------------------------------------------------------

    "dti_ratio": "LEVERAGE",
    "loan_to_income_ratio": "LEVERAGE",

    # -------------------------------------------------------------------------
    # CREDIT BEHAVIOR
    # -------------------------------------------------------------------------

    "credit_utilization": "CREDIT BEHAVIOR",

    # -------------------------------------------------------------------------
    # AFFORDABILITY
    # -------------------------------------------------------------------------

    "payment_burden_ratio": "AFFORDABILITY",
    "payment_shock_index": "AFFORDABILITY",

    # -------------------------------------------------------------------------
    # DELINQUENCY
    # -------------------------------------------------------------------------

    "total_delinquency": "DELINQUENCY",
    "high_delinquency_flag": "DELINQUENCY",
    "delinq_2yrs": "DELINQUENCY",
    "days_past_due": "DELINQUENCY",
    "delinquency_severity": "DELINQUENCY",

    # -------------------------------------------------------------------------
    # DEMOGRAPHICS
    # -------------------------------------------------------------------------

    "young_borrower_flag": "DEMOGRAPHICS",
    "senior_borrower_flag": "DEMOGRAPHICS",
    "age": "DEMOGRAPHICS",
    "age_risk_score": "DEMOGRAPHICS",

    # -------------------------------------------------------------------------
    # LOAN STRUCTURE
    # -------------------------------------------------------------------------

    "loan_amount": "LOAN_STRUCTURE",
    "loan_term": "LOAN_STRUCTURE",
    "monthly_payment": "LOAN_STRUCTURE",

    # -------------------------------------------------------------------------
    # COLLATERAL
    # -------------------------------------------------------------------------

    "collateral_value": "COLLATERAL",
    "collateral_coverage_ratio": "COLLATERAL",
    "collateral_shortfall_ratio": "COLLATERAL",

    # -------------------------------------------------------------------------
    # MACRO
    # -------------------------------------------------------------------------

    "interest_rate": "MACRO",
    "interest_rate_sensitivity": "MACRO",
    "unemployment_sensitivity": "MACRO",
    "macro_sensitivity": "MACRO",
    "macro_stress_score": "MACRO",
    "macro_x_behavioral": "MACRO",

    # -------------------------------------------------------------------------
    # BEHAVIORAL
    # -------------------------------------------------------------------------

    "utilization_x_delinquency": "BEHAVIORAL",
    "risk_migration_x_ews": "BEHAVIORAL",
    "risk_migration_score": "BEHAVIORAL",
    "credit_stress_score": "BEHAVIORAL",
    "behavioral_risk_score": "BEHAVIORAL",
    "dti_x_behavioral_risk": "BEHAVIORAL",

    # -------------------------------------------------------------------------
    # EARLY WARNING SYSTEM
    # -------------------------------------------------------------------------

    "early_warning_score": "EWS",
    "watchlist_flag": "EWS",

    # -------------------------------------------------------------------------
    # LOSS SEVERITY
    # -------------------------------------------------------------------------

    "lgd_seed": "LOSS_SEVERITY",
    "recovery_rate": "LOSS_SEVERITY",
    "default_severity": "LOSS_SEVERITY",

    # -------------------------------------------------------------------------
    # EXPOSURE
    # -------------------------------------------------------------------------

    "ead_seed": "EXPOSURE",
    "credit_limit": "EXPOSURE",
    "revolving_balance": "EXPOSURE",
    "credit_headroom": "EXPOSURE",
    "credit_buffer_ratio": "EXPOSURE",
    "exposure_utilization": "EXPOSURE",

    # -------------------------------------------------------------------------
    # IFRS9
    # -------------------------------------------------------------------------

    "ifrs_stage_2_flag": "IFRS9",
    "ifrs_stage_3_flag": "IFRS9",
    "ifrs_stage_Stage_2": "IFRS9",
    "ifrs_stage_Stage_3": "IFRS9",
    "ifrs_stage_STAGE 2": "IFRS9",
    "ifrs_stage_STAGE 3": "IFRS9",
}

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
# LOAD FEATURE COLUMNS
# =============================================================================

def load_feature_columns():
    """
    Load feature columns.
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
# EXTRACT FEATURE IMPORTANCE
# =============================================================================

def extract_feature_importance(
    model,
    feature_cols
):
    """
    Extract feature importance from ensemble model.
    """

    print("\n" + "=" * 80)
    print("[KRONOS] EXTRACTING FEATURE IMPORTANCE")
    print("=" * 80)

    importance_scores = np.zeros(
        len(feature_cols)
    )

    # -------------------------------------------------------------------------
    # ENSEMBLE MODEL HANDLING
    # -------------------------------------------------------------------------

    if hasattr(
        model,
        "estimators_"
    ):

        for estimator in model.estimators_:

            if hasattr(
                estimator,
                "feature_importances_"
            ):

                importance_scores += (
                    estimator.feature_importances_
                )

        importance_scores = (
            importance_scores
            / len(model.estimators_)
        )

    else:

        importance_scores = (
            model.feature_importances_
        )

    # -------------------------------------------------------------------------
    # BUILD DATAFRAME
    # -------------------------------------------------------------------------

    importance_df = pd.DataFrame({

        "feature":
            feature_cols,

        "importance":
            importance_scores,
    })

    # -------------------------------------------------------------------------
    # REMOVE IDENTIFIER COLUMNS
    # -------------------------------------------------------------------------

    importance_df = importance_df[
        ~importance_df["feature"].isin([
            "borrower_id",
            "customer_id",
            "loan_id",
            "account_id",
        ])
    ]

    # -------------------------------------------------------------------------
    # NORMALIZE TO PERCENTAGE
    # -------------------------------------------------------------------------

    total_importance = importance_df["importance"].sum()

    importance_df["importance_pct"] = (
        (
            importance_df["importance"]
            / total_importance
        )
        * 100
        if total_importance > 0
        else 0
    )

    # -------------------------------------------------------------------------
    # FEATURE CATEGORIES
    # -------------------------------------------------------------------------

    importance_df["category"] = (

        importance_df["feature"]

        .map(FEATURE_CATEGORY_MAP)

        .fillna("OTHER")
    )

    # -------------------------------------------------------------------------
    # SORT DESCENDING
    # -------------------------------------------------------------------------

    importance_df = (

        importance_df

        .sort_values(
            by="importance_pct",
            ascending=False
        )

        .reset_index(
            drop=True
        )
    )

    return importance_df

# =============================================================================
# CATEGORY IMPORTANCE
# =============================================================================

def category_importance_summary(
    importance_df
):
    """
    Aggregate feature importance by category.
    """

    category_df = (
        importance_df
        .groupby("category")["importance_pct"]
        .sum()
        .reset_index()
    )

    category_df = category_df.sort_values(
        by="importance_pct",
        ascending=False
    )

    return category_df

# =============================================================================
# TOP FEATURE DRIVERS
# =============================================================================

def top_feature_drivers(
    importance_df,
    top_n=10
):
    """
    Get top enterprise risk drivers.
    """

    return importance_df.head(top_n)

# =============================================================================
# MODEL INTERPRETATION
# =============================================================================

def model_behavior_summary(
    category_df
):
    """
    Generate executive model interpretation.
    """

    top_category = (
        category_df.iloc[0]["category"]
    )

    top_importance = round(
        category_df.iloc[0]["importance_pct"],
        2
    )

    summary = (
        f"KRONOS credit risk model is primarily driven by "
        f"{top_category.lower()} signals, contributing "
        f"{top_importance}% of total predictive importance."
    )

    return summary

# =============================================================================
# PORTFOLIO EXPLAINABILITY SUMMARIES
# =============================================================================

def key_risk_driver_report(
    importance_df,
    top_n=5
):
    """
    Build a compact key-driver report for executives.
    """

    if importance_df is None or importance_df.empty:

        return []

    return (
        importance_df
        .head(top_n)[
            [
                "feature",
                "category",
                "importance_pct",
            ]
        ]
        .round(
            {
                "importance_pct": 2
            }
        )
        .to_dict("records")
    )


def executive_explanation_summary(
    category_df,
    key_drivers
):
    """
    Summarize portfolio-level model drivers.
    """

    if category_df is None or category_df.empty:

        return {

            "dominant_risk_category":
                "UNKNOWN",

            "driver_count":
                0,

            "summary":
                "No feature-importance results are available.",
        }

    top_category = category_df.iloc[0]

    return {

        "dominant_risk_category":
            top_category["category"],

        "dominant_category_importance_pct":
            round(
                float(
                    top_category["importance_pct"]
                ),
                2
            ),

        "driver_count":
            len(key_drivers),

        "summary":
            (
                f"Portfolio-level model behavior is led by "
                f"{top_category['category']} signals, supported by "
                f"{len(key_drivers)} monitored key drivers."
            ),
    }


def model_reasoning_summary(
    summary,
    key_drivers
):
    """
    Convert model behavior into a plain-language reasoning summary.
    """

    driver_names = [
        driver["feature"]
        for driver in key_drivers[:3]
    ]

    driver_text = (
        ", ".join(driver_names)
        if driver_names
        else "no available drivers"
    )

    return (
        f"{summary} The leading monitored drivers are "
        f"{driver_text}."
    )


def portfolio_level_explainability(
    importance_df,
    category_df
):
    """
    Assemble portfolio-level explainability outputs.
    """

    key_drivers = key_risk_driver_report(
        importance_df
    )

    executive_summary = executive_explanation_summary(
        category_df,
        key_drivers
    )

    reasoning_summary = model_reasoning_summary(
        model_behavior_summary(category_df)
        if category_df is not None and not category_df.empty
        else "Model behavior summary is unavailable.",
        key_drivers
    )

    return {

        "key_risk_driver_report":
            key_drivers,

        "global_drivers":
            key_drivers,

        "local_drivers":
            key_drivers[:3],

        "executive_explanation_summary":
            executive_summary,

        "model_reasoning_summary":
            reasoning_summary,

        "model_limitations":
            model_card()["limitations"],
    }


def model_card():
    """
    Return the KRONOS PD model card for governance review.
    """

    return {

        "model_name":
            "KRONOS Probability of Default Model",

        "purpose":
            (
                "Estimate borrower probability of default for portfolio "
                "risk analytics, provisioning support, dashboarding, and "
                "decision-support workflows."
            ),

        "assumptions":
            [
                "Input portfolio features follow the KRONOS scored portfolio contract.",
                "Model artifacts are loaded from the governed local model directory.",
                "Feature columns remain compatible with the saved scaler and model artifacts.",
                "Outputs support analyst review and portfolio monitoring.",
            ],

        "limitations":
            [
                "The project is a portfolio-grade analytics platform, not a production banking model.",
                "Training data includes synthetic and simulated credit-risk signals.",
                "LGD and EAD targets are synthetic approximations for demonstration.",
                "Explainability outputs support transparency but do not replace independent model validation.",
            ],

        "training_data_notes":
            (
                "KRONOS uses a generated institutional-style credit portfolio "
                "with engineered behavioral, macro, credit, collateral, and "
                "IFRS9 features."
            ),

        "synthetic_data_disclosure":
            (
                "Synthetic data and target construction are used for portfolio "
                "demonstration and interview-ready model-risk discussion."
            ),
    }

# =============================================================================
# PRINT FEATURE REPORT
# =============================================================================

def print_feature_report(
    top_features,
    category_df,
    summary
):
    """
    Print enterprise feature intelligence report.
    """

    print("\n" + "=" * 80)
    print("[KRONOS] FEATURE IMPORTANCE REPORT")
    print("=" * 80)

    print("\nTOP FEATURE DRIVERS\n")

    for _, row in top_features.iterrows():

        print(
            f"{row['feature']} | "
            f"{row['importance_pct']:.2f}% | "
            f"{row['category']}"
        )

    print("\n" + "-" * 80)

    print("\nCATEGORY IMPORTANCE\n")

    for _, row in category_df.iterrows():

        print(
            f"{row['category']} | "
            f"{row['importance_pct']:.2f}%"
        )

    print("\n" + "-" * 80)

    print("\nEXECUTIVE INTERPRETATION\n")

    print(summary)

    print("=" * 80)

# =============================================================================
# RUN FULL FEATURE ANALYSIS
# =============================================================================

def run_feature_analysis():
    """
    Run full feature governance pipeline.
    """

    model = load_model()

    feature_cols = load_feature_columns()

    if (
        model is None
        or not feature_cols
    ):

        print("[KRONOS ERROR] Missing model artifacts")

        return None

    # -------------------------------------------------------------------------
    # FEATURE IMPORTANCE
    # -------------------------------------------------------------------------

    importance_df = extract_feature_importance(
        model,
        feature_cols
    )

    # -------------------------------------------------------------------------
    # CATEGORY ANALYSIS
    # -------------------------------------------------------------------------

    category_df = category_importance_summary(
        importance_df
    )

    # -------------------------------------------------------------------------
    # TOP DRIVERS
    # -------------------------------------------------------------------------

    top_features = top_feature_drivers(
        importance_df
    )

    # -------------------------------------------------------------------------
    # EXECUTIVE SUMMARY
    # -------------------------------------------------------------------------

    summary = model_behavior_summary(
        category_df
    )

    explainability_summary = portfolio_level_explainability(
        importance_df,
        category_df
    )

    card = model_card()

    # -------------------------------------------------------------------------
    # REPORTING
    # -------------------------------------------------------------------------

    print_feature_report(
        top_features,
        category_df,
        summary
    )

    save_feature_importance_report(
        importance_df,
        category_df,
        summary
    )

    return {

        "feature_importance":
            importance_df,

        "category_importance":
            category_df,

        "summary":
            summary,

        "portfolio_explainability":
            explainability_summary,

        "model_card":
            card,
    }

# =============================================================================
# SAVE FEATURE IMPORTANCE REPORT
# =============================================================================

def save_feature_importance_report(
    importance_df,
    category_df,
    summary
):
    """
    Save feature governance report.
    """

    importance_df.to_csv(
        "reports/feature_importance.csv",
        index=False
    )

    category_df.to_csv(
        "reports/category_importance.csv",
        index=False
    )

    with open(
        "reports/feature_summary.txt",
        "w"
    ) as f:

        f.write(summary)

    print(
        "\n[KRONOS] Feature importance report saved"
    )

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":

    run_feature_analysis()

    print("\n[KRONOS] FEATURE IMPORTANCE ENGINE COMPLETED")

# =============================================================================
# END OF FILE
# =============================================================================
