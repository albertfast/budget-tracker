import * as React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  Pressable,
  Image,
  Alert,
} from 'react-native';
import SwipeNavigationWrapper from '@/components/SwipeNavigationWrapper';

export default function AccountScreen() {
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');

  const onLogin = () => {
    if (!email.trim() || !password) {
      Alert.alert('Missing info', 'Please enter email and password.');
      return;
    }
    // TODO: connect to backend auth
    Alert.alert('Login', `Email: ${email}`);
  };

  const onForgot = () => Alert.alert('Forgot password', 'Password reset flow TBD');
  const onCreate = () => Alert.alert('Create account', 'Account creation flow TBD');
  const onGoogle = () => Alert.alert('Google Sign-In', 'Google auth flow TBD');

  return (
    <SwipeNavigationWrapper currentTab="Account">
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
            <Text style={styles.cardTitle}>Welcome</Text>
            <Text style={styles.cardSubtitle}>Sign in to sync your data</Text>
          </View>
        </View>

        <View style={{ gap: 10 }}>
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

          <Pressable onPress={onLogin} style={[styles.button, { marginTop: 4 }]}>
            <Text style={styles.buttonText}>Log in</Text>
          </Pressable>

          <View style={styles.hr} />

          <Pressable onPress={onGoogle} style={[styles.button, styles.googleBtn]}>
            <Text style={styles.buttonText}>Continue with Google</Text>
          </Pressable>

          <Pressable onPress={onCreate} style={styles.linkBtn}>
            <Text style={styles.linkText}>Create an account</Text>
          </Pressable>
        </View>
      </View>
    </View>
    </SwipeNavigationWrapper>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, paddingHorizontal: 20, paddingVertical: 20, backgroundColor: '#0b1220' },
  title: { color: 'white', fontSize: 24, fontWeight: '700', marginBottom: 20, textAlign: 'center' },
  card: { flex: 1, backgroundColor: '#111a30', borderRadius: 12, padding: 20, gap: 16, marginHorizontal: 8 },
  avatarRow: { flexDirection: 'row', alignItems: 'center', gap: 16, marginBottom: 8, paddingVertical: 8 },
  avatar: { width: 60, height: 60, borderRadius: 30, backgroundColor: '#0f1930' },
  cardTitle: { color: 'white', fontWeight: '700', fontSize: 18 },
  cardSubtitle: { color: '#9bb4da', fontSize: 14, marginTop: 2 },
  label: { color: '#a9c1ea', fontSize: 13, fontWeight: '600', marginTop: 4, marginBottom: 6 },
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
    backgroundColor: '#3b82f6',
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: 'center',
    marginVertical: 4,
    minHeight: 44,
  },
  googleBtn: { backgroundColor: '#ea4335' },
  buttonText: { color: 'white', fontWeight: '700' },
  linkBtn: { alignSelf: 'flex-end', paddingVertical: 8, paddingHorizontal: 4 },
  linkText: { color: '#7da0d6', fontWeight: '600' },
  hr: { height: 1, backgroundColor: '#223459', marginVertical: 10, opacity: 0.6 },
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
});
