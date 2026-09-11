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
# SQL Unit Tests
# ==============================================================================
@pytest.fixture
def db_connection():
    conn = sqlite3.connect("assessment.db")
    yield conn
    conn.close()


def test_sql_task1(db_connection, candidate_sql_queries):
    query = candidate_sql_queries.get("sql_task1", "")
    df = pd.read_sql_query(query, db_connection)

    assert len(df) == 4, "SQL Task 1: Should return 4 customers."
    assert "customer_tier" in df.columns, "SQL Task 1: Missing customer_tier column."
    assert df.loc[df["customer_id"] == 1, "customer_tier"].values[0] == "Tier 1"


def test_sql_task2(db_connection, candidate_sql_queries):
    query = candidate_sql_queries.get("sql_task2", "")
    df = pd.read_sql_query(query, db_connection)

    assert "amount_rank" in df.columns, "SQL Task 2: Missing amount_rank column."
    assert (
        df.loc[df["order_id"] == 105, "amount_rank"].values[0] == 1
    ), "SQL Task 2: Rank calculation incorrect."


def test_sql_task3(db_connection, candidate_sql_queries):
    query = candidate_sql_queries.get("sql_task3", "")
    df = pd.read_sql_query(query, db_connection)

    assert "running_total" in df.columns, "SQL Task 3: Missing running_total column."
    assert (
        df.loc[df["order_id"] == 102, "running_total"].values[0] == 350.0
    ), "SQL Task 3: Running total incorrect."


# ==============================================================================
# Python Unit Tests
# ==============================================================================
@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "customer_id": [1, 2, 3, 4, 5],
        "account_length": [10, 20, 30, 40, 50],
        "monthly_spend": [50.0, np.nan, 60.0, 70.0, 2000.0],
        "tier": ["Basic", "VIP", "Premium", "Basic", "VIP"],
        "churn": [0, 1, 0, 0, 1],
    })


def test_python_task1(sample_df):
    res = clean_and_transform_data(sample_df)

    assert res["monthly_spend"].isna().sum() == 0, "Python Task 1: NaNs not imputed."
    assert (
        res["monthly_spend"].max() < 2000.0
    ), "Python Task 1: Outlier was not capped."
    assert (
        "log_account_length" in res.columns
    ), "Python Task 1: Missing log_account_length."


def test_python_task2():
    transformer = build_preprocessor(
        ["account_length", "monthly_spend"], ["tier"]
    )
    assert isinstance(
        transformer, ColumnTransformer
    ), "Python Task 2: Must return ColumnTransformer."


def test_python_task3(sample_df):
    cleaned = clean_and_transform_data(sample_df)
    X = cleaned[["account_length", "monthly_spend", "log_account_length", "tier"]]
    y = cleaned["churn"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.4, random_state=42
    )
    preprocessor = build_preprocessor(
        ["account_length", "monthly_spend", "log_account_length"], ["tier"]
    )

    auc = train_and_evaluate_model(X_train, X_test, y_train, y_test, preprocessor)
    assert isinstance(auc, float), "Python Task 3: Should return float ROC-AUC score."