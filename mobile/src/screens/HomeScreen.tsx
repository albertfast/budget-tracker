import * as React from 'react';
import { View, Text, StyleSheet, Pressable, ScrollView } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import SwipeNavigationWrapper from '@/components/SwipeNavigationWrapper';
import FinancialSummary from '@/components/FinancialSummary';
import InvestmentAnalysis from '@/components/InvestmentAnalysis';

export default function HomeScreen() {
  const navigation = useNavigation();

  const tabs = [
    { name: 'Home', icon: '🏠', description: 'Dashboard & Overview' },
    { name: 'Transactions', icon: '💳', description: 'View & Add Transactions' },
    { name: 'Add', icon: '➕', description: 'Quick Entry Form' },
    { name: 'Connect Account', icon: '🏦', description: 'Link Bank Account' },
    { name: 'Account', icon: '👤', description: 'Profile & Settings' },
  ];

  const handleTabPress = (tabName: string) => {
    if (tabName !== 'Home') {
      navigation.navigate(tabName as never);
    }
  };

  return (
    <SwipeNavigationWrapper currentTab="Home">
      <ScrollView style={styles.screen} showsVerticalScrollIndicator={false}>
        <Text style={styles.sectionHeader}>Dashboard Overview</Text>
        <Text style={styles.sectionDescription}>Track your finances and navigate between sections</Text>
        
        {/* Financial Summary component */}
        <FinancialSummary />
        
        {/* Investment Analysis component */}
        <InvestmentAnalysis />
        
        <View style={styles.disclaimerContainer}>
          <Text style={styles.disclaimerText}>
            Disclaimer: Investment recommendations are not provided by a CFP (Certified Financial Planner), licensed investment broker, or financial professional. They are generated using known risk assessment principles and algorithmic analysis. All investment decisions are made at the user's own risk.
          </Text>
        </View>
        
        <View style={styles.card}>
          <Text style={styles.body}>Your financial overview and quick insights. Check the Connect Account tab to link your bank for automatic transaction syncing.</Text>
        </View>
      </ScrollView>
    </SwipeNavigationWrapper>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, paddingHorizontal: 20, paddingVertical: 20, backgroundColor: '#0b1220' },
  title: { color: 'white', fontSize: 24, fontWeight: '700', marginBottom: 20, textAlign: 'center' },
  menuContainer: {
    marginBottom: 28,
    paddingHorizontal: 8,
  },
  menuTitle: {
    color: '#9fb3c8',
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 16,
    textAlign: 'center',
  },
  menuGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    gap: 16,
    paddingVertical: 8,
  },
  menuItem: {
    backgroundColor: '#111a30',
    borderRadius: 12,
    padding: 18,
    width: '100%', // Doubled width: full width instead of 48%
    alignItems: 'center',
    borderWidth: 2,
    borderColor: 'transparent',
    minHeight: 100,
    justifyContent: 'center',
  },
  menuItemActive: {
    backgroundColor: '#1a2442',
    borderColor: '#9fb3c8',
  },
  menuIcon: {
    fontSize: 28,
    marginBottom: 10,
  },
  menuItemName: {
    color: '#9fb3c8',
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 4,
    textAlign: 'center',
  },
  menuItemNameActive: {
    color: '#ffffff',
  },
  menuItemDescription: {
    color: '#7a8fa5',
    fontSize: 11,
    textAlign: 'center',
    lineHeight: 14,
  },
  card: { backgroundColor: '#111a30', borderRadius: 12, padding: 16, marginTop: 8 },
  body: { color: '#cfe1ff', lineHeight: 20 },
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
  disclaimerContainer: {
    backgroundColor: '#2c2c2c',
    borderRadius: 8,
    padding: 12,
    marginVertical: 16,
    borderLeftWidth: 4,
    borderLeftColor: '#ffc107',
  },
  disclaimerText: {
    color: '#e0e0e0',
    fontSize: 13,
    lineHeight: 18,
    fontStyle: 'italic',
  },
});
