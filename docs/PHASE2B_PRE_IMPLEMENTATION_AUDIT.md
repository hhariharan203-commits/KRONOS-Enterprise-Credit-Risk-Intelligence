# KRONOS Phase 2B Pre-Implementation Audit

## Final Classification

**APPROVED_WITH_CHANGES**

The Phase 2B plan is architecturally compatible with the isolated temporal
platform and correctly excludes analytical functionality. Implementation may
proceed only after the mandatory corrections in Section 5 are incorporated
into the implementation specification.

## 1. Evidence Reviewed

- `docs/PHASE2B_IMPLEMENTATION_PLAN.md`
- `docs/PHASE2A_REMEDIATION_COMPLETION_REPORT.md`
- Phase 2A runtime modules under `src/temporal_risk/`
- Phase 2A DDL under `sql/phase2a/ddl/`
- Phase 2A tests
- Published temporal database:
  `temporal_platform/warehouse/kronos_temporal_risk.duckdb`

Read-only verification produced:

| Evidence | Result |
|---|---:|
| Phase 2A tests | 24 passed |
| Schemas | 5 |
| Tables | 17 |
| Views | 0 |
| Core objects | 0 |
| Mart objects | 0 |
| Latest DQ controls | 27 |
| Latest reconciliations | 9 |
| Lineage | 5 nodes / 4 edges / 4 column mappings |
| Temporal database SHA-256 | `E73E374A01ECA52991D67A44DA592A1DB33FA24AE9B292ED514E0B2E016C34B0` |
| Current warehouse SHA-256 | `0B0529F947D81FDDC049873BF40AB8360FC595314EA21F0C883F10E7F5AE4CA5` |
| Scored portfolio SHA-256 | `DA9BA40AE0E29FF02D98025C9320DAD2AEB0C03CF30316983C10804086488FBB` |

## 2. Requirement Assessment

| # | Audit Requirement | Result | Finding |
|---:|---|---|---|
| 1 | Phase 2A acceptance is complete | PASS | Mandatory remediation is recorded as complete and the Phase 2A suite passes 24/24. |
| 2 | Phase 2A database integrity is preserved | PASS | The published database has the expected catalog, classifications, controls, and hash. |
| 3 | Extend 17 tables to 36 without conflict | PASS WITH CHANGE | Nineteen proposed names do not collide with existing objects. Exact Phase 2A catalog validation must become upgrade-aware. |
| 4 | No Phase 2A table redesign | PASS | Existing tables can remain structurally unchanged. Phase 2B requires additive tables and additive metadata rows only. |
| 5 | No lineage conflicts | PASS | Dedicated `historical_lineage_*` tables preserve the Phase 2A 5/4/4 lineage contract. |
| 6 | No DQ or reconciliation conflicts | PASS | Phase 2B uses dedicated historical result tables and does not alter Phase 2A result definitions. |
| 7 | No app, enterprise-data, or Phase 4 dependency | PASS | No current application or Phase 4 module imports `src.temporal_risk`; the proposed package remains isolated. |
| 8 | No current warehouse modification risk | PASS | Existing connection guards prohibit writable access to `data/warehouse/kronos_risk.duckdb`. Phase 2B must retain them. |
| 9 | No dashboard integration | PASS | The plan creates no application or dashboard dependency. |
| 10 | No analytical capability | PASS | Storage, DQ, reconciliation, lineage, rejects, and readiness evidence are controls, not analytics. |
| 11 | Rollback strategy is valid | PASS | Verified file-copy publication and backup restoration already exist. A fresh pre-2B backup is mandatory. |
| 12 | Independent removability remains valid | PASS | Restore the pre-2B database before deleting Phase 2B code, SQL, tests, documentation, inbound files, and evidence. |
| 13 | Protected-hash strategy is valid | PASS WITH CHANGE | The plan needs an explicit protected allowlist and must exclude intended Phase 2B additions from equality comparison. |
| 14 | Readiness gates prevent later capabilities | PASS WITH CHANGE | Activation is globally disabled. IFRS9 readiness requires a stricter Phase 2B ceiling described below. |

## 3. Catalog and Object Conflict Review

The proposed catalog arithmetic is correct:

```text
Existing Phase 2A tables: 17
Proposed Phase 2B tables: 19
Post-deployment tables:   36
Schemas:                   5
Views:                     0
Mart objects:              0
```

No proposed Phase 2B table name conflicts with the existing 17 tables.
`core` can receive the five proposed historical dimensions and facts without
altering an existing object. `mart` remains empty.

The current Phase 2A validator is intentionally exact:

```text
table_count = 17
core_object_count = 0
mart_object_count = 0
```

After Phase 2B deployment, calling that validator against the upgraded
production temporal database will fail. This is expected but must be handled
as a governed upgrade state rather than a generic Phase 2A failure.

## 4. Shared-Control Compatibility

The following existing tables can accept additive Phase 2B metadata without
redesign:

- `control.platform_release`
- `control.deployment_run`
- `control.source_asset`
- `control.source_column`
- `control.temporal_contract`
- `control.snapshot_registry`
- `control.snapshot_source_link`
- `control.publish_status`
- `staging.stg_snapshot_manifest`

Existing Phase 2A rows must remain unchanged by primary key and row content.
Counts in shared registries may increase when Phase 2B registers new releases,
sources, contracts, or snapshots. Compatibility tests must therefore compare
the original rows, not require unchanged total row counts.

Phase 2B must not add records to:

- `control.temporal_quality_result`
- `control.reconciliation_result`
- `control.lineage_node`
- `control.lineage_edge`
- `control.column_lineage`

Dedicated Phase 2B DQ, reconciliation, and lineage tables preserve those
Phase 2A contracts.

## 5. Mandatory Corrections

### 5.1 Add an Upgrade-Aware Phase 2A Guard

The plan requires `PHASE2A_UPGRADE_PRESENT`, but no proposed file implements
it. Before Phase 2A opens a writable working database, it must inspect the
published temporal catalog read-only.

Required behavior:

- exact 5/17/0 catalog: normal Phase 2A behavior;
- exact recognized 5/36/0 Phase 2B catalog: return
  `PHASE2A_UPGRADE_PRESENT`;
- any other catalog: retain the existing validation failure;
- do not weaken `validate_catalog()` for fresh Phase 2A deployments.

The final implementation inventory must explicitly identify the minimal
Phase 2A runtime and test files changed for this guard.

### 5.2 Use a Phase 2B-Specific Release Registrar

`src/temporal_risk/audit.py::register_release()` is hardcoded to:

```text
phase_name = PHASE2A
release_version = 2A.1
release_id = SHA-256(PHASE2A | 2A.1)
```

Calling it for Phase 2B would update the existing Phase 2A release row with
the 36-table catalog and Phase 2B specification inventory.

Phase 2B must implement its own registrar inside the new Phase 2B package. It
must create a distinct `control.platform_release` row with a Phase 2B release
ID and must never update the Phase 2A release row.

### 5.3 Define Shared-Registry Write Rules

The plan must explicitly state that Phase 2B may append governed metadata to
the shared release, deployment, source, contract, snapshot, publish, and
manifest tables listed in Section 4.

Required controls:

- existing Phase 2A rows are hash-compared before and after deployment;
- Phase 2B source assets use `authoritative_baseline = false`;
- observed and simulated contracts receive distinct IDs and versions;
- historical snapshots never overwrite the Phase 2A baseline snapshot;
- Phase 2B does not reuse Phase 2A DQ, reconciliation, or lineage tables.

### 5.4 Finalize the Protected-Hash Boundary

Protected verification must use a dynamic SHA-256 inventory captured at
deployment start. It must include:

- `app/`
- `src/enterprise_data/`
- credit-risk, model-validation, IFRS9, EWS, stress, contagion, decisioning,
  provisioning, and reporting modules;
- `models/`
- `data/`
- `outputs/`
- `reports/`
- `analytics/`
- existing Phase 2A SQL and all unaffected Phase 2A runtime files.

Intended Phase 2B code, SQL, tests, documentation, inbound, backup, and
evidence paths must not be treated as protected equality targets.

No Git state may be required. This workspace is not currently a Git working
tree, so verification must remain file-hash based.

### 5.5 Enforce the Phase 2B IFRS9 Readiness Ceiling

The proposed canonical staging and core structures do not persist complete
contractual cash-flow schedules, discounting schedules, or scenario-weighted
macroeconomic paths.

Therefore, during Phase 2B:

```text
IFRS9_TEMPORAL_INPUTS.data_status = NOT_READY or NOT_ELIGIBLE
IFRS9_TEMPORAL_INPUTS.activation_status = DISABLED_PENDING_FUTURE_PHASE
```

Phase 2B must not emit `READY_BUT_DISABLED` for IFRS9 temporal calculations,
even when individual dates or EIR fields are present. A later approved phase
must extend the contract and storage model before that status can change.

## 6. Readiness-Gate Assessment

Subject to Correction 5.5, the gates correctly prevent analytical use:

| Capability | Required Phase 2B Result |
|---|---|
| Historical storage | May pass only for a valid source-supplied temporal contract |
| Migration | Evidence only; activation disabled |
| Roll rates | Evidence only; activation disabled |
| Vintage | Evidence only; activation disabled |
| True OOT | Evidence only; simulated sources not eligible; activation disabled |
| IFRS9 temporal calculations | `NOT_READY` or `NOT_ELIGIBLE`; activation disabled |

No matrix, transition, cohort, curve, model validation, ECL, provision, or
reserve output may be created.

## 7. Rollback and Removability

The rollback design is valid if performed in this order:

1. Close all temporal database connections.
2. Create and hash-verify a fresh backup of the current Phase 2A database.
3. Deploy Phase 2B only to a working copy.
4. On rollback, restore and hash-verify the pre-2B database.
5. Confirm the restored catalog is exactly 5 schemas, 17 tables, and 0 views.
6. Remove Phase 2B package, SQL, tests, documentation, inbound, and evidence.

The backup must be restored before any runtime directory containing that
backup is removed.

Two stale Phase 2A working artifacts currently exist beside the published
database. Phase 2B must target only the exact published filename and must
neither treat these artifacts as a source nor publish them. Their presence is
non-blocking but should be covered by path-selection tests.

## 8. Required Test Additions

In addition to the planned tests, implementation must verify:

1. The original Phase 2A release row is unchanged.
2. All original shared-control rows are unchanged by primary key and hash.
3. A distinct Phase 2B release row records the 5/36/0 catalog.
4. Phase 2A returns `PHASE2A_UPGRADE_PRESENT` against the recognized upgraded
   database before creating evidence or a writable working copy.
5. Fresh temporary Phase 2A deployment still validates exactly 5/17/0.
6. Phase 2B ignores stale `.working.duckdb` and WAL files.
7. Protected hashes use the approved allowlist and dynamic baseline.
8. IFRS9 readiness cannot become `READY_BUT_DISABLED` in Phase 2B.
9. Restoring the pre-2B backup returns the exact Phase 2A database hash and
   catalog.

## 9. Final Decision

Phase 2B is technically feasible and does not require a Phase 2A table
redesign, current-warehouse modification, dashboard integration, Phase 4
dependency, or analytical functionality.

Implementation is approved only after the five mandatory corrections above
are incorporated into the controlling implementation specification.

**APPROVED_WITH_CHANGES**
