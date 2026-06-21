# KRONOS Enterprise Risk Marts Data Dictionary

## `mart.vw_concentration_risk_current`

Grain: one dimension/category combination.

| Field | Meaning |
| --- | --- |
| `dimension_type` | `INDUSTRY`, `REGION`, `RISK_BAND`, or `RISK_GRADE` |
| `category` | Current category value |
| `account_count` | Borrower/facility proxy count |
| `total_ead` | Category EAD |
| `exposure_share` | Category EAD divided by dimension EAD |
| `hhi_contribution` | Squared exposure share |
| `hhi` | Sum of HHI contributions for the dimension |
| `average_pd` | Unweighted category PD |
| `average_lgd` | Unweighted category LGD |
| `weighted_pd` | EAD-weighted category PD |
| `weighted_lgd` | EAD-weighted category LGD |
| `current_credit_loss_proxy` | Sum of `PD * LGD * EAD` |
| `source_run_id` | Current scoring run |
| `source_model_version` | Persisted scoring model version |
| `warehouse_snapshot_timestamp` | Warehouse process timestamp |

## `mart.vw_portfolio_quality_current`

Grain: one current portfolio.

Includes:

- portfolio count and total EAD,
- average and EAD-weighted PD/LGD,
- watchlist count and exposure,
- Stage 1, 2, and 3 counts and exposure,
- delinquent count and exposure,
- average and maximum days past due,
- average total delinquency,
- average, maximum, and EAD-weighted utilization,
- current credit loss proxy,
- run, model, temporal and warehouse metadata.

`temporal_quality` remains `PROCESS TIME ONLY`.

## `mart.vw_watchlist_intelligence_current`

Grain: one current watchlisted borrower/facility proxy.

| Field | Meaning |
| --- | --- |
| `borrower_key` | Technical warehouse borrower key |
| `facility_key` | Technical facility proxy key |
| `pd_score` | Current probability of default score |
| `lgd` | Current loss-given-default estimate |
| `ead` | Current exposure at default |
| `ews_score` | Persisted early-warning score |
| `risk_band` | Current risk band |
| `risk_grade` | Current risk grade |
| `watchlist_flag` | Persisted watchlist indicator |
| `priority_rank` | Deterministic current-state ranking |

Priority order is EWS descending, PD descending, EAD descending, then
`borrower_key` ascending.

The view does not execute EWS engines or generate escalation actions.

## `mart.vw_model_governance_current`

Grain: one model family: PD, LGD, or EAD.

Includes:

- model version and artifact relationship status,
- artifact count,
- approval, calibration, challenger, validation and governance statuses,
- PSI,
- AUC, accuracy, precision, recall and F1,
- Brier score,
- MAE, RMSE and R-squared,
- feature, train-sample and test-sample counts,
- champion and challenger metadata.

PD-specific validation fields are not assigned to LGD or EAD. Their absent
independent validation is reported as `NOT AVAILABLE`, and calibration is
reported as `NOT APPLICABLE`.

The persisted status `UNRESOLVED_CURRENT_ARTIFACTS_DIFFER` is preserved.

## `mart.vw_enterprise_risk_summary_current`

Grain: one current portfolio and published Phase 4B batch.

Combines:

- portfolio and watchlist metrics,
- stage composition,
- delinquency and utilization,
- industry, region, risk-band and risk-grade HHI,
- PD governance and calibration,
- Phase 4B data-quality status,
- direct reconciliation status,
- warehouse publish status,
- source run, model and temporal metadata.

It does not use `control.vw_latest_reconciliation`.

## Prohibited Interpretations

`current_credit_loss_proxy` is not:

- IFRS9 ECL,
- a provision,
- an accounting reserve,
- a regulatory capital measure.

No Phase 4D view supports vintage, migration, roll-rate, cure, recovery,
lifetime-ECL, or historical-trend reporting.
