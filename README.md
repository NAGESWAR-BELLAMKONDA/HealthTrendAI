# HealthTrend AI
**Comparative Analysis of Machine Learning and Time-Series Models for Disease Trend Mining and Hospital Admission Forecasting**

A public research capstone for warehousing aggregate Indian public-health observations, mining disease trends, and comparing forecasting methods.

## Verified disease data currently loaded
- 22 monthly national malaria-positive observations from January 2024 to October 2025.
- Jan–Dec 2024: NCVBDC December 2024 MMIS country summary (TPC Current Year).
- Jan–Oct 2025: NCVBDC October 2025 MMIS India summary (Positive Current Year).
- Source URLs and report periods are retained in the processed CSV and Supabase.
- This is national malaria surveillance data, not district-level data or hospital admissions.

## Hospital admissions data research
HMIS monthly district/sub-district data contains the explicit inpatient-admissions indicator “Total number of patients admitted (Inpatients) during the month”. Six consecutive Dindigul, Tamil Nadu fiscal-year extracts (2016–17 to 2021–22) are catalogued as a candidate 72-month series. The exact indicator must be confirmed in each CSV before admission records are loaded. See [source validation](docs/DATA_SOURCES.md).

## Stack
React + TypeScript + Vite, Supabase PostgreSQL with RLS/realtime, Python pandas/scikit-learn/statsmodels/XGBoost/Prophet, GitHub Actions.

## Local setup
```bash
npm install
npm run dev
```

## ETL and modelling
```bash
cd backend
python -m pip install -r requirements.txt
PYTHONPATH=. python scripts/ingest_mmis.py
# Download the six Dindigul FY2016-17 to FY2021-22 CSVs; see backend/README.md for the full command
# and the exact indicator/category validation.
PYTHONPATH=. pytest -q
PYTHONPATH=. python scripts/run_model_comparison.py --csv ../data/processed/hmis_ipd_monthly.csv --target-name hospital_admissions --push-supabase
```
MMIS ingestion can push to Supabase with `--push-supabase` when server-side `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are set. Never commit service-role credentials.

## Current model readiness
- The malaria series has 22 contiguous monthly observations; the model comparison requires at least 36 and intentionally refuses to publish scores yet.
- The monthly HMIS inpatient-admissions indicator has been identified, but its raw data has not yet been ingested.
- No hospital-admission values or fabricated model metrics are in the database.
- Aggregate public data only; not a clinical diagnosis system.

See [methodology](docs/METHODOLOGY.md), [data sources](docs/DATA_SOURCES.md), [backend instructions](backend/README.md), and [GitHub Pages deployment](docs/DEPLOYMENT.md).
