import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Pressable,
  ActivityIndicator,
  Alert,
  Platform,
} from 'react-native';
import * as DocumentPicker from 'expo-document-picker';
import SwipeNavigationWrapper from '@/components/SwipeNavigationWrapper';
import { analyzeFinancialsFromFile, CompanyAnalysis, AnalysisResults } from '@/services/financialAnalysisApi';
import { useNavigation } from '@react-navigation/native';

export default function FinancialAnalysisScreen() {
  const navigation = useNavigation();
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<AnalysisResults | null>(null);
  const [selectedFile, setSelectedFile] = useState<any>(null);

  const pickFile = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: ['text/csv', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel', 'application/xml', 'text/html', 'application/json'],
        copyToCacheDirectory: true,
      });

      if (result.assets && result.assets.length > 0) {
        setSelectedFile(result.assets[0]);
        setResults(null); // Clear previous results
      }
    } catch (err) {
      Alert.alert('Error', 'Failed to pick file');
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      Alert.alert('No File', 'Please select a file first');
      return;
    }

    setLoading(true);
    try {
      // In a real app, we would get the token from auth service
      const token = 'mock-token'; 
      const response = await analyzeFinancialsFromFile(
        selectedFile.uri,
        selectedFile.name,
        token
      );
      
      setResults(response.analysis_results);
    } catch (error: any) {
      Alert.alert('Analysis Failed', error.message || 'Unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  const renderCompanyCard = (company: CompanyAnalysis, index: number) => {
    return (
      <View key={company.ticker} style={styles.companyCard}>
        <View style={styles.companyHeader}>
          <View style={styles.rankBadge}>
            <Text style={styles.rankText}>#{index + 1}</Text>
          </View>
          <View style={{ flex: 1, marginLeft: 12 }}>
            <Text style={styles.ticker}>{company.ticker}</Text>
            <Text style={styles.companyName}>{company.company_name || 'Unknown Company'}</Text>
          </View>
          <View style={[styles.gradeBadge, { backgroundColor: getGradeColor(company.quality_score.grade) }]}>
            <Text style={styles.gradeText}>{company.quality_score.grade}</Text>
          </View>
        </View>

        <View style={styles.scoreRow}>
          <View style={styles.scoreItem}>
            <Text style={styles.scoreLabel}>Overall Score</Text>
            <Text style={styles.scoreValue}>{company.overall_score.toFixed(1)}</Text>
          </View>
          <View style={styles.scoreItem}>
            <Text style={styles.scoreLabel}>Predictability</Text>
            <Text style={styles.scoreValue}>{company.predictability.overall_predictability.toFixed(1)}</Text>
          </View>
          <View style={styles.scoreItem}>
            <Text style={styles.scoreLabel}>Report Depth</Text>
            <Text style={styles.scoreValue}>{company.report_depth.depth_score.toFixed(1)}</Text>
          </View>
        </View>

        <View style={[styles.recommendationBanner, { backgroundColor: getRecommendationColor(company.recommendation.action) }]}>
          <Text style={styles.recommendationText}>{company.recommendation.action}</Text>
          <Text style={styles.confidenceText}>{company.recommendation.confidence}% Confidence</Text>
        </View>

        <View style={styles.priceGrid}>
          <View style={styles.priceItem}>
            <Text style={styles.priceLabel}>Current</Text>
            <Text style={styles.priceValue}>${company.price_analysis.current_price?.toFixed(2) || 'N/A'}</Text>
          </View>
          <View style={styles.priceItem}>
            <Text style={styles.priceLabel}>Buy Point</Text>
            <Text style={styles.priceValue}>${company.price_analysis.buy_point?.toFixed(2) || 'N/A'}</Text>
          </View>
          <View style={styles.priceItem}>
            <Text style={styles.priceLabel}>Target</Text>
            <Text style={styles.priceValue}>${company.price_analysis.target_price?.toFixed(2) || 'N/A'}</Text>
          </View>
          <View style={styles.priceItem}>
            <Text style={styles.priceLabel}>Stop Loss</Text>
            <Text style={styles.priceValue}>${company.price_analysis.stop_loss?.toFixed(2) || 'N/A'}</Text>
          </View>
        </View>
      </View>
    );
  };

  const getGradeColor = (grade: string) => {
    if (grade.startsWith('A')) return '#4CAF50';
    if (grade.startsWith('B')) return '#8BC34A';
    if (grade.startsWith('C')) return '#FFC107';
    if (grade.startsWith('D')) return '#FF5722';
    return '#9E9E9E';
  };

  const getRecommendationColor = (action: string) => {
    switch (action) {
      case 'STRONG BUY': return '#00C853';
      case 'BUY': return '#76FF03';
      case 'HOLD': return '#FFEB3B';
      case 'WATCH': return '#FF9800';
      case 'AVOID': return '#F44336';
      default: return '#9E9E9E';
    }
  };

  return (
    <SwipeNavigationWrapper currentTab="FinancialAnalysis">
      <ScrollView style={styles.screen} contentContainerStyle={{ paddingBottom: 40 }}>
        <Text style={styles.headerTitle}>Financial Analysis Tool</Text>
        <Text style={styles.headerSubtitle}>
          Upload financial data for comprehensive quality scoring and buy/sell recommendations
        </Text>

        <Pressable 
          style={styles.navButton}
          onPress={() => navigation.navigate('FinancialAnalysisTwo' as never)}
        >
          <Text style={styles.navButtonText}>Go to Advanced Analysis (Page 2) →</Text>
        </Pressable>

        <View style={styles.card}>
          <Text style={styles.cardTitle}>Upload Financial Data</Text>
          <Text style={styles.cardDescription}>
            Supported formats: Barchart (CSV), Morningstar (CSV/Excel), SEC EDGAR (XBRL/HTML)
          </Text>
          
          <Pressable style={styles.uploadButton} onPress={pickFile}>
            <Text style={styles.uploadButtonText}>
              {selectedFile ? '📄 ' + selectedFile.name : 'Select File...'}
            </Text>
          </Pressable>

          {selectedFile && (
            <Pressable 
              style={[styles.analyzeButton, loading && styles.disabledButton]} 
              onPress={handleAnalyze}
              disabled={loading}
            >
              {loading ? (
                <ActivityIndicator color="white" />
              ) : (
                <Text style={styles.analyzeButtonText}>Analyze Financials</Text>
              )}
            </Pressable>
          )}
        </View>

        {results && (
          <View style={styles.resultsContainer}>
            <Text style={styles.resultsTitle}>Analysis Results</Text>
            <Text style={styles.resultsSubtitle}>
              {results.total_companies} companies analyzed • Sorted by Quality Score
            </Text>
            
            {results.companies.map((company, index) => renderCompanyCard(company, index))}
          </View>
        )}

        <View style={styles.infoCard}>
          <Text style={styles.infoTitle}>How it works</Text>
          <Text style={styles.infoText}>
            • Predictability: Measures consistency of revenue/earnings growth{'\n'}
            • Report Depth: Analyzes 10-K disclosure quality{'\n'}
            • Quality Score: Weighted average of all metrics{'\n'}
            • Buy/Sell Points: Calculated using technical support/resistance
          </Text>
        </View>
      </ScrollView>
    </SwipeNavigationWrapper>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: '#0b1220',
    padding: 20,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    textAlign: 'center',
    marginBottom: 8,
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#9bb4da',
    textAlign: 'center',
    marginBottom: 24,
    lineHeight: 20,
  },
  navButton: {
    backgroundColor: '#1a2442',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#3b82f6',
  },
  navButtonText: {
    color: '#3b82f6',
    fontWeight: '600',
    fontSize: 14,
  },
  card: {
    backgroundColor: '#111a30',
    borderRadius: 12,
    padding: 20,
    marginBottom: 20,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 8,
  },
  cardDescription: {
    fontSize: 14,
    color: '#9bb4da',
    marginBottom: 16,
  },
  uploadButton: {
    borderWidth: 2,
    borderColor: '#3b82f6',
    borderStyle: 'dashed',
    borderRadius: 12,
    padding: 20,
    alignItems: 'center',
    marginBottom: 16,
    backgroundColor: 'rgba(59, 130, 246, 0.1)',
  },
  uploadButtonText: {
    color: '#3b82f6',
    fontSize: 16,
    fontWeight: '600',
  },
  analyzeButton: {
    backgroundColor: '#3b82f6',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
  },
  disabledButton: {
    opacity: 0.6,
  },
  analyzeButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  resultsContainer: {
    marginTop: 8,
  },
  resultsTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 4,
  },
  resultsSubtitle: {
    fontSize: 14,
    color: '#9bb4da',
    marginBottom: 16,
  },
  companyCard: {
    backgroundColor: '#111a30',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    borderLeftWidth: 4,
    borderLeftColor: '#3b82f6',
  },
  companyHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  rankBadge: {
    backgroundColor: '#1a2442',
    width: 32,
    height: 32,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
  },
  rankText: {
    color: '#3b82f6',
    fontWeight: 'bold',
  },
  ticker: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  companyName: {
    color: '#9bb4da',
    fontSize: 12,
  },
  gradeBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  gradeText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 12,
  },
  scoreRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
    backgroundColor: '#0f1930',
    padding: 12,
    borderRadius: 8,
  },
  scoreItem: {
    alignItems: 'center',
  },
  scoreLabel: {
    color: '#7a8fa5',
    fontSize: 11,
    marginBottom: 4,
  },
  scoreValue: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 16,
  },
  recommendationBanner: {
    padding: 8,
    borderRadius: 8,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  recommendationText: {
    color: '#000',
    fontWeight: 'bold',
    fontSize: 14,
  },
  confidenceText: {
    color: 'rgba(0,0,0,0.7)',
    fontSize: 12,
    fontWeight: '600',
  },
  priceGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  priceItem: {
    flex: 1,
    minWidth: '45%',
    backgroundColor: '#0f1930',
    padding: 8,
    borderRadius: 6,
  },
  priceLabel: {
    color: '#7a8fa5',
    fontSize: 11,
    marginBottom: 2,
  },
  priceValue: {
    color: 'white',
    fontWeight: '600',
  },
  infoCard: {
    backgroundColor: '#1a2442',
    borderRadius: 12,
    padding: 16,
    marginTop: 8,
  },
  infoTitle: {
    color: '#9bb4da',
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  infoText: {
    color: '#7a8fa5',
    fontSize: 12,
    lineHeight: 18,
  },
});
