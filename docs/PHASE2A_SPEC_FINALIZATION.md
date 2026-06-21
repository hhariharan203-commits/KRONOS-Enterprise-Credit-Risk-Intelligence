# KRONOS Phase 2A Specification Finalization

## Finalized Baseline Rules

Do not hardcode the current warehouse hash, artifact-registry count, portfolio
row count, source column count, run-ID count, model-version count, identifiers,
or process timestamp as permanent platform requirements.

Required behavior:

1. Capture the current warehouse hash and catalog at deployment start.
2. Capture the artifact-registry count at deployment start.
3. Capture the complete scored-portfolio profile at deployment start.
4. Verify all captured values remain unchanged after deployment.
5. Store complete sorted run-ID and model-version inventories in evidence.
6. Use inventory-aware deterministic snapshot identity.

## Fixed Architecture

The following remain fixed:

- runtime under `temporal_platform/`,
- five schemas,
- seventeen tables,
- zero views,
- empty `core` and `mart`,
- twenty-seven DQ controls,
- nine reconciliations,
- five lineage nodes,
- four lineage edges,
- four column mappings,
- `PROCESS_TIME_ONLY`,
- `SYNTHETIC_BASELINE`,
- `NOT_ESTABLISHED`,
- historical eligibility false,
- file-based rollback,
- no Phase 2B functionality.
