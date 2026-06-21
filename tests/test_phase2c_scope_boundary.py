from __future__ import annotations

import ast

import pytest

from src.temporal_risk.migration_readiness.config import ROOT_DIR
from src.temporal_risk.migration_readiness.contracts import (
    PHASE2C_SCOPE_VIOLATION,
    Phase2CScopeError,
    enforce_scope,
)


def test_scope_guard_rejects_analytical_requests() -> None:
    enforce_scope()
    with pytest.raises(Phase2CScopeError, match=PHASE2C_SCOPE_VIOLATION):
        enforce_scope(("migration matrices",))


def test_runtime_package_has_no_application_or_phase4_imports() -> None:
    forbidden = (
        "app",
        "src.enterprise_data",
        "src.credit_risk",
        "src.model_validation",
        "src.provisioning",
        "src.ews",
        "src.stress_testing",
        "src.contagion",
        "src.decisioning",
        "src.reporting",
    )
    violations = []
    package = ROOT_DIR / "src" / "temporal_risk" / "migration_readiness"
    for path in package.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            violations.extend(
                f"{path.name}:{name}"
                for name in names
                if name.startswith(forbidden)
            )
    assert violations == []
