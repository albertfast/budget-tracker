import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity } from 'react-native';
import { investmentApi, generateMockInvestmentData, InvestmentRecommendation, RiskProfile, SavingsPotential } from '../services/investmentApi';

interface InvestmentAnalysisProps {
  transactions?: any[];
}

export default function InvestmentAnalysis({ transactions = [] }: InvestmentAnalysisProps) {
  const [selectedView, setSelectedView] = useState<'overview' | 'recommendations' | 'savings'>('overview');
  const [data, setData] = useState(generateMockInvestmentData());

  useEffect(() => {
    if (transactions.length > 0) {
      const income = transactions.filter(t => t.category === 'Income').reduce((sum, t) => sum + Number(t.amount), 0);
      const expenses = transactions.filter(t => t.category !== 'Income').reduce((sum, t) => sum + Number(t.amount), 0);
      
      const savings = Math.max(0, income - expenses);
      const savingsRate = income > 0 ? savings / income : 0;
      const expenseRatio = income > 0 ? expenses / income : 0;
      
      // Simple logic to determine risk level based on savings rate
      let riskLevel: 'low' | 'moderate' | 'high' = 'moderate';
      if (savingsRate > 0.5) riskLevel = 'low';
      else if (savingsRate > 0.3) riskLevel = 'low';
      else if (savingsRate < 0.1) riskLevel = 'high';

      setData({
        ...data,
        riskProfile: {
          ...data.riskProfile,
          risk_level: riskLevel,
          expense_ratio: expenseRatio
        },
        savingsPotential: {
          ...data.savingsPotential,
          savings_rate: savingsRate,
          current_monthly_savings: savings,
          total_monthly_potential: savings * 1.2, // Assume 20% optimization
          annual_potential: savings * 12
        }
      });
    }
  }, [transactions]);

  const { recommendations, riskProfile, savingsPotential } = data;

  const getRiskEmoji = (riskLevel: string) => {
    switch (riskLevel) {
      case 'very_low': return '🟢';
      case 'low': return '🔵';
      case 'medium': return '🟡';
      case 'high': return '🟠';
      case 'very_high': return '🔴';
      default: return '⚪';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return '#ef4444';
      case 'medium': return '#f59e0b';
      case 'low': return '#10b981';
      default: return '#6b7280';
    }
  };

  const renderOverview = () => (
    <View style={styles.sectionContainer}>
      <Text style={styles.sectionTitle}>💼 Investment Overview</Text>
      
      {/* Risk Profile Card */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>📊 Risk Profile</Text>
        <View style={styles.profileRow}>
          <Text style={styles.profileLabel}>Risk Level:</Text>
          <Text style={[styles.profileValue, { color: getPriorityColor(riskProfile.risk_level === 'low' ? 'low' : riskProfile.risk_level === 'high' ? 'high' : 'medium') }]}>
            {riskProfile.risk_level.toUpperCase()}
          </Text>
        </View>
        <View style={styles.profileRow}>
          <Text style={styles.profileLabel}>Savings Rate:</Text>
          <Text style={styles.profileValue}>{(savingsPotential.savings_rate * 100).toFixed(1)}%</Text>
        </View>
        <View style={styles.profileRow}>
          <Text style={styles.profileLabel}>Expense Ratio:</Text>
          <Text style={styles.profileValue}>{(riskProfile.expense_ratio * 100).toFixed(1)}%</Text>
        </View>
      </View>

      {/* Savings Potential Card */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>💰 Savings Potential</Text>
        <View style={styles.savingsGrid}>
          <View style={styles.savingsItem}>
            <Text style={styles.savingsAmount}>${savingsPotential.current_monthly_savings}</Text>
            <Text style={styles.savingsLabel}>Current Monthly</Text>
          </View>
          <View style={styles.savingsItem}>
            <Text style={styles.savingsAmount}>${savingsPotential.total_monthly_potential}</Text>
            <Text style={styles.savingsLabel}>Potential Monthly</Text>
          </View>
          <View style={styles.savingsItem}>
            <Text style={styles.savingsAmount}>${savingsPotential.annual_potential.toLocaleString()}</Text>
            <Text style={styles.savingsLabel}>Annual Potential</Text>
          </View>
        </View>
      </View>
    </View>
  );

  const renderRecommendations = () => (
    <View style={styles.sectionContainer}>
      <Text style={styles.sectionTitle}>🎯 Investment Recommendations</Text>
      {recommendations.map((rec, index) => (
        <View key={index} style={styles.recommendationCard}>
          <View style={styles.recommendationHeader}>
            <Text style={styles.recommendationTitle}>{rec.title}</Text>
            <View style={[styles.priorityBadge, { backgroundColor: getPriorityColor(rec.priority) }]}>
              <Text style={styles.priorityText}>{rec.priority.toUpperCase()}</Text>
            </View>
          </View>
          
          <Text style={styles.recommendationDescription}>{rec.description}</Text>
          
          <View style={styles.recommendationDetails}>
            {rec.recommended_allocation !== undefined && rec.recommended_allocation > 0 && (
              <View style={styles.detailRow}>
                <Text style={styles.detailLabel}>Monthly Allocation:</Text>
                <Text style={styles.detailValue}>${rec.recommended_allocation}</Text>
              </View>
            )}
            {rec.potential_savings !== undefined && rec.potential_savings > 0 && (
              <View style={styles.detailRow}>
                <Text style={styles.detailLabel}>Potential Savings:</Text>
                <Text style={styles.detailValue}>${rec.potential_savings}/month</Text>
              </View>
            )}
            {rec.expected_return !== undefined && rec.expected_return > 0 && (
              <View style={styles.detailRow}>
                <Text style={styles.detailLabel}>Expected Return:</Text>
                <Text style={styles.detailValue}>{(rec.expected_return * 100).toFixed(1)}%</Text>
              </View>
            )}
            <View style={styles.detailRow}>
              <Text style={styles.detailLabel}>Risk Level:</Text>
              <View style={styles.riskContainer}>
                <Text style={styles.riskEmoji}>{getRiskEmoji(rec.risk_level || 'none')}</Text>
                <Text style={styles.detailValue}>{(rec.risk_level || 'none').replace('_', ' ').toUpperCase()}</Text>
              </View>
            </View>
          </View>

          {rec.action_items && (
            <View style={styles.actionItemsContainer}>
              <Text style={styles.actionItemsTitle}>Action Items:</Text>
              {rec.action_items.map((item, itemIndex) => (
                <Text key={itemIndex} style={styles.actionItem}>• {item}</Text>
              ))}
            </View>
          )}
        </View>
      ))}
    </View>
  );

  const renderSavingsOptimization = () => (
    <View style={styles.sectionContainer}>
      <Text style={styles.sectionTitle}>📈 Savings Optimization</Text>
      
      <View style={styles.optimizationCard}>
        <Text style={styles.cardTitle}>Current vs Potential Savings</Text>
        
        <View style={styles.comparisonContainer}>
          <View style={styles.comparisonItem}>
            <Text style={styles.comparisonLabel}>Current Monthly Savings</Text>
            <Text style={styles.comparisonAmount}>${savingsPotential.current_monthly_savings}</Text>
            <View style={styles.progressBar}>
              <View 
                style={[
                  styles.progressFill, 
                  { 
                    width: `${(savingsPotential.current_monthly_savings / savingsPotential.total_monthly_potential) * 100}%`,
                    backgroundColor: '#10b981'
                  }
                ]} 
              />
            </View>
          </View>
          
          <View style={styles.comparisonItem}>
            <Text style={styles.comparisonLabel}>Potential Monthly Savings</Text>
            <Text style={styles.comparisonAmount}>${savingsPotential.total_monthly_potential}</Text>
            <View style={styles.progressBar}>
              <View style={[styles.progressFill, { width: '100%', backgroundColor: '#3b82f6' }]} />
            </View>
          </View>
        </View>

        <View style={styles.optimizationBreakdown}>
          <Text style={styles.breakdownTitle}>Optimization Opportunities:</Text>
          <View style={styles.breakdownRow}>
            <Text style={styles.breakdownLabel}>Subscription Optimization:</Text>
            <Text style={styles.breakdownValue}>+${savingsPotential.subscription_optimization_savings}</Text>
          </View>
          <View style={styles.breakdownRow}>
            <Text style={styles.breakdownLabel}>Category Optimization:</Text>
            <Text style={styles.breakdownValue}>+${savingsPotential.category_optimization_savings}</Text>
          </View>
          <View style={[styles.breakdownRow, styles.breakdownTotal]}>
            <Text style={styles.breakdownTotalLabel}>Additional Monthly Potential:</Text>
            <Text style={styles.breakdownTotalValue}>
              +${savingsPotential.subscription_optimization_savings + savingsPotential.category_optimization_savings}
            </Text>
          </View>
        </View>
      </View>
    </View>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Investment Analysis</Text>
      
      {/* Tab Navigation */}
      <View style={styles.tabContainer}>
        <TouchableOpacity
          style={[styles.tab, selectedView === 'overview' && styles.tabActive]}
          onPress={() => setSelectedView('overview')}
        >
          <Text style={[styles.tabText, selectedView === 'overview' && styles.tabTextActive]}>Overview</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, selectedView === 'recommendations' && styles.tabActive]}
          onPress={() => setSelectedView('recommendations')}
        >
          <Text style={[styles.tabText, selectedView === 'recommendations' && styles.tabTextActive]}>Recommendations</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, selectedView === 'savings' && styles.tabActive]}
          onPress={() => setSelectedView('savings')}
        >
          <Text style={[styles.tabText, selectedView === 'savings' && styles.tabTextActive]}>Savings</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.contentContainer}>
        {selectedView === 'overview' && renderOverview()}
        {selectedView === 'recommendations' && renderRecommendations()}
        {selectedView === 'savings' && renderSavingsOptimization()}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#111a30',
    borderRadius: 12,
    padding: 16,
    marginHorizontal: 40,
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
  tabContainer: {
    flexDirection: 'row',
    backgroundColor: '#0f1930',
    borderRadius: 8,
    padding: 4,
    marginBottom: 16,
  },
  tab: {
    flex: 1,
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 6,
    alignItems: 'center',
  },
  tabActive: {
    backgroundColor: '#1e40af',
  },
  tabText: {
    fontSize: 12,
    color: '#7a8fa5',
    fontWeight: '500',
  },
  tabTextActive: {
    color: '#ffffff',
    fontWeight: '600',
  },
  contentContainer: {
    // Removed fixed height to allow full expansion
  },
  sectionContainer: {
    flex: 1,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#9fb3c8',
    marginBottom: 12,
    textAlign: 'center',
  },
  card: {
    backgroundColor: '#0f1930',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#1e3a8a',
  },
  cardTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#9fb3c8',
    marginBottom: 8,
  },
  profileRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  profileLabel: {
    fontSize: 13,
    color: '#7a8fa5',
  },
  profileValue: {
    fontSize: 13,
    fontWeight: '600',
    color: '#9fb3c8',
  },
  savingsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  savingsItem: {
    alignItems: 'center',
    flex: 1,
  },
  savingsAmount: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#22c55e',
    marginBottom: 4,
  },
  savingsLabel: {
    fontSize: 10,
    color: '#7a8fa5',
    textAlign: 'center',
  },
  recommendationCard: {
    backgroundColor: '#0f1930',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#1e3a8a',
  },
  recommendationHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  recommendationTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#9fb3c8',
    flex: 1,
  },
  priorityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10,
    marginLeft: 8,
  },
  priorityText: {
    fontSize: 10,
    color: '#ffffff',
    fontWeight: 'bold',
  },
  recommendationDescription: {
    fontSize: 12,
    color: '#7a8fa5',
    marginBottom: 8,
    lineHeight: 16,
  },
  recommendationDetails: {
    marginBottom: 8,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  detailLabel: {
    fontSize: 12,
    color: '#7a8fa5',
  },
  detailValue: {
    fontSize: 12,
    fontWeight: '600',
    color: '#9fb3c8',
  },
  riskContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  riskEmoji: {
    fontSize: 12,
    marginRight: 4,
  },
  actionItemsContainer: {
    backgroundColor: '#0a1425',
    borderRadius: 6,
    padding: 8,
    marginTop: 8,
  },
  actionItemsTitle: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#9fb3c8',
    marginBottom: 6,
  },
  actionItem: {
    fontSize: 11,
    color: '#7a8fa5',
    marginBottom: 2,
    paddingLeft: 4,
  },
  optimizationCard: {
    backgroundColor: '#0f1930',
    borderRadius: 8,
    padding: 12,
    borderWidth: 1,
    borderColor: '#1e3a8a',
  },
  comparisonContainer: {
    marginBottom: 16,
  },
  comparisonItem: {
    marginBottom: 12,
  },
  comparisonLabel: {
    fontSize: 12,
    color: '#7a8fa5',
    marginBottom: 4,
  },
  comparisonAmount: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#9fb3c8',
    marginBottom: 6,
  },
  progressBar: {
    height: 6,
    backgroundColor: '#1e3a8a',
    borderRadius: 3,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    borderRadius: 3,
  },
  optimizationBreakdown: {
    borderTopWidth: 1,
    borderTopColor: '#1e3a8a',
    paddingTop: 12,
  },
  breakdownTitle: {
    fontSize: 13,
    fontWeight: 'bold',
    color: '#9fb3c8',
    marginBottom: 8,
  },
  breakdownRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  breakdownLabel: {
    fontSize: 12,
    color: '#7a8fa5',
  },
  breakdownValue: {
    fontSize: 12,
    fontWeight: '600',
    color: '#22c55e',
  },
  breakdownTotal: {
    borderTopWidth: 1,
    borderTopColor: '#1e3a8a',
    paddingTop: 8,
    marginTop: 8,
  },
  breakdownTotalLabel: {
    fontSize: 13,
    fontWeight: 'bold',
    color: '#9fb3c8',
  },
  breakdownTotalValue: {
    fontSize: 13,
    fontWeight: 'bold',
    color: '#22c55e',
  },
});