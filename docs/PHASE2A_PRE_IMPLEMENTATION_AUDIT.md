# KRONOS Phase 2A Pre-Implementation Audit

## Decision

**APPROVED WITH CHANGES**

## Authoritative Corrections

1. Store runtime assets under `temporal_platform/`, outside Phase 4 artifact
   discovery roots.
2. Execute twenty-seven DQ controls.
3. Execute nine reconciliations.
4. Persist lineage with five nodes, four edges, and four column mappings.
5. Classify the current source as `PROCESS_TIME_ONLY`,
   `SYNTHETIC_BASELINE`, and `NOT_ESTABLISHED`.
6. Keep historical eligibility false.
7. Use file-level rollback; do not create rollback SQL.
8. Use SHA-256 inventories rather than Git assumptions.
9. Validate target and scope before persistent writes.
10. Treat run/model cardinalities as dynamic evidence.

## Hidden Dependency Control

Phase 4 artifact discovery scans `data/` and `outputs/`. Phase 2A runtime
assets must therefore remain outside those directories.

## Approval Condition

Implementation may proceed only under the Phase 2A control boundary and must
remain independently removable.
