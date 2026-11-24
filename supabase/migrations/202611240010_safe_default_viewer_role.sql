-- Keep self-service registration least-privileged. Provision the project owner
-- as administrator only after their verified email account exists.
create or replace function public.handle_new_healthtrend_user()
returns trigger
language plpgsql
security definer
set search_path = public, pg_temp
as $$
begin
  insert into public.profiles(user_id,email,display_name)
  values(new.id,new.email,coalesce(new.raw_user_meta_data->>'display_name',''))
  on conflict(user_id) do update set email=excluded.email;
  insert into public.app_user_roles(user_id,role)
  values(new.id,'viewer')
  on conflict(user_id) do nothing;
  return new;
end;
$$;
revoke all on function public.handle_new_healthtrend_user() from public, anon, authenticated;

-- All policies now use private.has_app_role; remove the earlier exposed helper.
drop function if exists public.has_app_role(text[]);
