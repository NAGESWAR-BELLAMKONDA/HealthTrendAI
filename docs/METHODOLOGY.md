# Research methodology

## Research target
The initial target is India national monthly malaria positive cases, based on NCVBDC MMIS. It is not an admission count. Hospital admissions remains a separate target until a validated monthly admission indicator is obtained.

## Models in scope
- Machine learning: Decision Tree, Random Forest, XGBoost.
- Time-series: ARIMA, SARIMA, Prophet.
- ML predictors: lag 1, 2, 3, 6 and 12; trailing rolling means; calendar seasonality features.

## Evaluation protocol
All models use the same final chronological holdout and rolling one-step-ahead forecasts. At each test month, preceding actual observations are assumed available. This is not a fixed-origin multi-month forecast. A minimum of 36 contiguous monthly observations is required before comparing seasonal models. The current series has 22 months, so model scoring is intentionally blocked until additional verified reports are ingested.

MAE, RMSE and MAPE are computed from identical test observations. MAPE excludes zero actual denominators and is null if all actuals are zero. No fabricated scores are displayed. Model runs and forecasts are persisted only after successful real-data training.

## Research integrity and safety
The original presentation labels its sample metrics as illustrative randomly generated values, not experimental findings. Those values are not reused. Only aggregate public data is used; this is not a clinical decision-support or diagnosis system.
