import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, ScrollView, ActivityIndicator, Dimensions } from 'react-native';
import { investmentApi } from '../services/investmentApi';

const { width } = Dimensions.get('window');

interface ChartDataPoint {
  date: string;
  price: number;
  volume: number;
  ma_50: number | null;
  ma_200: number | null;
  ma_250: number | null;
}

interface MovingAverageInfo {
  current: number | null;
  trend: string;
  slope: number;
  distance_from_price?: number;
}

interface BullishConfidence {
  overall_score: number;
  rating: string;
  components: Record<string, number>;
  key_signals: string[];
  risk_factors: string[];
}

interface CandlestickPattern {
  pattern: string;
  timestamp: string;
  strength: number;
  reliability: number;
  direction: string;
  combination_type: string;
  context_required: string;
  description: string;
}

interface PatternSummary {
  total_patterns: number;
  bullish_patterns: number;
  bearish_patterns: number;
  neutral_patterns: number;
  dominant_direction: string;
  strongest_pattern: {
    pattern: string;
    direction: string;
    strength: number;
    reliability: number;
    description: string;
  } | null;
  pattern_confidence: number;
}

interface PatternOutcome {
  pattern: string;
  direction: string;
  reliability: number;
  predicted_correctly: boolean;
  moves: Record<string, number>;
  magnitude: number;
}

interface TrendFollowingAnalysis {
  pattern_outcomes: PatternOutcome[];
  success_rate: number;
  avg_move_after_bullish: number;
  avg_move_after_bearish: number;
  total_patterns_analyzed: number;
}

interface FrequencyChange {
  recent_frequency: number;
  older_frequency: number;
  percent_change: number;
  trend: string;
}

interface FrequencyAnalysis {
  frequency_changes: Record<string, FrequencyChange>;
  regime_shift_detected: boolean;
  current_regime: string;
  significant_changes_count: number;
}

interface PatternEvolution {
  reliability_trend: string;
  strength_trend: string;
  reliability_adjustment: number;
  pattern_characteristics: {
    reliability_improving: boolean;
    strength_improving: boolean;
    overall_quality: string;
  };
}

interface AdaptiveScore {
  base_score: number;
  trend_following_adjustment: number;
  frequency_adjustment: number;
  evolution_adjustment: number;
  final_adaptive_score: number;
  adjustments_summary: Record<string, string>;
}

interface TemporalAnalysis {
  trend_following: TrendFollowingAnalysis;
  frequency_changes: FrequencyAnalysis;
  pattern_evolution: PatternEvolution;
  adaptive_scoring: AdaptiveScore;
}

interface PortfolioChartData {
  symbol: string;
  period: string;
  current_price: number;
  chart_data: ChartDataPoint[];
  moving_averages: {
    ma_50: MovingAverageInfo;
    ma_200: MovingAverageInfo;
    ma_250: MovingAverageInfo;
    golden_cross: boolean;
    death_cross: boolean;
    ma_alignment: string;
  };
  fibonacci_analysis: {
    levels: any[];
    golden_ratio_levels: any[];
    current_fib_position: string;
    golden_ratio_strength: number;
    fib_trend_alignment: string;
  };
  bullish_confidence: BullishConfidence;
  candlestick_analysis: {
    patterns: CandlestickPattern[];
    recent_patterns: CandlestickPattern[];
    pattern_summary: PatternSummary;
    temporal_analysis: TemporalAnalysis;
  };
  volume_analysis: any;
  support_resistance: any;
  trend_analysis: any;
}

interface PortfolioChartProps {
  symbol: string;
  defaultPeriod?: string;
}

export default function PortfolioChart({ symbol, defaultPeriod = '1y' }: PortfolioChartProps) {
  const [loading, setLoading] = useState(true);
  const [chartData, setChartData] = useState<PortfolioChartData | null>(null);
  const [selectedPeriod, setSelectedPeriod] = useState(defaultPeriod);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchChartData();
  }, [symbol, selectedPeriod]);

  const fetchChartData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await investmentApi.getPortfolioChartData(symbol, selectedPeriod);
      setChartData(data);
    } catch (err) {
      console.error('Error fetching chart data:', err);
      setError('Failed to load chart data');
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceColor = (score: number): string => {
    if (score >= 80) return '#22c55e';
    if (score >= 65) return '#84cc16';
    if (score >= 50) return '#eab308';
    if (score >= 35) return '#f97316';
    return '#ef4444';
  };

  const getTrendIcon = (trend: string): string => {
    if (trend === 'bullish') return '📈';
    if (trend === 'bearish') return '📉';
    return '➡️';
  };

  const renderSimpleChart = () => {
    if (!chartData) return null;

    const data = chartData.chart_data;
    const minPrice = Math.min(...data.map(d => d.price));
    const maxPrice = Math.max(...data.map(d => d.price));
    const priceRange = maxPrice - minPrice;
    
    const chartWidth = width - 40;
    const chartHeight = 200;
    const pointWidth = chartWidth / (data.length - 1);

    // Prepare MA lines (filter nulls)
    const ma50Points = data.map((d, i) => ({
      x: i * pointWidth,
      y: d.ma_50 ? chartHeight - ((d.ma_50 - minPrice) / priceRange) * chartHeight : null,
      value: d.ma_50
    })).filter(p => p.y !== null);

    const ma200Points = data.map((d, i) => ({
      x: i * pointWidth,
      y: d.ma_200 ? chartHeight - ((d.ma_200 - minPrice) / priceRange) * chartHeight : null,
      value: d.ma_200
    })).filter(p => p.y !== null);

    const ma250Points = data.map((d, i) => ({
      x: i * pointWidth,
      y: d.ma_250 ? chartHeight - ((d.ma_250 - minPrice) / priceRange) * chartHeight : null,
      value: d.ma_250
    })).filter(p => p.y !== null);

    return (
      <View style={styles.chartContainer}>
        <Text style={styles.chartTitle}>{chartData.symbol} Price Chart</Text>
        
        {/* Price Line */}
        <View style={[styles.chart, { height: chartHeight }]}>
          {data.map((point, index) => {
            const x = index * pointWidth;
            const y = chartHeight - ((point.price - minPrice) / priceRange) * chartHeight;
            
            return (
              <View
                key={index}
                style={[
                  styles.pricePoint,
                  {
                    left: x,
                    bottom: y,
                  }
                ]}
              />
            );
          })}
          
          {/* MA Lines (visual representation) */}
          {ma50Points.length > 0 && (
            <View style={styles.maLine}>
              <Text style={[styles.maLabel, { color: '#3b82f6' }]}>MA50</Text>
            </View>
          )}
          {ma200Points.length > 0 && (
            <View style={[styles.maLine, { top: 30 }]}>
              <Text style={[styles.maLabel, { color: '#8b5cf6' }]}>MA200</Text>
            </View>
          )}
          {ma250Points.length > 0 && (
            <View style={[styles.maLine, { top: 60 }]}>
              <Text style={[styles.maLabel, { color: '#ec4899' }]}>MA250</Text>
            </View>
          )}
        </View>

        <View style={styles.priceInfo}>
          <Text style={styles.priceLabel}>Current Price</Text>
          <Text style={styles.priceValue}>${chartData.current_price.toFixed(2)}</Text>
        </View>
      </View>
    );
  };

  const renderMovingAverages = () => {
    if (!chartData) return null;

    const { moving_averages } = chartData;

    return (
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📊 Moving Averages</Text>
        
        {/* MA Alignment */}
        <View style={styles.alignmentCard}>
          <Text style={styles.alignmentTitle}>MA Alignment</Text>
          <View style={[
            styles.alignmentBadge,
            { backgroundColor: moving_averages.ma_alignment.includes('bullish') ? '#22c55e' : '#ef4444' }
          ]}>
            <Text style={styles.alignmentText}>
              {moving_averages.ma_alignment.replace('_', ' ').toUpperCase()}
            </Text>
          </View>
          
          {moving_averages.golden_cross && (
            <Text style={styles.crossSignal}>🌟 Golden Cross Detected!</Text>
          )}
          {moving_averages.death_cross && (
            <Text style={[styles.crossSignal, { color: '#ef4444' }]}>⚠️ Death Cross Detected</Text>
          )}
        </View>

        {/* Individual MAs */}
        <View style={styles.maGrid}>
          {/* MA 50 */}
          <View style={styles.maCard}>
            <Text style={styles.maTitle}>50-Day MA</Text>
            <Text style={styles.maValue}>
              ${moving_averages.ma_50.current?.toFixed(2) || 'N/A'}
            </Text>
            <Text style={styles.maTrend}>
              {getTrendIcon(moving_averages.ma_50.trend)} {moving_averages.ma_50.trend}
            </Text>
          </View>

          {/* MA 200 */}
          <View style={styles.maCard}>
            <Text style={styles.maTitle}>200-Day MA</Text>
            <Text style={styles.maValue}>
              ${moving_averages.ma_200.current?.toFixed(2) || 'N/A'}
            </Text>
            <Text style={styles.maTrend}>
              {getTrendIcon(moving_averages.ma_200.trend)} {moving_averages.ma_200.trend}
            </Text>
          </View>

          {/* MA 250 */}
          <View style={styles.maCard}>
            <Text style={styles.maTitle}>250-Day MA</Text>
            <Text style={styles.maValue}>
              ${moving_averages.ma_250.current?.toFixed(2) || 'N/A'}
            </Text>
            <Text style={styles.maTrend}>
              {getTrendIcon(moving_averages.ma_250.trend)} {moving_averages.ma_250.trend}
            </Text>
            {moving_averages.ma_250.distance_from_price !== undefined && (
              <Text style={[
                styles.distanceText,
                { color: moving_averages.ma_250.distance_from_price > 0 ? '#22c55e' : '#ef4444' }
              ]}>
                {moving_averages.ma_250.distance_from_price > 0 ? '+' : ''}
                {moving_averages.ma_250.distance_from_price.toFixed(1)}% from price
              </Text>
            )}
          </View>
        </View>
      </View>
    );
  };

  const renderFibonacciAnalysis = () => {
    if (!chartData) return null;

    const { fibonacci_analysis } = chartData;

    return (
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>✨ Fibonacci Golden Ratio Analysis</Text>
        
        <View style={styles.fibCard}>
          <View style={styles.fibRow}>
            <Text style={styles.fibLabel}>Current Position:</Text>
            <Text style={styles.fibValue}>
              {fibonacci_analysis.current_fib_position.replace('_', ' ')}
            </Text>
          </View>

          <View style={styles.fibRow}>
            <Text style={styles.fibLabel}>Golden Ratio Strength:</Text>
            <View style={styles.strengthBar}>
              <View
                style={[
                  styles.strengthFill,
                  {
                    width: `${fibonacci_analysis.golden_ratio_strength}%`,
                    backgroundColor: getConfidenceColor(fibonacci_analysis.golden_ratio_strength)
                  }
                ]}
              />
            </View>
            <Text style={styles.strengthValue}>
              {fibonacci_analysis.golden_ratio_strength.toFixed(0)}%
            </Text>
          </View>

          <View style={styles.fibRow}>
            <Text style={styles.fibLabel}>Trend Alignment:</Text>
            <Text style={[
              styles.fibValue,
              { 
                color: fibonacci_analysis.fib_trend_alignment === 'bullish' ? '#22c55e' : 
                       fibonacci_analysis.fib_trend_alignment === 'bearish' ? '#ef4444' : '#eab308'
              }
            ]}>
              {fibonacci_analysis.fib_trend_alignment}
            </Text>
          </View>
        </View>

        {/* Key Fibonacci Levels */}
        <Text style={styles.subsectionTitle}>Key Levels (Golden Ratio Related)</Text>
        <View style={styles.fibLevels}>
          {fibonacci_analysis.golden_ratio_levels.slice(0, 5).map((level: any, index: number) => (
            <View key={index} style={styles.fibLevelCard}>
              <Text style={styles.fibLevelLabel}>{(level.level * 100).toFixed(1)}%</Text>
              <Text style={styles.fibLevelPrice}>${level.price.toFixed(2)}</Text>
              {level.level === 0.618 && (
                <Text style={styles.goldenLabel}>✨ Golden</Text>
              )}
            </View>
          ))}
        </View>
      </View>
    );
  };

  const renderBullishConfidence = () => {
    if (!chartData) return null;

    const { bullish_confidence } = chartData;
    const confidenceColor = getConfidenceColor(bullish_confidence.overall_score);

    return (
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🎯 Enhanced Bullish Confidence</Text>
        
        {/* Overall Score */}
        <View style={[styles.confidenceCard, { borderColor: confidenceColor }]}>
          <View style={styles.confidenceHeader}>
            <Text style={styles.confidenceLabel}>Confidence Score</Text>
            <Text style={[styles.confidenceRating, { color: confidenceColor }]}>
              {bullish_confidence.rating}
            </Text>
          </View>
          
          <View style={styles.scoreCircle}>
            <Text style={[styles.scoreText, { color: confidenceColor }]}>
              {bullish_confidence.overall_score.toFixed(1)}
            </Text>
            <Text style={styles.scoreLabel}>/ 100</Text>
          </View>
        </View>

        {/* Components Breakdown */}
        <Text style={styles.subsectionTitle}>Score Components</Text>
        <View style={styles.componentsGrid}>
          {Object.entries(bullish_confidence.components).map(([key, value]) => (
            <View key={key} style={styles.componentCard}>
              <Text style={styles.componentLabel}>
                {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </Text>
              <Text style={[
                styles.componentValue,
                { color: (value as number) > 8 ? '#22c55e' : (value as number) > 4 ? '#eab308' : '#ef4444' }
              ]}>
                {(value as number).toFixed(1)}
              </Text>
            </View>
          ))}
        </View>

        {/* Key Signals */}
        {bullish_confidence.key_signals.length > 0 && (
          <>
            <Text style={styles.subsectionTitle}>✅ Key Signals</Text>
            {bullish_confidence.key_signals.map((signal, index) => (
              <Text key={index} style={styles.signalText}>{signal}</Text>
            ))}
          </>
        )}

        {/* Risk Factors */}
        {bullish_confidence.risk_factors.length > 0 && (
          <>
            <Text style={[styles.subsectionTitle, { color: '#f97316' }]}>⚠️ Risk Factors</Text>
            {bullish_confidence.risk_factors.map((risk, index) => (
              <Text key={index} style={styles.riskText}>{risk}</Text>
            ))}
          </>
        )}
      </View>
    );
  };

  const renderCandlestickPatterns = () => {
    if (!chartData || !chartData.candlestick_analysis) return null;

    const { candlestick_analysis } = chartData;
    const { pattern_summary, recent_patterns } = candlestick_analysis;

    // Get direction color
    const getDirectionColor = (direction: string) => {
      if (direction === 'bullish') return '#22c55e';
      if (direction === 'bearish') return '#ef4444';
      return '#64748b';
    };

    const getDirectionEmoji = (direction: string) => {
      if (direction === 'bullish') return '🟢';
      if (direction === 'bearish') return '🔴';
      return '⚪';
    };

    const getReliabilityBadge = (reliability: number) => {
      if (reliability >= 85) return { text: 'VERY HIGH', color: '#22c55e' };
      if (reliability >= 75) return { text: 'HIGH', color: '#84cc16' };
      if (reliability >= 65) return { text: 'MEDIUM', color: '#eab308' };
      return { text: 'LOW', color: '#94a3b8' };
    };

    const formatPatternName = (pattern: string) => {
      return pattern
        .replace(/_/g, ' ')
        .split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
    };

    return (
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🕯️ Candlestick Pattern Analysis</Text>
        
        {/* Pattern Summary Card */}
        <View style={styles.patternSummaryCard}>
          <View style={styles.patternSummaryHeader}>
            <Text style={styles.patternSummaryTitle}>Pattern Summary</Text>
            <View style={[styles.confidenceBadge, { 
              backgroundColor: pattern_summary.pattern_confidence >= 65 ? '#22c55e20' : '#eab30820'
            }]}>
              <Text style={[styles.confidenceBadgeText, {
                color: pattern_summary.pattern_confidence >= 65 ? '#22c55e' : '#eab308'
              }]}>
                {pattern_summary.pattern_confidence.toFixed(0)}% Confidence
              </Text>
            </View>
          </View>

          <View style={styles.patternSummaryStats}>
            <View style={styles.patternStat}>
              <Text style={styles.patternStatLabel}>Total</Text>
              <Text style={styles.patternStatValue}>{pattern_summary.total_patterns}</Text>
            </View>
            <View style={styles.patternStat}>
              <Text style={styles.patternStatLabel}>🟢 Bullish</Text>
              <Text style={[styles.patternStatValue, { color: '#22c55e' }]}>
                {pattern_summary.bullish_patterns}
              </Text>
            </View>
            <View style={styles.patternStat}>
              <Text style={styles.patternStatLabel}>🔴 Bearish</Text>
              <Text style={[styles.patternStatValue, { color: '#ef4444' }]}>
                {pattern_summary.bearish_patterns}
              </Text>
            </View>
            <View style={styles.patternStat}>
              <Text style={styles.patternStatLabel}>⚪ Neutral</Text>
              <Text style={styles.patternStatValue}>{pattern_summary.neutral_patterns}</Text>
            </View>
          </View>

          {/* Dominant Direction */}
          <View style={[styles.dominantDirection, {
            backgroundColor: getDirectionColor(pattern_summary.dominant_direction) + '20'
          }]}>
            <Text style={[styles.dominantDirectionText, {
              color: getDirectionColor(pattern_summary.dominant_direction)
            }]}>
              {getDirectionEmoji(pattern_summary.dominant_direction)} Dominant Direction: {
                pattern_summary.dominant_direction.charAt(0).toUpperCase() + 
                pattern_summary.dominant_direction.slice(1)
              }
            </Text>
          </View>
        </View>

        {/* Strongest Pattern */}
        {pattern_summary.strongest_pattern && (
          <>
            <Text style={styles.subsectionTitle}>💪 Strongest Pattern</Text>
            <View style={[styles.patternCard, {
              borderColor: getDirectionColor(pattern_summary.strongest_pattern.direction)
            }]}>
              <View style={styles.patternCardHeader}>
                <Text style={styles.patternName}>
                  {formatPatternName(pattern_summary.strongest_pattern.pattern)}
                </Text>
                <View style={[styles.reliabilityBadge, {
                  backgroundColor: getReliabilityBadge(pattern_summary.strongest_pattern.reliability).color + '20'
                }]}>
                  <Text style={[styles.reliabilityBadgeText, {
                    color: getReliabilityBadge(pattern_summary.strongest_pattern.reliability).color
                  }]}>
                    {getReliabilityBadge(pattern_summary.strongest_pattern.reliability).text}
                  </Text>
                </View>
              </View>

              <Text style={styles.patternDescription}>
                {pattern_summary.strongest_pattern.description}
              </Text>

              <View style={styles.patternMetrics}>
                <View style={styles.patternMetric}>
                  <Text style={styles.patternMetricLabel}>Direction</Text>
                  <Text style={[styles.patternMetricValue, {
                    color: getDirectionColor(pattern_summary.strongest_pattern.direction)
                  }]}>
                    {getDirectionEmoji(pattern_summary.strongest_pattern.direction)} {
                      pattern_summary.strongest_pattern.direction.charAt(0).toUpperCase() +
                      pattern_summary.strongest_pattern.direction.slice(1)
                    }
                  </Text>
                </View>
                <View style={styles.patternMetric}>
                  <Text style={styles.patternMetricLabel}>Strength</Text>
                  <Text style={styles.patternMetricValue}>
                    {pattern_summary.strongest_pattern.strength}%
                  </Text>
                </View>
                <View style={styles.patternMetric}>
                  <Text style={styles.patternMetricLabel}>Reliability</Text>
                  <Text style={styles.patternMetricValue}>
                    {pattern_summary.strongest_pattern.reliability}%
                  </Text>
                </View>
              </View>
            </View>
          </>
        )}

        {/* Recent Patterns */}
        {recent_patterns.length > 0 && (
          <>
            <Text style={styles.subsectionTitle}>📊 Recent Patterns (Last 5)</Text>
            {recent_patterns.map((pattern, index) => (
              <View
                key={`${pattern.pattern}-${index}`}
                style={[styles.recentPatternCard, {
                  borderLeftColor: getDirectionColor(pattern.direction),
                  borderLeftWidth: 4
                }]}
              >
                <View style={styles.recentPatternHeader}>
                  <Text style={styles.recentPatternName}>
                    {formatPatternName(pattern.pattern)}
                  </Text>
                  <Text style={[styles.recentPatternDirection, {
                    color: getDirectionColor(pattern.direction)
                  }]}>
                    {getDirectionEmoji(pattern.direction)} {pattern.direction.toUpperCase()}
                  </Text>
                </View>
                
                <Text style={styles.recentPatternDescription}>
                  {pattern.description}
                </Text>

                <View style={styles.recentPatternFooter}>
                  <Text style={styles.recentPatternType}>
                    {pattern.combination_type.replace(/_/g, ' ')}
                  </Text>
                  <Text style={styles.recentPatternMetric}>
                    Strength: {pattern.strength}%
                  </Text>
                  <Text style={styles.recentPatternMetric}>
                    Reliability: {pattern.reliability}%
                  </Text>
                </View>
              </View>
            ))}
          </>
        )}
      </View>
    );
  };

  const renderTemporalAnalysis = () => {
    if (!chartData || !chartData.candlestick_analysis?.temporal_analysis) return null;

    const { temporal_analysis } = chartData.candlestick_analysis;
    const { trend_following, frequency_changes, pattern_evolution, adaptive_scoring } = temporal_analysis;

    if (!adaptive_scoring) return null;

    return (
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>⏱️ Temporal Pattern Analysis</Text>
        
        {/* Adaptive Scoring Card */}
        <View style={styles.adaptiveScoreCard}>
          <Text style={styles.adaptiveScoreTitle}>Adaptive Pattern Score</Text>
          <Text style={styles.adaptiveScoreSubtitle}>
            Score adjusts based on recent pattern performance
          </Text>
          
          <View style={styles.adaptiveScoreDisplay}>
            <Text style={[styles.adaptiveScoreValue, {
              color: adaptive_scoring.final_adaptive_score >= 70 ? '#22c55e' :
                     adaptive_scoring.final_adaptive_score >= 50 ? '#eab308' : '#ef4444'
            }]}>
              {adaptive_scoring.final_adaptive_score?.toFixed(1) || '50.0'}
            </Text>
            <Text style={styles.adaptiveScoreLabel}>/ 100</Text>
          </View>

          <View style={styles.adjustmentBreakdown}>
            <View style={styles.adjustmentRow}>
              <Text style={styles.adjustmentLabel}>Base Score:</Text>
              <Text style={styles.adjustmentValue}>
                {adaptive_scoring.base_score?.toFixed(1) || '50.0'}
              </Text>
            </View>
            {adaptive_scoring.adjustments_summary && Object.entries(adaptive_scoring.adjustments_summary).map(([key, value]) => (
              <View key={key} style={styles.adjustmentRow}>
                <Text style={styles.adjustmentLabel}>
                  {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:
                </Text>
                <Text style={[styles.adjustmentValue, {
                  color: (value as string).startsWith('+') ? '#22c55e' : 
                         (value as string).startsWith('-') ? '#ef4444' : '#9fb3c8'
                }]}>
                  {value}
                </Text>
              </View>
            ))}
          </View>
        </View>

        {/* Trend Following Performance */}
        {trend_following && trend_following.total_patterns_analyzed > 0 && (
          <>
            <Text style={styles.subsectionTitle}>📊 Pattern Prediction Performance</Text>
            <View style={styles.trendFollowingCard}>
              <View style={styles.trendFollowingStats}>
                <View style={styles.trendFollowingStat}>
                  <Text style={styles.trendFollowingLabel}>Success Rate</Text>
                  <Text style={[styles.trendFollowingValue, {
                    color: trend_following.success_rate >= 60 ? '#22c55e' :
                           trend_following.success_rate >= 45 ? '#eab308' : '#ef4444'
                  }]}>
                    {trend_following.success_rate?.toFixed(1) || '0.0'}%
                  </Text>
                </View>
                <View style={styles.trendFollowingStat}>
                  <Text style={styles.trendFollowingLabel}>Patterns Analyzed</Text>
                  <Text style={styles.trendFollowingValue}>
                    {trend_following.total_patterns_analyzed}
                  </Text>
                </View>
              </View>

              <View style={styles.avgMovesContainer}>
                <View style={styles.avgMoveCard}>
                  <Text style={styles.avgMoveLabel}>Avg Move After Bullish</Text>
                  <Text style={[styles.avgMoveValue, {
                    color: trend_following.avg_move_after_bullish > 0 ? '#22c55e' : '#ef4444'
                  }]}>
                    {trend_following.avg_move_after_bullish > 0 ? '+' : ''}
                    {trend_following.avg_move_after_bullish?.toFixed(2) || '0.00'}%
                  </Text>
                </View>
                <View style={styles.avgMoveCard}>
                  <Text style={styles.avgMoveLabel}>Avg Move After Bearish</Text>
                  <Text style={[styles.avgMoveValue, {
                    color: trend_following.avg_move_after_bearish < 0 ? '#22c55e' : '#ef4444'
                  }]}>
                    {trend_following.avg_move_after_bearish > 0 ? '+' : ''}
                    {trend_following.avg_move_after_bearish?.toFixed(2) || '0.00'}%
                  </Text>
                </View>
              </View>
            </View>
          </>
        )}

        {/* Frequency Changes & Regime Shift */}
        {frequency_changes && (
          <>
            <Text style={styles.subsectionTitle}>🔄 Pattern Frequency Analysis</Text>
            <View style={styles.frequencyCard}>
              <View style={[styles.regimeIndicator, {
                backgroundColor: 
                  frequency_changes.current_regime === 'bullish_dominant' ? '#22c55e20' :
                  frequency_changes.current_regime === 'bearish_dominant' ? '#ef444420' : '#eab30820'
              }]}>
                <Text style={[styles.regimeText, {
                  color: 
                    frequency_changes.current_regime === 'bullish_dominant' ? '#22c55e' :
                    frequency_changes.current_regime === 'bearish_dominant' ? '#ef4444' : '#eab308'
                }]}>
                  Current Regime: {frequency_changes.current_regime?.replace(/_/g, ' ').toUpperCase() || 'UNKNOWN'}
                </Text>
              </View>

              {frequency_changes.regime_shift_detected && (
                <View style={styles.regimeShiftWarning}>
                  <Text style={styles.regimeShiftText}>
                    ⚠️ Regime Shift Detected - {frequency_changes.significant_changes_count} significant pattern changes
                  </Text>
                </View>
              )}

              <Text style={styles.frequencyNote}>
                Pattern frequency comparison: Recent vs Historical windows
              </Text>
            </View>
          </>
        )}

        {/* Pattern Evolution */}
        {pattern_evolution && (
          <>
            <Text style={styles.subsectionTitle}>📈 Pattern Quality Evolution</Text>
            <View style={styles.evolutionCard}>
              <View style={styles.evolutionRow}>
                <Text style={styles.evolutionLabel}>Reliability Trend:</Text>
                <Text style={[styles.evolutionValue, {
                  color: pattern_evolution.pattern_characteristics?.reliability_improving ? '#22c55e' : '#9fb3c8'
                }]}>
                  {pattern_evolution.reliability_trend?.replace(/_/g, ' ').toUpperCase() || 'STABLE'}
                  {pattern_evolution.pattern_characteristics?.reliability_improving ? ' ✓' : ''}
                </Text>
              </View>

              <View style={styles.evolutionRow}>
                <Text style={styles.evolutionLabel}>Strength Trend:</Text>
                <Text style={[styles.evolutionValue, {
                  color: pattern_evolution.pattern_characteristics?.strength_improving ? '#22c55e' : '#9fb3c8'
                }]}>
                  {pattern_evolution.strength_trend?.replace(/_/g, ' ').toUpperCase() || 'STABLE'}
                  {pattern_evolution.pattern_characteristics?.strength_improving ? ' ✓' : ''}
                </Text>
              </View>

              <View style={styles.evolutionRow}>
                <Text style={styles.evolutionLabel}>Overall Quality:</Text>
                <Text style={[styles.evolutionValue, {
                  color: pattern_evolution.pattern_characteristics?.overall_quality === 'improving' ? '#22c55e' : '#9fb3c8'
                }]}>
                  {pattern_evolution.pattern_characteristics?.overall_quality?.toUpperCase() || 'STABLE'}
                </Text>
              </View>
            </View>
          </>
        )}

        <View style={styles.temporalNote}>
          <Text style={styles.temporalNoteText}>
            💡 This analysis adapts the pattern score based on recent performance, frequency shifts, and evolving reliability
          </Text>
        </View>
      </View>
    );
  };

  const renderPeriodSelector = () => {
    const periods = [
      { label: '1M', value: '1mo' },
      { label: '3M', value: '3mo' },
      { label: '6M', value: '6mo' },
      { label: '1Y', value: '1y' },
      { label: '2Y', value: '2y' },
      { label: '5Y', value: '5y' }
    ];

    return (
      <View style={styles.periodSelector}>
        {periods.map(period => (
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
    );
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#3b82f6" />
        <Text style={styles.loadingText}>Loading chart data...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>❌ {error}</Text>
        <TouchableOpacity style={styles.retryButton} onPress={fetchChartData}>
          <Text style={styles.retryButtonText}>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {renderPeriodSelector()}
      {renderSimpleChart()}
      {renderBullishConfidence()}
      {renderCandlestickPatterns()}
      {renderTemporalAnalysis()}
      {renderMovingAverages()}
      {renderFibonacciAnalysis()}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0f1e',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#0a0f1e',
    padding: 20,
  },
  loadingText: {
    color: '#9fb3c8',
    marginTop: 12,
    fontSize: 14,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#0a0f1e',
    padding: 20,
  },
  errorText: {
    color: '#ef4444',
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 16,
  },
  retryButton: {
    backgroundColor: '#3b82f6',
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 8,
  },
  retryButtonText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '600',
  },
  periodSelector: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    padding: 16,
    backgroundColor: '#111a30',
    borderBottomWidth: 1,
    borderBottomColor: '#1e3a8a',
  },
  periodButton: {
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 6,
    backgroundColor: '#0f1930',
  },
  periodButtonActive: {
    backgroundColor: '#3b82f6',
  },
  periodButtonText: {
    color: '#7a8fa5',
    fontSize: 12,
    fontWeight: '600',
  },
  periodButtonTextActive: {
    color: '#ffffff',
  },
  chartContainer: {
    padding: 16,
    backgroundColor: '#111a30',
    marginBottom: 8,
  },
  chartTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#9fb3c8',
    marginBottom: 16,
    textAlign: 'center',
  },
  chart: {
    width: '100%',
    backgroundColor: '#0f1930',
    borderRadius: 8,
    position: 'relative',
    marginBottom: 16,
  },
  pricePoint: {
    position: 'absolute',
    width: 3,
    height: 3,
    backgroundColor: '#22c55e',
    borderRadius: 1.5,
  },
  maLine: {
    position: 'absolute',
    top: 10,
    left: 10,
  },
  maLabel: {
    fontSize: 10,
    fontWeight: 'bold',
  },
  priceInfo: {
    alignItems: 'center',
  },
  priceLabel: {
    fontSize: 12,
    color: '#7a8fa5',
    marginBottom: 4,
  },
  priceValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#9fb3c8',
  },
  section: {
    padding: 16,
    backgroundColor: '#111a30',
    marginBottom: 8,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#9fb3c8',
    marginBottom: 16,
  },
  subsectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#9fb3c8',
    marginTop: 16,
    marginBottom: 8,
  },
  alignmentCard: {
    backgroundColor: '#0f1930',
    borderRadius: 8,
    padding: 16,
    marginBottom: 16,
  },
  alignmentTitle: {
    fontSize: 14,
    color: '#7a8fa5',
    marginBottom: 8,
  },
  alignmentBadge: {
    alignSelf: 'flex-start',
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 6,
    marginBottom: 12,
  },
  alignmentText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  crossSignal: {
    fontSize: 14,
    color: '#22c55e',
    fontWeight: '600',
  },
  maGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  maCard: {
    width: '48%',
    backgroundColor: '#0f1930',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
  },
  maTitle: {
    fontSize: 12,
    color: '#7a8fa5',
    marginBottom: 8,
  },
  maValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#9fb3c8',
    marginBottom: 4,
  },
  maTrend: {
    fontSize: 12,
    color: '#9fb3c8',
  },
  distanceText: {
    fontSize: 10,
    marginTop: 4,
  },
  fibCard: {
    backgroundColor: '#0f1930',
    borderRadius: 8,
    padding: 16,
    marginBottom: 16,
  },
  fibRow: {
    marginBottom: 16,
  },
  fibLabel: {
    fontSize: 12,
    color: '#7a8fa5',
    marginBottom: 4,
  },
  fibValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#9fb3c8',
  },
  strengthBar: {
    height: 8,
    backgroundColor: '#1e3a8a',
    borderRadius: 4,
    overflow: 'hidden',
    marginVertical: 8,
  },
  strengthFill: {
    height: '100%',
  },
  strengthValue: {
    fontSize: 12,
    color: '#9fb3c8',
    fontWeight: '600',
  },
  fibLevels: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  fibLevelCard: {
    width: '30%',
    backgroundColor: '#0f1930',
    borderRadius: 6,
    padding: 10,
    marginBottom: 8,
    alignItems: 'center',
  },
  fibLevelLabel: {
    fontSize: 10,
    color: '#7a8fa5',
    marginBottom: 4,
  },
  fibLevelPrice: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#9fb3c8',
  },
  goldenLabel: {
    fontSize: 8,
    color: '#fbbf24',
    marginTop: 4,
  },
  confidenceCard: {
    backgroundColor: '#0f1930',
    borderRadius: 8,
    padding: 16,
    marginBottom: 16,
    borderWidth: 2,
  },
  confidenceHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  confidenceLabel: {
    fontSize: 14,
    color: '#7a8fa5',
  },
  confidenceRating: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  scoreCircle: {
    alignItems: 'center',
  },
  scoreText: {
    fontSize: 48,
    fontWeight: 'bold',
  },
  scoreLabel: {
    fontSize: 14,
    color: '#7a8fa5',
  },
  componentsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  componentCard: {
    width: '48%',
    backgroundColor: '#0f1930',
    borderRadius: 6,
    padding: 10,
    marginBottom: 8,
  },
  componentLabel: {
    fontSize: 10,
    color: '#7a8fa5',
    marginBottom: 4,
  },
  componentValue: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  signalText: {
    fontSize: 12,
    color: '#22c55e',
    marginBottom: 6,
    paddingLeft: 8,
  },
  riskText: {
    fontSize: 12,
    color: '#f97316',
    marginBottom: 6,
    paddingLeft: 8,
  },
  // Candlestick Pattern Styles
  patternSummaryCard: {
    backgroundColor: '#0f1930',
    borderRadius: 8,
    padding: 16,
    marginBottom: 16,
  },
  patternSummaryHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  patternSummaryTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#9fb3c8',
  },
  confidenceBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  confidenceBadgeText: {
    fontSize: 12,
    fontWeight: '600',
  },
  patternSummaryStats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 16,
  },
  patternStat: {
    alignItems: 'center',
  },
  patternStatLabel: {
    fontSize: 11,
    color: '#7a8fa5',
    marginBottom: 4,
  },
  patternStatValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#9fb3c8',
  },
  dominantDirection: {
    padding: 12,
    borderRadius: 6,
    alignItems: 'center',
  },
  dominantDirectionText: {
    fontSize: 14,
    fontWeight: '600',
  },
  patternCard: {
    backgroundColor: '#0f1930',
    borderRadius: 8,
    padding: 16,
    marginBottom: 16,
    borderWidth: 2,
  },
  patternCardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  patternName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#9fb3c8',
    flex: 1,
  },
  reliabilityBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 10,
  },
  reliabilityBadgeText: {
    fontSize: 10,
    fontWeight: '700',
  },
  patternDescription: {
    fontSize: 13,
    color: '#7a8fa5',
    marginBottom: 12,
    lineHeight: 18,
  },
  patternMetrics: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  patternMetric: {
    alignItems: 'center',
  },
  patternMetricLabel: {
    fontSize: 10,
    color: '#7a8fa5',
    marginBottom: 4,
  },
  patternMetricValue: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#9fb3c8',
  },
  recentPatternCard: {
    backgroundColor: '#0f1930',
    borderRadius: 6,
    padding: 12,
    marginBottom: 12,
    borderLeftWidth: 4,
  },
  recentPatternHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  recentPatternName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#9fb3c8',
    flex: 1,
  },
  recentPatternDirection: {
    fontSize: 11,
    fontWeight: '700',
  },
  recentPatternDescription: {
    fontSize: 12,
    color: '#7a8fa5',
    marginBottom: 8,
    lineHeight: 16,
  },
  recentPatternFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  recentPatternType: {
    fontSize: 10,
    color: '#64748b',
    fontStyle: 'italic',
  },
  recentPatternMetric: {
    fontSize: 10,
    color: '#7a8fa5',
  },
  // Temporal Analysis Styles
  adaptiveScoreCard: {
    backgroundColor: '#0f1930',
    borderRadius: 8,
    padding: 16,
    marginBottom: 16,
  },
  adaptiveScoreTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#9fb3c8',
    marginBottom: 4,
  },
  adaptiveScoreSubtitle: {
    fontSize: 12,
    color: '#7a8fa5',
    marginBottom: 16,
  },
  adaptiveScoreDisplay: {
    alignItems: 'center',
    marginBottom: 16,
  },
  adaptiveScoreValue: {
    fontSize: 42,
    fontWeight: 'bold',
  },
  adaptiveScoreLabel: {
    fontSize: 14,
    color: '#7a8fa5',
  },
  adjustmentBreakdown: {
    backgroundColor: '#0a0f1e',
    borderRadius: 6,
    padding: 12,
  },
  adjustmentRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  adjustmentLabel: {
    fontSize: 12,
    color: '#7a8fa5',
  },
  adjustmentValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#9fb3c8',
  },
  trendFollowingCard: {
    backgroundColor: '#0f1930',
    borderRadius: 8,
    padding: 16,
    marginBottom: 16,
  },
  trendFollowingStats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 16,
  },
  trendFollowingStat: {
    alignItems: 'center',
  },
  trendFollowingLabel: {
    fontSize: 11,
    color: '#7a8fa5',
    marginBottom: 6,
    textAlign: 'center',
  },
  trendFollowingValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#9fb3c8',
  },
  avgMovesContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  avgMoveCard: {
    flex: 1,
    backgroundColor: '#0a0f1e',
    borderRadius: 6,
    padding: 12,
    marginHorizontal: 4,
    alignItems: 'center',
  },
  avgMoveLabel: {
    fontSize: 10,
    color: '#7a8fa5',
    marginBottom: 8,
    textAlign: 'center',
  },
  avgMoveValue: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  frequencyCard: {
    backgroundColor: '#0f1930',
    borderRadius: 8,
    padding: 16,
    marginBottom: 16,
  },
  regimeIndicator: {
    padding: 12,
    borderRadius: 6,
    marginBottom: 12,
    alignItems: 'center',
  },
  regimeText: {
    fontSize: 14,
    fontWeight: '600',
  },
  regimeShiftWarning: {
    backgroundColor: '#f9731620',
    padding: 10,
    borderRadius: 6,
    marginBottom: 12,
  },
  regimeShiftText: {
    fontSize: 12,
    color: '#f97316',
    textAlign: 'center',
  },
  frequencyNote: {
    fontSize: 11,
    color: '#7a8fa5',
    fontStyle: 'italic',
    textAlign: 'center',
  },
  evolutionCard: {
    backgroundColor: '#0f1930',
    borderRadius: 8,
    padding: 16,
    marginBottom: 16,
  },
  evolutionRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  evolutionLabel: {
    fontSize: 13,
    color: '#7a8fa5',
  },
  evolutionValue: {
    fontSize: 13,
    fontWeight: '600',
  },
  temporalNote: {
    backgroundColor: '#3b82f620',
    padding: 12,
    borderRadius: 6,
  },
  temporalNoteText: {
    fontSize: 11,
    color: '#3b82f6',
    textAlign: 'center',
    lineHeight: 16,
  },
});
