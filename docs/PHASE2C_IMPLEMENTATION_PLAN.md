# KRONOS Phase 2C Implementation Plan

## 1. Status and Authorization

```text
Status: PLANNING ONLY
Implementation authorized: NO
Pre-implementation audit required: YES
```

This document proposes Phase 2C only. It does not authorize code, SQL,
database, runtime, or test changes.

Phase 2A and Phase 2B are accepted. Phase 2C implementation may begin only
after a formal pre-implementation audit approves this plan and resolves every
catalog, preservation, rollback, and scope-control requirement.

## 2. Verified Starting State

The current isolated temporal database is:

```text
temporal_platform/warehouse/kronos_temporal_risk.duckdb
```

Verified current catalog:

```text
Schemas:      5
Tables:      36
Views:        0
Mart objects: 0
```

Verified release state:

```text
PHASE2A: PUBLISHED
PHASE2B: PUBLISHED
```

Verified historical population:

```text
Historical snapshots:       0
Historical observations:    0
Historical ingestion runs:  0
Readiness results:           0
```

Therefore, Phase 2C may deploy a governed migration-readiness control
foundation, but it cannot publish a production snapshot-pair readiness result
until at least two qualifying source-supplied observed snapshots have been
ingested through Phase 2B.

The absence of historical snapshots must return:

```text
PHASE2C_SOURCE_NOT_READY
```

It must not trigger generated snapshots, generated dates, simulated
continuity, or fabricated readiness evidence.

## 3. Objective

Phase 2C extends the isolated temporal platform with governed
migration-transition readiness controls.

Phase 2C may:

- select two governed historical snapshots;
- verify chronological snapshot continuity;
- verify persistent source-supplied identity;
- verify source-supplied state-field continuity;
- register a migration-readiness contract;
- execute readiness data-quality controls;
- record non-analytical continuity evidence;
- execute migration-readiness reconciliations;
- persist independent Phase 2C lineage;
- calculate a governance control score;
- publish migration-readiness evidence with analytical activation disabled.

Phase 2C evaluates whether future migration analytics could be implemented
honestly. It does not implement those analytics.

## 4. Implementation Boundary

Phase 2C must not:

- generate migration matrices;
- persist from-state/to-state combinations;
- calculate transition counts by state pair;
- calculate transition probabilities;
- classify upgrades, downgrades, cures, or deterioration;
- calculate roll rates;
- calculate vintage cohorts or curves;
- calculate cumulative default curves;
- perform true OOT validation;
- perform model training, scoring, recalibration, or replacement;
- perform IFRS9 calculations or staging;
- calculate ECL, provisions, reserves, or discounted cash flows;
- create dashboards or application integration;
- integrate with the current KRONOS warehouse;
- modify Phase 4 architecture or artifacts;
- integrate with SAS-style analytics;
- create database views, marts, facts, or dimensions;
- generate identities, dates, states, events, or historical records.

Any attempted prohibited capability must stop with:

```text
PHASE2C_SCOPE_VIOLATION
```

## 5. Preserved Platforms

The following must remain unchanged:

- `data/warehouse/kronos_risk.duckdb`
- `data/processed/scored_portfolio.csv`
- `app/`
- `src/enterprise_data/`
- Phase 1 and Phase 1.5 assets
- Phase 4A through Phase 4E assets
- models, scoring, validation, reporting, and risk engines
- all existing Phase 2A database rows
- all existing Phase 2B database rows
- all Phase 2A DQ, reconciliation, and lineage evidence
- all Phase 2B DQ, reconciliation, and lineage evidence
- all Phase 2B historical facts and dimensions

Phase 2C failure must not affect KRONOS startup, Phase 2A, Phase 2B, or any
completed Phase 4 capability.

## 6. Runtime Architecture

Phase 2C may use only:

```text
temporal_platform/
├── warehouse/
│   └── kronos_temporal_risk.duckdb
├── backups/
└── evidence/
    └── phase2c/
        └── <deployment_or_readiness_run_id>/
```

Phase 2C must not create an inbound data path. It consumes only already
published Phase 2B snapshot metadata and facts.

No Phase 2C runtime asset may be written under:

- `data/`
- `models/`
- `outputs/`
- `reports/`
- `analytics/`

## 7. Proposed Authored Files

Create:

```text
src/temporal_risk/migration_readiness/
├── __init__.py
├── config.py
├── contracts.py
├── source_catalog.py
├── pair_selector.py
├── continuity.py
├── state_validation.py
├── data_quality.py
├── reconciliation.py
├── lineage.py
├── release_registry.py
├── publisher.py
└── pipeline.py
```

Create:

```text
sql/phase2c/ddl/
├── 001_migration_control_tables.sql
└── 002_migration_lineage_tables.sql
```

Create tests:

```text
tests/test_phase2c_schema.py
tests/test_phase2c_contracts.py
tests/test_phase2c_connection_safety.py
tests/test_phase2c_upgrade_guards.py
tests/test_phase2c_snapshot_pair.py
tests/test_phase2c_quality.py
tests/test_phase2c_readiness.py
tests/test_phase2c_reconciliation.py
tests/test_phase2c_lineage.py
tests/test_phase2c_idempotency.py
tests/test_phase2c_release_registry.py
tests/test_phase2c_scope_boundary.py
tests/test_phase2c_no_analytics.py
tests/test_phase2c_protected_hashes.py
tests/test_phase2c_rollback.py
tests/test_phase2c_compatibility.py
```

Create implementation documentation:

```text
docs/PHASE2C_COMPLETION_REPORT.md
docs/MIGRATION_READINESS_ARCHITECTURE.md
docs/MIGRATION_READINESS_CONTRACT.md
docs/MIGRATION_READINESS_DATA_DICTIONARY.md
docs/MIGRATION_READINESS_OPERATIONS.md
```

## 8. Existing Files Requiring Pre-Audit Approval

The current Phase 2A and Phase 2B implementations recognize an exact
5-schema/36-table Phase 2B catalog. An additive Phase 2C catalog would
otherwise cause their exact-catalog checks to reject the upgraded database.

The pre-implementation audit must approve narrowly scoped compatibility
changes to:

```text
src/temporal_risk/pipeline.py
src/temporal_risk/historical_ingestion/config.py
src/temporal_risk/historical_ingestion/contracts.py
src/temporal_risk/historical_ingestion/pipeline.py
```

Permitted purposes only:

1. Phase 2A recognizes the exact Phase 2C catalog and returns
   `PHASE2A_UPGRADE_PRESENT` before any write or evidence creation.
2. Phase 2B schema deployment recognizes the exact Phase 2C catalog and
   returns `PHASE2B_UPGRADE_PRESENT` before any write or evidence creation.
3. Phase 2B historical ingestion accepts the exact additive Phase 2C catalog
   while continuing to validate every Phase 2A and Phase 2B object.
4. Counts alone are never sufficient; exact object names are mandatory.
5. Phase 2A and Phase 2B must not import the Phase 2C package.

No existing Phase 2A or Phase 2B table, contract, DQ rule, reconciliation,
lineage record, release row, or ingestion behavior may be redesigned.

The formal pre-implementation audit must reject the plan if these limited
guard changes cannot preserve Phase 2B ingestion after the upgrade.

## 9. Proposed Database Extension

Retain the existing schemas:

- `control`
- `staging`
- `reference`
- `core`
- `mart`

Create exactly ten additive control tables:

1. `control.migration_readiness_run`
2. `control.migration_snapshot_pair`
3. `control.migration_transition_contract`
4. `control.migration_quality_result`
5. `control.migration_readiness_result`
6. `control.migration_reconciliation_result`
7. `control.migration_lineage_node`
8. `control.migration_lineage_edge`
9. `control.migration_column_lineage`
10. `control.migration_publish_status`

Proposed post-deployment catalog:

```text
Schemas:      5
Tables:      46
Views:        0
Mart objects: 0
```

No staging, reference, core, or mart object is added. No existing object is
dropped, replaced, truncated, renamed, or altered.

## 10. Proposed Table Contracts

### 10.1 `control.migration_readiness_run`

Grain:

```text
one schema deployment or snapshot-pair readiness evaluation
```

Required attributes:

- readiness run ID;
- Phase 2C release ID;
- run type;
- start and end timestamps;
- lifecycle status;
- earlier and later snapshot IDs;
- state field;
- contract ID and version;
- quality score and status;
- readiness status;
- activation status;
- pre-operation and published database hashes;
- error class and message.

### 10.2 `control.migration_snapshot_pair`

Grain:

```text
one governed earlier/later snapshot pair per state-field contract
```

Store only governance evidence:

- pair ID;
- readiness run ID;
- earlier and later snapshot IDs and dates;
- source system;
- identity grain;
- history mode;
- evidence classification;
- state field;
- earlier and later source hashes;
- earlier and later population counts;
- overlapping identity count;
- earlier and later state-complete overlap counts;
- identity continuity status;
- state continuity status;
- eligibility status.

This table must not contain:

- from state;
- to state;
- transition category;
- transition count;
- transition probability;
- upgrade/downgrade classification.

### 10.3 `control.migration_transition_contract`

Contract:

```text
MIGRATION_TRANSITION_READINESS_V1
```

Store:

- contract ID, name, and version;
- supported history mode;
- supported evidence classification;
- permitted identity grains;
- permitted state fields;
- declared state-domain rules;
- required source provenance;
- prohibited capabilities;
- contract hash;
- status and registration timestamp.

Phase 2C permits only source-supplied:

- `risk_grade`
- `risk_band`

`delinquency_state` is reserved for a future roll-rate phase.
`ifrs9_stage` is reserved for the temporal IFRS9 phase.
`default_outcome` is not a migration state in Phase 2C.

### 10.4 `control.migration_quality_result`

Grain:

```text
one quality control per readiness run and snapshot pair
```

Store:

- quality result ID;
- readiness run and pair IDs;
- control name and category;
- critical flag;
- earlier and later values;
- status;
- details;
- evaluation timestamp.

### 10.5 `control.migration_readiness_result`

Create exactly four results per eligible snapshot-pair evaluation:

1. `SNAPSHOT_CONTINUITY`
2. `IDENTITY_CONTINUITY`
3. `STATE_FIELD_CONTINUITY`
4. `MIGRATION_TRANSITION_INPUTS`

Every result must set:

```text
activation_status = DISABLED_PENDING_FUTURE_PHASE
```

Allowed data statuses:

- `READY_BUT_DISABLED`
- `NOT_READY`
- `NOT_ELIGIBLE`
- `FAILED`

The governance readiness score is:

```text
100 * passed applicable controls / applicable controls
```

It is a control-completeness score only. It must never be described as a
transition score, credit score, migration probability, or model output.

### 10.6 `control.migration_reconciliation_result`

Store only pair-level control parity. No state-pair aggregation is permitted.

### 10.7 Phase 2C Lineage Tables

Use dedicated:

- `control.migration_lineage_node`
- `control.migration_lineage_edge`
- `control.migration_column_lineage`

Do not write to Phase 2A or Phase 2B lineage tables.

### 10.8 `control.migration_publish_status`

Allowed lifecycle:

```text
DRAFT -> VALIDATED -> PUBLISHED
```

A `NOT_READY`, `NOT_ELIGIBLE`, or `FAILED` pair must not be published as
migration-ready.

## 11. Snapshot-Pair Eligibility Contract

A pair is eligible only when all conditions are satisfied:

1. Both snapshots exist in `core.dim_historical_snapshot`.
2. Both snapshots were published through Phase 2B controls.
3. Snapshot IDs are distinct.
4. The earlier source-supplied snapshot date precedes the later date.
5. Both snapshots use `OBSERVED_TEMPORAL`.
6. Both snapshots use `OBSERVED_SOURCE`.
7. Both snapshots belong to the same source system.
8. Both snapshots use the same identity grain.
9. The source-supplied identity is stable and overlaps across snapshots.
10. The selected state field is permitted by the Phase 2C contract.
11. The state field is explicitly mapped and source supplied in both
    snapshots.
12. Both snapshots use a compatible declared state domain.
13. Source hashes and mappings remain consistent with Phase 2B evidence.

Simulated snapshots are:

```text
NOT_ELIGIBLE
```

They may not support observed migration-readiness claims.

## 12. Mandatory Data-Quality Controls

Execute exactly 24 controls per snapshot-pair evaluation.

### Platform and Release

1. Exact recognized Phase 2C catalog.
2. Published Phase 2A release exists.
3. Published Phase 2B release exists.
4. Mart remains empty and no views exist.

### Snapshot Governance

5. Earlier snapshot exists.
6. Later snapshot exists.
7. Snapshot IDs are distinct.
8. Earlier snapshot date precedes later snapshot date.
9. Both snapshots are Phase 2B-published.
10. Both snapshots are `OBSERVED_TEMPORAL`.
11. Both snapshots are `OBSERVED_SOURCE`.
12. Both snapshots have registered immutable source hashes.

### Identity Continuity

13. Source system matches.
14. Identity grain matches.
15. Earlier identity keys are non-null.
16. Later identity keys are non-null.
17. Earlier identity grain is unique.
18. Later identity grain is unique.
19. At least one identity overlaps.

### State-Field Continuity

20. State field is contract-allowlisted.
21. Earlier state mapping exists and is source supplied.
22. Later state mapping exists and is source supplied.
23. State-domain contract is identical across the pair.
24. Overlapping identities have valid state-domain values in both snapshots.

Critical failures block publication. No row-level transition record may be
created as part of quality evaluation.

## 13. Mandatory Reconciliations

Create exactly ten reconciliation results per evaluated pair:

1. Earlier snapshot registry count equals one.
2. Later snapshot registry count equals one.
3. Earlier accepted Phase 2B population equals earlier observation-fact
   population.
4. Later accepted Phase 2B population equals later observation-fact
   population.
5. Earlier distinct identity count equals earlier fact identity count.
6. Later distinct identity count equals later fact identity count.
7. Overlap count does not exceed earlier population.
8. Overlap count does not exceed later population.
9. Earlier state-complete overlap plus earlier state-missing overlap equals
   total overlap.
10. Later state-complete overlap plus later state-missing overlap equals total
    overlap.

Write only to:

```text
control.migration_reconciliation_result
```

Do not persist state-pair counts or any analytical aggregation.

## 14. Independent Lineage

Required lineage nodes:

- Phase 2C transition-readiness contract;
- earlier historical snapshot;
- later historical snapshot;
- earlier identity mapping;
- later identity mapping;
- earlier state mapping;
- later state mapping;
- continuity control evidence;
- readiness evidence;
- published readiness run.

Required lineage edges must connect the two governed source snapshots and
their source-supplied mappings to the control evidence and published
readiness result.

Column lineage must cover, at minimum:

- earlier identity source column;
- later identity source column;
- earlier snapshot-date source column;
- later snapshot-date source column;
- earlier state source column;
- later state source column.

Lineage must not identify a transition fact, transition matrix, mart, view, or
analytical output because none may exist in Phase 2C.

## 15. Safe Entry Points

Proposed entry points:

```text
deploy_phase2c_schema()
deploy_phase2c_schema_safe()
evaluate_migration_readiness()
evaluate_migration_readiness_safe()
```

Governed statuses:

- `PHASE2C_SCHEMA_READY`
- `PHASE2C_READINESS_PUBLISHED`
- `PHASE2C_SCOPE_VIOLATION`
- `PHASE2C_UNAVAILABLE`
- `PHASE2C_BASELINE_MISMATCH`
- `PHASE2C_SOURCE_NOT_READY`
- `PHASE2C_SOURCE_NOT_ELIGIBLE`
- `PHASE2C_PAIR_CONFLICT`
- `SKIPPED_ALREADY_PUBLISHED`

No exception may propagate into KRONOS, Phase 2A, Phase 2B, application, or
Phase 4 callers.

## 16. Idempotency

The readiness-evaluation idempotency key is:

```text
earlier snapshot ID
+ later snapshot ID
+ state field
+ Phase 2C contract version
+ earlier source hash
+ later source hash
```

An exact published match returns:

```text
SKIPPED_ALREADY_PUBLISHED
```

The same snapshot pair and state field with changed source or contract
evidence returns:

```text
PHASE2C_PAIR_CONFLICT
```

Published Phase 2C evidence must not be overwritten.

## 17. Release Registration

Phase 2C must use a dedicated release registrar and append a distinct row to:

```text
control.platform_release
```

Required release attributes:

```text
phase_name = PHASE2C
schema_count = 5
table_count = 46
view_count = 0
status = DRAFT, then PUBLISHED
```

The registrar must:

- update only the deterministic Phase 2C release primary key;
- preserve Phase 2A and Phase 2B release rows by canonical row hash;
- preserve all existing Phase 2A and Phase 2B rows;
- record controlled Phase 2C specification hashes;
- use no Phase 2A or Phase 2B release-registration function.

## 18. Protected Hash Boundary

Capture dynamic SHA-256 inventories before each schema deployment and
readiness evaluation.

Protect:

- all existing KRONOS authored assets;
- `app/`;
- `src/enterprise_data/`;
- model and risk-engine code;
- `models/`, `data/`, `outputs/`, `reports/`, and `analytics/`;
- current warehouse;
- scored portfolio;
- all unaffected Phase 2A and Phase 2B code, SQL, tests, and documentation;
- all pre-existing Phase 2A and Phase 2B database rows.

Authorize only:

- `src/temporal_risk/migration_readiness/`;
- `sql/phase2c/`;
- `tests/test_phase2c_*.py`;
- Phase 2C documentation;
- pre-audit-approved Phase 2A/2B upgrade-guard files;
- `temporal_platform/evidence/phase2c/`;
- `temporal_platform/backups/`;
- the isolated temporal database during an authorized Phase 2C operation.

Use no Git dependency. Retain the accepted exact-file exclusions for the three
volatile generated artifacts established by the Phase 2B remediation.

## 19. Deployment Workflow

1. Verify Phase 2A and Phase 2B acceptance evidence.
2. Verify the exact 5/36/0 source catalog.
3. Verify the Phase 2A and Phase 2B published releases.
4. Capture the temporal database SHA-256.
5. Capture every existing database row by primary key and canonical row hash.
6. Capture current warehouse and scored-portfolio SHA-256 values.
7. Capture the protected repository inventory.
8. Validate the Phase 2C specification and runtime paths before writes.
9. Close all temporal database connections.
10. Create and verify a fresh file backup.
11. Copy the published temporal database to a working file.
12. Apply only the two Phase 2C DDL assets.
13. Register the single Phase 2C readiness contract.
14. Register the distinct Phase 2C release.
15. Validate the exact 5/46/0 catalog and empty mart schema.
16. Verify all pre-existing Phase 2A and Phase 2B rows by PK and hash.
17. Publish only the closed, validated working database.
18. Reopen read-only and repeat catalog and preservation checks.
19. Verify current warehouse, scored portfolio, and protected assets.
20. Write deployment evidence under `temporal_platform/evidence/phase2c/`.

Schema deployment must not evaluate a snapshot pair automatically.

## 20. Readiness Evaluation Workflow

1. Validate scope and requested state field.
2. Open the published temporal database read-only.
3. Validate the exact recognized Phase 2C catalog.
4. Select or validate explicit earlier and later snapshot IDs.
5. Return `PHASE2C_SOURCE_NOT_READY` before writes when fewer than two
   qualifying observed snapshots exist.
6. Return `PHASE2C_SOURCE_NOT_ELIGIBLE` before writes for simulated or
   incompatible snapshots.
7. Capture database and protected baselines.
8. Create and verify a fresh backup.
9. Copy the temporal database to a working file.
10. Register the readiness run and governed snapshot pair.
11. Execute exactly 24 quality controls.
12. Persist exactly four readiness results with activation disabled.
13. Execute exactly ten reconciliations.
14. Persist independent Phase 2C lineage.
15. Verify that no transition analytical object or output exists.
16. Record `DRAFT`, `VALIDATED`, and `PUBLISHED`.
17. Verify all Phase 2A and Phase 2B rows remain unchanged.
18. Publish the closed working database.
19. Reopen read-only and verify catalog, hashes, and evidence counts.
20. Write readiness evidence under `temporal_platform/evidence/phase2c/`.

## 21. Expected Row Counts

### Schema Deployment

| Object | Expected Addition |
|---|---:|
| Phase 2C release row | 1 |
| Migration transition contract | 1 |
| Schema deployment run | 1 |
| Phase 2C publish transitions | 3 |
| Other Phase 2C tables | 0 |
| Historical observations | 0 |
| Migration matrices | 0 |
| Views | 0 |
| Mart objects | 0 |

### Successful Readiness Evaluation

| Object | Expected Addition |
|---|---:|
| Readiness run | 1 |
| Snapshot pair | 1 |
| Quality results | 24 |
| Readiness results | 4 |
| Reconciliation results | 10 |
| Lineage nodes | 10 |
| Lineage edges | governed edge inventory |
| Column lineage | minimum 6; source-mapping driven |
| Publish transitions | 3 |
| Historical facts | 0 |
| Transition records | 0 |
| Analytical outputs | 0 |

Given the verified current database population, the initial production
readiness-evaluation addition is expected to be zero until qualifying observed
snapshots are ingested through Phase 2B.

## 22. Testing Requirements

Tests must prove:

1. Exact 5/46/0 Phase 2C catalog.
2. No views and empty mart schema.
3. All original Phase 2A rows remain unchanged by PK and canonical hash.
4. All original Phase 2B rows remain unchanged by PK and canonical hash.
5. A distinct Phase 2C release exists.
6. Phase 2A recognizes the exact Phase 2C upgrade before writes.
7. Phase 2B schema deployment recognizes the exact Phase 2C upgrade before
   writes.
8. Phase 2B historical ingestion remains operational against the exact
   additive Phase 2C catalog.
9. Unknown 5/46/0 catalogs are rejected.
10. Zero snapshots return `PHASE2C_SOURCE_NOT_READY` without mutation.
11. One snapshot returns `PHASE2C_SOURCE_NOT_READY` without mutation.
12. Simulated snapshot pairs are `NOT_ELIGIBLE`.
13. Reversed or equal snapshot dates are rejected.
14. Source-system and identity-grain mismatches are rejected.
15. Unsupported state fields return `PHASE2C_SCOPE_VIOLATION`.
16. Exactly 24 quality controls execute.
17. Exactly four readiness results are persisted.
18. Every activation status is `DISABLED_PENDING_FUTURE_PHASE`.
19. Exactly ten reconciliations execute.
20. Required independent lineage is complete.
21. Exact repeat evaluation is idempotent.
22. Conflicting pair evidence is rejected.
23. No transition matrix, state-pair count, probability, view, mart, or
    analytical artifact is produced.
24. Safe entry points never propagate exceptions.
25. Current warehouse and scored portfolio hashes remain unchanged.
26. Dynamic protected inventory remains unchanged.
27. File rollback restores the exact pre-Phase 2C database SHA-256 and
    5/36/0 catalog.
28. Phase 2A and Phase 2B test suites pass.
29. Existing compatibility suites pass with no new failures.

Isolated test fixtures may contain source-supplied observed snapshots solely
to verify controls. Tests must not write those fixtures into the published
production temporal database.

## 23. Rollback and Independent Removability

Rollback is file-based only.

Before every Phase 2C schema deployment or readiness publication:

1. close all temporal connections;
2. capture the published database hash;
3. create a fresh backup;
4. verify backup and published hashes match;
5. record the exact catalog and all Phase 2A/2B row hashes.

Rollback must:

1. restore the verified pre-operation database through atomic replacement;
2. verify the exact pre-operation SHA-256;
3. verify the 5/36/0 Phase 2B catalog;
4. verify Phase 2A and Phase 2B row hashes;
5. run Phase 2A and Phase 2B tests.

Complete Phase 2C removal requires:

1. restore the verified pre-Phase 2C database;
2. delete `src/temporal_risk/migration_readiness/`;
3. delete `sql/phase2c/`;
4. delete Phase 2C tests and implementation documentation;
5. delete `temporal_platform/evidence/phase2c/`;
6. revert only the approved Phase 2A/2B upgrade-guard changes.

After removal, the temporal database must be exactly 5 schemas, 36 tables,
zero views, and zero mart objects. Phase 2A, Phase 2B, and KRONOS startup must
remain operational.

## 24. Risks and Safeguards

### High: Exact-Catalog Compatibility

Current Phase 2A and Phase 2B code expects the 36-table catalog. Deploying
Phase 2C without approved upgrade guards would block Phase 2B ingestion.

Safeguard: formally audit exact 46-table recognition and test Phase 2B
ingestion after upgrade.

### High: Analytics Leakage

Identity overlap and state availability can easily drift into a migration
matrix.

Safeguard: prohibit from-state, to-state, transition count, probability,
direction, and analytical output fields in code, SQL, tests, and evidence.

### High: False Production Readiness

The current database has no historical snapshots.

Safeguard: return `PHASE2C_SOURCE_NOT_READY` before any writable operation.
Do not create a synthetic pair or production readiness result.

### Medium: Shared Release Registry

Phase 2C must append a release without changing Phase 2A or Phase 2B rows.

Safeguard: dedicated registrar plus pre/post canonical row hashes.

### Medium: State-Domain Incompatibility

Two snapshots may use differently defined grades or bands.

Safeguard: require an identical controlled state-domain contract before
readiness can pass.

### Medium: Removal Dependency

The shared temporal database cannot be cleaned safely through ad hoc drop
statements.

Safeguard: file-based backup restoration before deleting Phase 2C code or
evidence.

## 25. Formal Pre-Implementation Audit Requirements

The audit must verify:

- Phase 2A status is accepted.
- Phase 2B status is accepted.
- Current 5/36/0 catalog and zero-snapshot state.
- Exact ten-table extension has no naming or schema conflicts.
- No existing table requires redesign.
- Phase 2A and Phase 2B upgrade-guard changes are sufficient and minimal.
- Phase 2B ingestion remains usable after the 46-table upgrade.
- Existing rows can be preserved by primary key and canonical row hash.
- The 24 quality controls are implementable from current Phase 2B evidence.
- The ten reconciliations are non-analytical.
- The lineage design does not imply transition analytics.
- Simulated evidence cannot become observed migration evidence.
- The protected-hash boundary is correct.
- Full file rollback to 5/36/0 is feasible.
- Independent removability remains valid.
- No application, dashboard, warehouse, Phase 4, or SAS dependency exists.

Audit classification must be exactly one of:

```text
APPROVED
APPROVED_WITH_CHANGES
REJECTED
```

## 26. Definition of Completion

Phase 2C is complete only when:

- the exact 5/46/0 catalog is deployed;
- mart remains empty;
- all Phase 2A and Phase 2B rows are preserved;
- Phase 2A and Phase 2B remain operational against the upgraded catalog;
- the Phase 2C release and contract are distinct and governed;
- readiness evaluation requires two qualifying observed snapshots;
- simulated snapshots remain ineligible;
- exactly 24 quality controls, four readiness results, and ten
  reconciliations are enforced for an eligible pair;
- every activation status remains disabled;
- independent Phase 2C lineage is complete;
- no migration matrix, transition probability, roll rate, vintage, true OOT,
  IFRS9 calculation, view, mart, dashboard, application, current warehouse,
  Phase 4, or SAS integration exists;
- protected hashes and authoritative external assets remain unchanged;
- rollback restores the exact pre-Phase 2C database and 5/36/0 catalog;
- all Phase 2A, Phase 2B, Phase 2C, compatibility, protected-hash, and rollback
  tests pass without new failures.

Architecture completion does not mean production migration readiness. With the
current zero-snapshot population, the production status remains:

```text
PHASE2C_SOURCE_NOT_READY
```

## 27. Implementation Authorization Gate

Implementation must not begin until a formal pre-implementation audit confirms:

```text
PHASE2A_STATUS = ACCEPTED
PHASE2B_STATUS = ACCEPTED
PHASE2C_PLAN_STATUS = APPROVED or APPROVED_WITH_CHANGES
CURRENT_CATALOG = EXACT_5_36_0
ANALYTICAL_SCOPE_ENABLED = false
ROLLBACK_VERIFIED = true
```

Failure of any condition must stop implementation.
