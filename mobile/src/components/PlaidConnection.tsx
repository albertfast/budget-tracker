import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ActivityIndicator,
  Alert,
  Platform,
  TouchableOpacity
} from 'react-native';
import { create, open, LinkSuccess, LinkExit, LinkEvent } from 'react-native-plaid-link-sdk';
import { makeAuthenticatedRequest, authService } from '../services/authService';

interface PlaidConnectionProps {
  onSuccess: (publicToken: string, metadata: any) => void;
  onError: (error: any) => void;
}

// TODO: Move this to an environment variable or config file
// For physical device testing, use your computer's LAN IP (e.g., 192.168.1.223)
const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://192.168.1.223:8001';

export default function PlaidConnection({ onSuccess, onError }: PlaidConnectionProps) {
  const [linkToken, setLinkToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    createLinkToken();
  }, []);

  const createLinkToken = async () => {
    setLoading(true);
    setError(null);

    try {
      // Ensure user is authenticated
      if (!authService.isAuthenticated()) {
        // For demo purposes, we might need to handle this better
        console.warn('User not authenticated for Plaid Link');
      }

      console.log('[Plaid] Creating link token...');
      const response = await makeAuthenticatedRequest(`${API_BASE_URL}/api/banks/link/create-token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
      });

      if (response.ok) {
        const data = await response.json();
        console.log('[Plaid] Link token created:', data.link_token);
        setLinkToken(data.link_token);
        
        // Initialize Plaid Link with the token
        create({
          token: data.link_token,
          noLoadingState: false,
        });
      } else {
        const errorText = await response.text();
        console.error('[Plaid] Failed to create link token:', errorText);
        throw new Error(`Failed to create link token: ${response.status}`);
      }
    } catch (err: any) {
      setError('Failed to initialize Plaid Link. Please check your network connection.');
      console.error('[Plaid] Link token creation error:', err);
      onError(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#008080" />
        <Text style={styles.text}>Initializing Secure Connection...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>{error}</Text>
        <TouchableOpacity onPress={createLinkToken} style={styles.retryButton}>
          <Text style={styles.retryText}>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

  if (!linkToken) {
    return null;
  }

  return (
    <TouchableOpacity
      style={styles.button}
      onPress={() => {
        open({
          onSuccess: (success: LinkSuccess) => {
            console.log('[Plaid] Success:', success);
            onSuccess(success.publicToken, success.metadata);
          },
          onExit: (exit: LinkExit) => {
            console.log('[Plaid] Exit:', exit);
            if (exit.error) {
              onError(exit.error);
            }
          },
        });
      }}
    >
      <Text style={styles.buttonText}>Connect Bank Account</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
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
  errorText: {
    color: 'red',
    marginBottom: 10,
    textAlign: 'center',
  },
  retryButton: {
    padding: 10,
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
  },
  retryText: {
    color: '#333',
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
