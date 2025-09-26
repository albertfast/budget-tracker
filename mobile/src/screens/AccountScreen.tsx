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
    <View style={styles.screen}>
      <Text style={styles.title}>Account</Text>
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
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, padding: 16, backgroundColor: '#0b1220' },
  title: { color: 'white', fontSize: 24, fontWeight: '700', marginBottom: 12 },
  card: { flex: 1, backgroundColor: '#111a30', borderRadius: 12, padding: 16, gap: 14 },
  avatarRow: { flexDirection: 'row', alignItems: 'center', gap: 12, marginBottom: 4 },
  avatar: { width: 56, height: 56, borderRadius: 28, backgroundColor: '#0f1930' },
  cardTitle: { color: 'white', fontWeight: '700', fontSize: 16 },
  cardSubtitle: { color: '#9bb4da', fontSize: 12 },
  label: { color: '#a9c1ea', fontSize: 13, fontWeight: '600' },
  input: {
    height: 44,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#223459',
    color: 'white',
    paddingHorizontal: 12,
    backgroundColor: '#0f1930',
  },
  button: {
    backgroundColor: '#3b82f6',
    paddingVertical: 12,
    borderRadius: 10,
    alignItems: 'center',
  },
  googleBtn: { backgroundColor: '#ea4335' },
  buttonText: { color: 'white', fontWeight: '700' },
  linkBtn: { alignSelf: 'flex-end' },
  linkText: { color: '#7da0d6', fontWeight: '600' },
  hr: { height: 1, backgroundColor: '#223459', marginVertical: 10, opacity: 0.6 },
});
