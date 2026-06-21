from __future__ import annotations


def run_phase2a(*args, **kwargs):
    from src.temporal_risk.pipeline import run_phase2a as run

    return run(*args, **kwargs)


def run_phase2a_safe(*args, **kwargs):
    from src.temporal_risk.pipeline import run_phase2a_safe as run

    return run(*args, **kwargs)


__all__ = ["run_phase2a", "run_phase2a_safe"]
