# KRONOS Phase 2C Final Implementation Specification

## 1. Authority and Status

This document is the controlling implementation specification for:

```text
PHASE 2C - GOVERNED MIGRATION-TRANSITION READINESS
```

It uses `PHASE2C_IMPLEMENTATION_PLAN.md` as its architectural base and
incorporates every required correction from the Phase 2C pre-implementation
audit.

This specification supersedes any conflicting Phase 2C planning language.
Where this document differs from the planning document, this document is
authoritative.

Implementation remains subject to a final audit or explicit implementation
authorization.

## 2. Accepted Baseline

Accepted phase status:

```text
Phase 2A = ACCEPTED
Phase 2B = ACCEPTED
```

Published temporal database:

```text
temporal_platform/warehouse/kronos_temporal_risk.duckdb
```

Required pre-Phase 2C catalog:

```text
Schemas:      5
Tables:      36
Views:        0
Mart objects: 0
```

Current production historical population:

```text
Historical snapshots:      0
Historical observations:   0
Historical ingestion runs: 0
Readiness results:          0
```

The current production readiness status is:

```text
PHASE2C_SOURCE_NOT_READY
```

This status must remain until at least two qualifying source-supplied observed
snapshots have been published through Phase 2B.

## 3. Objective

Phase 2C extends the isolated temporal platform with migration-transition
readiness governance only.

Phase 2C may:

- validate a governed pair of historical snapshots;
- verify source-supplied chronological continuity;
- verify persistent source-supplied identity;
- verify source-supplied state-field continuity;
- register controlled readiness and state-domain contracts;
- execute readiness data-quality controls;
- persist non-analytical pair-governance evidence;
- execute pair-level reconciliations;
- persist independent Phase 2C lineage;
- calculate a governance control-completeness score;
- publish migration-readiness evidence with analytical activation disabled.

Phase 2C determines whether inputs are ready for a separately authorized
future migration-analytics phase. It does not create migration analytics.

## 4. Implementation Boundary

Phase 2C must not implement, calculate, generate, infer, persist, display, or
publish:

- migration matrices;
- state transitions;
- transition tables;
- transition direction;
- transition counts;
- transition probabilities;
- upgrade classification;
- downgrade classification;
- cure classification;
- deterioration classification;
- roll rates;
- vintage cohorts or curves;
- cumulative default curves;
- true OOT validation;
- model training;
- model scoring;
- model recalibration;
- model replacement;
- IFRS9 calculations;
- IFRS9 staging;
- SICR;
- contractual cash-flow discounting;
- scenario weighting;
- ECL;
- provisions;
- reserves;
- dashboards;
- application integration;
- current KRONOS warehouse integration;
- Phase 4 integration;
- SAS-style analytics integration;
- views;
- marts;
- facts;
- dimensions;
- generated historical evidence;
- generated state evidence;
- generated transition evidence;
- generated dates;
- generated identities;
- generated events.

Any requested or attempted prohibited capability must stop with:

```text
PHASE2C_SCOPE_VIOLATION
```

## 5. Explicit Prohibited Transition Fields

The following exact field names are prohibited:

```text
from_state
to_state
state_pair
transition_pair
transition_count
transition_probability
migration_matrix_cell
```

They must not appear as persisted or returned data fields in:

- SQL assets;
- database tables or columns;
- constraints or indexes;
- evidence files;
- lineage nodes, edges, or column mappings;
- reconciliation records;
- readiness records;
- runtime payloads;
- logs intended as governed evidence;
- exported files;
- completion artifacts.

Descriptive prose in controlled specifications and scope tests may mention
these names only to verify that their persistence is prohibited.

## 6. Preserved Platforms

The following must remain unchanged:

- `data/warehouse/kronos_risk.duckdb`;
- `data/processed/scored_portfolio.csv`;
- `app/`;
- `src/enterprise_data/`;
- Phase 1 and Phase 1.5 assets;
- Phase 4A through Phase 4E assets;
- model artifacts;
- scoring logic;
- model-validation logic;
- reporting logic;
- credit-risk, provisioning, IFRS9, EWS, stress, contagion, and decision
  engines;
- all existing Phase 2A database rows;
- all existing Phase 2B database rows;
- all Phase 2A and Phase 2B release rows;
- all Phase 2A and Phase 2B DQ evidence;
- all Phase 2A and Phase 2B reconciliation evidence;
- all Phase 2A and Phase 2B lineage evidence;
- all Phase 2B historical dimensions and facts.

Phase 2C failure must never affect KRONOS startup or any accepted phase.

## 7. Runtime Architecture

Phase 2C may use only:

```text
temporal_platform/
|-- warehouse/
|   `-- kronos_temporal_risk.duckdb
|-- backups/
`-- evidence/
    `-- phase2c/
        `-- <deployment_or_readiness_run_id>/
```

Phase 2C must not create an inbound source path. It consumes only already
published Phase 2B snapshot, mapping, source, and observation evidence.

No Phase 2C runtime file may be written under:

- `data/`;
- `models/`;
- `outputs/`;
- `reports/`;
- `analytics/`.

## 8. Final Authored File Inventory

### 8.1 New Runtime Package

Create:

```text
src/temporal_risk/migration_readiness/
|-- __init__.py
|-- config.py
|-- contracts.py
|-- source_catalog.py
|-- pair_selector.py
|-- continuity.py
|-- state_validation.py
|-- data_quality.py
|-- reconciliation.py
|-- lineage.py
|-- release_registry.py
|-- publisher.py
`-- pipeline.py
```

### 8.2 SQL Assets

Create:

```text
sql/phase2c/ddl/
|-- 001_migration_control_tables.sql
`-- 002_migration_lineage_tables.sql
```

No rollback SQL may be created. Rollback is file-based only.

### 8.3 Tests

Create:

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

### 8.4 Documentation

Create:

```text
docs/PHASE2C_COMPLETION_REPORT.md
docs/MIGRATION_READINESS_ARCHITECTURE.md
docs/MIGRATION_READINESS_CONTRACT.md
docs/MIGRATION_READINESS_DATA_DICTIONARY.md
docs/MIGRATION_READINESS_OPERATIONS.md
```

## 9. Authorized Existing-File Modifications

Modify only as required for exact catalog recognition:

```text
src/temporal_risk/pipeline.py
src/temporal_risk/historical_ingestion/config.py
src/temporal_risk/historical_ingestion/contracts.py
src/temporal_risk/historical_ingestion/pipeline.py
```

The only permitted purposes are:

1. Phase 2A exact recognition of Phase 2B and Phase 2C upgrade catalogs.
2. Phase 2B exact recognition of the Phase 2C upgrade catalog.
3. Phase 2B ingestion compatibility with an exact Phase 2C catalog.
4. Addition of the governed `PHASE2B_UPGRADE_PRESENT` status.

No existing Phase 2A or Phase 2B table, contract, DQ rule, reconciliation,
lineage, release, ingestion, idempotency, publication, or rollback behavior
may otherwise be redesigned.

Phase 2A and Phase 2B must not import the Phase 2C package.

## 10. Final Database Extension

Retain exactly these schemas:

- `control`
- `staging`
- `reference`
- `core`
- `mart`

Create exactly ten additive base tables:

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

Required post-deployment catalog:

```text
Schemas:      5
Tables:      46
Views:        0
Mart objects: 0
```

No staging, reference, core, or mart object may be added. No existing object
may be altered, dropped, replaced, truncated, renamed, or redefined.

## 11. Final Table Definitions

### 11.1 `control.migration_readiness_run`

Grain:

```text
one Phase 2C schema deployment or snapshot-pair readiness evaluation
```

Required attributes:

- readiness run ID;
- Phase 2C release ID;
- run type;
- start and end timestamps;
- lifecycle status;
- earlier snapshot ID;
- later snapshot ID;
- state field;
- readiness contract ID and version;
- readiness contract hash;
- state-domain contract ID and version;
- state-domain contract hash;
- applicable controls;
- passed applicable controls;
- governance score;
- quality status;
- readiness status;
- activation status;
- pre-operation database hash;
- working database hash;
- published database hash;
- error class;
- error message.

### 11.2 `control.migration_snapshot_pair`

Grain:

```text
one governed earlier/later snapshot pair per state field and contract set
```

Required attributes:

- pair ID;
- readiness run ID;
- earlier and later snapshot IDs;
- earlier and later snapshot dates;
- source system;
- identity grain;
- history mode;
- evidence classification;
- state field;
- readiness contract ID, version, and hash;
- state-domain contract ID, version, and hash;
- earlier and later source hashes;
- earlier and later population counts;
- overlapping identity count;
- earlier and later state-complete overlap counts;
- earlier and later state-missing overlap counts;
- identity continuity status;
- state continuity status;
- eligibility status.

This table must contain no transition-level record and none of the prohibited
transition fields.

### 11.3 `control.migration_transition_contract`

Grain:

```text
one controlled readiness or state-domain contract version
```

Required attributes:

- contract ID;
- contract type;
- contract name;
- contract version;
- supported history mode;
- supported evidence classification;
- permitted identity grains;
- state field where applicable;
- ordered allowed values where applicable;
- required source provenance;
- prohibited capabilities;
- contract definition JSON;
- contract hash;
- status;
- created timestamp.

Required contract types:

1. `MIGRATION_READINESS`
2. `RISK_GRADE_DOMAIN`
3. `RISK_BAND_DOMAIN`

Required readiness contract:

```text
MIGRATION_TRANSITION_READINESS_V1
```

Required state-domain contract names:

```text
RISK_GRADE_DOMAIN_V1
RISK_BAND_DOMAIN_V1
```

The state-domain contract definitions must be controlled specification
content. Their allowed values must not be discovered or inferred from
snapshot values.

### 11.4 `control.migration_quality_result`

Grain:

```text
one critical quality control per readiness run and snapshot pair
```

Required attributes:

- quality result ID;
- readiness run ID;
- pair ID;
- control name;
- control category;
- critical flag;
- applicable flag;
- earlier value;
- later value;
- expected value;
- status;
- details;
- evaluation timestamp.

### 11.5 `control.migration_readiness_result`

Grain:

```text
one readiness capability result per readiness run and snapshot pair
```

Create exactly four results:

1. `SNAPSHOT_CONTINUITY`
2. `IDENTITY_CONTINUITY`
3. `STATE_FIELD_CONTINUITY`
4. `MIGRATION_TRANSITION_INPUTS`

Required attributes:

- readiness result ID;
- readiness run ID;
- pair ID;
- capability name;
- data status;
- activation status;
- applicable controls;
- passed applicable controls;
- governance score;
- required evidence;
- available evidence;
- missing evidence;
- reason;
- evaluation timestamp.

### 11.6 `control.migration_reconciliation_result`

Grain:

```text
one non-analytical reconciliation control per readiness run and pair
```

Required attributes:

- reconciliation result ID;
- readiness run ID;
- pair ID;
- reconciliation name;
- earlier value;
- later value;
- expected value;
- difference;
- tolerance;
- status;
- details;
- reconciliation timestamp.

The table must not contain state-pair or transition-level values.

### 11.7 `control.migration_lineage_node`

Store Phase 2C lineage nodes only.

Required attributes:

- lineage node ID;
- readiness run ID;
- node type;
- node name;
- governed object identifier;
- object hash;
- created timestamp.

### 11.8 `control.migration_lineage_edge`

Store Phase 2C lineage edges only.

Required attributes:

- lineage edge ID;
- readiness run ID;
- upstream node ID;
- downstream node ID;
- governance relationship;
- created timestamp.

No edge may describe or imply a calculated transition.

### 11.9 `control.migration_column_lineage`

Store source-to-governance-evidence lineage only.

Required attributes:

- column-lineage ID;
- readiness run ID;
- snapshot ID;
- source asset ID;
- source column;
- canonical field;
- governance target;
- transformation type;
- provenance classification;
- created timestamp.

Allowed transformation types are limited to:

- source mapping reference;
- safe datatype interpretation;
- null-presence validation;
- controlled-domain membership validation.

No state normalization or transition derivation is permitted.

### 11.10 `control.migration_publish_status`

Allowed lifecycle:

```text
DRAFT -> VALIDATED -> PUBLISHED
```

Required attributes:

- publish status ID;
- readiness run ID;
- target name;
- previous status;
- new status;
- transition timestamp;
- details.

Only a `READY_BUT_DISABLED` result that passes every critical control and
reconciliation may be published as migration-ready.

## 12. PHASE2C_AUDIT_CORRECTIONS

### 12.1 Governance Score Formula

The governance score is a control-completeness score only.

It must be calculated exactly as:

```text
governance_score =
ROUND(
    100.0 * passed_applicable_controls /
    applicable_controls,
    2
)
```

The rounding mode must be deterministic decimal rounding to two places using
half-up behavior.

The following rules apply:

- `passed_applicable_controls` counts controls with status `PASS` and
  `applicable_flag = true`;
- `applicable_controls` counts controls with `applicable_flag = true`;
- failed applicable controls remain in the denominator;
- non-applicable controls are excluded from numerator and denominator;
- the score is not a model output;
- the score is not a credit score;
- the score is not a transition score;
- the score is not a migration probability;
- the score must not be used for ranking borrowers, facilities, states, or
  transition outcomes.

### 12.2 Divide-by-Zero Behavior

If:

```text
applicable_controls = 0
```

then:

```text
governance_score = NULL
readiness_status = FAILED
publication prohibited
```

No default score, zero score, or imputed score may be substituted.

### 12.3 Deterministic Pair Selection

Explicit snapshot IDs are required for ordinary readiness evaluation:

```text
earlier_snapshot_id
later_snapshot_id
```

The supplied IDs must be distinct, eligible, and chronologically ordered.

Automatic pair selection is optional and may run only when the request
explicitly supplies:

- one source system;
- one identity grain;
- one state field.

Automatic selection must:

1. restrict candidates to published, eligible `OBSERVED_TEMPORAL` and
   `OBSERVED_SOURCE` snapshots;
2. restrict candidates to the same source system;
3. restrict candidates to the same identity grain;
4. require the same requested state field and controlled domain contract;
5. select the earliest eligible snapshot date as the earlier snapshot;
6. select the latest eligible snapshot date as the later snapshot;
7. order snapshots sharing a date by `snapshot_id` ascending.

If more than one candidate remains valid for either boundary date after the
required `snapshot_id` ordering, automatic selection must not silently choose
one. It must return:

```text
PHASE2C_PAIR_CONFLICT
```

Automatic selection must also return `PHASE2C_PAIR_CONFLICT` when evidence
cannot prove one deterministic pair.

### 12.4 Explicit Prohibited Transition Fields

Persistence or return of these exact fields is prohibited:

```text
from_state
to_state
state_pair
transition_pair
transition_count
transition_probability
migration_matrix_cell
```

The prohibition applies to SQL, tables, evidence, lineage, reconciliations,
readiness outputs, and runtime payloads.

### 12.5 Contract-Hash Conflict Policy

The idempotency decision must compare both version and hash for:

- the Phase 2C readiness contract;
- the selected state-domain contract.

The following condition must return:

```text
same contract version
different contract hash
=> PHASE2C_PAIR_CONFLICT
```

This conflict must be detected before idempotency evaluation.

A changed readiness-contract hash or state-domain-contract hash must never be
treated as an exact repeat.

### 12.6 Complete Release-Recognition Matrix

Every recognition branch must use:

- exact schema inventory;
- exact table inventory;
- exact view inventory;
- zero mart objects;
- required published release rows;
- no unexpected object.

Counts alone are prohibited.

| Caller | Exact 17-Table Catalog | Exact 36-Table Catalog | Exact 46-Table Catalog |
|---|---|---|---|
| Phase 2A | Normal Phase 2A behavior | `PHASE2A_UPGRADE_PRESENT` | `PHASE2A_UPGRADE_PRESENT` |
| Phase 2B deployment | Not a Phase 2B idempotent state; existing Phase 2B deployment rules apply | Normal/idempotent Phase 2B behavior | `PHASE2B_UPGRADE_PRESENT` |
| Phase 2B ingestion | Not allowed; Phase 2B schema is not deployed | Allowed | Allowed |
| Phase 2C deployment | Reject as missing accepted Phase 2B baseline | Eligible Phase 2C baseline | `PHASE2C_SCHEMA_READY` |
| Phase 2C evaluation | Reject | Reject as Phase 2C not deployed | Allowed |

For clarity, Phase 2B deployment from an exact accepted 17-table Phase 2A
catalog remains governed by the accepted Phase 2B specification. The Phase 2C
change must not alter that deployment path.

An unknown 17-, 36-, or 46-table catalog must be rejected even when counts
match.

### 12.7 Corrected Rollback Targets

Schema deployment rollback:

```text
restore exact pre-deployment SHA-256
restore exact 5/36/0 catalog
restore all pre-deployment Phase 2A and Phase 2B row hashes
```

Readiness-run rollback:

```text
restore exact pre-run SHA-256
restore exact 5/46/0 catalog
restore all pre-run Phase 2A, Phase 2B, and existing Phase 2C row hashes
```

Full Phase 2C removal:

```text
restore verified pre-Phase 2C database
restore exact 5/36/0 catalog
remove Phase 2C authored and runtime assets
revert only Phase 2C catalog-recognition changes
```

No readiness-run rollback may restore a 5/36/0 database unless the run being
rolled back was the schema deployment itself.

### 12.8 State-Domain Governance Rules

Phase 2B does not persist formal risk-grade or risk-band domain definitions.
Phase 2C must not claim otherwise.

Phase 2C must register and govern:

- versioned risk-grade domain contracts;
- versioned risk-band domain contracts.

Each readiness evaluation must select exactly one state field:

- `risk_grade`; or
- `risk_band`.

Both snapshots must validate against the same state-domain contract ID,
version, and hash.

Domain values must come from controlled Phase 2C specification content. They
must not be inferred from:

- distinct snapshot values;
- the union or intersection of snapshot values;
- current scored-portfolio values;
- current warehouse dimensions;
- application code;
- model scoring logic;
- alphabetical ordering;
- observed frequency;
- ordinal assumptions.

Phase 2C must not:

- normalize a state;
- map aliases;
- trim or rewrite a governed state value beyond safe datatype interpretation;
- generate a missing state;
- assign an ordinal rank;
- infer severity;
- infer direction;
- infer a transition.

An unrecognized value must fail the applicable critical quality control.

### 12.9 Quality-Control Criticality Rules

All 24 Phase 2C quality controls are critical for
`READY_BUT_DISABLED` eligibility.

For an evaluated pair:

- every control must be recorded;
- every control must be applicable;
- every control must pass;
- `applicable_controls` must equal 24;
- `passed_applicable_controls` must equal 24;
- `governance_score` must equal `100.00`.

Any failed or non-applicable control prohibits `READY_BUT_DISABLED`.

The result must instead be:

- `NOT_READY` for insufficient or incomplete observed evidence;
- `NOT_ELIGIBLE` for prohibited evidence classes such as simulated history;
- `FAILED` for control execution or integrity failure.

Critical failures prohibit publication as migration-ready.

## 13. Snapshot-Pair Eligibility

A pair is eligible only when:

1. both snapshot IDs are present in `core.dim_historical_snapshot`;
2. both snapshots have valid Phase 2B publication evidence;
3. snapshot IDs are distinct;
4. both snapshot dates are source supplied;
5. earlier snapshot date precedes later snapshot date;
6. both snapshots use `OBSERVED_TEMPORAL`;
7. both snapshots use `OBSERVED_SOURCE`;
8. both snapshots use the same source system;
9. both snapshots use the same identity grain;
10. source-supplied identity overlaps across snapshots;
11. the selected state field is `risk_grade` or `risk_band`;
12. the state field is explicitly mapped and source supplied in both
    snapshots;
13. both snapshots validate against the same controlled state-domain contract;
14. source and mapping hashes remain consistent with Phase 2B evidence;
15. all 24 critical quality controls pass;
16. all ten reconciliations pass.

Simulated snapshots must return:

```text
PHASE2C_SOURCE_NOT_ELIGIBLE
```

Their readiness data status must be:

```text
NOT_ELIGIBLE
```

No simulated snapshot may support an observed migration-readiness claim.

## 14. Mandatory Data-Quality Framework

Run exactly 24 controls per evaluated snapshot pair.

### Platform and Release

1. Exact recognized Phase 2C catalog.
2. Published Phase 2A release exists.
3. Published Phase 2B release exists.
4. Mart is empty and no views exist.

### Snapshot Governance

5. Earlier snapshot exists.
6. Later snapshot exists.
7. Snapshot IDs are distinct.
8. Earlier snapshot date precedes later snapshot date.
9. Both snapshots have valid Phase 2B publication evidence.
10. Both snapshots are `OBSERVED_TEMPORAL`.
11. Both snapshots are `OBSERVED_SOURCE`.
12. Both snapshots have immutable registered source hashes.

### Identity Continuity

13. Source system matches.
14. Identity grain matches.
15. Earlier identity keys are non-null.
16. Later identity keys are non-null.
17. Earlier identity grain is unique within its snapshot.
18. Later identity grain is unique within its snapshot.
19. At least one identity overlaps.

### State-Field Continuity

20. State field is contract-allowlisted.
21. Earlier state mapping exists and is source supplied.
22. Later state mapping exists and is source supplied.
23. Both snapshots use the same controlled state-domain contract ID, version,
    and hash.
24. Every overlapping identity has a non-null, controlled-domain state value
    in both snapshots.

All controls are critical and must follow Section 12.9.

Control 24 validates state completeness and domain membership only. It must
not compare one state value to another or persist any paired state values.

## 15. Readiness Framework

Create exactly four readiness results:

- `SNAPSHOT_CONTINUITY`
- `IDENTITY_CONTINUITY`
- `STATE_FIELD_CONTINUITY`
- `MIGRATION_TRANSITION_INPUTS`

Every result must set:

```text
activation_status = DISABLED_PENDING_FUTURE_PHASE
```

Allowed data statuses:

- `READY_BUT_DISABLED`
- `NOT_READY`
- `NOT_ELIGIBLE`
- `FAILED`

`READY_BUT_DISABLED` requires:

- all 24 controls applicable;
- all 24 controls passed;
- governance score `100.00`;
- all ten reconciliations passed;
- complete Phase 2C lineage;
- no scope violation.

No readiness result activates analytics.

## 16. Mandatory Reconciliation Framework

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

No reconciliation may persist:

- paired state values;
- state combinations;
- transition classifications;
- transition-level counts;
- transition probabilities;
- migration matrix content.

All ten reconciliations must pass for `READY_BUT_DISABLED`.

## 17. Independent Lineage Framework

Write only to:

- `control.migration_lineage_node`;
- `control.migration_lineage_edge`;
- `control.migration_column_lineage`.

Do not write to:

- Phase 2A lineage tables;
- Phase 2B historical lineage tables;
- Phase 4 lineage tables.

Required nodes:

1. Phase 2C readiness contract.
2. Selected state-domain contract.
3. Earlier historical snapshot.
4. Later historical snapshot.
5. Earlier identity mapping.
6. Later identity mapping.
7. Earlier state mapping.
8. Later state mapping.
9. Continuity control evidence.
10. Published readiness run.

Required edges:

1. Readiness contract governs continuity evidence.
2. State-domain contract governs earlier state validation.
3. State-domain contract governs later state validation.
4. Earlier snapshot supplies earlier identity mapping.
5. Later snapshot supplies later identity mapping.
6. Earlier snapshot supplies earlier state mapping.
7. Later snapshot supplies later state mapping.
8. Earlier identity mapping supports continuity evidence.
9. Later identity mapping supports continuity evidence.
10. Earlier state mapping supports continuity evidence.
11. Later state mapping supports continuity evidence.
12. Continuity evidence authorizes the published readiness run.

Required column lineage:

- earlier identity source column;
- later identity source column;
- earlier snapshot-date source column;
- later snapshot-date source column;
- earlier state source column;
- later state source column.

Lineage must describe provenance and validation only. It must not imply an
analytical transition.

## 18. Idempotency and Conflict Policy

The idempotency key consists of:

```text
earlier_snapshot_id
+ later_snapshot_id
+ state_field
+ readiness_contract_version
+ readiness_contract_hash
+ state_domain_contract_version
+ state_domain_contract_hash
+ earlier_source_hash
+ later_source_hash
```

Before checking for an exact repeat, detect:

1. same readiness contract version with a different readiness contract hash;
2. same state-domain contract version with a different state-domain contract
   hash;
3. same governed pair and state field with changed source evidence.

Any such condition returns:

```text
PHASE2C_PAIR_CONFLICT
```

An exact published match returns:

```text
SKIPPED_ALREADY_PUBLISHED
```

It must add no duplicate run, pair, quality, readiness, reconciliation,
lineage, or publish records.

Published Phase 2C evidence must not be overwritten or superseded.

## 19. Dedicated Phase 2C Release Registration

Implement a dedicated Phase 2C release registrar.

Required release attributes:

```text
phase_name = PHASE2C
release_version = governed Phase 2C version
schema_count = 5
table_count = 46
view_count = 0
status = DRAFT, then PUBLISHED
```

The registrar must:

- use a deterministic Phase 2C release ID;
- insert or update only that Phase 2C primary key;
- never call Phase 2A or Phase 2B release registration;
- preserve Phase 2A and Phase 2B release rows by canonical row hash;
- preserve every existing Phase 2A and Phase 2B row;
- record controlled Phase 2C specification hashes;
- validate exact catalog recognition before publication.

## 20. Safe Entry Points and Statuses

Provide:

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
- `PHASE2B_UPGRADE_PRESENT`
- `SKIPPED_ALREADY_PUBLISHED`

No exception may propagate into KRONOS, Phase 2A, Phase 2B, application, or
Phase 4 callers.

## 21. Production No-Data Preflight

Before Phase 2C readiness evaluation creates:

- a readiness run ID;
- an evidence directory;
- an evidence file;
- a backup;
- a working database;
- a writable connection;

it must inspect the published temporal database read-only.

If fewer than two qualifying observed snapshots exist, return:

```text
PHASE2C_SOURCE_NOT_READY
```

This return must occur before any filesystem or database mutation.

No synthetic pair, simulated substitute, fabricated readiness row, or
placeholder evidence may be created.

## 22. Protected Hash Boundary

Protected verification must use dynamic SHA-256 inventories. Git state must
not be required.

Protect:

- all existing KRONOS authored assets;
- `app/`;
- `src/enterprise_data/`;
- all model and risk-engine code;
- `models/`;
- `data/`;
- `outputs/`;
- `reports/`;
- `analytics/`;
- current warehouse;
- scored portfolio;
- all unaffected Phase 2A and Phase 2B code, SQL, tests, and documentation;
- all pre-existing Phase 2A and Phase 2B database rows.

Authorize only:

- `src/temporal_risk/migration_readiness/`;
- `sql/phase2c/`;
- `tests/test_phase2c_*.py`;
- Phase 2C documentation;
- the four approved catalog-recognition files in Section 9;
- `temporal_platform/evidence/phase2c/`;
- `temporal_platform/backups/`;
- the isolated temporal database during an authorized operation.

Retain exactly these accepted volatile-file exclusions:

```text
data/live/live_intelligence_cache.json
outputs/artifact_lineage.json
reports/test_kronos_enterprise_report.pdf
```

No parent directory or broader path may be excluded.

The current warehouse and scored portfolio require independent direct
before-and-after SHA-256 equality.

## 23. Preservation Framework

Before schema deployment and before every writable readiness evaluation:

1. capture every existing Phase 2A and Phase 2B table definition;
2. capture every existing row by primary key;
3. calculate a canonical row hash for every captured row;
4. capture Phase 2A and Phase 2B release-row hashes;
5. capture all existing DQ, reconciliation, and lineage row hashes.

After publication:

- every pre-existing primary key must remain present;
- every canonical row hash must remain identical;
- no pre-existing Phase 2A or Phase 2B row may be updated or deleted;
- shared-table counts may increase only through the distinct Phase 2C release
  row where authorized.

Any mismatch returns:

```text
PHASE2C_BASELINE_MISMATCH
```

and prohibits publication.

## 24. Schema Deployment Workflow

1. Verify accepted Phase 2A and Phase 2B evidence.
2. Validate controlled Phase 2C specifications.
3. Validate the exact 5/36/0 baseline catalog.
4. Validate published Phase 2A and Phase 2B releases.
5. Capture temporal database, current warehouse, scored-portfolio, protected
   inventory, and row-hash baselines.
6. Validate target and evidence paths before writes.
7. Close all temporal database connections.
8. Create and hash-verify a fresh pre-deployment backup.
9. Copy the temporal database to a working location.
10. Apply only the two Phase 2C DDL assets.
11. Register the readiness and two state-domain contract records.
12. Validate the exact 5/46/0 catalog.
13. Verify zero views and zero mart objects.
14. Verify every Phase 2A and Phase 2B row by PK and hash.
15. Register the distinct Phase 2C release as `DRAFT`.
16. Record `DRAFT`, `VALIDATED`, and `PUBLISHED` deployment transitions.
17. Publish the Phase 2C release.
18. Publish only the closed, validated working database.
19. Reopen the published database read-only.
20. Repeat catalog, release, preservation, and protected-hash checks.
21. Write Phase 2C deployment evidence.

Schema deployment must not evaluate or publish a snapshot pair.

## 25. Readiness Evaluation Workflow

1. Validate requested capability and state field.
2. Open the exact published temporal database read-only.
3. Validate exact 5/46/0 recognition and published releases.
4. Validate explicit snapshot IDs or execute the governed automatic-selection
   rules.
5. Return `PHASE2C_SOURCE_NOT_READY` before writes when qualifying evidence is
   insufficient.
6. Return `PHASE2C_SOURCE_NOT_ELIGIBLE` before writes for simulated or
   prohibited evidence.
7. Detect contract-hash and pair conflicts before idempotency.
8. Return `SKIPPED_ALREADY_PUBLISHED` for an exact published match.
9. Capture database, row, external-asset, and protected baselines.
10. Close read-only connections.
11. Create and verify a fresh pre-run backup.
12. Copy the database to a working location.
13. Register the readiness run and snapshot pair.
14. Execute exactly 24 critical quality controls.
15. Calculate governance score according to Section 12.
16. Persist exactly four readiness results with activation disabled.
17. Execute exactly ten reconciliations.
18. Build independent Phase 2C lineage.
19. Verify prohibited transition fields and analytical objects are absent.
20. Verify all pre-existing Phase 2A, Phase 2B, and Phase 2C rows.
21. Record `DRAFT`, `VALIDATED`, and `PUBLISHED` where eligible.
22. Publish only the closed, validated working database.
23. Reopen read-only and repeat catalog, row, evidence, and hash checks.
24. Write readiness-run evidence.

## 26. Expected Row-Count Contracts

### 26.1 Schema Deployment

Expected additions:

| Object | Rows Added |
|---|---:|
| Phase 2C release | 1 |
| Readiness contract | 1 |
| Risk-grade domain contract | 1 |
| Risk-band domain contract | 1 |
| Schema deployment run | 1 |
| Schema deployment publish transitions | 3 |
| Other Phase 2C tables | 0 |
| Historical facts | 0 |
| Transition records | 0 |
| Views | 0 |
| Mart objects | 0 |

### 26.2 Successful Readiness Evaluation

Expected additions:

| Object | Rows Added |
|---|---:|
| Readiness run | 1 |
| Snapshot pair | 1 |
| Quality results | 24 |
| Readiness results | 4 |
| Reconciliation results | 10 |
| Lineage nodes | 10 |
| Lineage edges | 12 |
| Column lineage | 6 minimum; source-mapping driven |
| Publish transitions | 3 |
| Historical facts | 0 |
| Transition records | 0 |
| Analytical outputs | 0 |

With the current production population, no readiness-evaluation row may be
added. The safe result remains `PHASE2C_SOURCE_NOT_READY`.

## 27. Rollback and Independent Removability

Rollback is file-based only.

### 27.1 Schema Deployment Rollback

Restore:

- exact pre-deployment database SHA-256;
- exact 5/36/0 catalog;
- exact Phase 2A and Phase 2B row hashes.

### 27.2 Readiness-Run Rollback

Restore:

- exact pre-run database SHA-256;
- exact 5/46/0 catalog;
- exact Phase 2A, Phase 2B, and pre-existing Phase 2C row hashes.

### 27.3 Full Phase 2C Removal

1. Restore the verified pre-Phase 2C 5/36/0 database.
2. Delete `src/temporal_risk/migration_readiness/`.
3. Delete `sql/phase2c/`.
4. Delete Phase 2C tests and implementation documentation.
5. Delete `temporal_platform/evidence/phase2c/`.
6. Revert only the approved Phase 2A/2B catalog-recognition changes.
7. Verify Phase 2A and Phase 2B tests.
8. Verify KRONOS startup and completed phases remain unaffected.

The backup must be restored before deleting runtime paths containing required
rollback evidence.

## 28. Mandatory Test Requirements

Implementation must prove:

1. Exact 5/46/0 catalog.
2. Exact ten-table Phase 2C inventory.
3. No views and empty mart schema.
4. No table-name or schema conflict.
5. Complete exact-object release-recognition matrix.
6. Count-only catalog recognition is rejected.
7. Unknown 17-, 36-, and 46-table catalogs are rejected.
8. Phase 2A fresh 5/17/0 behavior remains valid.
9. Phase 2A returns `PHASE2A_UPGRADE_PRESENT` for exact 36 and 46 catalogs
   before writes.
10. Phase 2B deployment returns `PHASE2B_UPGRADE_PRESENT` for exact 46 before
    writes.
11. Phase 2B ingestion works against exact 36 and exact 46 catalogs.
12. Phase 2C deployment accepts exact 36 and is idempotent on exact 46.
13. Phase 2C evaluation accepts only exact 46.
14. Every pre-existing Phase 2A row is unchanged by PK and hash.
15. Every pre-existing Phase 2B row is unchanged by PK and hash.
16. Phase 2A and Phase 2B releases remain unchanged.
17. A distinct Phase 2C release exists.
18. Zero or one qualifying snapshot returns `PHASE2C_SOURCE_NOT_READY` before
    mutation.
19. Explicit snapshot IDs are enforced.
20. Automatic pair selection follows the deterministic rules.
21. Pair ambiguity returns `PHASE2C_PAIR_CONFLICT`.
22. Simulated snapshots are `NOT_ELIGIBLE`.
23. Source-supplied dates and chronological order are enforced.
24. Source-system and identity-grain continuity are enforced.
25. Risk-grade and risk-band domain contracts are controlled and versioned.
26. No domain inference or normalization occurs.
27. Same contract version with different hash returns
    `PHASE2C_PAIR_CONFLICT` before idempotency.
28. Exact idempotency key returns `SKIPPED_ALREADY_PUBLISHED`.
29. Exactly 24 quality controls execute.
30. All 24 controls are critical and applicable for `READY_BUT_DISABLED`.
31. Governance score uses the exact formula and half-up rounding.
32. Zero applicable controls produce NULL score, `FAILED`, and no publication.
33. Exactly four readiness results are created.
34. Every activation status is `DISABLED_PENDING_FUTURE_PHASE`.
35. Exactly ten reconciliations execute.
36. Exactly ten lineage nodes and twelve lineage edges exist.
37. Required column lineage is complete.
38. Phase 2A and Phase 2B lineage tables receive no Phase 2C rows.
39. Prohibited transition fields are absent from SQL, schema, evidence,
    lineage, reconciliation, readiness, and runtime payloads.
40. No transition matrix, probability, count, view, mart, fact, dimension, or
    analytical artifact exists.
41. Safe entry points do not propagate exceptions.
42. Dynamic protected inventory remains unchanged.
43. Only the three accepted volatile exact-file exclusions remain.
44. Current warehouse and scored portfolio hashes remain unchanged.
45. Schema rollback restores exact pre-deployment 5/36/0 and SHA-256.
46. Readiness-run rollback restores exact pre-run 5/46/0 and SHA-256.
47. Full removal restores exact 5/36/0.
48. Phase 2A tests pass.
49. Phase 2B tests pass.
50. Phase 2C tests pass.
51. Compatibility, protected-hash, and rollback tests pass.

Isolated test fixtures may use source-supplied observed snapshots. They must
not write test history into the published production temporal database.

## 29. Completion Criteria

Phase 2C is complete only when:

- the exact 5/46/0 catalog is deployed;
- all ten Phase 2C tables match this specification;
- mart remains empty and no views exist;
- all Phase 2A and Phase 2B rows are preserved;
- the complete release-recognition matrix is enforced;
- Phase 2B ingestion remains operational against the upgraded catalog;
- distinct readiness and domain contracts are governed;
- no state domain is inferred or normalized;
- explicit or deterministic snapshot-pair selection is enforced;
- exactly 24 critical controls execute;
- governance scoring follows the exact formula and failure behavior;
- exactly four readiness results and ten reconciliations are enforced;
- all activation statuses remain disabled;
- independent Phase 2C lineage is complete;
- contract-hash conflicts precede idempotency;
- every analytical and transition-field prohibition is enforced;
- protected hashes and authoritative external assets remain unchanged;
- schema rollback, readiness rollback, and full removal restore their exact
  required baselines;
- all Phase 2A, Phase 2B, Phase 2C, compatibility, protected-hash, and rollback
  tests pass without new failures.

Architecture completion does not imply production migration readiness.
Without two qualifying observed snapshots, production status remains:

```text
PHASE2C_SOURCE_NOT_READY
```

## 30. Implementation Authorization Gate

Implementation may begin only when:

```text
GOVERNING_SPECIFICATION = PHASE2C_IMPLEMENTATION_SPEC_FINAL.md
PHASE2A_STATUS = ACCEPTED
PHASE2B_STATUS = ACCEPTED
PHASE2C_FINAL_AUDIT = APPROVED
CURRENT_CATALOG = EXACT_5_36_0
ANALYTICAL_SCOPE_ENABLED = false
ROLLBACK_TARGETS_VERIFIED = true
```

Failure of any condition must stop implementation.
