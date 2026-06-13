"""Enterprise visual tokens and Plotly theme helpers for KRONOS."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import plotly.graph_objects as go
import plotly.io as pio


@dataclass(frozen=True)
class Theme:
    """Immutable design-system tokens shared across KRONOS dashboards."""

    name: str
    background: str
    panel: str
    card: str
    border: str
    text: str
    secondary_text: str
    primary_accent: str
    secondary_accent: str
    success: str
    warning: str
    critical: str
    font_primary: str
    font_fallback: str
    executive_kpi_px: tuple[int, int]
    section_header_px: tuple[int, int]
    body_px: tuple[int, int]
    diagnostics_px: tuple[int, int]
    chart_template: str
    chart_palette: tuple[str, ...]
    heatmap_scale: tuple[tuple[float, str], ...]

    @property
    def font_family(self) -> str:
        return f"{self.font_primary}, {self.font_fallback}, sans-serif"

    @property
    def surface(self) -> str:
        return self.panel

    @property
    def muted(self) -> str:
        return self.secondary_text

    @property
    def primary(self) -> str:
        return self.primary_accent

    @property
    def danger(self) -> str:
        return self.critical

    @property
    def accent(self) -> str:
        return self.secondary_accent


ENTERPRISE_THEME = Theme(
    name="KRONOS Institutional",
    background="#0B1220",
    panel="#111827",
    card="#172033",
    border="#334155",
    text="#F8FAFC",
    secondary_text="#CBD5E1",
    primary_accent="#3B82F6",
    secondary_accent="#06B6D4",
    success="#10B981",
    warning="#F59E0B",
    critical="#EF4444",
    font_primary="Inter",
    font_fallback="Segoe UI",
    executive_kpi_px=(36, 48),
    section_header_px=(22, 28),
    body_px=(14, 16),
    diagnostics_px=(12, 13),
    chart_template="kronos_enterprise",
    chart_palette=(
        "#3B82F6",
        "#06B6D4",
        "#10B981",
        "#F59E0B",
        "#EF4444",
        "#8B5CF6",
        "#22C55E",
        "#EAB308",
        "#F97316",
        "#94A3B8",
    ),
    heatmap_scale=(
        (0.0, "#172033"),
        (0.2, "#1E3A8A"),
        (0.45, "#2563EB"),
        (0.7, "#06B6D4"),
        (1.0, "#F8FAFC"),
    ),
)


KRONOS_CSS: str = ""

BG_PRIMARY = ENTERPRISE_THEME.background
BG_SECONDARY = ENTERPRISE_THEME.panel
BG_CARD = ENTERPRISE_THEME.card
TEXT_PRIMARY = ENTERPRISE_THEME.text
TEXT_MUTED = ENTERPRISE_THEME.secondary_text
BORDER_COLOR = ENTERPRISE_THEME.border
ACCENT_BLUE = ENTERPRISE_THEME.primary_accent
ACCENT_CYAN = ENTERPRISE_THEME.secondary_accent
ACCENT_GREEN = ENTERPRISE_THEME.success
ACCENT_AMBER = ENTERPRISE_THEME.warning
ACCENT_RED = ENTERPRISE_THEME.critical
ACCENT_PURPLE = "#8B5CF6"
CHART_COLORS = list(ENTERPRISE_THEME.chart_palette)
HEATMAP_COLORSCALE = list(ENTERPRISE_THEME.heatmap_scale)
CHART_TEMPLATE = ENTERPRISE_THEME.chart_template
FONT_FAMILY = ENTERPRISE_THEME.font_family


def _register_plotly_template() -> None:
    """Register the canonical KRONOS Plotly template once per process."""

    pio.templates[ENTERPRISE_THEME.chart_template] = go.layout.Template(
        layout={
            "font": {
                "family": ENTERPRISE_THEME.font_family,
                "color": ENTERPRISE_THEME.text,
                "size": ENTERPRISE_THEME.body_px[1],
            },
            "paper_bgcolor": ENTERPRISE_THEME.background,
            "plot_bgcolor": ENTERPRISE_THEME.panel,
            "colorway": list(ENTERPRISE_THEME.chart_palette),
            "hoverlabel": {
                "bgcolor": ENTERPRISE_THEME.card,
                "bordercolor": ENTERPRISE_THEME.primary_accent,
                "font": {
                    "family": ENTERPRISE_THEME.font_family,
                    "color": ENTERPRISE_THEME.text,
                    "size": ENTERPRISE_THEME.diagnostics_px[1],
                },
            },
            "legend": {
                "font": {
                    "family": ENTERPRISE_THEME.font_family,
                    "color": ENTERPRISE_THEME.secondary_text,
                    "size": ENTERPRISE_THEME.diagnostics_px[1],
                },
                "orientation": "h",
                "x": 0,
                "y": 1.08,
            },
            "xaxis": {
                "gridcolor": "#1E293B",
                "linecolor": ENTERPRISE_THEME.border,
                "tickcolor": ENTERPRISE_THEME.border,
                "zerolinecolor": ENTERPRISE_THEME.border,
            },
            "yaxis": {
                "gridcolor": "#1E293B",
                "linecolor": ENTERPRISE_THEME.border,
                "tickcolor": ENTERPRISE_THEME.border,
                "zerolinecolor": ENTERPRISE_THEME.border,
            },
        }
    )


_register_plotly_template()


def plotly_layout(title: str, *, height: int = 380) -> dict[str, Any]:
    """Return the canonical KRONOS Plotly layout contract."""

    return {
        "title": {
            "text": title,
            "font": {
                "family": ENTERPRISE_THEME.font_family,
                "size": ENTERPRISE_THEME.section_header_px[0],
                "color": ENTERPRISE_THEME.text,
            },
        },
        "template": ENTERPRISE_THEME.chart_template,
        "height": height,
        "margin": {"l": 44, "r": 28, "t": 58, "b": 46},
        "legend": {"orientation": "h", "y": 1.08, "x": 0},
        "font": {
            "family": ENTERPRISE_THEME.font_family,
            "color": ENTERPRISE_THEME.text,
            "size": ENTERPRISE_THEME.body_px[1],
        },
        "paper_bgcolor": ENTERPRISE_THEME.background,
        "plot_bgcolor": ENTERPRISE_THEME.panel,
        "hovermode": "closest",
        "colorway": list(ENTERPRISE_THEME.chart_palette),
    }


def apply_plotly_theme(fig: go.Figure, title: str | None = None, *, height: int = 380) -> go.Figure:
    """Apply the KRONOS institutional Plotly styling to an existing figure."""

    fig.update_layout(**plotly_layout(title or "", height=height))
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="#1E293B")
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="#1E293B")
    return fig
