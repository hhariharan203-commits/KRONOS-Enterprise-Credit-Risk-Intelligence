# =============================================================================
# KRONOS — SHARED PURE UTILITIES
# =============================================================================

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import numpy as np
import pandas as pd

IFRS_STAGE_VALUES: tuple[str, ...] = ("STAGE 1", "STAGE 2", "STAGE 3")

_IFRS_STAGE_ALIASES: dict[str, str] = {
    "STAGE 1": "STAGE 1",
    "STAGE 2": "STAGE 2",
    "STAGE 3": "STAGE 3",
    "STAGE_1": "STAGE 1",
    "STAGE_2": "STAGE 2",
    "STAGE_3": "STAGE 3",
    "1": "STAGE 1",
    "2": "STAGE 2",
    "3": "STAGE 3",
}

IFRS_STAGE_LEGACY_LABELS: dict[str, str] = {
    "STAGE 1": "Stage_1",
    "STAGE 2": "Stage_2",
    "STAGE 3": "Stage_3",
}


def current_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def current_date() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def clean_number(value: Any) -> float | None:
    try:
        numeric = pd.to_numeric(pd.Series([value]), errors="coerce").replace([np.inf, -np.inf], np.nan).iloc[0]
    except Exception:
        return None
    if pd.isna(numeric):
        return None
    return float(numeric)


def fmt_number(value: Any, decimals: int = 2) -> str | None:
    numeric = clean_number(value)
    if numeric is None:
        return None
    return f"{numeric:,.{decimals}f}"


def fmt_integer(value: Any) -> str | None:
    numeric = clean_number(value)
    if numeric is None:
        return None
    return f"{int(round(numeric)):,.0f}"


def fmt_currency(value: Any, decimals: int = 2) -> str | None:
    numeric = clean_number(value)
    if numeric is None:
        return None
    sign = "-" if numeric < 0 else ""
    value_abs = abs(numeric)
    if value_abs >= 1_000_000_000:
        return f"{sign}${value_abs / 1_000_000_000:,.{decimals}f}B"
    if value_abs >= 1_000_000:
        return f"{sign}${value_abs / 1_000_000:,.{decimals}f}M"
    if value_abs >= 1_000:
        return f"{sign}${value_abs / 1_000:,.{decimals}f}K"
    return f"{sign}${value_abs:,.0f}"


def fmt_ratio_percent(value: Any, decimals: int = 2) -> str | None:
    numeric = clean_number(value)
    if numeric is None:
        return None
    return f"{numeric * 100:,.{decimals}f}%"


def fmt_percent(value: Any, decimals: int = 2) -> str | None:
    numeric = clean_number(value)
    if numeric is None:
        return None
    return f"{numeric:,.{decimals}f}%"


def fmt_percent_auto(value: Any, decimals: int = 2) -> str | None:
    numeric = clean_number(value)
    if numeric is None:
        return None
    scaled = numeric * 100 if abs(numeric) <= 1 else numeric
    return f"{scaled:,.{decimals}f}%"


def fmt_signed(value: Any, decimals: int = 2) -> str | None:
    numeric = clean_number(value)
    if numeric is None:
        return None
    return f"{numeric:+,.{decimals}f}"


def safe_divide(numerator: Any, denominator: Any) -> float | None:
    left = clean_number(numerator)
    right = clean_number(denominator)
    if left is None or right is None or right == 0:
        return None
    return left / right


def expected_loss(pd_value: Any, lgd_value: Any, ead_value: Any) -> float | None:
    pd_number = clean_number(pd_value)
    lgd_number = clean_number(lgd_value)
    ead_number = clean_number(ead_value)
    if pd_number is None or lgd_number is None or ead_number is None:
        return None
    return pd_number * lgd_number * ead_number


def risk_label(score: Any) -> str | None:
    numeric = clean_number(score)
    if numeric is None:
        return None
    if numeric < 20:
        return "LOW RISK"
    if numeric < 40:
        return "MODERATE RISK"
    if numeric < 60:
        return "ELEVATED RISK"
    if numeric < 80:
        return "HIGH RISK"
    return "CRITICAL RISK"


def ifrs9_stage(pd_value: Any) -> str | None:
    numeric = clean_number(pd_value)
    if numeric is None:
        return None
    if numeric < 0.10:
        return "STAGE 1"
    if numeric < 0.30:
        return "STAGE 2"
    return "STAGE 3"


def normalize_ifrs_stage(value: Any, default: str = "STAGE 1") -> str:
    stage_text = str(value).strip().replace("-", "_").replace(" ", "_").upper()
    normalized = _IFRS_STAGE_ALIASES.get(stage_text)
    if normalized in IFRS_STAGE_VALUES:
        return normalized
    return default


def normalize_ifrs_stage_series(
    values: pd.Series,
    default: str = "STAGE 1",
) -> pd.Series:
    return values.apply(
        lambda value: normalize_ifrs_stage(value, default=default)
    )


def legacy_ifrs_stage_label(value: Any, default: str = "Stage_1") -> str:
    normalized = normalize_ifrs_stage(value)
    return IFRS_STAGE_LEGACY_LABELS.get(normalized, default)


def missing_summary(frame: pd.DataFrame) -> pd.DataFrame:
    if frame is None or frame.empty:
        return pd.DataFrame()
    return (
        pd.DataFrame(
            {
                "missing_values": frame.isna().sum(),
                "missing_percent": frame.isna().mean() * 100,
            }
        )
        .reset_index(names="column")
        .sort_values("missing_percent", ascending=False)
    )


def concentration_index(weights: list[float] | np.ndarray | pd.Series) -> float | None:
    series = pd.to_numeric(pd.Series(weights), errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
    if series.empty:
        return None
    total = float(series.sum())
    if total == 0:
        return None
    normalized = series / total
    return float(np.square(normalized).sum())


def weighted_average(frame: pd.DataFrame, value_col: str, weight_col: str) -> float | None:
    if frame is None or frame.empty or value_col not in frame.columns or weight_col not in frame.columns:
        return None
    values = pd.to_numeric(frame[value_col], errors="coerce")
    weights = pd.to_numeric(frame[weight_col], errors="coerce")
    valid = values.notna() & weights.notna() & (weights > 0)
    if not valid.any():
        return None
    return float(np.average(values[valid], weights=weights[valid]))
