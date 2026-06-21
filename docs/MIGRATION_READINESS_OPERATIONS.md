# Migration Readiness Operations

## Schema Deployment

Use the safe Phase 2C schema entry point. Deployment:

1. validates the exact Phase 2B baseline;
2. captures database, protected-file, and row-hash baselines;
3. creates and verifies a backup;
4. applies two controlled DDL assets to a working copy;
5. validates the exact Phase 2C catalog;
6. registers controlled contracts and the Phase 2C release;
7. verifies earlier-phase row preservation;
8. publishes the closed working database.

## Readiness Evaluation

Evaluation requires one supported state field and either:

- explicit earlier and later snapshot identifiers; or
- a source system and identity grain for deterministic selection.

With fewer than two qualifying observed snapshots, the entry point returns
`PHASE2C_SOURCE_NOT_READY` without creating a run, backup, working database,
or evidence directory.

## Expected Successful Control Counts

```text
Quality controls:       24
Readiness results:       4
Reconciliations:        10
Lineage nodes:          10
Lineage edges:          12
Column lineage:     at least 6
```

## Rollback

Schema deployment rollback restores the exact pre-deployment database and
36-table catalog.

Readiness-run rollback restores the exact pre-run database and 46-table
catalog.

Full removal first restores the verified pre-Phase 2C database, then removes
Phase 2C authored assets and reverts only the approved catalog-recognition
changes.

## Failure Isolation

Safe entry points return governed statuses. Phase 2C failure has no effect on
KRONOS startup, dashboards, scoring, current warehouse operation, or accepted
earlier phases.
