# =============================================================================
# KRONOS — PD CALIBRATION VALIDATION
# File: src/model_validation/calibration.py
# =============================================================================

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.metrics import brier_score_loss

from src.shared.config import (
    FEATURE_COLUMNS_FILE,
    MERGED_CREDIT_DATA,
    OUTPUTS_DIR,
    PD_MODEL_FILE,
    RANDOM_STATE,
    SCALER_FILE,
)
from src.shared.utils import (
    legacy_ifrs_stage_label,
    normalize_ifrs_stage_series,
)


CALIBRATION_OUTPUT_DIR: Path = OUTPUTS_DIR / "calibration"
CALIBRATION_CURVE_FILE: Path = (
    CALIBRATION_OUTPUT_DIR / "calibration_curve.png"
)
RELIABILITY_DIAGRAM_FILE: Path = (
    CALIBRATION_OUTPUT_DIR / "reliability_diagram.png"
)
DECILE_ANALYSIS_FILE: Path = (
    CALIBRATION_OUTPUT_DIR / "decile_analysis.csv"
)
CALIBRATION_SUMMARY_FILE: Path = (
    CALIBRATION_OUTPUT_DIR / "calibration_summary.json"
)


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def load_pd_artifacts():
    """
    Load the current champion PD model, scaler, and governed feature list.
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


def load_calibration_dataset() -> pd.DataFrame:
    """
    Load the merged credit dataset used for PD model validation.
    """

    df = pd.read_csv(
        MERGED_CREDIT_DATA
    )

    if "target_default" not in df.columns:
        raise ValueError(
            "target_default column missing from calibration dataset"
        )

    return df


def prepare_feature_matrix(
    df: pd.DataFrame,
    feature_cols: list[str],
) -> tuple[pd.DataFrame, pd.Series]:
    """
    Prepare the calibration feature matrix against the saved model feature list.
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


def predict_pd_scores(
    model,
    scaler,
    X: pd.DataFrame,
) -> np.ndarray:
    """
    Generate PD probabilities using the current champion PD model.
    """

    X_scaled = scaler.transform(
        X
    )

    return model.predict_proba(
        X_scaled
    )[:, 1]


def build_decile_analysis(
    y_true: pd.Series,
    y_prob: np.ndarray,
) -> pd.DataFrame:
    """
    Build observed-vs-predicted default analysis by PD decile.
    """

    analysis_df = pd.DataFrame(
        {
            "actual_default": y_true.astype(int).values,
            "predicted_pd": y_prob,
        }
    )

    analysis_df["decile"] = pd.qcut(
        analysis_df["predicted_pd"].rank(method="first"),
        q=10,
        labels=False,
    ) + 1

    portfolio_default_rate = analysis_df[
        "actual_default"
    ].mean()

    decile_df = (
        analysis_df
        .groupby("decile", as_index=False)
        .agg(
            observation_count=("actual_default", "size"),
            default_count=("actual_default", "sum"),
            predicted_pd_min=("predicted_pd", "min"),
            predicted_pd_max=("predicted_pd", "max"),
            average_predicted_pd=("predicted_pd", "mean"),
            actual_default_rate=("actual_default", "mean"),
        )
        .sort_values("decile")
        .reset_index(drop=True)
    )

    decile_df["non_default_count"] = (
        decile_df["observation_count"]
        - decile_df["default_count"]
    )

    decile_df["default_rate_lift"] = np.where(
        portfolio_default_rate > 0,
        decile_df["actual_default_rate"] / portfolio_default_rate,
        0,
    )

    decile_df["calibration_gap"] = (
        decile_df["average_predicted_pd"]
        - decile_df["actual_default_rate"]
    )

    numeric_cols = [
        "predicted_pd_min",
        "predicted_pd_max",
        "average_predicted_pd",
        "actual_default_rate",
        "default_rate_lift",
        "calibration_gap",
    ]

    decile_df[numeric_cols] = decile_df[numeric_cols].round(
        6
    )

    return decile_df


def create_calibration_curve_plot(
    y_true: pd.Series,
    y_prob: np.ndarray,
) -> dict:
    """
    Generate and save the calibration curve chart.
    """

    prob_true, prob_pred = calibration_curve(
        y_true,
        y_prob,
        n_bins=10,
        strategy="quantile",
    )

    plt.figure(
        figsize=(8, 6)
    )

    plt.plot(
        prob_pred,
        prob_true,
        marker="o",
        linewidth=2,
        label="KRONOS PD Model",
    )

    plt.plot(
        [0, 1],
        [0, 1],
        linestyle="--",
        color="gray",
        label="Perfect Calibration",
    )

    plt.title(
        "KRONOS PD Calibration Curve"
    )
    plt.xlabel(
        "Average Predicted PD"
    )
    plt.ylabel(
        "Observed Default Rate"
    )
    plt.grid(
        alpha=0.3
    )
    plt.legend()
    plt.tight_layout()
    plt.savefig(
        CALIBRATION_CURVE_FILE,
        dpi=160,
    )
    plt.close()

    return {
        "prob_true": [
            round(float(value), 6)
            for value in prob_true
        ],
        "prob_pred": [
            round(float(value), 6)
            for value in prob_pred
        ],
    }


def create_reliability_diagram(
    decile_df: pd.DataFrame,
) -> None:
    """
    Generate and save a decile-level reliability diagram.
    """

    plt.figure(
        figsize=(10, 6)
    )

    x_positions = np.arange(
        len(decile_df)
    )

    width = 0.38

    plt.bar(
        x_positions - width / 2,
        decile_df["average_predicted_pd"],
        width,
        label="Average Predicted PD",
        color="#1f77b4",
    )

    plt.bar(
        x_positions + width / 2,
        decile_df["actual_default_rate"],
        width,
        label="Actual Default Rate",
        color="#d62728",
    )

    plt.xticks(
        x_positions,
        decile_df["decile"].astype(str),
    )
    plt.title(
        "KRONOS PD Reliability Diagram by Decile"
    )
    plt.xlabel(
        "PD Decile (1 = Lowest Risk, 10 = Highest Risk)"
    )
    plt.ylabel(
        "Default Rate"
    )
    plt.grid(
        axis="y",
        alpha=0.3,
    )
    plt.legend()
    plt.tight_layout()
    plt.savefig(
        RELIABILITY_DIAGRAM_FILE,
        dpi=160,
    )
    plt.close()


def build_calibration_summary(
    y_true: pd.Series,
    y_prob: np.ndarray,
    decile_df: pd.DataFrame,
    curve_points: dict,
) -> dict:
    """
    Build JSON-serializable calibration summary metrics.
    """

    predicted_default_rate = float(
        np.mean(y_prob)
    )
    actual_default_rate = float(
        y_true.mean()
    )
    calibration_gap = (
        predicted_default_rate
        - actual_default_rate
    )

    max_abs_decile_gap = float(
        decile_df["calibration_gap"].abs().max()
    )

    highest_risk_decile = decile_df.iloc[
        decile_df["actual_default_rate"].idxmax()
    ]

    return {
        "report_name": "KRONOS PD Calibration Summary",
        "generated_at": _utc_timestamp(),
        "model_scope": "Probability of Default",
        "model_artifact": str(PD_MODEL_FILE),
        "scaler_artifact": str(SCALER_FILE),
        "feature_list_artifact": str(FEATURE_COLUMNS_FILE),
        "sample_count": int(len(y_true)),
        "default_count": int(y_true.sum()),
        "non_default_count": int(len(y_true) - y_true.sum()),
        "brier_score": round(
            float(
                brier_score_loss(
                    y_true,
                    y_prob,
                )
            ),
            6,
        ),
        "predicted_default_rate": round(
            predicted_default_rate,
            6,
        ),
        "actual_default_rate": round(
            actual_default_rate,
            6,
        ),
        "predicted_vs_actual_gap": round(
            calibration_gap,
            6,
        ),
        "absolute_predicted_vs_actual_gap": round(
            abs(calibration_gap),
            6,
        ),
        "max_absolute_decile_gap": round(
            max_abs_decile_gap,
            6,
        ),
        "highest_observed_risk_decile": int(
            highest_risk_decile["decile"]
        ),
        "highest_observed_default_rate": round(
            float(
                highest_risk_decile["actual_default_rate"]
            ),
            6,
        ),
        "calibration_curve_points": curve_points,
        "outputs": {
            "calibration_curve": str(CALIBRATION_CURVE_FILE),
            "reliability_diagram": str(RELIABILITY_DIAGRAM_FILE),
            "decile_analysis": str(DECILE_ANALYSIS_FILE),
            "calibration_summary": str(CALIBRATION_SUMMARY_FILE),
        },
    }


def save_calibration_outputs(
    decile_df: pd.DataFrame,
    summary: dict,
) -> None:
    """
    Save calibration CSV and JSON artifacts.
    """

    CALIBRATION_OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    decile_df.to_csv(
        DECILE_ANALYSIS_FILE,
        index=False,
    )

    with open(
        CALIBRATION_SUMMARY_FILE,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            summary,
            f,
            indent=4,
        )


def run_calibration_validation() -> dict:
    """
    Run backend-only PD calibration validation and write all required artifacts.
    """

    CALIBRATION_OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    model, scaler, feature_cols = load_pd_artifacts()
    df = load_calibration_dataset()
    X, y = prepare_feature_matrix(
        df,
        feature_cols,
    )
    y_prob = predict_pd_scores(
        model,
        scaler,
        X,
    )

    decile_df = build_decile_analysis(
        y,
        y_prob,
    )
    curve_points = create_calibration_curve_plot(
        y,
        y_prob,
    )
    create_reliability_diagram(
        decile_df
    )

    summary = build_calibration_summary(
        y,
        y_prob,
        decile_df,
        curve_points,
    )

    save_calibration_outputs(
        decile_df,
        summary,
    )

    return summary


if __name__ == "__main__":
    result = run_calibration_validation()
    print(
        json.dumps(
            result,
            indent=4,
        )
    )

# =============================================================================
# END OF FILE
# =============================================================================

