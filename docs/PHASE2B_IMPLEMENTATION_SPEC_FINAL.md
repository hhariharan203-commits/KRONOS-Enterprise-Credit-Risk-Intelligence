# KRONOS Phase 2B Final Implementation Specification

## 1. Authority and Status

This document is the controlling implementation specification for:

```text
PHASE 2B — GOVERNED HISTORICAL INGESTION FOUNDATION
```

It incorporates and supersedes conflicting Phase 2B language in:

- `docs/PHASE2B_IMPLEMENTATION_PLAN.md`
- `docs/PHASE2B_PRE_IMPLEMENTATION_AUDIT.md`

The pre-implementation audit classification was:

```text
APPROVED_WITH_CHANGES
```

All mandatory audit corrections are incorporated below. No Phase 2B
implementation may begin unless this specification is treated as
authoritative.

## 2. Objective

Phase 2B extends the isolated Phase 2 temporal platform with governed
historical ingestion architecture.

It may:

- accept source-supplied observed historical snapshots;
- accept externally produced, explicitly labelled simulated snapshots;
- validate immutable source manifests;
- preserve source-supplied temporal provenance;
- stage source rows;
- store validated historical dimensions and facts;
- store explicitly source-supplied events;
- execute data-quality controls;
- execute reconciliations;
- persist independent Phase 2B lineage;
- evaluate future-phase data readiness;
- publish the isolated temporal database through verified file replacement.

Phase 2B is an ingestion and control foundation. It is not an analytical
phase.

## 3. Implementation Boundary

Phase 2B must not implement:

- migration matrices;
- migration analytics;
- risk-band or rating transitions;
- roll rates;
- vintage cohorts or curves;
- cumulative default curves;
- true OOT validation;
- model training, scoring, recalibration, or replacement;
- IFRS9 calculations;
- IFRS9 staging logic;
- contractual cash-flow discounting;
- scenario weighting;
- lifetime ECL;
- provisions or reserves;
- recovery, cure, or default analytics;
- dashboard integration;
- application integration;
- current KRONOS warehouse integration;
- Phase 4 ETL, warehouse, analytics, marts, lineage, or visibility integration;
- SAS-style analytics integration;
- database views;
- marts;
- inferred or generated historical data.

Any attempted scope expansion must stop with:

```text
PHASE2B_SCOPE_VIOLATION
```

## 4. Preserved Platforms

Phase 2B may extend only:

```text
temporal_platform/warehouse/kronos_temporal_risk.duckdb
```

The following remain independent and must not be modified:

- `data/warehouse/kronos_risk.duckdb`
- `data/processed/scored_portfolio.csv`
- `app/`
- `src/enterprise_data/`
- Phase 1 and Phase 1.5 components;
- Phase 4A, 4B, 4C, 4D, and 4E components;
- credit-risk, IFRS9, EWS, stress, contagion, provisioning, decisioning, and
  reporting engines;
- model artifacts;
- current outputs, reports, and analytics artifacts.

Phase 2B failure must never affect KRONOS startup or any existing phase.

## 5. Runtime Architecture

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
        └── <deployment_or_ingestion_id>/
```

Phase 2B must target the exact published database filename:

```text
kronos_temporal_risk.duckdb
```

It must ignore:

- hidden files;
- `.working.duckdb` files;
- `.wal` files;
- rollback temporary files;
- stale Phase 2A working artifacts;
- any DuckDB file not equal to the configured published target.

No Phase 2B runtime file may be written under:

- `data/`
- `models/`
- `outputs/`
- `reports/`
- `analytics/`

Inbound files are immutable. Phase 2B may read and hash them but must not
rename, move, rewrite, truncate, or delete them.

## 6. Final Authored File Inventory

### 6.1 New Runtime Package

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
├── release_registry.py
├── publisher.py
└── pipeline.py
```

`release_registry.py` must contain the dedicated Phase 2B release-registration
implementation. It must not call the Phase 2A `register_release()` function.

### 6.2 SQL Assets

Create:

```text
sql/phase2b/ddl/
├── 001_reference_extensions.sql
├── 002_control_tables.sql
├── 003_staging_tables.sql
├── 004_core_dimensions.sql
└── 005_core_facts.sql
```

No rollback SQL may be created. Rollback is file-based only.

### 6.3 Minimal Existing Phase 2A Modification

Modify only:

```text
src/temporal_risk/pipeline.py
```

The sole permitted purpose is the pre-write
`PHASE2A_UPGRADE_PRESENT` guard defined in Section 8.

The existing exact Phase 2A catalog validator must not be weakened or changed.
No Phase 2A DDL, contract, registry, DQ, reconciliation, lineage, or
publication behavior may be redesigned.

### 6.4 Tests

Create:

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
tests/test_phase2b_release_registry.py
tests/test_phase2b_upgrade_guard.py
tests/test_phase2b_protected_hashes.py
tests/test_phase2b_rollback.py
tests/test_phase2b_compatibility.py
tests/test_phase2b_scope_boundary.py
```

Existing Phase 2A test files may be modified only where necessary to verify
the upgrade guard and preservation of fresh 5/17/0 deployment behavior.

### 6.5 Documentation

Create:

```text
docs/PHASE2B_COMPLETION_REPORT.md
docs/HISTORICAL_INGESTION_ARCHITECTURE.md
docs/HISTORICAL_SOURCE_CONTRACT.md
docs/HISTORICAL_DATA_DICTIONARY.md
docs/HISTORICAL_INGESTION_OPERATIONS.md
```

## 7. Safe Entry Points and Statuses

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
- `PHASE2B_BASELINE_MISMATCH`
- `HISTORICAL_SOURCE_NOT_READY`
- `HISTORICAL_CONTRACT_VIOLATION`
- `SNAPSHOT_VERSION_CONFLICT`
- `SKIPPED_ALREADY_PUBLISHED`

Safe entry points must return a governed result. No exception may propagate
into KRONOS, Phase 2A, application, or Phase 4 callers.

## 8. Mandatory Phase 2A Upgrade Guard

Before Phase 2A creates:

- a deployment ID;
- an evidence directory;
- evidence files;
- a backup;
- a working database;
- a writable connection;

it must inspect the exact published temporal database read-only.

### 8.1 Recognized Phase 2A Catalog

An exact Phase 2A catalog is:

```text
Schemas: 5
Tables: 17
Views: 0
Core objects: 0
Mart objects: 0
```

For this catalog, Phase 2A continues normally and retains its existing exact
validation.

### 8.2 Recognized Phase 2B Catalog

A recognized Phase 2B catalog requires all of the following:

- the same five schemas;
- all original 17 Phase 2A tables;
- all 19 exact Phase 2B tables listed in Section 11;
- 36 total base tables;
- zero views;
- zero mart objects;
- no unexpected object.

For this catalog, Phase 2A must return:

```text
PHASE2A_UPGRADE_PRESENT
```

The return must occur before any evidence or writable artifact is created.

### 8.3 Unknown Catalog

Any catalog other than exact Phase 2A or recognized Phase 2B must retain the
existing Phase 2A validation-failure behavior.

Counts alone are insufficient. A random 5-schema/36-table database must not be
recognized as Phase 2B unless the exact object inventory is present.

### 8.4 Dependency Direction

Phase 2A must not import:

```text
src.temporal_risk.historical_ingestion
```

The guard may use a static recognized-object inventory local to the Phase 2A
preflight. Phase 2B may import approved Phase 2A connection, hashing, and
file-publication helpers. Dependency direction must remain one-way.

## 9. Source Manifest Contracts

Every inbound source requires an immutable JSON sidecar manifest.

Required fields:

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

At least one source-supplied observation or reporting date is mandatory.

Paths must be repository-relative and resolve under the matching allowlisted
inbound directory. Reject:

- absolute paths;
- parent traversal;
- remote URLs;
- symbolic-link escape;
- paths into current KRONOS data directories;
- paths to the current or temporal warehouse;
- stale working or WAL files.

## 10. Historical Source Contracts

### 10.1 Observed Contract

Contract:

```text
OBSERVED_HISTORICAL_SNAPSHOT_V1
```

Required:

- `history_mode = OBSERVED_TEMPORAL`;
- `evidence_classification = OBSERVED_SOURCE`;
- stable source-supplied entity identifier;
- source-supplied observation or reporting date;
- complete date-field provenance;
- one governed snapshot date per file;
- immutable source and schema hashes;
- no simulation metadata.

Observed dates may not come from file timestamps, process timestamps,
ingestion timestamps, row order, current date, or generated vintages.

### 10.2 Simulated Contract

Contract:

```text
SIMULATED_HISTORICAL_SNAPSHOT_V1
```

Required:

- `history_mode = SIMULATED_TEMPORAL`;
- `evidence_classification = SIMULATED_SOURCE`;
- stable source-supplied entity identifier;
- explicit simulated observation or reporting date;
- simulation method;
- simulation version;
- simulation producer;
- simulation seed when randomness was used.

Phase 2B does not generate simulated data. It only ingests externally created
and explicitly labelled simulated data.

Simulated snapshots are never eligible for genuine historical, true OOT,
regulatory IFRS9, observed migration, cure, or recovery claims.

## 11. Final Database Extension

Retain the existing schemas:

- `control`
- `staging`
- `reference`
- `core`
- `mart`

Create exactly 19 additive base tables.

### 11.1 Reference

1. `reference.dim_identity_grain`
2. `reference.dim_readiness_status`

### 11.2 Control

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

### 11.3 Staging

13. `staging.stg_historical_snapshot_row`
14. `staging.stg_historical_event_row`

### 11.4 Core Dimensions

15. `core.dim_historical_entity`
16. `core.dim_historical_facility`
17. `core.dim_historical_snapshot`

### 11.5 Core Facts

18. `core.fact_historical_credit_observation`
19. `core.fact_historical_credit_event`

Required post-deployment catalog:

```text
Schemas: 5
Tables: 36
Views: 0
Mart objects: 0
```

No existing table may be dropped, replaced, truncated, renamed, or redefined.

## 12. Reference Records

`reference.dim_identity_grain` contains:

- `BORROWER`
- `FACILITY`

Facility grain requires a stable source-supplied facility identifier. Borrower
identifiers must not be reused as facility proxies.

`reference.dim_readiness_status` contains:

- `NOT_ASSESSED`
- `READY_BUT_DISABLED`
- `NOT_READY`
- `NOT_ELIGIBLE`
- `FAILED`

`READY_BUT_DISABLED` means only that future-phase input fields appear
available. It never activates an analytical capability.

## 13. Dedicated Phase 2B Release Registration

Phase 2B must implement release registration in:

```text
src/temporal_risk/historical_ingestion/release_registry.py
```

It must use the existing `control.platform_release` table without altering its
schema.

Required release attributes:

```text
phase_name = PHASE2B
release_version = governed Phase 2B version
schema_count = 5
table_count = 36
view_count = 0
status = DRAFT, then PUBLISHED after verification
```

The release ID must be deterministically distinct from the Phase 2A release
ID.

The Phase 2B registrar must:

- insert or update only the Phase 2B release primary key;
- never call Phase 2A `register_release()`;
- never update the Phase 2A release row;
- never replace Phase 2A specification hashes;
- record controlled Phase 2B specification hashes;
- verify the Phase 2A release row is byte-for-byte equivalent by canonical
  row hash before and after publication.

## 14. Shared Registry Write Rules

Phase 2B may append governed metadata only to:

- `control.platform_release`
- `control.deployment_run`
- `control.source_asset`
- `control.source_column`
- `control.temporal_contract`
- `control.snapshot_registry`
- `control.snapshot_source_link`
- `control.publish_status`
- `staging.stg_snapshot_manifest`

Rules:

1. Every pre-existing Phase 2A row must remain unchanged by primary key and
   canonical row hash.
2. Total row counts may increase only through governed Phase 2B append
   operations.
3. Phase 2B source assets must set:

   ```text
   authoritative_baseline = false
   ```

4. Observed and simulated contracts must have distinct contract names,
   versions, IDs, and hashes.
5. Historical snapshots must use new snapshot IDs and must never overwrite
   the Phase 2A baseline snapshot.
6. Phase 2B append operations must be idempotent.
7. Existing Phase 2A release, source, contract, snapshot, manifest, deployment,
   and publish records must remain unchanged.

Phase 2B must never insert, update, or delete rows in:

- `control.temporal_quality_result`
- `control.reconciliation_result`
- `control.lineage_node`
- `control.lineage_edge`
- `control.column_lineage`

All historical DQ, reconciliation, and lineage evidence must use dedicated
Phase 2B tables.

## 15. Control Structures

### 15.1 Historical Ingestion Batch

Store:

- ingestion batch ID;
- source and manifest IDs;
- contract ID and version;
- history mode;
- start and end timestamps;
- lifecycle status;
- records read, staged, accepted, rejected, inserted, and skipped;
- snapshot count;
- source, working-database, and published-database hashes;
- error class and message.

### 15.2 Historical Ingestion File

Store:

- ingestion file ID;
- batch ID;
- source and manifest asset IDs;
- repository-relative paths;
- source formats;
- source and schema hashes;
- row and column counts;
- declared and observed snapshot dates;
- status and timestamps.

### 15.3 Historical Field Mapping

Store one row per explicit mapping:

- source column;
- canonical column;
- mapping type;
- required flag;
- source-supplied flag;
- permitted cast;
- transformation description.

Mappings may perform only explicit rename, safe datatype cast, null
preservation, warehouse-key hashing, and source event normalization.

Mappings must not generate an identifier, date, event, outcome, score, stage,
risk band, delinquency state, or loss value.

### 15.4 Reject Records

Store:

- batch and snapshot IDs;
- source asset and row;
- raw source entity and facility identifiers;
- column name;
- invalid value;
- severity;
- rejection reason;
- immutable payload JSON;
- rejection timestamp.

Reject handling must never modify the source.

### 15.5 Historical Publish Status

Allowed lifecycle:

```text
DRAFT -> VALIDATED -> PUBLISHED
```

Only a batch passing historical-storage DQ and reconciliation gates may be
published.

## 16. Staging and Core Grain

### 16.1 Snapshot Staging

`staging.stg_historical_snapshot_row` grain:

```text
one source row per ingestion batch and governed snapshot
```

The table may retain rejected rows to support exact source-to-staging parity.

### 16.2 Event Staging

Store only explicitly source-supplied events:

- `ORIGINATION`
- `DEFAULT`
- `CURE`
- `RECOVERY`
- `MATURITY`
- `CLOSURE`

No event may be inferred from stage, score, delinquency, watchlist, model
output, or row ordering.

### 16.3 Entity Dimension

Technical key:

```text
SHA-256(source_system | identity_grain | source_entity_id)
```

The original source identifier must be retained. The hash is a technical key,
not a fabricated business identifier.

### 16.4 Facility Dimension

Create only when a stable source-supplied facility ID exists.

Technical key:

```text
SHA-256(source_system | source_facility_id)
```

### 16.5 Snapshot Dimension

Store governed snapshot identity, source, contract, batch, date and date type,
history mode, evidence classification, identity continuity, source run/model
inventories, hashes, temporal quality, storage readiness, and load timestamp.

### 16.6 Observation Fact

Grain:

```text
one accepted entity/facility observation per governed snapshot
```

Observation ID:

```text
SHA-256(snapshot_id | entity_key | facility_key-or-null)
```

Store normalized source values only. Do not calculate or recalculate credit
metrics.

### 16.7 Event Fact

Grain:

```text
one explicitly source-supplied event per entity/facility and event date
```

No event analytics may be persisted.

## 17. Mandatory Data-Quality Framework

Run exactly 36 controls per source snapshot. Optional controls return
`NOT_APPLICABLE`; the control inventory remains fixed.

### Manifest and Source

1. Manifest exists.
2. Manifest JSON is valid.
3. Contract name and version are supported.
4. Source exists and is a regular file.
5. Source path is allowlisted.
6. Manifest hash equals source hash.
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
29. A different hash for the same governed snapshot is rejected as a version
    conflict.

### Optional Credit Fields

30. PD is in `[0,1]` when present.
31. LGD is in `[0,1]` when present.
32. EAD is non-negative when present.
33. IFRS9 stage is in the declared domain when present.
34. Risk band and grade are in declared domains when present.
35. Complete source run/model inventories are captured without fixed
    cardinality assumptions.
36. No business identifier, date, event, or credit value is generated.

Critical failures block publication. Row-level rejects are permitted only when
the accepted population still satisfies the governing snapshot contract.

## 18. Data-Readiness Framework

Create exactly six readiness results per governed snapshot:

- `HISTORICAL_STORAGE`
- `MIGRATION_INPUTS`
- `ROLL_RATE_INPUTS`
- `VINTAGE_INPUTS`
- `TRUE_OOT_INPUTS`
- `IFRS9_TEMPORAL_INPUTS`

Every result must set:

```text
activation_status = DISABLED_PENDING_FUTURE_PHASE
```

No Phase 2B result may activate processing.

### 18.1 Historical Storage

May pass only with:

- valid contract;
- immutable source hash;
- source-supplied entity identity;
- source-supplied observation or reporting date;
- unique snapshot grain;
- successful critical DQ controls;
- complete reconciliation.

### 18.2 Migration Inputs

`READY_BUT_DISABLED` may be used only for observed history with at least two
source snapshots, stable identity continuity, and a supported source state
field.

No transition is calculated.

### 18.3 Roll-Rate Inputs

`READY_BUT_DISABLED` may be used only for observed facility identity,
consecutive source dates, and source-supplied delinquency state.

No roll rate is calculated.

### 18.4 Vintage Inputs

`READY_BUT_DISABLED` may be used only for observed source-supplied origination
dates and sufficient source observation depth.

No cohort or curve is calculated.

### 18.5 True OOT Inputs

`READY_BUT_DISABLED` may be used only for observed feature dates, mature
source outcomes, model version, model freeze metadata, and point-in-time
feature availability.

Simulated sources are `NOT_ELIGIBLE`.

No model is trained, scored, or validated.

### 18.6 Mandatory IFRS9 Readiness Ceiling

During Phase 2B:

```text
IFRS9_TEMPORAL_INPUTS.data_status ∈ {NOT_READY, NOT_ELIGIBLE}
IFRS9_TEMPORAL_INPUTS.activation_status = DISABLED_PENDING_FUTURE_PHASE
```

The following status is prohibited for IFRS9 in Phase 2B:

```text
READY_BUT_DISABLED
```

This ceiling applies even if individual source fields such as reporting date,
origination date, maturity date, EIR, default date, cure date, or recovery date
are present.

Reason: Phase 2B does not persist or validate the complete contractual
cash-flow, discounting, scenario, and lifetime-exposure architecture required
for temporal IFRS9 calculations.

Phase 2B must contain no:

- IFRS9 calculation;
- IFRS9 staging engine;
- SICR calculation;
- cash-flow schedule generation;
- EIR discounting;
- macroeconomic scenario logic;
- probability weighting;
- lifetime ECL;
- provision or reserve logic.

## 19. Reconciliation Framework

Create exactly 12 dedicated Phase 2B reconciliation results per snapshot:

1. Source rows equal staging rows.
2. Staging rows equal accepted plus rejected rows.
3. Accepted rows equal inserted or idempotently skipped observation facts.
4. Accepted distinct entities equal linked entity-dimension population.
5. Accepted distinct facilities equal linked facility-dimension population.
6. One source snapshot equals one snapshot-dimension row.
7. Source hash equals registered source hash.
8. Source schema hash equals registered schema hash.
9. Declared snapshot date equals persisted snapshot date.
10. Source event count equals staged event count.
11. Accepted staged events equal inserted or idempotently skipped event facts.
12. Optional EAD/default aggregate parity passes or is `NOT_APPLICABLE`.

Results must be written only to:

```text
control.historical_reconciliation_result
```

No analytical aggregation may be persisted.

## 20. Independent Lineage Framework

Phase 2B lineage must connect:

- manifest file;
- historical source file;
- temporal contract;
- field-mapping set;
- snapshot staging;
- event staging;
- entity dimension;
- facility dimension when applicable;
- snapshot dimension;
- observation fact;
- event fact when applicable;
- readiness evidence;
- reject evidence when applicable;
- published ingestion batch.

Column lineage is mandatory for every canonical mapped field.

Write only to:

- `control.historical_lineage_node`
- `control.historical_lineage_edge`
- `control.historical_column_lineage`

Do not write to Phase 2A or Phase 4 lineage structures.

## 21. Idempotency and Conflict Policy

The idempotency key consists of:

```text
source hash
+ manifest hash
+ contract version
+ governed snapshot identity
```

An exact match returns:

```text
SKIPPED_ALREADY_PUBLISHED
```

It must add no duplicate staging, dimension, fact, readiness, reconciliation,
lineage, or publish records.

The same governed snapshot identity with a different source hash returns:

```text
SNAPSHOT_VERSION_CONFLICT
```

Published snapshots must not be overwritten or superseded. Corrections require
a separately approved governance design.

## 22. Dynamic Protected-Hash Boundary

Protected verification must use SHA-256 inventories captured dynamically at
the start of implementation verification and at the start of every schema or
ingestion deployment.

No hardcoded repository hash and no Git state may be required.

### 22.1 Protected Assets

Protect:

- `app/`
- `src/enterprise_data/`
- `src/credit_risk/`
- `src/model_validation/`
- `src/provisioning/`
- `src/ews/`
- `src/stress_testing/`
- `src/contagion/`
- `src/decisioning/`
- `src/reporting/`
- other existing risk-engine modules;
- `models/`
- `data/`
- `outputs/`
- `reports/`
- `analytics/`
- `sql/phase2a/`
- all unaffected files under `src/temporal_risk/`;
- all existing Phase 1, Phase 1.5, and Phase 4 documentation and tests.

### 22.2 Authorized Exclusions

Exclude only intended Phase 2B additions and the explicitly authorized Phase
2A guard change:

- `src/temporal_risk/historical_ingestion/`
- `sql/phase2b/`
- `tests/test_phase2b_*.py`
- Phase 2B documentation;
- `src/temporal_risk/pipeline.py` during implementation-diff verification;
- explicitly amended Phase 2A guard tests;
- `temporal_platform/inbound/`
- `temporal_platform/backups/`
- `temporal_platform/evidence/phase2b/`
- the intended temporal database target during an authorized deployment.

Exclusion permits intended change only. It does not permit writes outside the
defined Phase 2B responsibility.

### 22.3 Verification Rules

- Baseline and final inventories must use repository-relative paths.
- File additions, removals, and content changes in protected paths fail
  verification.
- Inventory comparison must not depend on Git.
- The current KRONOS warehouse and scored portfolio require direct before and
  after SHA-256 equality.
- Existing Phase 2A shared rows require canonical PK-and-row-hash equality.
- Phase 2B code must not modify protected files at deployment runtime.

## 23. Schema Deployment Workflow

1. Validate Phase 2A acceptance evidence.
2. Validate controlled Phase 2B specifications.
3. Capture the temporal database SHA-256 and exact 5/17/0 catalog.
4. Capture all Phase 2A table definitions, primary keys, row counts, and
   canonical row hashes.
5. Capture current warehouse, scored-portfolio, and protected-file baselines.
6. Validate target and evidence paths before any write.
7. Close all temporal database connections.
8. Create and hash-verify a fresh pre-Phase 2B backup.
9. Copy the temporal database to a temporary working location.
10. Apply only the five Phase 2B DDL assets.
11. Load only the seven required reference rows.
12. Validate the exact 5/36/0 catalog and empty mart schema.
13. Verify all pre-existing Phase 2A rows remain unchanged by PK and row hash.
14. Create a distinct Phase 2B release through the Phase 2B registrar.
15. Publish only the closed, validated working database.
16. Reopen the published database read-only.
17. Verify catalog, release separation, hashes, and shared-row preservation.
18. Verify current warehouse, scored portfolio, and protected assets are
    unchanged.
19. Write Phase 2B deployment evidence.

Schema deployment must not ingest a historical source automatically.

## 24. Historical Ingestion Workflow

1. Validate manifest and inbound paths before writes.
2. Capture manifest and source hashes.
3. Select the observed or simulated contract.
4. Validate explicit field mappings.
5. Capture temporal database and protected baselines.
6. Create and verify a fresh backup.
7. Copy the temporal database to a working database.
8. Append governed source and manifest metadata.
9. Load all source rows to historical staging.
10. Execute 36 DQ controls.
11. Record row rejects without changing the source.
12. Load accepted entity, facility, snapshot, observation, and event records.
13. Evaluate six readiness capabilities.
14. Enforce the IFRS9 readiness ceiling.
15. Execute 12 historical reconciliations.
16. Build independent Phase 2B lineage.
17. Validate historical-storage readiness and idempotency.
18. Record `DRAFT`, `VALIDATED`, and `PUBLISHED`.
19. Verify all original Phase 2A rows remain unchanged.
20. Publish the closed working database.
21. Reopen read-only and verify hashes and counts.
22. Write ingestion-specific evidence.

## 25. Expected Row-Count Contracts

### 25.1 Schema Deployment Only

Expected additions:

| Object | Rows Added |
|---|---:|
| `reference.dim_identity_grain` | 2 |
| `reference.dim_readiness_status` | 5 |
| Distinct Phase 2B platform release | 1 |
| Phase 2B deployment run | 1 |
| Phase 2B publish transitions | governed lifecycle rows |
| Other new Phase 2B tables | 0 |
| Historical observations | 0 |
| Historical events | 0 |
| Mart objects | 0 |

Original Phase 2A rows remain unchanged. Shared-table total counts may increase
only through the listed append-only Phase 2B records.

### 25.2 Successful Snapshot

Let:

- `N` = source rows;
- `R` = rejected rows;
- `A = N - R` = accepted rows;
- `E` = distinct accepted entities;
- `F` = distinct accepted non-null facilities;
- `V` = explicitly source-supplied events;
- `M` = declared field mappings.

Expected additions:

| Object | Rows Added |
|---|---:|
| Ingestion batch | 1 |
| Ingestion file | 1 |
| Field mappings | `M` |
| Snapshot staging | `N` |
| Reject records | `R` |
| Entity dimension | New members up to `E` |
| Facility dimension | New members up to `F` |
| Snapshot dimension | 1 |
| Observation fact | `A` |
| Event staging | `V` |
| Event fact | Accepted events up to `V` |
| Readiness results | 6 |
| Historical reconciliations | 12 |
| Historical publish transitions | 3 |

All counts are source-driven. No 50,000-row or fixed run/model cardinality
assumption applies.

## 26. Mandatory Test Requirements

### 26.1 Audit-Mandated Tests

Implementation must prove:

1. The original Phase 2A `platform_release` row is unchanged.
2. Every pre-existing shared Phase 2A row is unchanged by primary key and
   canonical row hash.
3. A distinct Phase 2B release row exists and records the 5/36/0 catalog.
4. Phase 2A returns `PHASE2A_UPGRADE_PRESENT` for the exact recognized Phase
   2B catalog.
5. The upgrade guard runs before evidence, backup, working database, or
   writable connection creation.
6. A fresh temporary Phase 2A deployment still validates exactly 5/17/0.
7. Unknown 5/36/0 catalogs are not falsely accepted as Phase 2B.
8. Stale working DuckDB and WAL files are ignored.
9. Protected-hash inventories follow the allowlist and authorized exclusions.
10. Git is not required.
11. IFRS9 readiness is limited to `NOT_READY` or `NOT_ELIGIBLE`.
12. IFRS9 activation is always `DISABLED_PENDING_FUTURE_PHASE`.
13. IFRS9 `READY_BUT_DISABLED` is impossible in Phase 2B.
14. Full rollback restores the exact pre-Phase 2B database SHA-256 and 5/17/0
    catalog.

### 26.2 Functional Tests

Also verify:

- exact 5/36/0 catalog;
- no views and empty mart schema;
- observed and simulated contract validation;
- manifest validation;
- path traversal and symbolic-link escape rejection;
- immutable source hashes;
- source-supplied date provenance;
- absence of generated identities, dates, events, and credit values;
- borrower and facility grain;
- optional-field normalization;
- exactly 36 DQ controls;
- reject handling;
- six readiness records;
- exactly 12 historical reconciliations;
- complete independent lineage;
- identical-source idempotency;
- conflicting snapshot rejection;
- schema deployment without ingestion;
- safe failure without evidence mutation;
- current warehouse and scored-portfolio hash equality;
- no application, dashboard, Phase 4, model, or analytics dependency.

### 26.3 Compatibility Tests

Run:

- all Phase 2A tests;
- all Phase 2B tests;
- existing application compatibility tests;
- existing Phase 4 compatibility tests;
- protected-hash verification;
- temporal database rollback verification.

Known pre-existing unrelated test failures must be documented and compared
against a pre-implementation baseline. They must not be silently attributed to
Phase 2B or repaired outside scope.

## 27. Rollback and Independent Removability

Rollback is file-based only.

Before every schema deployment or ingestion:

1. Close all temporal connections.
2. Capture the published temporal database hash.
3. Create a fresh backup under `temporal_platform/backups/`.
4. Verify the backup hash equals the published database hash.
5. Record the pre-operation catalog and Phase 2A row hashes.

Rollback:

1. Close all connections.
2. Restore the verified pre-Phase 2B backup through atomic replacement.
3. Verify the restored SHA-256 equals the exact pre-Phase 2B SHA-256.
4. Verify the restored catalog is exactly 5 schemas, 17 tables, and 0 views.
5. Verify original Phase 2A row hashes.
6. Verify Phase 2A tests.

Complete removal:

- restore the pre-Phase 2B database first;
- delete `src/temporal_risk/historical_ingestion/`;
- delete `sql/phase2b/`;
- delete Phase 2B tests;
- delete Phase 2B documentation;
- delete Phase 2B inbound and evidence directories;
- revert only the authorized Phase 2A upgrade-guard change.

The backup must be restored before deleting a runtime directory that contains
the backup.

After removal, Phase 2A and all existing KRONOS phases must remain operational.

## 28. Implementation Sequence

### Phase 2B.1 — Upgrade Safety and Schema

- implement the Phase 2A upgrade guard;
- implement Phase 2B configuration and scope controls;
- deploy the 19 additive tables and seven reference rows;
- implement the distinct release registrar;
- verify 5/36/0 and Phase 2A row preservation.

### Phase 2B.2 — Contracts and Source Governance

- implement observed and simulated contracts;
- implement immutable manifests;
- implement inbound path safety;
- implement explicit schema mapping;
- implement source and manifest append-only registration.

### Phase 2B.3 — Staging and Quality

- implement extraction and normalization;
- load source rows to staging;
- execute 36 DQ controls;
- implement reject handling;
- implement six disabled readiness results;
- enforce the IFRS9 readiness ceiling.

### Phase 2B.4 — Historical Storage Controls

- implement entity, facility, and snapshot dimensions;
- implement observation and source-event facts;
- execute 12 reconciliations;
- create independent Phase 2B lineage.

### Phase 2B.5 — Publication and Acceptance

- implement idempotency and conflict handling;
- implement closed-file publication;
- implement dynamic protected hashes;
- verify rollback;
- run all compatibility tests;
- generate the completion report.

No later analytical phase may be included in any Phase 2B increment.

## 29. Completion Criteria

Phase 2B is complete only when:

- the isolated temporal database contains 5 schemas, 36 tables, and 0 views;
- the mart schema remains empty;
- all 19 new tables match this specification;
- all original Phase 2A rows remain unchanged by PK and hash;
- the Phase 2A release row is unchanged;
- a distinct Phase 2B release row exists;
- the Phase 2A upgrade guard returns `PHASE2A_UPGRADE_PRESENT` before writes;
- fresh Phase 2A deployment still validates exact 5/17/0;
- observed and simulated contracts are independently enforced;
- no source is ingested without source-supplied temporal identity;
- no identifier, date, event, or credit value is fabricated;
- schema deployment performs no automatic ingestion;
- exactly 36 DQ controls execute per snapshot;
- exactly six readiness records are created per snapshot;
- exactly 12 historical reconciliations execute per snapshot;
- IFRS9 readiness never exceeds `NOT_READY` or `NOT_ELIGIBLE`;
- every analytical activation remains disabled;
- no Phase 2A DQ, reconciliation, or lineage table receives a Phase 2B row;
- idempotency, conflict, lineage, protected-hash, compatibility, and rollback
  tests pass;
- rollback restores the exact pre-Phase 2B database hash and 5/17/0 catalog;
- no migration, roll-rate, vintage, true OOT, IFRS9 calculation, dashboard,
  application, current warehouse, Phase 4, or SAS-style analytics capability
  exists.

## 30. Implementation Authorization Gate

Before code implementation begins, the implementation process must confirm:

```text
GOVERNING_SPECIFICATION = PHASE2B_IMPLEMENTATION_SPEC_FINAL.md
AUDIT_CORRECTIONS_INCORPORATED = true
PHASE2A_STATUS = COMPLETE
ANALYTICAL_SCOPE_ENABLED = false
```

Failure of any condition must stop implementation.
