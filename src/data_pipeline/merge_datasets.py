# =============================================================================
# KRONOS — MASTER DATASET ENGINE
# File: src/data_pipeline/merge_datasets.py
# =============================================================================

import pandas as pd
import numpy as np

from src.shared.config import (
    ENGINEERED_FEATURES_DATA,
    MERGED_CREDIT_DATA,
)

# =============================================================================
# LOAD ENGINEERED DATASET
# =============================================================================

def load_engineered_dataset():

    try:

        df = pd.read_csv(
            ENGINEERED_FEATURES_DATA
        )

        print("\n" + "=" * 80)
        print("[KRONOS] ENGINEERED DATASET LOADED")
        print("=" * 80)

        print(f"Shape: {df.shape}")

        return df

    except Exception as e:

        print("[KRONOS ERROR] Failed loading engineered dataset")
        print(e)

        return pd.DataFrame()

# =============================================================================
# ADD DATASET SOURCE
# =============================================================================

def add_dataset_source(df):

    df["dataset_source"] = "KRONOS_MASTER"

    print("[KRONOS] Dataset source added")

    return df

# =============================================================================
# OPTIMIZE DTYPES
# =============================================================================

def optimize_dtypes(df):

    for col in df.columns:

        try:

            if df[col].dtype == "int64":

                df[col] = df[col].astype(
                    np.int32
                )

            elif df[col].dtype == "float64":

                df[col] = df[col].astype(
                    np.float32
                )

        except (TypeError, ValueError, OverflowError):
            pass

    print("[KRONOS] Data types optimized")

    return df

# =============================================================================
# VALIDATE DATASET
# =============================================================================

def validate_dataset(df):

    required_cols = [

    "target_default",

    "dti_ratio",

    "credit_utilization",

    "payment_burden_ratio",

    "loan_to_income_ratio",

    "total_delinquency",

    "high_delinquency_flag",

    "young_borrower_flag",

    "senior_borrower_flag",

    "dataset_source",

    "behavioral_risk_score",

    "risk_migration_score",

    "early_warning_score",

    "ifrs_stage",

    "watchlist_flag",
]

    missing = [
        col
        for col in required_cols
        if col not in df.columns
    ]

    if missing:

        raise ValueError(
            f"Missing columns: {missing}"
        )

    print("[KRONOS] Dataset validation passed")

# =============================================================================
# BUILD MASTER DATASET
# =============================================================================

def build_master_dataset():

    df = load_engineered_dataset()

    if df.empty:

        return pd.DataFrame()

    df = add_dataset_source(df)

    df = optimize_dtypes(df)

    df = df.drop_duplicates()

    validate_dataset(df)

    print(f"[KRONOS] Final Shape: {df.shape}")

    return df

# =============================================================================
# SAVE DATASET
# =============================================================================

def save_master_dataset(df):

    MERGED_CREDIT_DATA.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        MERGED_CREDIT_DATA,
        index=False
    )

    print("\n[KRONOS] Master dataset saved:")
    print(MERGED_CREDIT_DATA)

# =============================================================================
# OVERVIEW
# =============================================================================

def dataset_overview(df):

    print("\n" + "=" * 80)
    print("[KRONOS] MASTER DATASET OVERVIEW")
    print("=" * 80)

    print(df.head())

    print("\nShape:")
    print(df.shape)

    print("\nColumns:")
    print(df.columns.tolist())

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":

    df = build_master_dataset()

    if not df.empty:

        save_master_dataset(df)

        dataset_overview(df)

        print(
            "\n[KRONOS] DATA MERGING PIPELINE COMPLETED"
        )

# =============================================================================
# END OF FILE
# =============================================================================
