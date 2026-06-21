from __future__ import annotations

from pathlib import Path

from src.temporal_risk.historical_ingestion.config import ROOT_DIR


def test_phase2b_is_not_an_application_or_phase4_dependency() -> None:
    application = "\n".join(
        path.read_text(encoding="utf-8") for path in (ROOT_DIR / "app").glob("*.py")
    )
    enterprise = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT_DIR / "src" / "enterprise_data").rglob("*.py")
    )
    assert "historical_ingestion" not in application
    assert "historical_ingestion" not in enterprise


def test_phase2b_contains_no_analytical_objects() -> None:
    sql = "\n".join(
        path.read_text(encoding="utf-8").upper()
        for path in (ROOT_DIR / "sql" / "phase2b").rglob("*.sql")
    )
    assert "CREATE VIEW" not in sql
    assert "CREATE TABLE MART." not in sql
