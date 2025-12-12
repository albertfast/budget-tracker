// Plaid Transaction Service
import { supabase } from './supabaseClient';

const API_BASE_URL = 'http://10.180.211.211:8001';

export interface PlaidTransaction {
  transaction_id: string;
  amount: number;
  name: string;
  merchant_name?: string;
  category?: string[];
  date: string;
  pending: boolean;
  account_id: string;
}

export interface SpendingAnalysis {
  total_spending: number;
  category_breakdown: Record<string, number>;
  top_categories: [string, number][];
  recommendations: {
    type: string;
    category: string;
    message: string;
    potential_savings?: number;
  }[];
  analysis_period: string;
}

export interface InvestmentAdvice {
  disposable_income: number;
  recommended_monthly_investment: number;
  risk_profile: string;
  allocation: Record<string, number>;
  recommendations: {
    type: string;
    category: string;
    message: string;
    monthly_amount?: number;
    percentage?: number;
  }[];
  projected_annual_savings: number;
}

/**
 * Fetch transactions from Plaid for a given access token
 */
export async function syncPlaidTransactions(accessToken: string): Promise<PlaidTransaction[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/plaid/sync_transactions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        access_token: accessToken,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to sync transactions: ${response.status}`);
    }

    const data = await response.json();
    return data.transactions || [];
  } catch (error) {
    console.error('[Plaid] Sync transactions error:', error);
    throw error;
  }
}

/**
 * Get AI-powered spending analysis
 */
export async function analyzeSpending(transactions: PlaidTransaction[]): Promise<SpendingAnalysis> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/ai/analyze_spending`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(transactions),
    });

    if (!response.ok) {
      throw new Error(`Failed to analyze spending: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('[AI] Spending analysis error:', error);
    throw error;
  }
}

/**
 * Get AI-powered investment recommendations
 */
export async function getInvestmentAdvice(params: {
  monthly_income: number;
  monthly_expenses: number;
  current_savings: number;
  risk_profile?: 'conservative' | 'moderate' | 'aggressive';
}): Promise<InvestmentAdvice> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/ai/investment_advice`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      throw new Error(`Failed to get investment advice: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('[AI] Investment advice error:', error);
    throw error;
  }
}

/**
 * Save Plaid transactions to Supabase
 */
export async function savePlaidTransactionsToSupabase(
  userId: string,
  bankAccountId: string,
  transactions: PlaidTransaction[]
): Promise<void> {
  try {
    const records = transactions.map((tx) => ({
      user_id: userId,
      bank_account_id: bankAccountId,
      amount: Math.abs(tx.amount), // Store as positive
      memo: tx.name || tx.merchant_name || 'Unknown',
      category: tx.category?.[0] || 'Other',
      occurred_on: `${tx.date}T12:00:00Z`,
      source: 'plaid',
      currency: 'USD',
      plaid_transaction_id: tx.transaction_id,
      is_pending: tx.pending,
    }));

    // Insert with conflict handling (upsert based on plaid_transaction_id)
    const { error } = await supabase
      .from('financial_records')
      .upsert(records, {
        onConflict: 'plaid_transaction_id',
        ignoreDuplicates: false,
      });

    if (error) throw error;

    console.log(`[Plaid] Saved ${transactions.length} transactions to Supabase`);
  } catch (error) {
    console.error('[Plaid] Error saving transactions to Supabase:', error);
    throw error;
  }
}

export default {
  syncPlaidTransactions,
  analyzeSpending,
  getInvestmentAdvice,
  savePlaidTransactionsToSupabase,
};
