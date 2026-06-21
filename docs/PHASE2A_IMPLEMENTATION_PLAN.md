# KRONOS Phase 2A Implementation Plan

## Scope

Phase 2A is a control foundation only. It creates an isolated temporal
database, source and snapshot registries, temporal contracts, DQ controls,
reconciliations, lineage, publication safety, and rollback.

## Runtime

Runtime assets must exist only under:

```text
temporal_platform/
├── warehouse/
├── backups/
└── evidence/
```

## Database Contract

- Five schemas: `control`, `staging`, `reference`, `core`, `mart`
- Seventeen base tables
- Zero views
- Empty `core`
- Empty `mart`

## Current Baseline

The current portfolio must be classified as:

- `PROCESS_TIME_ONLY`
- `SYNTHETIC_BASELINE`
- identity continuity `NOT_ESTABLISHED`
- historical eligibility false.

## Controls

- Twenty-seven DQ controls
- Nine reconciliations
- Five lineage nodes
- Four lineage edges
- Four column-lineage mappings

## Safety

All repository-specific counts, hashes, identifiers, timestamps, run
inventories, and model-version inventories are dynamic deployment evidence.
They are not permanent temporal-platform assumptions.

Rollback is file-based only.
