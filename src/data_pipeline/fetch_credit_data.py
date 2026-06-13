# =============================================================================
# KRONOS — ENTERPRISE CREDIT PORTFOLIO GENERATOR V2
# File: src/data_pipeline/fetch_credit_data.py
# =============================================================================

import numpy as np
import pandas as pd

from src.shared.config import (
    MASTER_CREDIT_DATA,
    RANDOM_STATE,
)

# =============================================================================
# CONFIGURATION
# =============================================================================

N_BORROWERS = 50000

# =============================================================================
# PORTFOLIO DEFINITIONS
# =============================================================================

RISK_PROFILES = [
    "PRIME",
    "NEAR_PRIME",
    "SUBPRIME",
    "HIGH_RISK",
]

RISK_PROFILE_WEIGHTS = [
    0.40,
    0.30,
    0.20,
    0.10,
]

INDUSTRIES = [
    "Technology",
    "Manufacturing",
    "Healthcare",
    "Retail",
    "Construction",
    "Financial Services",
    "Energy",
    "Transportation",
    "Government",
    "Education",
]

INDUSTRY_WEIGHTS = [
    0.12,
    0.10,
    0.12,
    0.10,
    0.08,
    0.12,
    0.08,
    0.08,
    0.10,
    0.10,
]

REGIONS = [
    "North",
    "South",
    "East",
    "West",
    "Central",
]

REGIONS_WEIGHTS = [
    0.22,
    0.20,
    0.20,
    0.18,
    0.20,
]

# =============================================================================
# GENERATE PORTFOLIO SEGMENTS
# =============================================================================

def generate_portfolio_segments(n):

    risk_profile = np.random.choice(
        RISK_PROFILES,
        size=n,
        p=RISK_PROFILE_WEIGHTS
    )

    industry = np.random.choice(
        INDUSTRIES,
        size=n,
        p=INDUSTRY_WEIGHTS
    )

    region = np.random.choice(
        REGIONS,
        size=n,
        p=REGIONS_WEIGHTS
    )

    return risk_profile, industry, region

# =============================================================================
# GENERATE BORROWER DEMOGRAPHICS
# =============================================================================

def generate_demographics(risk_profile):

    n = len(risk_profile)

    age = np.zeros(n)

    employment_years = np.zeros(n)

    annual_income = np.zeros(n)

    for i in range(n):

        profile = risk_profile[i]

        if profile == "PRIME":

            age[i] = np.random.randint(30, 70)

            employment_years[i] = np.random.randint(8, 35)

            annual_income[i] = np.random.lognormal(
                mean=14.2,
                sigma=0.35
            )

        elif profile == "NEAR_PRIME":

            age[i] = np.random.randint(25, 65)

            employment_years[i] = np.random.randint(4, 25)

            annual_income[i] = np.random.lognormal(
                mean=13.7,
                sigma=0.45
            )

        elif profile == "SUBPRIME":

            age[i] = np.random.randint(22, 60)

            employment_years[i] = np.random.randint(1, 15)

            annual_income[i] = np.random.lognormal(
                mean=13.1,
                sigma=0.55
            )

        else:

            age[i] = np.random.randint(21, 55)

            employment_years[i] = np.random.randint(0, 8)

            annual_income[i] = np.random.lognormal(
                mean=12.6,
                sigma=0.65
            )

    annual_income = np.clip(
        annual_income,
        250000,
        10000000
    )

    return (
        age.astype(int),
        employment_years.astype(int),
        annual_income
    )

# =============================================================================
# GENERATE CREDIT FACILITIES
# =============================================================================

def generate_credit_facilities(
    risk_profile,
    annual_income
):

    n = len(risk_profile)

    loan_amount = np.zeros(n)

    credit_limit = np.zeros(n)

    interest_rate = np.zeros(n)

    loan_term = np.zeros(n)

    for i in range(n):

        profile = risk_profile[i]

        income = annual_income[i]

        if profile == "PRIME":

            loan_amount[i] = (
                income *
                np.random.uniform(0.20, 0.80)
            )

            credit_limit[i] = (
                income *
                np.random.uniform(1.0, 2.5)
            )

            interest_rate[i] = np.random.uniform(
                6,
                12
            )

        elif profile == "NEAR_PRIME":

            loan_amount[i] = (
                income *
                np.random.uniform(0.40, 1.00)
            )

            credit_limit[i] = (
                income *
                np.random.uniform(0.8, 2.0)
            )

            interest_rate[i] = np.random.uniform(
                10,
                18
            )

        elif profile == "SUBPRIME":

            loan_amount[i] = (
                income *
                np.random.uniform(0.70, 1.50)
            )

            credit_limit[i] = (
                income *
                np.random.uniform(0.5, 1.5)
            )

            interest_rate[i] = np.random.uniform(
                15,
                25
            )

        else:

            loan_amount[i] = (
                income *
                np.random.uniform(1.00, 2.00)
            )

            credit_limit[i] = (
                income *
                np.random.uniform(0.3, 1.0)
            )

            interest_rate[i] = np.random.uniform(
                20,
                35
            )

        loan_term[i] = np.random.choice(
            [12, 24, 36, 48, 60]
        )

    return (
        loan_amount,
        credit_limit,
        interest_rate,
        loan_term.astype(int)
    )

# =============================================================================
# GENERATE BEHAVIORAL VARIABLES
# =============================================================================

def generate_behavioral_variables(
    risk_profile,
    annual_income,
    loan_amount,
    credit_limit,
    loan_term
):

    n = len(risk_profile)

    revolving_balance = np.zeros(n)

    delinq_2yrs = np.zeros(n)

    days_past_due = np.zeros(n)

    collateral_value = np.zeros(n)

    monthly_payment = np.zeros(n)

    for i in range(n):

        profile = risk_profile[i]

        if profile == "PRIME":

            utilization = np.random.uniform(
                0.05,
                0.45
            )

            delinq = np.random.poisson(0.2)

            dpd = np.random.choice(
                [0, 0, 0, 30],
                p=[0.80, 0.10, 0.05, 0.05]
            )

            collateral_mult = np.random.uniform(
                1.20,
                2.00
            )

        elif profile == "NEAR_PRIME":

            utilization = np.random.uniform(
                0.20,
                0.70
            )

            delinq = np.random.poisson(1.0)

            dpd = np.random.choice(
                [0, 30, 60],
                p=[0.70, 0.20, 0.10]
            )

            collateral_mult = np.random.uniform(
                1.00,
                1.60
            )

        elif profile == "SUBPRIME":

            utilization = np.random.uniform(
                0.50,
                0.95
            )

            delinq = np.random.poisson(2.5)

            dpd = np.random.choice(
                [0, 30, 60, 90],
                p=[0.40, 0.30, 0.20, 0.10]
            )

            collateral_mult = np.random.uniform(
                0.70,
                1.30
            )

        else:

            utilization = np.random.uniform(
                0.70,
                1.20
            )

            delinq = np.random.poisson(4.0)

            dpd = np.random.choice(
                [30, 60, 90, 120],
                p=[0.20, 0.30, 0.30, 0.20]
            )

            collateral_mult = np.random.uniform(
                0.40,
                1.00
            )

        revolving_balance[i] = (
            credit_limit[i] * utilization
        )

        delinq_2yrs[i] = min(delinq, 12)

        days_past_due[i] = dpd

        collateral_value[i] = (
            loan_amount[i] * collateral_mult
        )

        monthly_payment[i] = (
            loan_amount[i] / loan_term[i]
        )

    return (
        revolving_balance,
        delinq_2yrs.astype(int),
        days_past_due.astype(int),
        collateral_value,
        monthly_payment,
    )

# =============================================================================
# CREATE ADVANCED CREDIT RATIOS
# =============================================================================

def create_credit_ratios(
    annual_income,
    loan_amount,
    credit_limit,
    revolving_balance,
    monthly_payment,
    collateral_value
):

    dti_ratio = (
        loan_amount /
        annual_income
    )

    credit_utilization = (
        revolving_balance /
        credit_limit
    )

    payment_burden_ratio = (
        (monthly_payment * 12)
        / annual_income
    )

    loan_to_income_ratio = (
        loan_amount /
        annual_income
    )

    collateral_coverage_ratio = (
        collateral_value /
        loan_amount
    )

    return (
        dti_ratio,
        credit_utilization,
        payment_burden_ratio,
        loan_to_income_ratio,
        collateral_coverage_ratio
    )

# =============================================================================
# STRESS TESTING VARIABLES
# =============================================================================

def generate_macro_sensitivity(
    risk_profile
):

    n = len(risk_profile)

    macro_sensitivity = np.zeros(n)

    interest_rate_sensitivity = np.zeros(n)

    unemployment_sensitivity = np.zeros(n)

    for i in range(n):

        profile = risk_profile[i]

        if profile == "PRIME":

            macro_sensitivity[i] = np.random.uniform(
                0.10,
                0.40
            )

            interest_rate_sensitivity[i] = np.random.uniform(
                0.10,
                0.40
            )

            unemployment_sensitivity[i] = np.random.uniform(
                0.10,
                0.40
            )

        elif profile == "NEAR_PRIME":

            macro_sensitivity[i] = np.random.uniform(
                0.30,
                0.60
            )

            interest_rate_sensitivity[i] = np.random.uniform(
                0.30,
                0.60
            )

            unemployment_sensitivity[i] = np.random.uniform(
                0.30,
                0.60
            )

        elif profile == "SUBPRIME":

            macro_sensitivity[i] = np.random.uniform(
                0.50,
                0.85
            )

            interest_rate_sensitivity[i] = np.random.uniform(
                0.50,
                0.85
            )

            unemployment_sensitivity[i] = np.random.uniform(
                0.50,
                0.85
            )

        else:

            macro_sensitivity[i] = np.random.uniform(
                0.70,
                1.00
            )

            interest_rate_sensitivity[i] = np.random.uniform(
                0.70,
                1.00
            )

            unemployment_sensitivity[i] = np.random.uniform(
                0.70,
                1.00
            )

    return (
        macro_sensitivity,
        interest_rate_sensitivity,
        unemployment_sensitivity,
    )

# =============================================================================
# EWS VARIABLES
# =============================================================================

def generate_ews_scores(
    dti_ratio,
    credit_utilization,
    delinq_2yrs,
    days_past_due
):

    risk_driver = (
        (dti_ratio * 25)
        + (credit_utilization * 25)
        + (delinq_2yrs * 4)
        + ((days_past_due / 120) * 25)
    )

    behavioral_risk_score = (
        risk_driver * 1.5
    )

    risk_migration_score = (
        behavioral_risk_score
        + np.random.normal(
            0,
            5,
            len(behavioral_risk_score)
        )
    )

    # =========================================================
    # PERCENTILE NORMALIZATION
    # =========================================================

    behavioral_risk_score = (
        pd.Series(
            behavioral_risk_score
        )
        .rank(
            method="first",
            pct=True
        )
        .values
        * 99
    )

    risk_migration_score = (
        pd.Series(
            risk_migration_score
        )
        .rank(
            method="first",
            pct=True
        )
        .values
        * 99
    )

    # =========================================================
    # EARLY WARNING SCORE
    # =========================================================

    early_warning_score = (
        (behavioral_risk_score * 0.55)
        + (risk_migration_score * 0.35)
        + (credit_utilization * 5)
        + (dti_ratio * 5)
    )

    early_warning_score = (
        pd.Series(
            early_warning_score
        )
        .rank(
            method="first",
            pct=True
        )
        .values
        * 99
    )

    return (
        behavioral_risk_score,
        risk_migration_score,
        early_warning_score,
    )

# =============================================================================
# IFRS9 STAGING
# =============================================================================

def generate_ifrs_stage(days_past_due):

    stage = np.where(
        days_past_due >= 90,
        "STAGE 3",
        np.where(
            days_past_due >= 30,
            "STAGE 2",
            "STAGE 1"
        )
    )

    watchlist_flag = np.where(
        days_past_due >= 30,
        1,
        0
    )

    return stage, watchlist_flag

# =============================================================================
# DEFAULT TARGET GENERATION
# =============================================================================

def generate_default_target(
    risk_profile,
    dti_ratio,
    credit_utilization,
    delinq_2yrs,
    employment_years,
    interest_rate
):

    segment_pd = np.select(
        [
            risk_profile == "PRIME",
            risk_profile == "NEAR_PRIME",
            risk_profile == "SUBPRIME",
            risk_profile == "HIGH_RISK"
        ],
        [
            0.03,
            0.08,
            0.18,
            0.40
        ]
    )

    risk_adjustment = (
        ((dti_ratio - 0.40) * 0.25)
        + ((credit_utilization - 0.50) * 0.20)
        + (((interest_rate - 12) / 20) * 0.15)
        + ((delinq_2yrs / 10) * 0.20)
        - ((employment_years / 40) * 0.10)
    )

    default_probability = (
        segment_pd
        + risk_adjustment
    )

    default_probability = np.clip(
        default_probability,
        0.01,
        0.95
    )

    target_default = np.random.binomial(
        1,
        default_probability
    )

    return target_default

# =============================================================================
# LGD & EAD SEEDS
# =============================================================================

def generate_lgd_ead_seed(
    credit_utilization,
    dti_ratio,
    loan_amount,
    collateral_value
):

    lgd_seed = (
        0.20
        + (credit_utilization * 0.30)
        + (dti_ratio * 0.20)
        - ((collateral_value / loan_amount) * 0.15)
    )

    lgd_seed = np.clip(
        lgd_seed,
        0.05,
        0.95
    )

    ead_seed = (
        loan_amount
        * (
            0.60
            + credit_utilization
        )
    )

    return lgd_seed, ead_seed

# =============================================================================
# GENERATE PORTFOLIO
# =============================================================================

def generate_portfolio():

    np.random.seed(RANDOM_STATE)

    print("\n" + "=" * 80)
    print("[KRONOS] GENERATING ENTERPRISE CREDIT PORTFOLIO")
    print("=" * 80)

    borrower_id = np.arange(
        1,
        N_BORROWERS + 1
    )

    risk_profile, industry, region = (
        generate_portfolio_segments(
            N_BORROWERS
        )
    )

    (
        age,
        employment_years,
        annual_income
    ) = generate_demographics(
        risk_profile
    )

    (
        loan_amount,
        credit_limit,
        interest_rate,
        loan_term
    ) = generate_credit_facilities(
        risk_profile,
        annual_income
    )

    (
        revolving_balance,
        delinq_2yrs,
        days_past_due,
        collateral_value,
        monthly_payment
    ) = generate_behavioral_variables(
        risk_profile,
        annual_income,
        loan_amount,
        credit_limit,
        loan_term
    )

    (
        dti_ratio,
        credit_utilization,
        payment_burden_ratio,
        loan_to_income_ratio,
        collateral_coverage_ratio
    ) = create_credit_ratios(
        annual_income,
        loan_amount,
        credit_limit,
        revolving_balance,
        monthly_payment,
        collateral_value
    )

    (
        macro_sensitivity,
        interest_rate_sensitivity,
        unemployment_sensitivity
    ) = generate_macro_sensitivity(
        risk_profile
    )

    (
        behavioral_risk_score,
        risk_migration_score,
        early_warning_score
    ) = generate_ews_scores(
        dti_ratio,
        credit_utilization,
        delinq_2yrs,
        days_past_due
    )

    ifrs_stage, watchlist_flag = (
        generate_ifrs_stage(
            days_past_due
        )
    )

    target_default = (
        generate_default_target(
            risk_profile,
            dti_ratio,
            credit_utilization,
            delinq_2yrs,
            employment_years,
            interest_rate
        )
    )

    lgd_seed, ead_seed = (
        generate_lgd_ead_seed(
            credit_utilization,
            dti_ratio,
            loan_amount,
            collateral_value
        )
    )

    df = pd.DataFrame({

        "borrower_id": borrower_id,
        "age": age,
        "annual_income": annual_income,
        "employment_years": employment_years,

        "industry": industry,
        "region": region,
        "risk_profile": risk_profile,

        "loan_amount": loan_amount,
        "interest_rate": interest_rate,
        "loan_term": loan_term,

        "credit_limit": credit_limit,
        "revolving_balance": revolving_balance,

        "monthly_payment": monthly_payment,

        "delinq_2yrs": delinq_2yrs,
        "days_past_due": days_past_due,

        "collateral_value": collateral_value,

        "dti_ratio": dti_ratio,
        "credit_utilization": credit_utilization,
        "payment_burden_ratio": payment_burden_ratio,
        "loan_to_income_ratio": loan_to_income_ratio,
        "collateral_coverage_ratio": collateral_coverage_ratio,

        "macro_sensitivity": macro_sensitivity,
        "interest_rate_sensitivity": interest_rate_sensitivity,
        "unemployment_sensitivity": unemployment_sensitivity,

        "behavioral_risk_score": behavioral_risk_score,
        "risk_migration_score": risk_migration_score,
        "early_warning_score": early_warning_score,

        "ifrs_stage": ifrs_stage,
        "watchlist_flag": watchlist_flag,

        "target_default": target_default,

        "lgd_seed": lgd_seed,
        "ead_seed": ead_seed,
    })

    print(f"[KRONOS] Generated {len(df):,} borrowers")

    return df

# =============================================================================
# SAVE DATASET
# =============================================================================

def save_dataset(df):

    MASTER_CREDIT_DATA.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        MASTER_CREDIT_DATA,
        index=False
    )

    print("\n[KRONOS] Dataset saved:")
    print(MASTER_CREDIT_DATA)

# =============================================================================
# LOAD OR GENERATE
# =============================================================================

def load_master_dataset():

    if MASTER_CREDIT_DATA.exists():

        print("\n[KRONOS] Existing dataset found")

        return pd.read_csv(
            MASTER_CREDIT_DATA
        )

    df = generate_portfolio()

    save_dataset(df)

    return df

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":

    df = generate_portfolio()

    save_dataset(df)

    print("\nShape:", df.shape)

    print(
        "\nDefault Rate:",
        round(
            df["target_default"].mean() * 100,
            2
        ),
        "%"
    )

    print("\n[KRONOS] PORTFOLIO GENERATION COMPLETED")

# =============================================================================
# END OF FILE
# =============================================================================
