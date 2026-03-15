import random
import uuid
import pandas as pd
from datetime import datetime, timedelta
import os

# ==========================================================
# HELPER FUNCTION TO APPEND TO EXCEL
# ==========================================================
def append_to_excel(df, file_name):
    if os.path.exists(file_name):
        existing_df = pd.read_excel(file_name)
        combined_df = pd.concat([existing_df, df], ignore_index=True)
        combined_df.to_excel(file_name, index=False)
    else:
        df.to_excel(file_name, index=False)

# ==========================================================
# 1. PRODUCTS MASTER TABLE (Sensitivity Database)
# ==========================================================
products_master = [
    {
        "product_id": "P001",
        "product_name": "Mango",
        "temp_min": 1,
        "temp_max": 3,
        "critical_threshold": 6,
        "max_dwell_time_hours": 120,
        "humidity_min": 85,
        "humidity_max": 95,
        "shelf_life_days": 14,
        "thermal_sensitivity": 0.8,
        "handling_fragility": 7
    },
    {
        "product_id": "P002",
        "product_name": "Grape",
        "temp_min": 0,
        "temp_max": 2,
        "critical_threshold": 5,
        "max_dwell_time_hours": 100,
        "humidity_min": 90,
        "humidity_max": 98,
        "shelf_life_days": 10,
        "thermal_sensitivity": 0.9,
        "handling_fragility": 8
    },
    {
        "product_id": "P003",
        "product_name": "Pomegranate",
        "temp_min": 2,
        "temp_max": 4,
        "critical_threshold": 7,
        "max_dwell_time_hours": 140,
        "humidity_min": 80,
        "humidity_max": 90,
        "shelf_life_days": 20,
        "thermal_sensitivity": 0.6,
        "handling_fragility": 5
    }
]

# Convert products master into DataFrame
df_products = pd.DataFrame(products_master)

# ==========================================================
# OUTPUT TABLES
# ==========================================================
shipments = []
sensors = []
events = []
quality_outcomes = []
decision_logs = []

# ==========================================================
# SETTINGS
# ==========================================================
NUM_SHIPMENTS = 50   # daily shipments
READINGS_PER_SHIPMENT = 50

export_standards = ["US", "EU", "China"]
locations = ["India Packhouse", "Dubai Port", "Rotterdam Port", "US Distribution"]
stages = ["packhouse", "pre_cooling", "storage", "transport", "port", "distribution"]
event_types = ["delay", "handling", "temperature_spike", "humidity_drop", "port_hold"]
agents = ["RiskAgent", "ComplianceAgent", "MonitoringAgent"]

# ==========================================================
# GENERATE DATA
# ==========================================================
print("Generating full cold-chain synthetic dataset...")

for i in range(NUM_SHIPMENTS):
    shipment_id = str(uuid.uuid4())
    product = random.choice(products_master)

    created_time = datetime.now() - timedelta(days=random.randint(1, 30))
    expected_delivery = created_time + timedelta(days=5)

    # -------------------------------
    # Shipment Table Row
    # -------------------------------
    shipments.append({
        "shipment_id": shipment_id,
        "product_type": product["product_name"],
        "product_quantity": round(random.uniform(1000, 10000), 2),
        "initial_quality_score": round(random.uniform(85, 100), 2),
        "origin_location": "India Packhouse",
        "destination_location": "US Distribution Center",
        "export_standard": random.choice(export_standards),
        "created_timestamp": created_time,
        "expected_delivery_date": expected_delivery
    })

    # -------------------------------
    # Sensors Table Rows
    # -------------------------------
    base_temp = (product["temp_min"] + product["temp_max"]) / 2
    base_humidity = (product["humidity_min"] + product["humidity_max"]) / 2

    anomaly_count = 0

    for r in range(READINGS_PER_SHIPMENT):
        timestamp = created_time + timedelta(minutes=15 * r)
        stage = random.choice(stages)

        temp = base_temp + random.uniform(-1, 1)
        humidity = base_humidity + random.uniform(-5, 5)

        is_anomalous_temp = temp > product["critical_threshold"]
        if is_anomalous_temp:
            anomaly_count += 1

        sensors.append({
            "sensor_id": f"TEMP-{shipment_id[:6]}-{r}",
            "shipment_id": shipment_id,
            "sensor_type": "temperature",
            "timestamp": timestamp,
            "value": round(temp, 2),
            "unit": "°C",
            "location_stage": stage,
            "is_anomalous": is_anomalous_temp
        })

        sensors.append({
            "sensor_id": f"HUM-{shipment_id[:6]}-{r}",
            "shipment_id": shipment_id,
            "sensor_type": "humidity",
            "timestamp": timestamp,
            "value": round(humidity, 2),
            "unit": "%",
            "location_stage": stage,
            "is_anomalous": humidity < product["humidity_min"]
        })

    # -------------------------------
    # Events Table Rows
    # -------------------------------
    if random.random() > 0.6:
        event = random.choice(event_types)
        severity = random.choice(["low", "medium", "high"])
        quality_loss = round(random.uniform(2, 20), 2)

        events.append({
            "event_id": str(uuid.uuid4()),
            "shipment_id": shipment_id,
            "event_type": event,
            "severity": severity,
            "timestamp": created_time + timedelta(hours=random.randint(5, 80)),
            "duration_minutes": random.randint(30, 300),
            "description": f"Synthetic event: {event}",
            "location": random.choice(locations),
            "impact_on_quality": quality_loss
        })

    
# ==========================================================
# SAVE ALL TABLES TO EXCEL
# ==========================================================
append_to_excel(pd.DataFrame(shipments), "shipments.xlsx")
append_to_excel(pd.DataFrame(sensors), "sensors.xlsx")
append_to_excel(pd.DataFrame(events), "events.xlsx")


# Overwrite master products file (constant 3 products)
pd.DataFrame(products_master).to_excel("products_master.xlsx", index=False)

print("\n✅ FULL DATASET GENERATED SUCCESSFULLY!")
print("Excel Files Created / Updated:")
print("1. shipments.xlsx")
print("2. sensors.xlsx")
print("3. events.xlsx")
print("4. products_master.xlsx")

