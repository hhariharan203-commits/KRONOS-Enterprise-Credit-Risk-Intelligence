from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.enterprise_data.audit import record_step
from src.enterprise_data.config import MART_SQL_FILES, ROOT_DIR
from src.enterprise_data.schema_manager import execute_sql_file
from src.enterprise_data.transformations import (
    artifact_role,
    current_model_composite_version,
    prepare_scored_portfolio,
)


def _now():
    return datetime.now(timezone.utc)


def _id(*values) -> str:
    return hashlib.sha256(
        "|".join("" if value is None else str(value) for value in values).encode("utf-8")
    ).hexdigest()[:32]


def _numeric(frame: pd.DataFrame, column: str):
    if column not in frame:
        return pd.Series([None] * len(frame), index=frame.index)
    return pd.to_numeric(frame[column], errors="coerce")


def _text(frame: pd.DataFrame, column: str):
    if column not in frame:
        return pd.Series([None] * len(frame), index=frame.index)
    return frame[column].where(frame[column].notna(), None)


def _insert_new(connection, table: str, frame: pd.DataFrame, primary_key: str) -> int:
    if frame.empty:
        return 0
    connection.register("_incoming_core_frame", frame)
    try:
        before = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        connection.execute(
            f"""
            INSERT INTO {table} BY NAME
            SELECT incoming.*
            FROM _incoming_core_frame incoming
            WHERE NOT EXISTS (
                SELECT 1 FROM {table} existing
                WHERE existing.{primary_key} = incoming.{primary_key}
            )
            """
        )
        after = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    finally:
        connection.unregister("_incoming_core_frame")
    return int(after - before)


def _staging_frame(connection, table_name: str, source_asset_id: str) -> pd.DataFrame:
    return connection.execute(
        f"SELECT * FROM staging.{table_name} WHERE source_asset_id = ?",
        [source_asset_id],
    ).fetchdf()


def build_credit_core(connection, batch_id: str, source_asset_id: str) -> dict:
    raw = _staging_frame(connection, "stg_scored_portfolio", source_asset_id)
    prepared = prepare_scored_portfolio(raw)
    now = _now()

    borrower = pd.DataFrame(
        {
            "borrower_key": prepared["borrower_key"],
            "source_borrower_id": prepared["borrower_key"],
            "age": _numeric(prepared, "age"),
            "annual_income": _numeric(prepared, "annual_income"),
            "employment_years": _numeric(prepared, "employment_years"),
            "industry": _text(prepared, "industry"),
            "region": _text(prepared, "region"),
            "risk_profile": _text(prepared, "risk_profile"),
            "source_asset_id": source_asset_id,
            "warehouse_loaded_at": now,
        }
    ).drop_duplicates("borrower_key")

    facility = pd.DataFrame(
        {
            "facility_key": prepared["facility_key"],
            "borrower_key": prepared["borrower_key"],
            "source_account_id": None,
            "account_proxy_flag": True,
            "loan_amount": _numeric(prepared, "loan_amount"),
            "interest_rate": _numeric(prepared, "interest_rate"),
            "loan_term": _numeric(prepared, "loan_term"),
            "credit_limit": _numeric(prepared, "credit_limit"),
            "revolving_balance": _numeric(prepared, "revolving_balance"),
            "monthly_payment": _numeric(prepared, "monthly_payment"),
            "collateral_value": _numeric(prepared, "collateral_value"),
            "source_asset_id": source_asset_id,
            "warehouse_loaded_at": now,
        }
    ).drop_duplicates("facility_key")

    source_run = _text(prepared, "run_id")
    source_model = _text(prepared, "model_version")
    snapshot = pd.DataFrame(
        {
            "borrower_key": prepared["borrower_key"],
            "facility_key": prepared["facility_key"],
            "source_asset_id": source_asset_id,
            "etl_batch_id": batch_id,
            "source_run_id": source_run,
            "source_model_version": source_model,
            "scoring_execution_timestamp": prepared["scoring_execution_timestamp"],
            "temporal_basis": prepared["temporal_basis"],
            "temporal_quality": prepared["temporal_quality"],
            "pd_score": _numeric(prepared, "pd_score"),
            "lgd": _numeric(prepared, "lgd"),
            "ead": _numeric(prepared, "ead"),
            "credit_score": _numeric(prepared, "credit_score"),
            "risk_band": _text(prepared, "risk_band"),
            "risk_grade": _text(prepared, "risk_grade"),
            "underwriting_decision": _text(prepared, "underwriting_decision"),
            "ifrs_stage": prepared["ifrs_stage"],
            "scoring_status": _text(prepared, "scoring_status"),
            "industry": _text(prepared, "industry"),
            "region": _text(prepared, "region"),
            "risk_profile": _text(prepared, "risk_profile"),
            "watchlist_flag": _numeric(prepared, "watchlist_flag"),
            "target_default": _numeric(prepared, "target_default"),
            "days_past_due": _numeric(prepared, "days_past_due"),
            "total_delinquency": _numeric(prepared, "total_delinquency"),
            "credit_utilization": _numeric(prepared, "credit_utilization"),
            "payment_burden_ratio": _numeric(prepared, "payment_burden_ratio"),
            "loan_to_income_ratio": _numeric(prepared, "loan_to_income_ratio"),
            "early_warning_score": _numeric(prepared, "early_warning_score"),
            "dataset_source": _text(prepared, "dataset_source"),
            "warehouse_loaded_at": now,
        }
    )
    snapshot.insert(
        0,
        "snapshot_id",
        [
            _id(source_asset_id, borrower_key, run_id, model_version)
            for borrower_key, run_id, model_version in zip(
                snapshot["borrower_key"],
                snapshot["source_run_id"],
                snapshot["source_model_version"],
            )
        ],
    )

    borrower_rows = _insert_new(connection, "core.dim_borrower", borrower, "borrower_key")
    facility_rows = _insert_new(
        connection,
        "core.dim_credit_facility",
        facility,
        "facility_key",
    )
    snapshot_rows = _insert_new(
        connection,
        "core.fact_credit_risk_snapshot",
        snapshot,
        "snapshot_id",
    )

    reference_specs = (
        ("reference.dim_industry", "industry_key", "industry_name", prepared.get("industry")),
        ("reference.dim_region", "region_key", "region_name", prepared.get("region")),
        ("reference.dim_risk_band", "risk_band_key", "risk_band_name", prepared.get("risk_band")),
        ("reference.dim_risk_grade", "risk_grade_key", "risk_grade_name", prepared.get("risk_grade")),
        ("reference.dim_ifrs_stage", "ifrs_stage_key", "ifrs_stage_name", prepared.get("ifrs_stage")),
        ("reference.dim_data_source", "data_source_key", "data_source_name", prepared.get("dataset_source")),
    )
    for table, key_name, value_name, values in reference_specs:
        if values is None:
            continue
        distinct = pd.Series(values).dropna().astype(str).drop_duplicates()
        ref = pd.DataFrame({key_name: distinct, value_name: distinct})
        _insert_new(connection, table, ref, key_name)

    versions = prepared["model_version"].dropna().astype(str).drop_duplicates()
    current_composite = current_model_composite_version()
    model_rows = pd.DataFrame(
        [
            {
                "model_version": version,
                "model_version_source": "SCORED_PORTFOLIO",
                "artifact_match_status": (
                    "MATCHED_CURRENT_ARTIFACTS"
                    if version == current_composite
                    else "UNRESOLVED_CURRENT_ARTIFACTS_DIFFER"
                ),
                "notes": (
                    "Scored portfolio model version matches the current PD/LGD/EAD artifact composite."
                    if version == current_composite
                    else "The scored portfolio predates the current model artifacts; no false artifact association was created."
                ),
                "first_seen_at": now,
            }
            for version in versions
        ]
    )
    _insert_new(connection, "core.dim_model", model_rows, "model_version")

    record_step(
        connection,
        batch_id,
        "BUILD_CREDIT_CORE",
        status="SUCCESS",
        row_count=snapshot_rows,
        message=(
            f"borrowers={borrower_rows}; facilities={facility_rows}; "
            f"snapshots={snapshot_rows}"
        ),
    )
    return {
        "borrower_rows_inserted": borrower_rows,
        "facility_rows_inserted": facility_rows,
        "snapshot_rows_inserted": snapshot_rows,
        "source_row_count": len(prepared),
        "model_artifact_match_status": (
            "MATCHED_CURRENT_ARTIFACTS"
            if any(versions == current_composite)
            else "UNRESOLVED_CURRENT_ARTIFACTS_DIFFER"
        ),
    }


def build_model_artifact_dimension(connection) -> int:
    registry = connection.execute(
        """
        SELECT artifact_id, relative_path, sha256, size_bytes, modified_at
        FROM control.artifact_registry
        WHERE relative_path LIKE 'models/%'
        """
    ).fetchdf()
    rows = []
    for record in registry.to_dict("records"):
        family, role = artifact_role(Path(record["relative_path"]))
        rows.append(
            {
                "artifact_id": record["artifact_id"],
                "model_family": family,
                "artifact_role": role,
                "relative_path": record["relative_path"],
                "sha256": record["sha256"],
                "size_bytes": record["size_bytes"],
                "modified_at": record["modified_at"],
            }
        )
    return _insert_new(
        connection,
        "core.dim_model_artifact",
        pd.DataFrame(rows),
        "artifact_id",
    )


def build_model_risk_facts(connection, batch_id: str) -> dict:
    json_rows = connection.execute(
        """
        SELECT j.source_asset_id, j.relative_path, j.payload_json, j.loaded_at
        FROM staging.stg_json_artifact j
        """
    ).fetchdf()
    performance_rows = []
    validation_rows = []
    for row in json_rows.to_dict("records"):
        payload = json.loads(row["payload_json"])
        relpath = row["relative_path"]
        if relpath in {
            "models/model_metrics.json",
            "models/lgd_metrics.json",
            "models/ead_metrics.json",
        } and isinstance(payload, dict):
            family = {
                "models/model_metrics.json": "PD",
                "models/lgd_metrics.json": "LGD",
                "models/ead_metrics.json": "EAD",
            }[relpath]
            for metric_name, metric_value in payload.items():
                performance_rows.append(
                    {
                        "performance_id": _id(row["source_asset_id"], metric_name),
                        "source_asset_id": row["source_asset_id"],
                        "etl_batch_id": batch_id,
                        "model_family": family,
                        "metric_name": metric_name,
                        "metric_value": json.dumps(metric_value),
                        "source_generated_at": None,
                        "warehouse_loaded_at": row["loaded_at"],
                    }
                )
        elif relpath.startswith("outputs/") and isinstance(payload, dict):
            status = next(
                (
                    payload[key]
                    for key in (
                        "approval_status",
                        "overall_status",
                        "validation_status",
                        "calibration_status",
                        "oot_status",
                        "psi_status",
                        "model_replacement",
                    )
                    if payload.get(key) is not None
                ),
                None,
            )
            generated_at = payload.get("generated_at")
            validation_rows.append(
                {
                    "validation_id": _id(row["source_asset_id"], relpath),
                    "source_asset_id": row["source_asset_id"],
                    "etl_batch_id": batch_id,
                    "validation_type": relpath,
                    "validation_status": str(status) if status is not None else None,
                    "metrics_json": json.dumps(payload, default=str),
                    "source_generated_at": pd.to_datetime(
                        generated_at,
                        errors="coerce",
                        utc=True,
                    ),
                    "warehouse_loaded_at": row["loaded_at"],
                }
            )

    performance_count = _insert_new(
        connection,
        "core.fact_model_performance",
        pd.DataFrame(performance_rows),
        "performance_id",
    )
    validation_count = _insert_new(
        connection,
        "core.fact_model_validation",
        pd.DataFrame(validation_rows),
        "validation_id",
    )
    return {
        "performance_rows_inserted": performance_count,
        "validation_rows_inserted": validation_count,
    }


def build_feature_importance_fact(
    connection,
    batch_id: str,
    source_asset_id: str,
) -> int:
    frame = _staging_frame(connection, "stg_feature_importance", source_asset_id)
    now = _now()
    fact = pd.DataFrame(
        {
            "feature_importance_id": [
                _id(source_asset_id, feature)
                for feature in frame["feature"].astype(str)
            ],
            "source_asset_id": source_asset_id,
            "etl_batch_id": batch_id,
            "feature_name": frame["feature"].astype(str),
            "importance": _numeric(frame, "importance"),
            "importance_pct": _numeric(frame, "importance_pct"),
            "category": _text(frame, "category"),
            "warehouse_loaded_at": now,
        }
    )
    return _insert_new(
        connection,
        "core.fact_feature_importance",
        fact,
        "feature_importance_id",
    )


def build_market_facts(connection, batch_id: str, source_results: dict[str, dict]) -> int:
    source_specs = (
        ("fred_observation", "stg_fred_observation", "FRED", "date", "series_id", "value"),
        ("vix_observation", "stg_vix_observation", "VIX", "date", None, "close_^vix"),
        ("market_observation", "stg_market_observation", "ALPHA_VANTAGE", "date", "instrument", "close"),
    )
    rows = []
    now = _now()
    for source_name, table, system, date_col, series_col, value_col in source_specs:
        source_result = source_results.get(source_name)
        if not source_result:
            continue
        asset_id = source_result["source_asset_id"]
        frame = _staging_frame(connection, table, asset_id)
        for position, record in enumerate(frame.to_dict("records"), start=1):
            observation_date = pd.to_datetime(
                record.get(date_col),
                errors="coerce",
            )
            metric_value = pd.to_numeric(
                pd.Series([record.get(value_col)]),
                errors="coerce",
            ).iloc[0]
            rows.append(
                {
                    "observation_id": _id(asset_id, position),
                    "source_asset_id": asset_id,
                    "etl_batch_id": batch_id,
                    "source_system": system,
                    "observation_date": (
                        observation_date.date()
                        if not pd.isna(observation_date)
                        else None
                    ),
                    "series_key": (
                        str(record.get(series_col))
                        if series_col and record.get(series_col) is not None
                        else None
                    ),
                    "metric_name": value_col,
                    "metric_value": (
                        float(metric_value)
                        if not pd.isna(metric_value)
                        else None
                    ),
                    "payload_json": json.dumps(record, default=str),
                    "warehouse_loaded_at": now,
                }
            )
    return _insert_new(
        connection,
        "core.fact_market_observation",
        pd.DataFrame(rows),
        "observation_id",
    )


def build_marts(connection, batch_id: str) -> dict[str, int]:
    for path in MART_SQL_FILES:
        execute_sql_file(connection, path)
    connection.execute(
        """
        CREATE OR REPLACE TABLE mart.mart_data_quality AS
        SELECT * FROM core.fact_data_quality
        """
    )
    tables = (
        "mart_credit_risk_current",
        "mart_ifrs9_stage_current",
        "mart_ews_current",
        "mart_model_risk",
        "mart_executive_current",
        "mart_data_quality",
    )
    counts = {
        table: int(
            connection.execute(f"SELECT COUNT(*) FROM mart.{table}").fetchone()[0]
        )
        for table in tables
    }
    record_step(
        connection,
        batch_id,
        "BUILD_MARTS",
        status="SUCCESS",
        row_count=sum(counts.values()),
        message=json.dumps(counts),
    )
    return counts
