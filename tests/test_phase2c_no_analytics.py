from __future__ import annotations

from src.temporal_risk.migration_readiness.config import ROOT_DIR
from src.temporal_risk.migration_readiness.contracts import (
    is_prohibited_field_name,
)


def test_phase2c_contains_no_analytical_objects_or_forbidden_fields() -> None:
    forbidden_fields = (
        "from_state",
        "to_state",
        "state_pair",
        "transition_pair",
        "transition_count",
        "transition_probability",
        "migration_matrix_cell",
    )
    sql = "\n".join(
        path.read_text(encoding="utf-8").lower()
        for path in (ROOT_DIR / "sql" / "phase2c").rglob("*.sql")
    )
    runtime = "\n".join(
        path.read_text(encoding="utf-8").lower()
        for path in (
            ROOT_DIR / "src" / "temporal_risk" / "migration_readiness"
        ).glob("*.py")
    )
    combined = sql + runtime
    assert "create view" not in sql
    assert "create table mart." not in sql
    assert "create table core." not in sql
    assert "create table staging." not in sql
    assert "create table reference." not in sql
    assert all(field not in combined for field in forbidden_fields)
    assert all(is_prohibited_field_name(field) for field in forbidden_fields)
