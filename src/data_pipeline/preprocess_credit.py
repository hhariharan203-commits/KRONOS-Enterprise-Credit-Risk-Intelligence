# =============================================================================
# KRONOS V2 — ENTERPRISE DATA PREPROCESSING ENGINE
# File: src/data_pipeline/preprocess_credit.py
# =============================================================================

import pandas as pd
import numpy as np

from sklearn.impute import SimpleImputer

from src.shared.config import (
    MASTER_CREDIT_DATA,
    CLEANED_CREDIT_DATA,
)
from src.shared.utils import normalize_ifrs_stage_series

# =============================================================================
# LOAD DATASET
# =============================================================================

def load_master_dataset():

    try:

        df = pd.read_csv(
            MASTER_CREDIT_DATA
        )

        print("\n" + "=" * 80)
        print("[KRONOS] MASTER DATASET LOADED")
        print("=" * 80)

        print(f"Shape: {df.shape}")

        return df

    except Exception as e:

        print("[KRONOS ERROR]")
        print(e)

        return pd.DataFrame()

# =============================================================================
# CLEAN COLUMN NAMES
# =============================================================================

def clean_column_names(df):

    df.columns = (
        df.columns
        .str.lower()
        .str.strip()
        .str.replace(" ", "_", regex=False)
        .str.replace("-", "_", regex=False)
        .str.replace("/", "_", regex=False)
    )

    print(
        "[KRONOS] Column names standardized"
    )

    return df

# =============================================================================
# REMOVE DUPLICATES
# =============================================================================

def remove_duplicates(df):

    before = len(df)

    df = df.drop_duplicates()

    removed = before - len(df)

    print(
        f"[KRONOS] Removed {removed} duplicates"
    )

    return df

# =============================================================================
# HANDLE MISSING VALUES
# =============================================================================

def handle_missing_values(df):

    numeric_cols = (
        df.select_dtypes(
            include=[np.number]
        ).columns
    )

    categorical_cols = (
        df.select_dtypes(
            exclude=[np.number]
        ).columns
    )

    if len(numeric_cols) > 0:

        numeric_imputer = (
            SimpleImputer(
                strategy="median"
            )
        )

        df[numeric_cols] = (
            numeric_imputer.fit_transform(
                df[numeric_cols]
            )
        )

    if len(categorical_cols) > 0:

        categorical_imputer = (
            SimpleImputer(
                strategy="most_frequent"
            )
        )

        df[categorical_cols] = (
            categorical_imputer.fit_transform(
                df[categorical_cols]
            )
        )

    print(
        "[KRONOS] Missing value treatment completed"
    )

    return df

# =============================================================================
# PRESERVE CRITICAL COLUMNS
# =============================================================================

CRITICAL_COLUMNS = [

    "industry",
    "region",
    "risk_profile",

    "ifrs_stage",
    "watchlist_flag",

    "behavioral_risk_score",
    "risk_migration_score",
    "early_warning_score",

    "macro_sensitivity",
    "interest_rate_sensitivity",
    "unemployment_sensitivity",

    "lgd_seed",
    "ead_seed",

    "target_default",
]

# =============================================================================
# VALIDATE CRITICAL COLUMNS
# =============================================================================

def validate_critical_columns(df):

    missing = []

    for col in CRITICAL_COLUMNS:

        if col not in df.columns:

            missing.append(col)

    if missing:

        raise ValueError(
            f"Missing critical columns: {missing}"
        )

    print(
        "[KRONOS] Critical column validation passed"
    )

    return True

# =============================================================================
# ENTERPRISE RANGE VALIDATION
# =============================================================================

def validate_numeric_ranges(df):

    checks = {

        "age": (18, 100),

        "annual_income": (100000, 50000000),

        "interest_rate": (0, 60),

        "loan_term": (6, 480),

        "dti_ratio": (0, 10),

        "credit_utilization": (0, 2),

        "payment_burden_ratio": (0, 5),

        "loan_to_income_ratio": (0, 10),

        "collateral_coverage_ratio": (0, 10),

        "lgd_seed": (0, 1),

    }

    for col, (min_val, max_val) in checks.items():

        if col not in df.columns:

            continue

        df[col] = np.clip(
            df[col],
            min_val,
            max_val
        )

    print(
        "[KRONOS] Numeric range validation completed"
    )

    return df

# =============================================================================
# OUTLIER TREATMENT
# =============================================================================

def clip_outliers(df):
    protected_cols = [

        "borrower_id",

        "target_default",

        "watchlist_flag",

        "industry",

        "region",

        "risk_profile",

        "ifrs_stage",

        # EWS PROTECTION

        "behavioral_risk_score",

        "risk_migration_score",

        "early_warning_score",

        # Stress Metrics

        "macro_sensitivity",

        "interest_rate_sensitivity",

        "unemployment_sensitivity",
    ]

    numeric_cols = [

        col

        for col in df.select_dtypes(
            include=[np.number]
        ).columns

        if col not in protected_cols
    ]

    for col in numeric_cols:

        try:

            lower = df[col].quantile(0.01)

            upper = df[col].quantile(0.99)

            df[col] = np.clip(
                df[col],
                lower,
                upper
            )

        except Exception:

            pass

    print(
        "[KRONOS] Outlier treatment completed"
    )

    return df

# =============================================================================
# CREDIT RATIO VALIDATION
# =============================================================================

def validate_credit_ratios(df):

    ratio_cols = [

        "dti_ratio",

        "credit_utilization",

        "payment_burden_ratio",

        "loan_to_income_ratio",

        "collateral_coverage_ratio",
    ]

    for col in ratio_cols:

        if col not in df.columns:

            continue

        df[col] = df[col].replace(
            [np.inf, -np.inf],
            np.nan
        )

        df[col] = df[col].fillna(
            df[col].median()
        )

    print(
        "[KRONOS] Credit ratio validation completed"
    )

    return df

# =============================================================================
# IFRS9 VALIDATION
# =============================================================================

def validate_ifrs9_fields(df):

    if "ifrs_stage" in df.columns:
        df["ifrs_stage"] = normalize_ifrs_stage_series(
            df["ifrs_stage"]
        )

    if "watchlist_flag" in df.columns:

        df["watchlist_flag"] = (
            df["watchlist_flag"]
            .astype(int)
        )

    print(
        "[KRONOS] IFRS9 validation completed"
    )

    return df

# =============================================================================
# EWS VALIDATION
# =============================================================================

def validate_ews_fields(df):

    ews_cols = [

        "behavioral_risk_score",

        "risk_migration_score",

        "early_warning_score",
    ]

    for col in ews_cols:

        if col not in df.columns:

            continue

        df[col] = df[col].clip(
            lower=0
        )

    print(
        "[KRONOS] EWS validation completed"
    )

    return df

# =============================================================================
# MASTER DATASET VALIDATION
# =============================================================================

def validate_dataset(df):

    required_cols = [

        "borrower_id",

        "age",

        "annual_income",

        "loan_amount",

        "interest_rate",

        "employment_years",

        "loan_term",

        "credit_limit",

        "revolving_balance",

        "monthly_payment",

        "delinq_2yrs",

        "collateral_value",

        "target_default",
    ]

    missing = [

        col

        for col in required_cols

        if col not in df.columns
    ]

    if missing:

        raise ValueError(
            f"Missing required columns: {missing}"
        )

    print(
        "[KRONOS] Dataset validation passed"
    )

# =============================================================================
# FULL PREPROCESSING PIPELINE
# =============================================================================

def preprocess_dataset():

    df = load_master_dataset()

    if df.empty:

        return pd.DataFrame()

    df = clean_column_names(df)

    df = remove_duplicates(df)

    df = handle_missing_values(df)

    df = validate_numeric_ranges(df)

    df = validate_credit_ratios(df)

    df = validate_ifrs9_fields(df)

    df = validate_ews_fields(df)

    df = clip_outliers(df)

    validate_dataset(df)

    print(
        f"[KRONOS] Final Shape: {df.shape}"
    )

    return df

# =============================================================================
# SAVE CLEANED DATA
# =============================================================================

def save_cleaned_data(df):

    CLEANED_CREDIT_DATA.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        CLEANED_CREDIT_DATA,
        index=False
    )

    print(
        "\n[KRONOS] Cleaned dataset saved:"
    )

    print(
        CLEANED_CREDIT_DATA
    )

# =============================================================================
# DATA QUALITY REPORT
# =============================================================================

def data_quality_report(df):

    print("\n" + "=" * 80)

    print(
        "[KRONOS] DATA QUALITY REPORT"
    )

    print("=" * 80)

    print(
        f"Rows: {len(df):,}"
    )

    print(
        f"Columns: {len(df.columns)}"
    )

    print(
        f"Duplicates: {df.duplicated().sum()}"
    )

    print(
        f"Missing Values: {df.isnull().sum().sum()}"
    )

    if "target_default" in df.columns:

        print(
            f"Default Rate: "
            f"{round(df['target_default'].mean()*100,2)}%"
        )

    print("=" * 80)

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":

    df = preprocess_dataset()

    if not df.empty:

        save_cleaned_data(df)

        data_quality_report(df)

        print(
            "\n[KRONOS] PREPROCESSING PIPELINE COMPLETED"
        )

# =============================================================================
# END OF FILE
# =============================================================================
