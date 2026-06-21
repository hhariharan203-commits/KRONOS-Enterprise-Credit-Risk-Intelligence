# KRONOS Phase 2A Implementation Prompt

## Implementation Boundary

Phase 2A is a control foundation only.

Explicitly prohibited:

- historical borrower records,
- historical scoring or model execution,
- migration matrices,
- roll rates,
- vintage curves,
- true OOT validation,
- temporal IFRS9 ECL,
- dashboards and application integration,
- current warehouse integration,
- SAS-style analytics,
- Phase 4 integration.

Phase 2A may only create the isolated control platform, register baseline and
snapshot metadata, register temporal contracts, execute DQ and reconciliation,
persist lineage, and publish the isolated database.

Scope violations return:

```text
PHASE2A_SCOPE_VIOLATION
```

## Removability

Deleting `src/temporal_risk/`, `sql/phase2a/`, and `temporal_platform/` must
remove operational Phase 2A without affecting KRONOS startup or any completed
phase.

## Preflight

Target, runtime root, scope, and controlled specifications must be validated
before evidence directories, files, or writable databases are created.

## Contracts

The isolated database must retain the 5/17/0 schema contract, empty core/mart,
27 DQ controls, nine reconciliations, and 5/4/4 lineage.

Repository-specific source and warehouse values are captured dynamically and
verified unchanged after deployment.
