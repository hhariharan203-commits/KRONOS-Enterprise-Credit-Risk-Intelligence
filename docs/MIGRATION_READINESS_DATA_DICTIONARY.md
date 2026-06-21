# Migration Readiness Data Dictionary

## Control Tables

| Table | Grain | Purpose |
|---|---|---|
| `control.migration_readiness_run` | One deployment or readiness evaluation | Run lifecycle, governed contracts, score, status, and hashes |
| `control.migration_snapshot_pair` | One governed snapshot pair and state field | Pair identity and continuity evidence |
| `control.migration_transition_contract` | One controlled contract version | Readiness and domain definitions |
| `control.migration_quality_result` | One control per readiness run | Twenty-four critical checks |
| `control.migration_readiness_result` | One capability per readiness run | Four disabled readiness outcomes |
| `control.migration_reconciliation_result` | One reconciliation per readiness run | Ten pair-level parity controls |
| `control.migration_lineage_node` | One governed provenance node | Independent Phase 2C lineage |
| `control.migration_lineage_edge` | One provenance relationship | Source-to-control relationships |
| `control.migration_column_lineage` | One source-column mapping | Identity, date, and state provenance |
| `control.migration_publish_status` | One lifecycle transition | Draft, validated, and published history |

## Supported State Fields

Only:

- `risk_grade`
- `risk_band`

Values are validated by exact case-sensitive membership in the applicable
controlled domain contract.

## Readiness Capabilities

- `SNAPSHOT_CONTINUITY`
- `IDENTITY_CONTINUITY`
- `STATE_FIELD_CONTINUITY`
- `MIGRATION_TRANSITION_INPUTS`

All capability rows retain disabled analytical activation.

## Production Population

At Phase 2C publication:

```text
Historical snapshots:      0
Historical observations:   0
Historical ingestion runs: 0
Readiness results:          0
```

The production readiness status is therefore
`PHASE2C_SOURCE_NOT_READY`.
