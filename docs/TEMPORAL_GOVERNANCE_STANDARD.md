# KRONOS Phase 2A Temporal Governance Standard

## Boundary

Phase 2A may register baseline metadata, contracts, snapshot metadata, quality,
reconciliation, lineage, and publication evidence only.

It prohibits historical borrower records, historical scoring, model execution,
migration matrices, roll rates, vintage curves, true OOT validation, temporal
IFRS9 ECL, dashboards, application integration, warehouse integration,
enterprise visibility, SAS-style analytics, and Phase 4 integration.

Scope violations return `PHASE2A_SCOPE_VIOLATION`.

## Temporal Integrity

Process time must never be represented as observation, reporting, origination,
vintage, default, cure, recovery, or maturity time. Missing dates remain null.

The current baseline is synthetic and does not establish longitudinal borrower
or account identity.

## Dynamic Protection

Repository-specific hashes, counts, identifiers, and source dimensions are
captured at deployment start and compared after deployment. They are evidence,
not permanent temporal-platform requirements.

## Publication Gate

Publication requires:

- twenty-seven DQ checks with no failures,
- nine reconciliations with no failures,
- complete five-node/four-edge/four-column lineage,
- unchanged current warehouse and scored portfolio,
- unchanged protected-file inventory,
- no scope-boundary violation.
