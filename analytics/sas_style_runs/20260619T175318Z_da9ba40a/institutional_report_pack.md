# KRONOS SAS-Style Analytics Institutional Report Pack

This pack contains PROC-Equivalent Analytics generated from the read-only KRONOS warehouse. It does not represent SAS runtime execution.

The current credit loss proxy is a cross-sectional analytical measure only. It is not IFRS 9 ECL, a provision, or an accounting reserve.

## Portfolio Summary Report

| portfolio_size | total_ead | average_pd | average_lgd | weighted_pd | weighted_lgd | current_credit_loss_proxy | watchlist_count | stage_2_count | stage_3_count | high_risk_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 50000 | 837946260.460002 | 0.23478296814000016 | 0.5471661901199958 | 0.48653532298394403 | 0.754665585867323 | 360543819.2391487 | 16378.0 | 12957.0 | 3421.0 | 15069.0 |

## Risk Concentration Report

| dimension | category_count | hhi | largest_exposure_share | top_3_exposure_share | total_ead |
| --- | --- | --- | --- | --- | --- |
| industry | 10 | 0.10239554890919317 | 0.1203653598079568 | 0.3595099245918529 | 837946260.4600009 |
| region | 5 | 0.20078444985367822 | 0.21886834126966656 | 0.6259754323529676 | 837946260.4599986 |

## Ifrs9 Stage Report

| dimension | category | count | total_ead | average_pd | average_lgd | weighted_pd | weighted_lgd | current_credit_loss_proxy | portfolio_share | exposure_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ifrs9_stage | STAGE 1 | 33622 | 343429056.05999964 | 0.10737267669978032 | 0.44606145853905277 | 0.24415882772258185 | 0.6111942412920219 | 65627438.81979097 | 0.67244 | 0.409846158716037 |
| ifrs9_stage | STAGE 2 | 12957 | 345336159.8199984 | 0.4149850221501889 | 0.7120054772709691 | 0.5752953341754025 | 0.8232536036178649 | 177858480.7193781 | 0.25914 | 0.4121220848105718 |
| ifrs9_stage | STAGE 3 | 3421 | 149181044.57999995 | 0.8044733525285018 | 0.9165086752411585 | 0.8390404935728187 | 0.9261773610499782 | 117057899.6999787 | 0.06842 | 0.17803175647338648 |
| ifrs9_stage | TOTAL | 50000 | 837946260.460002 | 0.23478296814000016 | 0.5471661901199958 | 0.48653532298394403 | 0.754665585867323 | 360543819.2391487 | 1.0 | 1.0 |

## Watchlist Report

| watchlist_status | count | total_ead | average_pd | average_lgd | weighted_pd | weighted_lgd | current_credit_loss_proxy |
| --- | --- | --- | --- | --- | --- | --- | --- |
| NON-WATCHLIST | 33622 | 343429056.05999964 | 0.10737267669978032 | 0.44606145853905277 | 0.24415882772258185 | 0.6111942412920219 | 65627438.81979097 |
| WATCHLIST | 16378 | 494517204.39999974 | 0.4963404732568097 | 0.7547216477591895 | 0.6548593574929777 | 0.8543026217494925 | 294916380.4193579 |

## Model Risk Report

| published_batch_id | quality_score | quality_status | reconciliation_count | reconciliation_failures | performance_metric_count | validation_record_count | feature_importance_count | validation_records |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 79239c0ed5c14df793050725552e2f5c | 100.0 | PASS | 15 | 0.0 | 26 | 13 | 61 | 13 |
