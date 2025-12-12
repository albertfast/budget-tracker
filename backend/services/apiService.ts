// Unified API Service for SmartBudget Mobile
import { 
  User, 
  BankAccount, 
  Transaction, 
  Budget, 
  Insight, 
  SpendingCategory, 
  MonthlySummary,
  BudgetAnalysis,
  SpendingAnalysis,
  FinancialHealthScore,
  ApiResponse 
} from '../types';
import SupabaseService from './supabaseService';
import PlaidService from './plaidService';
import ConfigService from './config';

class ApiService {
  private static instance: ApiService;
  private supabase = SupabaseService;
  private plaid = PlaidService;
  private config = ConfigService;

  private constructor() {}

  static getInstance(): ApiService {
    if (!ApiService.instance) {
      ApiService.instance = new ApiService();
    }
    return ApiService.instance;
  }

  // Authentication
  async signIn(email: string, password: string): Promise<ApiResponse<User>> {
    return this.supabase.signIn(email, password);
  }

  async signUp(email: string, password: string, fullName?: string): Promise<ApiResponse<User>> {
    return this.supabase.signUp(email, password, fullName);
  }

  async signOut(): Promise<ApiResponse<boolean>> {
    return this.supabase.signOut();
  }

  async getCurrentUser(): Promise<ApiResponse<User>> {
    return this.supabase.getCurrentUser();
  }

  // Bank Accounts
  async getBankAccounts(): Promise<ApiResponse<BankAccount[]>> {
    return this.supabase.getBankAccounts();
  }

  async createBankAccount(account: Omit<BankAccount, 'id' | 'created_at' | 'updated_at'>): Promise<ApiResponse<BankAccount>> {
    return this.supabase.createBankAccount(account);
  }

  async updateBankAccount(id: string, updates: Partial<BankAccount>): Promise<ApiResponse<BankAccount>> {
    return this.supabase.updateBankAccount(id, updates);
  }

  // Plaid Integration
  async createPlaidLinkToken(userId: string) {
    return this.plaid.createLinkToken(userId);
  }

  async exchangePlaidPublicToken(publicToken: string) {
    return this.plaid.exchangePublicToken(publicToken);
  }

  async syncPlaidTransactions(bankAccountId: string) {
    return this.plaid.syncTransactions(bankAccountId);
  }

  // Transactions
  async getTransactions(limit: number = 50, offset: number = 0): Promise<ApiResponse<Transaction[]>> {
    return this.supabase.getTransactions(limit, offset);
  }

  async createTransaction(transaction: Omit<Transaction, 'id' | 'created_at' | 'updated_at'>): Promise<ApiResponse<Transaction>> {
    return this.supabase.createTransaction(transaction);
  }

  async updateTransaction(id: string, updates: Partial<Transaction>): Promise<ApiResponse<Transaction>> {
    return this.supabase.updateTransaction(id, updates);
  }

  async deleteTransaction(id: string): Promise<ApiResponse<boolean>> {
    return this.supabase.deleteTransaction(id);
  }

  // Budgets
  async getBudgets(): Promise<ApiResponse<Budget[]>> {
    return this.supabase.getBudgets();
  }

  async createBudget(budget: Omit<Budget, 'id' | 'created_at' | 'updated_at'>): Promise<ApiResponse<Budget>> {
    return this.supabase.createBudget(budget);
  }

  // Analytics and Insights
  async getInsights(): Promise<ApiResponse<Insight[]>> {
    return this.supabase.getInsights();
  }

  async markInsightAsRead(id: string): Promise<ApiResponse<boolean>> {
    return this.supabase.markInsightAsRead(id);
  }

  async getMonthlySummary(month: string): Promise<ApiResponse<MonthlySummary>> {
    return this.supabase.getMonthlySummary(month);
  }

  async getSpendingCategories(): Promise<ApiResponse<SpendingCategory[]>> {
    return this.supabase.getSpendingCategories();
  }

  // Financial Analysis
  async getBudgetAnalysis(budgetId: string): Promise<ApiResponse<BudgetAnalysis>> {
    try {
      // Get budget details
      const budgetResponse = await this.supabase.getBudgets();
      if (!budgetResponse.success || !budgetResponse.data) {
        return {
          success: false,
          error: 'Failed to fetch budgets'
        };
      }

      const budget = budgetResponse.data.find(b => b.id === budgetId);
      if (!budget) {
        return {
          success: false,
          error: 'Budget not found'
        };
      }

      // Get transactions for the budget period
      const transactionsResponse = await this.supabase.getTransactions();
      if (!transactionsResponse.success || !transactionsResponse.data) {
        return {
          success: false,
          error: 'Failed to fetch transactions'
        };
      }

      const budgetTransactions = transactionsResponse.data.filter(t => {
        const transactionDate = new Date(t.date);
        const startDate = new Date(budget.start_date);
        const endDate = budget.end_date ? new Date(budget.end_date) : new Date();
        
        return transactionDate >= startDate && 
               transactionDate <= endDate &&
               (!budget.category || t.category_primary === budget.category);
      });

      const spent = budgetTransactions.reduce((sum, t) => sum + Math.abs(t.amount), 0);
      const remaining = budget.amount - spent;
      const percentageUsed = (spent / budget.amount) * 100;
      const isOverBudget = spent > budget.amount;
      
      const daysRemaining = Math.ceil((new Date(budget.end_date || new Date()).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24));
      const dailySpendingRate = spent / Math.max(1, (new Date().getTime() - new Date(budget.start_date).getTime()) / (1000 * 60 * 60 * 24));

      return {
        success: true,
        data: {
          budget_id: budget.id,
          budget_name: budget.name,
          spent,
          remaining,
          percentage_used: percentageUsed,
          is_over_budget: isOverBudget,
          days_remaining: Math.max(0, daysRemaining),
          daily_spending_rate: dailySpendingRate
        }
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
  }

  async getSpendingAnalysis(month?: string): Promise<ApiResponse<SpendingAnalysis[]>> {
    try {
      const transactionsResponse = await this.supabase.getTransactions();
      if (!transactionsResponse.success || !transactionsResponse.data) {
        return {
          success: false,
          error: 'Failed to fetch transactions'
        };
      }

      const transactions = month 
        ? transactionsResponse.data.filter(t => t.date.startsWith(month))
        : transactionsResponse.data;

      const spendingByCategory = transactions
        .filter(t => t.amount < 0) // Only expenses
        .reduce((acc, t) => {
          const category = t.category_primary || 'Other';
          acc[category] = (acc[category] || 0) + Math.abs(t.amount);
          return acc;
        }, {} as Record<string, number>);

      const totalSpending = Object.values(spendingByCategory).reduce((sum, amount) => sum + amount, 0);

      const analysis: SpendingAnalysis[] = Object.entries(spendingByCategory).map(([category, amount]) => ({
        category,
        amount,
        percentage: (amount / totalSpending) * 100,
        transaction_count: transactions.filter(t => t.category_primary === category).length,
        trend: 'stable' // This would require historical data for proper calculation
      }));

      return {
        success: true,
        data: analysis.sort((a, b) => b.amount - a.amount)
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
  }

  async getFinancialHealthScore(): Promise<ApiResponse<FinancialHealthScore>> {
    try {
      const monthlySummaryResponse = await this.supabase.getMonthlySummary(
        new Date().toISOString().slice(0, 7)
      );
      
      if (!monthlySummaryResponse.success || !monthlySummaryResponse.data) {
        return {
          success: false,
          error: 'Failed to fetch monthly summary'
        };
      }

      const summary = monthlySummaryResponse.data;
      
      // Calculate savings rate
      const savingsRate = summary.total_income > 0 
        ? (summary.net_savings / summary.total_income) * 100 
        : 0;

      // Get budgets for budget adherence
      const budgetsResponse = await this.supabase.getBudgets();
      let budgetAdherence = 100; // Default to perfect adherence
      
      if (budgetsResponse.success && budgetsResponse.data && budgetsResponse.data.length > 0) {
        const budgetAnalyses = await Promise.all(
          budgetsResponse.data.map(budget => this.getBudgetAnalysis(budget.id))
        );
        
        const validAnalyses = budgetAnalyses.filter(r => r.success).map(r => r.data!);
        if (validAnalyses.length > 0) {
          const avgPercentageUsed = validAnalyses.reduce((sum, analysis) => sum + analysis.percentage_used, 0) / validAnalyses.length;
          budgetAdherence = Math.max(0, 100 - Math.max(0, avgPercentageUsed - 100));
        }
      }

      // Calculate overall score
      const score = Math.round(
        (Math.min(100, savingsRate * 2) * 0.4) + // Savings rate (40% weight)
        (budgetAdherence * 0.3) + // Budget adherence (30% weight)
        (75 * 0.2) + // Spending consistency (placeholder, 20% weight)
        (80 * 0.1)   // Income stability (placeholder, 10% weight)
      );

      const recommendations: string[] = [];
      if (savingsRate < 20) {
        recommendations.push('Consider increasing your savings rate to at least 20%');
      }
      if (budgetAdherence < 80) {
        recommendations.push('Try to stick closer to your budget limits');
      }
      if (summary.total_expenses > summary.total_income) {
        recommendations.push('Your expenses exceed your income. Review your spending habits.');
      }

      return {
        success: true,
        data: {
          score,
          factors: {
            savings_rate: Math.min(100, savingsRate * 2),
            budget_adherence: budgetAdherence,
            spending_consistency: 75, // Placeholder
            income_stability: 80 // Placeholder
          },
          recommendations
        }
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
  }

  // Utility Functions
  async validateConfiguration(): Promise<ApiResponse<{ isValid: boolean; errors: string[] }>> {
    try {
      const supabaseValidation = { isValid: true, errors: [] as string[] };
      const plaidValidation = this.plaid.validatePlaidConfig();

      const allErrors = [
        ...supabaseValidation.errors,
        ...plaidValidation.errors
      ];

      return {
        success: true,
        data: {
          isValid: allErrors.length === 0,
          errors: allErrors
        }
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
  }

  async checkHealth(): Promise<ApiResponse<{ status: string; services: Record<string, boolean> }>> {
    try {
      const services = {
        supabase: false,
        plaid: false,
        config: false
      };

      // Check configuration
      const configValidation = this.config.validateConfig();
      services.config = configValidation.isValid;

      // Check Supabase connection
      const supabaseTest = await this.supabase.getCurrentUser();
      services.supabase = supabaseTest.success || Boolean(supabaseTest.error?.includes('No user found'));

      // Check Plaid configuration
      const plaidValidation = this.plaid.validatePlaidConfig();
      services.plaid = plaidValidation.isValid;

      const allHealthy = Object.values(services).every(Boolean);
      
      return {
        success: true,
        data: {
          status: allHealthy ? 'healthy' : 'degraded',
          services: {
            supabase: services.supabase || false,
            plaid: services.plaid || false,
            config: services.config || false
          }
        }
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
  }
}

export default ApiService.getInstance();
