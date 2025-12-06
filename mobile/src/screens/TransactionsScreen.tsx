import * as React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  Pressable,
  Platform,
  FlatList,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import DateTimePicker, { AndroidNativeProps, DateTimePickerEvent } from '@react-native-community/datetimepicker';
import Svg, { Rect } from 'react-native-svg';
import SwipeNavigationWrapper from '@/components/SwipeNavigationWrapper';

const CATEGORIES = ['Food', 'Transport', 'Bills', 'Shopping', 'Fun', 'Other'];
const STORAGE_KEY = 'smartbudget:transactions:v1';

type Entry = {
  id: string;
  amount: number;
  category: string;
  desc?: string;
  date: string; // ISO YYYY-MM-DD
};

function formatISO(d: Date) {
  const y = d.getFullYear();
  const m = `${d.getMonth() + 1}`.padStart(2, '0');
  const day = `${d.getDate()}`.padStart(2, '0');
  return `${y}-${m}-${day}`;
}

export default function TransactionsScreen() {
  const [amount, setAmount] = React.useState('');
  const [desc, setDesc] = React.useState('');
  const [category, setCategory] = React.useState<string>('Food');
  const [date, setDate] = React.useState<Date>(new Date());
  const [showPicker, setShowPicker] = React.useState(false);
  const [editingId, setEditingId] = React.useState<string | null>(null);
  const [items, setItems] = React.useState<Entry[]>([]);

  // Load persisted transactions
  React.useEffect(() => {
    (async () => {
      try {
        const raw = await AsyncStorage.getItem(STORAGE_KEY);
        if (raw) {
          const parsed = JSON.parse(raw) as Entry[];
          setItems(parsed);
        }
      } catch (e) {
        // ignore
      }
    })();
  }, []);

  // Persist on changes
  React.useEffect(() => {
    AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(items)).catch(() => {});
  }, [items]);

  const onAddOrSave = () => {
    const value = parseFloat(amount);
    if (Number.isNaN(value) || value <= 0) return;
    const entry: Entry = {
      id: editingId ?? `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      amount: value,
      category,
      desc: desc?.trim() || undefined,
      date: formatISO(date),
    };
    setItems((prev) => {
      if (!editingId) return [...prev, entry];
      return prev.map((it) => (it.id === editingId ? entry : it));
    });
    setAmount('');
    setDesc('');
    setCategory('Food');
    setDate(new Date());
    setEditingId(null);
  };

  const startEdit = (it: Entry) => {
    setEditingId(it.id);
    setAmount(String(it.amount));
    setDesc(it.desc ?? '');
    setCategory(it.category);
    setDate(new Date(it.date));
  };

  const onDelete = (id: string) => {
    setItems((prev) => prev.filter((it) => it.id !== id));
    if (editingId === id) setEditingId(null);
  };

  const totals = React.useMemo(() => {
    const map: Record<string, number> = {};
    for (const c of CATEGORIES) map[c] = 0;
    for (const it of items) map[it.category] += it.amount;
    return map;
  }, [items]);

  const maxVal = Math.max(1, ...Object.values(totals));

  return (
    <SwipeNavigationWrapper currentTab="Transactions">
      <View style={styles.screen}>
        <Text style={styles.sectionHeader}>Transaction Management</Text>
        <Text style={styles.sectionDescription}>Add, edit, and track your financial transactions</Text>
      
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

          <Text style={styles.label}>Date</Text>
          {Platform.OS === 'web' ? (
            <TextInput
              value={formatISO(date)}
              onChangeText={(txt) => {
                // very light validation: YYYY-MM-DD
                const m = /^\d{4}-\d{2}-\d{2}$/.exec(txt);
                if (m) setDate(new Date(txt));
              }}
              placeholder="YYYY-MM-DD"
              placeholderTextColor="#7a8fb2"
              style={styles.input}
            />
          ) : (
            <View>
              <Pressable onPress={() => setShowPicker(true)} style={[styles.input, styles.dateButton] }>
                <Text style={{ color: 'white' }}>{formatISO(date)}</Text>
              </Pressable>
              {showPicker && (
                <DateTimePicker
                  value={date}
                  mode="date"
                  display={Platform.OS === 'ios' ? 'inline' : 'default'}
                  onChange={(evt: DateTimePickerEvent, selected) => {
                    if (Platform.OS === 'android') setShowPicker(false);
                    if (selected) setDate(selected);
                  }}
                />
              )}
            </View>
          )}

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

          <Pressable onPress={onAddOrSave} style={[styles.button, { marginTop: 6 }]}>
            <Text style={styles.buttonText}>{editingId ? 'Save' : 'Add'}</Text>
          </Pressable>
        </View>

        <View style={styles.hr} />

        <Text style={styles.subTitle}>Recent</Text>
        <FlatList
          data={[...items].reverse()}
          keyExtractor={(it) => it.id}
          style={{ maxHeight: 240 }}
          contentContainerStyle={{ paddingVertical: 8 }}
          ItemSeparatorComponent={() => <View style={{ height: 12 }} />}
          renderItem={({ item }) => (
            <View style={styles.row}>
              <View style={{ flex: 1 }}>
                <Text style={{ color: 'white', fontWeight: '700' }}>
                  {item.category} • {item.amount.toFixed(2)}
                </Text>
                <Text style={{ color: '#9bb4da' }}>
                  {item.date}{item.desc ? ` • ${item.desc}` : ''}
                </Text>
              </View>
              <View style={{ flexDirection: 'row', gap: 8 }}>
                <Pressable onPress={() => startEdit(item)} style={[styles.smallBtn, { backgroundColor: '#1e40af' }]}>
                  <Text style={styles.smallBtnText}>Edit</Text>
                </Pressable>
                <Pressable onPress={() => onDelete(item.id)} style={[styles.smallBtn, { backgroundColor: '#ef4444' }]}>
                  <Text style={styles.smallBtnText}>Del</Text>
                </Pressable>
              </View>
            </View>
          )}
        />

        <View style={styles.hr} />

        <Text style={styles.subTitle}>Spend by category</Text>
        <View style={{ gap: 10 }}>
          {/* SVG chart */}
          <View style={{ backgroundColor: '#0f1930', borderRadius: 10, padding: 20 }}>
            <Svg viewBox="0 0 100 70" width="100%" height={140}>
              {CATEGORIES.map((c, idx) => {
                const val = totals[c] || 0;
                const pct = Math.max(0, (val / maxVal) * 100);
                const y = idx * 10 + 2; // space between bars
                return (
                  <Rect key={c} x={0} y={y} width={pct} height={6} fill="#3b82f6" rx={2} />
                );
              })}
            </Svg>
            <View style={{ marginTop: 4, gap: 4 }}>
              {CATEGORIES.map((c) => (
                <View key={c} style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
                  <Text style={styles.catName}>{c}</Text>
                  <Text style={styles.catVal}>{(totals[c] || 0).toFixed(2)}</Text>
                </View>
              ))}
            </View>
          </View>
        </View>
      </View>
    </View>
    </SwipeNavigationWrapper>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, paddingHorizontal: 20, paddingVertical: 20, backgroundColor: '#0b1220' },
  title: { color: 'white', fontSize: 24, fontWeight: '700', marginBottom: 20, textAlign: 'center' },
  subTitle: { color: 'white', fontSize: 16, fontWeight: '700', marginBottom: 12, textAlign: 'center' },
  card: { flex: 1, backgroundColor: '#111a30', borderRadius: 12, padding: 20, gap: 16, marginHorizontal: 8 },
  label: { color: '#a9c1ea', fontSize: 13, fontWeight: '600' },
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
  dateButton: { justifyContent: 'center' },
  pickerRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 12, marginVertical: 8 },
  pill: {
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#223459',
    backgroundColor: '#0f1930',
    minWidth: 48,
    alignItems: 'center',
  },
  pillActive: { backgroundColor: '#1e40af', borderColor: '#1e40af' },
  pillText: { color: 'white', fontWeight: '600' },
  button: { backgroundColor: '#3b82f6', paddingVertical: 14, borderRadius: 10, alignItems: 'center', marginVertical: 8 },
  buttonText: { color: 'white', fontWeight: '700' },
  hr: { height: 1, backgroundColor: '#223459', marginVertical: 10, opacity: 0.6 },
  catName: { color: '#cfe1ff' },
  catVal: { color: '#9bb4da' },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#0f1930',
    borderRadius: 12,
    padding: 14,
    marginHorizontal: 4,
    marginVertical: 2,
  },
  smallBtn: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
    minWidth: 48,
    alignItems: 'center',
  },
  smallBtnText: { color: 'white', fontWeight: '700' },
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
