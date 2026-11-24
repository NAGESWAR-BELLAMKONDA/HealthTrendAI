-- Notify the dashboard when a modelling run is persisted.
do $$
begin
  if exists (select 1 from pg_publication where pubname='supabase_realtime') then
    if not exists (select 1 from pg_publication_tables where pubname='supabase_realtime' and schemaname='public' and tablename='model_runs') then
      alter publication supabase_realtime add table public.model_runs;
    end if;
  end if;
end $$;
