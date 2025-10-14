import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, Alert } from 'react-native';

interface InvestmentRecommendation {
  type: string;
  priority: string;
  title: string;
  description: string;
  recommended_allocation?: number;
  potential_savings?: number;
  expected_return?: number;
  risk_level?: string;
}

interface FinancialProfile {
  monthly_income: number;
  monthly_expenses: number;
  net_monthly: number;
  savings_potential: number;
  risk_level: string;
}

interface InvestmentRecommendationsProps {
  userId?: string;
}

export default function InvestmentRecommendations({ userId }: InvestmentRecommendationsProps) {
  const [recommendations, setRecommendations] = useState<InvestmentRecommendation[]>([]);
  const [financialProfile, setFinancialProfile] = useState<FinancialProfile | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedTab, setSelectedTab] = useState<'recommendations' | 'profile'>('recommendations');

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async () => {
    setLoading(true);
    try {
      // TODO: Replace with actual API call
      // const response = await fetch('/api/v1/insights/investment-recommendations');
      // const data = await response.json();

      // Mock data for demonstration
      const mockData = {
        financial_profile_summary: {
          monthly_income: 4200.00,
          monthly_expenses: 3100.00,
          net_monthly: 1100.00,
          savings_potential: 1350.00,
          risk_level: 'moderate'
        },
        recommendations: [
          {
            type: 'emergency_fund',
            priority: 'high',
            title: 'Build Emergency Fund',
            description: 'Build a $18,600 emergency fund (6 months of expenses)',
            recommended_allocation: 500,
            expected_return: 0.04,
            risk_level: 'very_low'
          },
          {
            type: 'stock_index_fund',
            priority: 'high',
            title: 'Total Stock Market Index Fund',
            description: 'Diversified exposure to the entire stock market',
            recommended_allocation: 600,
            expected_return: 0.10,
            risk_level: 'medium'
          },
          {
            type: 'subscription_optimization',
            priority: 'medium',
            title: 'Optimize Subscriptions',
            description: 'Review $85/month in subscriptions',
            potential_savings: 25.50
          },
          {
            type: 'bond_fund',
            priority: 'medium',
            title: 'Conservative Bond Index Fund',
            description: 'Diversified bond portfolio for steady income',
            recommended_allocation: 250,
            expected_return: 0.05,
            risk_level: 'low'
          }
        ]
      };

      setFinancialProfile(mockData.financial_profile_summary);
      setRecommendations(mockData.recommendations);
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      Alert.alert('Error', 'Failed to load investment recommendations');
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (priority: string): string => {
    switch (priority) {
      case 'high': return '#ef4444';
      case 'medium': return '#f97316';
      case 'low': return '#22c55e';
      default: return '#6b7280';
    }
  };

  const getRiskColor = (riskLevel: string): string => {
    switch (riskLevel) {
      case 'very_low': return '#22c55e';
      case 'low': return '#84cc16';
      case 'medium': return '#f97316';
      case 'high': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const formatRiskLevel = (riskLevel: string): string => {
    return riskLevel.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const renderRecommendation = (rec: InvestmentRecommendation, index: number) => (
    <View key={index} style={styles.recommendationCard}>
      <View style={styles.recommendationHeader}>
        <View style={styles.titleRow}>
          <View style={[styles.priorityDot, { backgroundColor: getPriorityColor(rec.priority) }]} />
          <Text style={styles.recommendationTitle}>{rec.title}</Text>
        </View>
        <View style={styles.priorityBadge}>
          <Text style={[styles.priorityText, { color: getPriorityColor(rec.priority) }]}>
            {rec.priority.toUpperCase()}
          </Text>
        </View>
      </View>

      <Text style={styles.recommendationDescription}>{rec.description}</Text>

      <View style={styles.recommendationDetails}>
        {rec.recommended_allocation && (
          <View style={styles.detailItem}>
            <Text style={styles.detailLabel}>Monthly Allocation:</Text>
            <Text style={styles.detailValue}>${rec.recommended_allocation.toFixed(2)}</Text>
          </View>
        )}

        {rec.potential_savings && (
          <View style={styles.detailItem}>
            <Text style={styles.detailLabel}>Potential Savings:</Text>
            <Text style={[styles.detailValue, { color: '#22c55e' }]}>
              ${rec.potential_savings.toFixed(2)}/month
            </Text>
          </View>
        )}

        {rec.expected_return && (
          <View style={styles.detailItem}>
            <Text style={styles.detailLabel}>Expected Return:</Text>
            <Text style={styles.detailValue}>{(rec.expected_return * 100).toFixed(1)}% annually</Text>
          </View>
        )}

        {rec.risk_level && (
          <View style={styles.detailItem}>
            <Text style={styles.detailLabel}>Risk Level:</Text>
            <Text style={[styles.detailValue, { color: getRiskColor(rec.risk_level) }]}>
              {formatRiskLevel(rec.risk_level)}
            </Text>
          </View>
        )}
      </View>
    </View>
  );

  const renderFinancialProfile = () => (
    <View style={styles.profileContainer}>
      <Text style={styles.profileTitle}>Financial Profile Summary</Text>
      
      <View style={styles.profileCard}>
        <View style={styles.profileItem}>
          <Text style={styles.profileLabel}>Monthly Income:</Text>
          <Text style={[styles.profileValue, { color: '#22c55e' }]}>
            ${financialProfile?.monthly_income.toFixed(2)}
          </Text>
        </View>

        <View style={styles.profileItem}>
          <Text style={styles.profileLabel}>Monthly Expenses:</Text>
          <Text style={[styles.profileValue, { color: '#ef4444' }]}>
            ${financialProfile?.monthly_expenses.toFixed(2)}
          </Text>
        </View>

        <View style={styles.profileItem}>
          <Text style={styles.profileLabel}>Net Monthly:</Text>
          <Text style={[
            styles.profileValue, 
            { color: (financialProfile?.net_monthly || 0) >= 0 ? '#22c55e' : '#ef4444' }
          ]}>
            ${financialProfile?.net_monthly.toFixed(2)}
          </Text>
        </View>

        <View style={styles.profileItem}>
          <Text style={styles.profileLabel}>Savings Potential:</Text>
          <Text style={[styles.profileValue, { color: '#3b82f6' }]}>
            ${financialProfile?.savings_potential.toFixed(2)}
          </Text>
        </View>

        <View style={styles.profileItem}>
          <Text style={styles.profileLabel}>Risk Profile:</Text>
          <Text style={[
            styles.profileValue, 
            { color: getRiskColor(financialProfile?.risk_level || 'medium') }
          ]}>
            {formatRiskLevel(financialProfile?.risk_level || 'medium')}
          </Text>
        </View>
      </View>

      <View style={styles.savingsInsight}>
        <Text style={styles.insightTitle}>💰 Savings Insight</Text>
        <Text style={styles.insightText}>
          You have the potential to save ${financialProfile?.savings_potential.toFixed(2)} per month. 
          That's ${((financialProfile?.savings_potential || 0) * 12).toFixed(2)} annually!
        </Text>
      </View>
    </View>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Investment Recommendations</Text>
      
      {/* Tab Selector */}
      <View style={styles.tabSelector}>
        <TouchableOpacity
          style={[styles.tab, selectedTab === 'recommendations' && styles.activeTab]}
          onPress={() => setSelectedTab('recommendations')}
        >
          <Text style={[
            styles.tabText, 
            selectedTab === 'recommendations' && styles.activeTabText
          ]}>
            Recommendations
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, selectedTab === 'profile' && styles.activeTab]}
          onPress={() => setSelectedTab('profile')}
        >
          <Text style={[
            styles.tabText, 
            selectedTab === 'profile' && styles.activeTabText
          ]}>
            Profile
          </Text>
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.scrollContainer} showsVerticalScrollIndicator={false}>
        {loading ? (
          <View style={styles.loadingContainer}>
            <Text style={styles.loadingText}>Loading recommendations...</Text>
          </View>
        ) : selectedTab === 'recommendations' ? (
          <View>
            {recommendations.map((rec, index) => renderRecommendation(rec, index))}
          </View>
        ) : (
          renderFinancialProfile()
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#111a30',
    borderRadius: 12,
    padding: 16,
    marginHorizontal: 20,
    marginVertical: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 16,
    textAlign: 'center',
    color: '#9fb3c8',
    textShadowColor: '#000000',
    textShadowOffset: { width: 1, height: 1 },
    textShadowRadius: 2,
  },
  tabSelector: {
    flexDirection: 'row',
    backgroundColor: '#0f1930',
    borderRadius: 8,
    padding: 4,
    marginBottom: 16,
  },
  tab: {
    flex: 1,
    paddingVertical: 10,
    alignItems: 'center',
    borderRadius: 6,
  },
  activeTab: {
    backgroundColor: '#3b82f6',
  },
  tabText: {
    fontSize: 14,
    color: '#9fb3c8',
    fontWeight: '500',
    textShadowColor: '#000000',
    textShadowOffset: { width: 0.5, height: 0.5 },
    textShadowRadius: 1,
  },
  activeTabText: {
    color: '#ffffff',
    fontWeight: 'bold',
  },
  scrollContainer: {
    maxHeight: 500,
  },
  recommendationCard: {
    backgroundColor: '#0f1930',
    borderRadius: 8,
    padding: 16,
    marginBottom: 12,
  },
  recommendationHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  titleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  priorityDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 8,
  },
  recommendationTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#9fb3c8',
    flex: 1,
    textShadowColor: '#000000',
    textShadowOffset: { width: 0.5, height: 0.5 },
    textShadowRadius: 1,
  },
  priorityBadge: {
    backgroundColor: '#1e3a8a',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  priorityText: {
    fontSize: 10,
    fontWeight: 'bold',
  },
  recommendationDescription: {
    fontSize: 14,
    color: '#9fb3c8',
    marginBottom: 12,
    lineHeight: 20,
    textShadowColor: '#000000',
    textShadowOffset: { width: 0.5, height: 0.5 },
    textShadowRadius: 1,
  },
  recommendationDetails: {
    backgroundColor: '#1e3a8a',
    borderRadius: 6,
    padding: 12,
  },
  detailItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  detailLabel: {
    fontSize: 12,
    color: '#9fb3c8',
    textShadowColor: '#000000',
    textShadowOffset: { width: 0.5, height: 0.5 },
    textShadowRadius: 1,
  },
  detailValue: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#9fb3c8',
    textShadowColor: '#000000',
    textShadowOffset: { width: 0.5, height: 0.5 },
    textShadowRadius: 1,
  },
  profileContainer: {
    paddingBottom: 20,
  },
  profileTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#9fb3c8',
    marginBottom: 16,
    textAlign: 'center',
    textShadowColor: '#000000',
    textShadowOffset: { width: 1, height: 1 },
    textShadowRadius: 2,
  },
  profileCard: {
    backgroundColor: '#0f1930',
    borderRadius: 8,
    padding: 16,
    marginBottom: 16,
  },
  profileItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  profileLabel: {
    fontSize: 14,
    color: '#9fb3c8',
    textShadowColor: '#000000',
    textShadowOffset: { width: 0.5, height: 0.5 },
    textShadowRadius: 1,
  },
  profileValue: {
    fontSize: 16,
    fontWeight: 'bold',
    textShadowColor: '#000000',
    textShadowOffset: { width: 0.5, height: 0.5 },
    textShadowRadius: 1,
  },
  savingsInsight: {
    backgroundColor: '#0f1930',
    borderRadius: 8,
    padding: 16,
  },
  insightTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#9fb3c8',
    marginBottom: 8,
    textShadowColor: '#000000',
    textShadowOffset: { width: 0.5, height: 0.5 },
    textShadowRadius: 1,
  },
  insightText: {
    fontSize: 13,
    color: '#9fb3c8',
    lineHeight: 18,
    textShadowColor: '#000000',
    textShadowOffset: { width: 0.5, height: 0.5 },
    textShadowRadius: 1,
  },
  loadingContainer: {
    alignItems: 'center',
    paddingVertical: 40,
  },
  loadingText: {
    color: '#9fb3c8',
    fontSize: 16,
    textShadowColor: '#000000',
    textShadowOffset: { width: 0.5, height: 0.5 },
    textShadowRadius: 1,
  },
});