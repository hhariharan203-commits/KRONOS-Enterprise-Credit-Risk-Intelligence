# KRONOS Phase 2 Implementation Blueprint

## Architecture Decision

Create a separate temporal platform while preserving:

- `data/processed/scored_portfolio.csv`
- `data/warehouse/kronos_risk.duckdb`
- all completed Phase 1 and Phase 4 functionality.

## Phases

1. Phase 2A: temporal control foundation.
2. Phase 2B: governed historical ingestion.
3. Phase 2C: migration and roll-rate analytics.
4. Phase 2D: vintage analytics.
5. Phase 2E: true OOT development and monitoring.
6. Phase 2F: temporal IFRS9 architecture.

Each phase requires independent approval and data-readiness gates.

## Temporal Integrity

No business date, account identifier, vintage, default event, cure event,
recovery event, or contractual schedule may be fabricated.

Temporal evidence must be classified as `OBSERVED_TEMPORAL`,
`SIMULATED_TEMPORAL`, `PROCESS_TIME_ONLY`, or `UNKNOWN`.

## Isolation

The temporal platform must be independently removable and must never become an
application, dashboard, scoring, warehouse, ETL, analytics, or startup
dependency.

## Phase 2A

Phase 2A creates only isolated schemas, control tables, source and snapshot
metadata, DQ, reconciliation, lineage, publication controls, protected-hash
evidence, and file-level rollback.
