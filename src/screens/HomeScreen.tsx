import * as React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { SafeAreaView } from 'react-native-safe-area-context';
import SwipeNavigationWrapper from '../components/SwipeNavigationWrapper';
import FinancialSummary from '../components/FinancialSummary';
import InvestmentAnalysis from '../components/InvestmentAnalysis';
import FinancialActivityRings from '../components/FinancialActivityRings';
import AnimatedChart from '../components/AnimatedChart';
import { supabase } from '../services/supabaseClient';

// Define types locally
interface Transaction {
  id: string;
  amount: number;
  date: string;
  category_primary?: string;
  merchant?: string;
  memo?: string;
}

interface MonthlySummary {
  total_income?: number;
  total_expenses?: number;
  net_savings?: number;
}

export default function HomeScreen() {
  const [transactions, setTransactions] = React.useState<Transaction[]>([]);
  const [chartData, setChartData] = React.useState<any[]>([]);
  const [monthlySummary, setMonthlySummary] = React.useState<MonthlySummary | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [activityData, setActivityData] = React.useState({
    budget: { current: 0, target: 4000, percentage: 0 },
    savings: { current: 0, target: 1000, percentage: 0 },
    investment: { current: 0, target: 1000, percentage: 0 },
  });

  // Calculate monthly data for chart
  const calculateMonthlyData = (transactions: Transaction[]) => {
    const monthlyData: {[key: string]: number} = {};
    const currentYear = new Date().getFullYear();
    
    // Group transactions by month
    transactions.forEach(transaction => {
      const date = new Date(transaction.date);
      if (date.getFullYear() === currentYear) {
        const monthKey = date.toLocaleDateString('en-US', { month: 'short' });
        
        if (!monthlyData[monthKey]) {
          monthlyData[monthKey] = 0;
        }
        
        // Only count expenses (not income)
        if (transaction.amount < 0) {
          monthlyData[monthKey] += Math.abs(transaction.amount);
        }
      }
    });

    // Convert to chart format and get last 6 months
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const currentMonth = new Date().getMonth();
    const colors = ['#FF6B6B', '#4ECDC4', '#FFD93D', '#FF6B6B', '#4ECDC4', '#FFD93D'];
    
    const result = [];
    for (let i = 5; i >= 0; i--) {
      const monthIndex = (currentMonth - i + 12) % 12;
      const monthName = months[monthIndex];
      const amount = monthlyData[monthName] || 0;
      
      result.push({
        month: monthName,
        amount: amount,
        color: colors[5 - i],
      });
    }
    
    return result;
  };

  // Calculate activity rings data
  const calculateActivityData = (transactions: Transaction[], monthlySummary?: MonthlySummary) => {
    let totalIncome = 0;
    let totalExpenses = 0;
    let totalInvestments = 0;

    // Calculate from actual transactions
    transactions.forEach(transaction => {
      const amount = Number(transaction.amount) || 0;
      
      if (amount > 0) {
        totalIncome += amount;
      } else if (amount < 0) {
        totalExpenses += Math.abs(amount);
        
        // Check if it's an investment
        const category = (transaction.category_primary || transaction.description || '').toLowerCase();
        if (category.includes('investment') || category.includes('invest')) {
          totalInvestments += Math.abs(amount);
        }
      }
    });

    const totalSavings = totalIncome - totalExpenses;
    const monthlyBudget = 4000;
    const savingsTarget = 1000;
    const investmentTarget = 1000;

    return {
      budget: {
        current: totalExpenses,
        target: monthlyBudget,
        percentage: totalExpenses > 0 ? Math.min(Math.round((totalExpenses / monthlyBudget) * 100), 100) : 0,
      },
      savings: {
        current: totalSavings > 0 ? totalSavings : 0,
        target: savingsTarget,
        percentage: totalSavings > 0 ? Math.min(Math.round((totalSavings / savingsTarget) * 100), 100) : 0,
      },
      investment: {
        current: totalInvestments,
        target: investmentTarget,
        percentage: totalInvestments > 0 ? Math.min(Math.round((totalInvestments / investmentTarget) * 100), 100) : 0,
      },
    };
  };

  useFocusEffect(
    React.useCallback(() => {
      console.log('[HomeScreen] Screen focused, fetching transactions...');
      fetchTransactions();
    }, [])
  );

  const fetchTransactions = async () => {
    setLoading(true);
    try {
      console.log('[HomeScreen] Fetching transactions from Supabase...');
      
      // Try transactions table first (this is where mock data is inserted)
      const { data: txData, error: txError } = await supabase
        .from('transactions')
        .select('*')
        .order('date', { ascending: false })
        .limit(100);
      
      let data = txData;
      let error = txError;
      
      // If transactions table doesn't work, try financial_records
      if (txError) {
        console.log('[HomeScreen] Trying financial_records table...');
        const { data: financialData, error: financialError } = await supabase
          .from('financial_records')
          .select('*')
          .order('occurred_on', { ascending: false })
          .limit(100);
        
        data = financialData;
        error = financialError;
      }
      
      if (error) {
        console.error('[HomeScreen] Error fetching transactions:', error);
        return;
      }
      
      console.log(`[HomeScreen] Found ${data?.length || 0} transactions`);
      
      if (data && data.length > 0) {
        // Normalize the data structure
        const normalizedData = data.map((tx: any) => ({
          id: tx.id,
          amount: Number(tx.amount) || 0,
          date: tx.date || tx.occurred_on,
          category_primary: tx.category_primary || tx.category,
          merchant: tx.merchant,
          memo: tx.memo,
          description: tx.description
        }));
        
        console.log(`[HomeScreen] Normalized ${normalizedData.length} transactions`);
        setTransactions(normalizedData as Transaction[]);
        
        // Calculate derived data
        const monthlyData = calculateMonthlyData(normalizedData as Transaction[]);
        setChartData(monthlyData);
        
        // Calculate activity data
        const activityMetrics = calculateActivityData(normalizedData as Transaction[]);
        setActivityData(activityMetrics);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
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
          {/* Dynamic Financial Activity Rings Component */}
          <FinancialActivityRings 
            budgetUsed={activityData.budget.percentage}
            savingsGoal={activityData.savings.percentage}
            investmentsGrowth={activityData.investment.percentage}
          />
          
          {/* Dynamic Animated Chart Component */}
          <AnimatedChart data={chartData} />
          
          {/* Existing Financial Summary component */}
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
