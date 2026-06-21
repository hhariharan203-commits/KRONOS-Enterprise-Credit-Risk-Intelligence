# KRONOS Phase 4E Runtime Bug Root Cause

## Final Status

**PASS**

Phase 4E now loads existing Phase 4A-4D evidence under the same Python
interpreter used by Streamlit. Dashboard callers still receive
`{"status": "Artifact not available"}` on an active failure, while the full
exception is written to server logs.

## Root Cause

Streamlit was launched with:

```text
C:\Users\Hhari\OneDrive\Documents\KRONOS\venv\Scripts\python.exe
```

That environment did not contain the declared `duckdb` dependency. The exact
runtime exception was:

```text
ModuleNotFoundError("No module named 'duckdb'")
```

The failing statement was the lazy import inside
`_load_warehouse_evidence_cached()`:

```python
import duckdb
```

The public adapter intentionally caught the exception and returned the safe
fallback. That preserved dashboard availability but hid the dependency
mismatch from the UI.

The original cached fallback behavior was a secondary resilience and
observability defect: transient failures could be retained for the cache TTL.
Cached worker functions now raise failures, while the uncached public boundary
logs the traceback and returns the safe fallback.

## Why Tests Missed It

Earlier tests ran with the system interpreter:

```text
C:\Users\Hhari\AppData\Local\Programs\Python\Python311\python.exe
```

That interpreter already had DuckDB 1.4.3 installed. Those tests validated the
code and artifacts, but not dependency parity with the actual Streamlit
runtime.

## Repository Evidence

### Paths

```text
ROOT_DIR:
C:\Users\Hhari\OneDrive\Documents\KRONOS

WAREHOUSE_DB:
C:\Users\Hhari\OneDrive\Documents\KRONOS\data\warehouse\kronos_risk.duckdb

ANALYTICS_ROOT:
C:\Users\Hhari\OneDrive\Documents\KRONOS\analytics\sas_style_runs

MODULE_FILE:
C:\Users\Hhari\OneDrive\Documents\KRONOS\app\enterprise_visibility.py
```

The warehouse exists and is opened with `read_only=True`.

The latest Phase 4C run is:

```text
analytics/sas_style_runs/20260619T175318Z_da9ba40a
```

The following files exist and parse successfully:

- `manifest.json`
- `hash_inventory.json`
- `institutional_report_pack.md`

### Phase 4B Schema

The queried fields exist in the current warehouse:

- `publish.transition_at`
- `publish.published_at`
- `batch.duration_seconds`
- `batch.records_processed`
- `batch.records_loaded`
- `batch.records_rejected`
- `batch.source_count`
- `batch.artifact_count`
- `batch.warehouse_status`

Phase 4E queries `control.reconciliation_result` directly. It does not
reference `control.vw_latest_reconciliation`.

### Phase 4D Views

All required read-only queries succeeded:

- `mart.vw_enterprise_risk_summary_current`: 1 row
- `mart.vw_portfolio_quality_current`: 1 row
- `mart.vw_model_governance_current`: 3 rows
- `mart.vw_concentration_risk_current`: 27 rows

## Corrective Action

1. Installed DuckDB 1.4.3 into the repository Streamlit venv, matching the
   existing `requirements.txt` declaration.
2. Kept exception handling outside the cached warehouse and analytics workers.
3. Cached functions raise failures; public adapter functions log them and
   return the required safe fallback.
4. Preserved the 300-second cache, resource-signature cache keys, and `.clear()`
   compatibility.
5. Removed all temporary print instrumentation after verification.

No dashboard layout or business logic was changed. No ETL, analytics, mart,
model, scoring, or warehouse process was executed.

## Files Modified

- `app/enterprise_visibility.py`
- `tests/test_phase4e_visibility.py`

## File Created

- `docs/PHASE4E_BUG_ROOT_CAUSE.md`

## Verification Evidence

### Adapter Results

```text
warehouse_status=AVAILABLE
schema_count=5
table_count=58
view_count=10
source_asset_count=38
artifact_count=53
published_batch_id=79239c0ed5c14df793050725552e2f5c
dq_score=100.0
dq_status=PASS
reconciliation_status=PASS
model_governance_rows=3
concentration_rows=27

analytics_status=AVAILABLE
analytics_run_id=20260619T175318Z_da9ba40a
output_count=78
hash_inventory_count=78
```

### Tests

```text
tests/test_phase4e_visibility.py
9 passed

tests/test_phase4e_dashboard_render.py
3 passed
```

Instrumented Streamlit testing under the repository venv confirmed:

- `EXECUTIVE_PHASE4E_DATA.status=AVAILABLE`
- `EXPLAINABILITY_PHASE4E_DATA.status=AVAILABLE`
- `REPORTS_PHASE4E_DATA.warehouse.status=AVAILABLE`
- `REPORTS_PHASE4E_DATA.sas_analytics.status=AVAILABLE`
- All three dashboard render tests completed without an exception.

The Executive dashboard was also confirmed in a live Streamlit browser render
after installing DuckDB in the venv. AppTest render evidence covers all three
dashboards.

## Immutability Verification

Warehouse SHA-256 before the change:

```text
0b0529f947d81fddc049873bf40ab8360fc595314ea21f0c883f10e7f5ae4ca5
```

The following remained unchanged:

- warehouse schemas, tables, and views
- `app/main.py`
- `src/enterprise_data/`
- models
- processed datasets
- outputs
- reports
- SQL assets
- scoring logic
- ETL logic
- SAS-style analytics logic
- Phase 4D mart logic

No ETL, analytics runner, mart deployment, model, or scoring process was
executed.
