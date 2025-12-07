/**
 * Financial Analysis API Service
 * Comprehensive financial analysis with buy/sell points for Barchart & Morningstar formats
 */

const API_BASE_URL = 'http://localhost:8000/api';

export interface PriceAnalysis {
  current_price?: number;
  buy_point?: number;
  sell_point?: number;
  target_price?: number;
  stop_loss?: number;
  support_levels?: number[];
  resistance_levels?: number[];
  fibonacci_levels?: Record<string, number>;
  potential_return?: number;
  error?: string;
}

export interface PredictabilityMetrics {
  qoq_score: number;
  qoy_score: number;
  overall_predictability: number;
  grade: string;
  trend: string;
  details?: {
    qoq_mean_growth: number;
    qoq_volatility: number;
    qoy_mean_growth: number;
    qoy_volatility: number;
  };
}

export interface ReportDepth {
  depth_score: number;
  trend_score: number;
  expansion_trend: string;
  grade: string;
  latest_year?: {
    year: number;
    line_items: number;
    disclosure_sections: number;
    segment_details: number;
    risk_factors: number;
    md_and_a_pages: number;
  };
  year_over_year_change?: Record<string, number>;
  interpretation?: string;
}

export interface QualityScore {
  overall: number;
  components: {
    predictability: number;
    report_depth: number;
    expansion_trend: number;
    growth: number;
  };
  grade: string;
}

export interface Recommendation {
  action: 'STRONG BUY' | 'BUY' | 'HOLD' | 'WATCH' | 'AVOID';
  confidence: number;
  color: string;
  reasons: string[];
  summary: string;
}

export interface CompanyAnalysis {
  ticker: string;
  company_name?: string;
  overall_score: number;
  quality_score: QualityScore;
  recommendation: Recommendation;
  predictability: PredictabilityMetrics;
  report_depth: ReportDepth;
  price_analysis: PriceAnalysis;
  source_data?: any[];
}

export interface AnalysisSummary {
  total_screened: number;
  average_score: number;
  median_score: number;
  highest_score: number;
  lowest_score: number;
  recommendations: Record<string, number>;
  grade_distribution: Record<string, number>;
  top_performers: Array<{
    ticker: string;
    score: number;
    grade: string;
    recommendation: string;
    predictability_grade: string;
    report_depth_grade: string;
  }>;
  insights: string[];
}

export interface AnalysisResults {
  total_companies: number;
  file_type: string;
  companies: CompanyAnalysis[];
  summary: AnalysisSummary;
  screening_date: string;
}

export interface FinancialAnalysisResponse {
  success: boolean;
  analysis_type: string;
  file_name: string;
  analysis_results: AnalysisResults;
  message: string;
}

/**
 * Upload and analyze financials from file with comprehensive metrics
 * Supports Barchart, Morningstar, CSV, Excel, and SEC EDGAR formats
 * Optional chart data file for enhanced analysis with historical price/volume data
 */
export const analyzeFinancialsFromFile = async (
  fileUri: string,
  fileName: string,
  token: string,
  chartFile?: { uri: string; name: string }
): Promise<FinancialAnalysisResponse> => {
  try {
    const formData = new FormData();
    
    // Determine MIME type based on file extension
    let mimeType = 'text/csv';
    if (fileName.endsWith('.xlsx')) {
      mimeType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
    } else if (fileName.endsWith('.xls')) {
      mimeType = 'application/vnd.ms-excel';
    } else if (fileName.endsWith('.xml') || fileName.endsWith('.xbrl')) {
      mimeType = 'application/xml';
    } else if (fileName.endsWith('.htm') || fileName.endsWith('.html')) {
      mimeType = 'text/html';
    } else if (fileName.endsWith('.json')) {
      mimeType = 'application/json';
    } else if (fileName.endsWith('.txt')) {
      mimeType = 'text/plain';
    }
    
    // Create main file object for upload
    const file = {
      uri: fileUri,
      type: mimeType,
      name: fileName,
    } as any;
    
    formData.append('file', file);

    // Add optional chart data file if provided
    if (chartFile) {
      let chartMimeType = 'text/csv';
      if (chartFile.name.endsWith('.xlsx')) {
        chartMimeType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
      } else if (chartFile.name.endsWith('.xls')) {
        chartMimeType = 'application/vnd.ms-excel';
      }
      
      const chartFileObj = {
        uri: chartFile.uri,
        type: chartMimeType,
        name: chartFile.name,
      } as any;
      
      formData.append('chart_data_file', chartFileObj);
    }

    const response = await fetch(`${API_BASE_URL}/insights/analyze-financials`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      let errorMessage = 'Failed to analyze financials';
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorMessage;
      } catch (parseError) {
        // If error response is not JSON, use status text
        errorMessage = response.statusText || errorMessage;
      }
      throw new Error(errorMessage);
    }

    const data = await response.json();
    
    // Validate response structure
    if (!data.analysis_results || !data.analysis_results.companies) {
      throw new Error('Invalid response format from server');
    }
    
    return data;
  } catch (error) {
    console.error('Error analyzing financials:', error);
    // Re-throw with more context if it's a network error
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error('Network error: Unable to connect to server. Please check your connection.');
    }
    throw error;
  }
};

/**
 * Get color for recommendation action
 */
export const getRecommendationColor = (action: string): string => {
  switch (action) {
    case 'STRONG BUY':
      return '#00C853'; // Dark Green
    case 'BUY':
      return '#76FF03'; // Light Green
    case 'HOLD':
      return '#FFEB3B'; // Yellow
    case 'WATCH':
      return '#FF9800'; // Orange
    case 'AVOID':
      return '#F44336'; // Red
    default:
      return '#9E9E9E'; // Gray
  }
};

/**
 * Get color for grade
 */
export const getGradeColor = (grade: string): string => {
  if (grade.startsWith('A')) return '#4CAF50'; // Green
  if (grade.startsWith('B')) return '#8BC34A'; // Light Green
  if (grade.startsWith('C')) return '#FFC107'; // Amber
  if (grade.startsWith('D')) return '#FF5722'; // Deep Orange
  return '#9E9E9E'; // Gray
};

/**
 * Format price with currency symbol
 */
export const formatPrice = (price: number | undefined): string => {
  if (price === undefined || price === null) return 'N/A';
  return `$${price.toFixed(2)}`;
};

/**
 * Format percentage
 */
export const formatPercent = (value: number | undefined): string => {
  if (value === undefined || value === null) return 'N/A';
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(2)}%`;
};

/**
 * Get trend icon
 */
export const getTrendIcon = (trend: string): string => {
  switch (trend) {
    case 'improving':
      return '📈';
    case 'declining':
      return '📉';
    case 'stable':
      return '➡️';
    case 'expanding':
      return '🔼';
    case 'contracting':
      return '🔽';
    case 'stable_positive':
      return '✅';
    default:
      return '⏸️';
  }
};

/**
 * Get recommendation emoji
 */
export const getRecommendationEmoji = (action: string): string => {
  switch (action) {
    case 'STRONG BUY':
      return '🚀';
    case 'BUY':
      return '✅';
    case 'HOLD':
      return '✋';
    case 'WATCH':
      return '👀';
    case 'AVOID':
      return '⛔';
    default:
      return '❓';
  }
};

/**
 * Calculate risk level based on multiple factors
 */
export const calculateRiskLevel = (
  analysis: CompanyAnalysis
): { level: string; color: string; emoji: string } => {
  const score = analysis.overall_score;
  const predictability = analysis.predictability.overall_predictability;
  const action = analysis.recommendation.action;
  
  // Low risk: High score, good predictability, strong buy
  if (score >= 80 && predictability >= 75 && action === 'STRONG BUY') {
    return { level: 'Low Risk', color: '#4CAF50', emoji: '🟢' };
  }
  
  // Medium risk: Moderate scores
  if (score >= 60 && predictability >= 60) {
    return { level: 'Medium Risk', color: '#FFC107', emoji: '🟡' };
  }
  
  // High risk: Low scores or avoid recommendation
  if (score < 60 || action === 'AVOID') {
    return { level: 'High Risk', color: '#F44336', emoji: '🔴' };
  }
  
  return { level: 'Medium Risk', color: '#FF9800', emoji: '🟠' };
};

/**
 * Generate investment timeframe suggestion
 */
export const getTimeframeSuggestion = (analysis: CompanyAnalysis): string => {
  const action = analysis.recommendation.action;
  const predictability = analysis.predictability.overall_predictability;
  
  if (action === 'STRONG BUY' && predictability >= 80) {
    return 'Long-term (1-2 years+)';
  }
  
  if (action === 'BUY') {
    return 'Medium-term (6-12 months)';
  }
  
  if (action === 'HOLD') {
    return 'Monitor quarterly';
  }
  
  return 'Not recommended';
};

/**
 * Sort companies by various criteria
 */
export const sortCompanies = (
  companies: CompanyAnalysis[],
  sortBy: 'score' | 'potential_return' | 'confidence' | 'risk'
): CompanyAnalysis[] => {
  switch (sortBy) {
    case 'score':
      return [...companies].sort((a, b) => b.overall_score - a.overall_score);
    
    case 'potential_return':
      return [...companies].sort((a, b) => {
        const returnA = a.price_analysis.potential_return || 0;
        const returnB = b.price_analysis.potential_return || 0;
        return returnB - returnA;
      });
    
    case 'confidence':
      return [...companies].sort((a, b) => 
        b.recommendation.confidence - a.recommendation.confidence
      );
    
    case 'risk':
      return [...companies].sort((a, b) => {
        const riskA = calculateRiskLevel(a).level;
        const riskB = calculateRiskLevel(b).level;
        const riskOrder = { 'Low Risk': 0, 'Medium Risk': 1, 'High Risk': 2 };
        return (riskOrder[riskA as keyof typeof riskOrder] || 1) - 
               (riskOrder[riskB as keyof typeof riskOrder] || 1);
      });
    
    default:
      return companies;
  }
};
