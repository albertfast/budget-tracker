import React, { useState } from 'react';
import { StyleSheet, Text, View, TextInput, TouchableOpacity, KeyboardAvoidingView, Platform, ScrollView } from 'react-native';
import PortfolioChart from '../components/PortfolioChart';

export default function PortfolioChartScreen() {
  const [symbol, setSymbol] = useState('AAPL');
  const [searchSymbol, setSearchSymbol] = useState('');
  const [showChart, setShowChart] = useState(false);

  const handleSearch = () => {
    if (searchSymbol.trim()) {
      setSymbol(searchSymbol.trim().toUpperCase());
      setShowChart(true);
    }
  };

  const quickSymbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'SPY'];

  return (
    <KeyboardAvoidingView 
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <View style={styles.header}>
        <Text style={styles.headerTitle}>📊 Portfolio Chart Analysis</Text>
        <Text style={styles.headerSubtitle}>
          Advanced technical analysis with 250-day MA and Fibonacci golden ratio
        </Text>
      </View>

      {/* Search Bar */}
      <View style={styles.searchContainer}>
        <TextInput
          style={styles.searchInput}
          placeholder="Enter stock symbol (e.g., AAPL)"
          placeholderTextColor="#7a8fa5"
          value={searchSymbol}
          onChangeText={setSearchSymbol}
          autoCapitalize="characters"
          autoCorrect={false}
          onSubmitEditing={handleSearch}
        />
        <TouchableOpacity style={styles.searchButton} onPress={handleSearch}>
          <Text style={styles.searchButtonText}>Analyze</Text>
        </TouchableOpacity>
      </View>

      {/* Quick Select */}
      <View style={styles.quickSelectContainer}>
        <Text style={styles.quickSelectLabel}>Quick Select:</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.quickSelectScroll}>
          {quickSymbols.map((sym) => (
            <TouchableOpacity
              key={sym}
              style={[
                styles.quickButton,
                symbol === sym && showChart && styles.quickButtonActive
              ]}
              onPress={() => {
                setSymbol(sym);
                setSearchSymbol(sym);
                setShowChart(true);
              }}
            >
              <Text
                style={[
                  styles.quickButtonText,
                  symbol === sym && showChart && styles.quickButtonTextActive
                ]}
              >
                {sym}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      {/* Chart Display */}
      {showChart ? (
        <PortfolioChart symbol={symbol} defaultPeriod="1y" />
      ) : (
        <View style={styles.emptyState}>
          <Text style={styles.emptyStateIcon}>📈</Text>
          <Text style={styles.emptyStateTitle}>Ready to Analyze</Text>
          <Text style={styles.emptyStateText}>
            Enter a stock symbol above or select from quick picks to view advanced technical analysis
          </Text>
          
          <View style={styles.featuresList}>
            <Text style={styles.featureTitle}>What You'll Get:</Text>
            <Text style={styles.featureItem}>📊 50/200/250 Day Moving Averages</Text>
            <Text style={styles.featureItem}>✨ Fibonacci Golden Ratio Analysis</Text>
            <Text style={styles.featureItem}>🎯 Enhanced Bullish Confidence Score</Text>
            <Text style={styles.featureItem}>📈 Golden Cross Detection</Text>
            <Text style={styles.featureItem}>💪 MA Alignment & Trend Analysis</Text>
            <Text style={styles.featureItem}>🔮 Price Target Predictions</Text>
          </View>
        </View>
      )}
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0f1e',
  },
  header: {
    backgroundColor: '#111a30',
    padding: 20,
    paddingTop: 60,
    borderBottomWidth: 1,
    borderBottomColor: '#1e3a8a',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#9fb3c8',
    marginBottom: 8,
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#7a8fa5',
    lineHeight: 20,
  },
  searchContainer: {
    flexDirection: 'row',
    padding: 16,
    backgroundColor: '#111a30',
    gap: 12,
  },
  searchInput: {
    flex: 1,
    backgroundColor: '#0f1930',
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 12,
    color: '#9fb3c8',
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#1e3a8a',
  },
  searchButton: {
    backgroundColor: '#3b82f6',
    borderRadius: 8,
    paddingHorizontal: 24,
    justifyContent: 'center',
    alignItems: 'center',
  },
  searchButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  quickSelectContainer: {
    backgroundColor: '#111a30',
    paddingHorizontal: 16,
    paddingBottom: 16,
  },
  quickSelectLabel: {
    fontSize: 12,
    color: '#7a8fa5',
    marginBottom: 8,
  },
  quickSelectScroll: {
    flexDirection: 'row',
  },
  quickButton: {
    backgroundColor: '#0f1930',
    borderRadius: 6,
    paddingVertical: 8,
    paddingHorizontal: 16,
    marginRight: 8,
    borderWidth: 1,
    borderColor: '#1e3a8a',
  },
  quickButtonActive: {
    backgroundColor: '#3b82f6',
    borderColor: '#3b82f6',
  },
  quickButtonText: {
    color: '#7a8fa5',
    fontSize: 14,
    fontWeight: '600',
  },
  quickButtonTextActive: {
    color: '#ffffff',
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  emptyStateIcon: {
    fontSize: 64,
    marginBottom: 16,
  },
  emptyStateTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#9fb3c8',
    marginBottom: 8,
  },
  emptyStateText: {
    fontSize: 14,
    color: '#7a8fa5',
    textAlign: 'center',
    marginBottom: 24,
    lineHeight: 20,
  },
  featuresList: {
    alignSelf: 'stretch',
    backgroundColor: '#111a30',
    borderRadius: 12,
    padding: 20,
    borderWidth: 1,
    borderColor: '#1e3a8a',
  },
  featureTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#9fb3c8',
    marginBottom: 12,
  },
  featureItem: {
    fontSize: 14,
    color: '#7a8fa5',
    marginBottom: 8,
    paddingLeft: 8,
  },
});
