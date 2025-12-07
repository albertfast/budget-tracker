/**
 * Screening API Service
 * Handles company fundamental analysis screening from uploaded files
 */

const API_BASE_URL = 'http://localhost:8000/api';

export interface PredictabilityMetrics {
  qoq_score: number;
  qoy_score: number;
  overall_score: number;
  grade: string;
  trend: string;
}

export interface ReportDepth {
  depth_score: number;
  grade: string;
  expansion_trend: string;
  depth_metrics: {
    line_items: number;
    disclosure_sections: number;
    segment_details: number;
    risk_factors: number;
    md_and_a_pages: number;
  };
  yoy_changes: {
    line_items: number;
    disclosure_sections: number;
    segment_details: number;
    risk_factors: number;
    md_and_a_pages: number;
  };
}

export interface Recommendation {
  action: 'STRONG BUY' | 'BUY' | 'HOLD' | 'WATCH' | 'AVOID';
  confidence: number;
  reasons: string[];
}

export interface QualityComponents {
  predictability: number;
  depth: number;
  expansion_trend: number;
  growth: number;
}

export interface CompanyScreeningResult {
  ticker: string;
  overall_score: number;
  overall_grade: string;
  recommendation: Recommendation;
  predictability: PredictabilityMetrics;
  report_depth: ReportDepth;
  quality_components: QualityComponents;
}

export interface ScreeningSummary {
  statistics: {
    average_score: number;
    median_score: number;
    highest_score: number;
    lowest_score: number;
  };
  distribution: {
    recommendations: Record<string, number>;
    grades: Record<string, number>;
  };
  top_performers: Array<{
    ticker: string;
    score: number;
    recommendation: string;
  }>;
  insights: string[];
}

export interface ScreeningResults {
  total_companies: number;
  companies: CompanyScreeningResult[];
  summary: ScreeningSummary;
}

export interface ScreeningResponse {
  status: string;
  file_name: string;
  screening_results: ScreeningResults;
  message: string;
}

/**
 * Upload and screen companies from CSV/Excel file
 */
export const screenCompaniesFromFile = async (
  fileUri: string,
  fileName: string,
  token: string
): Promise<ScreeningResponse> => {
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
    
    // Create file object for upload
    const file = {
      uri: fileUri,
      type: mimeType,
      name: fileName,
    } as any;
    
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/insights/screen-companies`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      let errorMessage = 'Failed to screen companies';
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
    if (!data.screening_results || !data.screening_results.companies) {
      throw new Error('Invalid response format from server');
    }
    
    return data;
  } catch (error) {
    console.error('Error screening companies:', error);
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
      return '#00C853'; // Green
    case 'BUY':
      return '#76FF03'; // Lime
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
 * Format score as percentage
 */
export const formatScore = (score: number): string => {
  return `${score.toFixed(1)}%`;
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
