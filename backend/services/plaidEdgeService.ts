// Enhanced Plaid Service for SmartBudget Mobile
import { PlaidLinkToken, PlaidPublicToken, PlaidAccessToken, ApiResponse } from '../types';

class PlaidEdgeService {
  private static instance: PlaidEdgeService;
  private supabaseUrl: string;
  private supabaseAnonKey: string;

  private constructor() {
    this.supabaseUrl = process.env.EXPO_PUBLIC_SUPABASE_URL || 'https://ojcvjsxmshdvyxryunvk.supabase.co';
    this.supabaseAnonKey = process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY || 'your-anon-key';
  }

  static getInstance(): PlaidEdgeService {
    if (!PlaidEdgeService.instance) {
      PlaidEdgeService.instance = new PlaidEdgeService();
    }
    return PlaidEdgeService.instance;
  }

  // Create Plaid Link Token via Edge Function
  async createLinkToken(userId: string): Promise<ApiResponse<PlaidLinkToken>> {
    try {
      const response = await fetch(`${this.supabaseUrl}/functions/v1/plaid-webhook/plaid/create-link-token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.supabaseAnonKey}`
        },
        body: JSON.stringify({
          user_id: userId
        })
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          success: false,
          error: data.error || 'Failed to create link token'
        };
      }

      return {
        success: true,
        data: {
          link_token: data.link_token,
          expiration: data.expiration,
          request_id: data.request_id
        }
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
  }

  // Exchange public token for access token via Edge Function
  async exchangePublicToken(publicToken: string, userId: string): Promise<ApiResponse<PlaidAccessToken>> {
    try {
      const response = await fetch(`${this.supabaseUrl}/functions/v1/plaid-webhook/plaid/exchange-token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.supabaseAnonKey}`
        },
        body: JSON.stringify({
          public_token: publicToken,
          user_id: userId
        })
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          success: false,
          error: data.error || 'Failed to exchange public token'
        };
      }

      return {
        success: true,
        data: {
          access_token: data.access_token,
          item_id: data.item_id,
          request_id: 'edge-function-response'
        }
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
  }

  // Get accounts via Edge Function
  async getAccounts(userId: string): Promise<ApiResponse<any[]>> {
    try {
      const response = await fetch(`${this.supabaseUrl}/functions/v1/plaid-webhook/plaid/get-accounts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.supabaseAnonKey}`
        },
        body: JSON.stringify({
          user_id: userId
        })
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          success: false,
          error: data.error || 'Failed to fetch accounts'
        };
      }

      return {
        success: true,
        data: data.accounts || []
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
  }

  // Get transactions via Edge Function
  async getTransactions(userId: string, startDate?: string, endDate?: string): Promise<ApiResponse<any[]>> {
    try {
      const response = await fetch(`${this.supabaseUrl}/functions/v1/plaid-webhook/plaid/get-transactions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.supabaseAnonKey}`
        },
        body: JSON.stringify({
          user_id: userId,
          start_date: startDate,
          end_date: endDate
        })
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          success: false,
          error: data.error || 'Failed to fetch transactions'
        };
      }

      return {
        success: true,
        data: data.transactions || []
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
  }

  // Sync transactions for an account
  async syncTransactions(userId: string): Promise<ApiResponse<{ synced: number; new: number }>> {
    try {
      const response = await fetch(`${this.supabaseUrl}/functions/v1/plaid-webhook/plaid/get-transactions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.supabaseAnonKey}`
        },
        body: JSON.stringify({
          user_id: userId
        })
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          success: false,
          error: data.error || 'Failed to sync transactions'
        };
      }

      return {
        success: true,
        data: {
          synced: data.synced || 0,
          new: data.added || 0
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

export default PlaidEdgeService.getInstance();