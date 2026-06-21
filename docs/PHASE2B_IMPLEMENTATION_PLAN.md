# KRONOS Phase 2B Implementation Plan

## 1. Phase Objective

Phase 2B extends the isolated temporal platform with governed historical
ingestion only.

It will accept source-supplied historical snapshots, preserve their temporal
provenance, load validated rows into historical dimensions and facts, and
publish data-readiness evidence for future phases.

Phase 2B must not implement:

- migration matrices,
- roll rates,
- vintage analytics,
- true OOT validation,
- IFRS9 calculations,
- dashboard or application integration,
- current warehouse integration,
- Phase 4 ETL, analytics, marts, lineage, or visibility integration.

## 2. Architectural Boundary

Phase 2B may:

- extend `kronos_temporal_risk.duckdb`,
- register observed and simulated historical-source contracts,
- ingest source-supplied snapshot rows,
- normalize source fields into a governed canonical schema,
- store source-supplied credit events,
- execute DQ and reconciliation,
- evaluate data readiness,
- persist independent historical lineage,
- publish the isolated temporal database.

Phase 2B may not:

- generate historical rows,
- generate dates or business identifiers,
- execute models or scoring,
- derive migrations, cohorts, vintages, roll rates, ECL, or OOT metrics,
- create views or marts,
- activate any analytical capability.

Any scope violation must return:

```text
PHASE2B_SCOPE_VIOLATION
```

## 3. Existing Platform Preservation

Phase 2B builds on:

```text
temporal_platform/warehouse/kronos_temporal_risk.duckdb
```

Before deployment, capture:

- temporal database SHA-256,
- current 5-schema/17-table/0-view catalog,
- all Phase 2A table schemas and row counts,
- current KRONOS warehouse SHA-256 and catalog,
- scored-portfolio SHA-256 and profile,
- protected repository SHA-256 inventory,
- controlled Phase 2A and Phase 2B specification hashes.

Phase 2B must preserve all existing Phase 2A rows. No Phase 2A table may be
dropped, replaced, truncated, or redefined.

## 4. Runtime Architecture

Use only:

```text
temporal_platform/
├── warehouse/
│   └── kronos_temporal_risk.duckdb
├── backups/
├── inbound/
│   ├── observed/
│   └── simulated/
└── evidence/
    └── phase2b/
        └── <ingestion_batch_id>/
```

Inbound files remain immutable. Reject handling records metadata and rejected
rows without modifying or moving source files.

No Phase 2B runtime asset may be written under `data/`, `outputs/`, `reports/`,
`analytics/`, or `models/`.

## 5. Proposed Authored Files

Create:

```text
src/temporal_risk/historical_ingestion/
├── __init__.py
├── config.py
├── contracts.py
├── manifest.py
├── source_discovery.py
├── schema_mapping.py
├── extractor.py
├── normalizer.py
├── data_quality.py
├── readiness.py
├── reconciliation.py
├── lineage.py
├── loader.py
├── publisher.py
└── pipeline.py
```

Create SQL assets:

```text
sql/phase2b/ddl/
├── 001_reference_extensions.sql
├── 002_control_tables.sql
├── 003_staging_tables.sql
├── 004_core_dimensions.sql
└── 005_core_facts.sql
```

Create tests:

```text
tests/test_phase2b_contracts.py
tests/test_phase2b_manifest.py
tests/test_phase2b_connection_safety.py
tests/test_phase2b_schema.py
tests/test_phase2b_observed_ingestion.py
tests/test_phase2b_simulated_ingestion.py
tests/test_phase2b_data_quality.py
tests/test_phase2b_readiness.py
tests/test_phase2b_reconciliation.py
tests/test_phase2b_lineage.py
tests/test_phase2b_idempotency.py
tests/test_phase2b_conflict_handling.py
tests/test_phase2b_rollback.py
tests/test_phase2b_compatibility.py
tests/test_phase2b_scope_boundary.py
```

Create documentation:

```text
docs/PHASE2B_COMPLETION_REPORT.md
docs/HISTORICAL_INGESTION_ARCHITECTURE.md
docs/HISTORICAL_SOURCE_CONTRACT.md
docs/HISTORICAL_DATA_DICTIONARY.md
docs/HISTORICAL_INGESTION_OPERATIONS.md
```

No dashboard, application, Phase 4, model, scoring, reporting, or analytics
file may be modified.

## 6. Package Responsibilities

| Module | Responsibility |
|---|---|
| `config.py` | Phase 2B paths, DDL inventory, formats, statuses |
| `contracts.py` | Observed/simulated contracts and prohibited capabilities |
| `manifest.py` | Parse and validate immutable JSON sidecar manifests |
| `source_discovery.py` | Allowlisted inbound-file discovery and path safety |
| `schema_mapping.py` | Explicit source-to-canonical field mapping |
| `extractor.py` | Read CSV or Parquet without modifying the source |
| `normalizer.py` | Type normalization without business inference |
| `data_quality.py` | Manifest, identity, temporal, schema, and value controls |
| `readiness.py` | Data-readiness evidence with activation permanently disabled |
| `reconciliation.py` | Source/staging/core/reject parity |
| `lineage.py` | Independent Phase 2B source-to-fact lineage |
| `loader.py` | Idempotent staging, dimension, fact, event, and reject loading |
| `publisher.py` | Working-copy publication using Phase 2A connection safeguards |
| `pipeline.py` | Schema deployment and safe historical-ingestion orchestration |

Phase 2B may import Phase 2A connection, hashing, and file-publication helpers.
Phase 2A must never import Phase 2B.

## 7. Safe Entry Points

Provide:

```text
deploy_phase2b_schema()
deploy_phase2b_schema_safe()
run_historical_ingestion()
run_historical_ingestion_safe()
```

Governed statuses:

- `PHASE2B_SCHEMA_READY`
- `PHASE2B_INGESTION_SUCCESS`
- `PHASE2B_SCOPE_VIOLATION`
- `PHASE2B_UNAVAILABLE`
- `HISTORICAL_SOURCE_NOT_READY`
- `HISTORICAL_CONTRACT_VIOLATION`
- `SNAPSHOT_VERSION_CONFLICT`
- `PHASE2B_BASELINE_MISMATCH`

No exception may propagate into KRONOS or Phase 2A callers.

## 8. Source Manifest Contract

Every inbound data file requires an immutable JSON sidecar manifest.

Required manifest fields:

```text
manifest_version
contract_name
contract_version
history_mode
evidence_classification
source_system
source_file
source_file_sha256
source_format
identity_grain
entity_id_column
facility_id_column
observation_date_column
reporting_date_column
declared_snapshot_date
source_date_provenance
field_mapping
source_run_id_column
model_version_column
created_at
```

At least one of `observation_date_column` or `reporting_date_column` must be
source supplied.

Paths must be repository-relative and resolve under:

- `temporal_platform/inbound/observed/`, or
- `temporal_platform/inbound/simulated/`.

Absolute paths, parent traversal, remote URLs, and paths into current KRONOS
data directories are prohibited.

## 9. Observed Snapshot Contract

Contract:

```text
OBSERVED_HISTORICAL_SNAPSHOT_V1
```

Required:

- `history_mode = OBSERVED_TEMPORAL`
- `evidence_classification = OBSERVED_SOURCE`
- stable source-supplied entity identifier,
- source-supplied observation or reporting date,
- source-field date provenance,
- one declared snapshot date per file,
- source hash and schema hash,
- no simulation metadata.

Observed dates may not be derived from:

- file modification time,
- ingestion time,
- process timestamp,
- row order,
- current date,
- generated vintages.

An observed snapshot becomes historically data-eligible only after all
critical identity and temporal gates pass.

## 10. Simulated Snapshot Contract

Contract:

```text
SIMULATED_HISTORICAL_SNAPSHOT_V1
```

Required:

- `history_mode = SIMULATED_TEMPORAL`
- `evidence_classification = SIMULATED_SOURCE`
- stable source-supplied entity identifier,
- explicit simulated observation or reporting date,
- simulation method,
- simulation version,
- simulation producer,
- simulation seed when randomness was used.

Phase 2B does not generate simulated data. It only ingests an already-created,
explicitly labelled simulated source.

Simulated snapshots are never eligible for:

- genuine historical claims,
- true OOT,
- regulatory IFRS9,
- observed migration or cure claims.

They may be marked data-ready for a future demonstration phase, but every
analytical activation remains disabled.

## 11. Database Extension

Retain the existing five schemas:

- `control`
- `staging`
- `reference`
- `core`
- `mart`

Do not create a new schema.

Create nineteen additive base tables:

### Reference

1. `reference.dim_identity_grain`
2. `reference.dim_readiness_status`

### Control

3. `control.historical_ingestion_batch`
4. `control.historical_ingestion_file`
5. `control.historical_field_mapping`
6. `control.historical_reject_record`
7. `control.data_readiness_result`
8. `control.historical_reconciliation_result`
9. `control.historical_lineage_node`
10. `control.historical_lineage_edge`
11. `control.historical_column_lineage`
12. `control.historical_publish_status`

### Staging

13. `staging.stg_historical_snapshot_row`
14. `staging.stg_historical_event_row`

### Core Dimensions

15. `core.dim_historical_entity`
16. `core.dim_historical_facility`
17. `core.dim_historical_snapshot`

### Core Facts

18. `core.fact_historical_credit_observation`
19. `core.fact_historical_credit_event`

Post-deployment catalog:

```text
Schemas: 5
Tables: 36
Views: 0
Mart objects: 0
```

## 12. Reference Data

### `reference.dim_identity_grain`

Rows:

- `BORROWER`
- `FACILITY`

Facility grain requires a stable source-supplied facility identifier. No
facility proxy may be generated.

### `reference.dim_readiness_status`

Rows:

- `NOT_ASSESSED`
- `READY_BUT_DISABLED`
- `NOT_READY`
- `NOT_ELIGIBLE`
- `FAILED`

`READY_BUT_DISABLED` confirms data availability only. It never activates an
analytical capability.

## 13. Control Structures

### `control.historical_ingestion_batch`

Store:

- ingestion batch ID,
- source and manifest IDs,
- contract ID/version,
- history mode,
- start/end timestamps,
- lifecycle status,
- records read, staged, accepted, rejected, inserted, skipped,
- snapshot count,
- source, working-database, and published-database hashes,
- error class and message.

### `control.historical_ingestion_file`

Store:

- ingestion file ID,
- ingestion batch ID,
- source and manifest asset IDs,
- relative paths and formats,
- source and schema hashes,
- row and column counts,
- declared and observed snapshot dates,
- file status and timestamps.

### `control.historical_field_mapping`

Store one record per declared mapping:

- source column,
- canonical column,
- mapping type,
- required flag,
- source-supplied flag,
- allowed cast,
- transformation description.

No mapping may generate an identifier, date, default event, cure event, or
recovery event.

### `control.historical_reject_record`

Store rejected-row metadata and immutable source payload:

- batch, snapshot, source asset, source row,
- raw entity/facility identifier,
- column, invalid value,
- severity, rejection reason,
- payload JSON and rejection timestamp.

### `control.data_readiness_result`

Store one result for each capability:

- `HISTORICAL_STORAGE`
- `MIGRATION_INPUTS`
- `ROLL_RATE_INPUTS`
- `VINTAGE_INPUTS`
- `TRUE_OOT_INPUTS`
- `IFRS9_TEMPORAL_INPUTS`

Store:

- data status,
- activation status,
- required, available, and missing fields,
- history mode,
- evidence classification,
- reason and evaluation timestamp.

Activation status must always be:

```text
DISABLED_PENDING_FUTURE_PHASE
```

### `control.historical_reconciliation_result`

Store source, staging, core, reject, event, and aggregate parity evidence.

### Phase 2B Lineage Tables

Use dedicated Phase 2B lineage tables. Do not add records to the Phase 2A
5/4/4 lineage tables.

### `control.historical_publish_status`

Lifecycle:

```text
DRAFT -> VALIDATED -> PUBLISHED
```

Only batches passing the historical-storage gate may be published.

## 14. Historical Staging Design

### `staging.stg_historical_snapshot_row`

Grain:

```text
one source row per ingestion batch and snapshot
```

Canonical fields:

- source row number,
- ingestion batch and snapshot IDs,
- history mode and evidence classification,
- source entity and optional facility IDs,
- observation and reporting dates,
- origination, default, cure, recovery, and maturity dates when source supplied,
- source run and model version,
- PD, LGD, EAD, credit score,
- risk band, risk grade, IFRS9 stage,
- watchlist, delinquency, utilization, decision, and default outcome fields,
- DQ status,
- raw source payload JSON,
- loaded timestamp.

The table may contain rejected rows for complete source-to-staging parity.

### `staging.stg_historical_event_row`

Store only explicitly source-supplied events:

- `ORIGINATION`
- `DEFAULT`
- `CURE`
- `RECOVERY`
- `MATURITY`
- `CLOSURE`

No event may be inferred from score movement, stage movement, delinquency, or
model output.

## 15. Core Dimension Design

### `core.dim_historical_entity`

Technical key:

```text
SHA-256(source_system | identity_grain | source_entity_id)
```

Store the original source entity ID. The hash is a warehouse key, not a
fabricated business identifier.

### `core.dim_historical_facility`

Create a row only when a stable source facility ID is present.

Technical key:

```text
SHA-256(source_system | source_facility_id)
```

Do not use borrower IDs as facility proxies.

### `core.dim_historical_snapshot`

Store:

- snapshot and source-asset IDs,
- contract and batch IDs,
- snapshot date and date type,
- history mode and evidence classification,
- identity grain and continuity status,
- source run/model inventories,
- source and schema hashes,
- temporal quality and storage readiness,
- load timestamp.

## 16. Core Fact Design

### `core.fact_historical_credit_observation`

Grain:

```text
one accepted entity/facility observation per snapshot
```

Observation ID:

```text
SHA-256(snapshot_id | entity_key | facility_key-or-null)
```

Store only normalized source values. No score, stage, risk band, default,
delinquency, or loss value may be recalculated.

### `core.fact_historical_credit_event`

Grain:

```text
one explicitly source-supplied event per entity/facility and event date
```

Store event type, event date, source column, source row, provenance, and
optional source event value.

No event analytics are permitted.

## 17. Mandatory DQ Framework

Run a fixed core set of 36 controls per source snapshot. Optional field checks
must return `NOT_APPLICABLE`, preserving the control inventory.

### Manifest and Source

1. Manifest exists.
2. Manifest JSON is valid.
3. Contract name and version are supported.
4. Source exists and is a regular file.
5. Source path is allowlisted.
6. Manifest hash matches source hash.
7. Source hash remains stable during ingestion.
8. Canonical schema hash is reproducible.

### Mode and Classification

9. History mode is allowed.
10. Evidence classification matches history mode.
11. Observed source contains no simulation metadata.
12. Simulated source contains required simulation metadata.

### Identity

13. Entity ID field is declared.
14. Entity ID field exists.
15. Entity IDs are non-null.
16. Entity IDs are source supplied.
17. Identity grain is allowed.
18. Facility ID is present when facility grain is declared.

### Temporal Integrity

19. Observation or reporting date field is declared.
20. Declared date field exists.
21. Dates are parseable.
22. Dates are source supplied.
23. Dates do not use file or process timestamps as fallback.
24. One snapshot date exists per file.
25. Observed dates are not future-dated.
26. Source date provenance is complete.

### Grain and Duplication

27. Entity/facility grain is unique within the snapshot.
28. Snapshot identity does not duplicate a published snapshot.
29. Different hash for the same governed snapshot date is rejected as a conflict.

### Optional Credit Fields

30. PD is in `[0,1]` when present.
31. LGD is in `[0,1]` when present.
32. EAD is non-negative when present.
33. IFRS9 stage is within the declared domain when present.
34. Risk band and grade are within declared domains when present.
35. Source run/model inventories are captured without cardinality assumptions.
36. No generated business identifier, date, or event is introduced.

Any critical failure blocks publication. Row-level failures may be rejected only
when the remaining accepted population still satisfies the snapshot contract.

## 18. Data-Readiness Gates

Phase 2B evaluates readiness but activates nothing.

### Historical Storage

Required for ingestion publication:

- valid contract,
- immutable source hash,
- source-supplied entity ID,
- source-supplied observation/reporting date,
- unique snapshot grain,
- successful critical DQ controls,
- complete reconciliation.

### Migration Inputs

`READY_BUT_DISABLED` requires observed history, at least two source snapshots,
stable identity continuity, and a supported state field.

No transition matrix is generated.

### Roll-Rate Inputs

`READY_BUT_DISABLED` requires observed facility identity, consecutive dates,
and source-supplied delinquency state.

No roll rate is generated.

### Vintage Inputs

`READY_BUT_DISABLED` requires observed source-supplied origination date and
sufficient observation depth.

No vintage cohort or curve is generated.

### True OOT Inputs

`READY_BUT_DISABLED` requires observed feature dates, mature source outcomes,
model version, model freeze metadata, and point-in-time feature availability.

Simulated sources are `NOT_ELIGIBLE`.

No model is trained, scored, or validated.

### IFRS9 Temporal Inputs

Readiness requires source-supplied reporting, origination, maturity, EIR,
contractual cash-flow, default, cure, recovery, and scenario information.

Until the complete contract is available, status remains `NOT_READY`.
Simulated sources remain unsuitable for regulatory claims.

No staging or ECL calculation is executed.

## 19. Reconciliation Framework

Create twelve reconciliation results per source snapshot:

1. Source rows equal staging rows.
2. Staging rows equal accepted plus rejected rows.
3. Accepted rows equal observation-fact rows inserted or idempotently skipped.
4. Accepted distinct entities equal linked entity-dimension population.
5. Accepted distinct facilities equal linked facility-dimension population.
6. One source snapshot equals one snapshot-dimension row.
7. Source hash equals registered source hash.
8. Source schema hash equals registered schema hash.
9. Declared snapshot date equals persisted snapshot date.
10. Source event count equals staged event count.
11. Staged accepted event count equals event-fact count.
12. Optional EAD/default aggregate parity passes or is `NOT_APPLICABLE`.

No analytical aggregation may be persisted.

## 20. Lineage Framework

Phase 2B lineage must independently connect:

- manifest file,
- historical source file,
- temporal contract,
- field-mapping set,
- staging snapshot rows,
- staging event rows,
- entity dimension,
- facility dimension when applicable,
- snapshot dimension,
- observation fact,
- event fact when applicable,
- readiness evidence,
- rejects when applicable,
- published ingestion batch.

Column lineage must exist for every canonical mapped field.

Transformations are limited to:

- identity warehouse-key hashing,
- explicit rename,
- safe datatype cast,
- null preservation,
- source event normalization.

Do not write to Phase 1, Phase 4, SAS-style analytics, risk-mart, or Phase 2A
lineage tables.

## 21. Idempotency and Conflict Policy

Identical:

```text
source hash + manifest hash + contract version + snapshot identity
```

must return `SKIPPED_ALREADY_PUBLISHED` without adding staging, dimension,
fact, readiness, reconciliation, or lineage duplicates.

The same governed snapshot identity with a different source hash must return:

```text
SNAPSHOT_VERSION_CONFLICT
```

Phase 2B does not overwrite or supersede published snapshots. Corrections
require a separately approved governance design.

## 22. Deployment Workflow

1. Validate Phase 2A acceptance status.
2. Validate Phase 2B controlled specifications.
3. Capture temporal database and protected baselines.
4. Validate scope and runtime paths before writes.
5. Copy the temporal database to a temporary working location.
6. Apply only the five Phase 2B DDL assets.
7. Validate the 5-schema/36-table/0-view catalog.
8. Verify every Phase 2A table and row remains intact.
9. Register the Phase 2B release using the existing release framework.
10. Publish the closed working database.
11. Reopen read-only and verify hashes and catalog.
12. Confirm the current KRONOS warehouse and protected files are unchanged.

Schema deployment must not ingest any data automatically.

## 23. Historical Ingestion Workflow

1. Validate manifest and inbound paths before writes.
2. Capture manifest and source hashes.
3. Select observed or simulated contract.
4. Verify explicit field mappings.
5. Copy the temporal database to a working database.
6. Register source and manifest metadata.
7. Load source rows to historical staging.
8. Execute 36 DQ controls.
9. Record rejects without changing the source.
10. Load accepted entity, facility, snapshot, observation, and event records.
11. Evaluate six readiness capabilities.
12. Execute twelve reconciliations.
13. Build independent Phase 2B lineage.
14. Validate storage readiness and idempotency.
15. Record `DRAFT`, `VALIDATED`, and `PUBLISHED`.
16. Publish the verified working database.
17. Write deployment-specific evidence under `evidence/phase2b/`.

## 24. Expected Row-Count Contracts

### Schema Deployment Without Inbound Sources

| Object | Expected Change |
|---|---:|
| `dim_identity_grain` | +2 |
| `dim_readiness_status` | +5 |
| Other new Phase 2B tables | 0 |
| Historical observations | 0 |
| Historical events | 0 |
| Mart objects | 0 |

### Successful Snapshot With `N` Source Rows

Let:

- `R` = rejected rows,
- `A = N - R` = accepted rows,
- `E` = distinct accepted entities,
- `F` = distinct accepted non-null facilities,
- `V` = source-supplied events,
- `M` = declared field mappings.

Expected:

| Object | Rows Added |
|---|---:|
| Ingestion batch | 1 |
| Ingestion file | 1 |
| Field mappings | `M` |
| Staging snapshot rows | `N` |
| Reject records | `R` |
| Entity dimensions | New members up to `E` |
| Facility dimensions | New members up to `F` |
| Snapshot dimensions | 1 |
| Observation facts | `A` |
| Staging event rows | `V` |
| Event facts | Accepted events up to `V` |
| Readiness results | 6 |
| Reconciliations | 12 |
| Publish transitions | 3 |

All counts are source-driven. No current 50,000-row assumption applies.

## 25. Compatibility Requirements

Verify:

- Phase 1 and Phase 1.5 files and artifacts unchanged.
- Phase 4A–4E files, database, controls, marts, analytics, and outputs unchanged.
- Current `scored_portfolio.csv` unchanged.
- Current models unchanged.
- No `app/` import references Phase 2B.
- No `src/enterprise_data/` import references Phase 2B.
- No Phase 2B import executes application or Phase 4 code.
- Phase 2A business rows remain unchanged.
- Phase 2A tests continue to pass on a clean Phase 2A database.
- Phase 2B does not create views or mart objects.

After Phase 2B installation, rerunning Phase 2A against the upgraded production
temporal database must be blocked with:

```text
PHASE2A_UPGRADE_PRESENT
```

Phase 2A remains testable and deployable to a fresh temporary Phase 2A
database.

## 26. Testing Strategy

Tests must cover:

- exact 5/36/0 catalog,
- preservation of all Phase 2A objects,
- observed-contract validation,
- simulated-contract validation,
- manifest and path traversal rejection,
- source-hash stability,
- source-supplied date provenance,
- no generated identities or dates,
- borrower and facility grain,
- optional-field normalization,
- 36 DQ controls,
- row-level reject handling,
- storage-readiness publication gate,
- six readiness records with disabled activation,
- twelve reconciliations,
- complete source-to-fact lineage,
- identical-source idempotency,
- conflicting snapshot rejection,
- schema deployment without ingestion,
- file-level rollback,
- safe failure without evidence mutation,
- current warehouse and protected-hash compatibility,
- absence of analytical, dashboard, application, and Phase 4 dependencies.

## 27. Rollback

Before Phase 2B schema deployment or ingestion:

1. Close all temporal connections.
2. Create and verify a Phase 2A database backup.
3. Store backup hash and pre-deployment catalog.
4. Publish only from a closed working database.

Rollback restores the verified pre-Phase 2B database file. It must not execute
drop statements against the published database.

Complete Phase 2B removal requires:

- restoring the pre-Phase 2B temporal database backup,
- deleting `src/temporal_risk/historical_ingestion/`,
- deleting `sql/phase2b/`,
- deleting Phase 2B tests and documentation,
- deleting Phase 2B inbound and evidence directories.

Phase 2A and all existing KRONOS functionality must remain operational.

## 28. Implementation Sequence

### Phase 2B.1

Deploy additive schema and reference data only.

### Phase 2B.2

Implement manifests, contracts, source discovery, and schema mapping.

### Phase 2B.3

Implement staging, DQ, rejects, and readiness gates.

### Phase 2B.4

Implement dimensions, facts, events, reconciliation, and lineage.

### Phase 2B.5

Implement idempotency, publication, rollback, protected-hash verification, and
completion reporting.

No later analytical phase may be included in any Phase 2B increment.

## 29. Definition of Completion

Phase 2B is complete only when:

- the isolated database contains five schemas, 36 tables, and zero views,
- the mart schema remains empty,
- all existing Phase 2A rows are preserved,
- observed and simulated contracts are independently enforced,
- no source is ingested without a source-supplied temporal field,
- no identifier, date, or event is fabricated,
- schema deployment performs no automatic ingestion,
- historical storage succeeds only through the readiness gate,
- all analytical capabilities remain disabled,
- DQ, rejection, reconciliation, lineage, and idempotency tests pass,
- current KRONOS warehouse and protected hashes remain unchanged,
- rollback restores the verified Phase 2A database,
- no migration, roll-rate, vintage, true OOT, IFRS9, dashboard, application,
  Phase 4, or SAS-style analytical functionality exists.
