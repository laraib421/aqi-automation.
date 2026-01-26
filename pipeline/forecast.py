from datetime import timedelta

def forecast_next_days(model, last_row, feature_order, days=3):
    current = last_row.copy()
    preds = []

    for i in range(days):
        p = model.predict([current[feature_order]])[0]
        preds.append(round(p,2))

        current["lag3"], current["lag2"], current["lag1"] = (
            current["lag2"], current["lag1"], p
        )

    return preds
