-- Deduplicate exact repeated monthly disease facts and enforce one source fact per month/location/disease.
-- The audit confirmed nine exact duplicate pairs for Jan-Sep 2023: same source, date,
-- count, unit and quality flag; only their source_record_id labels differed.
with ranked as (
  select id,
         row_number() over (
           partition by date_key, location_id, disease_id, source_id
           order by loaded_at asc, id asc
         ) as row_num
  from public.fact_disease_cases
)
delete from public.fact_disease_cases f
using ranked r
where f.id = r.id
  and r.row_num > 1;

alter table public.fact_disease_cases
  drop constraint if exists fact_disease_cases_natural_key;

alter table public.fact_disease_cases
  add constraint fact_disease_cases_natural_key
  unique nulls not distinct (date_key, location_id, disease_id, source_id);
