-- Keep scheduled mining runs idempotent: one row per analysis definition and period.
-- NULL location/disease values are treated as equal so national/global analyses also deduplicate.
alter table public.mining_results
  add constraint mining_results_natural_key
  unique nulls not distinct (
    analysis_type,
    target_name,
    location_id,
    disease_id,
    period_start,
    period_end,
    algorithm
  );
