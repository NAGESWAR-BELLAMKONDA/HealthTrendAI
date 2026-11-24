-- Authentication and application role schema for HealthTrend AI.
create table if not exists public.profiles (
  user_id uuid primary key references auth.users(id) on delete cascade,
  email text,
  display_name text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create table if not exists public.app_user_roles (
  user_id uuid primary key references auth.users(id) on delete cascade,
  role text not null default 'viewer' check (role in ('admin','data_analyst','researcher','viewer')),
  granted_by uuid references auth.users(id),
  created_at timestamptz not null default now()
);
create or replace function public.has_app_role(allowed_roles text[])
returns boolean language sql stable security definer set search_path=public
as $$ select exists(select 1 from public.app_user_roles r where r.user_id=auth.uid() and r.role=any(allowed_roles)); $$;
create or replace function public.handle_new_healthtrend_user()
returns trigger language plpgsql security definer set search_path=public
as $$
begin
  insert into public.profiles(user_id,email,display_name)
  values(new.id,new.email,coalesce(new.raw_user_meta_data->>'display_name',''))
  on conflict(user_id) do update set email=excluded.email;
  insert into public.app_user_roles(user_id,role) values(new.id,'viewer') on conflict(user_id) do nothing;
  return new;
end;
$$;
drop trigger if exists on_healthtrend_auth_user_created on auth.users;
create trigger on_healthtrend_auth_user_created after insert on auth.users
for each row execute procedure public.handle_new_healthtrend_user();
alter table public.profiles enable row level security;
alter table public.app_user_roles enable row level security;
drop policy if exists "Users read own profile" on public.profiles;
create policy "Users read own profile" on public.profiles for select to authenticated
using(user_id=auth.uid() or public.has_app_role(array['admin']));
drop policy if exists "Users update own profile" on public.profiles;
create policy "Users update own profile" on public.profiles for update to authenticated
using(user_id=auth.uid()) with check(user_id=auth.uid());
drop policy if exists "Users read own role" on public.app_user_roles;
create policy "Users read own role" on public.app_user_roles for select to authenticated
using(user_id=auth.uid() or public.has_app_role(array['admin']));
drop policy if exists "Admins manage roles" on public.app_user_roles;
create policy "Admins manage roles" on public.app_user_roles for all to authenticated
using(public.has_app_role(array['admin'])) with check(public.has_app_role(array['admin']));
grant select,update on public.profiles to authenticated;
grant select,insert,update,delete on public.app_user_roles to authenticated;
grant execute on function public.has_app_role(text[]) to authenticated;
drop policy if exists "Public read dataset sources" on public.dataset_sources;
drop policy if exists "Public read date dimension" on public.dim_date;
drop policy if exists "Public read location dimension" on public.dim_location;
drop policy if exists "Public read disease dimension" on public.dim_disease;
drop policy if exists "Public read disease cases" on public.fact_disease_cases;
drop policy if exists "Public read hospital admissions" on public.fact_hospital_admissions;
drop policy if exists "Public read model runs" on public.model_runs;
drop policy if exists "Public read forecasts" on public.forecast_results;
create policy "Authenticated read dataset sources" on public.dataset_sources for select to authenticated using(true);
create policy "Authenticated read date dimension" on public.dim_date for select to authenticated using(true);
create policy "Authenticated read location dimension" on public.dim_location for select to authenticated using(true);
create policy "Authenticated read disease dimension" on public.dim_disease for select to authenticated using(true);
create policy "Authenticated read disease cases" on public.fact_disease_cases for select to authenticated using(true);
create policy "Authenticated read hospital admissions" on public.fact_hospital_admissions for select to authenticated using(true);
create policy "Authenticated read model runs" on public.model_runs for select to authenticated using(true);
create policy "Authenticated read forecasts" on public.forecast_results for select to authenticated using(true);
revoke select on public.dataset_sources,public.dim_date,public.dim_location,public.dim_disease,public.fact_disease_cases,public.fact_hospital_admissions,public.model_runs,public.forecast_results from anon;
grant select on public.dataset_sources,public.dim_date,public.dim_location,public.dim_disease,public.fact_disease_cases,public.fact_hospital_admissions,public.model_runs,public.forecast_results to authenticated;
create table if not exists public.mining_results(
 id uuid primary key default gen_random_uuid(),
 analysis_type text not null,
 target_name text not null check(target_name in('disease_cases','hospital_admissions')),
 location_id uuid references public.dim_location(id),
 disease_id uuid references public.dim_disease(id),
 period_start date,
 period_end date,
 algorithm text not null,
 status text not null default 'completed' check(status in('completed','insufficient_data','failed')),
 result jsonb not null default '{}'::jsonb,
 sample_size integer not null default 0,
 created_at timestamptz not null default now()
);
alter table public.mining_results enable row level security;
drop policy if exists "Authenticated read mining results" on public.mining_results;
create policy "Authenticated read mining results" on public.mining_results for select to authenticated using(true);
grant select on public.mining_results to authenticated;
grant all on public.mining_results to service_role;
create index if not exists idx_roles_role on public.app_user_roles(role);
create index if not exists idx_mining_results_created on public.mining_results(created_at desc);
