# KRONOS Phase 2A Temporal Platform Operations

## Safe Execution

Use `run_phase2a_safe()` for operational execution. Success returns
`PHASE2A_SUCCESS`. Failures return a governed status and do not affect KRONOS.

## Runtime Locations

- Database: `temporal_platform/warehouse/kronos_temporal_risk.duckdb`
- Backups: `temporal_platform/backups/`
- Evidence: `temporal_platform/evidence/phase2a/`

## Idempotency

Repeated deployment preserves one source, one snapshot, one manifest, two
contracts, five lineage nodes, four edges, and four column mappings.
Deployment, quality, reconciliation, and publish histories append per run.

## Rollback

Rollback is file-based. A first deployment may remove only the validated
temporal target after path verification. Later deployments restore a
hash-verified backup using same-volume replacement.

No rollback operation may target `data/warehouse/kronos_risk.duckdb`.

## Failure Isolation

Phase 2A is not imported by the application or existing warehouse pipelines.
Missing or corrupt temporal runtime assets therefore have no KRONOS startup
impact.
