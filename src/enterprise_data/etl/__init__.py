"""Phase 4B DataStage-style ETL control framework."""


def run_phase4b_etl(*args, **kwargs):
    from src.enterprise_data.etl.scheduler import run_phase4b_etl as run

    return run(*args, **kwargs)


def run_phase4b_etl_safe(*args, **kwargs):
    from src.enterprise_data.etl.scheduler import run_phase4b_etl_safe as run

    return run(*args, **kwargs)


__all__ = ["run_phase4b_etl", "run_phase4b_etl_safe"]
