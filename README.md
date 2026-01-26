# 🌍 AQI Forecasting for Hyderabad

A comprehensive machine learning project for forecasting Air Quality Index (AQI) in Hyderabad, Pakistan. This project analyzes real-time AQI data, builds predictive models, and provides an interactive web application for AQI monitoring and forecasting.

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Data Sources](#data-sources)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Model Training](#model-training)
- [Web Application](#web-application)
- [Exploratory Data Analysis](#exploratory-data-analysis)
- [Model Evaluation](#model-evaluation)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Project Overview

This project aims to:
- Collect and analyze real-time AQI data from Hyderabad
- Understand patterns in key pollutants (PM2.5, PM10, NO2, O3)
- Build machine learning models for AQI forecasting
- Provide interpretable model explanations using SHAP
- Deploy an interactive web application for AQI monitoring

## ✨ Features

- **Real-time Data Collection**: Automated pipeline for fetching AQI data
- **Comprehensive EDA**: Detailed exploratory data analysis with visualizations
- **Machine Learning Models**: Multiple ML algorithms (XGBoost, LightGBM, etc.) for forecasting
- **Model Interpretability**: SHAP-based explanations for model predictions
- **Web Application**: Streamlit-based interactive dashboard
- **Automated Pipeline**: GitHub Actions workflow for continuous data processing
- **MongoDB Integration**: Cloud-based data storage and retrieval

## 📊 Data Sources

- **Primary Data**: Real-time AQI measurements from Hyderabad monitoring stations
- **Storage**: MongoDB Atlas for engineered features and raw data
- **Pollutants Tracked**: PM2.5, PM10, NO2, O3, and meteorological factors

## 🏗️ Project Structure

```
AQIHYDERABAD/
│
├── .github/workflows/
│   └── pipeline.yml              # GitHub Actions CI/CD pipeline
│
├── app/
│   └── app.py                    # Streamlit web application
│
├── data/
│   ├── fetch_raw_data.py         # Raw data collection script
│   ├── fetch_historical_data.py  # Historical data retrieval
│   └── hyderabad_aqi_eda_clean.csv  # Processed dataset
│
├── features/
│   ├── __init__.py
│   └── build_features.py         # Feature engineering pipeline
│
├── models/
│   ├── best_model.pkl            # Trained model (generated)
│   ├── model_metrics.json        # Model performance metrics
│   ├── train_models_compare.py   # Model training and comparison
│   └── predict_3_days.py         # 3-day forecasting script
│
├── notebooks/
│   └── EDA_AQI_Hyderabad_FULL.ipynb  # Comprehensive EDA notebook
│
├── explainability/
│   └── shap_analysis.py          # SHAP explanations
│
├── pipeline/
│   └── forecast.py               # Main forecasting pipeline
│
├── config.py                     # Configuration file
├── requirements.txt              # Python dependencies
├── README.md                     # Project documentation
├── TODO.md                       # Project roadmap and tasks
└── .gitignore                    # Git ignore rules
```

## 🚀 Installation

### Prerequisites

- Python 3.8+
- MongoDB Atlas account
- GitHub account (for Actions)

### Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/AQIHYDERABAD.git
   cd AQIHYDERABAD
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   - Copy `config.py` and update MongoDB credentials
   - Set up environment variables for API keys if needed

5. **Set up MongoDB:**
   - Create a MongoDB Atlas cluster
   - Update connection string in `config.py`

## 📖 Usage

### Data Pipeline

Run the complete data processing pipeline:

```bash
# Fetch raw data
python data/fetch_raw_data.py

# Build features
python features/build_features.py

# Train models
python models/train_models_compare.py
```

### Individual Components

- **Data Collection**: `python data/fetch_raw_data.py`
- **Feature Engineering**: `python features/build_features.py`
- **Model Training**: `python models/train_models_compare.py`
- **3-Day Forecast**: `python models/predict_3_days.py`

## 🤖 Model Training

The project supports multiple machine learning algorithms:

- XGBoost
- LightGBM
- Random Forest
- Gradient Boosting
- Support Vector Regression

Models are trained on engineered features including:
- Pollutant concentrations
- Temporal features (hour, day, month)
- Lag features for time series forecasting

## 🌐 Web Application

Launch the Streamlit web application:

```bash
streamlit run app/app.py
```

Features:
- Real-time AQI monitoring
- 3-day forecasting visualization
- Historical data exploration
- Model performance metrics
- SHAP-based feature importance

## 📈 Exploratory Data Analysis

The comprehensive EDA notebook (`notebooks/EDA_AQI_Hyderabad_FULL.ipynb`) includes:

- Data overview and summary statistics
- Univariate and multivariate analysis
- Temporal trend analysis (hourly, daily, monthly)
- AQI categorization
- Correlation analysis
- SHAP model explanations

## 📊 Model Evaluation

Models are evaluated using:
- Mean Absolute Error (MAE)
- Root Mean Squared Error (RMSE)
- R² Score
- Cross-validation scores

Results are saved in `models/model_metrics.json`

## 🔄 CI/CD Pipeline

The project uses GitHub Actions for automated workflows:

- **Scheduled Runs**: Hourly data collection and model retraining
- **Automated Testing**: Code quality checks
- **Deployment**: Automatic updates to the web application

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- AQI data provided by Hyderabad environmental monitoring stations
- Built with Python, scikit-learn, XGBoost, and Streamlit
- Special thanks to the open-source ML community

## 📞 Contact

For questions or contributions, please open an issue on GitHub.

---

**Note**: This project is for educational and research purposes. Always verify AQI data with official sources for critical health decisions.
