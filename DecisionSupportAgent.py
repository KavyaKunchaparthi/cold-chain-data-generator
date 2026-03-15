import pandas as pd
import numpy as np
from datetime import datetime

def build_decision_support():

    agent2 = pd.read_excel("Agent2_Quality_Risk_Report.xlsx")
    agent3 = pd.read_excel("Agent3_Root_Cause_Report.xlsx")
    agent4 = pd.read_excel("Agent4_Prescriptive_Recommendations.xlsx")

    df = agent2.merge(agent3, on="shipment_id", suffixes=("_risk", "_cause"))
    df = df.merge(agent4, on="shipment_id")

    # -----------------------------
    # HUMAN REVIEW FIELDS
    # -----------------------------
    df["review_status"] = "PENDING"
    df["reviewed_by"] = ""
    df["review_notes"] = ""
    df["decision_timestamp"] = ""

    # -----------------------------
    # TIMESTAMP
    # -----------------------------
    df["generated_at"] = datetime.utcnow().isoformat()

    # -----------------------------
    # SIMULATE ACTUAL DELIVERY QUALITY
    # -----------------------------
    if "predicted_final_quality" in df.columns:

        df["actual_quality"] = (
            df["predicted_final_quality"]
            - np.random.randint(-10, 15, size=len(df))
        )

        # keep value between 0–100
        df["actual_quality"] = df["actual_quality"].clip(0, 100)

    # -----------------------------
    # SAVE FINAL OUTPUT
    # -----------------------------
    df.to_excel("Decision_Support_Output.xlsx", index=False)

    print("✅ Decision Support File Created")

if __name__ == "__main__":
    build_decision_support()
