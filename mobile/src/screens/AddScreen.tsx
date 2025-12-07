import * as React from 'react';
import { View, Text, TextInput, Pressable, Alert, StyleSheet, ActivityIndicator } from 'react-native';
import SwipeNavigationWrapper from '@/components/SwipeNavigationWrapper';
import Spacer from '@/components/Spacer';
import { insertFinancialRecord } from '@/services/financialDataService';

export default function AddScreen() {
  const [amount, setAmount] = React.useState('');
  const [desc, setDesc] = React.useState('');
  const [type, setType] = React.useState<'expense' | 'income'>('expense');
  const [transactionId, setTransactionId] = React.useState('');
  const [merchant, setMerchant] = React.useState('');
  const [loading, setLoading] = React.useState(false);

  const onSave = async () => {
    const value = parseFloat(amount);
    if (Number.isNaN(value) || value <= 0) {
      Alert.alert('Invalid amount', 'Please enter a positive number.');
      return;
    }

    setLoading(true);
    try {
      await insertFinancialRecord({
        category: type === 'expense' ? 'Expense' : 'Income',
        amount: value,
        currency: 'USD',
        occurred_on: new Date().toISOString(),
        merchant: merchant || undefined,
        memo: desc || undefined,
        source: 'manual'
      });

      Alert.alert('Success', 'Transaction saved successfully');
      setAmount(''); 
      setDesc(''); 
      setType('expense');
      setTransactionId('');
      setMerchant('');
    } catch (error: any) {
      Alert.alert('Error', error.message || 'Failed to save transaction');
    } finally {
      setLoading(false);
    }
  };

  return (
    <SwipeNavigationWrapper currentTab="Add">
      <View style={styles.screen}>
        <Text style={styles.sectionHeader}>Quick Entry</Text>
        <Text style={styles.sectionDescription}>Add new transactions and financial entries</Text>
      
      <View style={styles.card}>
        <Text style={styles.label}>Type</Text>
        <View style={{ flexDirection: 'row', marginTop: 12, marginBottom: 8, gap: 12 }}>
          <Pressable onPress={() => setType('expense')}
            style={[styles.segment, type === 'expense' && styles.segmentActive]}>
            <Text style={styles.segmentText}>Expense</Text>
          </Pressable>
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

        <Text style={styles.label}>📝 Description (Optional)</Text>
        <TextInput
          value={desc}
          onChangeText={setDesc}
          placeholder="e.g. Groceries, Salary, Gas (optional)"
          placeholderTextColor="#7a8fb2"
          style={styles.input}
        />

        {type === 'expense' && (
          <>
            <View style={styles.sectionDivider}>
              <View style={styles.dividerLine} />
              <Text style={styles.dividerText}>Expense Details</Text>
              <View style={styles.dividerLine} />
            </View>
            
            <Text style={styles.label}>🏪 Merchant (Optional)</Text>
            <TextInput
              value={merchant}
              onChangeText={setMerchant}
              placeholder="e.g. Walmart, Target, Amazon"
              placeholderTextColor="#7a8fb2"
              style={styles.input}
              autoCapitalize="words"
            />

            <Spacer />
            
            <Text style={styles.label}>🔢 Transaction ID (Optional)</Text>
            <TextInput
              value={transactionId}
              onChangeText={setTransactionId}
              placeholder="e.g. TXN123456789"
              placeholderTextColor="#7a8fb2"
              style={styles.input}
              autoCapitalize="characters"
            />
          </>
        )}

        <Spacer h={16} />

        <Pressable style={[styles.save, loading && { opacity: 0.7 }]} onPress={onSave} disabled={loading}>
          {loading ? (
            <ActivityIndicator color="white" />
          ) : (
            <Text style={styles.saveText}>Save</Text>
          )}
        </Pressable>
      </View>
    </View>
    </SwipeNavigationWrapper>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, paddingHorizontal: 20, paddingVertical: 20, backgroundColor: '#0b1220' },
  title: { color: 'white', fontSize: 24, fontWeight: '700', marginBottom: 20, textAlign: 'center' },
  card: { backgroundColor: '#111a30', borderRadius: 12, padding: 20, marginHorizontal: 8 },
  label: { color: '#a9c1ea', fontSize: 13, fontWeight: '600', marginTop: 4 },
  input: {
    height: 48, borderRadius: 10, borderWidth: 1, borderColor: '#223459',
    color: 'white', paddingHorizontal: 16, backgroundColor: '#0f1930', marginTop: 12, marginBottom: 4
  },
  segment: {
    flex: 1, paddingVertical: 12, borderRadius: 10, borderWidth: 1, borderColor: '#223459',
    alignItems: 'center', backgroundColor: '#0f1930', minHeight: 44
  },
  segmentActive: { backgroundColor: '#1e40af', borderColor: '#1e40af' },
  segmentText: { color: 'white', fontWeight: '600' },
  save: { backgroundColor: '#3b82f6', paddingVertical: 14, borderRadius: 10, alignItems: 'center', marginTop: 8 },
  saveText: { color: 'white', fontWeight: '700' },
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
  sectionDivider: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 20,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: '#223459',
  },
  dividerText: {
    color: '#7a8fa5',
    fontSize: 12,
    fontWeight: '600',
    marginHorizontal: 12,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
});
