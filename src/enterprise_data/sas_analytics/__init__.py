"""Read-only KRONOS SAS-Style Analytics framework."""


def run_sas_style_analytics(*args, **kwargs):
    from src.enterprise_data.sas_analytics.analytics_runner import (
        run_sas_style_analytics as run,
    )

    return run(*args, **kwargs)


def run_sas_style_analytics_safe(*args, **kwargs):
    from src.enterprise_data.sas_analytics.analytics_runner import (
        run_sas_style_analytics_safe as run,
    )

    return run(*args, **kwargs)


__all__ = ["run_sas_style_analytics", "run_sas_style_analytics_safe"]
