# =============================================================================
# KRONOS — LOSS GIVEN DEFAULT (LGD) MODEL TRAINING ENGINE
# File: src/credit_risk/train_lgd_model.py
# =============================================================================

import json
import joblib
import pandas as pd
import numpy as np

from xgboost import XGBRegressor
from lightgbm import LGBMRegressor

from sklearn.ensemble import VotingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

from sklearn.preprocessing import StandardScaler

from src.shared.config import (
    LGD_FEATURE_COLUMNS_FILE as LGD_FEATURE_FILE,
    LGD_METRICS_FILE,
    LGD_MODEL_FILE,
    LGD_SCALER_FILE,
    MERGED_CREDIT_DATA,
    RANDOM_STATE,
    TEST_SIZE,
)

# =============================================================================
# LOAD DATASET
# =============================================================================

def load_master_dataset():
    """
    Load KRONOS merged dataset.
    """

    try:

        df = pd.read_csv(MERGED_CREDIT_DATA)

        print("\n" + "=" * 80)
        print("[KRONOS] LGD DATASET LOADED")
        print("=" * 80)

        print(f"Shape: {df.shape}")

        return df

    except Exception as e:

        print("[KRONOS ERROR] Failed loading dataset")
        print(e)

        return pd.DataFrame()

# =============================================================================
# SYNTHETIC LGD TARGET
# =============================================================================

def create_lgd_target(df):
    """
    Create synthetic LGD target for modeling.
    """

    np.random.seed(RANDOM_STATE)

    # Simulated LGD generation logic
    base_lgd = (
        (df.get("credit_utilization", 0) * 0.35)
        + (df.get("dti_ratio", 0) * 0.25)
        + (df.get("loan_to_income_ratio", 0) * 0.20)
        + (df.get("total_delinquency", 0) * 0.05)
    )

    noise = np.random.normal(
        0,
        0.05,
        len(df)
    )

    lgd = base_lgd + noise

    lgd = np.clip(
        lgd,
        0.05,
        0.95
    )

    df["lgd_target"] = lgd

    print("[KRONOS] Synthetic LGD target created")

    return df

# =============================================================================
# PREPARE TRAINING DATA
# =============================================================================

def prepare_training_data(df):
    """
    Prepare LGD features and target.
    """

    print("\n[KRONOS] PREPARING LGD TRAINING DATA")

    exclude_cols = [
        "target_default",
        "dataset_source",
        "risk_segment",
        "lgd_target",
    ]

    feature_cols = [
        col
        for col in df.columns
        if col not in exclude_cols
    ]

    X = df[feature_cols].copy()

    y = df["lgd_target"].copy()

    # ---------------------------------------------------------
    # Missing values
    # ---------------------------------------------------------

    X = X.fillna(0)

    # ---------------------------------------------------------
    # Encode categorical variables
    # ---------------------------------------------------------

    categorical_cols = X.select_dtypes(
        include=["object", "string"]
    ).columns

    if len(categorical_cols) > 0:

        X = pd.get_dummies(
            X,
            columns=categorical_cols,
            drop_first=True
        )

    feature_cols = X.columns.tolist()

    # ---------------------------------------------------------
    # Scaling
    # ---------------------------------------------------------

    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(X)

    print(f"[KRONOS] LGD Features: {len(feature_cols)}")

    print(f"[KRONOS] Samples: {len(X)}")

    return (
        X_scaled,
        y,
        scaler,
        feature_cols
    )

# =============================================================================
# BUILD XGBOOST MODEL
# =============================================================================

def build_xgb_model():
    """
    Build XGBoost LGD model.
    """

    model = XGBRegressor(
        n_estimators=250,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=RANDOM_STATE,
    )

    return model

# =============================================================================
# BUILD LIGHTGBM MODEL
# =============================================================================

def build_lgbm_model():
    """
    Build LightGBM LGD model.
    """

    model = LGBMRegressor(
        n_estimators=250,
        max_depth=5,
        learning_rate=0.05,
        random_state=RANDOM_STATE,
    )

    return model

# =============================================================================
# BUILD ENSEMBLE MODEL
# =============================================================================

def build_ensemble_model():
    """
    Build ensemble LGD model.
    """

    xgb_model = build_xgb_model()

    lgbm_model = build_lgbm_model()

    ensemble = VotingRegressor(
        estimators=[
            ("xgb", xgb_model),
            ("lgbm", lgbm_model),
        ]
    )

    return ensemble

# =============================================================================
# TRAIN LGD MODEL
# =============================================================================

def train_lgd_model():
    """
    Train enterprise LGD model.
    """

    df = load_master_dataset()

    if df.empty:

        return None

    df = create_lgd_target(df)

    (
        X,
        y,
        scaler,
        feature_cols
    ) = prepare_training_data(df)

    (
        X_train,
        X_test,
        y_train,
        y_test
    ) = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
    )

    print("\n" + "=" * 80)
    print("[KRONOS] TRAINING LGD MODEL")
    print("=" * 80)

    model = build_ensemble_model()

    model.fit(X_train, y_train)

    print("[KRONOS] LGD model training completed")

    # -------------------------------------------------------------------------
    # PREDICTIONS
    # -------------------------------------------------------------------------

    predictions = model.predict(X_test)

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    rmse = np.sqrt(
        mean_squared_error(
            y_test,
            predictions
        )
    )

    r2 = r2_score(
        y_test,
        predictions
    )

    metrics = {
        "mae": round(float(mae), 4),
        "rmse": round(float(rmse), 4),
        "r2_score": round(float(r2), 4),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "feature_count": len(feature_cols),
    }

    print("\n[KRONOS] LGD MODEL PERFORMANCE")

    for key, value in metrics.items():

        print(f"{key}: {value}")

    return (
        model,
        scaler,
        feature_cols,
        metrics
    )

# =============================================================================
# SAVE MODEL ARTIFACTS
# =============================================================================

def save_artifacts(
    model,
    scaler,
    feature_cols,
    metrics
):
    """
    Save LGD model artifacts.
    """

    # Save model
    joblib.dump(
        model,
        LGD_MODEL_FILE
    )

    print(f"\n[KRONOS] LGD model saved:")
    print(LGD_MODEL_FILE)

    # Save scaler
    joblib.dump(
        scaler,
        LGD_SCALER_FILE
    )

    print(f"\n[KRONOS] LGD scaler saved:")
    print(LGD_SCALER_FILE)

    # Save features
    with open(
        LGD_FEATURE_FILE,
        "w"
    ) as f:

        json.dump(
            feature_cols,
            f
        )

    print(f"\n[KRONOS] LGD feature columns saved:")
    print(LGD_FEATURE_FILE)

    # Save metrics
    with open(
        LGD_METRICS_FILE,
        "w"
    ) as f:

        json.dump(
            metrics,
            f,
            indent=4
        )

    print(f"\n[KRONOS] LGD metrics saved:")
    print(LGD_METRICS_FILE)

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":

    results = train_lgd_model()

    if results is not None:

        (
            model,
            scaler,
            feature_cols,
            metrics
        ) = results

        save_artifacts(
            model,
            scaler,
            feature_cols,
            metrics
        )

        print("\n[KRONOS] LGD MODEL PIPELINE COMPLETED")

# =============================================================================
# END OF FILE
# =============================================================================
