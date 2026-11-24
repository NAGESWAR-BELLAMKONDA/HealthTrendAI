# HealthTrend AI — ETL, mining and modelling

## Current verified series
The repository contains 22 India national monthly malaria-positive observations, January 2024–October 2025, from official NCVBDC MMIS summary rows. The values are not chart approximations. See `../docs/DATA_SOURCES.md`.

## Data mining
`healthtrend.mining` provides descriptive trend statistics, linear slope, month-of-year means and period-over-period movement; robust median/MAD anomaly screening; and K-means clustering on standardized level, lag, rolling mean and calendar-seasonality features.

Run locally:
```bash
python -m pip install -r requirements-ci.txt
PYTHONPATH=. python scripts/run_data_mining.py --csv ../data/processed/india_malaria_monthly_tpc_2024_2025.csv
```
Persist analyses to Supabase with `--push-supabase` in a trusted environment with server-side service-role credentials.

## Ingestion
`scripts/ingest_mmis.py` downloads the registered official 2024 and 2025 NCVBDC MMIS PDFs, extracts exact monthly Positive/TPC rows, validates non-negative and unique month values, and saves the processed CSV. Add `--push-supabase` to upsert source metadata, dimensions and fact rows.

The monthly scheduled GitHub Actions workflow re-runs the registered-source ETL and saves mining results. It needs repository Actions secrets `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`. These secrets are never committed or exposed to the frontend.

## Hospital admissions
The HMIS M14 parser in `healthtrend.ingestion.load_hmis_ipd_monthly_csv` accepts the exact monthly inpatient indicator and TOTAL category. It requires a combined facility aggregate when that field exists, aggregates sub-district rows only after those filters, preserves provisional source notes, rejects negative counts and never interpolates missing months.

The free Tamil Nadu monthly HMIS export located in the audit is scoped to Family Planning, Maternal Health and Immunization, not IPD. A free, long-span monthly M14 CSV has not yet been confirmed. See `../docs/DATA_SOURCES.md`.

When a validated HMIS M14 CSV is obtained:
```bash
PYTHONPATH=. python scripts/ingest_hmis_ipd.py \
  --input path/to/hmis_ipd.csv \
  --source-name "HMIS monthly IPD export" \
  --source-url "https://hmis.mohfw.gov.in/#/" \
  --state "Tamil Nadu" --district "Dindigul"
```
Add `--push-supabase` only with trusted server-side secrets.

## Model comparison
`healthtrend.models.compare_six_models` implements Decision Tree, Random Forest, XGBoost, ARIMA, SARIMA and Prophet when optional packages are installed. All models use a common chronological holdout and rolling one-step-ahead information set. A minimum of 36 contiguous monthly observations is required; missing months are not silently filled.

```bash
PYTHONPATH=. python scripts/run_model_comparison.py --csv ../data/processed/hmis_ipd_monthly.csv --target-name hospital_admissions --push-supabase
```

## Tests
```bash
python -m pip install -r requirements-ci.txt
PYTHONPATH=. pytest -q
```

## Research integrity
The original presentation labels its example model metrics as illustrative/randomly generated. They are not reused. No model score or admissions count is fabricated. The system is for aggregate research and education, not clinical diagnosis or patient-level decisions.
