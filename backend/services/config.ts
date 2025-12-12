// Unified Configuration Service for SmartBudget
import { Platform } from 'react-native';

class ConfigService {
  private static instance: ConfigService;
  
  // Supabase Configuration
  readonly supabase = {
    url: process.env.EXPO_PUBLIC_SUPABASE_URL || 'https://ojcvjsxmshdvyxryunvk.supabase.co',
    anonKey: process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9qY3Zqc3htc2hkdnl4cnl1bnZrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg4ODE3MDMsImV4cCI6MjA3NDQ1NzcwM30.sUPQRXSO9i4kAwUhAo6rSLXdusV-3VbphKlqUdxDdfM'
  };

  // Plaid Configuration
  readonly plaid = {
    clientId: process.env.PLAID_CLIENT_ID || '68f9e88c17270900222dae83',
    secret: process.env.PLAID_SECRET || 'ce8fb384dc57b556987e6874f719d9',
    env: process.env.PLAID_ENV || 'sandbox',
    publicToken: process.env.public_token || 'public-sandbox-378695db-9487-4f61-8bd5-e956d808f549',
    requestId: process.env.request_id || '4ajDtM6P9adboRd'
  };

  // API Configuration
  readonly api = {
    baseUrl: Platform.OS === 'ios' ? 'http://localhost:3000' : 'http://10.0.2.2:3000',
    timeout: 30000,
    retryAttempts: 3,
    retryDelay: 1000
  };

  // App Configuration
  readonly app = {
    name: 'SmartBudget',
    version: '1.0.0',
    currency: 'USD',
    dateFormat: 'YYYY-MM-DD',
    timeFormat: '24h'
  };

  // Feature Flags
  readonly features = {
    enablePushNotifications: true,
    enableBiometricAuth: true,
    enableDarkMode: true,
    enableAnalytics: false,
    enableBetaFeatures: false
  };

  // Budget Categories
  readonly defaultCategories = [
    { name: 'Food & Dining', icon: 'restaurant', color: '#FF6B6B' },
    { name: 'Transportation', icon: 'car', color: '#4ECDC4' },
    { name: 'Shopping', icon: 'bag', color: '#45B7D1' },
    { name: 'Entertainment', icon: 'game-controller', color: '#96CEB4' },
    { name: 'Bills & Utilities', icon: 'document-text', color: '#FFEAA7' },
    { name: 'Healthcare', icon: 'heart', color: '#DDA0DD' },
    { name: 'Education', icon: 'book', color: '#98D8C8' },
    { name: 'Travel', icon: 'airplane', color: '#F7DC6F' },
    { name: 'Other', icon: 'ellipsis-horizontal', color: '#BDC3C7' }
  ];

  // Alert Thresholds
  readonly alerts = {
    budgetWarning: 0.8, // 80%
    budgetCritical: 1.0, // 100%
    lowBalance: 100, // $100
    largeTransaction: 500 // $500
  };

  // Cache Configuration
  readonly cache = {
    ttl: {
      transactions: 300000, // 5 minutes
      accounts: 600000, // 10 minutes
      budgets: 300000, // 5 minutes
      insights: 3600000 // 1 hour
    }
  };

  private constructor() {}

  static getInstance(): ConfigService {
    if (!ConfigService.instance) {
      ConfigService.instance = new ConfigService();
    }
    return ConfigService.instance;
  }

  // Get Plaid environment configuration
  getPlaidEnv() {
    switch (this.plaid.env.toLowerCase()) {
      case 'sandbox':
        return 'sandbox';
      case 'development':
        return 'development';
      case 'production':
        return 'production';
      default:
        return 'sandbox';
    }
  }

  // Get API headers
  getApiHeaders() {
    return {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'User-Agent': `${this.app.name}/${this.app.version}`
    };
  }

  // Validate configuration
  validateConfig(): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!this.supabase.url) {
      errors.push('Supabase URL is missing');
    }

    if (!this.supabase.anonKey) {
      errors.push('Supabase anonymous key is missing');
    }

    if (!this.plaid.clientId) {
      errors.push('Plaid client ID is missing');
    }

    if (!this.plaid.secret) {
      errors.push('Plaid secret is missing');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  // Get environment info
  getEnvironmentInfo() {
    return {
      platform: Platform.OS,
      version: Platform.Version,
      appVersion: this.app.version,
      plaidEnv: this.getPlaidEnv(),
      features: this.features
    };
  }
}

export default ConfigService.getInstance();