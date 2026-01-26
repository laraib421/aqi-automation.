# =========================================================
# AQI MODEL TRAINING & COMPARISON
# Hyderabad, Pakistan
# =========================================================

import os
import sys
import json
import joblib
import numpy as np
import pandas as pd

from pymongo import MongoClient
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor

# ---------------------------------------------------------
# Path & Config
# ---------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import *

# ---------------------------------------------------------
# MongoDB Connection
# ---------------------------------------------------------
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# ---------------------------------------------------------
# Load Feature Store
# ---------------------------------------------------------
df = pd.DataFrame(list(db.engineered_features.find()))

if df.empty:
    print("❌ No data found in engineered_features collection.")
    print("➡ Run: python features/build_features.py")
    exit(1)

if "_id" in df.columns:
    df.drop(columns="_id", inplace=True)

# ---------------------------------------------------------
# REQUIRED COLUMN CHECK
# ---------------------------------------------------------
required_cols = [
    "pm2_5", "pm10", "ozone", "carbon_monoxide",
    "sulphur_dioxide", "nitrogen_dioxide",
    "temperature_2m", "relative_humidity_2m",
    "wind_speed_10m", "hour", "day", "month", "date"
]

missing = [c for c in required_cols if c not in df.columns]
if missing:
    print(f"❌ Missing required columns: {missing}")
    exit(1)

# ---------------------------------------------------------
# Create Proper Time Index (FIXED ROOT CAUSE)
# ---------------------------------------------------------
df["datetime"] = pd.to_datetime(
    df["date"] + " " + df["hour"].astype(str) + ":00:00"
)

df = df.sort_values("datetime").reset_index(drop=True)

# ---------------------------------------------------------
# Feature Engineering (Lags)
# ---------------------------------------------------------
df["lag1"] = df["pm2_5"].shift(1)
df["lag2"] = df["pm2_5"].shift(2)
df["lag3"] = df["pm2_5"].shift(3)

df.dropna(inplace=True)

if len(df) < 30:
    print(f"❌ Not enough data after lag creation: {len(df)} rows")
    print("➡ Need more historical data.")
    exit(1)

# ---------------------------------------------------------
# Feature Set
# ---------------------------------------------------------
FEATURES = [
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

X = df[FEATURES]
y = df["pm2_5"]

# ---------------------------------------------------------
# Train / Test Split (Time-Series Safe)
# ---------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    shuffle=False
)

# ---------------------------------------------------------
# Models to Compare
# ---------------------------------------------------------
models = {
    "Ridge": Ridge(alpha=1.0),
    "RandomForest": RandomForestRegressor(
        n_estimators=300,
        max_depth=None,
        random_state=42,
        n_jobs=-1
    ),
    "XGBoost": XGBRegressor(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        n_jobs=-1
    ),
    "LightGBM": LGBMRegressor(
        n_estimators=300,
        max_depth=-1,  # Leaf-wise growth
        learning_rate=0.1,
        random_state=42,
        n_jobs=-1
    )
}

results = {}
best_model = None
best_rmse = float("inf")
best_r2 = float("-inf")

# ---------------------------------------------------------
# Training Loop
# ---------------------------------------------------------
for name, model in models.items():
    print(f"🚀 Training {name}...")

    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    rmse = np.sqrt(mean_squared_error(y_test, preds))
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)

    results[name] = {
        "RMSE": round(rmse, 3),
        "MAE": round(mae, 3),
        "R2": round(r2, 3)
    }

    print(f"   RMSE: {rmse:.3f} | MAE: {mae:.3f} | R²: {r2:.3f}")

    # Select best model based on lowest RMSE and highest R²
    if rmse < best_rmse or (rmse == best_rmse and r2 > best_r2):
        best_rmse = rmse
        best_r2 = r2
        best_model = model
        best_model_name = name

# ---------------------------------------------------------
# Save Best Model & Metrics
# ---------------------------------------------------------
os.makedirs("models", exist_ok=True)

joblib.dump(best_model, "models/best_model.pkl")

with open("models/model_metrics.json", "w") as f:
    json.dump(results, f, indent=4)

# ---------------------------------------------------------
# Final Output
# ---------------------------------------------------------
print("\n✅ TRAINING COMPLETE")
print(f"🏆 Best Model : {best_model_name}")
print(f"📉 Best RMSE : {best_rmse:.3f}")

print("💾 Saved: models/best_model.pkl")
print("📊 Saved: models/model_metrics.json")
