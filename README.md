# HealthTrend AI

**Comparative Analysis of Machine Learning and Time-Series Models for Disease Trend Mining and Hospital Admission Forecasting**

A Data Mining capstone application for public-health data warehousing, disease trend discovery, anomaly screening, clustering and model comparison.

## Product modules
- Overview and realtime warehouse status
- Disease Explorer with filters and source traceability
- Star-schema Data Warehouse
- Data Mining Studio: trend summaries, robust anomaly detection and K-means pattern clustering
- ML Laboratory: Decision Tree, Random Forest and XGBoost
- Forecasting and Model Comparison: ARIMA, SARIMA and Prophet
- Data Sources and provenance registry
- Role-based User Access for administrators

## Technology
- Frontend: React, TypeScript, Vite, Recharts, Lucide
- Identity/database: Supabase Auth, PostgreSQL, Row Level Security, Realtime
- Analytics: Python, Pandas, NumPy, scikit-learn, Statsmodels, XGBoost, Prophet
- Delivery: GitHub Actions and GitHub Pages

## Verified dataset in the repository
- 31 exact India-wide malaria-positive observations from NCVBDC MMIS: January–September 2023, January–December 2024 and January–October 2025.
- The values are extracted from the exact monthly report rows and retain source-report provenance.
- The September 2026 report is available, but its extracted graph descriptions provide approximate chart-read values rather than a machine-readable exact monthly series. Those estimates are not loaded.
- Hospital admissions are a separate target. The free HMIS options reviewed either do not contain IPD or are annual/limited-period. The hospital-admissions fact table remains empty until a verified monthly M14 source is supplied.
- See [data-source audit](docs/DATA_SOURCES.md).

## Local development
```bash
npm install
npm run dev
```

Set `VITE_SUPABASE_URL` and `VITE_SUPABASE_PUBLISHABLE_KEY` in `.env.local` if using a different Supabase project. The public publishable key is safe for the browser when RLS is correctly configured. Never put a service-role key in frontend code.

## Backend tests and analytics
```bash
cd backend
python -m pip install -r requirements-ci.txt
PYTHONPATH=. pytest -q
PYTHONPATH=. python scripts/run_data_mining.py --csv ../data/processed/india_malaria_monthly_tpc_2023_2025.csv
```

For Supabase ingestion/mining, install `requirements-pipeline.txt` and set server-side `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` only in a trusted environment. The monthly GitHub Actions workflow is `.github/workflows/monthly-data-pipeline.yml`; add both values under **Settings → Secrets and variables → Actions** before manually running it.

## Research evaluation
The six-model comparison uses the same chronological holdout and rolling one-step-ahead evaluation. It requires at least 36 contiguous monthly observations. The current malaria series has 31 observations with a three-month gap in 2023, so model scoring is intentionally blocked. No illustrative PPT scores are reused as results.

## Deployment
See [GitHub Pages and Supabase setup](docs/DEPLOYMENT.md) and [Auth/SMTP setup](docs/AUTH_SETUP.md). Initial admin role setup is described there. Aggregate public-health research only; this is not a diagnosis or clinical decision-support system.
