from __future__ import annotations


def deploy_phase2b_schema(*args, **kwargs):
    from src.temporal_risk.historical_ingestion.pipeline import deploy_phase2b_schema

    return deploy_phase2b_schema(*args, **kwargs)


def deploy_phase2b_schema_safe(*args, **kwargs):
    from src.temporal_risk.historical_ingestion.pipeline import (
        deploy_phase2b_schema_safe,
    )

    return deploy_phase2b_schema_safe(*args, **kwargs)


def run_historical_ingestion(*args, **kwargs):
    from src.temporal_risk.historical_ingestion.pipeline import (
        run_historical_ingestion,
    )

    return run_historical_ingestion(*args, **kwargs)


def run_historical_ingestion_safe(*args, **kwargs):
    from src.temporal_risk.historical_ingestion.pipeline import (
        run_historical_ingestion_safe,
    )

    return run_historical_ingestion_safe(*args, **kwargs)


__all__ = [
    "deploy_phase2b_schema",
    "deploy_phase2b_schema_safe",
    "run_historical_ingestion",
    "run_historical_ingestion_safe",
]
