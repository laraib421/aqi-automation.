# AQI Hyderabad Enhancement Tasks

## 1. Update Dependencies
- [ ] Add XGBoost and LightGBM to requirements.txt

## 2. Model Training Pipeline
- [x] Update models/train_models_compare.py to include XGBoost and LightGBM
- [x] Ensure best model selection based on lowest RMSE and highest R²
- [x] Configure LightGBM with leaf-wise growth for efficiency

## 3. Forecasting Pipeline
- [x] Update pipeline/forecast.py to support variable forecast days (1-7)

## 4. Streamlit Dashboard Enhancements
- [x] Add sidebar slider for forecast horizon (1-7 days)
- [x] Enhance visualization: Merge observed + predicted data, color-coded thresholds, tooltips
- [x] Add CSV download button for predictions
- [x] Ensure all pollutants (CO, NO2, O3, SO2) and meteorological variables are displayed

## 5. Testing and Validation
- [x] Test model training with new algorithms (Ridge selected as best model)
- [ ] Test dynamic forecasting (requires trained model)
- [ ] Test dashboard features (requires data and model)
- [ ] Test CSV export functionality (requires forecast data)
