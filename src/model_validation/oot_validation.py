# =============================================================================
# KRONOS — PROXY OUT-OF-TIME VALIDATION
# File: src/model_validation/oot_validation.py
# =============================================================================

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)

from src.credit_risk.credit_engine import classify_risk_band
from src.shared.config import (
    FEATURE_COLUMNS_FILE,
    MERGED_CREDIT_DATA,
    OUTPUTS_DIR,
    PD_MODEL_FILE,
    SCALER_FILE,
)
from src.shared.utils import (
    legacy_ifrs_stage_label,
    normalize_ifrs_stage_series,
)


OOT_OUTPUT_DIR: Path = OUTPUTS_DIR / "oot_validation"

METHODOLOGY_FILE: Path = OOT_OUTPUT_DIR / "methodology.json"
OOT_METRICS_FILE: Path = OOT_OUTPUT_DIR / "oot_metrics.json"
OOT_SUMMARY_FILE: Path = OOT_OUTPUT_DIR / "oot_summary.csv"
SCORE_SHIFT_FILE: Path = OOT_OUTPUT_DIR / "score_distribution_shift.csv"
RISK_BAND_SHIFT_FILE: Path = OOT_OUTPUT_DIR / "risk_band_distribution_shift.csv"
PSI_REPORT_FILE: Path = OOT_OUTPUT_DIR / "psi_report.json"
OOT_AUC_CURVE_FILE: Path = OOT_OUTPUT_DIR / "oot_auc_curve.png"
OOT_SCORE_DISTRIBUTION_FILE: Path = OOT_OUTPUT_DIR / "oot_score_distribution.png"
EXECUTIVE_SUMMARY_FILE: Path = OOT_OUTPUT_DIR / "executive_summary.json"

TEMPORAL_FIELD_HIERARCHY = [
    "origination_date",
    "vintage_month",
    "reporting_month",
    "observation_date",
    "snapshot_date",
    "as_of_date",
]

VALIDATION_LIMITATION = (
    "Dataset does not contain origination, vintage, reporting, "
    "or observation dates. Validation uses chronological "
    "record-order fallback and should not be interpreted as "
    "true future-period model validation."
)

PROXY_TRAIN_FRACTION = 0.80
CLASSIFICATION_THRESHOLD = 0.50


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def load_pd_artifacts():
    """
    Load the existing champion PD model artifacts without retraining.
    """

    model = joblib.load(
        PD_MODEL_FILE
    )

    scaler = joblib.load(
        SCALER_FILE
    )

    with open(
        FEATURE_COLUMNS_FILE,
        "r",
        encoding="utf-8",
    ) as f:
        feature_cols = json.load(f)

    return model, scaler, feature_cols


def load_modeling_dataset() -> pd.DataFrame:
    """
    Load the borrower-level modeling dataset without modifying source data.
    """

    df = pd.read_csv(
        MERGED_CREDIT_DATA
    )

    if "target_default" not in df.columns:
        raise ValueError(
            "target_default column missing from OOT validation dataset"
        )

    return df


def detect_temporal_field(
    df: pd.DataFrame,
) -> str | None:
    """
    Detect the best available temporal field using the approved hierarchy.
    """

    normalized_columns = {
        column.lower(): column
        for column in df.columns
    }

    for candidate in TEMPORAL_FIELD_HIERARCHY:
        if candidate in normalized_columns:
            return normalized_columns[candidate]

    return None


def build_proxy_split(
    df: pd.DataFrame,
    selected_time_field: str | None,
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """
    Build true temporal split if possible, otherwise documented proxy row-order split.
    """

    if selected_time_field is not None:
        sorted_df = df.copy()
        sorted_df[selected_time_field] = pd.to_datetime(
            sorted_df[selected_time_field],
            errors="coerce",
        )
        sorted_df = sorted_df.sort_values(
            selected_time_field
        ).reset_index(drop=True)

        split_index = int(
            len(sorted_df) * PROXY_TRAIN_FRACTION
        )
        train_df = sorted_df.iloc[:split_index].copy()
        oot_df = sorted_df.iloc[split_index:].copy()

        methodology = {
            "validation_type": "Out-of-Time Validation",
            "true_temporal_field_found": True,
            "selected_time_field": selected_time_field,
            "split_method": "temporal_field_ordering",
            "train_period": {
                "start": str(
                    train_df[selected_time_field].min()
                ),
                "end": str(
                    train_df[selected_time_field].max()
                ),
            },
            "test_period": {
                "start": str(
                    oot_df[selected_time_field].min()
                ),
                "end": str(
                    oot_df[selected_time_field].max()
                ),
            },
            "limitations": [],
        }

        return train_df, oot_df, methodology

    working_df = df.copy().reset_index(drop=True)
    working_df["_proxy_record_order_index"] = np.arange(
        len(working_df)
    )

    split_index = int(
        len(working_df) * PROXY_TRAIN_FRACTION
    )

    train_df = working_df.iloc[:split_index].copy()
    oot_df = working_df.iloc[split_index:].copy()

    methodology = {
        "validation_type": "Proxy OOT Validation",
        "true_temporal_field_found": False,
        "selected_time_field": None,
        "split_method": "chronological_record_ordering_fallback",
        "fallback_field": "_proxy_record_order_index",
        "train_period": {
            "label": "Proxy Train Segment",
            "record_order_start": int(
                train_df["_proxy_record_order_index"].min()
            ),
            "record_order_end": int(
                train_df["_proxy_record_order_index"].max()
            ),
            "population_size": int(
                len(train_df)
            ),
        },
        "test_period": {
            "label": "Proxy OOT Segment",
            "record_order_start": int(
                oot_df["_proxy_record_order_index"].min()
            ),
            "record_order_end": int(
                oot_df["_proxy_record_order_index"].max()
            ),
            "population_size": int(
                len(oot_df)
            ),
        },
        "limitations": [
            VALIDATION_LIMITATION
        ],
    }

    return train_df, oot_df, methodology


def prepare_feature_matrix(
    df: pd.DataFrame,
    feature_cols: list[str],
) -> tuple[pd.DataFrame, pd.Series]:
    """
    Prepare validation features to match the saved champion feature list.
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
            "_proxy_record_order_index",
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


def predict_probabilities(
    model,
    scaler,
    X: pd.DataFrame,
) -> np.ndarray:
    """
    Score observations with the existing champion PD model.
    """

    X_scaled = scaler.transform(
        X
    )

    return model.predict_proba(
        X_scaled
    )[:, 1]


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


def calculate_top_decile_lift(
    y_true: pd.Series,
    y_prob: np.ndarray,
) -> float:
    analysis_df = pd.DataFrame(
        {
            "target_default": y_true.values,
            "pd_score": y_prob,
        }
    ).sort_values(
        "pd_score",
        ascending=False,
    )

    top_decile_size = max(
        int(len(analysis_df) * 0.10),
        1,
    )

    portfolio_default_rate = analysis_df[
        "target_default"
    ].mean()

    if portfolio_default_rate == 0:
        return 0.0

    top_decile_default_rate = analysis_df.head(
        top_decile_size
    )["target_default"].mean()

    return round(
        float(
            top_decile_default_rate / portfolio_default_rate
        ),
        6,
    )


def evaluate_segment(
    segment_name: str,
    y_true: pd.Series,
    y_prob: np.ndarray,
) -> dict:
    """
    Calculate performance metrics for a validation segment.
    """

    y_pred = (
        y_prob >= CLASSIFICATION_THRESHOLD
    ).astype(int)

    return {
        "segment": segment_name,
        "population_size": int(
            len(y_true)
        ),
        "default_count": int(
            y_true.sum()
        ),
        "default_rate": round(
            float(
                y_true.mean()
            ),
            6,
        ),
        "average_pd": round(
            float(
                np.mean(y_prob)
            ),
            6,
        ),
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
        "top_decile_lift": calculate_top_decile_lift(
            y_true,
            y_prob,
        ),
        "classification_threshold": CLASSIFICATION_THRESHOLD,
    }


def _score_bins(
    expected_scores: np.ndarray,
    bucket_count: int = 10,
) -> np.ndarray:
    quantiles = np.linspace(
        0,
        1,
        bucket_count + 1,
    )

    bins = np.quantile(
        expected_scores,
        quantiles,
    )

    bins[0] = min(
        bins[0],
        0.0,
    )
    bins[-1] = max(
        bins[-1],
        1.0,
    )

    return np.unique(
        bins
    )


def build_score_distribution_shift(
    train_scores: np.ndarray,
    oot_scores: np.ndarray,
) -> tuple[pd.DataFrame, float]:
    """
    Build PD score distribution shift and PSI report table.
    """

    bins = _score_bins(
        train_scores
    )

    if len(bins) < 3:
        bins = np.linspace(
            0,
            1,
            11,
        )

    train_counts, bin_edges = np.histogram(
        train_scores,
        bins=bins,
    )
    oot_counts, _ = np.histogram(
        oot_scores,
        bins=bin_edges,
    )

    train_pct = train_counts / max(
        len(train_scores),
        1,
    )
    oot_pct = oot_counts / max(
        len(oot_scores),
        1,
    )

    psi_contribution = (
        train_pct - oot_pct
    ) * np.log(
        (train_pct + 1e-6)
        / (oot_pct + 1e-6)
    )

    shift_df = pd.DataFrame(
        {
            "bucket": np.arange(
                1,
                len(train_counts) + 1,
            ),
            "score_min": bin_edges[:-1],
            "score_max": bin_edges[1:],
            "proxy_train_count": train_counts,
            "proxy_train_pct": train_pct,
            "proxy_oot_count": oot_counts,
            "proxy_oot_pct": oot_pct,
            "pct_point_shift": oot_pct - train_pct,
            "psi_contribution": psi_contribution,
        }
    )

    numeric_cols = [
        "score_min",
        "score_max",
        "proxy_train_pct",
        "proxy_oot_pct",
        "pct_point_shift",
        "psi_contribution",
    ]

    shift_df[numeric_cols] = shift_df[numeric_cols].round(
        8
    )

    psi = round(
        float(
            np.sum(
                psi_contribution
            )
        ),
        6,
    )

    return shift_df, psi


def build_risk_band_distribution_shift(
    train_scores: np.ndarray,
    oot_scores: np.ndarray,
) -> pd.DataFrame:
    """
    Compare existing KRONOS risk-band distributions across proxy segments.
    """

    train_bands = pd.Series(
        [
            classify_risk_band(score)
            for score in train_scores
        ],
        name="risk_band",
    )
    oot_bands = pd.Series(
        [
            classify_risk_band(score)
            for score in oot_scores
        ],
        name="risk_band",
    )

    all_bands = sorted(
        set(train_bands.unique())
        | set(oot_bands.unique())
    )

    rows = []

    for band in all_bands:
        train_count = int(
            (train_bands == band).sum()
        )
        oot_count = int(
            (oot_bands == band).sum()
        )
        train_pct = train_count / max(
            len(train_bands),
            1,
        )
        oot_pct = oot_count / max(
            len(oot_bands),
            1,
        )

        rows.append(
            {
                "risk_band": band,
                "proxy_train_count": train_count,
                "proxy_train_pct": round(
                    float(train_pct),
                    8,
                ),
                "proxy_oot_count": oot_count,
                "proxy_oot_pct": round(
                    float(oot_pct),
                    8,
                ),
                "pct_point_shift": round(
                    float(oot_pct - train_pct),
                    8,
                ),
            }
        )

    return pd.DataFrame(
        rows
    )


def classify_psi_status(
    psi: float,
) -> str:
    if psi < 0.10:
        return "NO MATERIAL DRIFT"
    if psi < 0.25:
        return "MODERATE DRIFT"
    return "SEVERE DRIFT"


def plot_oot_auc_curve(
    y_oot: pd.Series,
    oot_scores: np.ndarray,
    oot_auc: float,
) -> None:
    fpr, tpr, _ = roc_curve(
        y_oot,
        oot_scores,
    )

    plt.figure(
        figsize=(8, 6)
    )
    plt.plot(
        fpr,
        tpr,
        linewidth=2,
        label=f"Proxy OOT AUC = {oot_auc:.4f}",
    )
    plt.plot(
        [0, 1],
        [0, 1],
        linestyle="--",
        color="gray",
        label="Random Classifier",
    )
    plt.title(
        "KRONOS Proxy OOT ROC Curve"
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
    plt.legend()
    plt.tight_layout()
    plt.savefig(
        OOT_AUC_CURVE_FILE,
        dpi=160,
    )
    plt.close()


def plot_score_distribution(
    train_scores: np.ndarray,
    oot_scores: np.ndarray,
) -> None:
    plt.figure(
        figsize=(9, 6)
    )
    plt.hist(
        train_scores,
        bins=30,
        alpha=0.55,
        label="Proxy Train Segment",
        density=True,
    )
    plt.hist(
        oot_scores,
        bins=30,
        alpha=0.55,
        label="Proxy OOT Segment",
        density=True,
    )
    plt.title(
        "KRONOS Proxy OOT PD Score Distribution"
    )
    plt.xlabel(
        "Predicted PD"
    )
    plt.ylabel(
        "Density"
    )
    plt.grid(
        alpha=0.3
    )
    plt.legend()
    plt.tight_layout()
    plt.savefig(
        OOT_SCORE_DISTRIBUTION_FILE,
        dpi=160,
    )
    plt.close()


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


def run_proxy_oot_validation() -> dict:
    """
    Run additive proxy OOT validation without retraining or artifact mutation.
    """

    OOT_OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    model, scaler, feature_cols = load_pd_artifacts()
    df = load_modeling_dataset()
    selected_time_field = detect_temporal_field(
        df
    )
    train_df, oot_df, methodology = build_proxy_split(
        df,
        selected_time_field,
    )

    X_train, y_train = prepare_feature_matrix(
        train_df,
        feature_cols,
    )
    X_oot, y_oot = prepare_feature_matrix(
        oot_df,
        feature_cols,
    )

    train_scores = predict_probabilities(
        model,
        scaler,
        X_train,
    )
    oot_scores = predict_probabilities(
        model,
        scaler,
        X_oot,
    )

    train_metrics = evaluate_segment(
        "Proxy Train Segment",
        y_train,
        train_scores,
    )
    oot_metrics = evaluate_segment(
        "Proxy OOT Segment",
        y_oot,
        oot_scores,
    )

    score_shift_df, psi = build_score_distribution_shift(
        train_scores,
        oot_scores,
    )
    risk_band_shift_df = build_risk_band_distribution_shift(
        train_scores,
        oot_scores,
    )

    methodology["generated_at"] = _utc_timestamp()
    methodology["model_artifact"] = str(
        PD_MODEL_FILE
    )
    methodology["scaler_artifact"] = str(
        SCALER_FILE
    )
    methodology["feature_list_artifact"] = str(
        FEATURE_COLUMNS_FILE
    )
    methodology["source_dataset"] = str(
        MERGED_CREDIT_DATA
    )

    oot_metrics_payload = {
        "validation_type": methodology["validation_type"],
        "generated_at": _utc_timestamp(),
        "train_metrics": train_metrics,
        "oot_metrics": oot_metrics,
        "performance_degradation": {
            "auc_delta_oot_minus_train": round(
                oot_metrics["auc"] - train_metrics["auc"],
                6,
            ),
            "ks_delta_oot_minus_train": round(
                oot_metrics["ks_statistic"]
                - train_metrics["ks_statistic"],
                6,
            ),
            "f1_delta_oot_minus_train": round(
                oot_metrics["f1_score"]
                - train_metrics["f1_score"],
                6,
            ),
        },
    }

    oot_summary_df = pd.DataFrame(
        [
            train_metrics,
            oot_metrics,
        ]
    )

    score_drift_summary = {
        "proxy_train_mean_pd": round(
            float(
                np.mean(train_scores)
            ),
            6,
        ),
        "proxy_oot_mean_pd": round(
            float(
                np.mean(oot_scores)
            ),
            6,
        ),
        "mean_pd_shift": round(
            float(
                np.mean(oot_scores)
                - np.mean(train_scores)
            ),
            6,
        ),
        "proxy_train_median_pd": round(
            float(
                np.median(train_scores)
            ),
            6,
        ),
        "proxy_oot_median_pd": round(
            float(
                np.median(oot_scores)
            ),
            6,
        ),
    }

    psi_report = {
        "validation_type": methodology["validation_type"],
        "generated_at": _utc_timestamp(),
        "psi": psi,
        "psi_status": classify_psi_status(
            psi
        ),
        "feature_drift_summary": {
            "scope": "PD score distribution only",
            "reason": (
                "Task 3 requested proxy OOT validation without modifying "
                "feature engineering or existing datasets."
            ),
            "feature_count": int(
                len(feature_cols)
            ),
        },
        "score_drift_summary": score_drift_summary,
        "risk_band_distribution_comparison": risk_band_shift_df.to_dict(
            orient="records"
        ),
    }

    validation_status = (
        "PASSED"
        if (
            oot_metrics["auc"] >= 0.70
            and psi < 0.25
        )
        else "REVIEW REQUIRED"
    )

    executive_summary = {
        "validation_status": validation_status,
        "methodology": methodology["validation_type"],
        "limitations": methodology["limitations"],
        "key_metrics": {
            "oot_auc": oot_metrics["auc"],
            "oot_ks_statistic": oot_metrics["ks_statistic"],
            "oot_f1_score": oot_metrics["f1_score"],
            "oot_default_rate": oot_metrics["default_rate"],
            "psi": psi,
            "psi_status": psi_report["psi_status"],
        },
        "recommendation": (
            "Use results as a proxy stability diagnostic only. Add a true "
            "origination, vintage, reporting, or observation date before "
            "treating this as future-period model validation."
        ),
    }

    score_shift_df.to_csv(
        SCORE_SHIFT_FILE,
        index=False,
    )
    risk_band_shift_df.to_csv(
        RISK_BAND_SHIFT_FILE,
        index=False,
    )
    oot_summary_df.to_csv(
        OOT_SUMMARY_FILE,
        index=False,
    )

    plot_oot_auc_curve(
        y_oot,
        oot_scores,
        oot_metrics["auc"],
    )
    plot_score_distribution(
        train_scores,
        oot_scores,
    )

    save_json(
        METHODOLOGY_FILE,
        methodology,
    )
    save_json(
        OOT_METRICS_FILE,
        oot_metrics_payload,
    )
    save_json(
        PSI_REPORT_FILE,
        psi_report,
    )
    save_json(
        EXECUTIVE_SUMMARY_FILE,
        executive_summary,
    )

    return {
        "methodology": methodology,
        "oot_metrics": oot_metrics_payload,
        "psi_report": psi_report,
        "executive_summary": executive_summary,
        "outputs": {
            "methodology": str(METHODOLOGY_FILE),
            "oot_metrics": str(OOT_METRICS_FILE),
            "oot_summary": str(OOT_SUMMARY_FILE),
            "score_distribution_shift": str(SCORE_SHIFT_FILE),
            "risk_band_distribution_shift": str(RISK_BAND_SHIFT_FILE),
            "psi_report": str(PSI_REPORT_FILE),
            "oot_auc_curve": str(OOT_AUC_CURVE_FILE),
            "oot_score_distribution": str(OOT_SCORE_DISTRIBUTION_FILE),
            "executive_summary": str(EXECUTIVE_SUMMARY_FILE),
        },
    }


if __name__ == "__main__":
    result = run_proxy_oot_validation()
    print(
        json.dumps(
            result["executive_summary"],
            indent=4,
        )
    )

# =============================================================================
# END OF FILE
# =============================================================================

