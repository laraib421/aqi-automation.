# =========================================================
# AQI AUTOMATION - STREAMLIT DASHBOARD (FULL VERSION)
# =========================================================

import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

import streamlit as st
import plotly.graph_objects as go
import shap

from pymongo import MongoClient

# ---------------------------------------------------------
# Path & Config
# ---------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import *

# ---------------------------------------------------------
# Streamlit Page Config
# ---------------------------------------------------------
st.set_page_config(
    page_title="AQI Automation – Hyderabad",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    st.error("❌ No data found in Feature Store. Run data pipeline first.")
    st.stop()

if "_id" in df.columns:
    df.drop(columns="_id", inplace=True)

df = df.sort_values("timestamp").reset_index(drop=True)

# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------
st.sidebar.title("🌍 AQI Automation – Hyderabad")

forecast_days = st.sidebar.slider("Forecast Horizon (Days)", 1, 7, 3)
st.sidebar.markdown(f"**Forecast Horizon:** {forecast_days} Days")

pollutants_to_show = st.sidebar.multiselect(
    "Pollutants to Display",
    ["PM2.5", "PM10", "O₃", "NO₂", "SO₂", "CO"],
    default=["PM2.5"]
)

show_shap = st.sidebar.checkbox("Show Explainability", True)

# ---------------------------------------------------------
# Load Model & Metrics
# ---------------------------------------------------------
MODEL_PATH = "models/best_model.pkl"
METRICS_PATH = "models/model_metrics.json"

if not os.path.exists(MODEL_PATH):
    st.error("❌ Trained model not found. Run training pipeline.")
    st.stop()

model = joblib.load(MODEL_PATH)

metrics = {}
if os.path.exists(METRICS_PATH):
    metrics = json.load(open(METRICS_PATH))

best_model_name = max(metrics, key=lambda k: metrics[k]["R2"]) if metrics else "Unknown"

st.sidebar.markdown("### 🏆 Best Model")
st.sidebar.success(best_model_name)

st.sidebar.markdown("### 📊 Model Performance")
for k, v in metrics.items():
    st.sidebar.write(f"**{k}** → RMSE: {v['RMSE']:.2f}, R²: {v['R2']:.2f}")

# ---------------------------------------------------------
# AQI Breakpoints & Category
# ---------------------------------------------------------
AQI_BREAKPOINTS = [
    (0, 50, "Good", "🟢"),
    (51, 100, "Moderate", "🟡"),
    (101, 150, "Unhealthy (Sensitive)", "🟠"),
    (151, 200, "Unhealthy", "🔴"),
    (201, 300, "Very Unhealthy", "🟣"),
    (301, 500, "Hazardous", "⚫"),
]

def aqi_category(pm):
    for low, high, category, emoji in AQI_BREAKPOINTS:
        if low <= pm <= high:
            return category, emoji
    return "Hazardous", "⚫"

# AQI computation function per pollutant
def compute_overall_aqi(row):
    pollutants = ["pm2_5","pm10","ozone","nitrogen_dioxide","sulphur_dioxide","carbon_monoxide"]
    # Use max AQI as overall AQI
    return max([row[p] for p in pollutants])

# ---------------------------------------------------------
# Header
# ---------------------------------------------------------
st.markdown("""
<div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); border-radius: 15px; margin-bottom: 20px;">
    <h1 style="color: white; font-size: 3rem; margin: 0;">🌍 AQI Automation</h1>
    <h2 style="color: #FFD700; font-size: 1.5rem; margin: 10px 0;">Intelligent AQI Forecasting</h2>
    <p style="color: #E0E0E0; font-size: 1.1rem; margin: 10px 0;">Multi-Pollutant • Meteorology • Explainable ML • Forecast Horizon</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Forecast Logic
# ---------------------------------------------------------
FEATURE_ORDER = [
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

# Add lags
df["lag1"] = df["pm2_5"].shift(1)
df["lag2"] = df["pm2_5"].shift(2)
df["lag3"] = df["pm2_5"].shift(3)
df.dropna(inplace=True)

# ---------------------------------------------------------
# Latest Snapshot
# ---------------------------------------------------------
latest = df.iloc[-1]

# Compute overall AQI
latest_overall_aqi = compute_overall_aqi(latest)
overall_category, overall_emoji = aqi_category(latest_overall_aqi)

st.markdown("---")
col1, col2, col3 = st.columns([2,1,1])

with col1:
    st.markdown(f"""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white; margin-bottom: 20px;">
        <h1 style="font-size: 4rem; margin: 0; color: white;">{latest_overall_aqi:.0f}</h1>
        <h2 style="font-size: 2rem; margin: 5px 0; color: #FFD700;">Overall AQI</h2>
        <h3 style="font-size: 1.5rem; margin: 5px 0; color: #90EE90;">{overall_category} {overall_emoji}</h3>
        <p style="font-size: 1rem; margin: 10px 0; opacity: 0.9;">Current Air Quality Index</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("### 📊 Pollutants (µg/m³)")
    for p in ["pm2_5","pm10","ozone","nitrogen_dioxide","sulphur_dioxide","carbon_monoxide"]:
        st.metric(p.upper(), f"{latest[p]:.1f}")

with col3:
    st.markdown("### 🌡️ Weather Conditions")
    st.metric("Temperature", f"{latest.temperature_2m:.1f}°C")
    st.metric("Humidity", f"{latest.relative_humidity_2m}%")
    st.metric("Wind Speed", f"{latest.wind_speed_10m} m/s")
    st.metric("Last Updated", latest.timestamp.strftime("%H:%M"))

current = latest.copy()
current["hour"] = pd.to_datetime(current["timestamp"]).hour
current["day"] = pd.to_datetime(current["timestamp"]).day
current["month"] = pd.to_datetime(current["timestamp"]).month
forecast = []
dates = []

for i in range(forecast_days):
    pred = model.predict(pd.DataFrame([current[FEATURE_ORDER]]))[0]
    pred = round(float(pred),2)
    forecast.append(pred)
    dates.append((datetime.now() + timedelta(days=i+1)).strftime("%Y-%m-%d"))

    current["lag3"] = current["lag2"]
    current["lag2"] = current["lag1"]
    current["lag1"] = pred

forecast_df = pd.DataFrame({
    "Date": dates,
    "PM2.5": forecast
})

forecast_df[["Category","Emoji"]] = forecast_df["PM2.5"].apply(lambda x: pd.Series(aqi_category(x)))

# ---------------------------------------------------------
# Forecast Cards
# ---------------------------------------------------------
forecast_display = forecast_df.head(min(forecast_days,7))
n_cols = min(len(forecast_display),4)

for i in range(0,len(forecast_display),n_cols):
    row_data = forecast_display.iloc[i:i+n_cols]
    cols = st.columns(len(row_data))
    for j, (_, row) in enumerate(row_data.iterrows()):
        with cols[j]:
            st.metric(
                label=f"{row.Date} {row.Emoji}",
                value=f"{row['PM2.5']} µg/m³",
                delta=row["Category"]
            )

# ---------------------------------------------------------
# Forecast + Observed Trend Chart
# ---------------------------------------------------------
recent_observed = df.tail(24).copy()
recent_observed["timestamp"] = pd.to_datetime(recent_observed["timestamp"])
recent_observed["time_label"] = recent_observed["timestamp"].dt.strftime("%m/%d %I%p")

forecast_timestamps = pd.date_range(
    start=datetime.now(),
    periods=forecast_days+1,
    freq='D'
)[1:]

forecast_df["timestamp"] = forecast_timestamps
forecast_df["time_label"] = forecast_df["timestamp"].dt.strftime("%m/%d")

plot_df = pd.concat([
    recent_observed[["time_label","pm2_5"]].rename(columns={"pm2_5":"AQI"}),
    forecast_df[["time_label","PM2.5"]].rename(columns={"PM2.5":"AQI"})
]).reset_index(drop=True)

fig = go.Figure()
# Observed
fig.add_trace(go.Scatter(
    x=recent_observed["time_label"],
    y=recent_observed["pm2_5"],
    mode="lines+markers",
    name="Observed PM2.5",
    line=dict(color="blue", width=2),
    marker=dict(size=6),
    hovertemplate="Time: %{x}<br>Observed AQI: %{y:.1f}<extra></extra>"
))
# Forecast
fig.add_trace(go.Scatter(
    x=forecast_df["time_label"],
    y=forecast_df["PM2.5"],
    mode="lines+markers",
    name="Forecasted PM2.5",
    line=dict(color="red", width=3, dash="dash"),
    marker=dict(size=8, symbol="diamond"),
    hovertemplate="Date: %{x}<br>Forecasted AQI: %{y:.1f}<extra></extra>"
))

# Color-coded threshold areas
threshold_colors = [
    (0,50,"green","Good"),
    (51,100,"yellow","Moderate"),
    (101,150,"orange","Unhealthy (Sensitive)"),
    (151,200,"red","Unhealthy"),
    (201,300,"purple","Very Unhealthy"),
    (301,max(plot_df["AQI"].max(),400),"maroon","Hazardous")
]
for y0,y1,color,label in threshold_colors:
    fig.add_hrect(y0=y0,y1=y1,fillcolor=color,opacity=0.1,line_width=0,annotation_text=label,annotation_position="top left")

fig.update_layout(
    title="AQI Trend: Observed + Forecast",
    xaxis_title="Time",
    yaxis_title="AQI (PM2.5 µg/m³)",
    height=500,
    template="plotly_white",
    hovermode="x unified"
)

st.plotly_chart(fig,use_container_width=True)

# ---------------------------------------------------------
# Data Export
# ---------------------------------------------------------
st.subheader("📥 Download Forecast Data")
csv_data = forecast_df.to_csv(index=False)
st.download_button(
    label="Download Forecast as CSV",
    data=csv_data,
    file_name=f"aqi_forecast_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
    mime="text/csv",
    key="download-csv"
)

# ---------------------------------------------------------
# SHAP Explainability
# ---------------------------------------------------------
if show_shap:
    st.subheader("🧠 Feature Importance (SHAP)")

    try:
        X = df[FEATURE_ORDER]
        explainer = shap.Explainer(model, X)
        shap_values = explainer(X)
        importance = np.abs(shap_values.values).mean(axis=0)
        imp_df = pd.DataFrame({
            "Feature": FEATURE_ORDER,
            "Impact": importance
        }).sort_values("Impact", ascending=False)

        st.write("**Top factors influencing AQI prediction:**")
        st.bar_chart(imp_df.set_index("Feature").head(6))

    except Exception as e:
        st.warning(f"SHAP explanation failed: {e}")

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown("---")
st.markdown("Developed by **Laraib Liaquat** | AQI Automation – Multi-Pollutant • CI/CD • Explainable ML")
