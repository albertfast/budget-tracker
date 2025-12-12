import * as React from 'react';
import { View, Text, TextInput, Pressable, Alert, StyleSheet, ActivityIndicator, ScrollView, TouchableOpacity, ImageBackground } from 'react-native';
import Svg, { Circle, G } from 'react-native-svg';
import { useFocusEffect } from '@react-navigation/native';
import SwipeNavigationWrapper from '@/components/SwipeNavigationWrapper';
import Spacer from '@/components/Spacer';
import { insertFinancialRecord } from '@/services/financialDataService';
import { supabase } from '@/services/supabaseClient';
import { EXPENSE_CATEGORIES, INCOME_CATEGORIES } from '@/constants/categories';

export default function AddScreen() {
  const [amount, setAmount] = React.useState('');
  const [desc, setDesc] = React.useState('');
  const [type, setType] = React.useState<'expense' | 'income'>('expense');
  const [category, setCategory] = React.useState(EXPENSE_CATEGORIES[0].id);
  const [showDropdown, setShowDropdown] = React.useState(false);
  const [transactionId, setTransactionId] = React.useState('');
  const [merchant, setMerchant] = React.useState('');
  const [loading, setLoading] = React.useState(false);
  const [chartData, setChartData] = React.useState<any[]>([]);

  const categories = type === 'expense' ? EXPENSE_CATEGORIES : INCOME_CATEGORIES;
  const selectedCategory = categories.find(c => c.id === category) || categories[0];

  useFocusEffect(
    React.useCallback(() => {
      fetchChartData();
    }, [type])
  );

  const fetchChartData = async () => {
    const { data: allData } = await supabase
      .from('financial_records')
      .select('category, amount');

    if (allData) {
      // Filter for current type's categories
      const typeCategories = type === 'expense' ? EXPENSE_CATEGORIES : INCOME_CATEGORIES;
      const relevantData = allData.filter(d => 
        typeCategories.some(c => c.id === d.category) || 
        (type === 'expense' && d.category === 'Expense') || // Handle legacy
        (type === 'income' && d.category === 'Income')
      );

      // Group by category
      const grouped = new Map<string, number>();
      relevantData.forEach(d => {
        let cat = d.category;
        // Map legacy 'Expense'/'Income' to 'Other' if needed, or keep as is
        if (cat === 'Expense' || cat === 'Income') cat = 'Other';
        
        const current = grouped.get(cat) || 0;
        grouped.set(cat, current + Number(d.amount));
      });

      setChartData(Array.from(grouped.entries()).map(([key, val]) => ({
        category: key,
        amount: val,
        color: typeCategories.find(c => c.id === key)?.color || '#6b7280'
      })));
    }
  };

  const onSave = async () => {
    const value = parseFloat(amount);
    if (Number.isNaN(value) || value <= 0) {
      Alert.alert('Invalid amount', 'Please enter a positive number.');
      return;
    }

    setLoading(true);
    try {
      await insertFinancialRecord({
        category: category, // Save the specific category!
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
      setTransactionId('');
      setMerchant('');
      fetchChartData(); // Refresh chart
    } catch (error: any) {
      Alert.alert('Error', error.message || 'Failed to save transaction');
    } finally {
      setLoading(false);
    }
  };

  // Donut Chart Logic
  const total = chartData.reduce((sum, item) => sum + item.amount, 0);
  let startAngle = 0;
  const radius = 60;
  const strokeWidth = 15;
  const circumference = 2 * Math.PI * radius;

  return (
    <SwipeNavigationWrapper currentTab="Add">
      <ImageBackground
        source={require('../public/images/nature_collection_12_20250803_183423.png')}
        style={styles.backgroundImage}
        imageStyle={styles.imageStyle}
      >
        <View style={styles.overlay}>
      <ScrollView style={styles.screen} contentContainerStyle={{ paddingBottom: 40 }}>
        <Text style={styles.sectionHeader}>Quick Entry</Text>
        <Text style={styles.sectionDescription}>Add new transactions and financial entries</Text>
      
      <View style={styles.card}>
        <Text style={styles.label}>Type</Text>
        <View style={{ flexDirection: 'row', marginTop: 12, marginBottom: 8, gap: 12 }}>
          <Pressable onPress={() => { setType('expense'); setCategory(EXPENSE_CATEGORIES[0].id); }}
            style={[styles.segment, type === 'expense' && styles.segmentActive]}>
            <Text style={styles.segmentText}>Expense</Text>
          </Pressable>
          <Pressable onPress={() => { setType('income'); setCategory(INCOME_CATEGORIES[0].id); }}
            style={[styles.segment, type === 'income' && styles.segmentActive]}>
            <Text style={styles.segmentText}>Income</Text>
          </Pressable>
        </View>

        <Spacer />

        <Text style={styles.label}>Category</Text>
        <TouchableOpacity 
          style={styles.dropdownButton} 
          onPress={() => setShowDropdown(!showDropdown)}
        >
          <Text style={styles.dropdownButtonText}>{selectedCategory.label}</Text>
          <Text style={styles.dropdownArrow}>{showDropdown ? '▲' : '▼'}</Text>
        </TouchableOpacity>

        {showDropdown && (
          <View style={styles.dropdownList}>
            {categories.map((cat) => (
              <TouchableOpacity 
                key={cat.id} 
                style={[styles.dropdownItem, category === cat.id && styles.dropdownItemActive]}
                onPress={() => {
                  setCategory(cat.id);
                  setShowDropdown(false);
                }}
              >
                <Text style={styles.dropdownItemText}>{cat.label}</Text>
              </TouchableOpacity>
            ))}
          </View>
        )}

        {/* Donut Chart */}
        {total > 0 && (
          <View style={styles.chartContainer}>
            <Svg height="160" width="160" viewBox="0 0 160 160">
              <G rotation="-90" origin="80, 80">
                {chartData.map((item, index) => {
                  const percentage = item.amount / total;
                  const strokeDasharray = `${percentage * circumference} ${circumference}`;
                  const strokeDashoffset = -startAngle * circumference; // This logic is slightly wrong for dashoffset
                  // Correct logic for simple segments:
                  // We need to rotate each segment.
                  // Actually, simpler:
                  const angle = percentage * 360;
                  const currentStartAngle = startAngle;
                  startAngle += percentage; // Accumulate for next

                  return (
                    <Circle
                      key={index}
                      cx="80"
                      cy="80"
                      r={radius}
                      stroke={item.color}
                      strokeWidth={strokeWidth}
                      fill="transparent"
                      strokeDasharray={strokeDasharray}
                      strokeDashoffset={0} // We handle rotation via transform
                      rotation={currentStartAngle * 360}
                      origin="80, 80"
                    />
                  );
                })}
              </G>
              {/* Center Text */}
              <View style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, justifyContent: 'center', alignItems: 'center' }}>
                 {/* SVG doesn't support View inside. We need to overlay View or use SvgText */}
              </View>
            </Svg>
            {/* Overlay for center text */}
            <View style={styles.chartCenter}>
              <Text style={styles.chartTotal}>${total.toFixed(0)}</Text>
              <Text style={styles.chartLabel}>Total</Text>
            </View>
          </View>
        )}

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
      </ScrollView>
        </View>
      </ImageBackground>
    </SwipeNavigationWrapper>
  );
}

const styles = StyleSheet.create({
  backgroundImage: { flex: 1 },
  imageStyle: { opacity: 0.9 },
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(1, 3, 12, 0.35)',
  },
  screen: { flex: 1, paddingHorizontal: 20, paddingVertical: 20 },
  title: { color: 'white', fontSize: 24, fontWeight: '700', marginBottom: 20, textAlign: 'center' },
  card: { backgroundColor: 'rgba(48, 52, 66, 0.55)', borderRadius: 12, padding: 20, marginHorizontal: 8 },
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
    color: '#820d99ff',
    fontSize: 20,
    fontWeight: '700',
    marginBottom: 8,
    textAlign: 'center',
  },
  sectionDescription: {
    color: '#0b08ceff',
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
  dropdownButton: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#0f1930',
    borderWidth: 1,
    borderColor: '#223459',
    borderRadius: 10,
    paddingHorizontal: 16,
    paddingVertical: 12,
    marginTop: 8,
    marginBottom: 8,
  },
  dropdownButtonText: {
    color: 'white',
    fontSize: 16,
  },
  dropdownArrow: {
    color: '#7a8fa5',
    fontSize: 12,
  },
  dropdownList: {
    backgroundColor: '#0f1930',
    borderWidth: 1,
    borderColor: '#223459',
    borderRadius: 10,
    marginTop: 4,
    marginBottom: 12,
    overflow: 'hidden',
  },
  dropdownItem: {
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#1a2238',
  },
  dropdownItemActive: {
    backgroundColor: '#1e3a8a',
  },
  dropdownItemText: {
    color: 'white',
    fontSize: 14,
  },
  chartContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    marginVertical: 16,
    height: 160,
  },
  chartCenter: {
    position: 'absolute',
    alignItems: 'center',
    justifyContent: 'center',
  },
  chartTotal: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  chartLabel: {
    color: '#7a8fa5',
    fontSize: 12,
  },
});
