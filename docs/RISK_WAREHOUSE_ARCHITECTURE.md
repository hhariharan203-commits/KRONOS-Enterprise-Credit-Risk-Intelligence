# KRONOS Enterprise Risk Warehouse Architecture

## Purpose

Phase 4A provides a governed analytical mirror of existing KRONOS artifacts. It preserves all current CSV workflows and does not change scoring, dashboards, models, risk engines, validation, or reporting.

## Architecture

```mermaid
flowchart LR
    A["Existing CSV and JSON Sources"] --> B["Source Registry"]
    C["PKL, PDF, PNG, MD and TXT Artifacts"] --> D["Hash-Only Artifact Registry"]
    B --> E["Staging Schema"]
    E --> F["Quality and Reconciliation"]
    F --> G["Core Warehouse"]
    G --> H["Credit Risk Mart"]
    G --> I["IFRS9 Stage Mart"]
    G --> J["EWS Mart"]
    G --> K["Model Risk Mart"]
    G --> L["Executive Mart"]
    B --> M["Column Lineage"]
    E --> M
    G --> M
    H --> M
    I --> M
    J --> M
    K --> M
    L --> M

    N["app/main.py"] --> O["scored_portfolio.csv"]
    O --> P["Existing Dashboards and Reports"]
    O -. "read-only mirror" .-> B
```

## Technology

- Database: DuckDB 1.4.3
- Database path: `data/warehouse/kronos_risk.duckdb`
- SQL schemas: `control`, `staging`, `reference`, `core`, `mart`
- Source-of-truth policy: existing CSV artifacts

## Isolation

No existing application module imports `src.enterprise_data`. Warehouse failure therefore cannot interrupt application startup.

The database is built in a local temporary directory and copied to the synchronized workspace only after the connection closes. This prevents DuckDB WAL checkpoint failures caused by workspace child-file deletion restrictions.

## Data Layers

### Control

Tracks:

- ETL batches and steps
- Source files and hashes
- Artifact metadata
- Source schemas
- Quality checks
- Reconciliations
- Rejected records
- Lineage nodes, edges, and columns

### Staging

CSV tables mirror source values and add only:

- `etl_batch_id`
- `source_asset_id`
- `source_sha256`
- `loaded_at`

JSON artifacts are preserved as JSON payload text with their source hash.

### Core

The core credit fact is append-only and keyed by source hash, borrower, run, and model version. Repeated identical files do not create duplicate business facts.

The facility dimension does not contain a fabricated account ID. It uses a technical warehouse key derived directly from the current borrower row, stores `source_account_id` as null, and sets `account_proxy_flag` to true.

### Marts

Phase 4A marts expose current persisted information only. They do not execute IFRS9, EWS, stress, contagion, or decision engines and do not claim to contain their transient runtime outputs.

## Model-Version Integrity

The scored portfolio contains model version `51a7373f45ff8b6f`. The active model artifacts currently produce a different composite hash. The warehouse records:

```text
UNRESOLVED_CURRENT_ARTIFACTS_DIFFER
```

No false association is created between the historical scoring run and current model files.

## Temporal Integrity

The only borrower-level timestamp is scoring execution time. It is not an observation, reporting, origination, default, or vintage date.

Historical migrations, roll rates, and vintage analysis remain unavailable until genuine repeated observations and source dates exist.

## Phase 4B ETL Control Plane

Phase 4B adds a DataStage-style operational control plane without changing the
Phase 4A physical warehouse design.

```mermaid
flowchart LR
    S["Existing KRONOS source files"] --> J1["SOURCE_LOAD verification"]
    J1 --> J2["VALIDATION"]
    J2 --> J3["STAGING_LOAD verification"]
    J3 --> J4["CORE_LOAD verification"]
    J4 --> J5["MART_BUILD verification"]
    J5 --> J6["RECONCILIATION"]
    J6 --> J7["PUBLISH control"]
    J7 --> J8["LINEAGE capture"]

    J1 --> C["control schema"]
    J2 --> C
    J3 --> C
    J4 --> C
    J5 --> C
    J6 --> C
    J7 --> C
    J8 --> C
```

The Phase 4B jobs do not reload source rows, rebuild core tables, or recreate
marts. They validate that the existing read-only mirror matches its registered
source hashes and row-count contracts.

Operational services are implemented under `src/enterprise_data/etl/`:

- batch and job control,
- dependency validation and topological execution,
- enterprise data-quality rules,
- reject metadata logging,
- publish lifecycle controls,
- operational metrics,
- restart-safe recovery,
- job and batch lineage.

Downstream jobs are marked `BLOCKED` when an upstream dependency fails. A
recovery creates a new linked batch, skips previously successful jobs, and
resumes the failed and downstream steps without duplicating warehouse facts.
