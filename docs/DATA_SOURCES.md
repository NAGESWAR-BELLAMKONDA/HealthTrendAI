# Dataset validation and provenance

## 1. NCVBDC Monthly Malaria Situation Information System (MMIS) — loaded disease series\n- October 2023 report: Jan–Sep 2023 exact TPC Current Year values (7,584; 6,269; 6,532; 9,714; 13,483; 17,272; 27,677; 30,001; 25,343). Source: https://ncvbdc.mohfw.gov.in/Doc/MMIS/October-2023/MMISReport-Country-October-2023.pdf
- Publisher: National Centre for Vector Borne Diseases Control (NCVBDC), Directorate General of Health Services, Ministry of Health & Family Welfare, Government of India.
- Frequency: monthly summary reports; geography: India national total.
- Measure: malaria Total Positive Cases (TPC) / Positive cases, not hospital admissions.
- December 2024 report: exact TPC Current Year values for January–December 2024.
- October 2025 report: exact Positive Current Year values for January–October 2025; this later report refreshes the overlapping 2025 months.
- Sources: https://ncvbdc.mohfw.gov.in/Doc/MMIS/2024/MMIS-Report-Country-Dec-2024.pdf ; https://ncvbdc.mohfw.gov.in/Doc/MMIS/2025/MMIS-Report-India-Oct-2025.pdf
- Loaded series: 31 continuous monthly observations, January 2023–October 2025. National, not district-level.

## 2. HMIS — monthly inpatient admissions candidate
- Publisher: Health Management Information System, Ministry of Health & Family Welfare, Government of India.
- Official portal: https://hmis.mohfw.gov.in/#/
- Recommended candidate: Dindigul district, Tamil Nadu, monthly HMIS data from FY 2008–09 through FY 2021–22: https://dataful.in/datasets/15964/
- Catalogue metadata: 132,120 rows, 13 columns, monthly/district granularity, 601 distinct indicator values. The exact M14 admissions indicator must be confirmed in the CSV before any values are accepted.
- Exact M14 wording confirmed in a separate HMIS monthly district/sub-district extract for The Dangs, Gujarat, FY 2014–15: **“Total number of patients admitted (Inpatients) during the month (sum of items 14.10.1.a and 14.10.1.b)”**. That source is only one fiscal year and is used to verify the indicator definition, not as the primary long-series target: https://dataful.in/datasets/8141/
- The ingestion parser requires the exact M14 indicator, category TOTAL and combined facility aggregate. It sums sub-district rows only after selecting the combined facility aggregate and preserves source notes such as provisional reporting. It refuses missing indicators, ambiguous totals, duplicate months and negative counts.
- If the long-span Dindigul CSV contains a complete M14 series, it can provide up to 168 monthly observations. No hospital-admission values have been loaded into Supabase yet.
- Alternative if the long-span file does not contain M14: six consecutive Dindigul fiscal-year datasets FY 2016–17 to 2021–22 (datasets 11769–11774). Exact M14 coverage must be verified in each CSV.

## 3. National HMIS state/month alternatives
National state/month HMIS medical-services extracts are catalogued for FY 2019–20, 2020–21 and 2021–22: https://dataful.in/datasets/6222/ ; https://dataful.in/datasets/6221/ ; https://dataful.in/datasets/6220/. The 2021–22 extract has 508,009 rows, 9 columns, 38 state/UT values, monthly frequency and an All India row. The exact M14 admissions indicator must be checked in each CSV before using them as a national series.

## 4. Annual IPD data (cross-check only)
The HMIS catalogue also has annual IPD statistics for 2007–08 to 2019–20: https://dataful.in/datasets/6166/. This is annual and cannot be silently converted to monthly observations.

## 5. HMIS stock data is not admissions
A Tamil Nadu district-month stock dataset exists for 2008–09 to 2021–22, but it covers family-planning, maternal-health and immunization stock received/distributed/unusable counts, not patient admissions: https://dataful.in/datasets/17420/. It is not used as a hospital-admissions target.

## Data quality rules
Preserve source URL, fiscal year, district/sub-district and indicator definition for every observation; keep missing distinct from zero; reject duplicates/negative counts; select Total rather than summing overlapping age groups; select a combined facility aggregate rather than summing public/private and rural/urban variants; do not interpolate missing months for model evaluation.
