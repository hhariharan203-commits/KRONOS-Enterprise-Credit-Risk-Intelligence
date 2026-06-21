# KRONOS Historical Data Dictionary

## Reference

- `reference.dim_identity_grain`: borrower and facility identity contracts.
- `reference.dim_readiness_status`: disabled readiness classifications.

## Control

- `control.historical_ingestion_batch`: batch lifecycle, counts, hashes, and
  the fixed 36-control quality payload.
- `control.historical_ingestion_file`: immutable source and manifest metadata.
- `control.historical_field_mapping`: explicit source-to-canonical mappings.
- `control.historical_reject_record`: rejected-row evidence.
- `control.data_readiness_result`: six future-capability readiness records.
- `control.historical_reconciliation_result`: twelve parity controls.
- `control.historical_lineage_node`: Phase 2B lineage nodes.
- `control.historical_lineage_edge`: Phase 2B lineage edges.
- `control.historical_column_lineage`: canonical mapped-field lineage.
- `control.historical_publish_status`: draft, validated, and published states.

## Staging

- `staging.stg_historical_snapshot_row`: one immutable source row per batch and
  snapshot, including rejected rows.
- `staging.stg_historical_event_row`: explicitly source-supplied events only.

## Core

- `core.dim_historical_entity`: stable source entity identity with a technical
  SHA-256 key.
- `core.dim_historical_facility`: source facilities when a stable facility ID
  exists.
- `core.dim_historical_snapshot`: governed temporal snapshot metadata.
- `core.fact_historical_credit_observation`: accepted source observations.
- `core.fact_historical_credit_event`: accepted source-supplied events.

## Readiness Ceiling

`IFRS9_TEMPORAL_INPUTS` can only be `NOT_READY` or `NOT_ELIGIBLE` in Phase 2B.
Its activation status is always `DISABLED_PENDING_FUTURE_PHASE`.
