# KRONOS Phase 2A Temporal Control Data Dictionary

## Reference

- `dim_temporal_classification`: governed temporal provenance classes.
- `dim_snapshot_status`: snapshot lifecycle values.

## Control

- `platform_release`: Phase 2A release metadata.
- `deployment_run`: append-only deployment execution history.
- `source_asset`: hash-versioned baseline source metadata.
- `source_column`: ordered source schema and semantic roles.
- `temporal_contract`: governed current and future temporal contracts.
- `snapshot_registry`: metadata-only snapshot registration.
- `snapshot_source_link`: source-to-snapshot provenance.
- `temporal_quality_result`: twenty-seven controls per deployment.
- `reconciliation_result`: nine controls per deployment.
- `lineage_node`: five independent Phase 2A lineage nodes.
- `lineage_edge`: four independent Phase 2A lineage edges.
- `column_lineage`: four source-to-registry mappings.
- `publish_status`: DRAFT, VALIDATED, and PUBLISHED transitions.
- `rollback_event`: file-level rollback metadata.

## Staging

`stg_snapshot_manifest` contains one metadata record for the current baseline.
It contains no borrower-level records.

## Current Classification

- History mode: `PROCESS_TIME_ONLY`
- Evidence: `SYNTHETIC_BASELINE`
- Identity continuity: `NOT_ESTABLISHED`
- Historical eligibility: false
- Source-date provenance: `PROCESS_TIMESTAMP_ONLY`
