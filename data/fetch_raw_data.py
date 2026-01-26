import os
import sys
from pymongo import MongoClient
from datetime import datetime, timezone

# ---------------------------------------------------------
# Path & Config
# ---------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import *  # Contains MONGO_URI, DB_NAME

# ----------------- MongoDB -----------------
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# ----------------- BUILD FEATURES -----------------
def build_features():
    inserted = 0
    skipped = 0

    for r in db.raw_weather.find():
        timestamp = r.get("timestamp")
        if not timestamp or not isinstance(timestamp, datetime):
            skipped += 1
            continue

        # ------------------ POLLUTION DATA ------------------
        # WAQI format
        if "aqi_data" in r:
            aqi_data = r["aqi_data"]
            iaqi = aqi_data.get("iaqi", {})
            p = {
                "pm2_5": iaqi.get("pm25", {}).get("v", 0),
                "pm10": iaqi.get("pm10", {}).get("v", 0),
                "ozone": iaqi.get("o3", {}).get("v", 0),
                "carbon_monoxide": iaqi.get("co", {}).get("v", 0),
                "sulphur_dioxide": iaqi.get("so2", {}).get("v", 0),
                "nitrogen_dioxide": iaqi.get("no2", {}).get("v", 0),
                "aqi": aqi_data.get("aqi", None)
            }
            w = r.get("weather_data", {})

        # OpenWeatherMap format
        elif "pollution_data" in r:
            pollution_data = r["pollution_data"]
            weather_data = r.get("weather_data", {})
            if "list" not in pollution_data or not pollution_data["list"]:
                skipped += 1
                continue
            p = pollution_data["list"][0]["components"]
            p = {
                "pm2_5": p.get("pm2_5", 0),
                "pm10": p.get("pm10", 0),
                "ozone": p.get("o3", 0),
                "carbon_monoxide": p.get("co", 0),
                "sulphur_dioxide": p.get("so2", 0),
                "nitrogen_dioxide": p.get("no2", 0),
                "aqi": None
            }
            w = weather_data

        else:
            skipped += 1
            continue

        # ------------------ WEATHER DATA ------------------
        temp = round(w.get("main", {}).get("temp", 0) - 273.15, 2)
        humidity = w.get("main", {}).get("humidity", 0)
        wind_speed = w.get("wind", {}).get("speed", 0)

        # ------------------ FEATURE DICTIONARY ------------------
        features = {
            "pm2_5": p["pm2_5"],
            "pm10": p["pm10"],
            "ozone": p["ozone"],
            "carbon_monoxide": p["carbon_monoxide"],
            "sulphur_dioxide": p["sulphur_dioxide"],
            "nitrogen_dioxide": p["nitrogen_dioxide"],
            "aqi": p.get("aqi", None),
            "temperature_2m": temp,
            "relative_humidity_2m": humidity,
            "wind_speed_10m": wind_speed,
            "hour": timestamp.hour,
            "day": timestamp.day,
            "month": timestamp.month,
            "year": timestamp.year,
            "timestamp": timestamp
        }

        # ------------------ UPSERT INTO ENGINEERED FEATURES ------------------
        db.engineered_features.update_one(
            {"timestamp": timestamp},
            {"$set": features},
            upsert=True
        )
        inserted += 1

    print(f"✅ Feature Store Updated")
    print(f"   Inserted: {inserted}")
    print(f"   Skipped : {skipped}")


# ----------------- RUN -----------------
if __name__ == "__main__":
    build_features()
