import * as React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { useNavigation, useFocusEffect } from '@react-navigation/native';
import { SafeAreaView } from 'react-native-safe-area-context';
import SwipeNavigationWrapper from '@/components/SwipeNavigationWrapper';
import FinancialSummary from '@/components/FinancialSummary';
import InvestmentAnalysis from '@/components/InvestmentAnalysis';
import { supabase } from '@/services/supabaseClient';

export default function HomeScreen() {
  const [transactions, setTransactions] = React.useState([]);

  useFocusEffect(
    React.useCallback(() => {
      fetchTransactions();
    }, [])
  );

  const fetchTransactions = async () => {
    const { data, error } = await supabase
      .from('financial_records')
      .select('*')
      .order('occurred_on', { ascending: false });
      
    if (!error && data) {
      setTransactions(data);
    }
  };

  return (
   <SafeAreaView style={{ flex: 1, backgroundColor: '#0b1220' }}>
      <SwipeNavigationWrapper currentTab="Home" scrollable={false}>
        <ScrollView
          style={styles.screen}
          showsVerticalScrollIndicator={false}
          contentInsetAdjustmentBehavior="never"
        >
          {/* Financial Summary component */}
          <FinancialSummary transactions={transactions} />
          
          {/* Investment Analysis component */}
          <InvestmentAnalysis transactions={transactions} />
          
          <View style={styles.card}>
            <Text style={styles.body}>Your financial overview and quick insights. Check the Connect Account tab to link your bank for automatic transaction syncing.</Text>
          </View>
        </ScrollView>
      </SwipeNavigationWrapper>
  </SafeAreaView> 
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, paddingHorizontal: 20, paddingVertical: 20, backgroundColor: '#0b1220' },
  card: { backgroundColor: '#111a30', borderRadius: 12, padding: 16, marginTop: 8 },
  body: { color: '#cfe1ff', lineHeight: 20 },
});
