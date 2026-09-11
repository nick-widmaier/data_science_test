import os
import sqlite3
import subprocess
import pandas as pd
import resend
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

# Function to send submission via Resend API
def send_submission_via_resend(c_name, c_email, q1, q2, q3, py_code, test_passed, test_logs):
    api_key = st.secrets.get("RESEND_API_KEY", "")
    recipient = st.secrets.get("RECIPIENT_EMAIL", "")

    if not api_key or not recipient:
        raise ValueError("RESEND_API_KEY or RECIPIENT_EMAIL missing from Streamlit secrets!")

    resend.api_key = api_key

    params = {
        "from": "Assessment Portal <onboarding@resend.dev>",
        "to": [recipient],
        "reply_to": c_email,
        "subject": f"[Assessment Submission] {c_name} - ({'PASSED' if test_passed else 'FAILED'})",
        "html": f"""
        <h2>Datakaru Candidate Assessment Submission</h2>
        <p><b>Candidate Name:</b> {c_name}</p>
        <p><b>Candidate Email:</b> {c_email}</p>
        <p><b>Pytest Status:</b> {'<b style="color:green;">PASSED</b>' if test_passed else '<b style="color:red;">FAILED / UNCHECKED</b>'}</p>
        <hr>
        <h3>SQL Section Answers</h3>
        <h4>Task 1 (Spend Tiers)</h4>
        <pre>{q1}</pre>
        <h4>Task 2 (Order Ranking)</h4>
        <pre>{q2}</pre>
        <h4>Task 3 (Cumulative Spend)</h4>
        <pre>{q3}</pre>
        <hr>
        <h3>Python Pipeline Solution</h3>
        <pre>{py_code}</pre>
        <hr>
        <h3>Automated Test Execution Logs</h3>
        <pre>{test_logs}</pre>
        """
    }

    return resend.Emails.send(params)


# Initialize session state variables
if "sql_q1" not in st.session_state:
    st.session_state["sql_q1"] = ""
if "sql_q2" not in st.session_state:
    st.session_state["sql_q2"] = ""
if "sql_q3" not in st.session_state:
    st.session_state["sql_q3"] = ""
if "python_code" not in st.session_state:
    st.session_state["python_code"] = ""
if "test_passed" not in st.session_state:
    st.session_state["test_passed"] = False
if "test_logs" not in st.session_state:
    st.session_state["test_logs"] = "Tests have not been run yet."

# Application Header
st.title("⚡ Data Science & Analytics Assessment")
st.caption("Target Level: Entry to Mid-Level Data Scientist | Time Limit: 75 Minutes")
st.markdown("---")

# Instantiate Tabs
tab_sql, tab_python, tab_submit = st.tabs(
    [
        "🗄️ Section 1: SQL Analytics",
        "🐍 Section 2: Python & ML Pipeline",
        "🚀 Section 3: Final Submission",
    ]
)

# ==============================================================================
# TAB 1: SQL SECTION
# ==============================================================================
with tab_sql:
    st.header("Section 1: SQL Analytics")
    st.markdown("Write SQL queries to answer the business questions below using the database schema provided.")

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
    st.subheader("📝 SQL Code Editors")

    default_q1 = """-- Task 1: Customer Spend Tiers
-- Write your SQL query below:

"""

    default_q2 = """-- Task 2: Order Ranking per Customer
-- Write your SQL query below:

"""

    default_q3 = """-- Task 3: Running Cumulative Spend
-- Write your SQL query below:

"""

    st.session_state["sql_q1"] = st.text_area("SQL Editor - Task 1 (Spend Tiers):", value=default_q1, height=130)
    st.session_state["sql_q2"] = st.text_area("SQL Editor - Task 2 (Order Ranking):", value=default_q2, height=130)
    st.session_state["sql_q3"] = st.text_area("SQL Editor - Task 3 (Cumulative Spend):", value=default_q3, height=130)

    if st.button("▶️ Run & Validate SQL Queries", type="primary", use_container_width=True):
        conn = sqlite3.connect("assessment.db", timeout=20.0)
        st.markdown("### 📊 SQL Query Output & Validation")
        res_col1, res_col2, res_col3 = st.columns(3)

        with res_col1:
            st.subheader("Task 1 Results")
            try:
                df1 = pd.read_sql_query(st.session_state["sql_q1"], conn)
                st.dataframe(df1, use_container_width=True)
                st.success("✅ Output rendered!")
            except Exception as e:
                st.error(f"❌ Query Error: {e}")

        with res_col2:
            st.subheader("Task 2 Results")
            try:
                df2 = pd.read_sql_query(st.session_state["sql_q2"], conn)
                st.dataframe(df2, use_container_width=True)
                st.success("✅ Output rendered!")
            except Exception as e:
                st.error(f"❌ Query Error: {e}")

        with res_col3:
            st.subheader("Task 3 Results")
            try:
                df3 = pd.read_sql_query(st.session_state["sql_q3"], conn)
                st.dataframe(df3, use_container_width=True)
                st.success("✅ Output rendered!")
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

        #### Task 1: Data Cleaning & Feature Transformation
        Write `clean_and_transform_data(df)`:
        1. **Impute missing values** in `monthly_spend` using median.
        2. **Cap outliers** in `monthly_spend` outside $[Q1 - 1.5 \\times IQR, Q3 + 1.5 \\times IQR]$.
        3. **Create feature** `log_account_length` using `np.log1p(account_length)`.

        #### Task 2: Scikit-Learn Preprocessing Pipeline
        Write `build_preprocessor(num_cols, cat_cols)`:
        1. Construct a `ColumnTransformer` (median impute + StandardScaler for numeric, most_frequent + OneHotEncoder for categorical).

        #### Task 3: Model Pipeline & Evaluation
        Write `train_and_evaluate_model(X_train, X_test, y_train, y_test, preprocessor)`:
        1. Combine `preprocessor` and `RandomForestClassifier(n_estimators=50, random_state=42)` into a `Pipeline`.
        2. Fit training data and return **ROC-AUC score** rounded to 4 decimals.
        """)

        st.markdown("---")
        st.subheader("Sample Dataset Preview (`customer_data.csv`)")
        st.dataframe(pd.read_csv("customer_data.csv").head(6), use_container_width=True)

    with p_col_right:
        st.subheader("📝 Python Code Editor")

        py_starter = '''import pandas as pd
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
    """
    Imputes missing monthly_spend using median, caps outliers using IQR bounds,
    and creates log_account_length = log1p(account_length).
    """
    # TODO: Implement candidate solution
    pass

# ==============================================================================
# Task 2: Modular Preprocessing Pipeline
# ==============================================================================
def build_preprocessor(num_cols: list[str], cat_cols: list[str]) -> ColumnTransformer:
    """
    Returns a ColumnTransformer scaling numeric features and one-hot encoding categorical features.
    """
    # TODO: Implement candidate solution
    pass

# ==============================================================================
# Task 3: Model Training & Evaluation
# ==============================================================================
def train_and_evaluate_model(X_train, X_test, y_train, y_test, preprocessor) -> float:
    """
    Combines preprocessor and RandomForestClassifier(n_estimators=50, random_state=42) into a Pipeline,
    fits training data, and returns ROC-AUC score on test set (rounded to 4 decimal places).
    """
    # TODO: Implement candidate solution
    pass
'''

        st.session_state["python_code"] = st.text_area(
            "Write your solutions below:",
            value=py_starter,
            height=440,
        )

        if st.button("🚀 Run Pytest Suite", type="primary", use_container_width=True):
            with open("candidate_code.py", "w") as f:
                f.write(st.session_state["python_code"])

            with st.spinner("Running unit tests..."):
                res = subprocess.run(
                    ["pytest", "test_suite.py", "-v", "--color=no"],
                    capture_output=True,
                    text=True,
                )

            st.session_state["test_passed"] = (res.returncode == 0)
            st.session_state["test_logs"] = res.stdout if res.stdout else res.stderr

            if st.session_state["test_passed"]:
                st.success("🎉 ALL UNIT TESTS PASSED SUCCESSFULLY!")
            else:
                st.error("❌ TEST FAILURES DETECTED")

            with st.expander("View Terminal Execution Output", expanded=True):
                st.code(st.session_state["test_logs"], language="text")

# ==============================================================================
# TAB 3: FINAL SUBMISSION SECTION
# ==============================================================================
with tab_submit:
    st.header("Section 3: Final Submission")
    st.markdown("Review your solutions below and enter your details to submit your completed assessment.")
    st.markdown("---")

    with st.form("candidate_submission_form"):
        st.subheader("👤 Candidate Details")
        c_name = st.text_input("Full Name *", placeholder="Jane Doe")
        c_email = st.text_input("Email Address *", placeholder="jane.doe@example.com")

        st.markdown("---")
        st.subheader("📋 Submission Preview")
        st.markdown("**SQL Task 1 Answer:**")
        st.code(st.session_state.get("sql_q1", ""), language="sql")
        st.markdown("**SQL Task 2 Answer:**")
        st.code(st.session_state.get("sql_q2", ""), language="sql")
        st.markdown("**SQL Task 3 Answer:**")
        st.code(st.session_state.get("sql_q3", ""), language="sql")
        st.markdown("**Python Pipeline Solution:**")
        st.code(st.session_state.get("python_code", ""), language="python")
        st.markdown(
            f"**Pytest Automated Status:** {'🟢 Passed' if st.session_state.get('test_passed') else '🔴 Failed / Unchecked'}"
        )

        submit_button = st.form_submit_button("📤 Submit Final Assessment", type="primary", use_container_width=True)

        if submit_button:
            if not c_name.strip() or not c_email.strip():
                st.error("⚠️ Please enter both your Full Name and Email Address before submitting.")
            else:
                try:
                    with st.spinner("Submitting assessment to recruiting team..."):
                        send_submission_via_resend(
                            c_name.strip(),
                            c_email.strip(),
                            st.session_state.get("sql_q1", ""),
                            st.session_state.get("sql_q2", ""),
                            st.session_state.get("sql_q3", ""),
                            st.session_state.get("python_code", ""),
                            st.session_state.get("test_passed", False),
                            st.session_state.get("test_logs", ""),
                        )
                    st.balloons()
                    st.success("🎉 Assessment submitted successfully! Your responses have been sent to the recruiting team.")
                except Exception as ex:
                    st.error(f"❌ Submission failed: {ex}")
