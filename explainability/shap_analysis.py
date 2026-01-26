import os
import sys
import joblib
import pandas as pd
import shap
import matplotlib.pyplot as plt
from pymongo import MongoClient

# -------------------------------------------------
# Path Fix
# -------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import *

# -------------------------------------------------
# MongoDB Connection
# -------------------------------------------------
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# -------------------------------------------------
# Load Feature Store
# -------------------------------------------------
df = pd.DataFrame(list(db.engineered_features.find()))

if df.empty:
    raise ValueError("❌ No data found in engineered_features collection")

if "_id" in df.columns:
    df.drop(columns="_id", inplace=True)

df = df.sort_values("timestamp").reset_index(drop=True)

# -------------------------------------------------
# Lag Features (MUST match training)
# -------------------------------------------------
df["lag1"] = df["pm2_5"].shift(1)
df["lag2"] = df["pm2_5"].shift(2)
df["lag3"] = df["pm2_5"].shift(3)
df.dropna(inplace=True)

FEATURE_ORDER = [
    "pm10","ozone","carbon_monoxide","sulphur_dioxide",
    "nitrogen_dioxide","temperature_2m","relative_humidity_2m",
    "wind_speed_10m","hour","day","month","lag1","lag2","lag3"
]

X = df[FEATURE_ORDER]

# -------------------------------------------------
# Load Model
# -------------------------------------------------
MODEL_PATH = "models/best_model.pkl"

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError("❌ best_model.pkl not found. Train model first.")

model = joblib.load(MODEL_PATH)

# -------------------------------------------------
# SHAP Explainer (Explicit & Stable)
# -------------------------------------------------
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X)

# -------------------------------------------------
# SHAP Summary Plot (Feature Importance)
# -------------------------------------------------
shap.summary_plot(
    shap_values,
    X,
    plot_type="bar",
    show=False
)
plt.title("Global Feature Importance (SHAP)")
plt.tight_layout()
plt.savefig("shap_summary.png", dpi=300, bbox_inches="tight")
plt.close()

print("✅ SHAP summary plot saved as shap_summary.png")

# -------------------------------------------------
# SHAP Force Plot (Latest Prediction)
# -------------------------------------------------
latest = X.iloc[-1]

expected_value = (
    explainer.expected_value[0]
    if isinstance(explainer.expected_value, list)
    else explainer.expected_value
)

shap.force_plot(
    expected_value,
    shap_values[-1],
    latest,
    matplotlib=True,
    show=False
)

plt.title("SHAP Force Plot – Latest AQI Prediction")
plt.savefig("shap_force_latest.png", dpi=300, bbox_inches="tight")
plt.close()

print("✅ SHAP force plot saved as shap_force_latest.png")
