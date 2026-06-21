# Migration Readiness Architecture

## Purpose

Phase 2C adds an isolated governance layer that determines whether two
source-supplied observed snapshots contain sufficient continuity evidence for
a separately authorized future phase.

It does not calculate migration analytics.

## Platform Boundary

Phase 2C extends only:

```text
temporal_platform/warehouse/kronos_temporal_risk.duckdb
```

It has no dependency from application startup, dashboards, current scoring,
the current KRONOS warehouse, Phase 4, or SAS-style analytics.

## Catalog

The accepted Phase 2B catalog contained five schemas and 36 tables. Phase 2C
adds ten control tables, producing:

```text
Schemas:      5
Tables:      46
Views:        0
Mart objects: 0
```

No staging, reference, core, or mart object is added.

## Runtime Flow

1. Validate the exact catalog and published earlier releases.
2. Verify controlled readiness and state-domain contracts.
3. Confirm that two qualifying observed snapshots exist.
4. Select explicit snapshot identifiers or apply deterministic selection.
5. Validate identity, date, source, state-field, and domain continuity.
6. Execute 24 critical quality controls.
7. Execute ten pair-level reconciliations.
8. Persist four disabled readiness results.
9. Persist independent provenance lineage.
10. Publish through a verified working database copy.

When qualifying source history is unavailable, the process returns
`PHASE2C_SOURCE_NOT_READY` before any mutation.

## Isolation

Phase 2C has dedicated quality, readiness, reconciliation, lineage, run, pair,
contract, and publication tables. It does not write Phase 2A or Phase 2B
control evidence.
