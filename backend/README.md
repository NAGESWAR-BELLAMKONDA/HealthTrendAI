# HealthTrend AI — ETL and modelling

## Verified disease dataset
The repository contains 31 national monthly malaria-positive observations: Jan–Sep 2023 from NCVBDC's October 2023 report, Jan–Dec 2024 from its December 2024 report and Jan–Oct 2025 from its October 2025 report. See `../data/processed/india_malaria_monthly_tpc_2023_2025.csv`.

## Ingestion
- `healthtrend.ingestion` normalizes month starts, rejects negative counts and duplicate months, and extracts TPC/Positive Current Year rows from official NCVBDC MMIS PDFs.
- `scripts/ingest_mmis.py` downloads the selected official reports and can upsert them into Supabase with server-side credentials.
- `load_hmis_ipd_monthly_csv` requires the exact HMIS M14 inpatient-admissions indicator and Total category. For district/sub-district exports it also requires the combined facility aggregate before summing sub-districts.
- Recommended HMIS candidate: Dindigul, Tamil Nadu, monthly data for 2008–09 through 2021–22 (Dataful dataset 15964). It has 132,120 rows, 13 columns, monthly district detail and 601 indicator values. The exact M14 indicator must be present in the downloaded CSV; the parser fails closed if absent.
- The Dangs FY 2014–15 dataset independently confirms the exact M14 indicator wording in the HMIS monthly collection.

## Download and ingest the HMIS file
Download the CSV from https://dataful.in/datasets/15964/ and run:
```bash
PYTHONPATH=. python scripts/ingest_hmis_ipd.py \
  --input path/to/dindigul_hmis_2008_2022.csv \
  --source-name "HMIS Dindigul Monthly 2008-09 to 2021-22" \
  --source-url https://dataful.in/datasets/15964/ \
  --state "Tamil Nadu" --district "Dindigul"
```
The script requires the exact M14 indicator, Total category and combined facility aggregate. It preserves source notes (including provisional flags), checks monthly uniqueness, and does not interpolate missing values. If the CSV contains a complete M14 series, it can provide up to 168 monthly observations. Add `--push-supabase` only in a trusted environment with `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` set.

If the single long-span file lacks M14 or has gaps, the six fiscal-year Dindigul extracts are alternative files (FY 2016–17 through 2021–22): datasets 11769–11774. Their exact M14 coverage must also be checked before use.

## Modelling
`healthtrend.models.compare_six_models` implements Decision Tree, Random Forest, XGBoost, ARIMA, SARIMA and Prophet where installed. All models use a shared chronological holdout and rolling one-step-ahead evaluation. It requires 36 contiguous monthly observations. The loaded national malaria series currently has 31 months, so malaria model scoring is intentionally blocked. The Dindigul HMIS admissions series has not yet been ingested.

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
PYTHONPATH=. python scripts/run_model_comparison.py --csv ../data/processed/hmis_ipd_monthly.csv --target-name hospital_admissions --push-supabase
```
Supply the correct Supabase location ID when persisting a specific district run. Model scores and forecast rows are written only after a completed real-data evaluation.

## Research integrity
The original presentation labels its sample metrics as illustrative randomly generated values, not experimental findings. Those values are not reused. Aggregate public data only; this is not a clinical diagnosis or patient-level decision-support tool.
