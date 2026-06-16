# =============================================================================
# KRONOS — PD CHALLENGER MODEL FRAMEWORK
# File: src/model_validation/challenger_models.py
# =============================================================================

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier
from scipy.stats import ks_2samp
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

from src.shared.config import (
    FEATURE_COLUMNS_FILE,
    MERGED_CREDIT_DATA,
    OUTPUTS_DIR,
    PD_MODEL_FILE,
    RANDOM_STATE,
    SCALER_FILE,
    TEST_SIZE,
)
from src.shared.utils import (
    legacy_ifrs_stage_label,
    normalize_ifrs_stage_series,
)


CHALLENGER_OUTPUT_DIR: Path = OUTPUTS_DIR / "challenger_models"

MODEL_COMPARISON_FILE: Path = (
    CHALLENGER_OUTPUT_DIR / "model_comparison.csv"
)
MODEL_PERFORMANCE_TABLE_FILE: Path = (
    CHALLENGER_OUTPUT_DIR / "model_performance_table.csv"
)
MODEL_RANKINGS_FILE: Path = (
    CHALLENGER_OUTPUT_DIR / "model_rankings.json"
)
CHALLENGER_SUMMARY_FILE: Path = (
    CHALLENGER_OUTPUT_DIR / "challenger_summary.json"
)
ROC_COMPARISON_FILE: Path = (
    CHALLENGER_OUTPUT_DIR / "roc_comparison.png"
)

CHAMPION_MODEL_NAME = "Current VotingClassifier (Champion)"
CLASSIFICATION_THRESHOLD = 0.50


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def load_governed_feature_set() -> list[str]:
    """
    Load the current governed PD feature set.
    """

    with open(
        FEATURE_COLUMNS_FILE,
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


def load_dataset() -> pd.DataFrame:
    """
    Load the current merged borrower-level modeling dataset.
    """

    df = pd.read_csv(
        MERGED_CREDIT_DATA
    )

    if "target_default" not in df.columns:
        raise ValueError(
            "target_default column missing from challenger dataset"
        )

    return df


def prepare_feature_matrix(
    df: pd.DataFrame,
    feature_cols: list[str],
) -> tuple[pd.DataFrame, pd.Series]:
    """
    Apply the same champion preprocessing pattern and align to saved features.
    """

    working_df = df.copy()

    if "ifrs_stage" in working_df.columns:
        working_df["ifrs_stage"] = normalize_ifrs_stage_series(
            working_df["ifrs_stage"]
        ).apply(
            legacy_ifrs_stage_label
        )

    X = working_df.drop(
        columns=[
            "target_default",
            "dataset_source",
            "risk_segment",
        ],
        errors="ignore",
    )

    X = X.fillna(0)

    categorical_cols = X.select_dtypes(
        include=[
            "object",
            "string",
        ]
    ).columns

    if len(categorical_cols) > 0:
        X = pd.get_dummies(
            X,
            columns=categorical_cols,
            drop_first=True,
        )

    X = X.reindex(
        columns=feature_cols,
        fill_value=0,
    )

    y = working_df["target_default"].astype(int)

    return X, y


def split_champion_methodology(
    X: pd.DataFrame,
    y: pd.Series,
):
    """
    Use the champion train/test methodology: same test size, random state, stratify.
    """

    return train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )


def calculate_ks_statistic(
    y_true: pd.Series,
    y_prob: np.ndarray,
) -> float:
    good_scores = y_prob[
        y_true.values == 0
    ]
    bad_scores = y_prob[
        y_true.values == 1
    ]

    if len(good_scores) == 0 or len(bad_scores) == 0:
        return 0.0

    return round(
        float(
            ks_2samp(
                good_scores,
                bad_scores,
            ).statistic
        ),
        6,
    )


def evaluate_model(
    model_name: str,
    y_true: pd.Series,
    y_prob: np.ndarray,
    role: str,
) -> dict:
    """
    Calculate common challenger performance metrics.
    """

    y_pred = (
        y_prob >= CLASSIFICATION_THRESHOLD
    ).astype(int)

    return {
        "model_name": model_name,
        "model_role": role,
        "auc": round(
            float(
                roc_auc_score(
                    y_true,
                    y_prob,
                )
            ),
            6,
        ),
        "accuracy": round(
            float(
                accuracy_score(
                    y_true,
                    y_pred,
                )
            ),
            6,
        ),
        "precision": round(
            float(
                precision_score(
                    y_true,
                    y_pred,
                    zero_division=0,
                )
            ),
            6,
        ),
        "recall": round(
            float(
                recall_score(
                    y_true,
                    y_pred,
                    zero_division=0,
                )
            ),
            6,
        ),
        "f1_score": round(
            float(
                f1_score(
                    y_true,
                    y_pred,
                    zero_division=0,
                )
            ),
            6,
        ),
        "ks_statistic": calculate_ks_statistic(
            y_true,
            y_prob,
        ),
        "brier_score": round(
            float(
                brier_score_loss(
                    y_true,
                    y_prob,
                )
            ),
            6,
        ),
        "classification_threshold": CLASSIFICATION_THRESHOLD,
    }


def build_challenger_models() -> dict:
    """
    Build in-memory challenger candidates. No production artifacts are saved.
    """

    return {
        "Logistic Regression": LogisticRegression(
            max_iter=1000,
            solver="lbfgs",
            random_state=RANDOM_STATE,
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=300,
            max_depth=8,
            min_samples_leaf=25,
            random_state=RANDOM_STATE,
            n_jobs=1,
        ),
        "XGBoost": XGBClassifier(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=RANDOM_STATE,
            eval_metric="logloss",
            n_jobs=1,
        ),
        "LightGBM": LGBMClassifier(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.05,
            random_state=RANDOM_STATE,
            n_jobs=1,
        ),
    }


def score_champion(
    X_test: pd.DataFrame,
) -> np.ndarray:
    """
    Score the existing saved champion VotingClassifier without retraining.
    """

    champion_model = joblib.load(
        PD_MODEL_FILE
    )

    champion_scaler = joblib.load(
        SCALER_FILE
    )

    X_test_scaled = champion_scaler.transform(
        X_test
    )

    return champion_model.predict_proba(
        X_test_scaled
    )[:, 1]


def train_and_score_challengers(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
) -> dict[str, np.ndarray]:
    """
    Train challenger models in memory and return test-set probabilities.
    """

    champion_scaler = joblib.load(
        SCALER_FILE
    )

    X_train_scaled = champion_scaler.transform(
        X_train
    )
    X_test_scaled = champion_scaler.transform(
        X_test
    )

    challenger_scores: dict[str, np.ndarray] = {}

    for model_name, model in build_challenger_models().items():
        model.fit(
            X_train_scaled,
            y_train,
        )

        challenger_scores[model_name] = model.predict_proba(
            X_test_scaled
        )[:, 1]

    return challenger_scores


def plot_roc_comparison(
    y_test: pd.Series,
    model_scores: dict[str, np.ndarray],
    comparison_df: pd.DataFrame,
) -> None:
    """
    Save ROC curve comparison for champion and challengers.
    """

    plt.figure(
        figsize=(9, 7)
    )

    for model_name, y_prob in model_scores.items():
        fpr, tpr, _ = roc_curve(
            y_test,
            y_prob,
        )

        auc_value = float(
            comparison_df.loc[
                comparison_df["model_name"] == model_name,
                "auc",
            ].iloc[0]
        )

        plt.plot(
            fpr,
            tpr,
            linewidth=2,
            label=f"{model_name} AUC={auc_value:.4f}",
        )

    plt.plot(
        [0, 1],
        [0, 1],
        linestyle="--",
        color="gray",
        label="Random Classifier",
    )

    plt.title(
        "KRONOS PD Champion vs Challenger ROC Comparison"
    )
    plt.xlabel(
        "False Positive Rate"
    )
    plt.ylabel(
        "True Positive Rate"
    )
    plt.grid(
        alpha=0.3
    )
    plt.legend(
        loc="lower right",
        fontsize=8,
    )
    plt.tight_layout()
    plt.savefig(
        ROC_COMPARISON_FILE,
        dpi=160,
    )
    plt.close()


def build_rankings(
    comparison_df: pd.DataFrame,
) -> dict:
    """
    Rank models while keeping the current VotingClassifier as champion.
    """

    ranked_df = comparison_df.sort_values(
        by=[
            "auc",
            "ks_statistic",
            "f1_score",
        ],
        ascending=False,
    ).reset_index(drop=True)

    ranked_df["rank"] = ranked_df.index + 1

    champion_row = comparison_df[
        comparison_df["model_name"] == CHAMPION_MODEL_NAME
    ].iloc[0]

    challengers_df = comparison_df[
        comparison_df["model_name"] != CHAMPION_MODEL_NAME
    ].sort_values(
        by=[
            "auc",
            "ks_statistic",
            "f1_score",
        ],
        ascending=False,
    )

    best_challenger = challengers_df.iloc[0]
    performance_gap = round(
        float(
            best_challenger["auc"]
            - champion_row["auc"]
        ),
        6,
    )

    return {
        "generated_at": _utc_timestamp(),
        "ranking_metric": "AUC, then KS Statistic, then F1 Score",
        "champion_model": CHAMPION_MODEL_NAME,
        "recommended_champion": CHAMPION_MODEL_NAME,
        "best_challenger": str(
            best_challenger["model_name"]
        ),
        "performance_gap_best_challenger_minus_champion_auc": performance_gap,
        "production_replacement_allowed": False,
        "model_rankings": ranked_df[
            [
                "rank",
                "model_name",
                "model_role",
                "auc",
                "ks_statistic",
                "f1_score",
                "brier_score",
            ]
        ].to_dict(
            orient="records"
        ),
    }


def build_summary(
    comparison_df: pd.DataFrame,
    rankings: dict,
) -> dict:
    """
    Build executive challenger summary.
    """

    champion = comparison_df[
        comparison_df["model_name"] == CHAMPION_MODEL_NAME
    ].iloc[0]

    best_challenger = comparison_df[
        comparison_df["model_name"] == rankings["best_challenger"]
    ].iloc[0]

    gap = rankings[
        "performance_gap_best_challenger_minus_champion_auc"
    ]

    if gap > 0.005:
        recommendation = (
            "Current VotingClassifier remains champion by policy. "
            "Best challenger shows a measurable AUC advantage and should "
            "be reviewed as a future challenger candidate, not promoted."
        )
    else:
        recommendation = (
            "Maintain Current VotingClassifier as champion. Challenger "
            "performance is broadly comparable and does not justify model "
            "replacement."
        )

    return {
        "report_name": "KRONOS PD Challenger Model Summary",
        "generated_at": _utc_timestamp(),
        "champion_model": CHAMPION_MODEL_NAME,
        "best_challenger": rankings["best_challenger"],
        "performance_gap_best_challenger_minus_champion_auc": gap,
        "champion_auc": float(
            champion["auc"]
        ),
        "best_challenger_auc": float(
            best_challenger["auc"]
        ),
        "model_replacement": "NOT PERMITTED",
        "recommendation": recommendation,
        "validation_scope": (
            "Additive model-risk challenger comparison only. Production "
            "PD artifacts and scoring logic are not modified."
        ),
    }


def save_json(
    path: Path,
    payload: dict,
) -> None:
    with open(
        path,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            payload,
            f,
            indent=4,
        )


def run_challenger_framework() -> dict:
    """
    Run additive PD challenger comparison and write outputs.
    """

    CHALLENGER_OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    feature_cols = load_governed_feature_set()
    df = load_dataset()
    X, y = prepare_feature_matrix(
        df,
        feature_cols,
    )

    (
        X_train,
        X_test,
        y_train,
        y_test,
    ) = split_champion_methodology(
        X,
        y,
    )

    model_scores: dict[str, np.ndarray] = {
        CHAMPION_MODEL_NAME: score_champion(
            X_test
        )
    }
    model_scores.update(
        train_and_score_challengers(
            X_train,
            X_test,
            y_train,
        )
    )

    rows = []

    for model_name, y_prob in model_scores.items():
        role = (
            "Champion"
            if model_name == CHAMPION_MODEL_NAME
            else "Challenger"
        )
        rows.append(
            evaluate_model(
                model_name,
                y_test,
                y_prob,
                role,
            )
        )

    comparison_df = pd.DataFrame(
        rows
    ).sort_values(
        by=[
            "auc",
            "ks_statistic",
            "f1_score",
        ],
        ascending=False,
    ).reset_index(drop=True)

    rankings = build_rankings(
        comparison_df
    )
    summary = build_summary(
        comparison_df,
        rankings,
    )

    comparison_df.to_csv(
        MODEL_COMPARISON_FILE,
        index=False,
    )
    comparison_df.to_csv(
        MODEL_PERFORMANCE_TABLE_FILE,
        index=False,
    )
    save_json(
        MODEL_RANKINGS_FILE,
        rankings,
    )
    save_json(
        CHALLENGER_SUMMARY_FILE,
        summary,
    )
    plot_roc_comparison(
        y_test,
        model_scores,
        comparison_df,
    )

    return {
        "summary": summary,
        "rankings": rankings,
        "outputs": {
            "model_comparison": str(MODEL_COMPARISON_FILE),
            "model_rankings": str(MODEL_RANKINGS_FILE),
            "challenger_summary": str(CHALLENGER_SUMMARY_FILE),
            "roc_comparison": str(ROC_COMPARISON_FILE),
            "model_performance_table": str(MODEL_PERFORMANCE_TABLE_FILE),
        },
    }


if __name__ == "__main__":
    result = run_challenger_framework()
    print(
        json.dumps(
            result["summary"],
            indent=4,
        )
    )

# =============================================================================
# END OF FILE
# =============================================================================
