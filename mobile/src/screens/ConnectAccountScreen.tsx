import * as React from 'react';
import {
  View,
  Text,
  TextInput,
  Pressable,
  Alert,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  Switch,
} from 'react-native';
import PlaidConnection from '../components/PlaidConnection';
import SwipeNavigationWrapper from '@/components/SwipeNavigationWrapper';
import { makeAuthenticatedRequest, authService } from '../services/authService';

const API_BASE_URL = 'http://localhost:8000/api';

type BankProvider = {
  id: string;
  name: string;
  logo: string;
  supported: boolean;
};

type ConnectionStatus = 'idle' | 'connecting' | 'connected' | 'error';

type Account = {
  account_id: string;
  name: string;
  mask?: string;
  type?: string;
  balance?: number;
};

type Transaction = {
  transaction_id: string;
  date: string;
  description: string;
  amount: number;
  type: string;
};

export default function ConnectAccountScreen() {
  const [connectionStatus, setConnectionStatus] = React.useState<ConnectionStatus>('idle');
  const [selectedProvider, setSelectedProvider] = React.useState<string>('');
  const [username, setUsername] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [enableAutoSync, setEnableAutoSync] = React.useState(true);
  const [syncFrequency, setSyncFrequency] = React.useState('daily');
  const [showPlaidConnection, setShowPlaidConnection] = React.useState(false);
  const [accountsData, setAccountsData] = React.useState<Account[]>([]);
  const [transactionsData, setTransactionsData] = React.useState<Transaction[]>([]);
  const [showAccounts, setShowAccounts] = React.useState(false);
  const [showTransactions, setShowTransactions] = React.useState(false);
  const [loadingAccounts, setLoadingAccounts] = React.useState(false);
  const [loadingTransactions, setLoadingTransactions] = React.useState(false);

  // Mock bank providers - in real app, this would come from API
  const bankProviders: BankProvider[] = [
    { id: 'chase', name: 'Chase Bank', logo: '🏦', supported: true },
    { id: 'bofa', name: 'Bank of America', logo: '🏛️', supported: true },
    { id: 'wells', name: 'Wells Fargo', logo: '🏪', supported: true },
    { id: 'citi', name: 'Citibank', logo: '🏢', supported: true },
    { id: 'capital', name: 'Capital One', logo: '💳', supported: false },
    { id: 'td', name: 'TD Bank', logo: '🏦', supported: false },
  ];

  // Plaid connection handlers
  const handlePlaidSuccess = async (publicToken: string, metadata: any) => {
    try {
      setConnectionStatus('connecting');
      
      // Ensure user is authenticated (mock for demo)
      if (!authService.isAuthenticated()) {
        authService.mockLogin();
      }
      
      // Exchange public token for access token using the correct endpoint
      const response = await makeAuthenticatedRequest(`${API_BASE_URL}/plaid-legacy/exchange-token`, {
        method: 'POST',
        body: JSON.stringify({
          public_token: publicToken
        })
      });

      if (response.ok) {
        const data = await response.json();
        setConnectionStatus('connected');
        setSelectedProvider('plaid-' + metadata.institution.institution_id);
        setShowPlaidConnection(false);
        
        Alert.alert(
          'Success!',
          `Connected to ${metadata.institution.name} successfully. ${data.message}`
        );
      } else {
        throw new Error('Failed to exchange token');
      }
    } catch (error) {
      console.error('Plaid success error:', error);
      setConnectionStatus('error');
      Alert.alert('Connection Error', 'Failed to complete bank connection. Please try again.');
    }
  };

  const handlePlaidError = (error: any) => {
    console.error('Plaid error:', error);
    setConnectionStatus('error');
    setShowPlaidConnection(false);
    Alert.alert('Connection Failed', 'Unable to connect to your bank. Please try again or contact support.');
  };

  const handleConnect = async () => {
    if (!selectedProvider) {
      Alert.alert('Select Bank', 'Please select a bank provider first.');
      return;
    }
    
    if (!username.trim() || !password.trim()) {
      Alert.alert('Missing Credentials', 'Please enter your banking credentials.');
      return;
    }

    setConnectionStatus('connecting');

    try {
      // Simulate API call to connect bank account
      const response = await fetch('/api/connect-bank', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer your-auth-token', // Replace with actual token
        },
        body: JSON.stringify({
          provider: selectedProvider,
          credentials: {
            username,
            password,
          },
          settings: {
            autoSync: enableAutoSync,
            syncFrequency,
          },
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setConnectionStatus('connected');
        Alert.alert('Success!', `Connected to ${bankProviders.find(p => p.id === selectedProvider)?.name}. Found ${data.accountCount || 0} accounts.`);
        
        // Clear sensitive data
        setUsername('');
        setPassword('');
      } else {
        throw new Error('Connection failed');
      }
    } catch (error) {
      setConnectionStatus('error');
      Alert.alert('Connection Failed', 'Unable to connect to your bank. Please check your credentials and try again.');
    }
  };

  const handleDisconnect = async () => {
    Alert.alert(
      'Disconnect Bank',
      'Are you sure you want to disconnect your bank account? This will stop automatic transaction syncing.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Disconnect',
          style: 'destructive',
          onPress: async () => {
            setConnectionStatus('idle');
            setSelectedProvider('');
            setAccountsData([]);
            setTransactionsData([]);
            setShowAccounts(false);
            setShowTransactions(false);
            // TODO: Call API to disconnect
          },
        },
      ]
    );
  };

  // Fetch accounts from Plaid legacy endpoint
  const fetchAccounts = async () => {
    try {
      setLoadingAccounts(true);
      const response = await makeAuthenticatedRequest(`${API_BASE_URL}/plaid-legacy/accounts`, {
        method: 'GET',
      });

      if (response.ok) {
        const data = await response.json();
        setAccountsData(data.accounts || []);
        setShowAccounts(true);
        Alert.alert('Success', `Found ${data.accounts?.length || 0} accounts`);
      } else {
        throw new Error('Failed to fetch accounts');
      }
    } catch (error) {
      console.error('Error fetching accounts:', error);
      Alert.alert('Error', 'Failed to fetch accounts. Please try again.');
    } finally {
      setLoadingAccounts(false);
    }
  };

  // Fetch transactions from Plaid legacy endpoint
  const fetchTransactions = async () => {
    try {
      setLoadingTransactions(true);
      const response = await makeAuthenticatedRequest(`${API_BASE_URL}/plaid-legacy/transactions`, {
        method: 'GET',
      });

      if (response.ok) {
        const data = await response.json();
        setTransactionsData(data.transactions || []);
        setShowTransactions(true);
        Alert.alert('Success', `Found ${data.transactions?.length || 0} transactions`);
      } else {
        throw new Error('Failed to fetch transactions');
      }
    } catch (error) {
      console.error('Error fetching transactions:', error);
      Alert.alert('Error', 'Failed to fetch transactions. Please try again.');
    } finally {
      setLoadingTransactions(false);
    }
  };

  const renderBankProvider = (provider: BankProvider) => (
    <Pressable
      key={provider.id}
      style={[
        styles.providerCard,
        selectedProvider === provider.id && styles.providerCardSelected,
        !provider.supported && styles.providerCardDisabled,
      ]}
      onPress={() => provider.supported && setSelectedProvider(provider.id)}
      disabled={!provider.supported}
    >
      <Text style={styles.providerLogo}>{provider.logo}</Text>
      <View style={styles.providerInfo}>
        <Text style={[styles.providerName, !provider.supported && styles.disabledText]}>
          {provider.name}
        </Text>
        <Text style={styles.providerStatus}>
          {provider.supported ? 'Available' : 'Coming Soon'}
        </Text>
      </View>
      {selectedProvider === provider.id && (
        <Text style={styles.selectedIndicator}>✓</Text>
      )}
    </Pressable>
  );

  if (connectionStatus === 'connected') {
    return (
      <ScrollView style={styles.screen}>
        <Text style={styles.title}>Connect Account</Text>
        
        <View style={styles.successCard}>
          <Text style={styles.successIcon}>✅</Text>
          <Text style={styles.successTitle}>Bank Connected!</Text>
          <Text style={styles.successMessage}>
            Your {bankProviders.find(p => p.id === selectedProvider)?.name} account is now connected.
            Transactions will sync automatically.
          </Text>
          
          <View style={styles.connectionInfo}>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Status:</Text>
              <Text style={styles.infoValue}>Active</Text>
            </View>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Auto Sync:</Text>
              <Text style={styles.infoValue}>{enableAutoSync ? 'Enabled' : 'Disabled'}</Text>
            </View>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Sync Frequency:</Text>
              <Text style={styles.infoValue}>{syncFrequency}</Text>
            </View>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Last Sync:</Text>
              <Text style={styles.infoValue}>Just now</Text>
            </View>
          </View>

          {/* Fetch Data Buttons */}
          <View style={styles.actionButtonsContainer}>
            <Pressable 
              style={[styles.fetchButton, loadingAccounts && styles.buttonDisabled]}
              onPress={fetchAccounts}
              disabled={loadingAccounts}
            >
              {loadingAccounts ? (
                <ActivityIndicator color="#ffffff" />
              ) : (
                <Text style={styles.fetchButtonText}>📊 Fetch Accounts</Text>
              )}
            </Pressable>

            <Pressable 
              style={[styles.fetchButton, loadingTransactions && styles.buttonDisabled]}
              onPress={fetchTransactions}
              disabled={loadingTransactions}
            >
              {loadingTransactions ? (
                <ActivityIndicator color="#ffffff" />
              ) : (
                <Text style={styles.fetchButtonText}>💳 Fetch Transactions</Text>
              )}
            </Pressable>
          </View>

          {/* Display Accounts */}
          {showAccounts && accountsData.length > 0 && (
            <View style={styles.dataContainer}>
              <Text style={styles.dataTitle}>📊 Accounts ({accountsData.length})</Text>
              {accountsData.map((account) => (
                <View key={account.account_id} style={styles.accountCard}>
                  <Text style={styles.accountName}>{account.name}</Text>
                  {account.mask && <Text style={styles.accountMask}>•••• {account.mask}</Text>}
                  {account.type && <Text style={styles.accountType}>{account.type}</Text>}
                  {account.balance !== undefined && (
                    <Text style={styles.accountBalance}>${account.balance.toFixed(2)}</Text>
                  )}
                </View>
              ))}
            </View>
          )}

          {/* Display Transactions */}
          {showTransactions && transactionsData.length > 0 && (
            <View style={styles.dataContainer}>
              <Text style={styles.dataTitle}>💳 Recent Transactions ({transactionsData.length})</Text>
              {transactionsData.slice(0, 10).map((transaction) => (
                <View key={transaction.transaction_id} style={styles.transactionCard}>
                  <View style={styles.transactionLeft}>
                    <Text style={styles.transactionDescription} numberOfLines={1}>
                      {transaction.description}
                    </Text>
                    <Text style={styles.transactionDate}>{transaction.date}</Text>
                  </View>
                  <Text style={[
                    styles.transactionAmount,
                    transaction.amount > 0 ? styles.amountPositive : styles.amountNegative
                  ]}>
                    {transaction.amount > 0 ? '+' : ''} ${Math.abs(transaction.amount).toFixed(2)}
                  </Text>
                </View>
              ))}
              {transactionsData.length > 10 && (
                <Text style={styles.moreText}>
                  ... and {transactionsData.length - 10} more transactions
                </Text>
              )}
            </View>
          )}

          <Pressable style={styles.disconnectButton} onPress={handleDisconnect}>
            <Text style={styles.disconnectButtonText}>Disconnect Bank</Text>
          </Pressable>
        </View>
      </ScrollView>
    );
  }

  return (
    <SwipeNavigationWrapper currentTab="Connect Account">
      <ScrollView style={styles.screen}>
        <Text style={styles.sectionHeader}>Bank Integration</Text>
        <Text style={styles.sectionDescription}>Connect your bank accounts for automatic transaction sync</Text>
      
        {/* Plaid Connection - Secure Bank Integration */}
        <View style={styles.card}>
          <Text style={styles.subtitle}>🔒 Secure Bank Connection</Text>
          <Text style={styles.description}>
            Connect securely with Plaid - trusted by millions of users and thousands of financial institutions.
          </Text>
          
          {!showPlaidConnection ? (
            <Pressable 
              style={styles.plaidButton}
              onPress={() => setShowPlaidConnection(true)}
            >
              <Text style={styles.plaidButtonText}>Connect with Plaid</Text>
              <Text style={styles.plaidButtonSubtext}>Recommended • Most Secure</Text>
            </Pressable>
          ) : (
            <PlaidConnection
              onSuccess={handlePlaidSuccess}
              onError={handlePlaidError}
            />
          )}
        </View>

        {/* Alternative Manual Connection */}
      <View style={styles.card}>
        <Text style={styles.subtitle}>Alternative: Manual Connection</Text>
        <Text style={styles.description}>
          Or connect manually by entering your banking credentials (less secure).
        </Text>

        <View style={styles.providersContainer}>
          {bankProviders.map(renderBankProvider)}
        </View>

        {selectedProvider && (
          <View style={styles.credentialsSection}>
            <Text style={styles.subtitle}>Banking Credentials</Text>
            <Text style={styles.securityNote}>
              🔒 Your credentials are encrypted and securely stored. We never store your actual banking password.
            </Text>

            <Text style={styles.label}>Username/Email</Text>
            <TextInput
              value={username}
              onChangeText={setUsername}
              placeholder="Enter your banking username"
              placeholderTextColor="#7a8fb2"
              autoCapitalize="none"
              style={styles.input}
            />

            <Text style={styles.label}>Password</Text>
            <TextInput
              value={password}
              onChangeText={setPassword}
              placeholder="Enter your banking password"
              placeholderTextColor="#7a8fb2"
              secureTextEntry
              style={styles.input}
            />

            <View style={styles.settingsSection}>
              <Text style={styles.subtitle}>Sync Settings</Text>
              
              <View style={styles.switchRow}>
                <Text style={styles.switchLabel}>Enable Auto Sync</Text>
                <Switch
                  value={enableAutoSync}
                  onValueChange={setEnableAutoSync}
                  trackColor={{ false: '#767577', true: '#3b82f6' }}
                  thumbColor={enableAutoSync ? '#ffffff' : '#f4f3f4'}
                />
              </View>

              {enableAutoSync && (
                <View style={styles.frequencySection}>
                  <Text style={styles.label}>Sync Frequency</Text>
                  <View style={styles.frequencyOptions}>
                    {['hourly', 'daily', 'weekly'].map((freq) => (
                      <Pressable
                        key={freq}
                        style={[
                          styles.frequencyOption,
                          syncFrequency === freq && styles.frequencyOptionActive,
                        ]}
                        onPress={() => setSyncFrequency(freq)}
                      >
                        <Text style={styles.frequencyText}>
                          {freq.charAt(0).toUpperCase() + freq.slice(1)}
                        </Text>
                      </Pressable>
                    ))}
                  </View>
                </View>
              )}
            </View>

            <Pressable
              style={[styles.connectButton, connectionStatus === 'connecting' && styles.connectButtonDisabled]}
              onPress={handleConnect}
              disabled={connectionStatus === 'connecting'}
            >
              {connectionStatus === 'connecting' ? (
                <ActivityIndicator color="#ffffff" />
              ) : (
                <Text style={styles.connectButtonText}>Connect Bank Account</Text>
              )}
            </Pressable>
          </View>
        )}
      </View>
    </ScrollView>
    </SwipeNavigationWrapper>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#0b1220', paddingHorizontal: 20, paddingVertical: 20 },
  title: { color: 'white', fontSize: 24, fontWeight: '700', marginBottom: 20, textAlign: 'center', marginTop: 8 },
  card: { backgroundColor: '#111a30', borderRadius: 12, marginVertical: 16, padding: 20, marginHorizontal: 8 },
  subtitle: { color: 'white', fontSize: 18, fontWeight: '600', marginBottom: 8 },
  description: { color: '#9bb4da', fontSize: 14, marginBottom: 20, lineHeight: 20 },
  
  // Bank providers
  providersContainer: { marginBottom: 28, paddingHorizontal: 4 },
  providerCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#0f1930',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 2,
    borderColor: 'transparent',
    minHeight: 60,
  },
  providerCardSelected: { borderColor: '#3b82f6' },
  providerCardDisabled: { opacity: 0.5 },
  providerLogo: { fontSize: 24, marginRight: 12 },
  providerInfo: { flex: 1 },
  providerName: { color: 'white', fontSize: 16, fontWeight: '600' },
  providerStatus: { color: '#9bb4da', fontSize: 12 },
  selectedIndicator: { color: '#3b82f6', fontSize: 20, fontWeight: 'bold' },
  disabledText: { color: '#666' },

  // Credentials
  credentialsSection: { marginTop: 20 },
  securityNote: { 
    color: '#22c55e', 
    fontSize: 12, 
    backgroundColor: '#0f1930', 
    padding: 10, 
    borderRadius: 8, 
    marginBottom: 16 
  },
  label: { color: '#a9c1ea', fontSize: 13, fontWeight: '600', marginBottom: 8, marginTop: 16 },
  input: {
    height: 48,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#223459',
    color: 'white',
    paddingHorizontal: 16,
    backgroundColor: '#0f1930',
    marginBottom: 12,
  },

  // Settings
  settingsSection: { marginTop: 20 },
  switchRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  switchLabel: { color: 'white', fontSize: 16 },
  frequencySection: { marginTop: 12 },
  frequencyOptions: { flexDirection: 'row', gap: 8, marginTop: 8 },
  frequencyOption: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
    backgroundColor: '#0f1930',
    borderWidth: 1,
    borderColor: '#223459',
  },
  frequencyOptionActive: { backgroundColor: '#3b82f6', borderColor: '#3b82f6' },
  frequencyText: { color: 'white', fontSize: 14 },

  // Buttons
  connectButton: {
    backgroundColor: '#3b82f6',
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 24,
  },
  connectButtonDisabled: { opacity: 0.6 },
  connectButtonText: { color: 'white', fontWeight: '700', fontSize: 16 },

  // Success state
  successCard: { backgroundColor: '#111a30', borderRadius: 12, marginVertical: 16, padding: 20, alignItems: 'center' },
  successIcon: { fontSize: 48, marginBottom: 16 },
  successTitle: { color: 'white', fontSize: 20, fontWeight: 'bold', marginBottom: 8 },
  successMessage: { color: '#9bb4da', fontSize: 14, textAlign: 'center', marginBottom: 24, lineHeight: 20 },
  connectionInfo: { width: '100%', marginBottom: 24 },
  infoRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 8 },
  infoLabel: { color: '#a9c1ea', fontSize: 14 },
  infoValue: { color: 'white', fontSize: 14, fontWeight: '600' },
  disconnectButton: {
    backgroundColor: '#ef4444',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
  },
  disconnectButtonText: { color: 'white', fontWeight: '600' },
  sectionHeader: {
    color: '#9fb3c8',
    fontSize: 20,
    fontWeight: '700',
    marginBottom: 8,
    textAlign: 'center',
  },
  sectionDescription: {
    color: '#7a8fa5',
    fontSize: 14,
    marginBottom: 20,
    textAlign: 'center',
    lineHeight: 18,
  },
  
  // Plaid button styles
  plaidButton: {
    backgroundColor: '#3b82f6',
    paddingVertical: 16,
    paddingHorizontal: 20,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#3b82f6',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  plaidButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 2,
  },
  plaidButtonSubtext: {
    color: '#bfdbfe',
    fontSize: 12,
    fontWeight: '500',
  },
  
  // Fetch data buttons and display
  actionButtonsContainer: {
    flexDirection: 'row',
    gap: 12,
    marginVertical: 20,
    width: '100%',
  },
  fetchButton: {
    flex: 1,
    backgroundColor: '#10b981',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  fetchButtonText: {
    color: 'white',
    fontWeight: '600',
    fontSize: 14,
  },
  buttonDisabled: {
    opacity: 0.6,
  },

  // Data display containers
  dataContainer: {
    marginTop: 24,
    marginBottom: 16,
    backgroundColor: '#0f1930',
    borderRadius: 10,
    padding: 16,
    borderLeftWidth: 4,
    borderLeftColor: '#3b82f6',
  },
  dataTitle: {
    color: 'white',
    fontSize: 16,
    fontWeight: '700',
    marginBottom: 12,
  },

  // Account card styles
  accountCard: {
    backgroundColor: '#111a30',
    borderRadius: 8,
    padding: 12,
    marginBottom: 10,
    borderLeftWidth: 3,
    borderLeftColor: '#06b6d4',
  },
  accountName: {
    color: 'white',
    fontSize: 15,
    fontWeight: '600',
    marginBottom: 4,
  },
  accountMask: {
    color: '#a9c1ea',
    fontSize: 13,
    marginBottom: 4,
  },
  accountType: {
    color: '#9bb4da',
    fontSize: 12,
    marginBottom: 4,
  },
  accountBalance: {
    color: '#10b981',
    fontSize: 14,
    fontWeight: '700',
  },

  // Transaction card styles
  transactionCard: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#111a30',
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
    borderLeftWidth: 3,
    borderLeftColor: '#f59e0b',
  },
  transactionLeft: {
    flex: 1,
  },
  transactionDescription: {
    color: 'white',
    fontSize: 14,
    fontWeight: '500',
    marginBottom: 4,
  },
  transactionDate: {
    color: '#9bb4da',
    fontSize: 12,
  },
  transactionAmount: {
    fontSize: 14,
    fontWeight: '700',
    marginLeft: 8,
  },
  amountPositive: {
    color: '#10b981',
  },
  amountNegative: {
    color: '#ef4444',
  },
  moreText: {
    color: '#9bb4da',
    fontSize: 12,
    fontStyle: 'italic',
    textAlign: 'center',
    marginTop: 8,
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: '#223459',
  },
});