# Dataset validation, free alternatives and provenance

## 1. Loaded disease-trend dataset — NCVBDC MMIS

- Publisher: National Centre for Vector Borne Diseases Control (NCVBDC), Directorate General of Health Services, Ministry of Health & Family Welfare, Government of India.
- Official MMIS index: https://ncvbdc.mohfw.gov.in/index1.php?font=Normal&level=1&lid=3957&sublinkid=5879&theme=Green
- Measure: national monthly malaria positive cases (the 2024 report labels the series TPC; the 2025 report labels it Positive).
- Exact observations committed and loaded: 31 months — January–September 2023, January–December 2024, and January–October 2025.
- October–December 2023 are missing. No values are interpolated.
- Source reports:
  - October 2023 report: https://ncvbdc.mohfw.gov.in/Doc/MMIS/October-2023/MMISReport-Country-October-2023.pdf
  - December 2024 report: https://ncvbdc.mohfw.gov.in/Doc/MMIS/2024/MMIS-Report-Country-Dec-2024.pdf
  - October 2025 report: https://ncvbdc.mohfw.gov.in/Doc/MMIS/2025/MMIS-Report-India-Oct-2025.pdf
- The official index now lists a September 2026 national report. The chart descriptions available for that report are approximate chart-read values rather than an exact machine-readable monthly table. They are intentionally excluded from the warehouse and model training:
  https://ncvbdc.mohfw.gov.in/WriteReadData/l892s/47244184261793623044.pdf
- This is national malaria surveillance data, not hospital admissions, not district-level data, and not a live hospital feed.

## 2. Hospital-admissions data — free-source audit

### Official HMIS portal (authoritative source)
- Portal: https://hmis.mohfw.gov.in/#/
- MoSPI's 2024 compendium describes HMIS as monthly administrative data beginning in FY 2008–09, with an approximately one-month dissemination lag. The published formats listed are the portal and PDF reports; a public direct CSV API for the required series was not established.
- Reference: https://mospi.gov.in/sites/default/files/publication_reports/Compendium_of_Datasets_and_Registries_in_India_2024_0.pdf
- The HMIS M14 Patient Services module defines monthly inpatient admissions. The user guide describes an admission as a planned 24-hour or overnight stay and records total patients admitted in the reporting month.
- Indicator reference: https://www.mohfw.gov.in/sites/default/files/7216231442HMISUserGuidelines.pdf

### Free Dataful monthly export — not an admissions dataset
- Dataset: Tamil Nadu month-wise HMIS indicators, FY 2008–09 to 2021–22.
- URL: https://dataful.in/datasets/16674/
- The page explicitly labels it Free and provides CSV/XLSX/Parquet with monthly granularity.
- Its described scope is Family Planning, Maternal Health and Immunization. It is not a verified M14 inpatient-admissions series and is not used as one.

### Dindigul HMIS monthly catalogue — not confirmed free
- URL: https://dataful.in/datasets/15964/
- The page describes 132,120 monthly records for FY 2008–09 to 2021–22, but does not clearly display a Free label and its stated scope is Family Planning, Maternal Health and Immunization.
- Do not purchase or use it as M14 without explicit permission and an audit of the actual downloaded CSV.

### The Dangs M14 sample — short period and not confirmed free
- URL: https://dataful.in/datasets/8141/
- Its preview explicitly shows the indicator “Total number of patients admitted (Inpatients) during the month (sum of items 14.10.1.a and 14.10.1.b)”.
- It covers FY 2014–15 only and the page does not establish free download. It is useful to verify indicator wording, not for long-range forecasting.

## 3. Decision

A free, publicly downloadable, long-span monthly Indian inpatient-admissions CSV with a verified M14 total series has not been confirmed in the audited sources. The Supabase hospital-admissions fact table therefore remains empty. This is deliberate research integrity, not a failed database connection.

If the official HMIS portal provides monthly PDF exports for the chosen geography and period, they can be processed after layout and exact indicator validation. If you already have an HMIS M14 CSV, place it in `data/raw/hmis/` and use the project's parser; the ETL requires the exact indicator, TOTAL category and combined facility aggregate, preserves source notes, rejects duplicates/negative values and never interpolates gaps.

## 4. Data-quality rules

- Preserve source URL, publisher, report period, geography, indicator text and extraction timestamp.
- Keep missing values distinct from zero.
- Reject duplicate month/location/indicator combinations unless an aggregation rule is documented.
- Do not add chart-read approximations to exact-value observations.
- Do not sum overlapping age groups or public/private/rural/urban subtotals when a combined total is available.
- Never interpolate missing months for model evaluation.
- Use aggregate public data only; do not ingest patient identifiers or clinical records into this public capstone.
