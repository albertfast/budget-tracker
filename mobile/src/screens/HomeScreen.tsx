import * as React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { SafeAreaView } from 'react-native-safe-area-context';
import SwipeNavigationWrapper from '@/components/SwipeNavigationWrapper';
import FinancialSummary from '@/components/FinancialSummary';
import InvestmentAnalysis from '@/components/InvestmentAnalysis';
import FinancialActivityRings from '@/components/FinancialActivityRings';
import AnimatedChart from '@/components/AnimatedChart';
import { supabase } from '@/services/supabaseClient';

export default function HomeScreen() {
  const [transactions, setTransactions] = React.useState([]);
  const [chartData, setChartData] = React.useState([]);
  const [activityData, setActivityData] = React.useState({
    budget: { current: 0, target: 4000, percentage: 0 },
    savings: { current: 0, target: 1000, percentage: 0 },
    investment: { current: 0, target: 1000, percentage: 0 },
  });

  // Calculate monthly data for chart
  const calculateMonthlyData = (transactions: any[]) => {
    const monthlyData: {[key: string]: number} = {};
    const currentYear = new Date().getFullYear();
    
    // Group transactions by month
    transactions.forEach(transaction => {
      const date = new Date(transaction.occurred_on);
      if (date.getFullYear() === currentYear) {
        const monthKey = date.toLocaleDateString('en-US', { month: 'short' });
        
        if (!monthlyData[monthKey]) {
          monthlyData[monthKey] = 0;
        }
        
        // Only count expenses (not income)
        if (transaction.category !== 'Income') {
          monthlyData[monthKey] += Number(transaction.amount) || 0;
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
  const calculateActivityData = (transactions: any[]) => {
    const currentYear = new Date().getFullYear();
    const currentMonth = new Date().getMonth();
    
    let totalIncome = 0;
    let totalExpenses = 0;
    let totalSavings = 0;
    let totalInvestments = 0;

    transactions.forEach(transaction => {
      const date = new Date(transaction.occurred_on);
      if (date.getFullYear() === currentYear && date.getMonth() === currentMonth) {
        const amount = Number(transaction.amount) || 0;
        
        if (transaction.category === 'Income') {
          totalIncome += amount;
        } else {
          totalExpenses += amount;
        }
      }

      // For savings and investments (cumulative)
      if (transaction.category === 'Savings') {
        totalSavings += Number(transaction.amount) || 0;
      } else if (transaction.category === 'Investment') {
        totalInvestments += Number(transaction.amount) || 0;
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
    const { data, error } = await supabase
      .from('financial_records')
      .select('*')
      .order('occurred_on', { ascending: false });
      
    if (!error && data) {
      setTransactions(data as any);
      
      // Calculate derived data
      const monthlyData = calculateMonthlyData(data);
      setChartData(monthlyData as any);
      
      const activityMetrics = calculateActivityData(data);
      setActivityData(activityMetrics);
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
