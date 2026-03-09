import pandas as pd
from datetime import datetime


class QualityRiskAgent:

    # --------------------------------------------------
    # CTAI CALCULATION
    # --------------------------------------------------
    def calculate_ctai(self, temp_df, optimal_temp, tolerance=0.5):
        ctai = 0.0
        temp_df = temp_df.sort_values("timestamp")

        for i in range(1, len(temp_df)):
            t_prev = temp_df.iloc[i - 1]["timestamp"]
            t_curr = temp_df.iloc[i]["timestamp"]
            delta_minutes = (t_curr - t_prev).total_seconds() / 60

            temp = temp_df.iloc[i]["value"]
            abuse = max(0, abs(temp - optimal_temp) - tolerance)
            ctai += abuse * delta_minutes

        return round(ctai, 2)

    # --------------------------------------------------
    # DWELL TIME + EFFECT
    # --------------------------------------------------
    def calculate_dwell(self, temp_df, optimal_temp, tolerance, sensitivity):
        dwell_hours = 0.0
        temp_df = temp_df.sort_values("timestamp")

        for i in range(1, len(temp_df)):
            t_prev = temp_df.iloc[i - 1]["timestamp"]
            t_curr = temp_df.iloc[i]["timestamp"]
            delta_hours = (t_curr - t_prev).total_seconds() / 3600

            temp = temp_df.iloc[i]["value"]
            if abs(temp - optimal_temp) > tolerance:
                dwell_hours += delta_hours

        if dwell_hours < 2:
            multiplier = 1
        elif dwell_hours < 6:
            multiplier = 1.5
        elif dwell_hours < 12:
            multiplier = 3
        else:
            multiplier = 5

        dwell_effect = dwell_hours * sensitivity * multiplier
        return round(dwell_hours, 2), round(dwell_effect, 2)

    # --------------------------------------------------
    # RISK LEVEL MAPPING (LOW / MEDIUM / HIGH)
    # --------------------------------------------------
    def map_risk_level(self, score):
        if score < 0.25:
            return "GREEN"
        elif score < 0.40:
            return "YELLOW"
        else:
            return "RED"

    # --------------------------------------------------
    def predict_risk_for_all_shipments(
        self,
        sensors_path,
        shipments_path,
        products_path,
        events_path
    ):

        sensors = pd.read_excel(sensors_path)
        shipments = pd.read_excel(shipments_path)
        products = pd.read_excel(products_path)
        events = pd.read_excel(events_path)

        sensors["timestamp"] = pd.to_datetime(sensors["timestamp"])
        results = []

        for _, shipment in shipments.iterrows():

            shipment_id = shipment["shipment_id"]
            product_type = shipment["product_type"]
            initial_quality = shipment["initial_quality_score"]

            product = products[products["product_name"] == product_type].iloc[0]

            optimal_temp = (product["temp_min"] + product["temp_max"]) / 2
            sensitivity = product["thermal_sensitivity"]
            tolerance = 0.5

            temp_data = sensors[
                (sensors["shipment_id"] == shipment_id) &
                (sensors["sensor_type"] == "temperature")
            ]

            if temp_data.empty:
                continue

            ctai_value = self.calculate_ctai(temp_data, optimal_temp, tolerance)
            dwell_time, dwell_effect = self.calculate_dwell(
                temp_data, optimal_temp, tolerance, sensitivity
            )

            shipment_events = events[events["shipment_id"] == shipment_id]
            operational_impact = shipment_events["impact_on_quality"].sum() if not shipment_events.empty else 0

            # ---------------- NORMALIZATION (CRITICAL FIX) ----------------
            ctai_norm = min(ctai_value / 200, 1)
            dwell_norm = min(dwell_effect / product["max_dwell_time_hours"], 1)
            event_norm = min(operational_impact / 50, 1)

            risk_score = round(
                (0.45 * ctai_norm) +
                (0.35 * dwell_norm) +
                (0.20 * event_norm),
                2
            )

            risk_score = min(1.0, risk_score)
            predicted_final_quality = round(initial_quality - (risk_score * 100), 2)
            spoilage_probability = round(min(1.0, risk_score * 0.9), 2)
            risk_level = self.map_risk_level(risk_score)

            results.append({
                "shipment_id": shipment_id,
                "product_type": product_type,
                "ctai_value": ctai_value,
                "dwell_time_hours": dwell_time,
                "dwell_effect": dwell_effect,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "predicted_final_quality": predicted_final_quality,
                "spoilage_probability": spoilage_probability,
                "timestamp": datetime.utcnow().isoformat()
            })

        return pd.DataFrame(results)


# --------------------------------------------------
# RUN AGENT 2
# --------------------------------------------------
if __name__ == "__main__":

    agent = QualityRiskAgent()

    output_df = agent.predict_risk_for_all_shipments(
        sensors_path="sensors.xlsx",
        shipments_path="shipments.xlsx",
        products_path="products_master.xlsx",
        events_path="events.xlsx"
    )

    output_df.to_excel("Agent2_Quality_Risk_Report.xlsx", index=False)

    print("\n✅ AGENT 2 COMPLETED SUCCESSFULLY")
    print("Risk distribution:")
    print(output_df["risk_level"].value_counts())


