# Analytical Scope and Claim Boundaries

KRONOS uses synthetic data. This table separates implemented analytical behavior from simulations and placeholders so reviewers can evaluate the repository without inflated claims.

| Capability | Classification | Evidence and boundary |
| --- | --- | --- |
| Probability of Default | Implemented | Trained classifier, saved artifacts, borrower scoring, calibration, discrimination, governance, and challenger evidence |
| LGD | Implemented on synthetic targets | Model and metrics exist; no realized recovery history supports production recovery validation |
| EAD | Implemented on synthetic targets | Model and metrics exist; no contractual limit/utilization history supports production CCF validation |
| IFRS 9 staging and ECL | Indicative simulation | Stage and expected-loss logic is implemented for portfolio analysis; it is not an accounting-policy engine |
| Early Warning System | Implemented portfolio analytics | Rule and score outputs operate on current synthetic borrower attributes, not a genuine monthly behavioral history |
| Stress testing | Implemented deterministic simulation | Baseline, adverse, severe, inflation, rate, and custom scenario mechanics are inspectable and repeatable |
| Contagion | Implemented portfolio simulation | Similarity and concentration networks are analytical proxies, not observed legal-entity dependencies |
| Segmentation | Implemented | Risk bands, grades, industry, region, and borrower-level views are used across analytics and dashboards |
| Challenger models | Implemented | Champion/challenger comparison is generated; promotion remains a governed recommendation, not an automatic deployment |
| Calibration | Implemented | Brier score, deciles, reliability outputs, and predicted-versus-observed comparison are persisted |
| Out-of-time validation | Proxy only | Record order is used because no genuine observation date exists; outputs explicitly preserve this limitation |
| Data warehouse | Implemented analytical mirror | DuckDB control, staging, reference, core, and mart layers; CSV remains the operational application source |
| Temporal ingestion Phase 2C | Complete with source not ready | `PHASE2C_SOURCE_NOT_READY` is the correct control outcome because KRONOS does not fabricate unavailable source dates |
| External intelligence | Optional integration | Saved local data supports deterministic use; network refresh requires explicit action and provider credentials |
| Independent validation | Simulated governance evidence | The repository demonstrates the process and artifacts but does not claim an independent institutional sign-off |

## Interpretation

“Implemented” means executable logic, persisted evidence, and tests exist in this repository. It does not mean that synthetic outputs have regulatory approval, production infrastructure, or validation against a bank’s realized loss history.

The deliberate non-fabrication decisions—proxy OOT disclosure and `PHASE2C_SOURCE_NOT_READY`—are governance strengths, not missing feature claims.
