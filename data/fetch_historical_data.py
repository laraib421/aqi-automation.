import os
import sys
import requests
from datetime import datetime, timezone
from pymongo import MongoClient
import time

# Add parent folder to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import *  # Contains MONGO_URI, DB_NAME, OPENWEATHER_API_KEY

# ----------------- CONSTANTS -----------------
CITY = "Hyderabad, Pakistan"
LAT = 25.3960
LON = 68.3578
WAQI_TOKEN = "0d9583517e439050db9914d3f1ef30e1c2feb449"
FETCH_INTERVAL_SECONDS = 3600  # 1 hour

# ----------------- MongoDB -----------------
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# ----------------- FETCH WAQI -----------------
def fetch_real_aqi():
    url = f"https://api.waqi.info/feed/geo:{LAT};{LON}/?token={WAQI_TOKEN}"
    res = requests.get(url, timeout=10)
    res.raise_for_status()
    data = res.json()
    if data["status"] != "ok":
        raise ValueError(f"WAQI API returned status: {data['status']}")
    return data["data"]

# ----------------- FETCH WEATHER -----------------
def fetch_weather():
    url = "http://api.openweathermap.org/data/2.5/weather"
    res = requests.get(url, params={"lat": LAT, "lon": LON, "appid": OPENWEATHER_API_KEY}, timeout=10)
    res.raise_for_status()
    return res.json()

# ----------------- STORE DATA -----------------
def fetch_and_store():
    ts = datetime.now(timezone.utc)
    try:
        aqi_data = fetch_real_aqi()
        weather_data = fetch_weather()
    except Exception as e:
        print(f"⚠️ Fetch failed at {ts}: {e}")
        return

    # --- Raw storage ---
    db.raw_weather.insert_one({
        "city": CITY,
        "timestamp": ts,
        "aqi_data": aqi_data,
        "weather_data": weather_data
    })

    # --- Feature engineering ---
    iaqi = aqi_data.get("iaqi", {})
    features = {
        "date": ts.strftime("%Y-%m-%d"),
        "aqi": aqi_data.get("aqi"),
        "pm2_5": iaqi.get("pm25", {}).get("v"),
        "pm10": iaqi.get("pm10", {}).get("v"),
        "ozone": iaqi.get("o3", {}).get("v"),
        "carbon_monoxide": iaqi.get("co", {}).get("v"),
        "sulphur_dioxide": iaqi.get("so2", {}).get("v"),
        "nitrogen_dioxide": iaqi.get("no2", {}).get("v"),
        "temperature_2m": round(weather_data["main"]["temp"] - 273.15, 2),
        "relative_humidity_2m": weather_data["main"]["humidity"],
        "wind_speed_10m": weather_data["wind"]["speed"],
        "hour": ts.hour,
        "day": ts.day,
        "month": ts.month,
        "year": ts.year
    }

    db.engineered_features.insert_one(features)
    print(f"✅ Data stored at {ts}")

# ----------------- RUN CONTINUOUSLY -----------------
if __name__ == "__main__":
    print("🌍 Starting continuous historical data collection...")
    while True:
        fetch_and_store()
        print(f"⏳ Waiting {FETCH_INTERVAL_SECONDS/60} minutes until next fetch...")
        time.sleep(FETCH_INTERVAL_SECONDS)
