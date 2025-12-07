// API service for investment analysis and insights
const API_BASE_URL = 'http://localhost:8000/api'; // Update with your backend URL

export interface InvestmentRecommendation {
  type: string;
  priority: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  recommended_allocation?: number;
  potential_savings?: number;
  expected_return?: number;
  risk_level?: string;
  action_items?: string[];
}

export interface RiskProfile {
  risk_level: 'low' | 'moderate' | 'high';
  risk_score: number;
  expense_ratio: number;
  spending_volatility: number;
  recommended_emergency_fund: number;
}

export interface SavingsPotential {
  current_monthly_savings: number;
  subscription_optimization_savings: number;
  category_optimization_savings: number;
  total_monthly_potential: number;
  annual_potential: number;
  savings_rate: number;
}

export interface FinancialProfileSummary {
  monthly_income: number;
  monthly_expenses: number;
  net_monthly: number;
  savings_potential: number;
  risk_level: string;
}

export interface InvestmentRecommendationsResponse {
  financial_profile_summary: FinancialProfileSummary;
  recommendations: InvestmentRecommendation[];
  summary: any;
  priority_actions: InvestmentRecommendation[];
}

export interface SpendingCategory {
  category: string;
  amount: number;
  percentage: number;
  transaction_count: number;
}

export interface CategoriesResponse {
  categories: SpendingCategory[];
  total_spending: number;
  analysis_period_days: number;
}

export interface SavingsOpportunity {
  type: string;
  title: string;
  description: string;
  potential_monthly_savings: number;
  action_items?: string[];
  suggestions?: string[];
}

export interface SavingsOpportunitiesResponse {
  opportunities: SavingsOpportunity[];
  total_potential_monthly_savings: number;
  total_potential_annual_savings: number;
}

class InvestmentApiService {
  private authToken: string | null = null;

  setAuthToken(token: string) {
    this.authToken = token;
  }

  private async makeRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...options.headers as Record<string, string>,
    };

    if (this.authToken) {
      headers['Authorization'] = `Bearer ${this.authToken}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  async getInvestmentRecommendations(days: number = 90): Promise<InvestmentRecommendationsResponse> {
    return this.makeRequest<InvestmentRecommendationsResponse>(
      `/insights/investment-recommendations?days=${days}`
    );
  }

  async getFinancialProfile(days: number = 90): Promise<any> {
    return this.makeRequest(`/insights/financial-profile?days=${days}`);
  }

  async getSpendingCategories(days: number = 30): Promise<CategoriesResponse> {
    return this.makeRequest<CategoriesResponse>(
      `/insights/categories?days=${days}`
    );
  }

  async getSpendingAnalysis(days: number = 30): Promise<any> {
    return this.makeRequest(`/insights/spending-analysis?days=${days}`);
  }

  async getRecurringTransactions(days: number = 90): Promise<any[]> {
    return this.makeRequest(`/insights/recurring-transactions?days=${days}`);
  }

  async getSavingsOpportunities(): Promise<SavingsOpportunitiesResponse> {
    return this.makeRequest<SavingsOpportunitiesResponse>('/insights/savings-opportunities');
  }

  async getTopMerchants(days: number = 30, limit: number = 10): Promise<any> {
    return this.makeRequest(`/insights/merchants?days=${days}&limit=${limit}`);
  }

  async getTransactions(options: {
    limit?: number;
    offset?: number;
    category?: string;
    merchant?: string;
    min_amount?: number;
    max_amount?: number;
  } = {}): Promise<any[]> {
    const params = new URLSearchParams();
    
    Object.entries(options).forEach(([key, value]) => {
      if (value !== undefined) {
        params.append(key, value.toString());
      }
    });

    const queryString = params.toString();
    const endpoint = `/insights/transactions${queryString ? `?${queryString}` : ''}`;
    
    return this.makeRequest(endpoint);
  }

  async uploadPortfolio(file: any): Promise<any> {
    const url = `${API_BASE_URL}/insights/upload-financial-document`;
    
    const formData = new FormData();
    formData.append('file', {
      uri: file.uri,
      type: 'text/csv',
      name: file.name || 'financial-document.csv',
    } as any);

    const headers: Record<string, string> = {};
    if (this.authToken) {
      headers['Authorization'] = `Bearer ${this.authToken}`;
    }

    const response = await fetch(url, {
      method: 'POST',
      body: formData,
      headers,
    });

    if (!response.ok) {
      throw new Error(`Document upload failed: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  async getPortfolioChartData(symbol: string, period: string = '1y'): Promise<any> {
    return this.makeRequest(`/insights/portfolio-chart-data/${symbol}?period=${period}`);
  }
}

// Export singleton instance
export const investmentApi = new InvestmentApiService();

// Mock data generator for development/testing
export const generateMockInvestmentData = (): {
  recommendations: InvestmentRecommendation[];
  riskProfile: RiskProfile;
  savingsPotential: SavingsPotential;
} => {
  return {
    recommendations: [
      {
        type: 'emergency_fund',
        priority: 'high',
        title: 'Build Emergency Fund',
        description: 'Build a $18,000 emergency fund (6 months of expenses)',
        recommended_allocation: 300,
        expected_return: 0.04,
        risk_level: 'very_low'
      },
      {
        type: 'stock_index_fund',
        priority: 'high',
        title: 'Total Stock Market Index Fund',
        description: 'Diversified exposure to the entire stock market',
        recommended_allocation: 400,
        expected_return: 0.10,
        risk_level: 'medium'
      },
      {
        type: 'subscription_optimization',
        priority: 'medium',
        title: 'Optimize Subscriptions',
        description: 'Review $85/month in subscriptions',
        potential_savings: 25,
        expected_return: 0,
        risk_level: 'none',
        action_items: [
          'Cancel unused subscriptions',
          'Downgrade to cheaper plans',
          'Share family plans',
          'Use annual billing for discounts'
        ]
      },
      {
        type: 'bond_fund',
        priority: 'medium',
        title: 'Conservative Bond Index Fund',
        description: 'Diversified bond portfolio for steady income',
        recommended_allocation: 200,
        expected_return: 0.05,
        risk_level: 'low'
      }
    ],
    riskProfile: {
      risk_level: 'moderate',
      risk_score: 3,
      expense_ratio: 0.72,
      spending_volatility: 0.25,
      recommended_emergency_fund: 18000
    },
    savingsPotential: {
      current_monthly_savings: 450,
      subscription_optimization_savings: 85,
      category_optimization_savings: 120,
      total_monthly_potential: 655,
      annual_potential: 7860,
      savings_rate: 0.15
    }
  };
};