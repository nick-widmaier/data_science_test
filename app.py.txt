import os
import sqlite3
import subprocess
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Data Science Technical Assessment", page_icon="⚡", layout="wide"
)

# Initialize environment if missing
if not os.path.exists("assessment.db") or not os.path.exists("customer_data.csv"):
    from setup_env import setup_assessment_environment

    setup_assessment_environment()

st.title("⚡ Data Science Technical Assessment")
st.caption("Target Level: Entry to Mid Level | Duration: 75 Minutes")
st.markdown("---")

tab_sql, tab_python = st.tabs(["🗄️ SQL Section (3 Tasks)", "🐍 Python Section (3 Tasks)"])

# ==============================================================================
# TAB 1: SQL SECTION
# ==============================================================================
with tab_sql:
    st.header("SQL Analytics Tasks")

    col_q1, col_q2, col_q3 = st.columns(3)
    with col_q1:
        st.subheader("Task 1: Customer Spend Tiers")
        st.markdown(
            "Write a query returning `customer_id`, `customer_name`, `completed_orders`, `total_spent`, and `customer_tier` ('Tier 1' $\ge 500$, 'Tier 2' $\ge 100$, 'Tier 3' $< 100$)."
        )
    with col_q2:
        st.subheader("Task 2: Order Ranking")
        st.markdown(
            "Rank completed orders per customer by `order_amount` DESC using `DENSE_RANK()`. Include `order_id`, `customer_id`, `order_date`, `order_amount`, `amount_rank`."
        )
    with col_q3:
        st.subheader("Task 3: Running Spend")
        st.markdown(
            "Calculate cumulative running total spend per customer ordered by date. Include `order_id`, `customer_id`, `order_date`, `order_amount`, `running_total`."
        )

    st.markdown("---")

    sql_code_1 = st.text_area(
        "SQL Query Task 1:",
        value="SELECT c.customer_id, c.customer_name, COUNT(o.order_id) AS completed_orders, COALESCE(SUM(o.order_amount), 0) AS total_spent, CASE WHEN COALESCE(SUM(o.order_amount), 0) >= 500 THEN 'Tier 1' WHEN COALESCE(SUM(o.order_amount), 0) >= 100 THEN 'Tier 2' ELSE 'Tier 3' END AS customer_tier FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.status = 'completed' GROUP BY c.customer_id, c.customer_name ORDER BY total_spent DESC, c.customer_id ASC;",
        height=120,
    )
    sql_code_2 = st.text_area(
        "SQL Query Task 2:",
        value="SELECT order_id, customer_id, order_date, order_amount, DENSE_RANK() OVER (PARTITION BY customer_id ORDER BY order_amount DESC) AS amount_rank FROM orders WHERE status = 'completed' ORDER BY customer_id ASC, amount_rank ASC;",
        height=120,
    )
    sql_code_3 = st.text_area(
        "SQL Query Task 3:",
        value="SELECT order_id, customer_id, order_date, order_amount, SUM(order_amount) OVER (PARTITION BY customer_id ORDER BY order_date ASC) AS running_total FROM orders WHERE status = 'completed' ORDER BY customer_id ASC, order_date ASC;",
        height=120,
    )

    if st.button("▶️ Test SQL Queries", type="primary"):
        conn = sqlite3.connect("assessment.db")
        try:
            st.success("Task 1 Results:")
            st.dataframe(
                pd.read_sql_query(sql_code_1, conn), use_container_width=True
            )
            st.success("Task 2 Results:")
            st.dataframe(
                pd.read_sql_query(sql_code_2, conn), use_container_width=True
            )
            st.success("Task 3 Results:")
            st.dataframe(
                pd.read_sql_query(sql_code_3, conn), use_container_width=True
            )
        except Exception as e:
            st.error(f"SQL Error: {e}")
        finally:
            conn.close()

# ==============================================================================
# TAB 2: PYTHON SECTION
# ==============================================================================
with tab_python:
    st.header("Python DS Tasks (Pandas, NumPy, Scikit-Learn)")

    p_col1, p_col2 = st.columns([1, 1])

    with p_col1:
        st.subheader("Instructions")
        st.markdown("""
        **Task 1:** Complete `clean_and_transform_data(df)`:
        - Median imputation for missing `monthly_spend`.
        - IQR outlier capping for `monthly_spend`.
        - Add `log_account_length = np.log1p(account_length)`.

        **Task 2:** Complete `build_preprocessor(num_cols, cat_cols)`:
        - Return `ColumnTransformer` (median impute + StandardScaler for numeric, most_frequent + OneHotEncoder for categorical).

        **Task 3:** Complete `train_and_evaluate_model(...)`:
        - Construct Pipeline with preprocessor & `RandomForestClassifier(n_estimators=50, random_state=42)`.
        - Return ROC-AUC score rounded to 4 decimals.
        """)

        st.subheader("Data Preview (`customer_data.csv`)")
        st.dataframe(pd.read_csv("customer_data.csv").head(6), use_container_width=True)

    with p_col2:
        st.subheader("Python Editor")
        py_code = st.text_area(
            "Write your solutions below:",
            value='''import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score

def clean_and_transform_data(df: pd.DataFrame) -> pd.DataFrame:
    df_clean = df.copy()
    median_val = df_clean['monthly_spend'].median()
    df_clean['monthly_spend'] = df_clean['monthly_spend'].fillna(median_val)
    
    q1 = df_clean['monthly_spend'].quantile(0.25)
    q3 = df_clean['monthly_spend'].quantile(0.75)
    iqr = q3 - q1
    df_clean['monthly_spend'] = np.clip(df_clean['monthly_spend'], q1 - 1.5*iqr, q3 + 1.5*iqr)
    df_clean['log_account_length'] = np.log1p(df_clean['account_length'])
    return df_clean

def build_preprocessor(num_cols: list[str], cat_cols: list[str]) -> ColumnTransformer:
    num_pipe = Pipeline([('imputer', SimpleImputer(strategy='median')), ('scaler', StandardScaler())])
    cat_pipe = Pipeline([('imputer', SimpleImputer(strategy='most_frequent')), ('encoder', OneHotEncoder(drop='first', sparse_output=False))])
    return ColumnTransformer([('num', num_pipe, num_cols), ('cat', cat_pipe, cat_cols)])

def train_and_evaluate_model(X_train, X_test, y_train, y_test, preprocessor) -> float:
    clf_pipeline = Pipeline([('preprocessor', preprocessor), ('clf', RandomForestClassifier(n_estimators=50, random_state=42))])
    clf_pipeline.fit(X_train, y_train)
    probas = clf_pipeline.predict_proba(X_test)[:, 1]
    return round(float(roc_auc_score(y_test, probas)), 4)
''',
            height=400,
        )

        if st.button("🚀 Run Pytest Suite", type="primary", use_container_width=True):
            with open("candidate_code.py", "w") as f:
                f.write(py_code)

            with st.spinner("Running unit tests..."):
                res = subprocess.run(
                    ["pytest", "test_suite.py", "-v", "--color=no"],
                    capture_output=True,
                    text=True,
                )

            if res.returncode == 0:
                st.success("🎉 ALL PYTHON & SQL TESTS PASSED!")
            else:
                st.error("❌ TEST FAILURES DETECTED")

            with st.expander("Pytest Output Logs", expanded=True):
                st.code(res.stdout if res.stdout else res.stderr, language="text")