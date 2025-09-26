import * as React from 'react';
import { View, Text, Pressable, Alert, StyleSheet } from 'react-native';
import Spacer from '@/components/Spacer';

export default function HomeScreen() {
  return (
    <View style={styles.screen}>
      <Text style={styles.title}>Home (Dashboard)</Text>
      <View style={styles.card}>
        <Text style={styles.body}>Month-to-date total, category snapshot, quick actions.</Text>
        <Spacer />
        <Pressable style={styles.button}
          onPress={() => Alert.alert('Coming soon', 'Bank connection flow TBD')}>
          <Text style={styles.buttonText}>Connect Bank</Text>
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, padding: 16, backgroundColor: '#0b1220' },
  title: { color: 'white', fontSize: 24, fontWeight: '700', marginBottom: 12 },
  card: { flex: 1, backgroundColor: '#111a30', borderRadius: 12, padding: 16 },
  body: { color: '#cfe1ff' },
  button: { backgroundColor: '#3b82f6', paddingVertical: 12, borderRadius: 10, alignItems: 'center', marginTop: 12 },
  buttonText: { color: 'white', fontWeight: '700' }
});
