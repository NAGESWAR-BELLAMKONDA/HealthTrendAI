from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX

from .metrics import forecast_metrics

MIN_MONTHS_FOR_COMPARISON = 36


@dataclass
class ModelResult:
    model_name: str
    metrics: dict[str, float | None]
    predictions: list[dict[str, float | str]]


def make_lag_features(values: pd.Series, dates: pd.Series) -> pd.DataFrame:
    x = pd.DataFrame({"y": values.to_numpy()}, index=pd.to_datetime(dates))
    for lag in (1, 2, 3, 6, 12):
        x[f"lag_{lag}"] = x["y"].shift(lag)
    x["rolling_mean_3"] = x["y"].shift(1).rolling(3).mean()
    x["rolling_mean_6"] = x["y"].shift(1).rolling(6).mean()
    month = x.index.month
    x["month_sin"] = np.sin(2 * np.pi * month / 12)
    x["month_cos"] = np.cos(2 * np.pi * month / 12)
    return x.dropna()


def _one_step_ml(model, history: list[float], next_date: pd.Timestamp) -> float:
    h = pd.Series(history, dtype=float)
    features = {
        "lag_1": h.iloc[-1], "lag_2": h.iloc[-2], "lag_3": h.iloc[-3],
        "lag_6": h.iloc[-6], "lag_12": h.iloc[-12],
        "rolling_mean_3": h.iloc[-3:].mean(), "rolling_mean_6": h.iloc[-6:].mean(),
        "month_sin": math.sin(2 * math.pi * next_date.month / 12),
        "month_cos": math.cos(2 * math.pi * next_date.month / 12),
    }
    row = pd.DataFrame([features])
    return max(0.0, float(model.predict(row)[0]))


def compare_six_models(frame: pd.DataFrame, date_col: str = "date", value_col: str = "cases") -> list[ModelResult]:
    """Compare six models with a common chronological holdout and rolling one-step forecasts.

    At each test month, the preceding actual month is assumed to have become available.
    This is a one-step-ahead operational evaluation, not a fixed-origin multi-month forecast.
    """
    from .ingestion import validate_monthly_observations
    clean = validate_monthly_observations(frame, date_col, value_col)
    if len(clean) < MIN_MONTHS_FOR_COMPARISON:
        raise ValueError(
            f"Need at least {MIN_MONTHS_FOR_COMPARISON} contiguous monthly observations "
            f"for a defensible seasonal comparison; received {len(clean)}."
        )
    dates = pd.to_datetime(clean[date_col])
    expected = pd.date_range(dates.iloc[0], dates.iloc[-1], freq="MS")
    if len(expected) != len(clean) or not dates.reset_index(drop=True).equals(pd.Series(expected)):
        raise ValueError("Monthly series has gaps or irregular dates; do not interpolate silently")

    values = clean[value_col].astype(float).reset_index(drop=True)
    split = max(24, int(len(clean) * 0.8))
    if split >= len(clean) - 1:
        split = len(clean) - 1
    train_dates, test_dates = dates.iloc[:split].reset_index(drop=True), dates.iloc[split:].reset_index(drop=True)
    train_values = values.iloc[:split].reset_index(drop=True)
    feature_frame = make_lag_features(values, dates)
    train_features = feature_frame[feature_frame.index < test_dates.iloc[0]]
    X_train = train_features.drop(columns="y")
    y_train = train_features["y"]

    results: list[ModelResult] = []
    ml_models = [
        ("Decision Tree", DecisionTreeRegressor(max_depth=5, min_samples_leaf=2, random_state=42)),
        ("Random Forest", RandomForestRegressor(n_estimators=300, min_samples_leaf=2, random_state=42, n_jobs=-1)),
    ]
    try:
        from xgboost import XGBRegressor
        ml_models.append(("XGBoost", XGBRegressor(n_estimators=300, max_depth=3, learning_rate=0.03,
                                                   subsample=0.9, colsample_bytree=0.9,
                                                   objective="reg:squarederror", random_state=42, n_jobs=2)))
    except ImportError:
        pass

    for name, model in ml_models:
        model.fit(X_train, y_train)
        history = train_values.tolist()
        preds = []
        for idx in range(split, len(clean)):
            pred = _one_step_ml(model, history, pd.Timestamp(dates.iloc[idx]))
            preds.append(pred)
            history.append(float(values.iloc[idx]))
        results.append(_result(name, test_dates, values.iloc[split:].tolist(), preds))

    # Refit time-series models at each test origin so all methods use the same
    # one-step-ahead information set.
    for name, order, seasonal_order in [
        ("ARIMA", (1, 1, 1), None),
        ("SARIMA", (1, 1, 1), (1, 1, 1, 12)),
    ]:
        history = train_values.tolist()
        preds = []
        for idx in range(split, len(clean)):
            if name == "ARIMA":
                fitted = ARIMA(history, order=order).fit()
            else:
                fitted = SARIMAX(history, order=order, seasonal_order=seasonal_order,
                                 enforce_stationarity=False, enforce_invertibility=False).fit(disp=False)
            preds.append(max(0.0, float(fitted.forecast(1)[0])))
            history.append(float(values.iloc[idx]))
        results.append(_result(name, test_dates, values.iloc[split:].tolist(), preds))

    try:
        from prophet import Prophet
        history = train_values.tolist()
        preds = []
        for idx in range(split, len(clean)):
            pframe = pd.DataFrame({"ds": train_dates.tolist() + test_dates.iloc[:len(preds)].tolist(),
                                   "y": history})
            prophet = Prophet(yearly_seasonality=True, weekly_seasonality=False,
                              daily_seasonality=False, interval_width=0.8)
            prophet.fit(pframe)
            future = prophet.make_future_dataframe(periods=1, freq="MS", include_history=False)
            preds.append(max(0.0, float(prophet.predict(future).iloc[-1]["yhat"])))
            history.append(float(values.iloc[idx]))
        results.append(_result("Prophet", test_dates, values.iloc[split:].tolist(), preds))
    except ImportError:
        pass

    return results


def _result(name: str, dates: pd.Series, actual: list[float], predicted: list[float]) -> ModelResult:
    metrics = forecast_metrics(actual, predicted)
    predictions = [
        {"date": pd.Timestamp(d).strftime("%Y-%m-%d"), "actual": float(a), "predicted": float(p)}
        for d, a, p in zip(dates, actual, predicted)
    ]
    return ModelResult(name, metrics, predictions)
