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
    const currentYear = new Date().getFullYear();
    const currentMonth = new Date().getMonth();
    
    let totalIncome = monthlySummary?.total_income || 0;
    let totalExpenses = monthlySummary?.total_expenses || 0;
    let totalSavings = monthlySummary?.net_savings || 0;
    let totalInvestments = 0;

    // For investments (cumulative)
    transactions.forEach(transaction => {
      if (transaction.category_primary?.toLowerCase().includes('investment')) {
        totalInvestments += Math.abs(transaction.amount);
      }
    });

    const monthlyBudget = 4000;
    const savingsTarget = 1000;
    const investmentTarget = 1000;

    return {
      budget: {
        current: totalExpenses,
        target: monthlyBudget,
        percentage: Math.min(Math.round((totalExpenses / monthlyBudget) * 100), 100),
      },
      savings: {
        current: totalSavings,
        target: savingsTarget,
        percentage: Math.min(Math.round((totalSavings / savingsTarget) * 100), 100),
      },
      investment: {
        current: totalInvestments,
        target: investmentTarget,
        percentage: Math.min(Math.round((totalInvestments / investmentTarget) * 100), 100),
      },
    };
  };

  useFocusEffect(
    React.useCallback(() => {
      fetchTransactions();
    }, [])
  );

  const fetchTransactions = async () => {
    setLoading(true);
    try {
      const { data, error } = await supabase
        .from('financial_records')
        .select('*')
        .order('occurred_on', { ascending: false })
        .limit(100);
      
      if (error) {
        console.error('Error fetching transactions:', error);
        return;
      }
      
      if (data) {
        setTransactions(data as Transaction[]);
        
        // Calculate derived data
        const monthlyData = calculateMonthlyData(data as Transaction[]);
        setChartData(monthlyData);
        
        // Calculate activity data
        const activityMetrics = calculateActivityData(data as Transaction[]);
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
