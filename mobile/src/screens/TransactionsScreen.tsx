import * as React from 'react';
import { View, Text, StyleSheet, TextInput, Pressable } from 'react-native';

const CATEGORIES = ['Food', 'Transport', 'Bills', 'Shopping', 'Fun', 'Other'];

export default function TransactionsScreen() {
  const [amount, setAmount] = React.useState('');
  const [desc, setDesc] = React.useState('');
  const [category, setCategory] = React.useState('Food');
  const [items, setItems] = React.useState<{ amount: number; category: string }[]>([]);

  const onAdd = () => {
    const value = parseFloat(amount);
    if (Number.isNaN(value) || value <= 0) return;
    setItems((prev) => [...prev, { amount: value, category }]);
    setAmount('');
    setDesc('');
  };

  const totals = React.useMemo(() => {
    const map: Record<string, number> = {};
    for (const c of CATEGORIES) map[c] = 0;
    for (const it of items) map[it.category] += it.amount;
    return map;
  }, [items]);

  const maxVal = Math.max(1, ...Object.values(totals));

  return (
    <View style={styles.screen}>
      <Text style={styles.title}>Transactions</Text>
      <View style={styles.card}>
        <View style={{ gap: 10 }}>
          <Text style={styles.label}>Amount</Text>
          <TextInput
            value={amount}
            onChangeText={setAmount}
            placeholder="0.00"
            placeholderTextColor="#7a8fb2"
            keyboardType="decimal-pad"
            style={styles.input}
          />

          <Text style={styles.label}>Description</Text>
          <TextInput
            value={desc}
            onChangeText={setDesc}
            placeholder="e.g. Coffee"
            placeholderTextColor="#7a8fb2"
            style={styles.input}
          />

          <Text style={styles.label}>Category</Text>
          <View style={styles.pickerRow}>
            {CATEGORIES.map((c) => (
              <Pressable
                key={c}
                onPress={() => setCategory(c)}
                style={[styles.pill, category === c && styles.pillActive]}
              >
                <Text style={styles.pillText}>{c}</Text>
              </Pressable>
            ))}
          </View>

          <Pressable onPress={onAdd} style={[styles.button, { marginTop: 6 }]}>
            <Text style={styles.buttonText}>Add</Text>
          </Pressable>
        </View>

        <View style={styles.hr} />

        <Text style={styles.subTitle}>Spend by category</Text>
        <View style={{ gap: 8 }}>
          {CATEGORIES.map((c) => {
            const val = totals[c] || 0;
            const pct = Math.max(0.05, val / maxVal);
            return (
              <View key={c} style={{ gap: 6 }}>
                <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
                  <Text style={styles.catName}>{c}</Text>
                  <Text style={styles.catVal}>{val.toFixed(2)}</Text>
                </View>
                <View style={styles.barTrack}>
                  <View style={[styles.barFill, { width: `${pct * 100}%` }]} />
                </View>
              </View>
            );
          })}
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, padding: 16, backgroundColor: '#0b1220' },
  title: { color: 'white', fontSize: 24, fontWeight: '700', marginBottom: 12 },
  subTitle: { color: 'white', fontSize: 16, fontWeight: '700', marginBottom: 8 },
  card: { flex: 1, backgroundColor: '#111a30', borderRadius: 12, padding: 16, gap: 12 },
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
  pickerRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  pill: {
    paddingHorizontal: 10,
    paddingVertical: 8,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#223459',
    backgroundColor: '#0f1930',
  },
  pillActive: { backgroundColor: '#1e40af', borderColor: '#1e40af' },
  pillText: { color: 'white', fontWeight: '600' },
  button: { backgroundColor: '#3b82f6', paddingVertical: 12, borderRadius: 10, alignItems: 'center' },
  buttonText: { color: 'white', fontWeight: '700' },
  hr: { height: 1, backgroundColor: '#223459', marginVertical: 10, opacity: 0.6 },
  catName: { color: '#cfe1ff' },
  catVal: { color: '#9bb4da' },
  barTrack: { height: 10, borderRadius: 6, backgroundColor: '#0f1930', overflow: 'hidden' },
  barFill: { height: 10, backgroundColor: '#3b82f6' },
});
