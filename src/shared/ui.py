"""Native Streamlit UI primitives for KRONOS dashboards.

This module intentionally avoids custom HTML/CSS rendering. All components are
implemented with native Streamlit elements so dynamic values cannot leak as raw
HTML and dashboards share a single rendering contract.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.shared.constants import DEFAULT_CHART_HEIGHT, DEFAULT_TABLE_ROWS, RESPONSIVE_COLUMNS
from src.shared.theme import apply_plotly_theme
from src.shared.utils import (
    clean_number,
    fmt_currency,
    fmt_integer,
    fmt_number,
    fmt_percent,
    fmt_percent_auto,
    fmt_ratio_percent,
)


MetricSpec = tuple[str, Any] | tuple[str, Any, str | None]


def is_present(value: Any) -> bool:
    """Return whether a dashboard value should be rendered."""

    if value is None:
        return False
    if isinstance(value, float) and pd.isna(value):
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return True


def to_number(value: Any) -> float | None:
    """Convert a value to a numeric scalar when possible."""

    return clean_number(value)


def number(value: Any, decimals: int = 2) -> str | None:
    """Format a numeric KPI."""

    return fmt_number(value, decimals)


def integer(value: Any) -> str | None:
    """Format an integer KPI."""

    return fmt_integer(value)


def money(value: Any, decimals: int = 2) -> str | None:
    """Format a monetary KPI."""

    return fmt_currency(value, decimals)


def ratio_percent(value: Any, decimals: int = 2) -> str | None:
    """Format a ratio stored on a 0-1 scale as a percentage."""

    return fmt_ratio_percent(value, decimals)


def percent_value(value: Any, decimals: int = 2) -> str | None:
    """Format a value that is already on percentage scale."""

    return fmt_percent(value, decimals)


def percent_auto(value: Any, decimals: int = 2) -> str | None:
    """Format a percentage, inferring whether it is stored as ratio or percent."""

    return fmt_percent_auto(value, decimals)


def text_value(value: Any) -> str | None:
    """Format a text value without substituting fabricated states."""

    if not is_present(value):
        return None
    return str(value)


def page_title(title: str, subtitle: str | None = None) -> None:
    """Render a dashboard page title."""

    st.title(title)
    if subtitle:
        st.caption(subtitle)


def section(title: str, description: str | None = None) -> None:
    """Render a dashboard section heading."""

    st.subheader(title)
    if description:
        st.caption(description)


def metric_grid(metrics: Sequence[MetricSpec], columns: int = RESPONSIVE_COLUMNS["standard_kpi"]) -> None:
    """Render a responsive grid of Streamlit metrics.

    Metrics with missing values are omitted instead of displaying artificial
    defaults. Each metric can be ``(label, value)`` or ``(label, value, help)``.
    """

    renderable: list[tuple[str, Any, str | None]] = []
    for metric in metrics:
        label, value, *rest = metric
        if not is_present(value):
            continue
        help_text = rest[0] if rest else None
        renderable.append((label, value, help_text))

    if not renderable:
        return

    column_count = max(1, min(columns, len(renderable)))
    for start in range(0, len(renderable), column_count):
        row = renderable[start : start + column_count]
        cols = st.columns(len(row))
        for col, (label, value, help_text) in zip(cols, row, strict=False):
            with col:
                with st.container(border=True):
                    st.metric(label=label, value=value)
                    if help_text:
                        st.caption(help_text)


def narrative(title: str, body: str | Sequence[str] | None) -> None:
    """Render a concise narrative panel using native Streamlit containers."""

    if not is_present(body):
        return

    with st.container(border=True):
        st.write(f"**{title}**")
        if isinstance(body, str):
            st.write(body)
            return
        for item in body:
            if is_present(item):
                st.write(f"- {item}")


def key_values(
    title: str,
    values: Mapping[str, Any],
    *,
    expanded: bool = False,
) -> None:
    """Render key-value details as an investigation expander."""

    rows = [
        {"Field": key, "Value": value}
        for key, value in values.items()
        if is_present(value)
    ]
    if not rows:
        return

    with st.expander(title, expanded=expanded):
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def key_value_grid(title: str, values: Mapping[str, Any], *, expanded: bool = False) -> None:
    """Backward-compatible native key-value renderer."""

    key_values(title, values, expanded=expanded)


def data_table(
    title: str,
    frame: pd.DataFrame | None,
    *,
    height: int = 420,
    max_rows: int = DEFAULT_TABLE_ROWS,
    expanded: bool = False,
) -> None:
    """Render a dataframe only inside an investigation expander."""

    if frame is None or frame.empty:
        return

    visible = frame.head(max_rows) if max_rows else frame
    with st.expander(title, expanded=expanded):
        st.dataframe(visible, use_container_width=True, height=height)
        st.download_button(
            label=f"Download {title}",
            data=visible.to_csv(index=False),
            file_name=f"{title.lower().replace(' ', '_')}.csv",
            mime="text/csv",
        )


def _trace_has_data(trace: Any) -> bool:
    """Return whether a Plotly trace has renderable data."""

    for attribute in ("x", "y", "z", "values", "labels", "parents", "ids"):
        values = getattr(trace, attribute, None)
        if values is None:
            continue
        try:
            if len(values) > 0:
                return True
        except TypeError:
            if values:
                return True
    return False


def render_plot(fig: go.Figure | None, key: str | None = None) -> bool:
    """Render a Plotly figure when it contains data.

    Returns ``True`` when the chart is rendered and ``False`` when there is no
    figure or no data-bearing trace. This prevents blank visual containers.
    """

    if fig is None:
        return False

    traces = list(getattr(fig, "data", []) or [])
    if not traces or not any(_trace_has_data(trace) for trace in traces):
        return False

    layout_title = getattr(getattr(fig.layout, "title", None), "text", None)
    layout_height = getattr(fig.layout, "height", None) or DEFAULT_CHART_HEIGHT
    apply_plotly_theme(fig, title=layout_title or "", height=int(layout_height))
    st.plotly_chart(
        fig,
        width="stretch",
        key=key,
        config={"responsive": True, "displaylogo": False},
    )
    return True


def render_tabs(tabs: Mapping[str, Any]) -> None:
    """Render tab content from callables or already prepared Streamlit content."""

    available = [(name, content) for name, content in tabs.items() if content is not None]
    if not available:
        return

    tab_objects = st.tabs([name for name, _ in available])
    for tab, (_, content) in zip(tab_objects, available, strict=False):
        with tab:
            if callable(content):
                content()
            else:
                st.write(content)


def execution_diagnostics(errors: Sequence[str] | None) -> None:
    """Render dashboard diagnostics collapsed by default."""

    if not errors:
        return

    with st.expander("Technical Diagnostics", expanded=False):
        for error in errors:
            if is_present(error):
                st.error(str(error))
