import streamlit as st
import pandas as pd
from datetime import datetime
import os
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Cold-Chain Decision Support Dashboard", layout="wide")

DATA_FILE = "Decision_Support_Output.xlsx"
AUDIT_FILE = "audit_log.csv"

# -----------------------------
# AUTO REFRESH (1 minute)
# -----------------------------
st_autorefresh(interval=60000, key="datarefresh")

# -----------------------------
# LOAD DATA (refresh every 1 minute)
# -----------------------------
@st.cache_data(ttl=60)
def load_data():
    if DATA_FILE.endswith(".xlsx"):
        return pd.read_excel(DATA_FILE)
    else:
        return pd.read_csv(DATA_FILE)

df = load_data()

# -----------------------------
# HEADER
# -----------------------------
st.title("🚚 Cold-Chain Decision Support Dashboard")

# -----------------------------
# RISK SUMMARY
# -----------------------------
green = (df["risk_level"] == "GREEN").sum()
yellow = (df["risk_level"] == "YELLOW").sum()
red = (df["risk_level"] == "RED").sum()

col1, col2, col3 = st.columns(3)

col1.metric("🟢 GREEN (Safe)", green)
col2.metric("🟡 YELLOW (Warning)", yellow)
col3.metric("🔴 RED (Critical)", red)

if red > 0:
    st.error(f"🚨 CRITICAL ALERT: {red} shipments are at HIGH RISK!")

# -----------------------------
# SHIPMENTS REQUIRING ATTENTION
# -----------------------------
st.subheader("⚠️ Shipments Requiring Attention (YELLOW & RED)")

attention_df = df[df["risk_level"].isin(["YELLOW", "RED"])]

st.dataframe(
    attention_df[
        [
            "shipment_id",
            "risk_level",
            "risk_score",
            "top_cause",
            "top_recommendation"
        ]
    ],
    use_container_width=True
)

# -----------------------------
# SHIPMENT DETAILS
# -----------------------------
st.subheader("🔍 Shipment Details")

selected_shipment = st.selectbox(
    "Select a shipment to view details",
    df["shipment_id"].unique()
)

shipment = df[df["shipment_id"] == selected_shipment].iloc[0]

# -----------------------------
# RISK OVERVIEW
# -----------------------------
st.markdown("### 📊 Risk Overview")

st.write(f"**Risk Level:** {shipment['risk_level']}")
st.write(f"**Risk Score:** {shipment['risk_score']}")
st.write(f"**Spoilage Probability:** {shipment['spoilage_probability']*100:.1f}%")

# -----------------------------
# ROOT CAUSE ANALYSIS
# -----------------------------
st.markdown("### 🔎 Root Cause Analysis")

st.write(f"**Top Cause:** {shipment['top_cause']}")
st.write(shipment["root_cause_summary"])

# -----------------------------
# RECOMMENDATION
# -----------------------------
st.markdown("### 🛠 Recommended Action")

st.success(shipment["top_recommendation"])

# -----------------------------
# HUMAN-IN-THE-LOOP SECTION
# -----------------------------
st.markdown("### 👤 Operator Decision (Human-in-the-Loop)")

decision = st.radio(
    "Decision",
    ["Approve", "Modify", "Reject"],
    horizontal=True
)

notes = st.text_area("Operator Notes (optional)")

# -----------------------------
# SAVE DECISION TO AUDIT LOG
# -----------------------------
if st.button("✅ Submit Decision"):

    log_entry = {
        "shipment_id": shipment["shipment_id"],
        "risk_level": shipment["risk_level"],
        "risk_score": shipment["risk_score"],
        "recommendation": shipment["top_recommendation"],
        "operator_decision": decision,
        "operator_notes": notes,
        "timestamp": datetime.now().isoformat()
    }

    if os.path.exists(AUDIT_FILE):

        audit_df = pd.read_csv(AUDIT_FILE)

        audit_df = pd.concat(
            [audit_df, pd.DataFrame([log_entry])],
            ignore_index=True
        )

    else:

        audit_df = pd.DataFrame([log_entry])

    audit_df.to_csv(AUDIT_FILE, index=False)

    st.success("✅ Decision logged successfully to audit trail!")

# -----------------------------
# FOOTER
# -----------------------------
st.caption("Cold-Chain Decision Support System | Agentic AI + Human-in-the-Loop")
