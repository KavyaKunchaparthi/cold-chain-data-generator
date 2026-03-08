import pandas as pd
import numpy as np
import os


class SensorValidationAgent:
    def __init__(self,
                 stuck_threshold_minutes=45,
                 max_gap_minutes=30,
                 spike_std_multiplier=2.0):
        self.stuck_threshold_minutes = stuck_threshold_minutes
        self.max_gap_minutes = max_gap_minutes
        self.spike_std_multiplier = spike_std_multiplier

    def validate_readings(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        df["synthetic_is_anomalous"] = df["is_anomalous"].fillna(False)
        df["sensor_fault_anomaly"] = False

        for _, group in df.groupby("sensor_id"):
            group = group.sort_values("timestamp")
            values = group["value"].values
            timestamps = group["timestamp"].values
            idx = group.index

            # ---------- 1. Impossible values ----------
            mask = np.zeros(len(values), dtype=bool)
            for i, row in enumerate(group.itertuples()):
                if row.sensor_type == "temperature" and not (-10 <= row.value <= 50):
                    mask[i] = True
                if row.sensor_type == "humidity" and not (5 <= row.value <= 95):
                    mask[i] = True

            valid_idx = idx[mask]
            filtered_idx = valid_idx[
                df.loc[valid_idx, "synthetic_is_anomalous"] == False
            ]
            df.loc[filtered_idx, "sensor_fault_anomaly"] = True

            # ---------- 2. Stuck sensor ----------
            window = max(2, int(self.stuck_threshold_minutes / 15))
            for i in range(window, len(values)):
                if np.std(values[i-window:i]) == 0:
                    if not df.loc[idx[i], "synthetic_is_anomalous"]:
                        df.loc[idx[i], "sensor_fault_anomaly"] = True

            # ---------- 3. Rolling spike ----------
            s = pd.Series(values)
            mean = s.rolling(5, min_periods=3).mean()
            std = s.rolling(5, min_periods=3).std()
            spike_mask = abs(s - mean) > (self.spike_std_multiplier * std)

            valid_idx = idx[spike_mask.fillna(False)]
            filtered_idx = valid_idx[
                df.loc[valid_idx, "synthetic_is_anomalous"] == False
            ]
            df.loc[filtered_idx, "sensor_fault_anomaly"] = True

            # ---------- 4. Timestamp gaps ----------
            for i in range(1, len(timestamps)):
                gap = (timestamps[i] - timestamps[i-1]) / np.timedelta64(1, "m")
                if gap > self.max_gap_minutes:
                    if not df.loc[idx[i], "synthetic_is_anomalous"]:
                        df.loc[idx[i], "sensor_fault_anomaly"] = True

        # ---------- FINAL OR ----------
        df["final_is_anomalous"] = (
            df["synthetic_is_anomalous"] |
            df["sensor_fault_anomaly"]
        )

        return df


# ================= RUN =================
if __name__ == "__main__":
    sensors_df = pd.read_excel("sensors.xlsx")

    agent = SensorValidationAgent()
    validated_df = agent.validate_readings(sensors_df)

    validated_df.to_excel("Sensors_Validated.xlsx", index=False)

    print("AGENT 1 COMPLETED SUCCESSFULLY")
    print("Synthetic anomalies :", validated_df["synthetic_is_anomalous"].sum())
    print("Sensor faults :", validated_df["sensor_fault_anomaly"].sum())
    print("Final anomalies :", validated_df["final_is_anomalous"].sum())
