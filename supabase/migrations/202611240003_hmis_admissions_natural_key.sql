-- Null-safe idempotency for aggregate hospital-admission facts (disease_id is optional).
alter table public.fact_hospital_admissions
drop constraint if exists fact_hospital_admissions_natural_key;
alter table public.fact_hospital_admissions
add constraint fact_hospital_admissions_natural_key
unique nulls not distinct (date_key,location_id,disease_id,source_id,source_record_id);
