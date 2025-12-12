// Backend Types for SmartBudget Mobile App

export interface User {
  id: string;
  email: string;
  username?: string;
  full_name?: string;
  avatar_url?: string;
  created_at: string;
  updated_at: string;
}

export interface BankAccount {
  id: string;
  user_id: string;
  account_name: string;
  bank_name: string;
  account_type: 'cash' | 'checking' | 'savings' | 'credit';
  is_active: boolean;
  plaid_access_token?: string;
  plaid_item_id?: string;
  created_at: string;
  updated_at: string;
}

export interface Transaction {
  id: string;
  bank_account_id: string;
  amount: number;
  description?: string;
  category_primary?: string;
  category_detailed?: string;
  date: string;
  is_manual: boolean;
  is_pending: boolean;
  plaid_transaction_id?: string;
  location?: {
    address?: string;
    city?: string;
    state?: string;
    zip?: string;
  };
  created_at: string;
  updated_at: string;
}

export interface Budget {
  id: string;
  user_id: string;
  name: string;
  category?: string;
  amount: number;
  period_type: 'monthly' | 'weekly' | 'yearly';
  start_date: string;
  end_date?: string;
  is_active: boolean;
  alert_threshold: number;
  created_at: string;
  updated_at: string;
}

export interface BudgetAlert {
  id: string;
  budget_id: string;
  user_id: string;
  alert_type: 'threshold_reached' | 'budget_exceeded' | 'budget_completed';
  message: string;
  is_read: boolean;
  created_at: string;
}

export interface Insight {
  id: string;
  user_id: string;
  insight_type: 'spending_pattern' | 'budget_recommendation' | 'savings_opportunity';
  title: string;
  description: string;
  data?: any;
  is_read: boolean;
  created_at: string;
}

export interface SpendingCategory {
  id: string;
  user_id: string;
  name: string;
  color: string;
  icon: string;
  is_custom: boolean;
  created_at: string;
}

export interface MonthlySummary {
  id: string;
  user_id: string;
  month: string;
  total_income: number;
  total_expenses: number;
  net_savings: number;
  top_spending_category?: string;
  transaction_count: number;
  created_at: string;
  updated_at: string;
}

// Plaid related types
export interface PlaidLinkToken {
  link_token: string;
  expiration: string;
  request_id: string;
}

export interface PlaidPublicToken {
  public_token: string;
}

export interface PlaidAccessToken {
  access_token: string;
  item_id: string;
  request_id: string;
}

export interface PlaidAccount {
  id: string;
  name: string;
  type: string;
  subtype: string;
  mask: string;
}

export interface PlaidTransaction {
  transaction_id: string;
  account_id: string;
  amount: number;
  date: string;
  name: string;
  merchant_name?: string;
  category?: string[];
  pending: boolean;
  location?: {
    address?: string;
    city?: string;
    region?: string;
    postal_code?: string;
    country?: string;
  };
}

// API Response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// Budget Analysis Types
export interface BudgetAnalysis {
  budget_id: string;
  budget_name: string;
  spent: number;
  remaining: number;
  percentage_used: number;
  is_over_budget: boolean;
  days_remaining: number;
  daily_spending_rate: number;
}

export interface SpendingAnalysis {
  category: string;
  amount: number;
  percentage: number;
  transaction_count: number;
  trend: 'increasing' | 'decreasing' | 'stable';
}

export interface MonthlyTrend {
  month: string;
  income: number;
  expenses: number;
  savings: number;
}

// Notification Types
export interface PushNotification {
  title: string;
  body: string;
  data?: Record<string, any>;
  sound?: string;
}

// Financial Insights Types
export interface FinancialHealthScore {
  score: number;
  factors: {
    savings_rate: number;
    budget_adherence: number;
    spending_consistency: number;
    income_stability: number;
  };
  recommendations: string[];
}

export interface SpendingPattern {
  category: string;
  frequency: number;
  average_amount: number;
  time_of_day: string;
  day_of_week: string;
}