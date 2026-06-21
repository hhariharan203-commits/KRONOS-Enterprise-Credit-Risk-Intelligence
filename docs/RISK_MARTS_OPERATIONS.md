# KRONOS Enterprise Risk Marts Operations

## Run Phase 4D

From the repository root:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -m src.enterprise_data.risk_marts.runner
```

Success returns:

```text
PHASE4D_SUCCESS
```

Failure returns:

```text
MARTS_UNAVAILABLE
```

The safe entry point does not propagate warehouse exceptions.

## Operational Preconditions

- `data/warehouse/kronos_risk.duckdb` exists.
- The Phase 4A current credit mart is populated.
- A successful published Phase 4B batch exists.
- Phase 1 validation facts are available in the warehouse.
- Existing mart counts satisfy the governed contracts.

## Refresh Behavior

Phase 4D views are logical current-state objects. They do not copy borrower
records or maintain independent history.

Deployment is restart-safe and idempotent:

- repeated execution recreates only the owned views,
- schema and base-table counts remain unchanged,
- existing mart row counts remain unchanged,
- validation occurs before publication.

## Verification Queries

```sql
SELECT dimension_type, COUNT(*), SUM(exposure_share)
FROM mart.vw_concentration_risk_current
GROUP BY dimension_type;
```

```sql
SELECT portfolio_count, total_ead, watchlist_count,
       stage_1_count + stage_2_count + stage_3_count AS stage_total
FROM mart.vw_portfolio_quality_current;
```

```sql
SELECT model_family, approval_status, calibration_status,
       validation_status, governance_status, artifact_match_status
FROM mart.vw_model_governance_current
ORDER BY model_family;
```

```sql
SELECT data_quality_status, reconciliation_status, publish_status
FROM mart.vw_enterprise_risk_summary_current;
```

## Tests

```powershell
python -m pytest -q -p no:cacheprovider `
  tests/test_phase4d_schema.py `
  tests/test_phase4d_concentration.py `
  tests/test_phase4d_portfolio_quality.py `
  tests/test_phase4d_watchlist.py `
  tests/test_phase4d_model_governance.py `
  tests/test_phase4d_reconciliation.py `
  tests/test_phase4d_idempotency.py `
  tests/test_phase4d_compatibility.py
```

## Rollback

1. Prepare a working copy of `data/warehouse/kronos_risk.duckdb`.
2. Execute `sql/phase4d/rollback_phase4d_views.sql` against the working copy.
3. Confirm the five Phase 4D views are absent.
4. Confirm five schemas and 58 base tables remain.
5. Confirm all original mart row counts.
6. Publish the verified working copy.

The rollback SQL contains five `DROP VIEW IF EXISTS` statements and no table
or schema operation.

## Control View Contract

`control.vw_latest_reconciliation` and `control.vw_latest_data_quality` use
explicit column projections. Warehouse and ETL schema initialization recreate
these views after idempotent control-table migrations, preventing stale DuckDB
view signatures when control columns are added.
