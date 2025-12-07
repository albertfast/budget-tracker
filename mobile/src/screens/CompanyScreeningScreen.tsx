/**
 * CompanyScreeningScreen
 * Upload CSV/Excel/XBRL/SEC EDGAR files to screen companies for fundamental quality
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  ScrollView,
} from 'react-native';
import * as DocumentPicker from 'expo-document-picker';
import AsyncStorage from '@react-native-async-storage/async-storage';
import SwipeNavigationWrapper from '@/components/SwipeNavigationWrapper';
import { ScreeningResults } from '../components/ScreeningResults';
import {
  screenCompaniesFromFile,
  ScreeningResponse,
} from '../services/screeningApi';

export default function CompanyScreeningScreen() {
  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<{
    name: string;
    uri: string;
  } | null>(null);
  const [screeningResults, setScreeningResults] = useState<ScreeningResponse | null>(null);

  const pickDocument = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: [
          'text/csv',
          'application/vnd.ms-excel',
          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
          'text/xml',
          'application/xml',
          'text/html',
          'application/json',
          'text/plain'
        ],
        copyToCacheDirectory: true,
        multiple: false,
      });

      if (!result.canceled && result.assets && result.assets.length > 0) {
        const asset = result.assets[0];
        
        // Validate file extension - now supports SEC EDGAR formats
        const fileName = asset.name.toLowerCase();
        const allowedExtensions = ['.csv', '.xlsx', '.xls', '.xml', '.xbrl', '.htm', '.html', '.txt', '.json'];
        const hasValidExtension = allowedExtensions.some(ext => fileName.endsWith(ext));
        
        if (!hasValidExtension) {
          Alert.alert(
            'Invalid File Type',
            'Please select a valid file:\n• CSV/Excel (.csv, .xlsx, .xls)\n• XBRL (.xml, .xbrl)\n• SEC Filing (.htm, .html)\n• JSON/Text (.json, .txt)'
          );
          return;
        }
        
        setSelectedFile({
          name: asset.name,
          uri: asset.uri,
        });
        setScreeningResults(null); // Clear previous results
      }
    } catch (error) {
      console.error('Error picking document:', error);
      Alert.alert(
        'Error', 
        'Failed to pick document. Please try again.'
      );
    }
  };

  const screenCompanies = async () => {
    if (!selectedFile) {
      Alert.alert('No File Selected', 'Please select a file first');
      return;
    }

    try {
      setLoading(true);

      // Get auth token
      const token = await AsyncStorage.getItem('authToken');
      if (!token) {
        Alert.alert('Authentication Required', 'Please log in to screen companies');
        setLoading(false);
        return;
      }

      // Upload and screen
      const results = await screenCompaniesFromFile(
        selectedFile.uri,
        selectedFile.name,
        token
      );

      setScreeningResults(results);
    } catch (error: any) {
      console.error('Error screening companies:', error);
      Alert.alert(
        'Screening Failed',
        error.message || 'Failed to screen companies. Please check your file format and try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  const clearResults = () => {
    setScreeningResults(null);
    setSelectedFile(null);
  };

  // Show results view if we have results
  if (screeningResults) {
    return (
      <SwipeNavigationWrapper currentTab="Screening">
        <ScreeningResults
          companies={screeningResults.screening_results.companies}
          summary={screeningResults.screening_results.summary}
          onClose={clearResults}
        />
      </SwipeNavigationWrapper>
    );
  }

  // Show upload view
  return (
    <SwipeNavigationWrapper currentTab="Screening">
      <ScrollView style={styles.container}>
      <View style={styles.content}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>📊 Company Screening</Text>
          <Text style={styles.subtitle}>
            Upload CSV, Excel, or SEC EDGAR filings (XBRL) to analyze fundamental quality
          </Text>
        </View>

        {/* Info Card */}
        <View style={styles.infoCard}>
          <Text style={styles.infoTitle}>What This Analyzes:</Text>
          <View style={styles.infoItem}>
            <Text style={styles.infoIcon}>📈</Text>
            <Text style={styles.infoText}>
              <Text style={styles.infoBold}>Predictability:</Text> QoQ and QoY revenue consistency
            </Text>
          </View>
          <View style={styles.infoItem}>
            <Text style={styles.infoIcon}>📄</Text>
            <Text style={styles.infoText}>
              <Text style={styles.infoBold}>Transparency:</Text> 10-K report depth expansion
            </Text>
          </View>
          <View style={styles.infoItem}>
            <Text style={styles.infoIcon}>🎯</Text>
            <Text style={styles.infoText}>
              <Text style={styles.infoBold}>Quality Score:</Text> 4-component fundamental health
            </Text>
          </View>
          <View style={styles.infoItem}>
            <Text style={styles.infoIcon}>💡</Text>
            <Text style={styles.infoText}>
              <Text style={styles.infoBold}>Recommendations:</Text> STRONG BUY through AVOID
            </Text>
          </View>
        </View>

        {/* File Format Info */}
        <View style={styles.formatCard}>
          <Text style={styles.formatTitle}>📁 Supported File Formats:</Text>
          
          <Text style={styles.formatSubtitle}>Traditional Formats:</Text>
          <Text style={styles.formatText}>
            • <Text style={styles.infoBold}>CSV</Text> (.csv) - Comma-separated values{'\n'}
            • <Text style={styles.infoBold}>Excel</Text> (.xlsx, .xls) - Microsoft Excel{'\n'}
            Column name: ticker, symbol, stock_symbol, or company{'\n'}
            Ticker format: 1-5 uppercase letters (e.g., AAPL, MSFT)
          </Text>
          
          <Text style={styles.formatSubtitle}>SEC EDGAR Formats (NEW!):</Text>
          <Text style={styles.formatText}>
            • <Text style={styles.infoBold}>XBRL</Text> (.xml, .xbrl) - SEC's standard financial format{'\n'}
            • <Text style={styles.infoBold}>HTML</Text> (.htm, .html) - 10-K, 10-Q reports{'\n'}
            • <Text style={styles.infoBold}>JSON</Text> (.json) - SEC API format{'\n'}
            • <Text style={styles.infoBold}>Text</Text> (.txt) - Plain text filings{'\n'}
            📥 Download from: sec.gov/edgar
          </Text>
          
          <Text style={styles.formatExample}>Example CSV:</Text>
          <View style={styles.codeBlock}>
            <Text style={styles.codeText}>
              ticker,shares,cost_basis{'\n'}
              AAPL,100,15000{'\n'}
              MSFT,50,12500{'\n'}
              GOOGL,25,7500
            </Text>
          </View>
          
          <Text style={styles.formatExample}>Example XBRL:</Text>
          <View style={styles.codeBlock}>
            <Text style={styles.codeText}>
              {'<'}xbrl{'>'}{'\n'}
              {'  <'}dei:TradingSymbol{'>'}AAPL{'<'}/dei:TradingSymbol{'>'}{'\n'}
              {'  <'}us-gaap:Revenues{'>'}394328000000{'<'}/...{'>'}{'\n'}
              {'<'}/xbrl{'>'}
            </Text>
          </View>
        </View>

        {/* File Selection */}
        <View style={styles.uploadSection}>
          <TouchableOpacity
            style={styles.pickButton}
            onPress={pickDocument}
            disabled={loading}
          >
            <Text style={styles.pickButtonIcon}>📁</Text>
            <Text style={styles.pickButtonText}>
              {selectedFile ? 'Change File' : 'Select File (CSV/Excel/XBRL)'}
            </Text>
          </TouchableOpacity>

          {selectedFile && (
            <View style={styles.selectedFile}>
              <Text style={styles.selectedFileIcon}>✅</Text>
              <View style={styles.selectedFileInfo}>
                <Text style={styles.selectedFileName}>{selectedFile.name}</Text>
                <Text style={styles.selectedFileLabel}>Selected file</Text>
              </View>
            </View>
          )}
        </View>

        {/* Screen Button */}
        {selectedFile && (
          <TouchableOpacity
            style={[styles.screenButton, loading && styles.screenButtonDisabled]}
            onPress={screenCompanies}
            disabled={loading}
          >
            {loading ? (
              <>
                <ActivityIndicator color="#fff" style={styles.spinner} />
                <Text style={styles.screenButtonText}>Screening Companies...</Text>
              </>
            ) : (
              <>
                <Text style={styles.screenButtonIcon}>🔍</Text>
                <Text style={styles.screenButtonText}>Screen Companies</Text>
              </>
            )}
          </TouchableOpacity>
        )}

        {/* Sample Files Info */}
        <View style={styles.sampleInfo}>
          <Text style={styles.sampleTitle}>💡 Tip:</Text>
          <Text style={styles.sampleText}>
            Test with sample files from the repository:{'\n'}
            • sample-portfolio.csv (Traditional format){'\n'}
            • test_xbrl_sample.xml (XBRL format){'\n'}
            Or download 10-K/10-Q from sec.gov/edgar
          </Text>
        </View>

        {/* Features List */}
        <View style={styles.featuresCard}>
          <Text style={styles.featuresTitle}>📋 What You'll Get:</Text>
          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>✅</Text>
            <Text style={styles.featureText}>
              Ranked list of all companies by quality score
            </Text>
          </View>
          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>✅</Text>
            <Text style={styles.featureText}>
              Investment recommendations with confidence levels
            </Text>
          </View>
          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>✅</Text>
            <Text style={styles.featureText}>
              Detailed predictability analysis (QoQ, QoY)
            </Text>
          </View>
          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>✅</Text>
            <Text style={styles.featureText}>
              10-K depth metrics and expansion trends
            </Text>
          </View>
          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>✅</Text>
            <Text style={styles.featureText}>
              Quality component breakdown with visualizations
            </Text>
          </View>
          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>✅</Text>
            <Text style={styles.featureText}>
              Portfolio summary with key insights
            </Text>
          </View>
        </View>
      </View>
    </ScrollView>
    </SwipeNavigationWrapper>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  content: {
    padding: 16,
  },
  header: {
    marginBottom: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    lineHeight: 22,
  },
  infoCard: {
    backgroundColor: '#E3F2FD',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  infoItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  infoIcon: {
    fontSize: 20,
    marginRight: 8,
  },
  infoText: {
    fontSize: 14,
    color: '#333',
    flex: 1,
    lineHeight: 20,
  },
  infoBold: {
    fontWeight: 'bold',
  },
  formatCard: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  formatTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  formatSubtitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#2196F3',
    marginTop: 12,
    marginBottom: 6,
  },
  formatText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 22,
    marginBottom: 12,
  },
  formatExample: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  codeBlock: {
    backgroundColor: '#f5f5f5',
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  codeText: {
    fontFamily: 'monospace',
    fontSize: 12,
    color: '#333',
    lineHeight: 18,
  },
  uploadSection: {
    marginBottom: 16,
  },
  pickButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#2196F3',
    borderStyle: 'dashed',
  },
  pickButtonIcon: {
    fontSize: 24,
    marginRight: 8,
  },
  pickButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2196F3',
  },
  selectedFile: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#E8F5E9',
    padding: 16,
    borderRadius: 12,
    marginTop: 12,
  },
  selectedFileIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  selectedFileInfo: {
    flex: 1,
  },
  selectedFileName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  selectedFileLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  screenButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#2196F3',
    padding: 18,
    borderRadius: 12,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 4,
  },
  screenButtonDisabled: {
    backgroundColor: '#90CAF9',
  },
  screenButtonIcon: {
    fontSize: 24,
    marginRight: 8,
  },
  screenButtonText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
  },
  spinner: {
    marginRight: 8,
  },
  sampleInfo: {
    backgroundColor: '#FFF3E0',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
  },
  sampleTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  sampleText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 22,
  },
  featuresCard: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
  },
  featuresTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  featureItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  featureIcon: {
    fontSize: 16,
    marginRight: 8,
  },
  featureText: {
    fontSize: 14,
    color: '#666',
    flex: 1,
    lineHeight: 20,
  },
});
