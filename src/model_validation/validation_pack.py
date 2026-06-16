# =============================================================================
# KRONOS — INSTITUTIONAL MODEL VALIDATION PACK
# File: src/model_validation/validation_pack.py
# =============================================================================

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from src.shared.config import (
    FEATURE_COLUMNS_FILE,
    MODEL_METRICS_FILE,
    OUTPUTS_DIR,
    REPORTS_DIR,
)


PACK_OUTPUT_DIR: Path = OUTPUTS_DIR / "model_validation_pack"

VALIDATION_SUMMARY_FILE: Path = (
    PACK_OUTPUT_DIR / "validation_summary.json"
)
GOVERNANCE_SUMMARY_FILE: Path = (
    PACK_OUTPUT_DIR / "governance_summary.json"
)
MODEL_RISK_SUMMARY_FILE: Path = (
    PACK_OUTPUT_DIR / "model_risk_summary.json"
)
EXECUTIVE_BRIEFING_FILE: Path = (
    PACK_OUTPUT_DIR / "executive_briefing.json"
)

PACK_PDF_FILE: Path = REPORTS_DIR / "model_validation_pack.pdf"
PACK_MD_FILE: Path = REPORTS_DIR / "model_validation_pack.md"

FEATURE_GOVERNANCE_FILE: Path = (
    OUTPUTS_DIR / "feature_governance_report.json"
)
CALIBRATION_DIR: Path = OUTPUTS_DIR / "calibration"
CALIBRATION_SUMMARY_FILE: Path = (
    CALIBRATION_DIR / "calibration_summary.json"
)
DECILE_ANALYSIS_FILE: Path = CALIBRATION_DIR / "decile_analysis.csv"
CALIBRATION_CURVE_FILE: Path = CALIBRATION_DIR / "calibration_curve.png"
RELIABILITY_DIAGRAM_FILE: Path = (
    CALIBRATION_DIR / "reliability_diagram.png"
)

OOT_DIR: Path = OUTPUTS_DIR / "oot_validation"
OOT_METHODOLOGY_FILE: Path = OOT_DIR / "methodology.json"
OOT_METRICS_FILE: Path = OOT_DIR / "oot_metrics.json"
OOT_EXECUTIVE_SUMMARY_FILE: Path = OOT_DIR / "executive_summary.json"
OOT_PSI_REPORT_FILE: Path = OOT_DIR / "psi_report.json"

CHALLENGER_DIR: Path = OUTPUTS_DIR / "challenger_models"
MODEL_COMPARISON_FILE: Path = CHALLENGER_DIR / "model_comparison.csv"
MODEL_RANKINGS_FILE: Path = CHALLENGER_DIR / "model_rankings.json"
CHALLENGER_SUMMARY_FILE: Path = (
    CHALLENGER_DIR / "challenger_summary.json"
)

APPROVAL_GREEN = "GREEN"
APPROVAL_AMBER = "AMBER"
APPROVAL_RED = "RED"


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def _read_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(
            f"Required validation artifact missing: {path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Required validation artifact missing: {path}"
        )

    return pd.read_csv(path)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            payload,
            f,
            indent=4,
        )


def load_phase1_artifacts() -> dict:
    """
    Load all completed Phase 1 model validation outputs.
    """

    return {
        "feature_governance": _read_json(
            FEATURE_GOVERNANCE_FILE
        ),
        "calibration_summary": _read_json(
            CALIBRATION_SUMMARY_FILE
        ),
        "decile_analysis": _read_csv(
            DECILE_ANALYSIS_FILE
        ),
        "oot_methodology": _read_json(
            OOT_METHODOLOGY_FILE
        ),
        "oot_metrics": _read_json(
            OOT_METRICS_FILE
        ),
        "oot_executive_summary": _read_json(
            OOT_EXECUTIVE_SUMMARY_FILE
        ),
        "oot_psi_report": _read_json(
            OOT_PSI_REPORT_FILE
        ),
        "model_comparison": _read_csv(
            MODEL_COMPARISON_FILE
        ),
        "model_rankings": _read_json(
            MODEL_RANKINGS_FILE
        ),
        "challenger_summary": _read_json(
            CHALLENGER_SUMMARY_FILE
        ),
        "champion_metrics": _read_json(
            MODEL_METRICS_FILE
        ),
        "feature_columns": _read_json(
            FEATURE_COLUMNS_FILE
        ),
    }


def classify_calibration_status(
    calibration_summary: dict,
) -> str:
    """
    Assess calibration using conservative validation thresholds.
    """

    brier_score = float(
        calibration_summary.get(
            "brier_score",
            1.0,
        )
    )
    absolute_gap = float(
        calibration_summary.get(
            "absolute_predicted_vs_actual_gap",
            1.0,
        )
    )
    max_decile_gap = float(
        calibration_summary.get(
            "max_absolute_decile_gap",
            1.0,
        )
    )

    if brier_score <= 0.12 and absolute_gap <= 0.01:
        if max_decile_gap <= 0.15:
            return "PASS"
        return "PASS WITH DECILE MONITORING"

    if brier_score <= 0.18 and absolute_gap <= 0.03:
        return "AMBER"

    return "FAIL"


def classify_oot_status(
    oot_executive_summary: dict,
    oot_methodology: dict,
) -> str:
    """
    Assess OOT stability while preserving proxy-methodology caveats.
    """

    key_metrics = oot_executive_summary.get(
        "key_metrics",
        {},
    )
    psi = float(
        key_metrics.get(
            "psi",
            1.0,
        )
    )
    oot_auc = float(
        key_metrics.get(
            "oot_auc",
            0.0,
        )
    )

    true_temporal_field_found = bool(
        oot_methodology.get(
            "true_temporal_field_found",
            False,
        )
    )

    if psi >= 0.25 or oot_auc < 0.65:
        return "FAIL"

    if not true_temporal_field_found:
        return "STABLE WITH PROXY LIMITATION"

    if psi >= 0.10:
        return "AMBER"

    return "PASS"


def determine_approval_status(
    governance_status: str,
    calibration_status: str,
    oot_status: str,
    challenger_present: bool,
) -> tuple[str, list[str]]:
    """
    Apply requested GREEN / AMBER / RED approval logic.
    """

    reasons: list[str] = []

    if governance_status != "PASSED":
        reasons.append(
            "Governance failure detected."
        )
        return APPROVAL_RED, reasons

    if calibration_status == "FAIL":
        reasons.append(
            "Calibration weakness detected."
        )
        return APPROVAL_RED, reasons

    if oot_status == "FAIL":
        reasons.append(
            "Model instability or severe drift detected."
        )
        return APPROVAL_RED, reasons

    if not challenger_present:
        reasons.append(
            "Challenger framework is missing."
        )
        return APPROVAL_RED, reasons

    if calibration_status != "PASS":
        reasons.append(
            f"Calibration status is {calibration_status}."
        )

    if "PROXY" in oot_status or "LIMITATION" in oot_status:
        reasons.append(
            "OOT validation uses proxy record-order methodology because no true temporal field exists."
        )

    if oot_status == "AMBER":
        reasons.append(
            "OOT drift status requires monitoring."
        )

    if reasons:
        return APPROVAL_AMBER, reasons

    return APPROVAL_GREEN, [
        "Governance, calibration, OOT stability, and challenger framework controls are present."
    ]


def build_validation_assessment(
    artifacts: dict,
) -> dict:
    """
    Convert raw Phase 1 artifacts into validation-pack summaries.
    """

    feature_governance = artifacts["feature_governance"]
    calibration_summary = artifacts["calibration_summary"]
    oot_methodology = artifacts["oot_methodology"]
    oot_executive = artifacts["oot_executive_summary"]
    oot_psi = artifacts["oot_psi_report"]
    challenger_summary = artifacts["challenger_summary"]
    champion_metrics = artifacts["champion_metrics"]
    model_rankings = artifacts["model_rankings"]

    governance_status = feature_governance.get(
        "overall_status",
        "UNKNOWN",
    )
    calibration_status = classify_calibration_status(
        calibration_summary
    )
    oot_status = classify_oot_status(
        oot_executive,
        oot_methodology,
    )
    challenger_present = bool(
        model_rankings.get(
            "model_rankings"
        )
    )

    approval_status, approval_reasons = determine_approval_status(
        governance_status,
        calibration_status,
        oot_status,
        challenger_present,
    )

    feature_columns = artifacts["feature_columns"]

    validation_summary = {
        "report_name": "KRONOS Institutional Model Validation Pack",
        "generated_at": _utc_timestamp(),
        "champion_model": "Current VotingClassifier",
        "feature_count": len(feature_columns),
        "approval_status": approval_status,
        "approval_reasons": approval_reasons,
        "champion_metrics": champion_metrics,
        "calibration_status": calibration_status,
        "oot_status": oot_status,
        "challenger_framework_present": challenger_present,
        "recommended_champion": challenger_summary.get(
            "champion_model",
            "Current VotingClassifier (Champion)",
        ),
    }

    governance_summary = {
        "governance_status": governance_status,
        "prohibited_feature_controls": feature_governance.get(
            "prohibited_identifier_features",
            [],
        ),
        "model_governance_results": feature_governance.get(
            "models",
            {},
        ),
        "leakage_prevention": (
            "Identifier-like fields are excluded and training fails if "
            "borrower_id, customer_id, account_id, loan_id, or "
            "application_id enters final training features."
        ),
    }

    model_risk_summary = {
        "strengths": [
            "Governed feature list excludes prohibited identifier fields.",
            "Calibration outputs include Brier score, decile analysis, and reliability charts.",
            "Proxy OOT framework quantifies score shift, PSI, and stability metrics.",
            "Challenger framework compares four challenger models against the champion.",
        ],
        "weaknesses": [
            "Borrower-level dataset lacks true origination, vintage, reporting, or observation date.",
            "OOT validation is proxy record-order validation, not true future-period validation.",
            "LGD and EAD are outside this PD validation pack scope.",
            "Independent model validation sign-off remains simulated through local artifacts.",
        ],
        "assumptions": [
            "Current VotingClassifier remains the approved champion by policy.",
            "Saved PD model, scaler, and feature list are the active production-demo artifacts.",
            "Merged credit dataset remains the validation population for Phase 1.",
        ],
        "limitations": oot_methodology.get(
            "limitations",
            [],
        ),
        "monitoring_focus": [
            "Capture a true loan origination or observation date for future validation.",
            "Monitor PSI and score distribution drift after each scoring refresh.",
            "Review challenger performance periodically without automatic replacement.",
        ],
    }

    executive_briefing = {
        "approval_status": approval_status,
        "champion_model": "Current VotingClassifier",
        "business_conclusion": (
            "Phase 1 materially improves model-risk governance through "
            "feature controls, calibration, proxy OOT validation, and "
            "challenger benchmarking."
        ),
        "key_metrics": {
            "champion_auc": champion_metrics.get(
                "roc_auc"
            ),
            "champion_f1": champion_metrics.get(
                "f1_score"
            ),
            "brier_score": calibration_summary.get(
                "brier_score"
            ),
            "calibration_gap": calibration_summary.get(
                "absolute_predicted_vs_actual_gap"
            ),
            "oot_auc": oot_executive.get(
                "key_metrics",
                {},
            ).get(
                "oot_auc"
            ),
            "oot_psi": oot_psi.get(
                "psi"
            ),
            "best_challenger": challenger_summary.get(
                "best_challenger"
            ),
            "challenger_auc_gap": challenger_summary.get(
                "performance_gap_best_challenger_minus_champion_auc"
            ),
        },
        "recommended_actions": [
            "Maintain VotingClassifier as champion.",
            "Do not replace the production-demo PD model based on challenger results.",
            "Add true borrower-level origination or observation date for future OOT validation.",
            "Continue monitoring calibration decile gaps and PSI trends.",
        ],
    }

    return {
        "validation_summary": validation_summary,
        "governance_summary": governance_summary,
        "model_risk_summary": model_risk_summary,
        "executive_briefing": executive_briefing,
    }


def save_summary_outputs(
    assessment: dict,
) -> None:
    _write_json(
        VALIDATION_SUMMARY_FILE,
        assessment["validation_summary"],
    )
    _write_json(
        GOVERNANCE_SUMMARY_FILE,
        assessment["governance_summary"],
    )
    _write_json(
        MODEL_RISK_SUMMARY_FILE,
        assessment["model_risk_summary"],
    )
    _write_json(
        EXECUTIVE_BRIEFING_FILE,
        assessment["executive_briefing"],
    )


def _metric_table_rows(
    metrics: dict,
) -> list[list[str]]:
    ordered_keys = [
        "accuracy",
        "precision",
        "recall",
        "f1_score",
        "roc_auc",
        "model_health_score",
        "psi",
        "model_drift",
        "train_auc",
        "overfitting_risk",
        "feature_count",
    ]

    return [
        [
            key,
            str(
                metrics.get(
                    key,
                    "N/A",
                )
            ),
        ]
        for key in ordered_keys
    ]


def build_markdown_report(
    artifacts: dict,
    assessment: dict,
) -> str:
    validation = assessment["validation_summary"]
    governance = assessment["governance_summary"]
    model_risk = assessment["model_risk_summary"]
    executive = assessment["executive_briefing"]

    calibration = artifacts["calibration_summary"]
    oot_methodology = artifacts["oot_methodology"]
    oot_executive = artifacts["oot_executive_summary"]
    challenger = artifacts["challenger_summary"]
    rankings = artifacts["model_rankings"]
    champion_metrics = artifacts["champion_metrics"]

    ranking_lines = "\n".join(
        [
            (
                f"- {row['rank']}. {row['model_name']} "
                f"({row['model_role']}): AUC {row['auc']}, "
                f"KS {row['ks_statistic']}, F1 {row['f1_score']}, "
                f"Brier {row['brier_score']}"
            )
            for row in rankings.get(
                "model_rankings",
                []
            )
        ]
    )

    strengths = "\n".join(
        f"- {item}"
        for item in model_risk["strengths"]
    )
    weaknesses = "\n".join(
        f"- {item}"
        for item in model_risk["weaknesses"]
    )
    actions = "\n".join(
        f"- {item}"
        for item in executive["recommended_actions"]
    )

    lines = [
        "# KRONOS Institutional Model Validation Pack",
        "",
        f"Generated: {validation['generated_at']}",
        "",
        "## 1. Executive Summary",
        "",
        (
            "KRONOS Phase 1 adds bank-style model-risk controls around the PD "
            "champion model. The pack consolidates feature governance, "
            "calibration, proxy OOT validation, and challenger benchmarking. "
            f"Final approval status: **{validation['approval_status']}**."
        ),
        "",
        "Approval rationale:",
        "; ".join(validation["approval_reasons"]),
        "",
        "## 2. Champion Model Overview",
        "",
        "- Champion model: Current VotingClassifier",
        f"- Feature count: {validation['feature_count']}",
        f"- ROC AUC: {champion_metrics.get('roc_auc')}",
        f"- Accuracy: {champion_metrics.get('accuracy')}",
        f"- Precision: {champion_metrics.get('precision')}",
        f"- Recall: {champion_metrics.get('recall')}",
        f"- F1 Score: {champion_metrics.get('f1_score')}",
        f"- Current status: {validation['approval_status']}",
        "",
        "## 3. Feature Governance",
        "",
        f"Governance status: **{governance['governance_status']}**",
        "",
        "Prohibited feature controls:",
        ", ".join(governance["prohibited_feature_controls"]),
        "",
        "Leakage prevention:",
        governance["leakage_prevention"],
        "",
        "## 4. Calibration Assessment",
        "",
        f"- Calibration status: {validation['calibration_status']}",
        f"- Brier Score: {calibration.get('brier_score')}",
        f"- Predicted default rate: {calibration.get('predicted_default_rate')}",
        f"- Actual default rate: {calibration.get('actual_default_rate')}",
        f"- Absolute predicted vs actual gap: {calibration.get('absolute_predicted_vs_actual_gap')}",
        f"- Maximum absolute decile gap: {calibration.get('max_absolute_decile_gap')}",
        "",
        "## 5. OOT Validation Assessment",
        "",
        f"- Methodology: {oot_methodology.get('validation_type')}",
        f"- Split method: {oot_methodology.get('split_method')}",
        f"- True temporal field found: {oot_methodology.get('true_temporal_field_found')}",
        f"- OOT AUC: {oot_executive.get('key_metrics', {}).get('oot_auc')}",
        f"- OOT KS: {oot_executive.get('key_metrics', {}).get('oot_ks_statistic')}",
        f"- PSI: {oot_executive.get('key_metrics', {}).get('psi')}",
        f"- OOT status: {validation['oot_status']}",
        "",
        "Limitation:",
        " ".join(oot_methodology.get("limitations", [])),
        "",
        "## 6. Challenger Model Assessment",
        "",
        f"Champion remains: {challenger.get('champion_model')}",
        "",
        f"Best challenger: {challenger.get('best_challenger')}",
        "",
        f"AUC performance gap: {challenger.get('performance_gap_best_challenger_minus_champion_auc')}",
        "",
        "Recommendation:",
        challenger.get("recommendation", ""),
        "",
        "Rankings:",
        ranking_lines,
        "",
        "## 7. Model Risk Assessment",
        "",
        "Strengths:",
        strengths,
        "",
        "Weaknesses:",
        weaknesses,
        "",
        "Assumptions:",
        "; ".join(model_risk["assumptions"]),
        "",
        "Limitations:",
        "; ".join(model_risk["limitations"]),
        "",
        "## 8. Governance & Monitoring Assessment",
        "",
        (
            "Feature governance, calibration monitoring, proxy OOT stability, "
            "and challenger controls are now present. The main monitoring gap "
            "is the lack of true borrower-level temporal fields."
        ),
        "",
        "## 9. Recommended Actions",
        "",
        actions,
        "",
        "## 10. Final Approval Status",
        "",
        f"**{validation['approval_status']}**",
    ]

    return "\n".join(lines) + "\n"


def write_markdown_report(
    markdown_text: str,
) -> None:
    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        PACK_MD_FILE,
        "w",
        encoding="utf-8",
    ) as f:
        f.write(
            markdown_text
        )


def _paragraph(
    text: str,
    style,
) -> Paragraph:
    return Paragraph(
        text.replace(
            "\n",
            "<br/>",
        ),
        style,
    )


def _bullet_list(
    items: list[str],
    style,
) -> Table:
    return Table(
        [
            [
                Paragraph(
                    f"- {item}",
                    style,
                )
            ]
            for item in items
        ],
        colWidths=[6.8 * inch],
        style=TableStyle(
            [
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        ),
    )


def _table(
    rows: list[list[str]],
    col_widths: list[float] | None = None,
) -> Table:
    table = Table(
        rows,
        colWidths=col_widths,
        repeatRows=1,
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def build_pdf_report(
    artifacts: dict,
    assessment: dict,
) -> None:
    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    styles = getSampleStyleSheet()
    title = styles["Title"]
    heading = styles["Heading2"]
    heading3 = styles["Heading3"]
    body = styles["BodyText"]
    body.fontSize = 9
    body.leading = 12

    doc = SimpleDocTemplate(
        str(PACK_PDF_FILE),
        pagesize=letter,
        rightMargin=0.55 * inch,
        leftMargin=0.55 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
    )

    validation = assessment["validation_summary"]
    governance = assessment["governance_summary"]
    model_risk = assessment["model_risk_summary"]
    executive = assessment["executive_briefing"]

    calibration = artifacts["calibration_summary"]
    oot_methodology = artifacts["oot_methodology"]
    oot_executive = artifacts["oot_executive_summary"]
    oot_psi = artifacts["oot_psi_report"]
    challenger = artifacts["challenger_summary"]
    model_comparison = artifacts["model_comparison"]
    champion_metrics = artifacts["champion_metrics"]
    decile_analysis = artifacts["decile_analysis"]

    story = [
        Paragraph(
            "KRONOS Institutional Model Validation Pack",
            title,
        ),
        Spacer(1, 8),
        Paragraph(
            f"Generated: {validation['generated_at']}",
            body,
        ),
        Spacer(1, 14),
        Paragraph(
            "1. Executive Summary",
            heading,
        ),
        _paragraph(
            (
                "Phase 1 consolidates model-risk evidence for the KRONOS PD "
                "champion. The pack includes feature governance, calibration, "
                "proxy OOT stability testing, and challenger benchmarking. "
                f"Final approval status: <b>{validation['approval_status']}</b>."
            ),
            body,
        ),
        Spacer(1, 8),
        _bullet_list(
            validation["approval_reasons"],
            body,
        ),
        Spacer(1, 12),
        Paragraph(
            "2. Champion Model Overview",
            heading,
        ),
        _table(
            [["Metric", "Value"]]
            + _metric_table_rows(
                champion_metrics
            ),
            [2.4 * inch, 4.6 * inch],
        ),
        Spacer(1, 12),
        Paragraph(
            "3. Feature Governance",
            heading,
        ),
        _paragraph(
            (
                f"Governance status: <b>{governance['governance_status']}</b>. "
                f"Prohibited controls: {', '.join(governance['prohibited_feature_controls'])}."
            ),
            body,
        ),
        _paragraph(
            governance["leakage_prevention"],
            body,
        ),
        Spacer(1, 12),
        Paragraph(
            "4. Calibration Assessment",
            heading,
        ),
        _table(
            [
                ["Metric", "Value"],
                ["Calibration Status", validation["calibration_status"]],
                ["Brier Score", str(calibration.get("brier_score"))],
                ["Predicted Default Rate", str(calibration.get("predicted_default_rate"))],
                ["Actual Default Rate", str(calibration.get("actual_default_rate"))],
                ["Absolute Gap", str(calibration.get("absolute_predicted_vs_actual_gap"))],
                ["Max Decile Gap", str(calibration.get("max_absolute_decile_gap"))],
            ],
            [2.4 * inch, 4.6 * inch],
        ),
        Spacer(1, 8),
    ]

    for image_path in [
        CALIBRATION_CURVE_FILE,
        RELIABILITY_DIAGRAM_FILE,
    ]:
        if image_path.exists():
            story.append(
                Image(
                    str(image_path),
                    width=3.25 * inch,
                    height=2.35 * inch,
                )
            )
            story.append(
                Spacer(1, 8)
            )

    decile_rows = [
        [
            "Decile",
            "Obs",
            "Default Rate",
            "Avg PD",
            "Gap",
        ]
    ]
    for _, row in decile_analysis.iterrows():
        decile_rows.append(
            [
                str(row.get("decile")),
                str(row.get("observation_count")),
                str(row.get("actual_default_rate")),
                str(row.get("average_predicted_pd")),
                str(row.get("calibration_gap")),
            ]
        )

    story.extend(
        [
            _table(
                decile_rows,
                [
                    0.7 * inch,
                    0.9 * inch,
                    1.3 * inch,
                    1.3 * inch,
                    1.1 * inch,
                ],
            ),
            PageBreak(),
            Paragraph(
                "5. OOT Validation Assessment",
                heading,
            ),
            _table(
                [
                    ["Metric", "Value"],
                    ["Methodology", str(oot_methodology.get("validation_type"))],
                    ["Split Method", str(oot_methodology.get("split_method"))],
                    ["True Temporal Field Found", str(oot_methodology.get("true_temporal_field_found"))],
                    ["OOT AUC", str(oot_executive.get("key_metrics", {}).get("oot_auc"))],
                    ["OOT KS", str(oot_executive.get("key_metrics", {}).get("oot_ks_statistic"))],
                    ["OOT F1", str(oot_executive.get("key_metrics", {}).get("oot_f1_score"))],
                    ["PSI", str(oot_psi.get("psi"))],
                    ["PSI Status", str(oot_psi.get("psi_status"))],
                ],
                [2.4 * inch, 4.6 * inch],
            ),
            Spacer(1, 8),
            _paragraph(
                "Limitation: "
                + " ".join(
                    oot_methodology.get(
                        "limitations",
                        [],
                    )
                ),
                body,
            ),
            Spacer(1, 12),
            Paragraph(
                "6. Challenger Model Assessment",
                heading,
            ),
            _paragraph(
                (
                    f"Best challenger: <b>{challenger.get('best_challenger')}</b>. "
                    f"AUC gap versus champion: {challenger.get('performance_gap_best_challenger_minus_champion_auc')}. "
                    f"Recommendation: {challenger.get('recommendation')}"
                ),
                body,
            ),
        ]
    )

    comparison_rows = [
        [
            "Model",
            "Role",
            "AUC",
            "KS",
            "F1",
            "Brier",
        ]
    ]
    for _, row in model_comparison.iterrows():
        comparison_rows.append(
            [
                str(row["model_name"]),
                str(row["model_role"]),
                str(row["auc"]),
                str(row["ks_statistic"]),
                str(row["f1_score"]),
                str(row["brier_score"]),
            ]
        )

    story.extend(
        [
            _table(
                comparison_rows,
                [
                    2.3 * inch,
                    0.9 * inch,
                    0.8 * inch,
                    0.8 * inch,
                    0.8 * inch,
                    0.8 * inch,
                ],
            ),
            Spacer(1, 12),
            Paragraph(
                "7. Model Risk Assessment",
                heading,
            ),
            Paragraph(
                "Strengths",
                heading3,
            ),
            _bullet_list(
                model_risk["strengths"],
                body,
            ),
            Paragraph(
                "Weaknesses",
                heading3,
            ),
            _bullet_list(
                model_risk["weaknesses"],
                body,
            ),
            Paragraph(
                "Assumptions",
                heading3,
            ),
            _bullet_list(
                model_risk["assumptions"],
                body,
            ),
            Paragraph(
                "Limitations",
                heading3,
            ),
            _bullet_list(
                model_risk["limitations"],
                body,
            ),
            Spacer(1, 12),
            Paragraph(
                "8. Governance & Monitoring Assessment",
                heading,
            ),
            _paragraph(
                (
                    "Governance controls, calibration evidence, proxy OOT "
                    "stability checks, and challenger benchmarking are now "
                    "available. Continued monitoring should focus on PSI, "
                    "calibration decile gaps, and introduction of true "
                    "borrower-level temporal fields."
                ),
                body,
            ),
            Paragraph(
                "9. Recommended Actions",
                heading,
            ),
            _bullet_list(
                executive["recommended_actions"],
                body,
            ),
            Paragraph(
                "10. Final Approval Status",
                heading,
            ),
            _paragraph(
                f"<b>{validation['approval_status']}</b>",
                body,
            ),
        ]
    )

    doc.build(
        story
    )


def run_validation_pack() -> dict:
    artifacts = load_phase1_artifacts()
    assessment = build_validation_assessment(
        artifacts
    )

    save_summary_outputs(
        assessment
    )

    markdown_text = build_markdown_report(
        artifacts,
        assessment,
    )
    write_markdown_report(
        markdown_text
    )
    build_pdf_report(
        artifacts,
        assessment,
    )

    return {
        "validation_summary": assessment["validation_summary"],
        "governance_summary": assessment["governance_summary"],
        "model_risk_summary": assessment["model_risk_summary"],
        "executive_briefing": assessment["executive_briefing"],
        "outputs": {
            "validation_summary": str(VALIDATION_SUMMARY_FILE),
            "governance_summary": str(GOVERNANCE_SUMMARY_FILE),
            "model_risk_summary": str(MODEL_RISK_SUMMARY_FILE),
            "executive_briefing": str(EXECUTIVE_BRIEFING_FILE),
            "pdf": str(PACK_PDF_FILE),
            "markdown": str(PACK_MD_FILE),
        },
    }


if __name__ == "__main__":
    result = run_validation_pack()
    print(
        json.dumps(
            {
                "approval_status": result["validation_summary"]["approval_status"],
                "outputs": result["outputs"],
            },
            indent=4,
        )
    )

# =============================================================================
# END OF FILE
# =============================================================================
