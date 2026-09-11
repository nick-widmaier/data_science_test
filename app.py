import os
import sqlite3
import subprocess
import pandas as pd
import streamlit as st
from setup_env import setup_assessment_environment

# Configure Streamlit Page
st.set_page_config(
    page_title="Data Science Assessment Portal", page_icon="⚡", layout="wide"
)


# Cache environment setup so it runs ONCE on server startup
@st.cache_resource
def init_app_environment():
    setup_assessment_environment()
    return True


init_app_environment()

# --- Application Header ---
st.title("⚡ Data Science & Analytics Assessment")
st.caption("Target Level: Entry to Mid-Level Data Scientist | Time Limit: 75 Minutes")
st.markdown("---")

# Main Navigation Tabs
tab_sql, tab_python = st.tabs(
    ["🗄️ Section 1: SQL Analytics (3 Tasks)", "🐍 Section 2: Python & ML Pipeline (3 Tasks)"]
)


# ==============================================================================
# TAB 1: SQL SECTION
# ==============================================================================
with tab_sql:
    st.header("Section 1: SQL Analytics")
    st.markdown("Write SQL queries to answer the business questions below using the database schema provided.")

    # Schema & Sample Data Preview
    with st.expander("📖 View Database Schema & Sample Tables", expanded=False):
        conn = sqlite3.connect("assessment.db", timeout=20.0)
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("`customers` Table")
            st.dataframe(pd.read_sql_query("SELECT * FROM customers", conn), use_container_width=True)
        with c2:
            st.subheader("`orders` Table")
            st.dataframe(pd.read_sql_query("SELECT * FROM orders", conn), use_container_width=True)
        conn.close()

    st.markdown("---")

    # SQL Task Descriptions
    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        st.subheader("Task 1: Spend Tiers")
        st.markdown("""
        Aggregate total spend and completed order count for **all customers** (including those with 0 completed orders). 
        
        Classify customer spend:
        - `'Tier 1'`: Spend $\ge \$500$
        - `'Tier 2'`: Spend between $\$100$ and $\$499.99$
        - `'Tier 3'`: Spend $< \$100$

        **Columns:** `customer_id`, `customer_name`, `completed_orders`, `total_spent`, `customer_tier`
        """)

    with col2:
        st.subheader("Task 2: Order Ranking")
        st.markdown("""
        Rank all **completed orders** for each customer based on `order_amount` in descending order using `DENSE_RANK()`.

        <br>

        **Columns:** `order_id`, `customer_id`, `order_date`, `order_amount`, `amount_rank`  
        **Sort:** `customer_id` ASC, `amount_rank` ASC.
        """, unsafe_allow_html=True)

    with col3:
        st.subheader("Task 3: Cumulative Spend")
        st.markdown("""
        Calculate the **running cumulative spend** over time for each customer across completed orders ordered by `order_date`.

        <br>

        **Columns:** `order_id`, `customer_id`, `order_date`, `order_amount`, `running_total`  
        **Sort:** `customer_id` ASC, `order_date` ASC.
        """, unsafe_allow_html=True)

    st.markdown("---")

    # SQL Code Inputs
    st.subheader("📝 SQL Code Editors")

    sql_code_1 = st.text_area(
        "SQL Editor - Task 1 (Spend Tiers):",
        value="""-- Write your SQL query for Task 1 below
SELECT 
    c.customer_id,
    c.customer_name,
    COUNT(o.order_id) AS completed_orders,
    COALESCE(SUM(o.order_amount), 0) AS total_spent,
    CASE 
        WHEN COALESCE(SUM(o.order_amount), 0) >= 500 THEN 'Tier 1'
        WHEN COALESCE(SUM(o.order_amount), 0) >= 100 THEN 'Tier 2'
        ELSE 'Tier 3'
    END AS customer_tier
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.status = 'completed'
GROUP BY c.customer_id, c.customer_name
ORDER BY total_spent DESC, c.customer_id ASC;""",
        height=140,
    )

    sql_code_2 = st.text_area(
        "SQL Editor - Task 2 (Order Ranking):",
        value="""-- Write your SQL query for Task 2 below
SELECT 
    order_id,
    customer_id,
    order_date,
    order_amount,
    DENSE_RANK() OVER (PARTITION BY customer_id ORDER BY order_amount DESC) AS amount_rank
FROM orders
WHERE status = 'completed'
ORDER BY customer_id ASC, amount_rank ASC;""",
        height=140,
    )

    sql_code_3 = st.text_area(
        "SQL Editor - Task 3 (Cumulative Spend):",
        value="""-- Write your SQL query for Task 3 below
SELECT 
    order_id,
    customer_id,
    order_date,
    order_amount,
    SUM(order_amount) OVER (PARTITION BY customer_id ORDER BY order_date ASC) AS running_total
FROM orders
WHERE status = 'completed'
ORDER BY customer_id ASC, order_date ASC;""",
        height=140,
    )

    # SQL Execution Button
    if st.button("▶️ Run & Validate SQL Queries", type="primary", use_container_width=True):
        conn = sqlite3.connect("assessment.db", timeout=20.0)
        st.markdown("### 📊 SQL Query Output & Validation")

        res_col1, res_col2, res_col3 = st.columns(3)

        # Validate Task 1
        with res_col1:
            st.subheader("Task 1 Results")
            try:
                df1 = pd.read_sql_query(sql_code_1, conn)
                st.dataframe(df1, use_container_width=True)
                req_cols1 = {"customer_id", "customer_name", "completed_orders", "total_spent", "customer_tier"}
                if req_cols1.issubset(set(df1.columns.str.lower())):
                    st.success("✅ Output schema valid!")
                else:
                    st.error(f"❌ Missing required columns: {req_cols1 - set(df1.columns.str.lower())}")
            except Exception as e:
                st.error(f"❌ Query Error: {e}")

        # Validate Task 2
        with res_col2:
            st.subheader("Task 2 Results")
            try:
                df2 = pd.read_sql_query(sql_code_2, conn)
                st.dataframe(df2, use_container_width=True)
                if "amount_rank" in df2.columns.str.lower():
                    st.success("✅ Output schema valid!")
                else:
                    st.error("❌ Missing column 'amount_rank'.")
            except Exception as e:
                st.error(f"❌ Query Error: {e}")

        # Validate Task 3
        with res_col3:
            st.subheader("Task 3 Results")
            try:
                df3 = pd.read_sql_query(sql_code_3, conn)
                st.dataframe(df3, use_container_width=True)
                if "running_total" in df3.columns.str.lower():
                    st.success("✅ Output schema valid!")
                else:
                    st.error("❌ Missing column 'running_total'.")
            except Exception as e:
                st.error(f"❌ Query Error: {e}")

        conn.close()


# ==============================================================================
# TAB 2: PYTHON SECTION
# ==============================================================================
with tab_python:
    st.header("Section 2: Python Data Science Pipeline")

    p_col_left, p_col_right = st.columns([1, 1], gap="medium")

    with p_col_left:
        st.subheader("📋 Instructions")
        st.markdown("""
        Complete the three Python functions in the editor to process data and build a Scikit-Learn pipeline.

        #### Task 1: Data Cleaning & Feature Transformation (Pandas & NumPy)
        Write `clean_and_transform_data(df)`:
        1. **Impute missing values** in `monthly_spend` using the column median.
        2. **Cap outliers** in `monthly_spend` outside $[Q1 - 1.5 \\times IQR, \\quad Q3 + 1.5 \\times IQR]$.
        3. **Create feature** `log_account_length` using $\\log(1 + X)$ via `np.log1p(account_length)`.

        #### Task 2: Scikit-Learn Preprocessing Pipeline
        Write `build_preprocessor(num_cols, cat_cols)`:
        1. Construct a `ColumnTransformer` with numeric pipeline (`SimpleImputer(median)` $\\rightarrow$ `StandardScaler`) and categorical pipeline (`SimpleImputer(most_frequent)` $\\rightarrow$ `OneHotEncoder(drop='first', sparse_output=False)`).

        #### Task 3: Model Pipeline & Evaluation
        Write `train_and_evaluate_model(X_train, X_test, y_train, y_test, preprocessor)`:
        1. Combine `preprocessor` and `RandomForestClassifier(n_estimators=50, random_state=42)` into a `Pipeline`.
        2. Fit on training data and return the **ROC-AUC score** on test data rounded to 4 decimals.
        """)

        st.markdown("---")
        st.subheader("Sample Dataset (`customer_data.csv`)")
        st.dataframe(pd.read_csv("customer_data.csv").head(6), use_container_width=True)

    with p_col_right:
        st.subheader("📝 Python Code Editor")

        py_code_starter = '''import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score

# ==============================================================================
# Task 1: Data Cleaning & Feature Engineering
# ==============================================================================
def clean_and_transform_data(df: pd.DataFrame) -> pd.DataFrame:
    df_clean = df.copy()
    
    # 1. Impute missing monthly_spend with median
    median_val = df_clean['monthly_spend'].median()
    df_clean['monthly_spend'] = df_clean['monthly_spend'].fillna(median_val)
    
    # 2. IQR Outlier capping
    q1 = df_clean['monthly_spend'].quantile(0.25)
    q3 = df_clean['monthly_spend'].quantile(0.75)
    iqr = q3 - q1
    df_clean['monthly_spend'] = np.clip(df_clean['monthly_spend'], q1 - 1.5 * iqr, q3 + 1.5 * iqr)
    
    # 3. Log transformation
    df_clean['log_account_length'] = np.log1p(df_clean['account_length'])
    
    return df_clean

# ==============================================================================
# Task 2: Modular Preprocessing Pipeline
# ==============================================================================
def build_preprocessor(num_cols: list[str], cat_cols: list[str]) -> ColumnTransformer:
    num_pipe = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    cat_pipe = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('encoder', OneHotEncoder(drop='first', sparse_output=False))
    ])
    
    return ColumnTransformer([
        ('num', num_pipe, num_cols),
        ('cat', cat_pipe, cat_cols)
    ])

# ==============================================================================
# Task 3: Model Training & Evaluation
# ==============================================================================
def train_and_evaluate_model(X_train, X_test, y_train, y_test, preprocessor) -> float:
    clf_pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('clf', RandomForestClassifier(n_estimators=50, random_state=42))
    ])
    
    clf_pipeline.fit(X_train, y_train)
    probas = clf_pipeline.predict_proba(X_test)[:, 1]
    
    return round(float(roc_auc_score(y_test, probas)), 4)
'''

        py_code = st.text_area(
            "Write your solutions below:",
            value=py_code_starter,
            height=460,
        )

        if st.button("🚀 Run Pytest Suite", type="primary", use_container_width=True):
            with open("candidate_code.py", "w") as f:
                f.write(py_code)

            with st.spinner("Running automated test suite..."):
                res = subprocess.run(
                    ["pytest", "test_suite.py", "-v", "--color=no"],
                    capture_output=True,
                    text=True,
                )

            st.markdown("### 🧪 Test Suite Results")
            if res.returncode == 0:
                st.success("🎉 ALL UNIT TESTS PASSED SUCCESSFULLY!")
            else:
                st.error("❌ TEST FAILURES DETECTED")

            with st.expander("View Terminal Execution Output", expanded=True):
                st.code(res.stdout if res.stdout else res.stderr, language="text")
