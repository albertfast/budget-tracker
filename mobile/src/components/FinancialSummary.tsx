import React from 'react';
import { StyleSheet, Text, View, ScrollView } from 'react-native';
import Svg, { Rect, Text as SvgText } from 'react-native-svg';

export default function FinancialSummary() {
  // Sample data - in a real app, this would come from props or API
  const monthlyIncome = 3500;
  const expenseCategories = [
    { name: 'Food', amount: 450, color: '#ef4444' },
    { name: 'Housing', amount: 1200, color: '#f97316' },
    { name: 'Transport', amount: 280, color: '#eab308' },
    { name: 'Bills', amount: 320, color: '#22c55e' },
    { name: 'Shopping', amount: 180, color: '#3b82f6' },
    { name: 'Entertainment', amount: 150, color: '#8b5cf6' },
    { name: 'Other', amount: 120, color: '#6b7280' },
  ];

  const totalExpenses = expenseCategories.reduce((sum, cat) => sum + cat.amount, 0);
  const totalBalance = monthlyIncome - totalExpenses;
  const maxAmount = Math.max(monthlyIncome, ...expenseCategories.map(cat => cat.amount));

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
      <Text style={styles.title}>Financial Summary</Text>
      
      {/* Financial Summary Table */}
      <View style={styles.tableContainer}>
        <View style={styles.table}>
          {/* Table Header */}
          <View style={styles.tableHeader}>
            <Text style={styles.tableHeaderText}>Category</Text>
            <Text style={styles.tableHeaderText}>Amount</Text>
            <Text style={styles.tableHeaderText}>Status</Text>
          </View>
          
          {/* Table Rows */}
          <View style={styles.tableRow}>
            <Text style={styles.tableCellLabel}>Monthly Income</Text>
            <Text style={[styles.tableCellAmount, styles.positive]}>${monthlyIncome.toFixed(2)}</Text>
            <Text style={[styles.tableCellStatus, styles.positive]}>+</Text>
          </View>
          
          <View style={styles.tableRow}>
            <Text style={styles.tableCellLabel}>Total Expenses</Text>
            <Text style={[styles.tableCellAmount, styles.negative]}>${totalExpenses.toFixed(2)}</Text>
            <Text style={[styles.tableCellStatus, styles.negative]}>-</Text>
          </View>
          
          <View style={[styles.tableRow, styles.tableRowTotal]}>
            <Text style={[styles.tableCellLabel, styles.totalLabel]}>Net Balance</Text>
            <Text style={[styles.tableCellAmount, styles.totalAmount, totalBalance >= 0 ? styles.positive : styles.negative]}>
              ${totalBalance.toFixed(2)}
            </Text>
            <Text style={[styles.tableCellStatus, totalBalance >= 0 ? styles.positive : styles.negative]}>
              {totalBalance >= 0 ? '✓' : '!'}
            </Text>
          </View>
        </View>
      </View>

      {/* Expense Categories Table */}
      <View style={styles.tableContainer}>
        <Text style={styles.tableTitle}>Expense Breakdown</Text>
        <View style={styles.table}>
          {/* Table Header */}
          <View style={styles.tableHeader}>
            <Text style={styles.tableHeaderText}>Category</Text>
            <Text style={styles.tableHeaderText}>Amount</Text>
            <Text style={styles.tableHeaderText}>%</Text>
          </View>
          
          {/* Expense Category Rows */}
          {expenseCategories.map((category, index) => (
            <View key={category.name} style={styles.tableRow}>
              <View style={styles.categoryCell}>
                <View style={[styles.categoryDot, { backgroundColor: category.color }]} />
                <Text style={styles.tableCellLabel}>{category.name}</Text>
              </View>
              <Text style={[styles.tableCellAmount, styles.negative]}>${category.amount.toFixed(2)}</Text>
              <Text style={styles.tableCellPercent}>
                {((category.amount / totalExpenses) * 100).toFixed(1)}%
              </Text>
            </View>
          ))}
        </View>
      </View>

      {/* Bar Chart */}
      <View style={styles.chartContainer}>
        <Text style={styles.chartTitle}>Income vs Expenses by Category</Text>
        
        {/* Income Bar */}
        <View style={styles.barRow}>
          <Text style={styles.barLabel}>Income</Text>
          <View style={styles.barContainer}>
            <View 
              style={[
                styles.bar, 
                { 
                  width: `${(monthlyIncome / maxAmount) * 100}%`, 
                  backgroundColor: '#22c55e' 
                }
              ]} 
            />
          </View>
        </View>

        {/* Expense Bars */}
        {expenseCategories.map((category, index) => (
          <View key={category.name} style={styles.barRow}>
            <Text style={styles.barLabel}>{category.name}</Text>
            <View style={styles.barContainer}>
              <View 
                style={[
                  styles.bar, 
                  { 
                    width: `${(category.amount / maxAmount) * 100}%`, 
                    backgroundColor: category.color 
                  }
                ]} 
              />
            </View>
          </View>
        ))}
      </View>

      {/* Category Legend */}
      <View style={styles.legendContainer}>
        <Text style={styles.legendTitle}>Category Breakdown</Text>
        <View style={styles.legendGrid}>
          {expenseCategories.map((category) => (
            <View key={category.name} style={styles.legendItem}>
              <View style={[styles.legendColor, { backgroundColor: category.color }]} />
              <Text style={styles.legendText}>
                {category.name}: ${category.amount}
              </Text>
            </View>
          ))}
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#111a30',
    borderRadius: 12,
    padding: 12,
    marginHorizontal: 40, // Increased from 16 to 40 for arrow space
    marginVertical: 8,
    marginTop: 40,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
    flex: 1,
  },
  scrollContent: {
    paddingTop: 20,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 12,
    textAlign: 'center',
    color: '#9fb3c8',
    textShadowColor: '#000000',
    textShadowOffset: { width: 1, height: 1 },
    textShadowRadius: 2,
  },
  // Table Styles
  tableContainer: {
    alignSelf: 'center',
    width: '95%',
    marginBottom: 16,
    backgroundColor: 'transparent',
  },
  tableTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#9fb3c8',
    marginBottom: 8,
    textAlign: 'center',
    textShadowColor: '#000000',
    textShadowOffset: { width: 1, height: 1 },
    textShadowRadius: 2,
  },
  table: {
    backgroundColor: '#0f1930',
    borderRadius: 8,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: '#1e3a8a',
  },
  tableHeader: {
    flexDirection: 'row',
    backgroundColor: '#1e40af',
    paddingVertical: 12,
    paddingHorizontal: 16,
  },
  tableHeaderText: {
    flex: 1,
    fontSize: 14,
    fontWeight: 'bold',
    color: '#ffffff',
    textAlign: 'center',
    textShadowColor: '#000000',
    textShadowOffset: { width: 0.5, height: 0.5 },
    textShadowRadius: 1,
  },
  tableRow: {
    flexDirection: 'row',
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#1e3a8a',
    backgroundColor: 'transparent',
  },
  tableRowTotal: {
    backgroundColor: '#0a1425',
    borderBottomWidth: 0,
  },
  tableCellLabel: {
    flex: 1,
    fontSize: 14,
    color: '#9fb3c8',
    textAlign: 'left',
    textShadowColor: '#000000',
    textShadowOffset: { width: 0.5, height: 0.5 },
    textShadowRadius: 1,
  },
  tableCellAmount: {
    flex: 1,
    fontSize: 14,
    fontWeight: '600',
    textAlign: 'center',
    textShadowColor: '#000000',
    textShadowOffset: { width: 0.5, height: 0.5 },
    textShadowRadius: 1,
  },
  tableCellStatus: {
    flex: 0.5,
    fontSize: 16,
    fontWeight: 'bold',
    textAlign: 'center',
    textShadowColor: '#000000',
    textShadowOffset: { width: 0.5, height: 0.5 },
    textShadowRadius: 1,
  },
  tableCellPercent: {
    flex: 0.8,
    fontSize: 13,
    color: '#9fb3c8',
    textAlign: 'center',
    fontWeight: '500',
    textShadowColor: '#000000',
    textShadowOffset: { width: 0.5, height: 0.5 },
    textShadowRadius: 1,
  },
  totalLabel: {
    fontWeight: 'bold',
    fontSize: 15,
  },
  totalAmount: {
    fontWeight: 'bold',
    fontSize: 15,
  },
  categoryCell: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
  },
  categoryDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 8,
  },
  label: {
    fontSize: 14,
    color: '#9fb3c8',
    textShadowColor: '#000000',
    textShadowOffset: { width: 0.5, height: 0.5 },
    textShadowRadius: 1,
  },
  amount: {
    fontSize: 14,
    fontWeight: '600',
    color: '#9fb3c8',
    textShadowColor: '#000000',
    textShadowOffset: { width: 0.5, height: 0.5 },
    textShadowRadius: 1,
  },
  positive: {
    color: '#22c55e',
    textShadowColor: '#000000',
    textShadowOffset: { width: 0.5, height: 0.5 },
    textShadowRadius: 1,
  },
  negative: {
    color: '#ef4444',
    textShadowColor: '#000000',
    textShadowOffset: { width: 0.5, height: 0.5 },
    textShadowRadius: 1,
  },
  chartContainer: {
    backgroundColor: '#0f1930',
    borderRadius: 8,
    padding: 12,
    paddingHorizontal: 20,
    marginBottom: 16,
  },
  chartTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#9fb3c8',
    marginBottom: 12,
    textAlign: 'center',
    textShadowColor: '#000000',
    textShadowOffset: { width: 1, height: 1 },
    textShadowRadius: 2,
  },
  barRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 6,
    backgroundColor: 'transparent',
  },
  barLabel: {
    width: 65,
    fontSize: 12,
    color: '#9fb3c8',
    fontWeight: '500',
    textShadowColor: '#000000',
    textShadowOffset: { width: 0.5, height: 0.5 },
    textShadowRadius: 1,
    flexShrink: 0,
  },
  barContainer: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'transparent',
    minWidth: 0,
    marginLeft: 8,
  },
  bar: {
    height: 16,
    borderRadius: 3,
    marginRight: 8,
    minWidth: 4,
    maxWidth: '70%',
  },
  barValue: {
    fontSize: 11,
    color: '#9fb3c8',
    fontWeight: '500',
    minWidth: 45,
    textShadowColor: '#000000',
    textShadowOffset: { width: 0.5, height: 0.5 },
    textShadowRadius: 1,
    flexShrink: 0,
    textAlign: 'right',
  },
  legendContainer: {
    backgroundColor: '#0f1930',
    borderRadius: 8,
    padding: 12,
    paddingHorizontal: 20,
  },
  legendTitle: {
    fontSize: 15,
    fontWeight: 'bold',
    color: '#9fb3c8',
    marginBottom: 10,
    textAlign: 'center',
    textShadowColor: '#000000',
    textShadowOffset: { width: 1, height: 1 },
    textShadowRadius: 2,
  },
  legendGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    width: '48%',
    marginBottom: 6,
    backgroundColor: 'transparent',
  },
  legendColor: {
    width: 10,
    height: 10,
    borderRadius: 2,
    marginRight: 6,
  },
  legendText: {
    fontSize: 11,
    color: '#9fb3c8',
    flex: 1,
    textShadowColor: '#000000',
    textShadowOffset: { width: 0.5, height: 0.5 },
    textShadowRadius: 1,
  },
});