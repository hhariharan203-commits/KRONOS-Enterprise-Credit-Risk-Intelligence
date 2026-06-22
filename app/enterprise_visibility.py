from __future__ import annotations

import json
import logging
from pathlib import Path

import streamlit as st


ROOT_DIR = Path(__file__).resolve().parent.parent
WAREHOUSE_DB = ROOT_DIR / "data" / "warehouse" / "kronos_risk.duckdb"
ANALYTICS_ROOT = ROOT_DIR / "analytics" / "sas_style_runs"
ARTIFACT_NOT_AVAILABLE = "Artifact not available"
LOGGER = logging.getLogger(__name__)


@st.cache_data(ttl=300, show_spinner=False)
def _load_warehouse_evidence_cached(
    database_path: str,
    cache_signature: tuple[int, int],
) -> dict:
    try:
        import duckdb

        path = Path(database_path)
        if not path.is_file():
            raise FileNotFoundError("Warehouse database is unavailable.")

        connection = duckdb.connect(str(path), read_only=True)
        try:
            inventory = connection.execute(
                """
                SELECT
                    (
                        SELECT COUNT(DISTINCT schema_name)
                        FROM information_schema.schemata
                        WHERE schema_name NOT IN (
                            'information_schema', 'main', 'pg_catalog'
                        )
                    ) AS schema_count,
                    (
                        SELECT COUNT(*)
                        FROM information_schema.tables
                        WHERE table_type = 'BASE TABLE'
                          AND table_schema NOT IN (
                              'information_schema', 'pg_catalog'
                          )
                    ) AS table_count,
                    (
                        SELECT COUNT(*)
                        FROM information_schema.tables
                        WHERE table_type = 'VIEW'
                          AND table_schema NOT IN (
                              'information_schema', 'pg_catalog'
                          )
                    ) AS view_count,
                    (
                        SELECT COUNT(*) FROM control.source_asset
                        WHERE is_current
                    ) AS source_asset_count,
                    (
                        SELECT COUNT(*) FROM control.artifact_registry
                        WHERE is_current
                    ) AS artifact_count
                """
            ).fetchone()

            latest_batch = connection.execute(
                """
                SELECT
                    batch.etl_batch_id,
                    batch.status,
                    batch.duration_seconds,
                    batch.records_processed,
                    batch.records_loaded,
                    batch.records_rejected,
                    batch.source_count,
                    batch.artifact_count,
                    batch.warehouse_status,
                    COALESCE(publish.transition_at, publish.published_at)
                        AS published_at
                FROM control.etl_batch batch
                JOIN control.publish_status publish
                  ON publish.etl_batch_id = batch.etl_batch_id
                WHERE batch.batch_type = 'PHASE4B_CONTROL'
                  AND batch.status = 'SUCCESS'
                  AND publish.status = 'PUBLISHED'
                ORDER BY COALESCE(
                    publish.transition_at,
                    publish.published_at
                ) DESC
                LIMIT 1
                """
            ).fetchone()
            if latest_batch is None:
                raise RuntimeError("No published Phase 4B batch is available.")

            batch_id = str(latest_batch[0])
            quality = connection.execute(
                """
                SELECT
                    quality_score,
                    quality_status,
                    rule_count,
                    passed_rule_count,
                    warning_rule_count,
                    failed_rule_count
                FROM control.etl_quality_summary
                WHERE etl_batch_id = ?
                ORDER BY evaluated_at DESC
                LIMIT 1
                """,
                [batch_id],
            ).fetchone()
            reconciliation = connection.execute(
                """
                SELECT
                    COUNT(*) AS reconciliation_count,
                    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END)
                        AS reconciliation_passes,
                    SUM(CASE WHEN status <> 'PASS' THEN 1 ELSE 0 END)
                        AS reconciliation_failures
                FROM control.reconciliation_result
                WHERE etl_batch_id = ?
                """,
                [batch_id],
            ).fetchone()
            publication = connection.execute(
                """
                SELECT status, target_name, row_count
                FROM control.publish_status
                WHERE etl_batch_id = ?
                ORDER BY COALESCE(transition_at, published_at) DESC
                LIMIT 1
                """,
                [batch_id],
            ).fetchone()
            operational_rows = connection.execute(
                """
                SELECT metric_name, metric_value, metric_text
                FROM control.operational_metric
                WHERE etl_batch_id = ?
                """,
                [batch_id],
            ).fetchall()
            operational_metrics = {
                str(name): text if text is not None else value
                for name, value, text in operational_rows
            }

            enterprise_cursor = connection.execute(
                """
                SELECT *
                FROM mart.vw_enterprise_risk_summary_current
                """
            )
            enterprise_columns = [
                item[0] for item in enterprise_cursor.description
            ]
            enterprise_row = enterprise_cursor.fetchone()

            quality_cursor = connection.execute(
                """
                SELECT *
                FROM mart.vw_portfolio_quality_current
                """
            )
            quality_columns = [
                item[0] for item in quality_cursor.description
            ]
            quality_row = quality_cursor.fetchone()

            governance_cursor = connection.execute(
                """
                SELECT *
                FROM mart.vw_model_governance_current
                ORDER BY
                    CASE model_family
                        WHEN 'PD' THEN 1
                        WHEN 'LGD' THEN 2
                        WHEN 'EAD' THEN 3
                        ELSE 4
                    END
                """
            )
            governance_columns = [
                item[0] for item in governance_cursor.description
            ]
            governance_rows = governance_cursor.fetchall()

            concentration_cursor = connection.execute(
                """
                SELECT *
                FROM mart.vw_concentration_risk_current
                ORDER BY dimension_type, total_ead DESC, category
                """
            )
            concentration_columns = [
                item[0] for item in concentration_cursor.description
            ]
            concentration_rows = concentration_cursor.fetchall()
        finally:
            connection.close()

        reconciliation_failures = int(reconciliation[2] or 0)
        result = {
            "status": "AVAILABLE",
            "warehouse": {
                "availability": "AVAILABLE",
                "schema_count": int(inventory[0]),
                "table_count": int(inventory[1]),
                "view_count": int(inventory[2]),
                "source_asset_count": int(inventory[3]),
                "artifact_count": int(inventory[4]),
            },
            "batch": {
                "published_batch_id": batch_id,
                "batch_status": latest_batch[1],
                "duration_seconds": latest_batch[2],
                "records_processed": latest_batch[3],
                "records_loaded": latest_batch[4],
                "records_rejected": latest_batch[5],
                "source_count": latest_batch[6],
                "artifact_count": latest_batch[7],
                "warehouse_status": latest_batch[8],
                "published_at": latest_batch[9],
            },
            "quality": {
                "quality_score": quality[0] if quality else None,
                "quality_status": quality[1] if quality else None,
                "rule_count": quality[2] if quality else None,
                "passed_rule_count": quality[3] if quality else None,
                "warning_rule_count": quality[4] if quality else None,
                "failed_rule_count": quality[5] if quality else None,
            },
            "reconciliation": {
                "reconciliation_count": int(reconciliation[0] or 0),
                "reconciliation_passes": int(reconciliation[1] or 0),
                "reconciliation_failures": reconciliation_failures,
                "reconciliation_status": (
                    "PASS" if reconciliation_failures == 0 else "FAIL"
                ),
            },
            "publication": {
                "publish_status": publication[0] if publication else None,
                "target_name": publication[1] if publication else None,
                "row_count": publication[2] if publication else None,
            },
            "operational_metrics": operational_metrics,
            "enterprise_summary": dict(
                zip(enterprise_columns, enterprise_row)
            ) if enterprise_row else {},
            "portfolio_quality": dict(
                zip(quality_columns, quality_row)
            ) if quality_row else {},
            "model_governance": [
                dict(zip(governance_columns, row))
                for row in governance_rows
            ],
            "concentration": [
                dict(zip(concentration_columns, row))
                for row in concentration_rows
            ],
        }
        return result
    except Exception:
        raise


def load_warehouse_evidence(database_path: str | None = None) -> dict:
    path = Path(database_path) if database_path else WAREHOUSE_DB

    try:
        import streamlit as st

        if not path.is_file():
            return {"status": ARTIFACT_NOT_AVAILABLE}

        stat = path.stat()

        return _load_warehouse_evidence_cached(
            str(path.resolve()),
            (int(stat.st_size), int(stat.st_mtime_ns)),
        )

    except Exception as exc:
        LOGGER.exception("PHASE4E ERROR [warehouse]: %r", exc)
        return {"status": ARTIFACT_NOT_AVAILABLE}


load_warehouse_evidence.clear = _load_warehouse_evidence_cached.clear


@st.cache_data(ttl=300, show_spinner=False)
def _load_sas_analytics_evidence_cached(
    analytics_root: str,
    cache_signature: tuple[tuple[str, int, int], ...],
) -> dict:
    try:
        root = Path(analytics_root)
        if not root.is_dir():
            raise FileNotFoundError("SAS-style analytics root is unavailable.")

        manifests = sorted(
            root.glob("*/manifest.json"),
            key=lambda path: path.parent.name,
            reverse=True,
        )
        if not manifests:
            raise FileNotFoundError("No SAS-style analytics manifest is available.")

        manifest_path = manifests[0]
        run_directory = manifest_path.parent
        manifest_bytes = manifest_path.read_bytes()
        manifest = json.loads(manifest_bytes)

        inventory_path = run_directory / "hash_inventory.json"
        report_path = run_directory / "institutional_report_pack.md"
        if not inventory_path.is_file() or not report_path.is_file():
            raise FileNotFoundError("SAS-style analytics evidence is incomplete.")

        inventory_bytes = inventory_path.read_bytes()
        inventory = json.loads(inventory_bytes)
        report_bytes = report_path.read_bytes()
        metadata = manifest.get("run_metadata", {})

        result = {
            "status": "AVAILABLE",
            "framework": manifest.get("framework"),
            "terminology": manifest.get("terminology"),
            "run_metadata": metadata,
            "output_count": manifest.get("output_count"),
            "hash_inventory_count": len(inventory),
            "warehouse_read_only": manifest.get("warehouse_read_only"),
            "warehouse_unchanged": manifest.get("warehouse_unchanged"),
            "borrower_level_ranks_persisted": manifest.get(
                "borrower_level_ranks_persisted"
            ),
            "disclaimer": manifest.get(
                "current_credit_loss_proxy_disclaimer"
            ),
            "downloads": {
                "manifest.json": manifest_bytes,
                "hash_inventory.json": inventory_bytes,
                "institutional_report_pack.md": report_bytes,
            },
        }
        return result
    except Exception:
        raise


def load_sas_analytics_evidence(analytics_root: str | None = None) -> dict:
    root = Path(analytics_root) if analytics_root else ANALYTICS_ROOT
    try:
        if not root.is_dir():
            return {"status": ARTIFACT_NOT_AVAILABLE}

        manifests = sorted(
            root.glob("*/manifest.json"),
            key=lambda path: path.parent.name,
            reverse=True,
        )
        if not manifests:
            return {"status": ARTIFACT_NOT_AVAILABLE}

        run_directory = manifests[0].parent
        required_paths = (
            run_directory / "manifest.json",
            run_directory / "hash_inventory.json",
            run_directory / "institutional_report_pack.md",
        )
        if not all(path.is_file() for path in required_paths):
            return {"status": ARTIFACT_NOT_AVAILABLE}

        signature = tuple(
            (
                path.name,
                int(path.stat().st_size),
                int(path.stat().st_mtime_ns),
            )
            for path in required_paths
        )
        return _load_sas_analytics_evidence_cached(
            str(root.resolve()),
            signature,
        )
    except Exception as exc:
        LOGGER.exception("PHASE4E ERROR [sas_analytics]: %r", exc)
        return {"status": ARTIFACT_NOT_AVAILABLE}


load_sas_analytics_evidence.clear = _load_sas_analytics_evidence_cached.clear


@st.cache_data(ttl=300, show_spinner=False)
def load_download_artifact(
    relative_path: str,
    base_directory: str | None = None,
) -> dict:
    try:
        base = Path(base_directory) if base_directory else ROOT_DIR
        path = base / relative_path
        if not path.is_file():
            return {"status": ARTIFACT_NOT_AVAILABLE}
        return {
            "status": "AVAILABLE",
            "file_name": path.name,
            "data": path.read_bytes(),
        }
    except Exception:
        return {"status": ARTIFACT_NOT_AVAILABLE}
