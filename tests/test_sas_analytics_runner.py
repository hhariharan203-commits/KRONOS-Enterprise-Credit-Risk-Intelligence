from __future__ import annotations

import json

from src.enterprise_data.sas_analytics.analytics_runner import (
    run_sas_style_analytics,
    run_sas_style_analytics_safe,
)


def test_runner_persists_only_governed_summary_outputs(tmp_path) -> None:
    result = run_sas_style_analytics(output_root=tmp_path)
    assert result["status"] == "SUCCESS"
    assert result["warehouse_read_only"] is True
    assert result["warehouse_unchanged"] is True
    assert result["borrower_level_ranks_persisted"] is False
    assert result["portfolio_size"] == 50_000

    run_directory = tmp_path / result["analytics_run_id"]
    assert (run_directory / "manifest.json").is_file()
    assert (run_directory / "lineage_manifest.json").is_file()
    assert (run_directory / "hash_inventory.json").is_file()
    assert (run_directory / "institutional_report_pack.md").is_file()

    manifest = json.loads(
        (run_directory / "manifest.json").read_text(encoding="utf-8")
    )
    lineage = json.loads(
        (run_directory / "lineage_manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["warehouse_read_only"] is True
    assert manifest["borrower_level_ranks_persisted"] is False
    assert lineage["warehouse_lineage_modified"] is False
    assert lineage["source_asset"]["source_hash"] == result["source_hash"]

    names = {path.name for path in run_directory.iterdir()}
    assert not any("borrower_rank" in name for name in names)
    assert "proc_rank_deciles.csv" in names


def test_safe_runner_is_non_propagating(tmp_path) -> None:
    missing = tmp_path / "missing.duckdb"
    result = run_sas_style_analytics_safe(
        database_path=missing,
        persist=False,
    )
    assert result["status"] == "ANALYTICS_UNAVAILABLE"
    assert result["application_impact"].startswith("NONE")
