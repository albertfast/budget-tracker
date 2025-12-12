import * as React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  Pressable,
  Platform,
  FlatList,
  ScrollView,
  ImageBackground,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import DateTimePicker, { AndroidNativeProps, DateTimePickerEvent } from '@react-native-community/datetimepicker';
import Svg, { Rect } from 'react-native-svg';
import SwipeNavigationWrapper from '@/components/SwipeNavigationWrapper';
import { useAuth } from '@/context/AuthContext';
import { supabase } from '@/services/supabaseClient';

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
  const { user } = useAuth();
  const [amount, setAmount] = React.useState('');
  const [desc, setDesc] = React.useState('');
  const [category, setCategory] = React.useState<string>('Food');
  const [date, setDate] = React.useState<Date>(new Date());
  const [showPicker, setShowPicker] = React.useState(false);
  const [editingId, setEditingId] = React.useState<string | null>(null);
  const [items, setItems] = React.useState<Entry[]>([]);
  const [loading, setLoading] = React.useState(false);
  
  // Filter state
  const [searchQuery, setSearchQuery] = React.useState('');
  const [minAmount, setMinAmount] = React.useState('');
  const [maxAmount, setMaxAmount] = React.useState('');
  const [showFilter, setShowFilter] = React.useState(true);
  const scrollViewRef = React.useRef<ScrollView>(null);
  const lastScrollY = React.useRef(0);

  // Fetch transactions from Supabase
  const fetchTransactions = React.useCallback(async () => {
    if (!user) return;
    try {
      setLoading(true);
      console.log('[TransactionsScreen] Fetching transactions...');
      
      // Try transactions table first (where mock data is inserted)
      const { data: txData, error: txErr } = await supabase
        .from('transactions')
        .select('*')
        .order('date', { ascending: false });
      
      let txs = txData;
      let txError = txErr;
      
      // Fallback to financial_records if needed
      if (txErr) {
        const { data: financialData, error: financialError } = await supabase
          .from('financial_records')
          .select('*')
          .order('occurred_on', { ascending: false });
        
        txs = financialData;
        txError = financialError;
      }

      if (txError) throw txError;

      console.log(`[TransactionsScreen] Found ${txs?.length || 0} transactions`);

      if (txs) {
        setItems(txs.map(t => ({
          id: t.id,
          amount: Math.abs(Number(t.amount) || 0),
          category: t.category_primary || t.category || 'Other',
          desc: t.description || t.memo || '',
          date: (t.date || t.occurred_on)?.split('T')[0] || formatISO(new Date()),
        })));
      }
    } catch (err) {
      console.error('[TransactionsScreen] Error fetching transactions:', err);
    } finally {
      setLoading(false);
    }
  }, [user]);

  React.useEffect(() => {
    fetchTransactions();
  }, [fetchTransactions]);

  const onAddOrSave = async () => {
    if (!user) return;
    const value = parseFloat(amount);
    if (Number.isNaN(value) || value <= 0) return;

    try {
      setLoading(true);
      
      // Use local date string + noon UTC to prevent timezone shifts
      const dateStr = formatISO(date);
      const isoDate = `${dateStr}T12:00:00Z`;

      // Try financial_records first
      let txData: any = {
        user_id: user.id,
        amount: value,
        memo: desc?.trim() || 'Manual Entry',
        category: category,
        occurred_on: isoDate,
        source: 'manual',
        currency: 'USD'
      };

      let error;
      
      if (editingId) {
        // Try to update in financial_records
        const { error: updateError } = await supabase
          .from('financial_records')
          .update(txData)
          .eq('id', editingId);
        
        if (updateError) {
          // Fallback to transactions table
          const txDataFallback = {
            amount: value,
            description: desc?.trim() || 'Manual Entry',
            category_primary: category,
            date: isoDate,
            is_manual: true
          };
          
          const { error: txUpdateError } = await supabase
            .from('transactions')
            .update(txDataFallback)
            .eq('id', editingId);
          
          error = txUpdateError;
        }
      } else {
        // Try to insert into financial_records
        const { error: insertError } = await supabase
          .from('financial_records')
          .insert(txData);
        
        if (insertError) {
          // Fallback to transactions table
          // Get first bank account
          const { data: bankAccounts } = await supabase
            .from('bank_accounts')
            .select('id')
            .eq('user_id', user.id)
            .limit(1);
          
          if (bankAccounts && bankAccounts.length > 0) {
            const txDataFallback = {
              bank_account_id: bankAccounts[0].id,
              amount: value,
              description: desc?.trim() || 'Manual Entry',
              category_primary: category,
              date: isoDate,
              is_manual: true
            };
            
            const { error: txInsertError } = await supabase
              .from('transactions')
              .insert(txDataFallback);
            
            error = txInsertError;
          } else {
            alert('Please connect a bank account first');
            return;
          }
        }
      }
      
      if (error) throw error;

      setAmount('');
      setDesc('');
      setCategory('Food');
      setDate(new Date());
      setEditingId(null);
      
      await fetchTransactions();

    } catch (err) {
      console.error('Error saving transaction:', err);
      alert('Failed to save transaction');
    } finally {
      setLoading(false);
    }
  };

  const startEdit = (it: Entry) => {
    setEditingId(it.id);
    setAmount(String(it.amount));
    setDesc(it.desc ?? '');
    setCategory(it.category);
    setDate(new Date(it.date));
  };

  const onDelete = async (id: string) => {
    try {
      // Try financial_records first
      let { error } = await supabase
        .from('financial_records')
        .delete()
        .eq('id', id);
      
      if (error) {
        // Fallback to transactions table
        const result = await supabase
          .from('transactions')
          .delete()
          .eq('id', id);
        error = result.error;
      }
      
      if (error) throw error;
      
      setItems((prev) => prev.filter((it) => it.id !== id));
      if (editingId === id) setEditingId(null);
    } catch (err) {
      console.error('Error deleting transaction:', err);
    }
  };

  const totals = React.useMemo(() => {
    const map: Record<string, number> = {};
    for (const c of CATEGORIES) map[c] = 0;
    for (const it of items) map[it.category] += it.amount;
    return map;
  }, [items]);

  const maxVal = Math.max(1, ...Object.values(totals));

  // Filter logic
  const filteredItems = React.useMemo(() => {
    let filtered = [...items];

    // Text search (description or category)
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(item => 
        item.desc?.toLowerCase().includes(query) ||
        item.category.toLowerCase().includes(query)
      );
    }

    // Amount range filter
    const min = parseFloat(minAmount);
    const max = parseFloat(maxAmount);
    if (!isNaN(min)) {
      filtered = filtered.filter(item => item.amount >= min);
    }
    if (!isNaN(max)) {
      filtered = filtered.filter(item => item.amount <= max);
    }

    return filtered;
  }, [items, searchQuery, minAmount, maxAmount]);

  // Handle scroll for filter visibility
  const handleScroll = (event: any) => {
    const currentScrollY = event.nativeEvent.contentOffset.y;
    const scrollingDown = currentScrollY > lastScrollY.current;
    
    if (scrollingDown && currentScrollY > 50) {
      setShowFilter(false);
    } else if (!scrollingDown && currentScrollY < lastScrollY.current - 10) {
      setShowFilter(true);
    }
    
    lastScrollY.current = currentScrollY;
  };

  return (
    <SwipeNavigationWrapper currentTab="Transactions" scrollable={false}>
      <ImageBackground
        source={require('../public/images/nature_collection_1_20250803_182435.png')}
        style={styles.backgroundImage}
        imageStyle={styles.imageStyle}
      >
        <View style={styles.overlay}>
      
      {/* Smart Filter Bar */}
      {showFilter && (
        <View style={styles.filterBar}>
          <View style={styles.filterRow}>
            <TextInput
              value={searchQuery}
              onChangeText={setSearchQuery}
              placeholder="Search by name or category..."
              placeholderTextColor="#7a8fb2"
              style={styles.filterInput}
            />
          </View>
          <View style={styles.filterRow}>
            <TextInput
              value={minAmount}
              onChangeText={setMinAmount}
              placeholder="Min $"
              placeholderTextColor="#7a8fb2"
              keyboardType="decimal-pad"
              style={[styles.filterInput, { flex: 1 }]}
            />
            <Text style={styles.filterSeparator}>—</Text>
            <TextInput
              value={maxAmount}
              onChangeText={setMaxAmount}
              placeholder="Max $"
              placeholderTextColor="#7a8fb2"
              keyboardType="decimal-pad"
              style={[styles.filterInput, { flex: 1 }]}
            />
          </View>
          {(searchQuery || minAmount || maxAmount) && (
            <Pressable 
              onPress={() => {
                setSearchQuery('');
                setMinAmount('');
                setMaxAmount('');
              }}
              style={styles.clearFilterButton}
            >
              <Text style={styles.clearFilterText}>Clear Filters</Text>
           filteredItems.length > 0 ? (
            [...filteredIessable>
          )}
        </View>
      )}

      <ScrollView 
        ref={scrollViewRef}
        style={styles.screen} 
        contentContainerStyle={{ paddingBottom: 100 }}
        onScroll={handleScroll}
        scrollEventThrottle={16}
      >
        <Text style={styles.sectionHeader}>Transactions</Text>
        <Text style={styles.sectionDescription}>Manage your expenses and income</Text>
      
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
                const m = /^\d{4}-\d{2}-\d{2}$/.exec(txt);
                if (m) setDate(new Date(txt));
              }}
              placeholder="YYYY-MM-DD"
              placeholderTextColor="#7a8fb2"
              style={styles.input}
            />
          ) : (
            <View>
              <Pressable onPress={() => setShowPicker(true)} style={[styles.input, styles.dateButton]}>
                <Text style={styles.dateText}>{formatISO(date)}</Text>
              </Pressable>
              {showPicker && (
                <View style={styles.datePickerOverlay}>
                  <View style={styles.datePickerContainer}>
                    <DateTimePicker
                      value={date}
                      mode="date"
                      display={Platform.OS === 'ios' ? 'spinner' : 'default'}
                      onChange={(evt: DateTimePickerEvent, selected) => {
                        if (selected) setDate(selected);
                        setShowPicker(false);
                      }}
                    />
                  </View>
                </View>
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
        <View style={{ paddingVertical: 8 }}>
          {[...items].reverse().map((item) => (
            <View key={item.id} style={{ marginBottom: 12 }}>
              <View style={styles.row}>
                <View style={{ flex: 1 }}>
                  <Text style={{ color: 'white', fontWeight: '700' }}>
                    {item.category} • ${item.amount.toFixed(2)}
                  </Text>
                  <Text style={{ color: '#9bc6daff' }}>
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
            
          ) : (
            <Text style={{ color: '#7a8fa5', textAlign: 'center', fontStyle: 'italic' }}>
              {items.length === 0 ? 'No transactions yet' : 'No matching transactions'}
            
            <Text style={{ color: '#7a8fa5', textAlign: 'center', fontStyle: 'italic' }}>No transactions yet</Text>
          )}
        </View>

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
                  <Text style={styles.catVal}>${(totals[c] || 0).toFixed(2)}</Text>
                </View>
              ))}
            </View>
          </View>
        </View>
      </View>
      </ScrollView>
        </View>
      </ImageBackground>
    </SwipeNavigationWrapper>
  );
}
0.2 },
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(10, 14, 39, 0.85)',
  },
  filterBar: {
    backgroundColor: 'rgba(17, 26, 48, 0.95)',
    paddingHorizontal: 16,
    paddingVertical: 12,
    gap: 8,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(59, 130, 246, 0.3)',
  },
  filterRow: {
    flexDirection: 'row',
    gap: 8,
    alignItems: 'center',
  },
  filterInput: {
    height: 42,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#223459',
    color: 'white',
    paddingHorizontal: 12,
    backgroundColor: '#0f1930',
    fontSize: 14,
  },
  filterSeparator: {
    color: '#9fb3c8',
    fontSize: 16,
    fontWeight: '600',
  },
  clearFilterButton: {
    alignSelf: 'center',
    paddingVertical: 6,
    paddingHorizontal: 12,
    backgroundColor: 'rgba(239, 68, 68, 0.15)',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: 'rgba(239, 68, 68, 0.5)',
  },
  clearFilterText: {
    color: '#ef4444',
    fontSize: 12,
    fontWeight: '600
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(10, 14, 39, 0.25)',
  },
  screen: { flex: 1, paddingHorizontal: 20, paddingVertical: 20 },
  title: { color: 'white', fontSize: 24, fontWeight: '700', marginBottom: 20, textAlign: 'center' },
  subTitle: { color: 'white', fontSize: 16, fontWeight: '700', marginBottom: 12, textAlign: 'center' },
  card: { backgroundColor: 'rgba(41, 44, 61, 0.5)', borderRadius: 12, padding: 20, gap: 16, marginHorizontal: 8 },
  label: { color: '#d6e0e0ff', fontSize: 13, fontWeight: '600' },
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
  dateButton: { 
    justifyContent: 'center',
    minHeight: 48,
  },
  dateText: {
    color: 'white',
    fontSize: 16,
  },
  datePickerOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000,
  },
  datePickerContainer: {
    backgroundColor: '#111a30',
    borderRadius: 12,
    padding: 20,
    minWidth: 300,
  },
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
  hr: { height: 1, backgroundColor: '#1e40af', marginVertical: 10, opacity: 0.6 },
  catName: { color: '#ffd2cfff' },
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
    color: '#942c1aff',
    backgroundColor: '#0f1930',
    fontSize: 20,
    fontWeight: '700',
    marginBottom: 8,
    textAlign: 'center',
  },
  sectionDescription: {
    color: '#245286ff',
    backgroundColor: '#0f1930',
    fontSize: 16,
    marginBottom: 20,
    textAlign: 'center',
    lineHeight: 18,
  },
});
