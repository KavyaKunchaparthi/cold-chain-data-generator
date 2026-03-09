import pandas as pd
from datetime import datetime

def build_decision_support():

    agent2 = pd.read_excel("Agent2_Quality_Risk_Report.xlsx")
    agent3 = pd.read_excel("Agent3_Root_Cause_Report.xlsx")
    agent4 = pd.read_excel("Agent4_Prescriptive_Recommendations.xlsx")

    df = agent2.merge(agent3, on="shipment_id", suffixes=("_risk", "_cause"))
    df = df.merge(agent4, on="shipment_id")

    df["review_status"] = "PENDING"
    df["reviewed_by"] = ""
    df["review_notes"] = ""
    df["decision_timestamp"] = ""

    df["generated_at"] = datetime.utcnow().isoformat()

    df.to_excel("Decision_Support_Output.xlsx", index=False)
    print("✅ Decision Support File Created")

if __name__ == "__main__":
    build_decision_support()
