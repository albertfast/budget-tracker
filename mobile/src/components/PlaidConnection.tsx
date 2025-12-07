import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Pressable,
  Alert,
  ActivityIndicator,
  Linking
} from 'react-native';
import { makeAuthenticatedRequest, authService } from '../services/authService';

const API_BASE_URL = 'http://localhost:8000/api';

interface PlaidConnectionProps {
  onSuccess: (publicToken: string, metadata: any) => void;
  onError: (error: any) => void;
}

interface PlaidLinkConfiguration {
  token: string;
  onSuccess: (publicToken: string, metadata: any) => void;
  onExit: (error: any, metadata: any) => void;
  onEvent: (eventName: string, metadata: any) => void;
}

export default function PlaidConnection({ onSuccess, onError }: PlaidConnectionProps) {
  const [linkToken, setLinkToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // In a real implementation, you would use @plaid/react-native-link
  // For this demo, we'll simulate the Plaid Link flow

  useEffect(() => {
    createLinkToken();
  }, []);

  const createLinkToken = async () => {
    setLoading(true);
    setError(null);

    try {
      // Ensure user is authenticated (mock for demo)
      if (!authService.isAuthenticated()) {
        authService.mockLogin();
      }

      // Legacy flow: fetch legacy Link init payload (public_key-based)
      const response = await makeAuthenticatedRequest(`${API_BASE_URL}/plaid-legacy/link-init`, {
        method: 'GET'
      });

      if (response.ok) {
        const data = await response.json();
        // For demo purposes, store a pseudo token to enable button
        // Real legacy Link uses public_key + products + env on the client init
        setLinkToken(data.public_key || 'legacy-public-key');
      } else {
        throw new Error('Failed to initialize legacy Plaid Link');
      }
    } catch (err) {
      setError('Failed to initialize Plaid Link. Please try again.');
      console.error('Link token creation error:', err);
    } finally {
      setLoading(false);
    }
  };

  const openPlaidLink = () => {
    if (!linkToken) {
      Alert.alert('Error', 'Plaid Link is not ready. Please wait or try again.');
      return;
    }

    // In a real implementation, you would use PlaidLink.openLink()
    // For this demo, we'll simulate the flow
    simulatePlaidLinkFlow();
  };

  const simulatePlaidLinkFlow = () => {
    Alert.alert(
      'Plaid Link (Demo)',
      'This is a demo version. In a real app, this would open Plaid Link to connect your bank account securely.',
      [
        {
          text: 'Cancel',
          style: 'cancel'
        },
        {
          text: 'Simulate Success',
          onPress: () => {
            // Simulate successful connection
            const mockPublicToken = 'public-token-' + Date.now();
            const mockMetadata = {
              institution: {
                institution_id: 'ins_demo',
                name: 'Demo Bank'
              },
              accounts: [
                {
                  id: 'acc_demo_1',
                  name: 'Demo Checking',
                  type: 'depository',
                  subtype: 'checking'
                }
              ],
              link_session_id: 'link-session-' + Date.now()
            };
            
            onSuccess(mockPublicToken, mockMetadata);
          }
        }
      ]
    );
  };

  const handleLearnMore = () => {
    Linking.openURL('https://plaid.com/safety/');
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#3b82f6" />
        <Text style={styles.loadingText}>Initializing secure connection...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorIcon}>⚠️</Text>
        <Text style={styles.errorText}>{error}</Text>
        <Pressable style={styles.retryButton} onPress={createLinkToken}>
          <Text style={styles.retryButtonText}>Try Again</Text>
        </Pressable>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.plaidHeader}>
        <Text style={styles.plaidLogo}>🔗 Plaid</Text>
        <Text style={styles.plaidSubtitle}>Powered by Plaid</Text>
      </View>

      <View style={styles.securityInfo}>
        <Text style={styles.securityTitle}>🔒 Bank-Level Security</Text>
        <Text style={styles.securityDescription}>
          Plaid uses bank-level 256-bit SSL encryption and is trusted by thousands of financial institutions.
        </Text>
        
        <View style={styles.securityFeatures}>
          <View style={styles.featureRow}>
            <Text style={styles.featureIcon}>✓</Text>
            <Text style={styles.featureText}>Read-only access to your accounts</Text>
          </View>
          <View style={styles.featureRow}>
            <Text style={styles.featureIcon}>✓</Text>
            <Text style={styles.featureText}>No storage of banking credentials</Text>
          </View>
          <View style={styles.featureRow}>
            <Text style={styles.featureIcon}>✓</Text>
            <Text style={styles.featureText}>Encrypted data transmission</Text>
          </View>
          <View style={styles.featureRow}>
            <Text style={styles.featureIcon}>✓</Text>
            <Text style={styles.featureText}>SOC 2 Type II certified</Text>
          </View>
        </View>
      </View>

      <View style={styles.benefits}>
        <Text style={styles.benefitsTitle}>What you'll get:</Text>
        <View style={styles.benefitsList}>
          <Text style={styles.benefitItem}>• Automatic transaction import</Text>
          <Text style={styles.benefitItem}>• Real-time account balances</Text>
          <Text style={styles.benefitItem}>• Categorized spending insights</Text>
          <Text style={styles.benefitItem}>• Investment tracking</Text>
        </View>
      </View>

      <Pressable 
        style={[styles.connectButton, !linkToken && styles.connectButtonDisabled]} 
        onPress={openPlaidLink}
        disabled={!linkToken}
      >
        <Text style={styles.connectButtonText}>
          Connect with Plaid
        </Text>
      </Pressable>

      <Pressable style={styles.learnMoreButton} onPress={handleLearnMore}>
        <Text style={styles.learnMoreText}>Learn more about Plaid security</Text>
      </Pressable>

      <Text style={styles.disclaimer}>
        By connecting your account, you agree to Plaid's Privacy Policy and Terms of Service.
        SmartBudget does not store your banking credentials.
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#111a30',
    borderRadius: 12,
    padding: 20,
    marginVertical: 16,
    marginHorizontal: 8,
  },
  
  // Loading state
  loadingText: {
    color: '#9bb4da',
    fontSize: 16,
    textAlign: 'center',
    marginTop: 16,
  },
  
  // Error state
  errorIcon: {
    fontSize: 48,
    textAlign: 'center',
    marginBottom: 16,
  },
  errorText: {
    color: '#ef4444',
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 20,
    lineHeight: 22,
  },
  retryButton: {
    backgroundColor: '#3b82f6',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    alignSelf: 'center',
  },
  retryButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  
  // Plaid branding
  plaidHeader: {
    alignItems: 'center',
    marginBottom: 24,
  },
  plaidLogo: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#3b82f6',
    marginBottom: 4,
  },
  plaidSubtitle: {
    color: '#9bb4da',
    fontSize: 14,
  },
  
  // Security info
  securityInfo: {
    marginBottom: 24,
  },
  securityTitle: {
    color: '#22c55e',
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 8,
  },
  securityDescription: {
    color: '#9bb4da',
    fontSize: 14,
    lineHeight: 20,
    marginBottom: 16,
  },
  securityFeatures: {
    backgroundColor: '#0f1930',
    borderRadius: 8,
    padding: 16,
  },
  featureRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  featureIcon: {
    color: '#22c55e',
    fontSize: 16,
    fontWeight: 'bold',
    marginRight: 12,
    width: 20,
  },
  featureText: {
    color: '#9bb4da',
    fontSize: 14,
    flex: 1,
  },
  
  // Benefits
  benefits: {
    marginBottom: 24,
  },
  benefitsTitle: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 12,
  },
  benefitsList: {
    backgroundColor: '#0f1930',
    borderRadius: 8,
    padding: 16,
  },
  benefitItem: {
    color: '#9bb4da',
    fontSize: 14,
    marginBottom: 6,
    lineHeight: 20,
  },
  
  // Connect button
  connectButton: {
    backgroundColor: '#3b82f6',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 16,
    shadowColor: '#3b82f6',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  connectButtonDisabled: {
    backgroundColor: '#4b5563',
    shadowOpacity: 0,
    elevation: 0,
  },
  connectButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  
  // Learn more
  learnMoreButton: {
    alignItems: 'center',
    paddingVertical: 8,
    marginBottom: 16,
  },
  learnMoreText: {
    color: '#3b82f6',
    fontSize: 14,
    textDecorationLine: 'underline',
  },
  
  // Disclaimer
  disclaimer: {
    color: '#6b7280',
    fontSize: 12,
    textAlign: 'center',
    lineHeight: 16,
  },
});