import random
import uuid
import pandas as pd
from datetime import datetime, timedelta
import os

# ==========================================================
# SETTINGS
# ==========================================================

SHIPMENTS_PER_DAY = 50
READINGS_PER_SHIPMENT = 50

export_standards = ["US", "EU", "China"]
locations = ["India Packhouse", "Dubai Port", "Rotterdam Port", "US Distribution"]

stages = ["packhouse", "pre_cooling", "storage", "transport", "port", "distribution"]

event_types = ["delay", "handling", "temperature_spike", "humidity_drop", "port_hold"]

agents = ["RiskAgent", "ComplianceAgent", "MonitoringAgent"]

# ==========================================================
# PRODUCT MASTER
# ==========================================================

products_master = [
    {
        "product_id": "P001",
        "product_name": "Mango",
        "temp_min": 1,
        "temp_max": 3,
        "critical_threshold": 6,
        "humidity_min": 85,
        "humidity_max": 95,
        "thermal_sensitivity": 0.8
    },
    {
        "product_id": "P002",
        "product_name": "Grape",
        "temp_min": 0,
        "temp_max": 2,
        "critical_threshold": 5,
        "humidity_min": 90,
        "humidity_max": 98,
        "thermal_sensitivity": 0.9
    },
    {
        "product_id": "P003",
        "product_name": "Pomegranate",
        "temp_min": 2,
        "temp_max": 4,
        "critical_threshold": 7,
        "humidity_min": 80,
        "humidity_max": 90,
        "thermal_sensitivity": 0.6
    }
]

# ==========================================================
# FUNCTION TO APPEND DATA TO EXCEL
# ==========================================================

def append_to_excel(filename, data):

    df_new = pd.DataFrame(data)

    if os.path.exists(filename):
        df_existing = pd.read_excel(filename)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new

    df_combined.to_excel(filename, index=False)


# ==========================================================
# DATA STORAGE
# ==========================================================

shipments = []
sensors = []
events = []
quality_outcomes = []
decision_logs = []

today = datetime.now()

# ==========================================================
# GENERATE DAILY SHIPMENTS
# ==========================================================

for i in range(SHIPMENTS_PER_DAY):

    shipment_id = str(uuid.uuid4())
    product = random.choice(products_master)

    created_time = today
    expected_delivery = created_time + timedelta(days=5)

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

    base_temp = (product["temp_min"] + product["temp_max"]) / 2
    base_humidity = (product["humidity_min"] + product["humidity_max"]) / 2

    anomaly_count = 0

    # ------------------------------------------------------
    # SENSOR DATA
    # ------------------------------------------------------

    for r in range(READINGS_PER_SHIPMENT):

        timestamp = created_time + timedelta(minutes=15 * r)
        stage = random.choice(stages)

        temp = base_temp + random.uniform(-1, 1)
        humidity = base_humidity + random.uniform(-5, 5)

        temp_anomaly = temp > product["critical_threshold"]

        if temp_anomaly:
            anomaly_count += 1

        sensors.append({
            "sensor_id": f"TEMP-{shipment_id[:6]}-{r}",
            "shipment_id": shipment_id,
            "sensor_type": "temperature",
            "timestamp": timestamp,
            "value": round(temp, 2),
            "unit": "°C",
            "location_stage": stage,
            "is_anomalous": temp_anomaly
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

    # ------------------------------------------------------
    # EVENTS (40% probability)
    # ------------------------------------------------------

    if random.random() > 0.6:

        events.append({
            "event_id": str(uuid.uuid4()),
            "shipment_id": shipment_id,
            "event_type": random.choice(event_types),
            "severity": random.choice(["low", "medium", "high"]),
            "timestamp": created_time + timedelta(hours=random.randint(5, 48)),
            "duration_minutes": random.randint(30, 300),
            "location": random.choice(locations)
        })

    # ------------------------------------------------------
    # QUALITY OUTCOME
    # ------------------------------------------------------

    final_quality = max(0, 95 - anomaly_count * product["thermal_sensitivity"])

    spoilage = "yes" if final_quality < 70 else "no"

    quality_outcomes.append({
        "shipment_id": shipment_id,
        "final_quality_score": round(final_quality, 2),
        "spoilage_observed": spoilage
    })

    # ------------------------------------------------------
    # DECISION LOG
    # ------------------------------------------------------

    decision_logs.append({
        "decision_id": str(uuid.uuid4()),
        "shipment_id": shipment_id,
        "agent_name": random.choice(agents),
        "risk_score": round(random.uniform(0, 1), 2),
        "confidence": round(random.uniform(0.6, 0.99), 2),
        "timestamp": created_time
    })


# ==========================================================
# APPEND TO EXCEL FILES
# ==========================================================

append_to_excel("shipments.xlsx", shipments)
append_to_excel("sensors.xlsx", sensors)
append_to_excel("events.xlsx", events)
append_to_excel("quality_outcomes.xlsx", quality_outcomes)
append_to_excel("decision_log.xlsx", decision_logs)

print("✅ 50 new shipments generated and appended to Excel successfully.")