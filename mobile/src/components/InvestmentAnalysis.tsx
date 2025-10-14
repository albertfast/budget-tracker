import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity } from 'react-native';
import { investmentApi, generateMockInvestmentData, InvestmentRecommendation, RiskProfile, SavingsPotential } from '../services/investmentApi';

export default function InvestmentAnalysis() {
  const [selectedView, setSelectedView] = useState<'overview' | 'recommendations' | 'savings'>('overview');
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(generateMockInvestmentData());

  // Load investment data - using mock data for now, can be switched to API
  useEffect(() => {
    loadInvestmentData();
  }, []);

  const loadInvestmentData = async () => {
    try {
      setLoading(true);
      // For now, use mock data. Uncomment below to use API:
      // const apiData = await investmentApi.getInvestmentRecommendations();
      // setData(transformApiData(apiData));
      setData(generateMockInvestmentData());
    } catch (error) {
      console.error('Failed to load investment data:', error);
      // Fallback to mock data on error
      setData(generateMockInvestmentData());
    } finally {
      setLoading(false);
    }
  };

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
            {rec.recommended_allocation && (
              <View style={styles.detailRow}>
                <Text style={styles.detailLabel}>Monthly Allocation:</Text>
                <Text style={styles.detailValue}>${rec.recommended_allocation}</Text>
              </View>
            )}
            {rec.potential_savings && (
              <View style={styles.detailRow}>
                <Text style={styles.detailLabel}>Potential Savings:</Text>
                <Text style={styles.detailValue}>${rec.potential_savings}/month</Text>
              </View>
            )}
            {rec.expected_return && rec.expected_return > 0 && (
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

          {/* ROI Time Estimates */}
          {rec.expected_return && rec.expected_return > 0 && rec.recommended_allocation && (
            <View style={styles.roiEstimatesContainer}>
              <Text style={styles.roiTitle}>⏱️ ROI Time Estimates</Text>
              <View style={styles.roiGrid}>
                <View style={styles.roiItem}>
                  <Text style={styles.roiPeriod}>1 Year</Text>
                  <Text style={styles.roiPercent}>
                    {(rec.expected_return * 100).toFixed(1)}%
                  </Text>
                  <Text style={styles.roiAmount}>
                    ${(rec.recommended_allocation * 12 * rec.expected_return).toFixed(0)}
                  </Text>
                </View>
                <View style={styles.roiItem}>
                  <Text style={styles.roiPeriod}>3 Years</Text>
                  <Text style={styles.roiPercent}>
                    {((Math.pow(1 + rec.expected_return, 3) - 1) * 100).toFixed(1)}%
                  </Text>
                  <Text style={styles.roiAmount}>
                    ${(rec.recommended_allocation * 12 * 3 * (Math.pow(1 + rec.expected_return, 3) - 1)).toFixed(0)}
                  </Text>
                </View>
                <View style={styles.roiItem}>
                  <Text style={styles.roiPeriod}>5 Years</Text>
                  <Text style={styles.roiPercent}>
                    {((Math.pow(1 + rec.expected_return, 5) - 1) * 100).toFixed(1)}%
                  </Text>
                  <Text style={styles.roiAmount}>
                    ${(rec.recommended_allocation * 12 * 5 * (Math.pow(1 + rec.expected_return, 5) - 1)).toFixed(0)}
                  </Text>
                </View>
                <View style={styles.roiItem}>
                  <Text style={styles.roiPeriod}>10 Years</Text>
                  <Text style={styles.roiPercent}>
                    {((Math.pow(1 + rec.expected_return, 10) - 1) * 100).toFixed(1)}%
                  </Text>
                  <Text style={styles.roiAmount}>
                    ${(rec.recommended_allocation * 12 * 10 * (Math.pow(1 + rec.expected_return, 10) - 1)).toFixed(0)}
                  </Text>
                </View>
              </View>
              <Text style={styles.roiDisclaimer}>
                * Estimates based on {(rec.expected_return * 100).toFixed(1)}% annual return with monthly contributions of ${rec.recommended_allocation}
              </Text>
            </View>
          )}

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

      <ScrollView style={styles.scrollContainer} showsVerticalScrollIndicator={false}>
        {selectedView === 'overview' && renderOverview()}
        {selectedView === 'recommendations' && renderRecommendations()}
        {selectedView === 'savings' && renderSavingsOptimization()}
      </ScrollView>
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
  scrollContainer: {
    maxHeight: 400,
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
  roiEstimatesContainer: {
    backgroundColor: '#0a1425',
    borderRadius: 8,
    padding: 12,
    marginTop: 12,
    borderWidth: 1,
    borderColor: '#1e40af',
  },
  roiTitle: {
    fontSize: 13,
    fontWeight: 'bold',
    color: '#3b82f6',
    marginBottom: 12,
    textAlign: 'center',
  },
  roiGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  roiItem: {
    flex: 1,
    alignItems: 'center',
    paddingHorizontal: 4,
  },
  roiPeriod: {
    fontSize: 11,
    color: '#7a8fa5',
    fontWeight: '600',
    marginBottom: 6,
  },
  roiPercent: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#22c55e',
    marginBottom: 4,
  },
  roiAmount: {
    fontSize: 12,
    color: '#9fb3c8',
    fontWeight: '600',
  },
  roiDisclaimer: {
    fontSize: 10,
    color: '#6b7280',
    fontStyle: 'italic',
    textAlign: 'center',
    marginTop: 8,
    lineHeight: 14,
  },
});