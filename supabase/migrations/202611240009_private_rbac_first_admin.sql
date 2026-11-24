create schema if not exists private;
revoke all on schema private from public, anon;
grant usage on schema private to authenticated, service_role;

create or replace function private.has_app_role(allowed_roles text[])
returns boolean
language sql
stable
security definer
set search_path = public, pg_temp
as $$
  select exists (
    select 1 from public.app_user_roles r
    where r.user_id = auth.uid() and r.role = any(allowed_roles)
  );
$$;
revoke all on function private.has_app_role(text[]) from public, anon;
grant execute on function private.has_app_role(text[]) to authenticated;

drop policy if exists "Users read own profile" on public.profiles;
create policy "Users read own profile" on public.profiles
for select to authenticated
using(user_id=auth.uid() or private.has_app_role(array['admin']));

drop policy if exists "Users read own role" on public.app_user_roles;
create policy "Users read own role" on public.app_user_roles
for select to authenticated
using(user_id=auth.uid() or private.has_app_role(array['admin']));

drop policy if exists "Admins manage roles" on public.app_user_roles;
create policy "Admins manage roles" on public.app_user_roles
for all to authenticated
using(private.has_app_role(array['admin']))
with check(private.has_app_role(array['admin']));

-- First registered account becomes the initial administrator. The transaction
-- advisory lock prevents two simultaneous signups from both becoming admins.
create or replace function public.handle_new_healthtrend_user()
returns trigger
language plpgsql
security definer
set search_path = public, pg_temp
as $$
declare initial_role text;
begin
  perform pg_advisory_xact_lock(hashtext('healthtrend-first-admin'));
  insert into public.profiles(user_id,email,display_name)
  values(new.id,new.email,coalesce(new.raw_user_meta_data->>'display_name',''))
  on conflict(user_id) do update set email=excluded.email;
  if exists(select 1 from public.app_user_roles where role='admin') then
    initial_role := 'viewer';
  else
    initial_role := 'admin';
  end if;
  insert into public.app_user_roles(user_id,role)
  values(new.id,initial_role)
  on conflict(user_id) do nothing;
  return new;
end;
$$;
revoke all on function public.handle_new_healthtrend_user() from public, anon, authenticated;

-- Realtime updates for analysis and forecast views.
do $$
declare t text;
begin
  foreach t in array array['forecast_results','mining_results'] loop
    if not exists (
      select 1 from pg_publication_tables
      where pubname='supabase_realtime' and schemaname='public' and tablename=t
    ) then
      execute format('alter publication supabase_realtime add table public.%I',t);
    end if;
  end loop;
end $$;
