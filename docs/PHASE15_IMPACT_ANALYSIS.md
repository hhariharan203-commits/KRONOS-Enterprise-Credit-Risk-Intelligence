# KRONOS Phase 1.5 Impact Analysis

Generated: 2026-06-16

## Scope

Phase 1.5 is a visibility enhancement only. It will surface already-generated Phase 1 model validation artifacts inside existing Streamlit dashboards so recruiters, hiring managers, and interviewers can see model governance, calibration, proxy OOT validation, PSI monitoring, challenger models, and the validation pack without opening backend folders.

No model training, scoring, dataset mutation, IFRS9 change, EWS change, stress-testing change, contagion change, navigation change, or new dashboard page is proposed.

## Current Dashboard Routing

Dashboard routing is centralized in `app/main.py` through the existing `PAGES` mapping:

| Navigation Label | Module |
|---|---|
| Executive Dashboard | `executive_dashboard` |
| Credit Engine Dashboard | `credit_engine_dashboard` |
| EWS Monitor | `ews_monitor` |
| Stress Lab | `stress_lab` |
| Contagion Terminal | `contagion_terminal` |
| Provisioning Dashboard | `provisioning_dashboard` |
| Decision Terminal | `decision_terminal` |
| Explainability Dashboard | `explainability_dashboard` |
| Risk Pulse Dashboard | `risk_pulse_dashboard` |
| Reports Dashboard | `reports_dashboard` |

No Phase 1.5 route addition is needed. `app/main.py` should remain unchanged.

## Existing Dashboard Modules

Current dashboard modules in `app/`:

- `executive_dashboard.py`
- `credit_engine_dashboard.py`
- `ews_monitor.py`
- `stress_lab.py`
- `contagion_terminal.py`
- `provisioning_dashboard.py`
- `decision_terminal.py`
- `explainability_dashboard.py`
- `risk_pulse_dashboard.py`
- `reports_dashboard.py`
- `live_intelligence_components.py`
- `main.py`

The requested visibility upgrade should touch only:

- `app/executive_dashboard.py`
- `app/explainability_dashboard.py`
- `app/reports_dashboard.py`

## Existing Phase 1 Outputs

Confirmed existing artifacts:

### Feature Governance

- `outputs/feature_governance_report.json`

### Calibration

- `outputs/calibration/calibration_summary.json`
- `outputs/calibration/decile_analysis.csv`
- `outputs/calibration/calibration_curve.png`
- `outputs/calibration/reliability_diagram.png`

### Proxy OOT Validation

- `outputs/oot_validation/executive_summary.json`
- `outputs/oot_validation/oot_metrics.json`
- `outputs/oot_validation/psi_report.json`
- `outputs/oot_validation/oot_auc_curve.png`
- `outputs/oot_validation/oot_score_distribution.png`

### Challenger Models

- `outputs/challenger_models/challenger_summary.json`
- `outputs/challenger_models/model_rankings.json`
- `outputs/challenger_models/model_comparison.csv`
- `outputs/challenger_models/roc_comparison.png`

### Model Validation Pack

- `outputs/model_validation_pack/validation_summary.json`
- `outputs/model_validation_pack/governance_summary.json`
- `outputs/model_validation_pack/model_risk_summary.json`
- `outputs/model_validation_pack/executive_briefing.json`
- `reports/model_validation_pack.pdf`
- `reports/model_validation_pack.md`

## Existing Target Dashboards

### Explainability Dashboard

File: `app/explainability_dashboard.py`

Relevant existing sections:

- `Executive Explainability Overview`
- `SHAP Executive Intelligence`
- `Enterprise Feature Importance`
- `Category Contribution Analysis`
- `Model Governance Summary`
- `Executive Export Center`

Recommended insertion point:

- Add a new section named `MODEL VALIDATION & GOVERNANCE` after the existing `Model Governance Summary` and before the interactive/export areas.

Reason:

- This location aligns model validation evidence with existing explainability and governance content.
- It does not require route changes or a new dashboard.
- It keeps the new material visible to interviewers reviewing model transparency.

### Reports Dashboard

File: `app/reports_dashboard.py`

Relevant existing behavior:

- Generates and downloads the main KRONOS enterprise report.
- Uses existing report-generation cache and PDF download controls.
- Has a final secure PDF download section for the current enterprise report.

Recommended insertion point:

- Add an `INSTITUTIONAL VALIDATION PACK` section near the existing PDF/report download area.

Reason:

- The validation pack is a reporting artifact, not a new analytics engine.
- The section can read existing JSON/PDF files and expose a download button without regenerating anything.

### Executive Dashboard

File: `app/executive_dashboard.py`

Relevant existing section:

- `Model Governance` section already reads `models/model_metrics.json`.

Recommended insertion point:

- Add a compact `MODEL GOVERNANCE STATUS` card inside or immediately adjacent to the existing `Model Governance` area.

Reason:

- The visual footprint remains small.
- The section already concerns board-level model health.
- It avoids altering the broader executive layout.

## Files To Be Modified After Approval

Proposed code modifications:

1. `app/explainability_dashboard.py`
   - Add artifact-safe readers.
   - Add `MODEL VALIDATION & GOVERNANCE` section.
   - Display champion model, AUC, F1, Brier score, calibration status, governance status, OOT status, PSI, best challenger, challenger AUC gap, approval status.
   - Display existing images: calibration curve, reliability diagram, ROC comparison.
   - Missing files should show `Artifact not available` and continue rendering.

2. `app/reports_dashboard.py`
   - Add `INSTITUTIONAL VALIDATION PACK` section.
   - Add validation pack PDF download control using `reports/model_validation_pack.pdf`.
   - Display validation status, governance status, model risk summary, and executive briefing summary.
   - No report regeneration.

3. `app/executive_dashboard.py`
   - Add compact `MODEL GOVERNANCE STATUS` card.
   - Display approval status, calibration status, OOT status, champion model, PSI, governance status.
   - Keep small footprint and preserve current layout.

## Files To Be Created After Approval

1. `docs/PHASE15_COMPLETION_REPORT.md`
   - Files modified
   - Screens added
   - Artifacts consumed
   - Risks identified
   - Verification results

No new dashboard page, no new navigation item, and no new model-validation backend artifact is required.

## Files Not To Be Modified

The following should remain unchanged:

- `app/main.py`
- `models/*`
- `data/*`
- `src/credit_risk/portfolio_scoring.py`
- IFRS9 modules under `src/provisioning/`
- EWS modules under `src/ews/`
- Stress-testing modules under `src/stress_testing/`
- Contagion modules under `src/contagion/`
- Existing Phase 1 output artifacts

## Dashboard Dependencies

Existing dependencies are sufficient:

- `streamlit`
- `pandas`
- `json`
- `pathlib.Path`

The target dashboards already use Streamlit primitives such as:

- `st.markdown`
- `st.columns`
- `st.metric`
- `st.image`
- `st.download_button`
- `st.warning`

No new package dependency is required.

## Existing Artifacts Consumed

### Explainability Dashboard

Reads:

- `outputs/model_validation_pack/validation_summary.json`
- `outputs/model_validation_pack/executive_briefing.json`
- `outputs/model_validation_pack/governance_summary.json`
- `outputs/calibration/calibration_summary.json`
- `outputs/calibration/calibration_curve.png`
- `outputs/calibration/reliability_diagram.png`
- `outputs/oot_validation/executive_summary.json`
- `outputs/oot_validation/psi_report.json`
- `outputs/challenger_models/challenger_summary.json`
- `outputs/challenger_models/roc_comparison.png`

### Reports Dashboard

Reads:

- `reports/model_validation_pack.pdf`
- `outputs/model_validation_pack/validation_summary.json`
- `outputs/model_validation_pack/governance_summary.json`
- `outputs/model_validation_pack/model_risk_summary.json`
- `outputs/model_validation_pack/executive_briefing.json`

### Executive Dashboard

Reads:

- `outputs/model_validation_pack/validation_summary.json`
- `outputs/model_validation_pack/governance_summary.json`
- `outputs/model_validation_pack/executive_briefing.json`
- `outputs/oot_validation/psi_report.json`

## Compatibility Risks

1. Missing artifact files
   - Risk: A dashboard section could fail if a JSON, CSV, PNG, or PDF is absent.
   - Mitigation: Wrap all reads in safe loaders and display `Artifact not available`.

2. Large visual footprint
   - Risk: Validation images could make the Explainability Dashboard too long.
   - Mitigation: Use existing section styling, columns, and compact image placement.

3. Reports Dashboard accidental regeneration
   - Risk: Existing report-generation flow could be triggered unintentionally.
   - Mitigation: Validation pack section must only read the existing PDF and JSON files.

4. Navigation changes
   - Risk: Adding a new route would violate scope.
   - Mitigation: Do not edit `app/main.py` or `PAGES`.

5. Runtime dependency gaps
   - Risk: Full app startup depends on installed Streamlit optional packages such as `streamlit_option_menu`.
   - Mitigation: Phase 1.5 does not add dependencies and should be verified through dashboard module smoke runs plus the available app runtime.

6. Styling drift
   - Risk: New section could look inconsistent.
   - Mitigation: Reuse existing dashboard section helpers and CSS classes where present.

## Rollback Plan

If approval is granted and implementation causes any issue:

1. Revert changes in:
   - `app/explainability_dashboard.py`
   - `app/reports_dashboard.py`
   - `app/executive_dashboard.py`
2. Delete:
   - `docs/PHASE15_COMPLETION_REPORT.md`
3. Do not touch:
   - `models/`
   - `data/`
   - `outputs/`
   - `reports/model_validation_pack.pdf`
   - `reports/model_validation_pack.md`
4. Re-run dashboard smoke verification for the original dashboard render paths.

Because the proposed change only reads existing artifacts, rollback does not require model retraining, rescoring, or data restoration.

## Proposed Verification After Approval

After implementation, verify:

- Executive Dashboard render path loads.
- Explainability Dashboard render path loads.
- Reports Dashboard render path loads.
- Existing dashboard routing is unchanged.
- `app/main.py` is unchanged.
- Model artifact hashes are unchanged.
- Dataset hashes are unchanged.
- `scored_portfolio.csv` is unchanged.
- Feature lists are unchanged.
- Existing Phase 1 artifacts are not regenerated.
- No schema changes occur.

## Impact Summary

Phase 1.5 is low-risk and high-visibility. It does not improve the underlying model, but it materially improves how the completed Phase 1 model-risk framework is presented to non-technical reviewers. The best implementation path is to modify only the three existing dashboards and create one completion report after verification.

Implementation should wait for explicit approval.
