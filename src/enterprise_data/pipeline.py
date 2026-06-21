from __future__ import annotations

import json
from pathlib import Path

from src.enterprise_data.artifact_registry import register_artifacts
from src.enterprise_data.audit import finish_batch, record_step, start_batch
from src.enterprise_data.config import WAREHOUSE_DB
from src.enterprise_data.connection import (
    connect_warehouse,
    discard_working_database,
    prepare_working_database,
    publish_working_database,
)
from src.enterprise_data.data_quality import (
    publish_data_quality_fact,
    run_data_quality,
)
from src.enterprise_data.lineage import build_lineage
from src.enterprise_data.loaders import load_all_csv_sources, load_json_sources
from src.enterprise_data.mart_builder import (
    build_credit_core,
    build_feature_importance_fact,
    build_market_facts,
    build_marts,
    build_model_artifact_dimension,
    build_model_risk_facts,
)
from src.enterprise_data.reconciliation import run_reconciliation
from src.enterprise_data.schema_manager import initialize_warehouse


def run_phase4a_pipeline(
    database_path: Path | str = WAREHOUSE_DB,
) -> dict:
    working_database = prepare_working_database(database_path)
    connection = connect_warehouse(working_database.working_path)
    batch_id = None
    source_results = []
    result = None
    try:
        initialize_warehouse(connection)
        connection.execute(
            "UPDATE control.source_asset SET is_current = FALSE"
        )
        connection.execute(
            "UPDATE control.artifact_registry SET is_current = FALSE"
        )
        batch_id = start_batch(connection)

        artifacts = register_artifacts(connection)
        record_step(
            connection,
            batch_id,
            "REGISTER_ARTIFACTS",
            status="SUCCESS",
            row_count=len(artifacts),
        )

        source_results = load_all_csv_sources(connection, batch_id)
        json_results = load_json_sources(connection, batch_id)
        by_name = {
            result["relative_path"]: result
            for result in source_results
        }
        by_source_name = {
            result["relative_path"].split("/")[-1]: result
            for result in source_results
        }
        named_results = {}
        for result in source_results:
            relative_path = result["relative_path"]
            if relative_path.endswith("scored_portfolio.csv"):
                named_results["scored_portfolio"] = result
            elif relative_path.endswith("feature_importance.csv"):
                named_results["feature_importance"] = result
            elif relative_path.endswith("fred_market_data.csv"):
                named_results["fred_observation"] = result
            elif relative_path.endswith("vix_data.csv"):
                named_results["vix_observation"] = result
            elif relative_path.endswith("alpha_vantage_market_data.csv"):
                named_results["market_observation"] = result

        credit_result = build_credit_core(
            connection,
            batch_id,
            named_results["scored_portfolio"]["source_asset_id"],
        )
        model_artifact_rows = build_model_artifact_dimension(connection)
        model_risk_result = build_model_risk_facts(connection, batch_id)
        feature_importance_rows = build_feature_importance_fact(
            connection,
            batch_id,
            named_results["feature_importance"]["source_asset_id"],
        )
        market_rows = build_market_facts(connection, batch_id, named_results)

        quality_results = run_data_quality(connection, batch_id, source_results)
        quality_fact_rows = publish_data_quality_fact(connection, batch_id)
        marts = build_marts(connection, batch_id)
        reconciliation_results = run_reconciliation(
            connection,
            batch_id,
            named_results["scored_portfolio"],
        )
        lineage_result = build_lineage(connection, batch_id, source_results)

        quality_failures = sum(
            result["status"] == "FAIL" for result in quality_results
        )
        reconciliation_failures = sum(
            result["status"] == "FAIL" for result in reconciliation_results
        )
        status = (
            "SUCCESS"
            if quality_failures == 0 and reconciliation_failures == 0
            else "FAILED_VALIDATION"
        )
        loaded_count = sum(result["status"] == "LOADED" for result in source_results)
        skipped_count = sum(result["status"] == "SKIPPED" for result in source_results)
        finish_batch(
            connection,
            batch_id,
            status=status,
            source_count=len(source_results),
            loaded_source_count=loaded_count,
            skipped_source_count=skipped_count,
        )

        result = {
            "status": status,
            "database_path": str(working_database.target_path),
            "etl_batch_id": batch_id,
            "artifact_count": len(artifacts),
            "csv_source_count": len(source_results),
            "json_source_count": len(json_results),
            "loaded_source_count": loaded_count,
            "skipped_source_count": skipped_count,
            "credit_core": credit_result,
            "model_artifact_rows_inserted": model_artifact_rows,
            "model_risk": model_risk_result,
            "feature_importance_rows_inserted": feature_importance_rows,
            "market_rows_inserted": market_rows,
            "quality_check_count": len(quality_results),
            "quality_failure_count": quality_failures,
            "quality_fact_rows": quality_fact_rows,
            "reconciliation_count": len(reconciliation_results),
            "reconciliation_failure_count": reconciliation_failures,
            "lineage": lineage_result,
            "marts": marts,
        }
    except Exception as exc:
        if batch_id is not None:
            finish_batch(
                connection,
                batch_id,
                status="FAILED",
                source_count=len(source_results),
                loaded_source_count=sum(
                    result.get("status") == "LOADED"
                    for result in source_results
                ),
                skipped_source_count=sum(
                    result.get("status") == "SKIPPED"
                    for result in source_results
                ),
                error_message=f"{type(exc).__name__}: {exc}",
            )
        raise
    finally:
        connection.close()
        if result is not None:
            publish_working_database(working_database)
        discard_working_database(working_database)
    return result


def run_phase4a_pipeline_safe(
    database_path: Path | str = WAREHOUSE_DB,
) -> dict:
    try:
        return run_phase4a_pipeline(database_path)
    except Exception as exc:
        return {
            "status": "WAREHOUSE_UNAVAILABLE",
            "database_path": str(Path(database_path)),
            "error": f"{type(exc).__name__}: {exc}",
            "application_impact": "NONE; existing CSV workflows remain authoritative.",
        }


if __name__ == "__main__":
    print(json.dumps(run_phase4a_pipeline(), indent=2, default=str))
