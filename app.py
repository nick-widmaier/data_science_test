import os
import sqlite3
import subprocess
import pandas as pd
import resend
import streamlit as st
from setup_env import setup_assessment_environment

# Configure Page
st.set_page_config(
    page_title="Data Science Assessment Portal", page_icon="⚡", layout="wide"
)

# Initialize environment cached
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

    # Email payload
    params = {
        "from": "Assessment Portal <onboarding@resend.dev>",
        "to": [recipient],
        "reply_to": c_email,  # Replying to this email in your inbox emails the candidate
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


# --- Keep your Tab 1 (SQL) and Tab 2 (Python) code as-is ---


# ==============================================================================
# TAB 3: FINAL SUBMISSION SECTION
# ==============================================================================
# Inside Tab 3 submit logic:
with tab_submit:
    st.header("Section 3: Final Submission")
    st.markdown("Review your solutions below and enter your details to complete your assessment submission.")
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
