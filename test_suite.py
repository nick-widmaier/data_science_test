import json
import os
import sqlite3
import numpy as np
import pandas as pd
import pytest
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split

from candidate_code import (
    build_preprocessor,
    clean_and_transform_data,
    train_and_evaluate_model,
)


# ==============================================================================
# Fixtures
# ==============================================================================
@pytest.fixture
def db_connection():
    conn = sqlite3.connect("assessment.db")
    yield conn
    conn.close()


@pytest.fixture
def candidate_sql():
    if os.path.exists("candidate_sql.json"):
        with open("candidate_sql.json") as f:
            return json.load(f)
    return {}


@pytest.fixture
def sample_df():
    np.random.seed(42)
    n_samples = 30
    df = pd.DataFrame({
        "customer_id": np.arange(1, n_samples + 1),
        "account_length": np.random.randint(1, 50, size=n_samples),
        "monthly_spend": np.random.uniform(10.0, 100.0, size=n_samples),
        "tier": np.random.choice(["Basic", "Premium", "VIP"], size=n_samples),
        "churn": np.random.choice([0, 1], size=n_samples, p=[0.6, 0.4]),
    })
    df.loc[::5, "monthly_spend"] = np.nan
    df.loc[3, "monthly_spend"] = 1500.0  # Outlier
    return df


# ==============================================================================
# SQL Unit Tests
# ==============================================================================
def test_sql_task1(db_connection, candidate_sql):
    query = candidate_sql.get("sql_q1", "")
    assert query.strip(), "SQL Task 1 query is empty."

    df = pd.read_sql_query(query, db_connection)
    assert len(df) == 4, "SQL Task 1: Should return 4 customers."
    assert "customer_tier" in df.columns.str.lower(), (
        "SQL Task 1: Missing 'customer_tier' column."
    )


def test_sql_task2(db_connection, candidate_sql):
    query = candidate_sql.get("sql_q2", "")
    assert query.strip(), "SQL Task 2 query is empty."

    df = pd.read_sql_query(query, db_connection)
    assert "amount_rank" in df.columns.str.lower(), (
        "SQL Task 2: Missing 'amount_rank' column."
    )


def test_sql_task3(db_connection, candidate_sql):
    query = candidate_sql.get("sql_q3", "")
    assert query.strip(), "SQL Task 3 query is empty."

    df = pd.read_sql_query(query, db_connection)
    assert "running_total" in df.columns.str.lower(), (
        "SQL Task 3: Missing 'running_total' column."
    )


# ==============================================================================
# Python Unit Tests
# ==============================================================================
def test_python_task1(sample_df):
    res = clean_and_transform_data(sample_df)

    assert res["monthly_spend"].isna().sum() == 0, (
        "Python Task 1: NaNs were not imputed."
    )
    assert res["monthly_spend"].max() < 1500.0, (
        "Python Task 1: Outlier was not capped."
    )
    assert "log_account_length" in res.columns, (
        "Python Task 1: Missing 'log_account_length' feature."
    )


def test_python_task2():
    transformer = build_preprocessor(
        ["account_length", "monthly_spend"], ["tier"]
    )
    assert isinstance(transformer, ColumnTransformer), (
        "Python Task 2: Must return a ColumnTransformer instance."
    )


def test_python_task3(sample_df):
    cleaned = clean_and_transform_data(sample_df)
    X = cleaned[
        ["account_length", "monthly_spend", "log_account_length", "tier"]
    ]
    y = cleaned["churn"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    preprocessor = build_preprocessor(
        ["account_length", "monthly_spend", "log_account_length"], ["tier"]
    )

    auc = train_and_evaluate_model(
        X_train, X_test, y_train, y_test, preprocessor
    )
    assert isinstance(auc, float), "Python Task 3: Should return a float."
    assert 0.0 <= auc <= 1.0, (
        "Python Task 3: ROC-AUC score must be between 0 and 1."
    )
