# =============================================================================
# KRONOS — FEATURE ENGINEERING ENGINE
# File: src/data_pipeline/feature_engineering.py
# =============================================================================

import pandas as pd
import numpy as np

from src.shared.config import (
    CLEANED_CREDIT_DATA,
    ENGINEERED_FEATURES_DATA,
)

from src.shared.utils import normalize_ifrs_stage_series, safe_divide

# =============================================================================
# LOAD CLEANED DATASET
# =============================================================================

def load_cleaned_dataset():

    try:

        df = pd.read_csv(CLEANED_CREDIT_DATA)

        print("\n" + "=" * 80)
        print("[KRONOS] CLEANED DATASET LOADED")
        print("=" * 80)

        print(f"Shape: {df.shape}")

        return df

    except Exception as e:

        print("[KRONOS ERROR] Failed loading cleaned dataset")
        print(e)

        return pd.DataFrame()

# =============================================================================
# DTI RATIO
# =============================================================================

def create_dti_ratio(df):

    df["dti_ratio"] = df.apply(
        lambda x: safe_divide(
            x["loan_amount"],
            x["annual_income"]
        ),
        axis=1
    )

    print("[KRONOS] DTI ratio created")

    return df

# =============================================================================
# CREDIT UTILIZATION
# =============================================================================

def create_credit_utilization(df):

    df["credit_utilization"] = df.apply(
        lambda x: safe_divide(
            x["revolving_balance"],
            x["credit_limit"]
        ),
        axis=1
    )

    print("[KRONOS] Credit utilization created")

    return df

# =============================================================================
# PAYMENT BURDEN
# =============================================================================

def create_payment_burden_ratio(df):

    df["payment_burden_ratio"] = df.apply(
        lambda x: safe_divide(
            x["monthly_payment"] * 12,
            x["annual_income"]
        ),
        axis=1
    )

    print("[KRONOS] Payment burden ratio created")

    return df

# =============================================================================
# LOAN TO INCOME
# =============================================================================

def create_loan_to_income_ratio(df):

    df["loan_to_income_ratio"] = df.apply(
        lambda x: safe_divide(
            x["loan_amount"],
            x["annual_income"]
        ),
        axis=1
    )

    print("[KRONOS] Loan-to-income ratio created")

    return df

# =============================================================================
# DELINQUENCY FEATURES
# =============================================================================

def create_delinquency_features(df):

    df["total_delinquency"] = df["delinq_2yrs"]

    df["high_delinquency_flag"] = (
        df["total_delinquency"] >= 3
    ).astype(int)

    print("[KRONOS] Delinquency features created")

    return df

# =============================================================================
# AGE FEATURES
# =============================================================================

def create_age_features(df):

    df["young_borrower_flag"] = (
        df["age"] < 25
    ).astype(int)

    df["senior_borrower_flag"] = (
        df["age"] >= 60
    ).astype(int)

    print("[KRONOS] Age features created")

    return df

# =============================================================================
# RISK SEGMENT
# =============================================================================

def create_risk_segment(df):

    conditions = [
        (df["target_default"] == 0),
        (df["target_default"] == 1),
    ]

    values = [
        "LOW_RISK",
        "HIGH_RISK"
    ]

    df["risk_segment"] = np.select(
        conditions,
        values,
        default="UNKNOWN"
    )

    print("[KRONOS] Risk segment created")

    return df

# =============================================================================
# CREDIT HEADROOM
# =============================================================================

def create_credit_headroom(df):

    df["credit_headroom"] = (
        df["credit_limit"]
        - df["revolving_balance"]
    )

    print("[KRONOS] Credit headroom created")

    return df


# =============================================================================
# CREDIT BUFFER RATIO
# =============================================================================

def create_credit_buffer_ratio(df):

    df["credit_buffer_ratio"] = df.apply(
        lambda x: safe_divide(
            x["credit_headroom"],
            x["credit_limit"]
        ),
        axis=1
    )

    print("[KRONOS] Credit buffer ratio created")

    return df


# =============================================================================
# DISPOSABLE INCOME
# =============================================================================

def create_disposable_income(df):

    df["disposable_income"] = (
        df["annual_income"]
        - (df["monthly_payment"] * 12)
    )

    print("[KRONOS] Disposable income created")

    return df


# =============================================================================
# EMPLOYMENT STABILITY
# =============================================================================

def create_employment_stability(df):

    df["employment_stability_score"] = df.apply(
        lambda x: safe_divide(
            x["employment_years"],
            x["age"]
        ),
        axis=1
    )

    print("[KRONOS] Employment stability score created")

    return df


# =============================================================================
# DELINQUENCY SEVERITY
# =============================================================================

def create_delinquency_severity(df):

    df["delinquency_severity"] = (
        df["delinq_2yrs"]
        * df["days_past_due"]
    )

    print("[KRONOS] Delinquency severity created")

    return df

# =============================================================================
# AGE RISK SCORE
# =============================================================================

def create_age_risk_score(df):

    df["age_risk_score"] = np.where(
        (df["age"] < 25)
        |
        (df["age"] > 65),
        1,
        0
    )

    print("[KRONOS] Age risk score created")

    return df


# =============================================================================
# COLLATERAL SHORTFALL
# =============================================================================

def create_collateral_shortfall(df):

    df["collateral_shortfall_ratio"] = np.where(
        df["collateral_coverage_ratio"] < 1,
        1 - df["collateral_coverage_ratio"],
        0
    )

    print("[KRONOS] Collateral shortfall created")

    return df

# =============================================================================
# FEATURE ENGINEERING PIPELINE
# =============================================================================

def engineer_features():

    df = load_cleaned_dataset()

    if df.empty:

        return pd.DataFrame()

    # Existing Features
    df = create_dti_ratio(df)

    df = create_credit_utilization(df)

    df = create_payment_burden_ratio(df)

    df = create_loan_to_income_ratio(df)

    df = create_delinquency_features(df)

    df = create_age_features(df)

    # New Enterprise Features
    df = create_credit_headroom(df)

    df = create_credit_buffer_ratio(df)

    df = create_disposable_income(df)

    df = create_employment_stability(df)

    df = create_delinquency_severity(df)

    df = create_age_risk_score(df)

    df = create_collateral_shortfall(df)

    # Interaction Features
    df["utilization_x_delinquency"] = (
        df["credit_utilization"]
        * df["delinq_2yrs"]
    )

    df["dti_x_behavioral_risk"] = (
        df["dti_ratio"]
        * df["behavioral_risk_score"]
    )

    df["macro_x_behavioral"] = (
        df["macro_sensitivity"]
        * df["behavioral_risk_score"]
    )

    df["risk_migration_x_ews"] = (
        df["risk_migration_score"]
        * df["early_warning_score"]
    )

    # IFRS9 Features
    df["ifrs_stage"] = normalize_ifrs_stage_series(
        df["ifrs_stage"]
    )

    df["ifrs_stage_2_flag"] = (
        df["ifrs_stage"] == "STAGE 2"
    ).astype(int)

    df["ifrs_stage_3_flag"] = (
        df["ifrs_stage"] == "STAGE 3"
    ).astype(int)

    # Final Risk Segment
    df = create_risk_segment(df)

    print(f"[KRONOS] Final Shape: {df.shape}")

    return df

# =============================================================================
# SAVE ENGINEERED DATA
# =============================================================================

def save_engineered_data(df):

    ENGINEERED_FEATURES_DATA.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        ENGINEERED_FEATURES_DATA,
        index=False
    )

    print("\n[KRONOS] Engineered dataset saved:")
    print(ENGINEERED_FEATURES_DATA)

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":

    df = engineer_features()

    if not df.empty:

        save_engineered_data(df)

        print(
            "\n[KRONOS] FEATURE ENGINEERING COMPLETED"
        )

# =============================================================================
# END OF FILE
# =============================================================================
