"""Compatibility entry points for SAS-Style Analytics."""

from src.enterprise_data.sas_analytics import (
    run_sas_style_analytics,
    run_sas_style_analytics_safe,
)

__all__ = ["run_sas_style_analytics", "run_sas_style_analytics_safe"]
