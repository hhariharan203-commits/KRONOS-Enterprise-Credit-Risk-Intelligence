from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from src.enterprise_data.config import CSV_SOURCES
from src.enterprise_data.schema_manager import table_columns


def _id(*values) -> str:
    return hashlib.sha256(
        "|".join("" if value is None else str(value) for value in values).encode("utf-8")
    ).hexdigest()[:32]


def _node(connection, node_type: str, node_name: str, object_path: str | None) -> str:
    node_id = _id(node_type, node_name, object_path)
    connection.execute(
        """
        INSERT OR IGNORE INTO control.lineage_node (
            lineage_node_id, node_type, node_name, object_path, created_at
        ) VALUES (?, ?, ?, ?, ?)
        """,
        [node_id, node_type, node_name, object_path, datetime.now(timezone.utc)],
    )
    return node_id


def _edge(
    connection,
    batch_id: str,
    upstream: str,
    downstream: str,
    transformation: str,
) -> None:
    edge_id = _id(batch_id, upstream, downstream, transformation)
    connection.execute(
        """
        INSERT OR IGNORE INTO control.lineage_edge (
            lineage_edge_id, upstream_node_id, downstream_node_id,
            transformation_name, etl_batch_id, created_at
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            edge_id,
            upstream,
            downstream,
            transformation,
            batch_id,
            datetime.now(timezone.utc),
        ],
    )


def _column(
    connection,
    batch_id: str,
    source_asset_id: str | None,
    source_column: str,
    target_schema: str,
    target_table: str,
    target_column: str,
    transformation: str,
) -> None:
    lineage_id = _id(
        batch_id,
        source_asset_id,
        source_column,
        target_schema,
        target_table,
        target_column,
    )
    connection.execute(
        """
        INSERT OR IGNORE INTO control.column_lineage (
            column_lineage_id, etl_batch_id, source_asset_id, source_column,
            target_schema, target_table, target_column, transformation, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            lineage_id,
            batch_id,
            source_asset_id,
            source_column,
            target_schema,
            target_table,
            target_column,
            transformation,
            datetime.now(timezone.utc),
        ],
    )


def build_lineage(
    connection,
    batch_id: str,
    source_results: list[dict],
) -> dict:
    by_name = {
        source.source_name: (source, result)
        for source, result in zip(CSV_SOURCES, source_results)
    }
    for source, result in zip(CSV_SOURCES, source_results):
        source_node = _node(
            connection,
            "SOURCE_FILE",
            source.source_name,
            result["relative_path"],
        )
        staging_node = _node(
            connection,
            "STAGING_TABLE",
            source.staging_table,
            f"staging.{source.staging_table}",
        )
        _edge(connection, batch_id, source_node, staging_node, "READ_ONLY_MIRROR")
        columns = table_columns(connection, "staging", source.staging_table)
        for column in columns:
            if column in {
                "etl_batch_id",
                "source_asset_id",
                "source_sha256",
                "loaded_at",
            }:
                continue
            _column(
                connection,
                batch_id,
                result["source_asset_id"],
                column,
                "staging",
                source.staging_table,
                column,
                "IDENTITY_MIRROR",
            )

    scored_source, scored_result = by_name["scored_portfolio"]
    staging_node = _node(
        connection,
        "STAGING_TABLE",
        scored_source.staging_table,
        f"staging.{scored_source.staging_table}",
    )
    core_node = _node(
        connection,
        "CORE_TABLE",
        "fact_credit_risk_snapshot",
        "core.fact_credit_risk_snapshot",
    )
    _edge(connection, batch_id, staging_node, core_node, "NORMALIZE_AND_SNAPSHOT")

    core_columns = table_columns(connection, "core", "fact_credit_risk_snapshot")
    source_columns = set(
        table_columns(connection, "staging", scored_source.staging_table)
    )
    technical_mapping = {
        "borrower_key": "borrower_id",
        "facility_key": "borrower_id",
        "source_run_id": "run_id",
        "source_model_version": "model_version",
        "scoring_execution_timestamp": "timestamp",
        "temporal_basis": "timestamp",
        "temporal_quality": "timestamp",
        "warehouse_loaded_at": "loaded_at",
        "snapshot_id": "borrower_id",
        "etl_batch_id": "etl_batch_id",
        "source_asset_id": "source_asset_id",
    }
    for target in core_columns:
        source_column = target if target in source_columns else technical_mapping.get(target)
        if source_column:
            _column(
                connection,
                batch_id,
                scored_result["source_asset_id"],
                source_column,
                "core",
                "fact_credit_risk_snapshot",
                target,
                "IDENTITY_OR_TECHNICAL_NORMALIZATION",
            )

    mart_sources = {
        "mart_credit_risk_current": "fact_credit_risk_snapshot",
        "mart_ifrs9_stage_current": "fact_credit_risk_snapshot",
        "mart_ews_current": "fact_credit_risk_snapshot",
        "mart_model_risk": "fact_model_validation",
        "mart_executive_current": "fact_credit_risk_snapshot",
        "mart_data_quality": "fact_data_quality",
    }
    for mart_table, core_table in mart_sources.items():
        upstream = _node(
            connection,
            "CORE_TABLE",
            core_table,
            f"core.{core_table}",
        )
        downstream = _node(
            connection,
            "MART_TABLE",
            mart_table,
            f"mart.{mart_table}",
        )
        _edge(connection, batch_id, upstream, downstream, "SQL_MART_BUILD")
        mart_columns = table_columns(connection, "mart", mart_table)
        core_available = set(table_columns(connection, "core", core_table))
        for target in mart_columns:
            source_column = target if target in core_available else next(
                iter(core_available),
                "source_asset_id",
            )
            _column(
                connection,
                batch_id,
                scored_result["source_asset_id"],
                source_column,
                "mart",
                mart_table,
                target,
                "IDENTITY_OR_AGGREGATION",
            )

    mart_column_count = connection.execute(
        """
        SELECT COUNT(*) FROM information_schema.columns
        WHERE table_schema = 'mart' AND table_name LIKE 'mart_%'
        """
    ).fetchone()[0]
    lineage_count = connection.execute(
        """
        SELECT COUNT(*) FROM control.column_lineage
        WHERE etl_batch_id = ? AND target_schema = 'mart'
        """,
        [batch_id],
    ).fetchone()[0]
    return {
        "mart_column_count": int(mart_column_count),
        "mart_lineage_count": int(lineage_count),
        "complete": int(lineage_count) >= int(mart_column_count),
    }


def build_etl_job_lineage(connection, batch_id: str) -> dict:
    batch_node = _node(
        connection,
        "ETL_BATCH",
        batch_id,
        f"control.etl_batch/{batch_id}",
    )
    job_rows = connection.execute(
        """
        SELECT job_id, job_name, job_type
        FROM control.etl_job_run
        WHERE etl_batch_id = ?
        ORDER BY start_time NULLS LAST, job_name
        """,
        [batch_id],
    ).fetchall()
    source_rows = connection.execute(
        """
        SELECT source_name, relative_path
        FROM control.source_asset
        WHERE file_type = 'CSV'
        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY relative_path ORDER BY last_seen_at DESC
        ) = 1
        ORDER BY relative_path
        """
    ).fetchall()
    staging_tables = [
        source.staging_table
        for source in CSV_SOURCES
    ]
    core_tables = [
        "dim_borrower",
        "dim_credit_facility",
        "dim_model",
        "dim_model_artifact",
        "fact_credit_risk_snapshot",
        "fact_data_quality",
        "fact_feature_importance",
        "fact_market_observation",
        "fact_model_performance",
        "fact_model_validation",
    ]
    mart_tables = [
        "mart_credit_risk_current",
        "mart_ifrs9_stage_current",
        "mart_ews_current",
        "mart_model_risk",
        "mart_executive_current",
        "mart_data_quality",
    ]
    edge_count = 0
    for job_id, job_name, job_type in job_rows:
        job_node = _node(
            connection,
            "ETL_JOB",
            job_name,
            f"control.etl_job_run/{batch_id}/{job_id}",
        )
        _edge(connection, batch_id, batch_node, job_node, "BATCH_EXECUTES_JOB")
        edge_count += 1

        targets: list[tuple[str, str, str]] = []
        if job_type == "SOURCE_LOAD":
            targets.extend(
                ("SOURCE_FILE", name, path)
                for name, path in source_rows
            )
        elif job_type in {"VALIDATION", "STAGING_LOAD"}:
            targets.extend(
                ("STAGING_TABLE", table, f"staging.{table}")
                for table in staging_tables
            )
        elif job_type == "CORE_LOAD":
            targets.extend(
                ("CORE_TABLE", table, f"core.{table}")
                for table in core_tables
            )
        elif job_type in {"MART_BUILD", "PUBLISH"}:
            targets.extend(
                ("MART_TABLE", table, f"mart.{table}")
                for table in mart_tables
            )
        elif job_type == "RECONCILIATION":
            targets.extend(
                [
                    (
                        "CONTROL_TABLE",
                        "reconciliation_result",
                        "control.reconciliation_result",
                    ),
                    (
                        "MART_TABLE",
                        "mart_credit_risk_current",
                        "mart.mart_credit_risk_current",
                    ),
                ]
            )
        elif job_type == "LINEAGE":
            targets.extend(
                [
                    ("CONTROL_TABLE", "lineage_node", "control.lineage_node"),
                    ("CONTROL_TABLE", "lineage_edge", "control.lineage_edge"),
                    ("CONTROL_TABLE", "column_lineage", "control.column_lineage"),
                ]
            )

        for node_type, node_name, object_path in targets:
            target_node = _node(
                connection,
                node_type,
                node_name,
                object_path,
            )
            _edge(
                connection,
                batch_id,
                job_node,
                target_node,
                f"JOB_{job_type}_OBJECT",
            )
            edge_count += 1

    batch_edges = int(
        connection.execute(
            """
            SELECT COUNT(*)
            FROM control.lineage_edge
            WHERE etl_batch_id = ?
              AND transformation_name = 'BATCH_EXECUTES_JOB'
            """,
            [batch_id],
        ).fetchone()[0]
    )
    object_edges = int(
        connection.execute(
            """
            SELECT COUNT(*)
            FROM control.lineage_edge
            WHERE etl_batch_id = ?
              AND transformation_name LIKE 'JOB_%_OBJECT'
            """,
            [batch_id],
        ).fetchone()[0]
    )
    return {
        "job_count": len(job_rows),
        "batch_job_edges": batch_edges,
        "job_object_edges": object_edges,
        "edges_processed": edge_count,
        "complete": batch_edges == len(job_rows) and object_edges > 0,
    }
