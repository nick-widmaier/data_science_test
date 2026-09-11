import sqlite3
import subprocess
import pandas as pd
import streamlit as st
from setup_env import setup_assessment_environment

st.set_page_config(
    page_title="Data Science Technical Assessment", page_icon="⚡", layout="wide"
)


# Cache environment setup so it only runs ONCE on app startup
@st.cache_resource
def init_app_environment():
    setup_assessment_environment()
    return True


init_app_environment()

st.title("⚡ Data Science Technical Assessment")
# ... (rest of your UI header layout) ...

# Inside TAB 1 (SQL Section) query test button:
if st.button("▶️ Test SQL Queries", type="primary"):
    # Add timeout=20.0 to prevent database locks during reads
    conn = sqlite3.connect("assessment.db", timeout=20.0)
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
