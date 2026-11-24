# HealthTrend AI — ETL and modelling

## Verified disease dataset
The repository contains 22 national monthly malaria-positive observations: Jan–Dec 2024 from NCVBDC's December 2024 report and Jan–Oct 2025 from NCVBDC's October 2025 report. See `../data/processed/india_malaria_monthly_tpc_2024_2025.csv`.

## Ingestion
- `healthtrend.ingestion` normalizes month starts, rejects negative counts and duplicate months, and extracts TPC/Positive Current Year rows from official NCVBDC MMIS PDFs.
- `scripts/ingest_mmis.py` downloads the selected official reports and can upsert them into Supabase with server-side credentials.
- `load_hmis_ipd_monthly_csv` requires the exact HMIS monthly inpatient-admissions indicator, the Total category, and (for district/sub-district extracts) the combined facility aggregate. It groups sub-district records to the district-month level without summing overlapping facility variants.
- HMIS IPD candidate: Dataful dataset 8141 (The Dangs, Gujarat, FY 2014–15) explicitly documents the exact monthly inpatient-admission indicator. Download and audit the source CSV before loading. National HMIS monthly datasets and Tamil Nadu district-month datasets are catalogued, but their exact M14 indicator must be confirmed per file.

## Modelling
`healthtrend.models.compare_six_models` implements Decision Tree, Random Forest, XGBoost, ARIMA, SARIMA and Prophet where installed. All models use a shared chronological holdout and rolling one-step-ahead evaluation. It requires 36 contiguous monthly observations. The loaded malaria series currently has 22 months, so malaria model scoring is intentionally blocked. No hospital-admission series has yet been loaded.

## Run tests
```bash
python -m pip install -r requirements-ci.txt
PYTHONPATH=. pytest -q
```

## Run malaria ingestion
```bash
pip install -r requirements.txt
PYTHONPATH=. python scripts/ingest_mmis.py
```
Add `--push-supabase` only in a trusted environment with `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` set. Never commit the service-role key or place it in Vite/frontend code.

## Run model comparison
```bash
PYTHONPATH=. python scripts/run_model_comparison.py --csv ../data/processed/india_malaria_monthly_tpc_2024_2025.csv
```
The current dataset returns a data-readiness error rather than fabricated scores.

## Research integrity
The original presentation labels its sample metrics as illustrative randomly generated values, not experimental findings. Those values are not reused. Aggregate public data only; this is not a clinical diagnosis or patient-level decision-support tool.
