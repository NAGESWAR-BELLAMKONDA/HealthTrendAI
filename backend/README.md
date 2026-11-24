# HealthTrend AI — ETL and modelling

## Verified initial dataset
The repository contains 22 national monthly malaria-positive observations: Jan–Dec 2024 from the NCVBDC December 2024 report and Jan–Oct 2025 from the NCVBDC October 2025 report. See `../data/processed/india_malaria_monthly_tpc_2024_2025.csv` and the exact source URL on every row.

## Ingestion
`healthtrend.ingestion` normalizes month starts, rejects negative counts and duplicate months, and extracts the official TPC/Positive Current Year row from NCVBDC MMIS PDFs. `scripts/ingest_mmis.py` downloads the selected official reports and can upsert them into Supabase using server-side credentials.

## Modelling
`healthtrend.models.compare_six_models` implements Decision Tree, Random Forest, XGBoost, ARIMA, SARIMA and Prophet where installed. All models use a shared chronological holdout and rolling one-step-ahead evaluation. It requires 36 contiguous monthly observations; the verified series currently has 22. Model comparison is intentionally blocked until sufficient monthly history exists.

## Run tests
```bash
python -m pip install -r requirements-ci.txt
PYTHONPATH=. pytest -q
```

## Run ingestion
```bash
pip install -r requirements.txt
PYTHONPATH=. python scripts/ingest_mmis.py
```

Add `--push-supabase` only in a trusted environment with `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` set. Never commit the service-role key or place it in Vite/frontend code.

## Run modelling
```bash
PYTHONPATH=. python scripts/run_model_comparison.py --csv ../data/processed/india_malaria_monthly_tpc_2024_2025.csv
```

The current dataset will correctly return a data-readiness error rather than fabricated scores.

## Admissions limitation
HMIS catalogues provide monthly medical-service indicators and district-level historical collections, but exact admission indicator semantics and a downloadable file still need validation. No hospital-admission values are fabricated or inserted.
