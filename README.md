# HealthTrend AI
**Comparative Analysis of Machine Learning and Time-Series Models for Disease Trend Mining and Hospital Admission Forecasting**

HealthTrend AI is a public research capstone for warehousing aggregate Indian public-health observations, mining disease trends, and comparing machine-learning and time-series forecasting methods.

## Verified data currently loaded
- 22 monthly national malaria-positive observations from January 2024 to October 2025.
- January–December 2024: NCVBDC December 2024 MMIS country summary (TPC Current Year).
- January–October 2025: NCVBDC October 2025 MMIS India summary (Positive Current Year).
- Source URLs and report periods are retained per observation in the processed CSV and Supabase source registry.
- This series is national malaria surveillance data, not district-level data and not hospital admissions.

## Project modules
1. Data warehousing and preprocessing.
2. Disease trend mining: Decision Tree, Random Forest and XGBoost.
3. Forecasting: ARIMA, SARIMA and Prophet.
4. Model comparison on a common chronological test period.

## Stack
- Frontend: React, TypeScript, Vite, Recharts.
- Database: Supabase PostgreSQL with RLS and realtime case-table notifications.
- ETL and modelling: Python, pandas, scikit-learn, statsmodels, XGBoost, Prophet.
- CI: GitHub Actions.

## Run locally
```bash
npm install
npm run dev
```
Copy `.env.example` to `.env.local` if you need to override the public Supabase URL/key.

## ETL and modelling
```bash
cd backend
python -m pip install -r requirements.txt
PYTHONPATH=. python scripts/ingest_mmis.py
PYTHONPATH=. pytest -q
PYTHONPATH=. python scripts/run_model_comparison.py --csv ../data/processed/india_malaria_monthly_tpc_2024_2025.csv
```
The ingestion script can upsert to Supabase with `--push-supabase` when `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are set in a trusted environment. Never commit service-role keys or expose them in browser code.

## Research limitations
- The verified time series currently has 22 contiguous months. Model comparison requires at least 36 months and therefore intentionally refuses to report model scores yet.
- Public HMIS datasets include monthly medical-service indicators, but an exact indicator with a defensible definition of hospital admissions has not yet been selected and ingested.
- The application never substitutes illustrative presentation metrics for measured model results.
- Aggregate public data only. This is not a clinical diagnosis or patient-level decision-support tool.

See [data-source validation](docs/DATA_SOURCES.md), [methodology](docs/METHODOLOGY.md), and [backend instructions](backend/README.md).
