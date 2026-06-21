# KRONOS Risk Warehouse Operations

## Build

```powershell
python -m src.enterprise_data.pipeline
```

The command prints a JSON summary containing:

- pipeline status,
- source and artifact counts,
- inserted/skipped rows,
- quality and reconciliation failures,
- lineage completeness,
- mart row counts.

## Safe Execution

For non-blocking integration:

```python
from src.enterprise_data import run_phase4a_pipeline_safe

result = run_phase4a_pipeline_safe()
```

Failures return `WAREHOUSE_UNAVAILABLE`; they do not affect existing KRONOS CSV workflows.

## Idempotency

Each source asset is identified by:

```text
relative path + SHA-256
```

Credit facts use:

```text
source asset + borrower + scoring run + model version
```

An unchanged repeat run:

- skips all 18 CSV sources,
- inserts no new borrower/facility/credit facts,
- preserves existing marts,
- adds a new operational audit batch and quality/reconciliation history.

## Verification

```powershell
python -m pytest -q tests/test_warehouse_schema.py `
    tests/test_warehouse_loads.py `
    tests/test_warehouse_idempotency.py `
    tests/test_warehouse_reconciliation.py `
    tests/test_warehouse_lineage.py `
    tests/test_warehouse_artifact_registry.py
```

## Read-Only Query

```python
from src.enterprise_data.connection import connect_warehouse

connection = connect_warehouse(read_only=True)
summary = connection.execute(
    "SELECT * FROM mart.mart_executive_current"
).fetchdf()
connection.close()
```

## Operational Controls

- Treat CSV artifacts as authoritative.
- Never write model, raw, processed, output, or report source files.
- Review `control.etl_batch` for failures or abandoned runs.
- Require all reconciliation results to pass before using marts.
- Treat temporal quality as process time only.
- Do not interpret technical facility keys as bank account IDs.

## Rollback

1. Stop running `src.enterprise_data.pipeline`.
2. Remove the generated database and zero-length WAL file if filesystem policy permits.
3. Remove `src/enterprise_data`, `sql`, and warehouse tests.
4. Revert documentation, requirements and ignore-file additions.
5. Run the original tests and dashboards.

No retraining, rescoring, data restoration, or report regeneration is required.

## Phase 4B Control Run

Execute the ETL control framework after the Phase 4A warehouse mirror is
current:

```powershell
python -m src.enterprise_data.etl.scheduler
```

The Phase 4B scheduler verifies the existing mirror. It does not reload data or
rebuild marts.

For non-blocking integration:

```python
from src.enterprise_data import run_phase4b_etl_safe

result = run_phase4b_etl_safe()
```

Failures return `ETL_UNAVAILABLE` and do not affect application startup.

## Phase 4B Dependency Flow

```text
REGISTER_SOURCES
  -> VALIDATE_QUALITY
  -> VERIFY_STAGING
  -> VERIFY_CORE
  -> VERIFY_MARTS
  -> RECONCILE_COUNTS
  -> PUBLISH_WAREHOUSE
  -> CAPTURE_LINEAGE
```

An upstream failure blocks every dependent job. Blocked jobs are retained in
`control.etl_job_run` for auditability.

## Phase 4B Recovery

Resume a failed, partially successful, or abandoned batch:

```python
from src.enterprise_data.etl.recovery import resume_failed_batch

result = resume_failed_batch("<failed_batch_id>")
```

Rerun a failed or blocked step and its downstream dependencies:

```python
from src.enterprise_data.etl.recovery import rerun_failed_step

result = rerun_failed_step("<failed_batch_id>", "VERIFY_CORE")
```

Recovery uses a new linked batch, skips previously successful jobs, and
preserves Phase 4A snapshot idempotency.

## Phase 4B Publish Lifecycle

The control lifecycle is:

```text
DRAFT -> VALIDATED -> PUBLISHED
```

Validation requires:

- no failed Phase 4B quality rule,
- exact reconciliation parity,
- successful upstream dependencies.

`ROLLED_BACK` is a metadata transition only. Phase 4B never changes source,
core, or mart contents during publication.

## Phase 4B Monitoring and Rejects

Operational metrics are stored in `control.operational_metric`:

- job success rate,
- batch success rate,
- average batch duration,
- average records processed,
- average records rejected,
- latest DQ score and status,
- latest publish status,
- warehouse freshness in hours.

Rejected records are metadata-only entries in `control.rejected_record`.
Source files are never corrected or mutated by the ETL framework.
