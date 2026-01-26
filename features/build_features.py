import os
import sys
from pymongo import MongoClient
from datetime import datetime

# ---------------------------------------------------------
# Path & Config
# ---------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import *

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

def build_features():
    inserted = 0
    skipped = 0

    for r in db.raw_weather.find():

        timestamp = r.get("timestamp")

        # ------------------ HANDLE BOTH FORMATS ------------------
        pollution = r.get("pollution") or r.get("pollution_data")
        weather = r.get("weather") or r.get("weather_data")

        if not pollution or "list" not in pollution or not pollution["list"]:
            skipped += 1
            continue

        if not weather or "main" not in weather:
            skipped += 1
            continue

        if not timestamp or not isinstance(timestamp, datetime):
            skipped += 1
            continue

        try:
            p = pollution["list"][0]["components"]
            w = weather

            features = {
                "pm2_5": p["pm2_5"],
                "pm10": p["pm10"],
                "ozone": p["o3"],
                "carbon_monoxide": p.get("co", 0),
                "sulphur_dioxide": p.get("so2", 0),
                "nitrogen_dioxide": p["no2"],
                "temperature_2m": w["main"]["temp"] - 273.15,
                "relative_humidity_2m": w["main"]["humidity"],
                "wind_speed_10m": w["wind"]["speed"],
                "hour": timestamp.hour,
                "day": timestamp.day,
                "month": timestamp.month,
                "year": timestamp.year,
                "timestamp": timestamp
            }

            db.engineered_features.update_one(
                {"timestamp": timestamp},
                {"$set": features},
                upsert=True
            )

            inserted += 1

        except Exception as e:
            skipped += 1

    print(f"✅ Feature Store Updated")
    print(f"   Inserted: {inserted}")
    print(f"   Skipped : {skipped}")

if __name__ == "__main__":
    build_features()
