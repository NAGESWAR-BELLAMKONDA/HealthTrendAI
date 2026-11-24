# Research methodology

Compare Machine Learning and time-series methods for disease trend mining and aggregate hospital-admission forecasting.

Models: Decision Tree, Random Forest, XGBoost, ARIMA, SARIMA and Prophet. ML features include lag values, rolling summaries and calendar variables. Time-series diagnostics include stationarity checks, decomposition, ACF and PACF where appropriate.

Evaluation protocol: define target/geography/time grain/horizon; sort chronologically; use one common final chronological test window; fit preprocessing only on training data; calculate MAE, RMSE and MAPE from identical test observations; document zero handling for MAPE and consider WAPE or sMAPE; persist parameters, date ranges, metrics and forecasts; discuss uncertainty and practical usefulness.

Integrity: the source presentation explicitly labels its demo metrics as randomly generated illustrative data, not experimental findings. This application does not present them as real results. Use aggregate public data only; this is not a clinical diagnosis or patient-level decision tool.