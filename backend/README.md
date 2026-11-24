# HealthTrend AI — ETL and modelling

## Verified disease dataset
The repository contains 22 national monthly malaria-positive observations: Jan–Dec 2024 from NCVBDC's December 2024 report and Jan–Oct 2025 from NCVBDC's October 2025 report. See `../data/processed/india_malaria_monthly_tpc_2024_2025.csv`.

## Ingestion
- `healthtrend.ingestion` normalizes month starts, rejects negative counts and duplicate months, and extracts TPC/Positive Current Year rows from official NCVBDC MMIS PDFs.
- `scripts/ingest_mmis.py` downloads the selected official reports and can upsert them into Supabase with server-side credentials.
- `load_hmis_ipd_monthly_csv` requires the exact HMIS M14 inpatient-admissions indicator and Total category. For district/sub-district exports it also requires the combined facility aggregate before summing sub-districts.
- Candidate national HMIS monthly extracts: FY 2019–20 (Dataful 6222), FY 2020–21 (6221), FY 2021–22 (6220). Each is state/month-level and includes an All India row. The M14 admissions indicator must be confirmed in each downloaded CSV; the ingestion script fails closed if it is absent.

## Download and ingest the HMIS monthly extracts
Download the CSV versions of these three public datasets:
- https://dataful.in/datasets/6222/ (FY 2019–20)
- https://dataful.in/datasets/6221/ (FY 2020–21)
- https://dataful.in/datasets/6220/ (FY 2021–22)

Then run (replace the local file paths with your downloaded CSV paths):
```bash
PYTHONPATH=. python scripts/ingest_hmis_ipd.py \
  --input path/to/hmis_2019_20.csv --source-name "HMIS State Monthly FY2019-20" --source-url https://dataful.in/datasets/6222/ \
  --input path/to/hmis_2020_21.csv --source-name "HMIS State Monthly FY2020-21" --source-url https://dataful.in/datasets/6221/ \
  --input path/to/hmis_2021_22.csv --source-name "HMIS State Monthly FY2021-22" --source-url https://dataful.in/datasets/6220/ \
  --state "All India"
```
The script checks the exact M14 indicator and requires Total-category observations. It combines 36 months only if the files actually contain that indicator and the months are unique. Add `--push-supabase` only in a trusted environment with `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` set.

## Modelling
`healthtrend.models.compare_six_models` implements Decision Tree, Random Forest, XGBoost, ARIMA, SARIMA and Prophet where installed. All models use a shared chronological holdout and rolling one-step-ahead evaluation. It requires 36 contiguous monthly observations. The loaded malaria series currently has 22 months, so malaria model scoring is intentionally blocked. The HMIS admission series has not yet been ingested.

## Tests
```bash
python -m pip install -r requirements-ci.txt
PYTHONPATH=. pytest -q
```

## Run malaria ingestion
```bash
pip install -r requirements.txt
PYTHONPATH=. python scripts/ingest_mmis.py
```
Add `--push-supabase` only with server-side secrets. Never commit service-role credentials or place them in Vite/frontend code.

## Run model comparison and persist results
```bash
PYTHONPATH=. python scripts/run_model_comparison.py --csv ../data/processed/your_validated_monthly_series.csv --target-name hospital_admissions --push-supabase
```
Model scores and forecast rows are written to Supabase only after a completed real-data evaluation.

## Research integrity
The original presentation labels its sample metrics as illustrative randomly generated values, not experimental findings. Those values are not reused. Aggregate public data only; this is not a clinical diagnosis or patient-level decision-support tool.
