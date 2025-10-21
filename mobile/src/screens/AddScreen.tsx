import * as React from 'react';
import { View, Text, TextInput, Pressable, Alert, StyleSheet } from 'react-native';
import Spacer from '@/components/Spacer';

export default function AddScreen() {
  const [amount, setAmount] = React.useState('');
  const [desc, setDesc] = React.useState('');
  const [type, setType] = React.useState<'expense' | 'income'>('expense');

  const onSave = () => {
    const value = parseFloat(amount);
    if (Number.isNaN(value) || value <= 0) {
      Alert.alert('Invalid amount', 'Please enter a positive number.');
      return;
    }
    if (!desc.trim()) {
      Alert.alert('Missing description', 'Please add a short description.');
      return;
    }
    Alert.alert('Saved', `${type === 'expense' ? 'Expense' : 'Income'}: ${value.toFixed(2)}\n${desc}`);
    setAmount(''); setDesc(''); setType('expense');
  };

  return (
    <View style={styles.screen}>
      <Text style={styles.title}>Add Entry</Text>
      <View style={styles.card}>
        <Text style={styles.label}>Type</Text>
        <View style={{ flexDirection: 'row', marginTop: 8 }}>
          <Pressable onPress={() => setType('expense')}
            style={[styles.segment, type === 'expense' && styles.segmentActive]}>
            <Text style={styles.segmentText}>Expense</Text>
          </Pressable>
          <View style={{ width: 8 }} />
          <Pressable onPress={() => setType('income')}
            style={[styles.segment, type === 'income' && styles.segmentActive]}>
            <Text style={styles.segmentText}>Income</Text>
          </Pressable>
        </View>

        <Spacer />

        <Text style={styles.label}>Amount</Text>
        <TextInput
          value={amount}
          onChangeText={setAmount}
          placeholder="0.00"
          placeholderTextColor="#7a8fb2"
          keyboardType="decimal-pad"
          style={styles.input}
        />

        <Spacer />

        <Text style={styles.label}>Description</Text>
        <TextInput
          value={desc}
          onChangeText={setDesc}
          placeholder="e.g. Groceries, Salary"
          placeholderTextColor="#7a8fb2"
          style={styles.input}
        />

        <Spacer h={16} />

        <Pressable style={styles.save} onPress={onSave}>
          <Text style={styles.saveText}>Save</Text>
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, padding: 16, backgroundColor: '#0b1220' },
  title: { color: 'white', fontSize: 24, fontWeight: '700', marginBottom: 12 },
  card: { backgroundColor: '#111a30', borderRadius: 12, padding: 16 },
  label: { color: '#a9c1ea', fontSize: 13, fontWeight: '600' },
  input: {
    height: 44, borderRadius: 10, borderWidth: 1, borderColor: '#223459',
    color: 'white', paddingHorizontal: 12, backgroundColor: '#0f1930', marginTop: 8
  },
  segment: {
    flex: 1, paddingVertical: 10, borderRadius: 10, borderWidth: 1, borderColor: '#223459',
    alignItems: 'center', backgroundColor: '#0f1930'
  },
  segmentActive: { backgroundColor: '#1e40af', borderColor: '#1e40af' },
  segmentText: { color: 'white', fontWeight: '600' },
  save: { backgroundColor: '#3b82f6', paddingVertical: 12, borderRadius: 10, alignItems: 'center' },
  saveText: { color: 'white', fontWeight: '700' }
});
