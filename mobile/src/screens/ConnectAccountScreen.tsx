import * as React from 'react';
import {
  View,
  Text,
  Pressable,
  Alert,
  StyleSheet,
  ScrollView,
} from 'react-native';
import PlaidConnection from '../components/PlaidConnection';
import SwipeNavigationWrapper from '@/components/SwipeNavigationWrapper';
import { makeAuthenticatedRequest, authService } from '../services/authService';

type ConnectionStatus = 'idle' | 'connecting' | 'connected' | 'error';

export default function ConnectAccountScreen() {
  const [connectionStatus, setConnectionStatus] = React.useState<ConnectionStatus>('idle');
  const [selectedProvider, setSelectedProvider] = React.useState<string>('');
  const [showPlaidConnection, setShowPlaidConnection] = React.useState(false);

  // Plaid connection handlers
  const handlePlaidSuccess = async (publicToken: string, metadata: any) => {
    try {
      setConnectionStatus('connecting');
      
      // Ensure user is authenticated (mock for demo)
      if (!authService.isAuthenticated()) {
        authService.mockLogin();
      }
      
      // Exchange public token for access token using the correct endpoint
      const response = await makeAuthenticatedRequest('/api/banks/link/exchange-token', {
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
            // TODO: Call API to disconnect
          },
        },
      ]
    );
  };

  if (connectionStatus === 'connected') {
    // Use generic "your bank" since we don't store the actual bank name after connection
    const bankName = selectedProvider.startsWith('plaid-') 
      ? 'your bank' 
      : (selectedProvider || 'your bank');
    
    return (
      <SwipeNavigationWrapper currentTab="Connect Account" scrollable={false}>
        <ScrollView style={styles.screen}>
          <Text style={styles.title}>Connect Account</Text>
          
          <View style={styles.successCard}>
            <Text style={styles.successIcon}>✅</Text>
            <Text style={styles.successTitle}>Bank Connected!</Text>
            <Text style={styles.successMessage}>
              Your {bankName} account is now connected.
              Transactions will sync automatically.
            </Text>
            
            <View style={styles.connectionInfo}>
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Status:</Text>
                <Text style={styles.infoValue}>Active</Text>
              </View>
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Last Sync:</Text>
                <Text style={styles.infoValue}>Just now</Text>
              </View>
            </View>

            <Pressable style={styles.disconnectButton} onPress={handleDisconnect}>
              <Text style={styles.disconnectButtonText}>Disconnect Bank</Text>
            </Pressable>
          </View>
        </ScrollView>
      </SwipeNavigationWrapper>
    );
  }

  return (
    <SwipeNavigationWrapper currentTab="Connect Account" scrollable={false}>
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
});