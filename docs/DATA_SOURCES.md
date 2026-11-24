# Dataset validation and provenance

## 1. NCVBDC Monthly Malaria Situation Information System (MMIS) — loaded disease series
- Publisher: National Centre for Vector Borne Diseases Control (NCVBDC), Directorate General of Health Services, Ministry of Health & Family Welfare, Government of India.
- Frequency: monthly summary reports; geography: India national total.
- Measure: malaria Total Positive Cases (TPC) / Positive cases, not hospital admissions.
- December 2024 report: exact TPC Current Year values for January–December 2024.
- October 2025 report: exact Positive Current Year values for January–October 2025; this later report refreshes the overlapping 2025 months.
- Sources: https://ncvbdc.mohfw.gov.in/Doc/MMIS/2024/MMIS-Report-Country-Dec-2024.pdf ; https://ncvbdc.mohfw.gov.in/Doc/MMIS/2025/MMIS-Report-India-Oct-2025.pdf
- Loaded series: 22 continuous monthly observations, January 2024–October 2025. National, not district-level.

## 2. HMIS — monthly inpatient admissions candidate
- Publisher: Health Management Information System, Ministry of Health & Family Welfare, Government of India.
- Official portal: https://hmis.mohfw.gov.in/#/
- A monthly HMIS sub-district dataset for The Dangs district, Gujarat, FY 2014–15, explicitly contains the indicator **“Total number of patients admitted (Inpatients) during the month (sum of items 14.10.1.a and 14.10.1.b)”**: https://dataful.in/datasets/8141/
- For a longer Tamil Nadu district series, Dataful catalogues Dindigul monthly HMIS extracts for six consecutive fiscal years:
  - FY 2016–17: https://dataful.in/datasets/11769/
  - FY 2017–18: https://dataful.in/datasets/11770/
  - FY 2018–19: https://dataful.in/datasets/11771/
  - FY 2019–20: https://dataful.in/datasets/11772/
  - FY 2020–21: https://dataful.in/datasets/11773/
  - FY 2021–22: https://dataful.in/datasets/11774/
- Each dataset is monthly and has district/sub-district/indicator detail. The exact M14 indicator must be present in every downloaded file; this has not yet been confirmed for all six Dindigul extracts. The ingestion parser checks the exact indicator, selects category TOTAL and the combined facility aggregate, then sums sub-district values to district-month.
- If all six files contain complete M14 monthly observations, the combined series will contain up to 72 monthly Dindigul admissions observations. No admission values have been loaded into Supabase yet.

## 3. National HMIS state/month alternatives
National state/month HMIS medical-service extracts are also catalogued for FY 2019–20, 2020–21 and 2021–22: https://dataful.in/datasets/6222/ ; https://dataful.in/datasets/6221/ ; https://dataful.in/datasets/6220/. The 2021–22 extract has 508,009 rows, 9 columns, 38 state/UT values, monthly frequency and an All India row. The exact M14 admissions indicator must be checked in each CSV before using them as a national series.

## 4. Annual IPD data (cross-check only)
The HMIS catalogue also has annual IPD statistics for 2007–08 to 2019–20: https://dataful.in/datasets/6166/. This is annual and cannot be silently converted to monthly observations.

## 5. HMIS stock data is not admissions
A Tamil Nadu district-month stock dataset exists for 2008–09 to 2021–22, but it covers family-planning, maternal-health and immunization stock received/distributed/unusable counts, not patient admissions: https://dataful.in/datasets/17420/. It is not used as a hospital-admissions target.

## Data quality rules
Preserve source URL, fiscal year, district/sub-district and indicator definition for every observation; keep missing distinct from zero; reject duplicates/negative counts; select Total rather than summing overlapping age groups; select a combined facility aggregate rather than summing public/private and rural/urban variants; do not interpolate missing months for model evaluation.
