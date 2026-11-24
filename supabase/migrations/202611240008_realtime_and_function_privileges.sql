revoke all on function public.handle_new_healthtrend_user() from public, anon, authenticated;
revoke all on function public.has_app_role(text[]) from public, anon;
grant execute on function public.has_app_role(text[]) to authenticated;
do $$
begin
  if not exists (
    select 1 from pg_publication_tables
    where pubname='supabase_realtime' and schemaname='public' and tablename='forecast_results'
  ) then
    alter publication supabase_realtime add table public.forecast_results;
  end if;
  if not exists (
    select 1 from pg_publication_tables
    where pubname='supabase_realtime' and schemaname='public' and tablename='mining_results'
  ) then
    alter publication supabase_realtime add table public.mining_results;
  end if;
end $$;
