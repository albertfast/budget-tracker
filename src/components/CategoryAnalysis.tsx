import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, Alert, ImageBackground } from 'react-native';

interface SpendingCategory {
  category: string;
  amount: number;
  percentage: number;
  transaction_count: number;
}

interface CategoryAnalysisProps {
  userId?: string;
  days?: number;
}

export default function CategoryAnalysis({ userId, days = 30 }: CategoryAnalysisProps) {
  const [categories, setCategories] = useState<SpendingCategory[]>([]);
  const [totalSpending, setTotalSpending] = useState(0);
  const [loading, setLoading] = useState(false);
  const [selectedPeriod, setSelectedPeriod] = useState(days);

  const periods = [
    { label: '7 Days', value: 7 },
    { label: '30 Days', value: 30 },
    { label: '90 Days', value: 90 },
    { label: '1 Year', value: 365 }
  ];

  useEffect(() => {
    fetchCategoryData();
  }, [selectedPeriod]);

  const fetchCategoryData = async () => {
    setLoading(true);
    try {
      // TODO: Replace with actual API call
      // const response = await fetch(`/api/v1/insights/categories?days=${selectedPeriod}`);
      // const data = await response.json();
      
      // Mock data for demonstration
      const mockData = {
        categories: [
          { category: 'Food and Drink', amount: 452.30, percentage: 35.2, transaction_count: 28 },
          { category: 'Transportation', amount: 284.50, percentage: 22.1, transaction_count: 12 },
          { category: 'Entertainment', amount: 198.75, percentage: 15.4, transaction_count: 15 },
          { category: 'Shopping', amount: 167.20, percentage: 13.0, transaction_count: 8 },
          { category: 'Bills & Utilities', amount: 125.00, percentage: 9.7, transaction_count: 4 },
          { category: 'Healthcare', amount: 58.25, percentage: 4.5, transaction_count: 3 }
        ],
        total_spending: 1286.00
      };

      setCategories(mockData.categories);
      setTotalSpending(mockData.total_spending);
    } catch (error) {
      console.error('Error fetching category data:', error);
      Alert.alert('Error', 'Failed to load spending categories');
    } finally {
      setLoading(false);
    }
  };

  const getCategoryColor = (index: number): string => {
    const colors = [
      '#ef4444', // Red
      '#f97316', // Orange  
      '#eab308', // Yellow
      '#22c55e', // Green
      '#3b82f6', // Blue
      '#8b5cf6', // Purple
      '#ec4899', // Pink
      '#6b7280'  // Gray
    ];
    return colors[index % colors.length];
  };

  const getCategoryEmoji = (category: string): string => {
    const emojiMap: { [key: string]: string } = {
      'Food and Drink': '🍽️',
      'Transportation': '🚗',
      'Entertainment': '🎭',
      'Shopping': '🛍️',
      'Bills & Utilities': '📮',
      'Healthcare': '🏥',
      'Travel': '✈️',
      'Education': '📚',
      'Fitness': '💪',
      'Groceries': '🛒',
      'Restaurants': '🍕',
      'Gas': '⛽',
      'Subscriptions': '📱',
      'Insurance': '🛡️',
      'Rent': '🏠',
      'Other': '📊'
    };
    
    // Try exact match first
    if (emojiMap[category]) {
      return emojiMap[category];
    }
    
    // Try partial matches for common patterns
    const categoryLower = category.toLowerCase();
    if (categoryLower.includes('food') || categoryLower.includes('drink') || categoryLower.includes('restaurant')) {
      return '🍽️';
    }
    if (categoryLower.includes('transport') || categoryLower.includes('gas') || categoryLower.includes('fuel')) {
      return '🚗';
    }
    if (categoryLower.includes('entertainment') || categoryLower.includes('fun') || categoryLower.includes('movie')) {
      return '🎭';
    }
    if (categoryLower.includes('shop') || categoryLower.includes('retail')) {
      return '🛍️';
    }
    if (categoryLower.includes('bill') || categoryLower.includes('utilit')) {
      return '📮';
    }
    if (categoryLower.includes('health') || categoryLower.includes('medical')) {
      return '🏥';
    }
    if (categoryLower.includes('travel') || categoryLower.includes('vacation')) {
      return '✈️';
    }
    
    // Default emoji for unknown categories
    return '📊';
  };

  const renderCategoryBar = (category: SpendingCategory, index: number) => (
    <View key={category.category} style={styles.categoryItem}>
      <View style={styles.categoryHeader}>
        <View style={styles.categoryLabelRow}>
          <Text style={styles.categoryEmoji}>{getCategoryEmoji(category.category)}</Text>
          <Text style={styles.categoryName}>{category.category}</Text>
        </View>
        <View style={styles.categoryAmounts}>
          <Text style={styles.categoryAmount}>${category.amount.toFixed(2)}</Text>
          <Text style={styles.categoryPercentage}>{category.percentage.toFixed(1)}%</Text>
        </View>
      </View>
      
      <View style={styles.progressBarContainer}>
        <View 
          style={[
            styles.progressBar,
            { 
              width: `${category.percentage}%`,
              backgroundColor: getCategoryColor(index)
            }
          ]} 
        />
      </View>
      
      <Text style={styles.transactionCount}>
        {category.transaction_count} transaction{category.transaction_count !== 1 ? 's' : ''}
      </Text>
    </View>
  );

  return (
    <ImageBackground
      source={require('../public/images/nature_collection_34_20250803_211409.png')}
      style={styles.backgroundContainer}
      imageStyle={styles.backgroundImage}
    >
      <View style={styles.overlay}>
        <View style={styles.container}>
          <Text style={styles.title}>Spending by Category</Text>
      
      {/* Period Selection */}
      <View style={styles.periodSelector}>
        {periods.map((period) => (
          <TouchableOpacity
            key={period.value}
            style={[
              styles.periodButton,
              selectedPeriod === period.value && styles.periodButtonActive
            ]}
            onPress={() => setSelectedPeriod(period.value)}
          >
            <Text 
              style={[
                styles.periodButtonText,
                selectedPeriod === period.value && styles.periodButtonTextActive
              ]}
            >
              {period.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <ScrollView style={styles.scrollContainer} showsVerticalScrollIndicator={false}>
        {/* Total Spending Summary - npadil10 */}
        <View style={styles.summaryContainer}>
          <Text style={styles.summaryLabel}>Total Spending ({selectedPeriod} days)</Text>
          <Text style={styles.summaryAmount}>${totalSpending.toFixed(2)}</Text>
          <Text style={styles.summaryAverage}>
            Avg: ${(totalSpending / selectedPeriod).toFixed(2)}/day
          </Text>
        </View>

        {/* Category Breakdown */}
        <View style={styles.categoriesContainer}>
          {loading ? (
            <View style={styles.loadingContainer}>
              <Text style={styles.loadingText}>Loading categories...</Text>
            </View>
          ) : (
            categories.map((category, index) => renderCategoryBar(category, index))
          )}
        </View>

        {/* Insights Section */}
        {!loading && categories.length > 0 && (
          <View style={styles.insightsContainer}>
            <Text style={styles.insightsTitle}>💡 Insights</Text>
            
            {categories[0] && (
              <View style={styles.insightItem}>
                <Text style={styles.insightText}>
                  Your highest spending category is {getCategoryEmoji(categories[0].category)} {categories[0].category} at 
                  ${categories[0].amount.toFixed(2)} ({categories[0].percentage.toFixed(1)}% of total)
                </Text>
              </View>
            )}
            
            {categories.length >= 3 && (
              <View style={styles.insightItem}>
                <Text style={styles.insightText}>
                  Your top 3 categories represent 
                  {(categories[0].percentage + categories[1].percentage + categories[2].percentage).toFixed(1)}% 
                  of your total spending
                </Text>
              </View>
            )}
          </View>
        )}
      </ScrollView>
        </View>
      </View>
    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  backgroundContainer: {
    flex: 1,
  },
  backgroundImage: {
    opacity: 0.2,
  },
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(10, 14, 39, 0.80)',
  },
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
  periodSelector: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 20,
    backgroundColor: '#0f1930',
    borderRadius: 8,
    padding: 4,
  },
  periodButton: {
    flex: 1,
    paddingVertical: 8,
    paddingHorizontal: 4,
    borderRadius: 6,
    alignItems: 'center',
  },
  periodButtonActive: {
    backgroundColor: '#3b82f6',
  },
  periodButtonText: {
    fontSize: 12,
    color: '#9fb3c8',
    fontWeight: '500',
    textShadowColor: '#000000',
    textShadowOffset: { width: 0.5, height: 0.5 },
    textShadowRadius: 1,
  },
  periodButtonTextActive: {
    color: '#ffffff',
    fontWeight: 'bold',
  },
  scrollContainer: {
    maxHeight: 400,
  },
  summaryContainer: {
    backgroundColor: '#0f1930',
    borderRadius: 8,
    padding: 16,
    marginBottom: 16,
    alignItems: 'center',
  },
  summaryLabel: {
    fontSize: 14,
    color: '#9fb3c8',
    marginBottom: 4,
    textShadowColor: '#000000',
    textShadowOffset: { width: 0.5, height: 0.5 },
    textShadowRadius: 1,
  },
  summaryAmount: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ef4444',
    marginBottom: 4,
    textShadowColor: '#000000',
    textShadowOffset: { width: 1, height: 1 },
    textShadowRadius: 2,
  },
  summaryAverage: {
    fontSize: 12,
    color: '#9fb3c8',
    fontStyle: 'italic',
    textShadowColor: '#000000',
    textShadowOffset: { width: 0.5, height: 0.5 },
    textShadowRadius: 1,
  },
  categoriesContainer: {
    marginBottom: 16,
  },
  categoryItem: {
    backgroundColor: '#0f1930',
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
  },
  categoryHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  categoryLabelRow: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  categoryEmoji: {
    fontSize: 18,
    marginRight: 8,
    textAlign: 'center',
    minWidth: 24,
  },
  categoryDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 8,
  },
  categoryName: {
    fontSize: 14,
    color: '#9fb3c8',
    fontWeight: '500',
    flex: 1,
    textShadowColor: '#000000',
    textShadowOffset: { width: 0.5, height: 0.5 },
    textShadowRadius: 1,
  },
  categoryAmounts: {
    alignItems: 'flex-end',
  },
  categoryAmount: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#ef4444',
    textShadowColor: '#000000',
    textShadowOffset: { width: 0.5, height: 0.5 },
    textShadowRadius: 1,
  },
  categoryPercentage: {
    fontSize: 12,
    color: '#9fb3c8',
    textShadowColor: '#000000',
    textShadowOffset: { width: 0.5, height: 0.5 },
    textShadowRadius: 1,
  },
  progressBarContainer: {
    height: 6,
    backgroundColor: '#1e3a8a',
    borderRadius: 3,
    marginBottom: 4,
  },
  progressBar: {
    height: 6,
    borderRadius: 3,
  },
  transactionCount: {
    fontSize: 11,
    color: '#9fb3c8',
    textAlign: 'right',
    fontStyle: 'italic',
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
  insightsContainer: {
    backgroundColor: '#0f1930',
    borderRadius: 8,
    padding: 16,
  },
  insightsTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#9fb3c8',
    marginBottom: 12,
    textShadowColor: '#000000',
    textShadowOffset: { width: 1, height: 1 },
    textShadowRadius: 2,
  },
  insightItem: {
    marginBottom: 8,
  },
  insightText: {
    fontSize: 13,
    color: '#9fb3c8',
    lineHeight: 18,
    textShadowColor: '#000000',
    textShadowOffset: { width: 0.5, height: 0.5 },
    textShadowRadius: 1,
  },
});
