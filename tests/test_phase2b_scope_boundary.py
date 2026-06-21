from __future__ import annotations

import ast

from src.temporal_risk.historical_ingestion.config import ROOT_DIR


def test_phase2b_runtime_has_no_forbidden_imports() -> None:
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
    for path in (ROOT_DIR / "src" / "temporal_risk" / "historical_ingestion").glob("*.py"):
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
