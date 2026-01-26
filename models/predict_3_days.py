import os
import sys
import joblib
import pandas as pd
from pymongo import MongoClient
from config import *

# ----------------- PATH SETUP -----------------
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ----------------- LOAD MODEL -----------------
MODEL_PATH = "models/best_model.pkl"
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError("❌ best_model.pkl not found")

model = joblib.load(MODEL_PATH)

# ----------------- MONGODB -----------------
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

df = pd.DataFrame(list(db.engineered_features.find()))
if df.empty:
    raise ValueError("❌ No data found in engineered_features")

df.drop(columns="_id", inplace=True)

# ----------------- LAG FEATURES -----------------
df["lag1"] = df["pm2_5"].shift(1)
df["lag2"] = df["pm2_5"].shift(2)
df["lag3"] = df["pm2_5"].shift(3)
df.dropna(inplace=True)

# ----------------- FEATURE ORDER (CRITICAL) -----------------
feature_order = [
    "pm10",
    "ozone",
    "carbon_monoxide",
    "sulphur_dioxide",
    "nitrogen_dioxide",
    "temperature_2m",
    "relative_humidity_2m",
    "wind_speed_10m",
    "hour",
    "day",
    "month",
    "lag1",
    "lag2",
    "lag3"
]

current = df.iloc[-1][feature_order].copy()

# ----------------- 3-DAY FORECAST -----------------
forecast = []

for day in range(1, 4):
    pred = model.predict(pd.DataFrame([current]))[0]
    pred = round(float(pred), 2)

    forecast.append(pred)

    # shift lags
    current["lag3"] = current["lag2"]
    current["lag2"] = current["lag1"]
    current["lag1"] = pred

print("\n🌍 Hyderabad AQI Forecast")
print("----------------------------")
for i, val in enumerate(forecast, 1):
    print(f"Day {i}: AQI ≈ {val}")
