from __future__ import annotations

import hashlib
from pathlib import Path

import duckdb

import app.enterprise_visibility as visibility
from app.enterprise_visibility import (
    ARTIFACT_NOT_AVAILABLE,
    load_download_artifact,
    load_sas_analytics_evidence,
    load_warehouse_evidence,
)


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except Exception:
        return ARTIFACT_NOT_AVAILABLE


def test_missing_database_returns_artifact_not_available(tmp_path) -> None:
    try:
        result = load_warehouse_evidence(
            str(tmp_path / "missing.duckdb")
        )
        assert result == {"status": ARTIFACT_NOT_AVAILABLE}
    except Exception as exc:
        raise AssertionError("Visibility adapter propagated an exception.") from exc


def test_missing_manifest_returns_artifact_not_available(tmp_path) -> None:
    try:
        result = load_sas_analytics_evidence(str(tmp_path))
        assert result == {"status": ARTIFACT_NOT_AVAILABLE}
    except Exception as exc:
        raise AssertionError("Visibility adapter propagated an exception.") from exc


def test_malformed_manifest_returns_artifact_not_available(tmp_path) -> None:
    try:
        run_directory = tmp_path / "invalid_run"
        run_directory.mkdir()
        (run_directory / "manifest.json").write_text(
            "{not-valid-json",
            encoding="utf-8",
        )
        result = load_sas_analytics_evidence(str(tmp_path))
        assert result == {"status": ARTIFACT_NOT_AVAILABLE}
    except Exception as exc:
        raise AssertionError("Visibility adapter propagated an exception.") from exc


def test_missing_document_returns_artifact_not_available(tmp_path) -> None:
    try:
        result = load_download_artifact(
            "missing.md",
            str(tmp_path),
        )
        assert result == {"status": ARTIFACT_NOT_AVAILABLE}
    except Exception as exc:
        raise AssertionError("Visibility adapter propagated an exception.") from exc


def test_missing_warehouse_directory_returns_artifact_not_available(
    tmp_path,
) -> None:
    try:
        result = load_warehouse_evidence(
            str(tmp_path / "warehouse" / "kronos_risk.duckdb")
        )
        assert result.get("status") == ARTIFACT_NOT_AVAILABLE
    except Exception as exc:
        raise AssertionError("Visibility adapter propagated an exception.") from exc


def test_production_loaders_are_read_only() -> None:
    database = Path("data/warehouse/kronos_risk.duckdb")
    before_hash = _sha256(database)
    warehouse = load_warehouse_evidence(str(database))
    analytics = load_sas_analytics_evidence()
    after_hash = _sha256(database)

    assert warehouse["status"] == "AVAILABLE"
    assert analytics["status"] == "AVAILABLE"
    assert before_hash == after_hash
    assert warehouse["warehouse"] == {
        "availability": "AVAILABLE",
        "schema_count": 5,
        "table_count": 58,
        "view_count": 10,
        "source_asset_count": 38,
        "artifact_count": 53,
    }
    assert warehouse["reconciliation"]["reconciliation_status"] == "PASS"
    assert analytics["warehouse_read_only"] is True
    assert analytics["warehouse_unchanged"] is True


def test_transient_warehouse_failure_is_not_cached(monkeypatch) -> None:
    real_connect = duckdb.connect
    attempts = {"count": 0}

    def flaky_connect(*args, **kwargs):
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise RuntimeError("simulated transient warehouse read failure")
        return real_connect(*args, **kwargs)

    monkeypatch.setattr(duckdb, "connect", flaky_connect)
    load_warehouse_evidence.clear()

    first = load_warehouse_evidence()
    second = load_warehouse_evidence()

    assert first == {"status": ARTIFACT_NOT_AVAILABLE}
    assert second["status"] == "AVAILABLE"
    assert attempts["count"] == 2


def test_transient_analytics_failure_is_not_cached(monkeypatch) -> None:
    real_loads = visibility.json.loads
    attempts = {"count": 0}

    def flaky_loads(*args, **kwargs):
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise RuntimeError("simulated transient analytics read failure")
        return real_loads(*args, **kwargs)

    monkeypatch.setattr(visibility.json, "loads", flaky_loads)
    load_sas_analytics_evidence.clear()

    first = load_sas_analytics_evidence()
    second = load_sas_analytics_evidence()

    assert first == {"status": ARTIFACT_NOT_AVAILABLE}
    assert second["status"] == "AVAILABLE"
    assert attempts["count"] == 3


def test_visibility_adapter_contains_no_execution_entry_points() -> None:
    source = Path("app/enterprise_visibility.py").read_text(encoding="utf-8")
    forbidden = (
        "run_phase4a_pipeline",
        "run_phase4b_etl",
        "run_sas_style_analytics",
        "run_phase4d",
        "vw_latest_reconciliation",
        "vw_watchlist_intelligence_current",
    )
    assert all(name not in source for name in forbidden)
    assert "read_only=True" in source
