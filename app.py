import streamlit as st
import tempfile
import os
from model import predict_log_risk, train_model, load_model
from utils import generate_excel_report
import pandas as pd

st.set_page_config(page_title="CyberLens: SSH Intrusion Detection", layout="wide")

st.title("🛡️ CyberLens: AI-based SSH Intrusion Detector")
st.markdown("Analyze SSH logs to detect abnormal login behavior using AI-powered anomaly detection.")

# Sidebar: model options
st.sidebar.header("Model Options")
model_mode = st.sidebar.radio("Choose model action", ["Load existing model", "Train new model"])

if model_mode == "Train new model":
    n_estimators = st.sidebar.slider("n_estimators", 50, 500, 150, step=50)
    contamination = st.sidebar.slider("contamination", 0.01, 0.3, 0.1, step=0.01)

    @st.cache_resource
    def retrain_model():
        df = pd.read_csv("logs/simulated_log.csv")
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        train_model(df, n_estimators=n_estimators, contamination=contamination)
        return "Model trained and saved."

    retrain_status = retrain_model()
    st.sidebar.success(retrain_status)

else:
    @st.cache_resource
    def load_saved_model_safe():
        try:
            load_model()
            return "Model loaded from disk."
        except FileNotFoundError:
            return "❌ Model not found. Please switch to 'Train new model'."

    load_status = load_saved_model_safe()
    if "not found" in load_status:
        st.sidebar.error(load_status)
    else:
        st.sidebar.success(load_status)

# Sidebar: log input
st.sidebar.header("Log Source")
use_sample = st.sidebar.checkbox("Use simulated_log.txt", value=True)
uploaded_file = None
if not use_sample:
    uploaded_file = st.sidebar.file_uploader("Upload SSH log file (.txt)", type=["txt"])

# Main: Analyze button
if st.button("Analyze Logs"):
    if use_sample:
        log_path = "logs/simulated_log.txt"
    elif uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp_file:
            tmp_file.write(uploaded_file.read())
            log_path = tmp_file.name
    else:
        st.warning("Please upload a log file or use the simulated one.")
        st.stop()

    with st.spinner("Analyzing logs..."):
        results, result_df = predict_log_risk(log_path)

    st.success(f"Analyzed {len(results)} log entries")

    # Dashboard
    st.subheader("📊 Risk Summary Dashboard")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Logs", len(result_df))
    col2.metric("High Risk", (result_df["risk_level"] == "high").sum())
    col3.metric("Medium Risk", (result_df["risk_level"] == "medium").sum())
    col4.metric("Low Risk", (result_df["risk_level"] == "low").sum())

    st.markdown("### Risk Level Distribution")
    risk_counts = result_df["risk_level"].value_counts()
    st.bar_chart(risk_counts)

    st.markdown("### Top Risky IP Addresses")
    top_ips = result_df[result_df["risk_level"] != "low"]["ip"].value_counts().head(10)
    st.dataframe(top_ips.rename("Count"))

    st.markdown("### Log Entries by Hour of Day")
    result_df["hour"] = result_df["timestamp"].dt.hour
    hourly_counts = result_df["hour"].value_counts().sort_index()
    st.line_chart(hourly_counts)

    st.markdown("### 🔍 Detailed Log Results")
    for res in results:
        color = "🔴" if res["risk_level"] == "high" else ("🟠" if res["risk_level"] == "medium" else "🟢")
        st.markdown(f"**{color} {res['risk_level'].capitalize()}** - `{res['line']}`")
        st.caption(res["reason"])

    if not use_sample and os.path.exists(log_path):
        os.remove(log_path)

    # Export button
    st.markdown("### 📤 Export Report")
    excel_data = generate_excel_report(result_df)

    st.download_button(
        label="📥 Download Excel Report",
        data=excel_data,
        file_name="output/cyberlens_summary_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
