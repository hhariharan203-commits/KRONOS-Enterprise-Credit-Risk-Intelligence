# =============================================================================
# KRONOS — PROBABILITY OF DEFAULT (PD) MODEL TRAINING ENGINE
# File: src/credit_risk/train_pd_model.py
# =============================================================================

import json
import joblib
import sys
import pandas as pd
import numpy as np

from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

from sklearn.ensemble import VotingClassifier
from sklearn.model_selection import train_test_split
from sklearn.utils import ClassifierTags
from sklearn.metrics import (
    accuracy_score,
    roc_auc_score,
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
)

from sklearn.preprocessing import StandardScaler

from src.shared.config import (
    MERGED_CREDIT_DATA,
    PD_MODEL_FILE,
    SCALER_FILE,
    FEATURE_COLUMNS_FILE,
    MODEL_METRICS_FILE,
    RANDOM_STATE,
    TEST_SIZE,
)

from src.credit_risk.model_validation import (
    calculate_psi,
    classify_model_drift,
    detect_overfitting,
)
from src.shared.utils import (
    legacy_ifrs_stage_label,
    normalize_ifrs_stage_series,
)


class KronosXGBClassifier(XGBClassifier):
    """
    Compatibility shim for scikit-learn estimator tags.
    """

    def __sklearn_tags__(self):
        tags = super().__sklearn_tags__()
        tags.estimator_type = "classifier"
        tags.classifier_tags = ClassifierTags()
        tags.target_tags.required = True
        return tags


if __name__ == "__main__":
    sys.modules["src.credit_risk.train_pd_model"] = sys.modules[__name__]

KronosXGBClassifier.__module__ = "src.credit_risk.train_pd_model"

# =============================================================================
# LOAD MASTER DATASET
# =============================================================================

def load_master_dataset():
    """
    Load KRONOS master merged dataset.
    """

    try:

        df = pd.read_csv(MERGED_CREDIT_DATA)

        print("\n" + "=" * 80)
        print("[KRONOS] MASTER DATASET LOADED")
        print("=" * 80)

        print(f"Shape: {df.shape}")

        return df

    except Exception as e:

        print("[KRONOS ERROR] Failed loading dataset")
        print(e)

        return pd.DataFrame()

# =============================================================================
# PREPARE TRAINING DATA
# =============================================================================

def prepare_training_data(df):
    """
    Prepare features and target for PD modeling.
    """

    print("\n[KRONOS] PREPARING TRAINING DATA")

    if "target_default" not in df.columns:

        raise ValueError(
            "target_default column missing from dataset"
        )

    exclude_cols = [
        "target_default",
        "dataset_source",
        "risk_segment",
    ]

    feature_cols = [
        col for col in df.columns
        if col not in exclude_cols
    ]

    X = df[feature_cols].copy()

    y = df["target_default"].copy()

    # Fill missing values
    X = X.fillna(0)

    # ---------------------------------------------------------
    # Encode categorical variables
    # ---------------------------------------------------------

    if "ifrs_stage" in X.columns:
        X["ifrs_stage"] = normalize_ifrs_stage_series(
            X["ifrs_stage"]
        ).apply(legacy_ifrs_stage_label)

    categorical_cols = X.select_dtypes(
        include=["object", "string"]
    ).columns

    if len(categorical_cols) > 0:

        X = pd.get_dummies(
            X,
            columns=categorical_cols,
            drop_first=True
        )

    # Update feature list after encoding
    feature_cols = X.columns.tolist()

    print(f"[KRONOS] Features: {len(feature_cols)}")

    print(f"[KRONOS] Samples: {len(X)}")

    return (
        X,
        y,
        feature_cols
    )

# =============================================================================
# TRAIN TEST SPLIT
# =============================================================================

def split_data(X, y):
    """
    Split training and testing data.
    """

    return train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

# =============================================================================
# BUILD XGBOOST MODEL
# =============================================================================

def build_xgboost():
    """
    Create XGBoost classifier.
    """

    model = KronosXGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=RANDOM_STATE,
        eval_metric="logloss",
    )

    return model

# =============================================================================
# BUILD LIGHTGBM MODEL
# =============================================================================

def build_lightgbm():
    """
    Create LightGBM classifier.
    """

    model = LGBMClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        random_state=RANDOM_STATE,
    )

    return model

# =============================================================================
# BUILD ENSEMBLE MODEL
# =============================================================================

def build_ensemble_model():
    """
    Create ensemble PD model.
    """

    xgb_model = build_xgboost()

    lgbm_model = build_lightgbm()

    ensemble = VotingClassifier(
        estimators=[
            ("xgb", xgb_model),
            ("lgbm", lgbm_model),
        ],
        voting="soft",
    )

    return ensemble

# =============================================================================
# TRAIN MODEL
# =============================================================================

def train_pd_model():
    """
    Train enterprise PD model.
    """

    df = load_master_dataset()

    if df.empty:

        return None

    X, y, feature_cols = prepare_training_data(df)

    (
        X_train,
        X_test,
        y_train,
        y_test
    ) = split_data(X, y)

    scaler = StandardScaler()

    X_train = scaler.fit_transform(
        X_train
    )

    X_test = scaler.transform(
        X_test
    )

    print("\n" + "=" * 80)
    print("[KRONOS] TRAINING PD MODEL")
    print("=" * 80)

    model = build_ensemble_model()

    model.fit(X_train, y_train)

    print("[KRONOS] Model training completed")

    # Predictions
    y_pred = model.predict(X_test)

    y_prob = model.predict_proba(X_test)[:, 1]

    train_prob = model.predict_proba(X_train)[:, 1]

    # ---------------------------------------------------------
    # Metrics
    # ---------------------------------------------------------

    accuracy = accuracy_score(
        y_test,
        y_pred
    )

    auc_score = roc_auc_score(
        y_test,
        y_prob
    )

    train_auc = roc_auc_score(
        y_train,
        train_prob
    )

    precision = precision_score(
        y_test,
        y_pred
    )

    recall = recall_score(
        y_test,
        y_pred
    )

    f1 = f1_score(
        y_test,
        y_pred
    )

    model_health_score = (
        accuracy
        + auc_score
        + f1
    ) / 3

    psi = calculate_psi(
        train_prob,
        y_prob
    )

    model_drift = classify_model_drift(
        psi
    )

    overfitting_risk = detect_overfitting(
        train_auc,
        auc_score
    )

    metrics = {

        "accuracy":
            round(accuracy, 4),

        "precision":
            round(precision, 4),

        "recall":
            round(recall, 4),

        "f1_score":
            round(f1, 4),

        "roc_auc":
            round(auc_score, 4),

        "model_health_score":
            round(model_health_score, 4),

        "population_stability_index":
            psi,

        "psi":
            psi,

        "model_drift":
            model_drift,

        "train_auc":
            round(train_auc, 4),

        "overfitting_risk":
            overfitting_risk,

        "train_samples":
            len(X_train),

        "test_samples":
            len(X_test),

        "feature_count":
            len(feature_cols),
    }

    print("\n[KRONOS] MODEL PERFORMANCE")

    for key, value in metrics.items():

        print(f"{key}: {value}")

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    return (
        model,
        scaler,
        feature_cols,
        metrics
    )

# =============================================================================
# SAVE MODEL ARTIFACTS
# =============================================================================

def save_model_artifacts(
    model,
    scaler,
    feature_cols,
    metrics
):
    """
    Save all model artifacts.
    """

    # Save model
    joblib.dump(model, PD_MODEL_FILE)

    print(f"\n[KRONOS] PD model saved:")
    print(PD_MODEL_FILE)

    # Save scaler
    joblib.dump(scaler, SCALER_FILE)

    print(f"\n[KRONOS] Scaler saved:")
    print(SCALER_FILE)

    # Save feature columns
    with open(FEATURE_COLUMNS_FILE, "w") as f:

        json.dump(feature_cols, f)

    print(f"\n[KRONOS] Feature columns saved:")
    print(FEATURE_COLUMNS_FILE)

    # Save metrics
    with open(MODEL_METRICS_FILE, "w") as f:

        json.dump(metrics, f, indent=4)

    print(f"\n[KRONOS] Metrics saved:")
    print(MODEL_METRICS_FILE)

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":

    results = train_pd_model()

    if results is not None:

        (
            model,
            scaler,
            feature_cols,
            metrics
        ) = results

        save_model_artifacts(
            model,
            scaler,
            feature_cols,
            metrics
        )

        print("\n[KRONOS] PD MODEL PIPELINE COMPLETED")

# =============================================================================
# END OF FILE
# =============================================================================
