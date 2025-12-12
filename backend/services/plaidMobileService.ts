import { 
  PlaidLinkToken, 
  PlaidPublicToken, 
  PlaidAccessToken, 
  PlaidAccount, 
  PlaidTransaction,
  ApiResponse 
} from '../types';

class PlaidMobileService {
  private static instance: PlaidMobileService;
  
  // Plaid SDK configuration
  private config = {
    clientId: process.env.PLAID_CLIENT_ID || '68f9e88c17270900222dae83',
    env: process.env.PLAID_ENV || 'sandbox'
  };

  private constructor() {}

  static getInstance(): PlaidMobileService {
    if (!PlaidMobileService.instance) {
      PlaidMobileService.instance = new PlaidMobileService();
    }
    return PlaidMobileService.instance;
  }

  // Create Plaid Link Token (using Plaid SDK)
  async createLinkToken(userId: string): Promise<ApiResponse<PlaidLinkToken>> {
    try {
      // This would use the Plaid SDK on mobile
      // For now, we'll use the Edge Function approach
      const response = await fetch(`${process.env.EXPO_PUBLIC_SUPABASE_URL}/functions/v1/plaid-webhook/plaid/create-link-token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY}`
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

  // Exchange public token for access token
  async exchangePublicToken(publicToken: string): Promise<ApiResponse<PlaidAccessToken>> {
    try {
      const response = await fetch(`${process.env.EXPO_PUBLIC_SUPABASE_URL}/functions/v1/plaid-webhook/plaid/exchange-token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY}`
        },
        body: JSON.stringify({
          public_token: publicToken
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
          item_id: data.item_id
        }
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
  }

  // Get accounts from Plaid
  async getAccounts(accessToken: string): Promise<ApiResponse<PlaidAccount[]>> {
    try {
      const response = await fetch(`${process.env.EXPO_PUBLIC_SUPABASE_URL}/functions/v1/plaid-webhook/plaid/get-accounts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY}`
        },
        body: JSON.stringify({
          access_token: accessToken
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

  // Get transactions from Plaid
  async getTransactions(
    accessToken: string, 
    startDate: string, 
    endDate: string
  ): Promise<ApiResponse<PlaidTransaction[]>> {
    try {
      const response = await fetch(`${process.env.EXPO_PUBLIC_SUPABASE_URL}/functions/v1/plaid-webhook/plaid/get-transactions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY}`
        },
        body: JSON.stringify({
          access_token: accessToken,
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
  async syncTransactions(bankAccountId: string): Promise<ApiResponse<{ synced: number; new: number }>> {
    try {
      const response = await fetch(`${process.env.EXPO_PUBLIC_SUPABASE_URL}/functions/v1/plaid-webhook/plaid/get-transactions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY}`
        }
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
          new: data.new || 0
        }
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
  }

  // Validate Plaid configuration
  validatePlaidConfig(): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];
    
    if (!process.env.PLAID_CLIENT_ID) {
      errors.push('Plaid client ID is missing');
    }
    
    if (!process.env.PLAID_SECRET) {
      errors.push('Plaid secret is missing');
    }
    
    if (!['sandbox', 'development', 'production'].includes(process.env.PLAID_ENV?.toLowerCase() || 'sandbox')) {
      errors.push('Invalid Plaid environment');
    }
    
    return {
      isValid: errors.length === 0,
      errors
    };
  }

  // Format Plaid account data for our database
  formatPlaidAccount(plaidAccount: PlaidAccount, userId: string): Partial<any> {
    return {
      user_id: userId,
      account_name: plaidAccount.name,
      bank_name: 'Plaid Bank', // This would be determined from the institution
      account_type: this.mapAccountType(plaidAccount.type, plaidAccount.subtype),
      is_active: true,
      plaid_account_id: plaidAccount.account_id,
      plaid_mask: plaidAccount.mask
    };
  }

  // Format Plaid transaction data for our database
  formatPlaidTransaction(
    plaidTransaction: PlaidTransaction, 
    bankAccountId: string
  ): Partial<any> {
    return {
      bank_account_id: bankAccountId,
      amount: plaidTransaction.amount,
      description: plaidTransaction.name || plaidTransaction.merchant_name,
      category_primary: plaidTransaction.category?.[0],
      category_detailed: plaidTransaction.category?.join(', '),
      date: plaidTransaction.date,
      is_manual: false,
      is_pending: plaidTransaction.pending,
      plaid_transaction_id: plaidTransaction.transaction_id,
      location: plaidTransaction.location ? {
        address: plaidTransaction.location.address,
        city: plaidTransaction.location.city,
        state: plaidTransaction.location.region,
        zip: plaidTransaction.location.postal_code
      } : null
    };
  }

  // Map Plaid account types to our types
  private mapAccountType(type: string, subtype?: string): string {
    switch (type.toLowerCase()) {
      case 'depository':
        if (subtype?.includes('checking')) return 'checking';
        if (subtype?.includes('savings')) return 'savings';
        return 'checking';
      case 'credit':
        return 'credit';
      case 'loan':
        return 'credit';
      case 'investment':
        return 'savings';
      default:
        return 'cash';
    }
  }
}

export default PlaidMobileService.getInstance();