# KRONOS Phase 2 Impact Analysis

## Decision

Use Option B: preserve the current single-snapshot KRONOS platform and create a
separate historical architecture. The current scored portfolio and
`kronos_risk.duckdb` remain authoritative for existing workflows.

## Current Temporal State

KRONOS contains one borrower-level scoring run and one scoring process
timestamp. It has no genuine observation, reporting, origination, vintage,
default, cure, recovery, maturity, or contractual cash-flow dates.

The existing OOT framework is a documented row-order proxy. Existing IFRS9
logic uses current-state staging and stage multipliers rather than temporal,
discounted lifetime expected-loss mechanics.

## Phase 2 Direction

Phase 2 must use an isolated architecture that can distinguish:

- observed temporal evidence,
- explicitly simulated temporal evidence,
- process-time-only evidence.

Only source-supplied observed dates may enable migration, vintage, roll-rate,
true OOT, or temporal IFRS9 claims.

## Compatibility

Phase 2 must not replace or modify Phase 1, Phase 1.5, Phase 4A, Phase 4B,
Phase 4C, Phase 4D, Phase 4E, current models, current dashboards, current
scoring, current datasets, or the current warehouse.

## Phase 2A Boundary

Phase 2A establishes temporal contracts, registries, quality, reconciliation,
lineage, deployment safety, and rollback only. It contains no historical
ingestion or analytical capability.
