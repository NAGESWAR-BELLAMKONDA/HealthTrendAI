# Forecasting and ETL workspace

Python experiments belong here. Install dependencies in a virtual environment with `pip install -r requirements.txt`.

Before training, select and validate a real source dataset, document its license/geography/time grain, aggregate it to a consistent time series, and create a chronological holdout. The first modelling release will persist run metadata and forecasts to Supabase using a server-side secret only. Never place a service-role key in the browser or commit secrets.

The current repository intentionally does not ship fabricated clinical observations or pre-filled performance scores.