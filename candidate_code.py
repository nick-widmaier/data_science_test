import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# ==============================================================================
# Python Task 1: Data Cleaning & Feature Transformation (Pandas & NumPy)
# ==============================================================================
def clean_and_transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """Imputes missing monthly_spend using median, caps outliers using IQR

    bounds, and creates log_account_length = log1p(account_length).
    """
    # TODO: Implement solution
    pass


# ==============================================================================
# Python Task 2: Scikit-Learn Preprocessing Pipeline
# ==============================================================================
def build_preprocessor(
    num_cols: list[str], cat_cols: list[str]
) -> ColumnTransformer:
    """Returns a ColumnTransformer scaling numeric features and one-hot encoding

    categorical features.
    """
    # TODO: Implement solution
    pass


# ==============================================================================
# Python Task 3: Model Training & ROC-AUC Evaluation
# ==============================================================================
def train_and_evaluate_model(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
    preprocessor: ColumnTransformer,
) -> float:
    """Combines preprocessor and RandomForestClassifier(n_estimators=50,

    random_state=42) into a Pipeline, fits training data, and returns ROC-AUC
    score on test set (rounded to 4 decimal places).
    """
    # TODO: Implement solution
    pass