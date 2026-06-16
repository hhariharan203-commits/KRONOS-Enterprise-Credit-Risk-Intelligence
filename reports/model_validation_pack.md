# KRONOS Institutional Model Validation Pack

Generated: 2026-06-15T18:19:01Z

## 1. Executive Summary

KRONOS Phase 1 adds bank-style model-risk controls around the PD champion model. The pack consolidates feature governance, calibration, proxy OOT validation, and challenger benchmarking. Final approval status: **AMBER**.

Approval rationale:
OOT validation uses proxy record-order methodology because no true temporal field exists.

## 2. Champion Model Overview

- Champion model: Current VotingClassifier
- Feature count: 61
- ROC AUC: 0.9068
- Accuracy: 0.8593
- Precision: 0.7513
- Recall: 0.6002
- F1 Score: 0.6673
- Current status: AMBER

## 3. Feature Governance

Governance status: **PASSED**

Prohibited feature controls:
borrower_id, customer_id, account_id, loan_id, application_id

Leakage prevention:
Identifier-like fields are excluded and training fails if borrower_id, customer_id, account_id, loan_id, or application_id enters final training features.

## 4. Calibration Assessment

- Calibration status: PASS
- Brier Score: 0.080149
- Predicted default rate: 0.234826
- Actual default rate: 0.23514
- Absolute predicted vs actual gap: 0.000314
- Maximum absolute decile gap: 0.122424

## 5. OOT Validation Assessment

- Methodology: Proxy OOT Validation
- Split method: chronological_record_ordering_fallback
- True temporal field found: False
- OOT AUC: 0.942631
- OOT KS: 0.739438
- PSI: 0.001287
- OOT status: STABLE WITH PROXY LIMITATION

Limitation:
Dataset does not contain origination, vintage, reporting, or observation dates. Validation uses chronological record-order fallback and should not be interpreted as true future-period model validation.

## 6. Challenger Model Assessment

Champion remains: Current VotingClassifier (Champion)

Best challenger: Logistic Regression

AUC performance gap: 0.002287

Recommendation:
Maintain Current VotingClassifier as champion. Challenger performance is broadly comparable and does not justify model replacement.

Rankings:
- 1. Logistic Regression (Challenger): AUC 0.909082, KS 0.658498, F1 0.675418, Brier 0.095236
- 2. Random Forest (Challenger): AUC 0.908391, KS 0.656136, F1 0.675801, Brier 0.095666
- 3. LightGBM (Challenger): AUC 0.906865, KS 0.650967, F1 0.665881, Brier 0.096578
- 4. Current VotingClassifier (Champion) (Champion): AUC 0.906795, KS 0.653167, F1 0.667297, Brier 0.096455
- 5. XGBoost (Challenger): AUC 0.905931, KS 0.652736, F1 0.668712, Brier 0.096845

## 7. Model Risk Assessment

Strengths:
- Governed feature list excludes prohibited identifier fields.
- Calibration outputs include Brier score, decile analysis, and reliability charts.
- Proxy OOT framework quantifies score shift, PSI, and stability metrics.
- Challenger framework compares four challenger models against the champion.

Weaknesses:
- Borrower-level dataset lacks true origination, vintage, reporting, or observation date.
- OOT validation is proxy record-order validation, not true future-period validation.
- LGD and EAD are outside this PD validation pack scope.
- Independent model validation sign-off remains simulated through local artifacts.

Assumptions:
Current VotingClassifier remains the approved champion by policy.; Saved PD model, scaler, and feature list are the active production-demo artifacts.; Merged credit dataset remains the validation population for Phase 1.

Limitations:
Dataset does not contain origination, vintage, reporting, or observation dates. Validation uses chronological record-order fallback and should not be interpreted as true future-period model validation.

## 8. Governance & Monitoring Assessment

Feature governance, calibration monitoring, proxy OOT stability, and challenger controls are now present. The main monitoring gap is the lack of true borrower-level temporal fields.

## 9. Recommended Actions

- Maintain VotingClassifier as champion.
- Do not replace the production-demo PD model based on challenger results.
- Add true borrower-level origination or observation date for future OOT validation.
- Continue monitoring calibration decile gaps and PSI trends.

## 10. Final Approval Status

**AMBER**
