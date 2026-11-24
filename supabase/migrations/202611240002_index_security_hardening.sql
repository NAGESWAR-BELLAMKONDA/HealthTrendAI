-- Performance indexes and least-privilege hardening for inherited helper function.
create index if not exists idx_etl_logs_source_id on public.etl_logs(source_id);
create index if not exists idx_cases_location_id on public.fact_disease_cases(location_id);
create index if not exists idx_cases_source_id on public.fact_disease_cases(source_id);
create index if not exists idx_admissions_disease_id on public.fact_hospital_admissions(disease_id);
create index if not exists idx_admissions_location_id on public.fact_hospital_admissions(location_id);
create index if not exists idx_admissions_source_id on public.fact_hospital_admissions(source_id);
create index if not exists idx_model_runs_disease_id on public.model_runs(disease_id);
create index if not exists idx_model_runs_location_id on public.model_runs(location_id);
revoke all on function public.rls_auto_enable() from public, anon, authenticated;