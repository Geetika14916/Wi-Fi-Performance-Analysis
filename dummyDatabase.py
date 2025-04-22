from datetime import datetime, timedelta
import random
from pymongo import MongoClient
from Database.config import DB_CONFIG

# Connect to MongoDB
client = MongoClient(DB_CONFIG["host"], DB_CONFIG["port"])
db = client[DB_CONFIG["database"]]
wifi_data_col = db["wifi_data"]

# Clear existing data
wifi_data_col.delete_many({})
print("✅ Cleared existing wifi_data collection.")

# Dummy locations
locations = [
    ['ECC', 67.12, -43.45],
    ['GEC', 70.21, -40.31],
    ['SDB', 65.78, -42.5],
    ['FOODCOURT', 68.33, -41.25],
    ['LOUNGE', 69.0, -39.9]
]

# Generate dummy data for 5 days
for day_offset in range(5):
    base_date = datetime.now() - timedelta(days=day_offset)
    date_str = base_date.strftime("%Y-%m-%d")

    for run_no in range(1, 3):  # Two runs per day
        for location in locations:
            location_name, x, y = location
            timestamp = f"{date_str} {random.randint(9, 18)}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}"

            dummy_entry = {
                "timestamp": timestamp,
                "run_no": run_no,
                "location": {
                    "position[x]": x,
                    "position[y]": y,
                    "position[name]": location_name
                },
                "download_speed": round(random.uniform(10, 100), 2),
                "upload_speed": round(random.uniform(5, 50), 2),
                "latency_ms": round(random.uniform(10, 100), 2),
                "jitter_ms": round(random.uniform(0, 20), 2),
                "packet_loss": round(random.uniform(0, 5), 2),
                "rssi": random.randint(30, 90)
            }

            wifi_data_col.update_one(
                {"_id": location_name},
                {"$push": {location_name: dummy_entry}},
                upsert=True
            )

print("✅ Dummy data for 5 days inserted successfully.")
