from __future__ import annotations

import pytest

from src.enterprise_data.etl.dependency_manager import (
    DependencyManager,
    DependencyValidationError,
)
from src.enterprise_data.etl.job import ETLJob


def _success(_context):
    return {"status": "SUCCESS"}


def test_dependency_ordering_and_validation() -> None:
    jobs = [
        ETLJob("SOURCE", "SOURCE_LOAD", _success),
        ETLJob("VALIDATE", "VALIDATION", _success, ("SOURCE",)),
        ETLJob("STAGE", "STAGING_LOAD", _success, ("VALIDATE",)),
        ETLJob("CORE", "CORE_LOAD", _success, ("STAGE",)),
        ETLJob("MART", "MART_BUILD", _success, ("CORE",)),
        ETLJob("PUBLISH", "PUBLISH", _success, ("MART",)),
    ]
    manager = DependencyManager(jobs)
    assert manager.execution_order == (
        "SOURCE",
        "VALIDATE",
        "STAGE",
        "CORE",
        "MART",
        "PUBLISH",
    )

    with pytest.raises(DependencyValidationError):
        DependencyManager(
            [
                ETLJob("A", "SOURCE_LOAD", _success, ("B",)),
                ETLJob("B", "VALIDATION", _success, ("A",)),
            ]
        )
