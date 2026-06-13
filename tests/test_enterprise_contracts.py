from __future__ import annotations

import json

import joblib
import numpy as np
import pandas as pd

from src.backtesting.validation_metrics import (
    drift_detection_placeholder,
    feature_drift_analysis,
    ks_statistic,
    population_stability_index,
    roc_auc_score_manual,
)
from src.credit_risk.portfolio_scoring import _prepare_feature_matrix
from src.reporting.report_generator import (
    aggregate_executive_metrics,
    build_enterprise_sections,
    prepare_engine_derived_reporting_data,
)
from src.shared.config import (
    EAD_FEATURE_COLUMNS_FILE,
    EAD_MODEL_FILE,
    FEATURE_COLUMNS_FILE,
    LGD_FEATURE_COLUMNS_FILE,
    LGD_MODEL_FILE,
    PD_MODEL_FILE,
    SCORED_PORTFOLIO_DATA,
)
from src.shared.governance import model_registry
from src.shared.utils import IFRS_STAGE_VALUES, normalize_ifrs_stage


def _contract_portfolio() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "borrower_id": "C001",
                "pd_score": 0.05,
                "lgd": 0.24,
                "ead": 25_000,
                "ifrs_stage": "Stage_1",
                "early_warning_score": 20,
                "credit_utilization": 0.35,
                "payment_burden_ratio": 0.18,
                "loan_to_income_ratio": 0.55,
                "total_delinquency": 0,
            },
            {
                "borrower_id": "C002",
                "pd_score": 0.32,
                "lgd": 0.58,
                "ead": 75_000,
                "ifrs_stage": "STAGE 2",
                "early_warning_score": 55,
                "credit_utilization": 0.72,
                "payment_burden_ratio": 0.36,
                "loan_to_income_ratio": 1.20,
                "total_delinquency": 2,
            },
            {
                "borrower_id": "C003",
                "pd_score": 0.71,
                "lgd": 0.82,
                "ead": 120_000,
                "ifrs_stage": "Stage_3",
                "early_warning_score": 90,
                "credit_utilization": 0.92,
                "payment_burden_ratio": 0.51,
                "loan_to_income_ratio": 2.10,
                "total_delinquency": 4,
            },
        ]
    )


def test_persisted_portfolio_contract() -> None:
    portfolio = pd.read_csv(SCORED_PORTFOLIO_DATA)
    required = {
        "borrower_id",
        "pd_score",
        "lgd",
        "ead",
        "ifrs_stage",
        "scoring_status",
    }
    assert required.issubset(portfolio.columns)
    assert portfolio["borrower_id"].notna().all()
    assert portfolio["pd_score"].between(0, 1).all()
    assert portfolio["lgd"].between(0, 1).all()
    assert (portfolio["ead"] >= 0).all()
    assert set(portfolio["ifrs_stage"].dropna().unique()).issubset(
        set(IFRS_STAGE_VALUES)
    )


def test_ifrs_stage_normalization_contract() -> None:
    cases = {
        "Stage_1": "STAGE 1",
        "Stage_2": "STAGE 2",
        "Stage_3": "STAGE 3",
        "stage 1": "STAGE 1",
        "STAGE-2": "STAGE 2",
        "3": "STAGE 3",
        "UNKNOWN": "STAGE 1",
    }
    for raw_value, expected in cases.items():
        assert normalize_ifrs_stage(raw_value) == expected


def test_model_feature_contract_preserves_legacy_ifrs_aliases() -> None:
    feature_columns = tuple(json.loads(FEATURE_COLUMNS_FILE.read_text()))
    frame = _contract_portfolio()
    matrix = _prepare_feature_matrix(frame, feature_columns)
    assert list(matrix.columns) == list(feature_columns)
    assert "ifrs_stage_Stage_2" in matrix.columns
    assert "ifrs_stage_Stage_3" in matrix.columns
    assert matrix["ifrs_stage_Stage_2"].sum() == 1
    assert matrix["ifrs_stage_Stage_3"].sum() == 1


def test_model_artifact_compatibility_contract() -> None:
    for model_path in [PD_MODEL_FILE, LGD_MODEL_FILE, EAD_MODEL_FILE]:
        model = joblib.load(model_path)
        assert hasattr(model, "predict")

    for feature_path in [
        FEATURE_COLUMNS_FILE,
        LGD_FEATURE_COLUMNS_FILE,
        EAD_FEATURE_COLUMNS_FILE,
    ]:
        features = json.loads(feature_path.read_text())
        assert len(features) > 0
        assert {"ifrs_stage_Stage_2", "ifrs_stage_Stage_3"}.issubset(
            set(features)
        )


def test_governance_registry_contract() -> None:
    registry = model_registry()
    assert {"pd_model", "lgd_model", "ead_model"}.issubset(
        registry["models"]
    )
    for model in registry["models"].values():
        assert model["sha256_model_hash"] != "UNAVAILABLE"
        assert model["model_owner"]
        assert model["approval_status"]
        assert model["validation_date"]
        assert model["promotion_date"]
        assert model["retirement_status"] == "ACTIVE"
        assert model["champion_designation"] is True


def test_reporting_contract_sections() -> None:
    portfolio, context = prepare_engine_derived_reporting_data(
        _contract_portfolio()
    )
    metrics = aggregate_executive_metrics(portfolio)
    sections = build_enterprise_sections(portfolio, metrics)
    assert {"provisioning", "stress_testing", "contagion", "decision"}.issubset(
        context["engine_summaries"]
    )
    assert {
        "portfolio_risk_summary",
        "ifrs9_summary",
        "stress_testing_summary",
        "concentration_risk_summary",
        "watchlist_summary",
        "top_exposure_summary",
        "executive_narrative_section",
    }.issubset(sections)
    assert sections["ifrs9_summary"]["stage_2_3_accounts"] == 2


def test_validation_edge_case_contracts() -> None:
    assert roc_auc_score_manual([1, 1, 1], [0.2, 0.4, 0.6]) == 0.0
    assert ks_statistic([0, 0, 0], [0.2, 0.4, 0.6]) == 0.0
    assert population_stability_index([0, 0, 0], [1, 2, 3]) == 0.0
    assert population_stability_index([np.nan, 0], [np.nan, 0]) == 0.0
    assert feature_drift_analysis(np.nan, 0.2)["drift_status"] == "UNAVAILABLE"
    assert drift_detection_placeholder()["monitoring_state"] == "PLACEHOLDER"
