# =============================================================================
# KRONOS — SHARED APPLICATION CONSTANTS
# =============================================================================

from __future__ import annotations

APP_NAME: str = "KRONOS"
APP_TAGLINE: str = "Enterprise Credit Risk Intelligence Platform"
VERSION: str = "1.0.0"

DASHBOARD_NAMES: tuple[str, ...] = (
    "Executive Dashboard",
    "Credit Risk Engine",
    "Early Warning System",
    "Stress Testing Lab",
    "Contagion Terminal",
    "Provisioning Dashboard",
    "Decision Terminal",
    "Explainability Center",
    "Risk Pulse Monitor",
    "Reports Center",
)

RISK_BANDS: tuple[str, ...] = (
    "LOW RISK",
    "MODERATE RISK",
    "ELEVATED RISK",
    "HIGH RISK",
    "CRITICAL RISK",
)

IFRS_STAGES: tuple[str, ...] = ("STAGE 1", "STAGE 2", "STAGE 3")

DEFAULT_TABLE_ROWS: int = 500
DEFAULT_CHART_HEIGHT: int = 380
DEFAULT_CACHE_TTL_SECONDS: int = 600

TYPOGRAPHY_SCALE: dict[str, tuple[int, int]] = {
    "executive_kpi": (36, 48),
    "section_header": (22, 28),
    "body": (14, 16),
    "diagnostics": (12, 13),
}

LAYOUT_SPACING: dict[str, int] = {
    "panel_gap": 16,
    "card_gap": 12,
    "section_gap": 24,
    "diagnostics_gap": 8,
}

RESPONSIVE_COLUMNS: dict[str, int] = {
    "executive_kpi": 4,
    "standard_kpi": 4,
    "investigation": 2,
    "diagnostics": 1,
}

CHART_DIMENSIONS: dict[str, int] = {
    "standard": DEFAULT_CHART_HEIGHT,
    "compact": 300,
    "wide": 460,
    "network": 560,
}
