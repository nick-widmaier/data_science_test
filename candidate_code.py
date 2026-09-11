import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def clean_and_transform_data(df: pd.DataFrame) -> pd.DataFrame:
    df_clean = df.copy()

    # 1. Median Imputation
    median_val = df_clean["monthly_spend"].median()
    df_clean["monthly_spend"] = df_clean["monthly_spend"].fillna(median_val)

    # 2. IQR Outlier Capping
    q1 = df_clean["monthly_spend"].quantile(0.25)
    q3 = df_clean["monthly_spend"].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    df_clean["monthly_spend"] = np.clip(
        df_clean["monthly_spend"], lower_bound, upper_bound
    )

    # 3. Log Feature Engineering
    df_clean["log_account_length"] = np.log1p(df_clean["account_length"])

    return df_clean


def build_preprocessor(
    num_cols: list[str], cat_cols: list[str]
) -> ColumnTransformer:
    num_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    # handle_unknown='ignore' prevents unknown category crashes during predict/transform
    cat_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        (
            "encoder",
            OneHotEncoder(
                drop="first", handle_unknown="ignore", sparse_output=False
            ),
        ),
    ])

    return ColumnTransformer([
        ("num", num_pipe, num_cols),
        ("cat", cat_pipe, cat_cols),
    ])


def train_and_evaluate_model(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
    preprocessor: ColumnTransformer,
) -> float:
    clf_pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("clf", RandomForestClassifier(n_estimators=50, random_state=42)),
    ])

    clf_pipeline.fit(X_train, y_train)
    probas = clf_pipeline.predict_proba(X_test)[:, 1]

    auc_score = roc_auc_score(y_test, probas)
    return round(float(auc_score), 4)
