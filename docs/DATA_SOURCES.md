# Dataset validation, free alternatives and provenance

## 1. Loaded disease-trend dataset — NCVBDC MMIS

- Publisher: National Centre for Vector Borne Diseases Control (NCVBDC), Directorate General of Health Services, Ministry of Health & Family Welfare, Government of India.
- Source index: https://ncvbdc.mohfw.gov.in/index1.php?font=Normal&level=1&lid=3957&sublinkid=5879&theme=Green
- Loaded measure: national monthly malaria positive cases (2024 report labels this TPC; 2025 report labels it Positive).
- Exact observations currently committed: 22 months, January 2024–October 2025.
- January–December 2024: December 2024 national MMIS PDF, exact TPC Current Year row.
- January–October 2025: October 2025 national MMIS PDF, exact Positive Current Year row.
- Report URLs:
  - https://ncvbdc.mohfw.gov.in/Doc/MMIS/2024/MMIS-Report-Country-Dec-2024.pdf
  - https://ncvbdc.mohfw.gov.in/Doc/MMIS/2025/MMIS-Report-India-Oct-2025.pdf
- The September 2026 NCVBDC national report is now listed on the official MMIS page. Its extracted graph descriptions provide approximate chart-read values, not a machine-readable monthly table. These approximations are deliberately NOT inserted into the fact table or model training data.
- 2026 report: https://ncvbdc.mohfw.gov.in/WriteReadData/l892s/47244184261793623044.pdf
- The 22-point series is continuous, but shorter than the 36-month seasonal-model threshold. The model runner blocks benchmark scoring until the required length is reached.

## 2. Hospital-admissions data — what is genuinely free

### Official HMIS portal (best authoritative route)
- Portal: https://hmis.mohfw.gov.in/#/
- MoSPI's 2024 compendium describes HMIS as monthly administrative data, starting FY 2008–09, with a stated dissemination lag of about one month. It lists PDF and portal as dissemination formats, not an openly documented direct CSV API.
- Reference: https://mospi.gov.in/sites/default/files/publication_reports/Compendium_of_Datasets_and_Registries_in_India_2024_0.pdf
- The HMIS M14 Patient Services module includes inpatient indicators. Monthly reports can be used if the public portal exposes the needed indicator and geography for the chosen period.
- A PDF/report export can be processed by the project's ETL after its layout and exact indicator are validated. Do not infer zero from missing values.

### Free Dataful alternative — useful, but NOT admissions
- Dataset: Month-wise HMIS data for Tamil Nadu, FY 2008–09 to 2021–22.
- URL: https://dataful.in/datasets/16674/
- The page explicitly labels this dataset **Free** and provides CSV/XLSX/Parquet.
- It has 132,120 rows and monthly granularity, but its stated scope is Family Planning, Maternal Health and Immunization. It is not a verified inpatient-admissions series, so it is not used as hospital-admissions data.

### HMIS inpatient candidate — one fiscal year only
- Dataset: The Dangs, Gujarat, FY 2014–15.
- URL: https://dataful.in/datasets/8141/
- Its preview explicitly contains the M14 indicator “Total number of patients admitted (Inpatients) during the month (sum of items 14.10.1.a and 14.10.1.b)”.
- It is monthly, but covers only one fiscal year and cannot support a defensible seasonal forecast by itself. The page does not establish that this download is free, so it is not represented as a free alternative.

### HMIS annual IPD alternative — wrong frequency for monthly modelling
- State/year HMIS extracts include M14 Patient Services indicators across FY 2008–09 to 2021–22; example Telangana: https://dataful.in/datasets/5872/
- This is annual data, not monthly data, and the page does not clearly establish free download. It cannot be merged into a monthly series without inventing intra-year values.

### ICMR COVID-19 National Clinical Registry — raw data restricted
- https://nhrdr.icmr.org.in/datasets/icmr-covid-19-national-clinical-registry-dataset
- Describes 51,781 hospitalized COVID-19 patients collected across 42 hospitals during 2020–2024.
- The repository states raw data will not be shared; only query outcomes are available after login. It is not an open raw CSV suitable for unattended ETL.

## 3. Decision and next step for admissions
A free, publicly downloadable, long-span monthly Indian inpatient-admissions CSV with a verified M14 total series has **not** been confirmed in the sources audited here. The application therefore keeps the hospital-admissions fact table empty until a validated source is supplied or extracted from the official HMIS portal. This is intentional research integrity, not a pipeline error.

If a free official HMIS report export is available for multiple years, place the CSVs in `data/raw/hmis/` and run the HMIS parser. It requires the exact M14 indicator, the TOTAL category and the combined facility aggregate, retains source notes, rejects duplicates/negative counts, and does not interpolate gaps.

## 4. Data-quality rules
- Preserve source URL, publisher, report period, geography, indicator text and extraction timestamp.
- Keep missing values distinct from zero.
- Reject duplicate month/location/indicator combinations unless the aggregation rule is explicitly documented.
- Do not add chart-read approximations to exact-value observations.
- Do not sum overlapping age groups or public/private/rural/urban subtotals when a combined total is available.
- Never interpolate missing months for model evaluation.
- Use aggregate public data only; do not ingest patient identifiers or clinical records into this public capstone.
