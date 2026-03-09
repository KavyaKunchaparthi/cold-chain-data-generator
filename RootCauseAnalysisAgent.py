import pandas as pd
from datetime import datetime


class RootCauseAnalysisAgent:

    # --------------------------------------------------
    def analyze_causes(
        self,
        agent2_report_path,
        sensors_validated_path,
        events_path
    ):

        risk_df = pd.read_excel(agent2_report_path)
        sensors_df = pd.read_excel(sensors_validated_path)
        events_df = pd.read_excel(events_path)

        sensors_df["timestamp"] = pd.to_datetime(sensors_df["timestamp"])

        results = []

        for _, row in risk_df.iterrows():

            shipment_id = row["shipment_id"]
            risk_score = row["risk_score"]
            risk_level = row["risk_level"]
            ctai = row["ctai_value"]
            dwell = row["dwell_time_hours"]
            dwell_effect = row["dwell_effect"]

            # -----------------------------
            # CONTRIBUTION CALCULATION
            # -----------------------------
            ctai_contrib = min(ctai / 200, 1)
            dwell_contrib = min(dwell_effect / 100, 1)

            shipment_events = events_df[
                events_df["shipment_id"] == shipment_id
            ]

            event_impact = shipment_events["impact_on_quality"].sum() if not shipment_events.empty else 0
            event_contrib = min(event_impact / 50, 1)

            total = ctai_contrib + dwell_contrib + event_contrib
            if total == 0:
                total = 1  # avoid division by zero

            ctai_pct = round((ctai_contrib / total) * 100, 2)
            dwell_pct = round((dwell_contrib / total) * 100, 2)
            event_pct = round((event_contrib / total) * 100, 2)

            # -----------------------------
            # SENSOR ANOMALIES (AGENT-1)
            # -----------------------------
            anomaly_count = sensors_df[
                (sensors_df["shipment_id"] == shipment_id) &
                (sensors_df["is_anomalous"] == True)
            ].shape[0]

            # -----------------------------
            # CONTROLLABILITY
            # -----------------------------
            controllable = []
            uncontrollable = []

            if ctai_pct > 20:
                controllable.append("Temperature control failure")
            if dwell_pct > 20:
                controllable.append("Excess dwell at suboptimal temperature")
            if event_pct > 20:
                uncontrollable.append("Operational / logistics events")

            # -----------------------------
            # HUMAN-READABLE EXPLANATION
            # -----------------------------
            explanation = (
                f"Shipment experienced {ctai_pct}% thermal abuse contribution, "
                f"{dwell_pct}% dwell-time stress, and "
                f"{event_pct}% operational impact. "
            )

            if anomaly_count > 0:
                explanation += f"{anomaly_count} sensor anomalies were detected. "

            if risk_level in ["RED", "ORANGE"]:
                explanation += "Immediate corrective action is recommended."

            # -----------------------------
            # SEVERITY RANKING
            # -----------------------------
            causes = [
                ("Thermal Abuse", ctai_pct),
                ("Dwell Time Stress", dwell_pct),
                ("Operational Events", event_pct)
            ]

            causes_sorted = sorted(causes, key=lambda x: x[1], reverse=True)

            results.append({
                "shipment_id": shipment_id,
                "risk_level": risk_level,
                "risk_score": risk_score,
                "top_cause": causes_sorted[0][0],
                "thermal_abuse_pct": ctai_pct,
                "dwell_time_pct": dwell_pct,
                "event_impact_pct": event_pct,
                "sensor_anomalies": anomaly_count,
                "controllable_factors": ", ".join(controllable) if controllable else "None",
                "uncontrollable_factors": ", ".join(uncontrollable) if uncontrollable else "None",
                "root_cause_summary": explanation,
                "analysis_timestamp": datetime.utcnow().isoformat()
            })

        return pd.DataFrame(results)


# --------------------------------------------------
# RUN AGENT-3
# --------------------------------------------------
if __name__ == "__main__":

    agent = RootCauseAnalysisAgent()

    output_df = agent.analyze_causes(
        agent2_report_path="Agent2_Quality_Risk_Report.xlsx",
        sensors_validated_path="sensors.xlsx",
        events_path="events.xlsx"
    )

    output_df.to_excel("Agent3_Root_Cause_Report.xlsx", index=False)

    print("\n✅ AGENT 3 COMPLETED SUCCESSFULLY")
    print("Saved: Agent3_Root_Cause_Report.xlsx")
    print(output_df[[
        "shipment_id",
        "top_cause",
        "thermal_abuse_pct",
        "dwell_time_pct",
        "event_impact_pct"
    ]].head())
