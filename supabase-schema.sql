-- Enhanced Supabase schema for SmartBudget with Budget Tracking and Insights

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
  plaid_access_token text,
  plaid_item_id text,
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
  category_detailed text,
  date timestamp with time zone default now(),
  is_manual boolean default false,
  is_pending boolean default false,
  plaid_transaction_id text,
  location jsonb,
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

-- 4. BUDGETS
create table if not exists public.budgets (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references auth.users(id) on delete cascade not null,
  name text not null,
  category text,
  amount numeric not null,
  period_type text not null, -- 'monthly', 'weekly', 'yearly'
  start_date date not null,
  end_date date,
  is_active boolean default true,
  alert_threshold numeric default 0.8, -- Alert when 80% spent
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone default now()
);

alter table public.budgets enable row level security;

create policy "Users can view their own budgets"
  on public.budgets for select
  using ( auth.uid() = user_id );

create policy "Users can insert their own budgets"
  on public.budgets for insert
  with check ( auth.uid() = user_id );

create policy "Users can update their own budgets"
  on public.budgets for update
  using ( auth.uid() = user_id );

-- 5. BUDGET ALERTS
create table if not exists public.budget_alerts (
  id uuid default gen_random_uuid() primary key,
  budget_id uuid references public.budgets(id) on delete cascade not null,
  user_id uuid references auth.users(id) on delete cascade not null,
  alert_type text not null, -- 'threshold_reached', 'budget_exceeded', 'budget_completed'
  message text not null,
  is_read boolean default false,
  created_at timestamp with time zone default now()
);

alter table public.budget_alerts enable row level security;

create policy "Users can view their own budget alerts"
  on public.budget_alerts for select
  using ( auth.uid() = user_id );

create policy "Users can update their own budget alerts"
  on public.budget_alerts for update
  using ( auth.uid() = user_id );

-- 6. INSIGHTS
create table if not exists public.insights (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references auth.users(id) on delete cascade not null,
  insight_type text not null, -- 'spending_pattern', 'budget_recommendation', 'savings_opportunity'
  title text not null,
  description text not null,
  data jsonb,
  is_read boolean default false,
  created_at timestamp with time zone default now()
);

alter table public.insights enable row level security;

create policy "Users can view their own insights"
  on public.insights for select
  using ( auth.uid() = user_id );

create policy "Users can update their own insights"
  on public.insights for update
  using ( auth.uid() = user_id );

-- 7. SPENDING CATEGORIES
create table if not exists public.spending_categories (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references auth.users(id) on delete cascade not null,
  name text not null,
  color text default '#008080',
  icon text default 'wallet',
  is_custom boolean default false,
  created_at timestamp with time zone default now()
);

alter table public.spending_categories enable row level security;

create policy "Users can view their own spending categories"
  on public.spending_categories for select
  using ( auth.uid() = user_id );

create policy "Users can insert their own spending categories"
  on public.spending_categories for insert
  with check ( auth.uid() = user_id );

-- Insert default spending categories
insert into public.spending_categories (user_id, name, icon) 
select 
  auth.uid(),
  unnest(ARRAY['Food & Dining', 'Transportation', 'Shopping', 'Entertainment', 'Bills & Utilities', 'Healthcare', 'Education', 'Travel', 'Other']),
  unnest(ARRAY['restaurant', 'car', 'bag', 'game-controller', 'document-text', 'heart', 'book', 'airplane', 'ellipsis-horizontal'])
where auth.uid() is not null
on conflict do nothing;

-- 8. MONTHLY SUMMARIES
create table if not exists public.monthly_summaries (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references auth.users(id) on delete cascade not null,
  month date not null, -- First day of the month
  total_income numeric default 0,
  total_expenses numeric default 0,
  net_savings numeric default 0,
  top_spending_category text,
  transaction_count integer default 0,
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone default now(),
  unique(user_id, month)
);

alter table public.monthly_summaries enable row level security;

create policy "Users can view their own monthly summaries"
  on public.monthly_summaries for select
  using ( auth.uid() = user_id );

create policy "Users can insert their own monthly summaries"
  on public.monthly_summaries for insert
  with check ( auth.uid() = user_id );

create policy "Users can update their own monthly summaries"
  on public.monthly_summaries for update
  using ( auth.uid() = user_id );

-- Indexes for better performance
create index if not exists idx_transactions_user_date on public.transactions(bank_account_id, date);
create index if not exists idx_bank_accounts_user on public.bank_accounts(user_id);
create index if not exists idx_budgets_user_active on public.budgets(user_id, is_active);
create index if not exists idx_insights_user_unread on public.insights(user_id, is_read);
create index if not exists idx_monthly_summaries_user_month on public.monthly_summaries(user_id, month);

-- Function to update monthly summaries
create or replace function public.update_monthly_summary()
returns trigger as $$
begin
  insert into public.monthly_summaries (user_id, month, total_income, total_expenses, net_savings, transaction_count)
  select 
    ba.user_id,
    date_trunc('month', new.date)::date,
    coalesce(sum(case when t.amount > 0 then t.amount else 0 end), 0),
    coalesce(sum(case when t.amount < 0 then abs(t.amount) else 0 end), 0),
    coalesce(sum(t.amount), 0),
    count(*)
  from public.transactions t
  join public.bank_accounts ba on t.bank_account_id = ba.id
  where date_trunc('month', t.date) = date_trunc('month', new.date)
  and ba.user_id = (select user_id from public.bank_accounts where id = new.bank_account_id)
  group by ba.user_id, date_trunc('month', new.date)
  on conflict (user_id, month) do update set
    total_income = excluded.total_income,
    total_expenses = excluded.total_expenses,
    net_savings = excluded.net_savings,
    transaction_count = excluded.transaction_count,
    updated_at = now();
  
  return new;
end;
$$ language plpgsql security definer;

-- Trigger to update monthly summaries on transaction insert/update
drop trigger if exists update_monthly_summary_trigger on public.transactions;
create trigger update_monthly_summary_trigger
  after insert or update on public.transactions
  for each row execute function public.update_monthly_summary();