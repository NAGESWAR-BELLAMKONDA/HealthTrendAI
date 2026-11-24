-- Keep ETL logs server-only while documenting the service-role policy explicitly.
drop policy if exists "Service role manages ETL logs" on public.etl_logs;
create policy "Service role manages ETL logs" on public.etl_logs
for all to service_role using (true) with check (true);

-- Notify the dashboard when aggregate inpatient observations are ingested.
do $$
begin
  if exists (select 1 from pg_publication where pubname='supabase_realtime') then
    if not exists (select 1 from pg_publication_tables where pubname='supabase_realtime' and schemaname='public' and tablename='fact_hospital_admissions') then
      alter publication supabase_realtime add table public.fact_hospital_admissions;
    end if;
  end if;
end $$;
