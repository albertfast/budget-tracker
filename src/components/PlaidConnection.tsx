import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ActivityIndicator,
  Alert,
  Platform,
  TouchableOpacity,
  Animated,
  Easing,
} from 'react-native';
import { create, open, LinkSuccess, LinkExit, LinkEvent } from 'react-native-plaid-link-sdk';
import { makeAuthenticatedRequest, authService } from '../services/authService';
import { useAuth } from '../context/AuthContext';
import { syncPlaidTransactions, savePlaidTransactionsToSupabase } from '../services/plaidTransactionService';
import axios from 'axios';

interface PlaidConnectionProps {
  onSuccess: (publicToken: string, metadata: any) => void;
  onError: (error: any) => void;
}

// Get the correct API URL for Expo Go
// When running in Expo Go on a physical device, we need the LAN IP
// When running in a simulator/emulator, we can use localhost
const getApiBaseUrl = () => {
  // For Expo Go on physical device, always use LAN IP
  // The EXPO_PUBLIC_API_URL with 'backend:8001' won't work from phone
  const envUrl = process.env.EXPO_PUBLIC_API_URL;
  
  // If env URL contains 'backend:' (Docker internal), replace with LAN IP
  if (envUrl && envUrl.includes('backend:')) {
    return 'http://10.0.0.214:8001';
  }
  
  return envUrl || 'http://10.0.0.214:8001';
};

const API_BASE_URL = getApiBaseUrl();

export default function PlaidConnection({ onSuccess, onError }: PlaidConnectionProps) {
  const { user } = useAuth();
  const [linkToken, setLinkToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Animation values
  const spinValue = useRef(new Animated.Value(0)).current;
  const pulseValue = useRef(new Animated.Value(1)).current;
  const floatValue1 = useRef(new Animated.Value(0)).current;
  const floatValue2 = useRef(new Animated.Value(0)).current;
  const floatValue3 = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (loading) {
      // Spinning animation
      Animated.loop(
        Animated.timing(spinValue, {
          toValue: 1,
          duration: 2000,
          easing: Easing.linear,
          useNativeDriver: true,
        })
      ).start();

      // Pulse animation
      Animated.loop(
        Animated.sequence([
          Animated.timing(pulseValue, {
            toValue: 1.2,
            duration: 800,
            easing: Easing.inOut(Easing.ease),
            useNativeDriver: true,
          }),
          Animated.timing(pulseValue, {
            toValue: 1,
            duration: 800,
            easing: Easing.inOut(Easing.ease),
            useNativeDriver: true,
          }),
        ])
      ).start();

      // Floating animations for particles
      [floatValue1, floatValue2, floatValue3].forEach((anim, index) => {
        Animated.loop(
          Animated.sequence([
            Animated.timing(anim, {
              toValue: 1,
              duration: 2000 + index * 500,
              easing: Easing.inOut(Easing.ease),
              useNativeDriver: true,
            }),
            Animated.timing(anim, {
              toValue: 0,
              duration: 2000 + index * 500,
              easing: Easing.inOut(Easing.ease),
              useNativeDriver: true,
            }),
          ])
        ).start();
      });
    }
  }, [loading]);

  useEffect(() => {
    if (user?.email) {
      createSandboxTokenAndInitialize();
    }
  }, [user]);

  const createSandboxTokenAndInitialize = async () => {
    setLoading(true);
    setError(null);

    try {
      if (!user?.email) {
        throw new Error('User email not available. Please log in again.');
      }

      console.log('[Plaid] Creating sandbox public token for user:', user.email);
      console.log('[Plaid] Using backend URL:', API_BASE_URL);

      // Check if this is a custom user (contains "custom" in email)
      const isCustomUser = user.email.toLowerCase().includes('custom');
      
      let sandboxResponse;
      
      if (isCustomUser) {
        // Use custom user config for richer test data
        console.log('[Plaid] Creating CUSTOM sandbox user with rich data');
        
        const customConfig = {
          seed: `custom-${Date.now()}`,
          override_accounts: [
            {
              type: "depository",
              subtype: "checking",
              starting_balance: 5000,
              transactions: [
                {
                  date_transacted: "2023-10-01",
                  date_posted: "2023-10-03",
                  amount: 100,
                  description: "1 year Netflix subscription",
                  currency: "USD"
                },
                {
                  date_transacted: "2023-10-01",
                  date_posted: "2023-10-02",
                  amount: 100,
                  description: "1 year mobile subscription",
                  currency: "USD"
                },
                {
                  date_transacted: "2023-09-15",
                  date_posted: "2023-09-16",
                  amount: 50,
                  description: "Grocery Store",
                  currency: "USD"
                },
                {
                  date_transacted: "2023-09-10",
                  date_posted: "2023-09-11",
                  amount: 200,
                  description: "Electric Company",
                  currency: "USD"
                }
              ]
            },
            {
              type: "credit",
              subtype: "credit card",
              starting_balance: 2000
            }
          ]
        };
        
        sandboxResponse = await fetch(`${API_BASE_URL}/api/plaid/sandbox/public_token`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            email: user.email,
            password: 'abc123',
            institution_id: 'ins_109508',
            custom_user_config: customConfig
          })
        });
      } else {
        // Standard user
        sandboxResponse = await fetch(`${API_BASE_URL}/api/plaid/sandbox/public_token`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            email: user.email,
            password: 'abc123',
            institution_id: 'ins_109508'
          })
        });
      }

      if (!sandboxResponse.ok) {
        const errorText = await sandboxResponse.text();
        console.error('[Plaid] Sandbox token error:', errorText);
        throw new Error(`Sandbox token creation failed: ${sandboxResponse.status}`);
      }

      const sandboxData = await sandboxResponse.json();
      console.log('[Plaid] Sandbox public_token created:', sandboxData.public_token);

      // Step 2: Exchange the public token for access token
      const exchangeResponse = await fetch(`${API_BASE_URL}/api/plaid/exchange-token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          public_token: sandboxData.public_token
        })
      });

      if (!exchangeResponse.ok) {
        const errorText = await exchangeResponse.text();
        console.error('[Plaid] Exchange token error:', errorText);
        throw new Error(`Token exchange failed: ${exchangeResponse.status}`);
      }

      const exchangeData = await exchangeResponse.json();
      console.log('[Plaid] Access token received:', exchangeData.access_token?.substring(0, 10) + '...');

      // Step 3: Get accounts with the access token
      const accountsResponse = await fetch(`${API_BASE_URL}/api/plaid/accounts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          access_token: exchangeData.access_token
        })
      });

      if (!accountsResponse.ok) {
        const errorText = await accountsResponse.text();
        console.error('[Plaid] Accounts fetch error:', errorText);
        throw new Error(`Accounts fetch failed: ${accountsResponse.status}`);
      }

      const accountsData = await accountsResponse.json();
      console.log('[Plaid] Accounts received:', accountsData.accounts?.length || 0);

      // Simulate success callback with the public token and metadata
      onSuccess(sandboxData.public_token, {
        institution: {
          name: 'Plaid Sandbox Bank',
          institution_id: 'ins_109508'
        },
        accounts: accountsData.accounts || [],
        link_session_id: sandboxData.request_id
      });

      setLoading(false);
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to initialize Plaid connection.';
      setError(errorMessage);
      console.error('[Plaid] Connection error:', err);
      onError(err);
      setLoading(false);
    }
  };

  if (loading) {
    const spin = spinValue.interpolate({
      inputRange: [0, 1],
      outputRange: ['0deg', '360deg'],
    });

    const float1 = floatValue1.interpolate({
      inputRange: [0, 1],
      outputRange: [-20, -60],
    });

    const float2 = floatValue2.interpolate({
      inputRange: [0, 1],
      outputRange: [-10, -70],
    });

    const float3 = floatValue3.interpolate({
      inputRange: [0, 1],
      outputRange: [-15, -80],
    });

    return (
      <View style={styles.loadingContainer}>
        {/* Floating particles */}
        <Animated.Text style={[styles.particle, styles.particle1, { transform: [{ translateY: float1 }] }]}>
          💰
        </Animated.Text>
        <Animated.Text style={[styles.particle, styles.particle2, { transform: [{ translateY: float2 }] }]}>
          🌿
        </Animated.Text>
        <Animated.Text style={[styles.particle, styles.particle3, { transform: [{ translateY: float3 }] }]}>
          ⚙️
        </Animated.Text>
        
        {/* Main spinner */}
        <Animated.View style={[styles.spinnerContainer, { transform: [{ scale: pulseValue }] }]}>
          <Animated.View style={[styles.spinner, { transform: [{ rotate: spin }] }]}>
            <Text style={styles.spinnerText}>🔐</Text>
          </Animated.View>
        </Animated.View>
        
        <Text style={styles.loadingText}>Connecting to Plaid Sandbox...</Text>
        <Text style={styles.loadingSubtext}>Authenticating with your credentials</Text>
        
        <View style={styles.dotsContainer}>
          <Animated.View style={[styles.dot, { opacity: pulseValue }]} />
          <Animated.View style={[styles.dot, { opacity: pulseValue }]} />
          <Animated.View style={[styles.dot, { opacity: pulseValue }]} />
        </View>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>{error}</Text>
        <TouchableOpacity onPress={createSandboxTokenAndInitialize} style={styles.retryButton}>
          <Text style={styles.retryText}>Retry Connection</Text>
        </TouchableOpacity>
      </View>
    );
  }

  // Show connect button when ready
  return (
    <TouchableOpacity
      style={styles.button}
      onPress={createSandboxTokenAndInitialize}
    >
      <Text style={styles.buttonText}>Connect Bank Account</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  loadingContainer: {
    padding: 40,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 300,
    position: 'relative',
  },
  spinnerContainer: {
    marginBottom: 20,
  },
  spinner: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: 'rgba(0, 128, 128, 0.1)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  spinnerText: {
    fontSize: 40,
  },
  particle: {
    position: 'absolute',
    fontSize: 24,
    opacity: 0.6,
  },
  particle1: {
    left: '20%',
    top: 60,
  },
  particle2: {
    right: '20%',
    top: 80,
  },
  particle3: {
    left: '50%',
    top: 70,
  },
  loadingText: {
    marginTop: 20,
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
  },
  loadingSubtext: {
    marginTop: 8,
    color: '#9fb3c8',
    fontSize: 14,
  },
  dotsContainer: {
    flexDirection: 'row',
    gap: 8,
    marginTop: 16,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#008080',
  },
  container: {
    padding: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  text: {
    marginTop: 10,
    color: '#666',
    fontSize: 16,
  },
  subtext: {
    marginTop: 5,
    color: '#999',
    fontSize: 14,
  },
  errorText: {
    color: '#ef4444',
    marginBottom: 10,
    textAlign: 'center',
    fontSize: 16,
  },
  retryButton: {
    padding: 12,
    backgroundColor: '#1e40af',
    borderRadius: 10,
  },
  retryText: {
    color: '#fff',
    fontWeight: '600',
  },
  button: {
    backgroundColor: '#008080',
    paddingVertical: 16,
    paddingHorizontal: 32,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
  },
});
