from __future__ import annotations

from dataclasses import asdict

from src.enterprise_data.sas_analytics.contracts import AnalyticsRunMetadata


def build_lineage_manifest(
    metadata: AnalyticsRunMetadata,
    artifacts: list[dict],
) -> dict:
    return {
        "framework": "KRONOS SAS-Style Analytics",
        "execution_timestamp": metadata.execution_timestamp,
        "analytics_run_id": metadata.analytics_run_id,
        "source_asset": {
            "source_asset_id": metadata.source_asset_id,
            "source_hash": metadata.source_hash,
            "published_batch_id": metadata.published_batch_id,
            "model_version": metadata.model_version,
        },
        "lineage_entries": [
            {
                "warehouse_objects": artifact["warehouse_objects"],
                "analytics_module": artifact["analytics_module"],
                "output_artifact": artifact["relative_path"],
                "file_hash": artifact["sha256"],
                "execution_timestamp": metadata.execution_timestamp,
            }
            for artifact in artifacts
        ],
        "run_metadata": asdict(metadata),
        "warehouse_lineage_modified": False,
    }
