-- Supabase schema for SmartBudget

-- 1. PROFILES
create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text,
  username text unique,
  full_name text,
  avatar_url text,
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone default now()
);

alter table public.profiles enable row level security;

drop policy if exists "Profiles are viewable by owner" on public.profiles;
create policy "Profiles are viewable by owner" on public.profiles for select using ( auth.uid() = id );

drop policy if exists "Profiles are editable by owner" on public.profiles;
create policy "Profiles are editable by owner" on public.profiles for update using ( auth.uid() = id );

drop policy if exists "Insert profile for self" on public.profiles;
create policy "Insert profile for self" on public.profiles for insert with check ( auth.uid() = id );

-- Trigger for new user profile
create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, email)
  values (new.id, new.email)
  on conflict (id) do update set email = excluded.email, updated_at = now();
  return new;
end;
$$ language plpgsql security definer;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- 2. BANK ACCOUNTS
create table if not exists public.bank_accounts (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references auth.users(id) on delete cascade not null,
  account_name text not null,
  bank_name text not null,
  account_type text not null, -- 'cash', 'checking', 'savings', 'credit'
  is_active boolean default true,
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone default now()
);

alter table public.bank_accounts enable row level security;

create policy "Users can view their own bank accounts"
  on public.bank_accounts for select
  using ( auth.uid() = user_id );

create policy "Users can insert their own bank accounts"
  on public.bank_accounts for insert
  with check ( auth.uid() = user_id );

create policy "Users can update their own bank accounts"
  on public.bank_accounts for update
  using ( auth.uid() = user_id );

-- 3. TRANSACTIONS
create table if not exists public.transactions (
  id uuid default gen_random_uuid() primary key,
  bank_account_id uuid references public.bank_accounts(id) on delete cascade not null,
  amount numeric not null,
  description text,
  category_primary text,
  date timestamp with time zone default now(),
  is_manual boolean default false,
  is_pending boolean default false,
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone default now()
);

alter table public.transactions enable row level security;

create policy "Users can view their own transactions"
  on public.transactions for select
  using (
    exists (
      select 1 from public.bank_accounts
      where bank_accounts.id = transactions.bank_account_id
      and bank_accounts.user_id = auth.uid()
    )
  );

create policy "Users can insert their own transactions"
  on public.transactions for insert
  with check (
    exists (
      select 1 from public.bank_accounts
      where bank_accounts.id = bank_account_id
      and bank_accounts.user_id = auth.uid()
    )
  );

create policy "Users can update their own transactions"
  on public.transactions for update
  using (
    exists (
      select 1 from public.bank_accounts
      where bank_accounts.id = transactions.bank_account_id
      and bank_accounts.user_id = auth.uid()
    )
  );

