-- Least-privilege grants for the HealthTrend AI browser roles.
-- RLS remains the row-level control; SQL grants are an additional table-level boundary.
revoke all privileges on all tables in schema public from anon, authenticated;
revoke all privileges on all sequences in schema public from anon, authenticated;
revoke all privileges on all functions in schema public from anon, authenticated;

grant select on
  public.dataset_sources,
  public.dim_date,
  public.dim_location,
  public.dim_disease,
  public.fact_disease_cases,
  public.fact_hospital_admissions,
  public.model_runs,
  public.forecast_results,
  public.mining_results
to authenticated;

grant select, update on public.profiles to authenticated;
grant select, update on public.app_user_roles to authenticated;

-- Server-side ETL uses the service role; it is never used by the browser.
grant all privileges on all tables in schema public to service_role;
grant all privileges on all sequences in schema public to service_role;
grant execute on all functions in schema public to service_role;

-- Keep future objects created by the migration owner least-privileged too.
alter default privileges for role postgres in schema public
  revoke all on tables from anon, authenticated;
alter default privileges for role postgres in schema public
  grant select on tables to authenticated;
alter default privileges for role postgres in schema public
  grant all on tables to service_role;
alter default privileges for role postgres in schema public
  revoke all on sequences from anon, authenticated;
alter default privileges for role postgres in schema public
  grant all on sequences to service_role;
alter default privileges for role postgres in schema public
  revoke execute on functions from anon, authenticated;
alter default privileges for role postgres in schema public
  grant execute on functions to service_role;
