-- Preserve HMIS notes such as provisional reporting status on each aggregated observation.
alter table public.fact_hospital_admissions add column if not exists source_note text;
