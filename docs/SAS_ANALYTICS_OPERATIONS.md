# KRONOS SAS-Style Analytics Operations

## Execute

```powershell
python -m src.enterprise_data.sas_analytics.analytics_runner
```

The runner reads the warehouse and writes a versioned run under:

```text
analytics/sas_style_runs/
```

## Safe Execution

```python
from src.enterprise_data.sas_analytics import run_sas_style_analytics_safe

result = run_sas_style_analytics_safe()
```

Failures return:

```text
ANALYTICS_UNAVAILABLE
```

No exception is propagated into KRONOS startup.

## Readiness Controls

Before analysis, the runner requires:

- a successful Phase 4B batch,
- `PUBLISHED` publish status,
- an acceptable DQ status,
- no failed reconciliation for the published batch,
- source and mart row parity,
- one resolved current model version.

The runner queries `control.reconciliation_result` directly. It does not depend
on `control.vw_latest_reconciliation`.

## Read-Only Controls

- Connection mode is always `read_only=True`.
- Warehouse signatures are captured before and after analytics.
- Base-table row counts are captured before and after analytics.
- A detected difference fails the run.
- No object-creation SQL is used.

## Outputs

Each run persists:

- one CSV and one JSON file for every analytical dataset,
- `institutional_report_pack.md`,
- `lineage_manifest.json`,
- `hash_inventory.json`,
- `manifest.json`.

No file is written to `data/`, `outputs/`, `reports/`, or `models/`.

## Temporal Requests

Unsupported historical requests return:

```text
TEMPORAL_HISTORY_NOT_AVAILABLE
```

Example:

```python
from src.enterprise_data.sas_analytics.contracts import (
    temporal_restriction_response,
)

result = temporal_restriction_response("migration analysis")
```

## Verification

```powershell
python -m pytest -q `
    tests/test_sas_analytics_freq.py `
    tests/test_sas_analytics_means.py `
    tests/test_sas_analytics_summary.py `
    tests/test_sas_analytics_tabulate.py `
    tests/test_sas_analytics_rank.py `
    tests/test_sas_analytics_transpose.py `
    tests/test_sas_analytics_runner.py `
    tests/test_sas_analytics_compatibility.py
```

## Rollback

1. Remove `src/enterprise_data/sas_analytics/`.
2. Remove `tests/test_sas_analytics_*.py`.
3. Remove the four Phase 4C documentation files.
4. Remove `analytics/sas_style_runs/`.

No database, model, dashboard, output, report, or source-data restoration is
required.
