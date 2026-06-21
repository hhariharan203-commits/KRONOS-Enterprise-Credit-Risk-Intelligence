# KRONOS Phase 2A Temporal Platform Architecture

## Purpose

Phase 2A is an independently removable control foundation. It registers the
current scored portfolio as metadata and does not store borrower history or
provide temporal analytics.

## Isolation

Runtime assets are stored only under `temporal_platform/`. The platform does
not import application, Phase 4, scoring, validation, provisioning, EWS,
stress, contagion, decisioning, reporting, or SAS-style analytics modules.

The existing `data/warehouse/kronos_risk.duckdb` database is opened read-only
for before-and-after compatibility evidence. It is never attached to the
temporal database.

## Database

The isolated database contains five schemas:

- `control`
- `staging`
- `reference`
- `core`
- `mart`

Phase 2A contains seventeen base tables and no views. The `core` and `mart`
schemas remain empty.

## Publication

Deployment uses a working database in the temporal runtime directory. Quality,
reconciliation, lineage, scope, and dynamic baseline gates must pass before
same-volume publication. An existing temporal database is hash-verified and
backed up before replacement.

## Removal

Deleting `src/temporal_risk/`, `sql/phase2a/`, and `temporal_platform/` removes
Phase 2A without affecting KRONOS startup or any completed phase.
