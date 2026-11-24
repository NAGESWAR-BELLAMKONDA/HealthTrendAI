# HealthTrend AI — ETL and modelling

## Verified disease dataset
The repository contains 22 national monthly malaria-positive observations: Jan–Dec 2024 from NCVBDC's December 2024 report and Jan–Oct 2025 from NCVBDC's October 2025 report. See `../data/processed/india_malaria_monthly_tpc_2024_2025.csv`.

## Ingestion
- `healthtrend.ingestion` normalizes month starts, rejects negative counts and duplicate months, and extracts TPC/Positive Current Year rows from official NCVBDC MMIS PDFs.
- `scripts/ingest_mmis.py` downloads the selected official reports and can upsert them into Supabase with server-side credentials.
- `load_hmis_ipd_monthly_csv` requires the exact HMIS M14 inpatient-admissions indicator and Total category. For district/sub-district exports it also requires the combined facility aggregate before summing sub-districts.
- A published HMIS monthly extract for The Dangs, Gujarat (FY 2014–15) confirms the exact M14 indicator wording. The Dindigul, Tamil Nadu district series is available in six yearly CSV datasets from FY 2016–17 through FY 2021–22; each contains 12 monthly periods. The M14 indicator must be verified in every downloaded file before the series is accepted.

## Download the six Dindigul monthly HMIS extracts
Download the CSV versions of:
- FY 2016–17: https://dataful.in/datasets/11769/
- FY 2017–18: https://dataful.in/datasets/11770/
- FY 2018–19: https://dataful.in/datasets/11771/
- FY 2019–20: https://dataful.in/datasets/11772/
- FY 2020–21: https://dataful.in/datasets/11773/
- FY 2021–22: https://dataful.in/datasets/11774/

Then run (replace local paths with your downloaded CSV paths):
```bash
PYTHONPATH=. python scripts/ingest_hmis_ipd.py \
  --input path/to/hmis_2016_17.csv --source-name "Dindigul HMIS FY2016-17" --source-url https://dataful.in/datasets/11769/ \
  --input path/to/hmis_2017_18.csv --source-name "Dindigul HMIS FY2017-18" --source-url https://dataful.in/datasets/11770/ \
  --input path/to/hmis_2018_19.csv --source-name "Dindigul HMIS FY2018-19" --source-url https://dataful.in/datasets/11771/ \
  --input path/to/hmis_2019_20.csv --source-name "Dindigul HMIS FY2019-20" --source-url https://dataful.in/datasets/11772/ \
  --input path/to/hmis_2020_21.csv --source-name "Dindigul HMIS FY2020-21" --source-url https://dataful.in/datasets/11773/ \
  --input path/to/hmis_2021_22.csv --source-name "Dindigul HMIS FY2021-22" --source-url https://dataful.in/datasets/11774/ \
  --state "Tamil Nadu" --district "Dindigul"
```
The script requires the exact M14 indicator, Total category and combined facility aggregate. It will fail rather than infer admissions if a file is missing the indicator or has overlapping totals. It also verifies that monthly dates are unique. A complete six-year series would provide 72 months; the actual number depends on source completeness.

Add `--push-supabase` only in a trusted environment with `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` set. The script records each source separately and upserts the district-month admission facts.

## Modelling
`healthtrend.models.compare_six_models` implements Decision Tree, Random Forest, XGBoost, ARIMA, SARIMA and Prophet where installed. All models use a shared chronological holdout and rolling one-step-ahead evaluation. It requires 36 contiguous monthly observations. The loaded national malaria series currently has 22 months, so malaria model scoring is intentionally blocked. The Dindigul HMIS admissions series has not yet been ingested.

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
