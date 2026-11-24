-- Final RBAC query-plan and foreign-key index hardening.
create index if not exists idx_app_user_roles_granted_by on public.app_user_roles(granted_by);
create index if not exists idx_mining_results_disease_id on public.mining_results(disease_id);
create index if not exists idx_mining_results_location_id on public.mining_results(location_id);

drop policy if exists "Users read own profile" on public.profiles;
create policy "Users read own profile" on public.profiles
for select to authenticated
using(user_id=(select auth.uid()) or private.has_app_role(array['admin']));

drop policy if exists "Users update own profile" on public.profiles;
create policy "Users update own profile" on public.profiles
for update to authenticated
using(user_id=(select auth.uid()))
with check(user_id=(select auth.uid()));

drop policy if exists "Users read own role" on public.app_user_roles;
create policy "Users read own role" on public.app_user_roles
for select to authenticated
using(user_id=(select auth.uid()) or private.has_app_role(array['admin']));

drop policy if exists "Admins manage roles" on public.app_user_roles;
drop policy if exists "Admins update roles" on public.app_user_roles;
create policy "Admins update roles" on public.app_user_roles
for update to authenticated
using(private.has_app_role(array['admin']))
with check(private.has_app_role(array['admin']));
drop policy if exists "Admins insert roles" on public.app_user_roles;
create policy "Admins insert roles" on public.app_user_roles
for insert to authenticated
with check(private.has_app_role(array['admin']));
drop policy if exists "Admins delete roles" on public.app_user_roles;
create policy "Admins delete roles" on public.app_user_roles
for delete to authenticated
using(private.has_app_role(array['admin']));
