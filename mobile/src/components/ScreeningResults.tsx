/**
 * ScreeningResults Component
 * Displays company screening results with expandable details
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Dimensions,
} from 'react-native';
import {
  CompanyScreeningResult,
  ScreeningSummary,
  getRecommendationColor,
  getGradeColor,
  formatScore,
  getTrendIcon,
} from '../services/screeningApi';

const { width } = Dimensions.get('window');

interface ScreeningResultsProps {
  companies: CompanyScreeningResult[];
  summary: ScreeningSummary;
  onClose: () => void;
}

export const ScreeningResults: React.FC<ScreeningResultsProps> = ({
  companies,
  summary,
  onClose,
}) => {
  const [expandedCompany, setExpandedCompany] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<'score' | 'ticker'>('score');

  // Sort companies
  const sortedCompanies = [...companies].sort((a, b) => {
    if (sortBy === 'score') {
      return b.overall_score - a.overall_score;
    }
    return a.ticker.localeCompare(b.ticker);
  });

  const toggleExpand = (ticker: string) => {
    setExpandedCompany(expandedCompany === ticker ? null : ticker);
  };

  return (
    <ScrollView style={styles.container}>
      {/* Summary Section */}
      <View style={styles.summaryCard}>
        <Text style={styles.summaryTitle}>📊 Screening Summary</Text>
        
        <View style={styles.statsRow}>
          <View style={styles.statBox}>
            <Text style={styles.statValue}>{companies.length}</Text>
            <Text style={styles.statLabel}>Companies</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statValue}>{formatScore(summary.statistics.average_score)}</Text>
            <Text style={styles.statLabel}>Avg Score</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statValue}>{formatScore(summary.statistics.highest_score)}</Text>
            <Text style={styles.statLabel}>Highest</Text>
          </View>
        </View>

        {/* Top Performers */}
        <View style={styles.topPerformers}>
          <Text style={styles.sectionTitle}>🏆 Top Performers</Text>
          {summary.top_performers.slice(0, 3).map((performer, index) => (
            <View key={performer.ticker} style={styles.performerRow}>
              <Text style={styles.performerRank}>#{index + 1}</Text>
              <Text style={styles.performerTicker}>{performer.ticker}</Text>
              <Text style={styles.performerScore}>{formatScore(performer.score)}</Text>
              <View
                style={[
                  styles.performerBadge,
                  { backgroundColor: getRecommendationColor(performer.recommendation) },
                ]}
              >
                <Text style={styles.performerBadgeText}>{performer.recommendation}</Text>
              </View>
            </View>
          ))}
        </View>

        {/* Insights */}
        {summary.insights.length > 0 && (
          <View style={styles.insights}>
            <Text style={styles.sectionTitle}>💡 Key Insights</Text>
            {summary.insights.map((insight, index) => (
              <Text key={index} style={styles.insightText}>
                • {insight}
              </Text>
            ))}
          </View>
        )}
      </View>

      {/* Sort Controls */}
      <View style={styles.sortControls}>
        <Text style={styles.sortLabel}>Sort by:</Text>
        <TouchableOpacity
          style={[styles.sortButton, sortBy === 'score' && styles.sortButtonActive]}
          onPress={() => setSortBy('score')}
        >
          <Text style={[styles.sortButtonText, sortBy === 'score' && styles.sortButtonTextActive]}>
            Score
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.sortButton, sortBy === 'ticker' && styles.sortButtonActive]}
          onPress={() => setSortBy('ticker')}
        >
          <Text style={[styles.sortButtonText, sortBy === 'ticker' && styles.sortButtonTextActive]}>
            Ticker
          </Text>
        </TouchableOpacity>
      </View>

      {/* Company List */}
      <View style={styles.companiesList}>
        {sortedCompanies.map((company, index) => (
          <View key={company.ticker} style={styles.companyCard}>
            <TouchableOpacity
              style={styles.companyHeader}
              onPress={() => toggleExpand(company.ticker)}
            >
              <View style={styles.companyHeaderLeft}>
                <Text style={styles.companyRank}>#{index + 1}</Text>
                <Text style={styles.companyTicker}>{company.ticker}</Text>
                <View
                  style={[
                    styles.gradeBadge,
                    { backgroundColor: getGradeColor(company.overall_grade) },
                  ]}
                >
                  <Text style={styles.gradeBadgeText}>{company.overall_grade}</Text>
                </View>
              </View>
              
              <View style={styles.companyHeaderRight}>
                <Text style={styles.companyScore}>{formatScore(company.overall_score)}</Text>
                <Text style={styles.expandIcon}>
                  {expandedCompany === company.ticker ? '▼' : '▶'}
                </Text>
              </View>
            </TouchableOpacity>

            {/* Recommendation Badge */}
            <View
              style={[
                styles.recommendationBadge,
                { backgroundColor: getRecommendationColor(company.recommendation.action) },
              ]}
            >
              <Text style={styles.recommendationText}>{company.recommendation.action}</Text>
              <Text style={styles.confidenceText}>
                {company.recommendation.confidence}% confidence
              </Text>
            </View>

            {/* Expanded Details */}
            {expandedCompany === company.ticker && (
              <View style={styles.companyDetails}>
                {/* Predictability */}
                <View style={styles.detailSection}>
                  <Text style={styles.detailTitle}>
                    📈 Predictability {getTrendIcon(company.predictability.trend)}
                  </Text>
                  <View style={styles.detailRow}>
                    <Text style={styles.detailLabel}>QoQ Score:</Text>
                    <Text style={styles.detailValue}>
                      {formatScore(company.predictability.qoq_score)}
                    </Text>
                  </View>
                  <View style={styles.detailRow}>
                    <Text style={styles.detailLabel}>QoY Score:</Text>
                    <Text style={styles.detailValue}>
                      {formatScore(company.predictability.qoy_score)}
                    </Text>
                  </View>
                  <View style={styles.detailRow}>
                    <Text style={styles.detailLabel}>Overall:</Text>
                    <Text style={[styles.detailValue, styles.detailValueBold]}>
                      {formatScore(company.predictability.overall_score)} ({company.predictability.grade})
                    </Text>
                  </View>
                  <View style={styles.detailRow}>
                    <Text style={styles.detailLabel}>Trend:</Text>
                    <Text style={styles.detailValue}>
                      {company.predictability.trend} {getTrendIcon(company.predictability.trend)}
                    </Text>
                  </View>
                </View>

                {/* Report Depth */}
                <View style={styles.detailSection}>
                  <Text style={styles.detailTitle}>
                    📄 10-K Report Depth {getTrendIcon(company.report_depth.expansion_trend)}
                  </Text>
                  <View style={styles.detailRow}>
                    <Text style={styles.detailLabel}>Depth Score:</Text>
                    <Text style={[styles.detailValue, styles.detailValueBold]}>
                      {formatScore(company.report_depth.depth_score)} ({company.report_depth.grade})
                    </Text>
                  </View>
                  <View style={styles.detailRow}>
                    <Text style={styles.detailLabel}>Expansion:</Text>
                    <Text style={styles.detailValue}>
                      {company.report_depth.expansion_trend} {getTrendIcon(company.report_depth.expansion_trend)}
                    </Text>
                  </View>
                  
                  <Text style={styles.metricsTitle}>Depth Metrics (YoY Change):</Text>
                  {Object.entries(company.report_depth.depth_metrics).map(([key, value]) => {
                    const change = company.report_depth.yoy_changes[key as keyof typeof company.report_depth.yoy_changes];
                    const changeIcon = change > 0 ? '🔼' : change < 0 ? '🔽' : '➡️';
                    return (
                      <View key={key} style={styles.metricRow}>
                        <Text style={styles.metricLabel}>
                          {key.replace(/_/g, ' ')}:
                        </Text>
                        <Text style={styles.metricValue}>
                          {value} {changeIcon} ({change > 0 ? '+' : ''}{change})
                        </Text>
                      </View>
                    );
                  })}
                </View>

                {/* Quality Components */}
                <View style={styles.detailSection}>
                  <Text style={styles.detailTitle}>🎯 Quality Components</Text>
                  <View style={styles.componentBar}>
                    <Text style={styles.componentLabel}>Predictability (35%):</Text>
                    <View style={styles.barContainer}>
                      <View
                        style={[
                          styles.barFill,
                          { width: `${(company.quality_components.predictability / 35) * 100}%` },
                        ]}
                      />
                    </View>
                    <Text style={styles.componentValue}>
                      {company.quality_components.predictability.toFixed(1)}
                    </Text>
                  </View>
                  <View style={styles.componentBar}>
                    <Text style={styles.componentLabel}>Depth (25%):</Text>
                    <View style={styles.barContainer}>
                      <View
                        style={[
                          styles.barFill,
                          { width: `${(company.quality_components.depth / 25) * 100}%` },
                        ]}
                      />
                    </View>
                    <Text style={styles.componentValue}>
                      {company.quality_components.depth.toFixed(1)}
                    </Text>
                  </View>
                  <View style={styles.componentBar}>
                    <Text style={styles.componentLabel}>Expansion (20%):</Text>
                    <View style={styles.barContainer}>
                      <View
                        style={[
                          styles.barFill,
                          { width: `${(company.quality_components.expansion_trend / 20) * 100}%` },
                        ]}
                      />
                    </View>
                    <Text style={styles.componentValue}>
                      {company.quality_components.expansion_trend.toFixed(1)}
                    </Text>
                  </View>
                  <View style={styles.componentBar}>
                    <Text style={styles.componentLabel}>Growth (20%):</Text>
                    <View style={styles.barContainer}>
                      <View
                        style={[
                          styles.barFill,
                          { width: `${(company.quality_components.growth / 20) * 100}%` },
                        ]}
                      />
                    </View>
                    <Text style={styles.componentValue}>
                      {company.quality_components.growth.toFixed(1)}
                    </Text>
                  </View>
                </View>

                {/* Recommendation Reasons */}
                <View style={styles.detailSection}>
                  <Text style={styles.detailTitle}>💭 Recommendation Reasons</Text>
                  {company.recommendation.reasons.map((reason, idx) => (
                    <Text key={idx} style={styles.reasonText}>
                      • {reason}
                    </Text>
                  ))}
                </View>
              </View>
            )}
          </View>
        ))}
      </View>

      {/* Close Button */}
      <TouchableOpacity style={styles.closeButton} onPress={onClose}>
        <Text style={styles.closeButtonText}>Close Results</Text>
      </TouchableOpacity>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  summaryCard: {
    backgroundColor: '#fff',
    margin: 16,
    padding: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  summaryTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 16,
    color: '#333',
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 16,
  },
  statBox: {
    alignItems: 'center',
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2196F3',
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  topPerformers: {
    marginTop: 16,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
    color: '#333',
  },
  performerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  performerRank: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#666',
    width: 30,
  },
  performerTicker: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    flex: 1,
  },
  performerScore: {
    fontSize: 14,
    color: '#666',
    marginRight: 8,
  },
  performerBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  performerBadgeText: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#fff',
  },
  insights: {
    marginTop: 16,
    padding: 12,
    backgroundColor: '#E3F2FD',
    borderRadius: 8,
  },
  insightText: {
    fontSize: 14,
    color: '#333',
    marginBottom: 4,
    lineHeight: 20,
  },
  sortControls: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    marginBottom: 8,
  },
  sortLabel: {
    fontSize: 14,
    color: '#666',
    marginRight: 8,
  },
  sortButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#eee',
    marginRight: 8,
  },
  sortButtonActive: {
    backgroundColor: '#2196F3',
  },
  sortButtonText: {
    fontSize: 14,
    color: '#666',
  },
  sortButtonTextActive: {
    color: '#fff',
    fontWeight: 'bold',
  },
  companiesList: {
    paddingHorizontal: 16,
  },
  companyCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
    overflow: 'hidden',
  },
  companyHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
  },
  companyHeaderLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  companyRank: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#666',
    marginRight: 12,
  },
  companyTicker: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginRight: 8,
  },
  gradeBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  gradeBadgeText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#fff',
  },
  companyHeaderRight: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  companyScore: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2196F3',
    marginRight: 8,
  },
  expandIcon: {
    fontSize: 12,
    color: '#666',
  },
  recommendationBadge: {
    paddingVertical: 8,
    paddingHorizontal: 16,
    alignItems: 'center',
  },
  recommendationText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#fff',
  },
  confidenceText: {
    fontSize: 12,
    color: '#fff',
    opacity: 0.9,
    marginTop: 2,
  },
  companyDetails: {
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#eee',
  },
  detailSection: {
    marginBottom: 16,
  },
  detailTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 4,
  },
  detailLabel: {
    fontSize: 14,
    color: '#666',
  },
  detailValue: {
    fontSize: 14,
    color: '#333',
  },
  detailValueBold: {
    fontWeight: 'bold',
    color: '#2196F3',
  },
  metricsTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 8,
    marginBottom: 4,
  },
  metricRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 2,
    paddingLeft: 8,
  },
  metricLabel: {
    fontSize: 12,
    color: '#666',
    textTransform: 'capitalize',
  },
  metricValue: {
    fontSize: 12,
    color: '#333',
  },
  componentBar: {
    marginBottom: 12,
  },
  componentLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  barContainer: {
    height: 8,
    backgroundColor: '#eee',
    borderRadius: 4,
    overflow: 'hidden',
    marginBottom: 2,
  },
  barFill: {
    height: '100%',
    backgroundColor: '#2196F3',
  },
  componentValue: {
    fontSize: 12,
    color: '#333',
    textAlign: 'right',
  },
  reasonText: {
    fontSize: 14,
    color: '#333',
    marginBottom: 4,
    lineHeight: 20,
  },
  closeButton: {
    margin: 16,
    padding: 16,
    backgroundColor: '#2196F3',
    borderRadius: 8,
    alignItems: 'center',
  },
  closeButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#fff',
  },
});
