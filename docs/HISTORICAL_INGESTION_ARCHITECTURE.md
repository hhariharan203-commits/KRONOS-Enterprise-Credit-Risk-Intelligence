# KRONOS Historical Ingestion Architecture

## Purpose

Phase 2B extends the isolated temporal database with governed historical
storage. It does not connect to the KRONOS application, current warehouse,
dashboards, Phase 4 framework, models, or analytical engines.

## Runtime

```text
temporal_platform/
├── warehouse/kronos_temporal_risk.duckdb
├── backups/
├── inbound/observed/
├── inbound/simulated/
└── evidence/phase2b/
```

All writes occur on a temporary working database. Publication replaces the
isolated temporal database only after catalog, reconciliation, lineage,
readiness, protected-hash, and Phase 2A row-preservation checks pass.

## Catalog

Phase 2B retains the five Phase 2A schemas and adds 19 base tables:

- two reference tables;
- ten historical control tables;
- two historical staging tables;
- three historical dimensions;
- two historical facts.

The governed catalog is five schemas, 36 tables, zero views, and an empty mart
schema.

## Dependency Boundary

Phase 2B may reuse Phase 2A connection, hashing, and file-publication helpers.
Phase 2A never imports Phase 2B. A read-only catalog guard prevents Phase 2A
from redeploying over a recognized Phase 2B database.

## Analytical Boundary

The platform stores source observations and source events only. Migration,
roll-rate, vintage, true OOT, and IFRS9 calculations are absent. Readiness
records remain disabled evidence for separately approved future phases.
