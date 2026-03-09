import pandas as pd
import random
from datetime import datetime, timezone


class RecommendationAgent:
    """
    Agent 4: Prescriptive Recommendation Agent
    - Uses Agent 2 (risk) + Agent 3 (root cause)
    - Generates prioritized actionable recommendations
    """

    # --------------------------------------------------
    def generate_recommendations(self, agent2_path, agent3_path):

        agent2 = pd.read_excel(agent2_path)
        agent3 = pd.read_excel(agent3_path)

        # Merge safely (1 row per shipment)
        data = agent2.merge(
            agent3,
            on=["shipment_id", "risk_score", "risk_level"],
            how="inner"
        )

        recommendations_output = []

        for _, row in data.iterrows():

            shipment_id = row["shipment_id"]
            risk_level = row["risk_level"]
            risk_score = row["risk_score"]

            dwell_hours = row.get("dwell_time_hours", 0)
            thermal_pct = row.get("thermal_abuse_pct", 0)
            event_pct = row.get("event_impact_pct", 0)

            actions = []

            # --------------------------------------------------
            # 1️⃣ Identify possible interventions
            # --------------------------------------------------
            if risk_level == "RED":
                actions.append({
                    "action": "Immediate temperature stabilization",
                    "base_effectiveness": 0.9
                })

            if dwell_hours > 6:
                actions.append({
                    "action": "Expedite next logistics stage",
                    "base_effectiveness": 0.7
                })

            if thermal_pct > 40:
                actions.append({
                    "action": "Recalibrate refrigeration unit",
                    "base_effectiveness": 0.8
                })

            if event_pct > 20:
                actions.append({
                    "action": "Reroute to avoid delay-prone hub",
                    "base_effectiveness": 0.6
                })

            if not actions:
                actions.append({
                    "action": "Continue monitoring (no intervention)",
                    "base_effectiveness": 0.3
                })

            # --------------------------------------------------
            # 2️⃣ Simulate impact + feasibility
            # --------------------------------------------------
            enriched_actions = []

            for act in actions:
                feasibility = round(random.uniform(0.6, 0.95), 2)
                cost = int(100 + (risk_score * 600) + random.randint(0, 150))

                timeline = (
                    "Immediate" if risk_level == "RED"
                    else "Within 2 hours" if risk_level == "YELLOW"
                    else "Next checkpoint"
                )

                effectiveness = round(act["base_effectiveness"] * feasibility, 2)

                enriched_actions.append({
                    "action": act["action"],
                    "effectiveness": effectiveness,
                    "feasibility": feasibility,
                    "estimated_cost_usd": cost,
                    "timeline": timeline,
                    "score": round(effectiveness / cost, 5)
                })

            # --------------------------------------------------
            # 3️⃣ Rank by effectiveness / cost
            # --------------------------------------------------
            enriched_actions = sorted(
                enriched_actions,
                key=lambda x: x["score"],
                reverse=True
            )

            # --------------------------------------------------
            # 4️⃣ Filter impractical actions
            # --------------------------------------------------
            enriched_actions = [
                a for a in enriched_actions if a["feasibility"] >= 0.65
            ]

            # --------------------------------------------------
            # 5️⃣ SAFETY FALLBACK (🔥 FIX)
            # --------------------------------------------------
            if not enriched_actions:
                enriched_actions.append({
                    "action": "Manual review required",
                    "effectiveness": 0.0,
                    "feasibility": 1.0,
                    "estimated_cost_usd": 0,
                    "timeline": "Immediate",
                    "score": 0
                })

            # --------------------------------------------------
            # 6️⃣ Final structured output
            # --------------------------------------------------
            recommendations_output.append({
                "shipment_id": shipment_id,
                "risk_level": risk_level,
                "risk_score": risk_score,
                "prioritized_actions": enriched_actions,
                "top_recommendation": enriched_actions[0]["action"],
                "generated_at": datetime.now(timezone.utc).isoformat()
            })

        return pd.DataFrame(recommendations_output)


# --------------------------------------------------
# RUN AGENT 4
# --------------------------------------------------
if __name__ == "__main__":

    agent = RecommendationAgent()

    output_df = agent.generate_recommendations(
        agent2_path="Agent2_Quality_Risk_Report.xlsx",
        agent3_path="Agent3_Root_Cause_Report.xlsx"
    )

    output_df.to_excel(
        "Agent4_Prescriptive_Recommendations.xlsx",
        index=False
    )

    print("\n✅ AGENT 4 COMPLETED SUCCESSFULLY")
    print("Saved: Agent4_Prescriptive_Recommendations.xlsx")
    print(output_df[["shipment_id", "risk_level", "top_recommendation"]].head())
