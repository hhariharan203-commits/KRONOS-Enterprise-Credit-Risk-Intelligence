from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.enterprise_data.config import WAREHOUSE_DB
from src.enterprise_data.sas_analytics.concentration_analytics import (
    run_concentration_analytics,
)
from src.enterprise_data.sas_analytics.contracts import ANALYTICS_UNAVAILABLE
from src.enterprise_data.sas_analytics.lineage_manifest import (
    build_lineage_manifest,
)
from src.enterprise_data.sas_analytics.model_risk_analytics import (
    run_model_risk_analytics,
)
from src.enterprise_data.sas_analytics.output_manager import (
    DEFAULT_OUTPUT_ROOT,
    create_run_directory,
    persist_frame,
    persist_json,
    persist_markdown,
    write_hash_inventory,
    write_run_manifest,
)
from src.enterprise_data.sas_analytics.portfolio_analytics import (
    run_portfolio_analytics,
)
from src.enterprise_data.sas_analytics.proc_freq import run_proc_freq
from src.enterprise_data.sas_analytics.proc_means import run_proc_means
from src.enterprise_data.sas_analytics.proc_rank import run_proc_rank
from src.enterprise_data.sas_analytics.proc_report import (
    institutional_reports,
    reports_to_markdown,
)
from src.enterprise_data.sas_analytics.proc_summary import run_proc_summary
from src.enterprise_data.sas_analytics.proc_tabulate import run_proc_tabulate
from src.enterprise_data.sas_analytics.proc_transpose import run_proc_transpose
from src.enterprise_data.sas_analytics.source_catalog import (
    open_read_only,
    run_metadata,
    warehouse_row_counts,
    warehouse_signature,
)
from src.enterprise_data.sas_analytics.stage_analytics import (
    run_stage_analytics,
)


PORTFOLIO_OBJECTS = ["mart.mart_credit_risk_current"]
MODEL_RISK_OBJECTS = [
    "core.dim_model",
    "core.dim_model_artifact",
    "core.fact_model_performance",
    "core.fact_model_validation",
    "core.fact_feature_importance",
    "staging.stg_calibration_decile",
    "staging.stg_challenger_comparison",
    "staging.stg_challenger_performance",
    "staging.stg_oot_summary",
    "staging.stg_oot_risk_band_shift",
    "staging.stg_oot_score_shift",
]


def _register(
    outputs: dict[str, dict],
    *,
    name: str,
    frame: pd.DataFrame,
    module: str,
    sources: list[str],
) -> None:
    outputs[name] = {
        "frame": frame,
        "module": module,
        "sources": sources,
    }


def _build_outputs(connection) -> tuple[dict[str, dict], str]:
    outputs: dict[str, dict] = {}
    _register(
        outputs,
        name="proc_freq",
        frame=run_proc_freq(connection),
        module="proc_freq",
        sources=PORTFOLIO_OBJECTS,
    )
    _register(
        outputs,
        name="proc_means",
        frame=run_proc_means(connection),
        module="proc_means",
        sources=PORTFOLIO_OBJECTS,
    )
    _register(
        outputs,
        name="proc_summary",
        frame=run_proc_summary(connection),
        module="proc_summary",
        sources=PORTFOLIO_OBJECTS,
    )
    _register(
        outputs,
        name="proc_tabulate",
        frame=run_proc_tabulate(connection),
        module="proc_tabulate",
        sources=PORTFOLIO_OBJECTS,
    )
    _register(
        outputs,
        name="proc_rank_deciles",
        frame=run_proc_rank(connection),
        module="proc_rank",
        sources=PORTFOLIO_OBJECTS,
    )
    for name, frame in run_proc_transpose(connection).items():
        _register(
            outputs,
            name=f"proc_transpose_{name}",
            frame=frame,
            module="proc_transpose",
            sources=PORTFOLIO_OBJECTS,
        )
    for name, frame in run_portfolio_analytics(connection).items():
        _register(
            outputs,
            name=name,
            frame=frame,
            module="portfolio_analytics",
            sources=PORTFOLIO_OBJECTS,
        )
    for name, frame in run_concentration_analytics(connection).items():
        _register(
            outputs,
            name=name,
            frame=frame,
            module="concentration_analytics",
            sources=PORTFOLIO_OBJECTS,
        )
    for name, frame in run_stage_analytics(connection).items():
        _register(
            outputs,
            name=name,
            frame=frame,
            module="stage_analytics",
            sources=PORTFOLIO_OBJECTS + ["mart.mart_ifrs9_stage_current"],
        )
    for name, frame in run_model_risk_analytics(connection).items():
        _register(
            outputs,
            name=name,
            frame=frame,
            module="model_risk_analytics",
            sources=MODEL_RISK_OBJECTS,
        )
    reports = institutional_reports(connection)
    for name, frame in reports.items():
        _register(
            outputs,
            name=name,
            frame=frame,
            module="proc_report",
            sources=(
                MODEL_RISK_OBJECTS
                if name == "model_risk_report"
                else PORTFOLIO_OBJECTS
            ),
        )
    return outputs, reports_to_markdown(reports)


def run_sas_style_analytics(
    database_path: Path | str = WAREHOUSE_DB,
    *,
    output_root: Path | str = DEFAULT_OUTPUT_ROOT,
    persist: bool = True,
) -> dict:
    connection = open_read_only(database_path)
    try:
        metadata = run_metadata(connection)
        signature_before = warehouse_signature(connection)
        rows_before = warehouse_row_counts(connection)
        outputs, report_markdown = _build_outputs(connection)
        signature_after = warehouse_signature(connection)
        rows_after = warehouse_row_counts(connection)
    finally:
        connection.close()

    warehouse_unchanged = (
        signature_before == signature_after and rows_before == rows_after
    )
    if not warehouse_unchanged:
        raise RuntimeError(
            "Read-only analytics detected a warehouse contract change."
        )

    run_directory = None
    artifact_records: list[dict] = []
    manifest_record = None
    if persist:
        run_directory = create_run_directory(metadata, output_root)
        for name, output in outputs.items():
            artifact_records.extend(
                persist_frame(
                    run_directory,
                    name=name,
                    frame=output["frame"],
                    analytics_module=output["module"],
                    warehouse_objects=output["sources"],
                )
            )
        artifact_records.append(
            persist_markdown(
                run_directory,
                name="institutional_report_pack",
                markdown=report_markdown,
                analytics_module="proc_report",
                warehouse_objects=PORTFOLIO_OBJECTS + MODEL_RISK_OBJECTS,
            )
        )
        lineage = build_lineage_manifest(metadata, artifact_records)
        lineage_record = persist_json(
            run_directory,
            "lineage_manifest",
            lineage,
        )
        artifact_records.append(
            {
                **lineage_record,
                "analytics_module": "lineage_manifest",
                "warehouse_objects": sorted(
                    set(PORTFOLIO_OBJECTS + MODEL_RISK_OBJECTS)
                ),
            }
        )
        hash_inventory = write_hash_inventory(
            run_directory,
            artifact_records,
        )
        manifest_record = write_run_manifest(
            run_directory,
            metadata,
            artifacts=artifact_records,
            hash_inventory=hash_inventory,
            warehouse_unchanged=warehouse_unchanged,
        )

    return {
        "status": "SUCCESS",
        "framework": "KRONOS SAS-Style Analytics",
        "terminology": "PROC-Equivalent Analytics",
        "analytics_run_id": metadata.analytics_run_id,
        "execution_timestamp": metadata.execution_timestamp,
        "source_hash": metadata.source_hash,
        "published_batch_id": metadata.published_batch_id,
        "model_version": metadata.model_version,
        "portfolio_size": metadata.portfolio_size,
        "output_directory": str(run_directory) if run_directory else None,
        "persisted_output_count": len(artifact_records),
        "manifest": manifest_record,
        "warehouse_read_only": True,
        "warehouse_unchanged": warehouse_unchanged,
        "borrower_level_ranks_persisted": False,
        "current_credit_loss_proxy_only": True,
        "output_names": sorted(outputs),
    }


def run_sas_style_analytics_safe(
    database_path: Path | str = WAREHOUSE_DB,
    **kwargs,
) -> dict:
    try:
        return run_sas_style_analytics(
            database_path=database_path,
            **kwargs,
        )
    except Exception as exc:
        return {
            "status": ANALYTICS_UNAVAILABLE,
            "error": f"{type(exc).__name__}: {exc}",
            "application_impact": (
                "NONE; KRONOS application, warehouse, and ETL operation remain "
                "independent of Phase 4C."
            ),
        }


if __name__ == "__main__":
    print(
        json.dumps(
            run_sas_style_analytics(),
            indent=2,
            default=str,
        )
    )
