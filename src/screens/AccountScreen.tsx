import * as React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  Pressable,
  Image,
  ActivityIndicator,
  ImageBackground,
} from 'react-native';
import SwipeNavigationWrapper from '@/components/SwipeNavigationWrapper';
import Toast from '@/components/Toast';
import { signInWithEmail, signUpWithEmail, signInWithGoogle, signOut as supaSignOut } from '@/services/supabaseAuth';
import { useAuth } from '@/context/AuthContext';

export default function AccountScreen() {
  const { user, loading, refreshSession } = useAuth();
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [username, setUsername] = React.useState('');
  const [mode, setMode] = React.useState<'login' | 'signup'>('login');
  const [submitting, setSubmitting] = React.useState(false);
  
  // Toast state
  const [toastVisible, setToastVisible] = React.useState(false);
  const [toastMessage, setToastMessage] = React.useState('');
  const [toastType, setToastType] = React.useState<'success' | 'error' | 'info'>('success');

  const showToast = (message: string, type: 'success' | 'error' | 'info' = 'success') => {
    setToastMessage(message);
    setToastType(type);
    setToastVisible(true);
  };

  const onLogin = async () => {
    if (!email.trim() || !password) {
      showToast('Please enter email and password', 'error');
      return;
    }
    try {
      setSubmitting(true);
      await signInWithEmail(email.trim(), password);
      await refreshSession();
      showToast('Signed in successfully! 🎉');
    } catch (err: any) {
      showToast(err?.message ?? 'Login failed. Please try again.', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  const onCreate = async () => {
    if (!email.trim() || !password) {
      showToast('Please enter email and password', 'error');
      return;
    }
    try {
      setSubmitting(true);
      await signUpWithEmail(email.trim(), password, username.trim() || undefined);
      await refreshSession();
      showToast('Account created! Check your email for confirmation.');
    } catch (err: any) {
      showToast(err?.message ?? 'Signup failed. Please try again.', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  const onGoogle = async () => {
    try {
      setSubmitting(true);
      await signInWithGoogle();
      await refreshSession();
      showToast('Signed in with Google! 🎉');
    } catch (err: any) {
      showToast(err?.message ?? 'Google Sign-In failed', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  const onForgot = () => showToast('Password reset flow coming soon!', 'info');
  
  const onLogout = async () => {
    try {
      setSubmitting(true);
      await supaSignOut();
      await refreshSession();
      showToast('Signed out successfully');
    } catch (err: any) {
      showToast(err?.message ?? 'Sign out failed', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  const isAuthed = !!user;
  const primaryAction = mode === 'login' ? onLogin : onCreate;
  const primaryLabel = mode === 'login' ? 'Log in' : 'Create account';

  return (
    <SwipeNavigationWrapper currentTab="Account">
      <Toast 
        visible={toastVisible}
        message={toastMessage}
        type={toastType}
        onHide={() => setToastVisible(false)}
      />
      <ImageBackground
        source={require('../public/images/nature_collection_31_20250803_185135.png')}
        style={styles.backgroundImage}
        imageStyle={styles.imageStyle}
      >
        <View style={styles.overlay}>
      <View style={styles.screen}>
        <Text style={styles.sectionHeader}>Account Settings</Text>
        <Text style={styles.sectionDescription}>Manage your profile and application preferences</Text>
      
      <View style={styles.card}>
        <View style={styles.avatarRow}>
          <Image
            source={{ uri: 'https://avatars.githubusercontent.com/u/9919?s=80&v=4' }}
            style={styles.avatar}
          />
          <View style={{ flex: 1 }}>
            <Text style={styles.cardTitle}>{isAuthed ? 'Signed in' : 'Welcome'}</Text>
            <Text style={styles.cardSubtitle}>
              {isAuthed ? user?.email : 'Sign in to sync your data'}
            </Text>
          </View>
        </View>

        {loading ? (
          <ActivityIndicator color="#3b82f6" />
        ) : isAuthed ? (
          <View style={{ gap: 10 }}>
            <Text style={styles.label}>You are signed in.</Text>
            <Pressable onPress={onLogout} style={[styles.button, { marginTop: 200 }]}>
              <Text style={styles.buttonText}>Sign out</Text>
            </Pressable>
          </View>
        ) : (
          <View style={{ gap: 10 }}>
            {mode === 'signup' && (
              <>
                <Text style={styles.label}>Username (optional)</Text>
                <TextInput
                  value={username}
                  onChangeText={setUsername}
                  placeholder="username"
                  placeholderTextColor="#7a8fb2"
                  autoCapitalize="none"
                  style={styles.input}
                />
              </>
            )}

            <Text style={styles.label}>Email</Text>
            <TextInput
              value={email}
              onChangeText={setEmail}
              placeholder="you@example.com"
              placeholderTextColor="#7a8fb2"
              keyboardType="email-address"
              autoCapitalize="none"
              style={styles.input}
            />

            <Text style={styles.label}>Password</Text>
            <TextInput
              value={password}
              onChangeText={setPassword}
              placeholder="••••••••"
              placeholderTextColor="#7a8fb2"
              secureTextEntry
              style={styles.input}
            />

            <Pressable onPress={onForgot} style={styles.linkBtn}>
              <Text style={styles.linkText}>Forgot password?</Text>
            </Pressable>

            <Pressable
              onPress={primaryAction}
              style={[styles.button, submitting && styles.disabledButton]}
              disabled={submitting}
            >
              {submitting ? <ActivityIndicator color="#fff" /> : <Text style={styles.buttonText}>{primaryLabel}</Text>}
            </Pressable>

            <View style={styles.hr} />

            <Pressable onPress={onGoogle} style={[styles.button, styles.googleBtn]} disabled={submitting}>
              {submitting ? <ActivityIndicator color="#fff" /> : <Text style={styles.buttonText}>Continue with Google</Text>}
            </Pressable>

            <Pressable onPress={() => setMode(mode === 'login' ? 'signup' : 'login')} style={styles.linkBtn}>
              <Text style={styles.linkText}>
                {mode === 'login' ? 'Need an account? Sign up' : 'Have an account? Log in'}
              </Text>
            </Pressable>
          </View>
        )}
      </View>
    </View>
        </View>
      </ImageBackground>
    </SwipeNavigationWrapper>
  );
}

const styles = StyleSheet.create({
  backgroundImage: { flex: 1 },
  imageStyle: { opacity: 0.8 },
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(10, 14, 39, 0.15)',
  },
  screen: { flex: 1, paddingHorizontal: 20, paddingVertical: 20 },
  title: { color: 'white', fontSize: 24, fontWeight: '700', marginBottom: 20, textAlign: 'center' },
  card: { flex: 1, backgroundColor: 'rgba(44, 50, 88, 0.45)', borderRadius: 12, padding: 20, gap: 16, marginHorizontal: 8 },
  avatarRow: { flexDirection: 'row', alignItems: 'center', gap: 16, marginBottom: 8, paddingVertical: 8 },
  avatar: { width: 60, height: 60, borderRadius: 30, backgroundColor: '#0f1930' },
  cardTitle: { color: 'white', backgroundColor: 'rgba(44, 50, 88, 0.45)', fontWeight: '700', fontSize: 18 },
  cardSubtitle: { color: '#9bb4da', backgroundColor: 'rgba(3, 4, 8, 0.45)', fontSize: 14, marginTop: 2 },
  label: { color: '#a9c1ea', backgroundColor: 'rgba(3, 4, 8, 0.45)', fontSize: 13, fontWeight: '600', marginTop: 4, marginBottom: 6 },
  input: {
    height: 48,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#223459',
    color: 'white',
    paddingHorizontal: 16,
    backgroundColor: '#0f1930',
    marginBottom: 4,
  },
  button: {
    backgroundColor: '#0e64eeff',
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: 'center',
    marginVertical: 4,
    minHeight: 44,
  },
  googleBtn: { backgroundColor: '#f02310ff' },
  disabledButton: { opacity: 0.6 },
  buttonText: { color: 'white', fontWeight: '700' },
  linkBtn: { alignSelf: 'flex-end', paddingVertical: 8, paddingHorizontal: 4 },
  linkText: { color: '#7da0d6', backgroundColor: 'rgba(3, 4, 8, 0.45)', fontWeight: '600' },
  hr: { height: 1, backgroundColor: '#223459', marginVertical: 10, opacity: 0.6 },
  sectionHeader: {
    color: '#9fb3c8',
    backgroundColor: 'rgba(3, 4, 8, 0.45)',
    fontSize: 20,
    fontWeight: '700',
    marginBottom: 8,
    textAlign: 'center',
  },
  sectionDescription: {
    color: '#edf5ebff',
    backgroundColor: 'rgba(3, 4, 8, 0.45)',
    fontSize: 14,
    marginBottom: 20,
    textAlign: 'center',
    lineHeight: 18,
  },
});
