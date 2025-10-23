-- Supabase schema for SmartBudget
-- 1) profiles table to extend auth.users
create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text,
  username text unique,
  full_name text,
  avatar_url text,
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone default now()
);

-- Enable RLS
alter table public.profiles enable row level security;

-- Policies: users can select/update/insert their own row
drop policy if exists "Profiles are viewable by owner" on public.profiles;
create policy "Profiles are viewable by owner"
  on public.profiles for select
  using ( auth.uid() = id );

drop policy if exists "Profiles are editable by owner" on public.profiles;
create policy "Profiles are editable by owner"
  on public.profiles for update
  using ( auth.uid() = id );

drop policy if exists "Insert profile for self" on public.profiles;
create policy "Insert profile for self"
  on public.profiles for insert
  with check ( auth.uid() = id );

-- Trigger to create profile on signup
create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, email)
  values (new.id, new.email)
  on conflict (id) do update set email = excluded.email, updated_at = now();
  return new;
end;
$$ language plpgsql security definer;

-- Ensure single trigger instance
drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();
