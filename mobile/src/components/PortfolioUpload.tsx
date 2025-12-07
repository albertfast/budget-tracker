import React, { useState } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, Alert, ScrollView } from 'react-native';
import * as DocumentPicker from 'expo-document-picker';
import { investmentApi } from '../services/investmentApi';

interface PortfolioHolding {
  symbol: string;
  quantity: number;
  current_price: number;
  current_value: number;
  gain_loss: number;
  gain_loss_percent: number;
  recommendation: string;
  confidence: number;
  target_price: number;
}

interface PortfolioAnalysisResponse {
  portfolio_summary: {
    total_value: number;
    total_gain_loss: number;
    item_count: number;
  };
  holdings: PortfolioHolding[];
}

export default function PortfolioUpload() {
  const [uploading, setUploading] = useState(false);
  const [analysis, setAnalysis] = useState<any | null>(null);
  const [documentType, setDocumentType] = useState<string>('');
  const [showSampleFormat, setShowSampleFormat] = useState(false);
  const [selectedFormat, setSelectedFormat] = useState<'portfolio' | 'profit_loss' | 'balance_sheet' | 'pink_slip'>('portfolio');

  const pickDocument = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: 'text/csv',
        copyToCacheDirectory: true,
      });

      if (!result.canceled && result.assets[0]) {
        uploadDocument(result.assets[0]);
      }
    } catch (error) {
      console.error('Error picking document:', error);
      Alert.alert('Error', 'Failed to pick file');
    }
  };

  const uploadDocument = async (file: any) => {
    try {
      setUploading(true);
      const response = await investmentApi.uploadPortfolio(file);
      setAnalysis(response);
      setDocumentType(response.document_type || 'Portfolio');
      
      const itemCount = response.holdings?.length || 
                       response.current_positions?.length || 
                       response.trade_summary?.total_trades || 0;
      
      Alert.alert('Success', `${response.document_type || 'Document'} analyzed!`);
    } catch (error) {
      console.error('Upload error:', error);
      Alert.alert('Upload Failed', 'Please check your CSV format and try again.');
    } finally {
      setUploading(false);
    }
  };

  const getRecommendationColor = (recommendation: string) => {
    switch (recommendation.toLowerCase()) {
      case 'strong_buy': return '#16a34a';
      case 'buy': return '#22c55e';
      case 'hold': return '#eab308';
      case 'sell': return '#f97316';
      case 'strong_sell': return '#dc2626';
      default: return '#6b7280';
    }
  };

  const formatRecommendation = (recommendation: string) => {
    return recommendation.replace('_', ' ').toUpperCase();
  };

  const renderSampleFormat = () => {
    const formats = {
      portfolio: {
        title: '📊 Portfolio Format',
        headers: ['Symbol', 'Quantity', 'Cost Basis'],
        rows: [
          ['AAPL', '10', '150.00'],
          ['MSFT', '5', '280.50'],
          ['GOOGL', '2', '2500.00']
        ],
        notes: 'Symbol: Stock ticker\nQuantity: Shares owned\nCost Basis: Purchase price/share'
      },
      profit_loss: {
        title: '💰 Profit & Loss Statement',
        headers: ['Category', 'Amount'],
        rows: [
          ['Revenue', '500000'],
          ['Cost of Goods Sold', '200000'],
          ['Operating Expenses', '150000'],
          ['Net Income', '150000']
        ],
        notes: 'Category: Revenue/Expense items\nAmount: Dollar amount\nPeriod: Optional date/period'
      },
      balance_sheet: {
        title: '📋 Balance Sheet',
        headers: ['Account', 'Amount'],
        rows: [
          ['Current Assets', '100000'],
          ['Total Assets', '250000'],
          ['Current Liabilities', '50000'],
          ['Total Equity', '150000']
        ],
        notes: 'Account: Asset/Liability/Equity items\nAmount: Dollar amount\nDate: Optional as-of date'
      },
      pink_slip: {
        title: '🎫 Trade Confirmations',
        headers: ['Symbol', 'Shares', 'Price', 'Commission', 'Date', 'Type'],
        rows: [
          ['AAPL', '10', '150.00', '0.50', '2024-01-15', 'buy'],
          ['MSFT', '5', '280.50', '0.25', '2024-02-20', 'buy'],
          ['GOOGL', '2', '2500.00', '1.00', '2024-03-10', 'sell']
        ],
        notes: 'Symbol: Ticker\nShares: Quantity\nPrice: Execution price\nType: buy/sell'
      }
    };

    const format = formats[selectedFormat];

    return (
      <View style={styles.sampleContainer}>
        {/* Format Tabs */}
        <View style={styles.formatTabs}>
          <TouchableOpacity 
            style={[styles.formatTab, selectedFormat === 'portfolio' && styles.formatTabActive]}
            onPress={() => setSelectedFormat('portfolio')}
          >
            <Text style={[styles.formatTabText, selectedFormat === 'portfolio' && styles.formatTabTextActive]}>
              Portfolio
            </Text>
          </TouchableOpacity>
          <TouchableOpacity 
            style={[styles.formatTab, selectedFormat === 'profit_loss' && styles.formatTabActive]}
            onPress={() => setSelectedFormat('profit_loss')}
          >
            <Text style={[styles.formatTabText, selectedFormat === 'profit_loss' && styles.formatTabTextActive]}>
              P&L
            </Text>
          </TouchableOpacity>
          <TouchableOpacity 
            style={[styles.formatTab, selectedFormat === 'balance_sheet' && styles.formatTabActive]}
            onPress={() => setSelectedFormat('balance_sheet')}
          >
            <Text style={[styles.formatTabText, selectedFormat === 'balance_sheet' && styles.formatTabTextActive]}>
              Balance Sheet
            </Text>
          </TouchableOpacity>
          <TouchableOpacity 
            style={[styles.formatTab, selectedFormat === 'pink_slip' && styles.formatTabActive]}
            onPress={() => setSelectedFormat('pink_slip')}
          >
            <Text style={[styles.formatTabText, selectedFormat === 'pink_slip' && styles.formatTabTextActive]}>
              Pink Slips
            </Text>
          </TouchableOpacity>
        </View>

        <Text style={styles.sampleTitle}>{format.title}</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          <View style={styles.sampleTable}>
            <View style={styles.sampleHeader}>
              {format.headers.map((header, i) => (
                <Text key={i} style={styles.sampleHeaderText}>{header}</Text>
              ))}
            </View>
            {format.rows.map((row, i) => (
              <View key={i} style={styles.sampleRow}>
                {row.map((cell, j) => (
                  <Text key={j} style={styles.sampleCell}>{cell}</Text>
                ))}
              </View>
            ))}
          </View>
        </ScrollView>
        <Text style={styles.sampleNote}>{format.notes}</Text>
      </View>
    );
  };

  const renderAnalysis = () => {
    if (!analysis) return null;

    const { portfolio_summary, holdings } = analysis;

    return (
      <ScrollView style={styles.analysisContainer} showsVerticalScrollIndicator={false}>
        {/* Portfolio Summary */}
        <View style={styles.summaryCard}>
          <Text style={styles.summaryTitle}>📊 Portfolio Summary</Text>
          <View style={styles.summaryGrid}>
            <View style={styles.summaryItem}>
              <Text style={styles.summaryLabel}>Total Value</Text>
              <Text style={styles.summaryValue}>${portfolio_summary.total_value.toLocaleString()}</Text>
            </View>
            <View style={styles.summaryItem}>
              <Text style={styles.summaryLabel}>Total P&L</Text>
              <Text style={[
                styles.summaryValue,
                { color: portfolio_summary.total_gain_loss >= 0 ? '#22c55e' : '#ef4444' }
              ]}>
                {portfolio_summary.total_gain_loss >= 0 ? '+' : ''}${portfolio_summary.total_gain_loss.toLocaleString()}
              </Text>
            </View>
            <View style={styles.summaryItem}>
              <Text style={styles.summaryLabel}>Holdings</Text>
              <Text style={styles.summaryValue}>{portfolio_summary.item_count}</Text>
            </View>
          </View>
        </View>

        {/* Individual Holdings */}
        <Text style={styles.holdingsTitle}>🎯 Individual Holdings Analysis</Text>
        {holdings.map((holding: any, index: number) => (
          <View key={index} style={styles.holdingCard}>
            <View style={styles.holdingHeader}>
              <Text style={styles.holdingSymbol}>{holding.symbol}</Text>
              <View style={[
                styles.recommendationBadge,
                { backgroundColor: getRecommendationColor(holding.recommendation) }
              ]}>
                <Text style={styles.recommendationText}>
                  {formatRecommendation(holding.recommendation)}
                </Text>
              </View>
            </View>

            <View style={styles.holdingDetails}>
              <View style={styles.holdingRow}>
                <Text style={styles.holdingLabel}>Quantity:</Text>
                <Text style={styles.holdingValue}>{holding.quantity} shares</Text>
              </View>
              <View style={styles.holdingRow}>
                <Text style={styles.holdingLabel}>Current Price:</Text>
                <Text style={styles.holdingValue}>${holding.current_price.toFixed(2)}</Text>
              </View>
              <View style={styles.holdingRow}>
                <Text style={styles.holdingLabel}>Current Value:</Text>
                <Text style={styles.holdingValue}>${holding.current_value.toLocaleString()}</Text>
              </View>
              <View style={styles.holdingRow}>
                <Text style={styles.holdingLabel}>Gain/Loss:</Text>
                <Text style={[
                  styles.holdingValue,
                  { color: holding.gain_loss >= 0 ? '#22c55e' : '#ef4444' }
                ]}>
                  {holding.gain_loss >= 0 ? '+' : ''}${holding.gain_loss.toFixed(2)} 
                  ({holding.gain_loss_percent >= 0 ? '+' : ''}{holding.gain_loss_percent.toFixed(1)}%)
                </Text>
              </View>
              <View style={styles.holdingRow}>
                <Text style={styles.holdingLabel}>Target Price:</Text>
                <Text style={styles.holdingValue}>${holding.target_price.toFixed(2)}</Text>
              </View>
              <View style={styles.holdingRow}>
                <Text style={styles.holdingLabel}>Confidence:</Text>
                <Text style={styles.holdingValue}>{holding.confidence}%</Text>
              </View>
            </View>
          </View>
        ))}
      </ScrollView>
    );
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>� Financial Document Analysis</Text>
      <Text style={styles.subtitle}>Upload Portfolio, P&L Statements, Balance Sheets, or Pink Slips for AI-powered analysis</Text>

      {/* Upload Section */}
      <View style={styles.uploadSection}>
        <TouchableOpacity
          style={[styles.uploadButton, uploading && styles.uploadButtonDisabled]}
          onPress={pickDocument}
          disabled={uploading}
        >
          <Text style={styles.uploadButtonText}>
            {uploading ? '📤 Analyzing...' : '📁 Upload Financial Document (CSV)'}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.formatButton}
          onPress={() => setShowSampleFormat(!showSampleFormat)}
        >
          <Text style={styles.formatButtonText}>
            {showSampleFormat ? '▼' : '▶'} View Required Format
          </Text>
        </TouchableOpacity>
      </View>

      {/* Sample Format */}
      {showSampleFormat && renderSampleFormat()}

      {/* Analysis Results */}
      {analysis && renderAnalysis()}

      {/* Instructions */}
      {!analysis && !showSampleFormat && (
        <View style={styles.instructionsContainer}>
          <Text style={styles.instructionsTitle}>🔍 Supported Documents:</Text>
          <Text style={styles.instructionItem}>📊 <Text style={{fontWeight: 'bold'}}>Portfolio:</Text> Get investment recommendations & analysis</Text>
          <Text style={styles.instructionItem}>💰 <Text style={{fontWeight: 'bold'}}>Profit & Loss:</Text> Profitability metrics & optimization tips</Text>
          <Text style={styles.instructionItem}>📋 <Text style={{fontWeight: 'bold'}}>Balance Sheet:</Text> Financial health & liquidity analysis</Text>
          <Text style={styles.instructionItem}>🎫 <Text style={{fontWeight: 'bold'}}>Pink Slips:</Text> Trade history & position analysis</Text>
          <Text style={[styles.instructionItem, {marginTop: 8}]}>✨ AI automatically detects document type</Text>
        </View>
      )}
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
    fontSize: 20,
    fontWeight: 'bold',
    color: '#9fb3c8',
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 14,
    color: '#7a8fa5',
    textAlign: 'center',
    marginBottom: 20,
    lineHeight: 20,
  },
  formatTabs: {
    flexDirection: 'row',
    marginBottom: 16,
    borderRadius: 8,
    overflow: 'hidden',
  },
  formatTab: {
    flex: 1,
    paddingVertical: 8,
    paddingHorizontal: 4,
    backgroundColor: '#0f1930',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#1e3a8a',
  },
  formatTabActive: {
    backgroundColor: '#1e40af',
  },
  formatTabText: {
    fontSize: 10,
    color: '#7a8fa5',
    fontWeight: '500',
  },
  formatTabTextActive: {
    color: '#ffffff',
    fontWeight: 'bold',
  },
  uploadSection: {
    alignItems: 'center',
    marginBottom: 20,
  },
  uploadButton: {
    backgroundColor: '#1e40af',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    marginBottom: 12,
    minWidth: 200,
    alignItems: 'center',
  },
  uploadButtonDisabled: {
    backgroundColor: '#374151',
  },
  uploadButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  formatButton: {
    paddingVertical: 8,
    paddingHorizontal: 16,
  },
  formatButtonText: {
    color: '#3b82f6',
    fontSize: 14,
    fontWeight: '500',
  },
  sampleContainer: {
    backgroundColor: '#0f1930',
    borderRadius: 8,
    padding: 16,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#1e3a8a',
  },
  sampleTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#9fb3c8',
    marginBottom: 12,
    textAlign: 'center',
  },
  sampleTable: {
    backgroundColor: '#0a1425',
    borderRadius: 6,
    overflow: 'hidden',
    marginBottom: 12,
  },
  sampleHeader: {
    flexDirection: 'row',
    backgroundColor: '#1e40af',
    paddingVertical: 8,
  },
  sampleHeaderText: {
    flex: 1,
    color: '#ffffff',
    fontWeight: 'bold',
    textAlign: 'center',
    fontSize: 12,
  },
  sampleRow: {
    flexDirection: 'row',
    paddingVertical: 6,
    borderBottomWidth: 1,
    borderBottomColor: '#1e3a8a',
  },
  sampleCell: {
    flex: 1,
    color: '#9fb3c8',
    textAlign: 'center',
    fontSize: 12,
  },
  sampleNote: {
    fontSize: 12,
    color: '#7a8fa5',
    lineHeight: 16,
  },
  analysisContainer: {
    maxHeight: 400,
  },
  summaryCard: {
    backgroundColor: '#0f1930',
    borderRadius: 8,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#1e3a8a',
  },
  summaryTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#9fb3c8',
    textAlign: 'center',
    marginBottom: 12,
  },
  summaryGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  summaryItem: {
    alignItems: 'center',
    flex: 1,
  },
  summaryLabel: {
    fontSize: 12,
    color: '#7a8fa5',
    marginBottom: 4,
  },
  summaryValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#9fb3c8',
  },
  holdingsTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#9fb3c8',
    marginBottom: 12,
    textAlign: 'center',
  },
  holdingCard: {
    backgroundColor: '#0f1930',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#1e3a8a',
  },
  holdingHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  holdingSymbol: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#9fb3c8',
  },
  recommendationBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  recommendationText: {
    color: '#ffffff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  holdingDetails: {
    gap: 6,
  },
  holdingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  holdingLabel: {
    fontSize: 12,
    color: '#7a8fa5',
  },
  holdingValue: {
    fontSize: 12,
    fontWeight: '600',
    color: '#9fb3c8',
  },
  instructionsContainer: {
    backgroundColor: '#0f1930',
    borderRadius: 8,
    padding: 16,
    borderWidth: 1,
    borderColor: '#1e3a8a',
  },
  instructionsTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#9fb3c8',
    marginBottom: 12,
  },
  instructionItem: {
    fontSize: 12,
    color: '#7a8fa5',
    marginBottom: 6,
    paddingLeft: 8,
  },
});