# Dataset validation and provenance

## 1. NCVBDC Monthly Malaria Situation Information System (MMIS) — initial time series
- Publisher: National Centre for Vector Borne Diseases Control (NCVBDC), Directorate General of Health Services, Ministry of Health & Family Welfare, Government of India.
- Frequency: monthly summary reports.
- Geography: India national total.
- Observation: monthly malaria Total Positive Cases (TPC) / Positive cases; not hospital admissions.
- December 2024 report: exact TPC Current Year values for January–December 2024.
- October 2025 report: exact Positive Current Year values for January–October 2025. This is the latest report used to refresh 2025 values and supersedes the earlier April 2025 snapshot for overlapping months.
- Sources: https://www.ncvbdc.mohfw.gov.in/Doc/MMIS/2024/MMIS-Report-Country-Dec-2024.pdf ; https://ncvbdc.mohfw.gov.in/Doc/MMIS/2025/MMIS-Report-India-Oct-2025.pdf
- The current committed series has 22 continuous monthly observations from Jan 2024 to Oct 2025. It is national, not district-level.

## 2. HMIS — service-delivery and hospital-utilization candidates
- Publisher: Health Management Information System, Ministry of Health & Family Welfare.
- Official portal: https://hmis.mohfw.gov.in/#/
- The public State and Month-wise Medical Services Statistics FY 2021–22 catalogue describes 508,009 rows, 9 columns, 38 states/UTs, monthly reporting, and multiple medical-service indicators. It is only one fiscal year in that extract: https://dataful.in/datasets/6220/
- A separate HMIS collection describes monthly state/district indicator coverage for 2008–09 to 2021–22: https://dataful.in/collections/482/
- Candidate HMIS indicators must be inspected by exact name and definition before being mapped to admissions. IPD attendance, inpatient census, deliveries, and actual admissions are not interchangeable. No admission values have been loaded yet.

## 3. IDSP weekly outbreak reports
The Integrated Disease Surveillance Programme is a potential source for disease outbreak cases by state/district and week. Weekly data should not be silently converted to monthly without a documented aggregation rule. Portal: https://idsp.mohfw.gov.in/

## Data quality rules
Preserve report URL and report period for every observation; keep missing distinct from zero; reject duplicates/negative counts; keep geography and measure definitions consistent; record ETL runs; do not interpolate missing months for model evaluation.
