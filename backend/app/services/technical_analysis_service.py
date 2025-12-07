from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import math
import logging
from dataclasses import dataclass
from enum import Enum

from .insider_analysis_service import insider_analysis_service

logger = logging.getLogger(__name__)

class CandlestickPattern(Enum):
    """Candlestick pattern types"""
    # Single candle patterns
    BULLISH_ENGULFING = "bullish_engulfing"
    BEARISH_ENGULFING = "bearish_engulfing"
    HAMMER = "hammer"
    SHOOTING_STAR = "shooting_star"
    DOJI = "doji"
    MORNING_STAR = "morning_star"
    EVENING_STAR = "evening_star"
    PIERCING_LINE = "piercing_line"
    DARK_CLOUD_COVER = "dark_cloud_cover"
    
    # Multi-candle combination patterns
    THREE_WHITE_SOLDIERS = "three_white_soldiers"
    THREE_BLACK_CROWS = "three_black_crows"
    RISING_THREE_METHODS = "rising_three_methods"
    FALLING_THREE_METHODS = "falling_three_methods"
    BULLISH_HARAMI = "bullish_harami"
    BEARISH_HARAMI = "bearish_harami"
    TWEEZER_TOP = "tweezer_top"
    TWEEZER_BOTTOM = "tweezer_bottom"
    THREE_INSIDE_UP = "three_inside_up"
    THREE_INSIDE_DOWN = "three_inside_down"
    BULLISH_ABANDONED_BABY = "bullish_abandoned_baby"
    BEARISH_ABANDONED_BABY = "bearish_abandoned_baby"
    TRIPLE_BOTTOM = "triple_bottom"
    TRIPLE_TOP = "triple_top"
    
class PatternReliability(Enum):
    """Historical pattern reliability scores"""
    VERY_HIGH = 85  # 85%+ historical accuracy
    HIGH = 75       # 75-84% historical accuracy
    MEDIUM = 65     # 65-74% historical accuracy
    LOW = 55        # 55-64% historical accuracy

class TrendDirection(Enum):
    """Market trend directions"""
    BULLISH = "bullish"
    BEARISH = "bearish"
    SIDEWAYS = "sideways"

@dataclass
class PriceData:
    """Single price data point"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    
@dataclass
class FibonacciLevel:
    """Fibonacci retracement level"""
    level: float
    price: float
    support_strength: float
    resistance_strength: float

@dataclass
class SupportResistanceLevel:
    """Support or resistance level"""
    price: float
    strength: float
    touches: int
    last_touch: datetime
    level_type: str  # 'support' or 'resistance'

@dataclass
class VolumeAnalysis:
    """Volume movement analysis"""
    avg_volume: float
    volume_trend: TrendDirection
    volume_spike_ratio: float
    price_volume_correlation: float
    accumulation_distribution: float

@dataclass
class TechnicalSignal:
    """Technical analysis signal"""
    signal_type: str
    strength: float  # 0-100
    direction: TrendDirection
    confidence: float  # 0-100
    timeframe: str
    description: str

class TechnicalAnalysisEngine:
    """Advanced technical analysis engine with Fibonacci, support/resistance, and pattern recognition"""
    
    def __init__(self):
        self.golden_ratio = 1.618
        self.fibonacci_levels = [0.236, 0.382, 0.5, 0.618, 0.786]
        self.indicator_weights = self._load_indicator_weights()
    
    def analyze_security(
        self, 
        symbol: str, 
        price_data: List[PriceData],
        analysis_period: int = 252  # 1 year
    ) -> Dict[str, Any]:
        """Comprehensive technical analysis of a security"""
        
        if len(price_data) < 200:
            raise ValueError("Insufficient price data for analysis (minimum 200 periods required)")
        
        # Calculate moving averages
        ma_50 = self._calculate_moving_average(price_data, 50)
        ma_200 = self._calculate_moving_average(price_data, 200)
        
        # Fibonacci analysis
        fibonacci_analysis = self._fibonacci_retracement_analysis(price_data)
        
        # Support and resistance levels
        support_resistance = self._identify_support_resistance_levels(price_data)
        
        # Volume analysis
        volume_analysis = self._analyze_volume_patterns(price_data)

        # On-Balance Volume (OBV)
        obv = self._calculate_on_balance_volume(price_data)

        # Bollinger Bands
        bollinger = self._calculate_bollinger_bands(price_data, window=20, num_std=2)

        # RSI
        rsi = self._calculate_rsi(price_data, period=14)
        
        # Candlestick patterns
        candlestick_patterns = self._detect_candlestick_patterns(price_data[-20:])  # Last 20 periods
        
        # NEW: Temporal pattern analysis
        trend_following_analysis = self._analyze_trend_following_after_patterns(
            candlestick_patterns, price_data
        )
        
        frequency_change_analysis = self._analyze_pattern_frequency_changes(
            candlestick_patterns
        )
        
        pattern_evolution_analysis = self._analyze_pattern_evolution(
            candlestick_patterns
        )
        
        adaptive_pattern_score = self._calculate_adaptive_pattern_score(
            candlestick_patterns,
            trend_following_analysis,
            frequency_change_analysis,
            pattern_evolution_analysis
        )
        
        # Moving average analysis
        ma_analysis = self._analyze_moving_averages(price_data, ma_50, ma_200)
        
        # Trend analysis
        trend_analysis = self._analyze_trend_direction(price_data, ma_50, ma_200)
        
        # Price targets and time predictions
        price_targets = self._calculate_price_targets(price_data, fibonacci_analysis, support_resistance)
        
        # Weighted signal analysis
        weighted_signals = self._calculate_weighted_signals(
            fibonacci_analysis, support_resistance, volume_analysis, 
            candlestick_patterns, ma_analysis
        )
        
        # NEW: Insider Trading & Calculus-Based Analysis
        insider_calculus_analysis = self._analyze_insider_and_calculus(
            symbol, price_data, candlestick_patterns
        )
        
        return {
            "symbol": symbol,
            "analysis_timestamp": datetime.utcnow(),
            "current_price": price_data[-1].close,
            "fibonacci_analysis": fibonacci_analysis,
            "support_resistance": support_resistance,
            "volume_analysis": volume_analysis,
            "obv": obv,
            "bollinger_bands": bollinger,
            "rsi": rsi,
            "candlestick_patterns": candlestick_patterns,
            "pattern_temporal_analysis": {
                "trend_following": trend_following_analysis,
                "frequency_changes": frequency_change_analysis,
                "pattern_evolution": pattern_evolution_analysis,
                "adaptive_score": adaptive_pattern_score
            },
            "insider_calculus_analysis": insider_calculus_analysis,
            "moving_average_analysis": ma_analysis,
            "trend_analysis": trend_analysis,
            "price_targets": price_targets,
            "weighted_signals": weighted_signals,
            "investment_recommendation": self._generate_investment_recommendation(
                weighted_signals, price_targets, trend_analysis
            )
        }
    
    def _fibonacci_retracement_analysis(self, price_data: List[PriceData]) -> Dict[str, Any]:
        """Analyze Fibonacci retracement levels using golden ratio"""
        
        # Find significant swing high and low over the analysis period
        prices = [p.close for p in price_data[-100:]]  # Last 100 periods
        swing_high = max(prices)
        swing_low = min(prices)
        
        swing_high_idx = prices.index(swing_high)
        swing_low_idx = prices.index(swing_low)
        
        # Determine if we're in uptrend or downtrend
        if swing_high_idx > swing_low_idx:
            # Uptrend - calculate retracement from high
            price_range = swing_high - swing_low
            trend_direction = TrendDirection.BULLISH
        else:
            # Downtrend - calculate extension from low
            price_range = swing_high - swing_low
            trend_direction = TrendDirection.BEARISH
        
        fibonacci_levels = []
        current_price = price_data[-1].close
        
        for level in self.fibonacci_levels:
            if trend_direction == TrendDirection.BULLISH:
                fib_price = swing_high - (price_range * level)
            else:
                fib_price = swing_low + (price_range * level)
            
            # Calculate support/resistance strength based on proximity and golden ratio
            distance_ratio = abs(current_price - fib_price) / current_price
            golden_ratio_factor = 1 / (1 + abs(level - 0.618))  # Stronger near golden ratio
            
            support_strength = (1 - distance_ratio) * golden_ratio_factor * 100
            resistance_strength = support_strength
            
            fibonacci_levels.append(FibonacciLevel(
                level=level,
                price=fib_price,
                support_strength=support_strength,
                resistance_strength=resistance_strength
            ))
        
        return {
            "swing_high": swing_high,
            "swing_low": swing_low,
            "price_range": price_range,
            "trend_direction": trend_direction.value,
            "fibonacci_levels": [
                {
                    "level": fl.level,
                    "price": fl.price,
                    "support_strength": fl.support_strength,
                    "resistance_strength": fl.resistance_strength
                } for fl in fibonacci_levels
            ],
            "golden_ratio_analysis": self._analyze_golden_ratio_significance(
                fibonacci_levels, current_price
            )
        }
    
    def _identify_support_resistance_levels(self, price_data: List[PriceData]) -> Dict[str, Any]:
        """Identify key support and resistance levels"""
        
        levels = []
        window_size = 20  # Look for levels over 20-period windows
        
        for i in range(window_size, len(price_data) - window_size):
            current_high = price_data[i].high
            current_low = price_data[i].low
            
            # Check for resistance levels (local highs)
            is_resistance = all(
                current_high >= price_data[j].high 
                for j in range(i - window_size, i + window_size + 1) 
                if j != i
            )
            
            # Check for support levels (local lows)
            is_support = all(
                current_low <= price_data[j].low 
                for j in range(i - window_size, i + window_size + 1) 
                if j != i
            )
            
            if is_resistance:
                strength = self._calculate_level_strength(price_data, current_high, 'resistance')
                levels.append(SupportResistanceLevel(
                    price=current_high,
                    strength=strength,
                    touches=self._count_level_touches(price_data, current_high, 0.01),
                    last_touch=price_data[i].timestamp,
                    level_type='resistance'
                ))
            
            if is_support:
                strength = self._calculate_level_strength(price_data, current_low, 'support')
                levels.append(SupportResistanceLevel(
                    price=current_low,
                    strength=strength,
                    touches=self._count_level_touches(price_data, current_low, 0.01),
                    last_touch=price_data[i].timestamp,
                    level_type='support'
                ))
        
        # Remove duplicate levels and sort by strength
        levels = self._consolidate_levels(levels)
        
        current_price = price_data[-1].close
        nearest_support = self._find_nearest_level(levels, current_price, 'support')
        nearest_resistance = self._find_nearest_level(levels, current_price, 'resistance')
        
        return {
            "support_levels": [
                {
                    "price": level.price,
                    "strength": level.strength,
                    "touches": level.touches,
                    "last_touch": level.last_touch,
                    "distance_from_current": abs(current_price - level.price) / current_price * 100
                }
                for level in levels if level.level_type == 'support'
            ][:10],  # Top 10 support levels
            "resistance_levels": [
                {
                    "price": level.price,
                    "strength": level.strength,
                    "touches": level.touches,
                    "last_touch": level.last_touch,
                    "distance_from_current": abs(current_price - level.price) / current_price * 100
                }
                for level in levels if level.level_type == 'resistance'
            ][:10],  # Top 10 resistance levels
            "nearest_support": nearest_support.price if nearest_support else None,
            "nearest_resistance": nearest_resistance.price if nearest_resistance else None,
            "support_strength": nearest_support.strength if nearest_support else 0,
            "resistance_strength": nearest_resistance.strength if nearest_resistance else 0
        }
    
    def _analyze_volume_patterns(self, price_data: List[PriceData]) -> VolumeAnalysis:
        """Analyze volume patterns and price-volume relationships"""
        
        volumes = [p.volume for p in price_data[-50:]]  # Last 50 periods
        prices = [p.close for p in price_data[-50:]]
        
        avg_volume = sum(volumes) / len(volumes)
        recent_volume = volumes[-10:]  # Last 10 periods
        recent_avg_volume = sum(recent_volume) / len(recent_volume)
        
        # Volume trend analysis
        volume_slope = self._calculate_trend_slope([i for i in range(len(volumes))], volumes)
        if volume_slope > 0.1:
            volume_trend = TrendDirection.BULLISH
        elif volume_slope < -0.1:
            volume_trend = TrendDirection.BEARISH
        else:
            volume_trend = TrendDirection.SIDEWAYS
        
        # Volume spike analysis
        volume_spike_ratio = recent_avg_volume / avg_volume if avg_volume > 0 else 1
        
        # Price-volume correlation
        price_volume_correlation = self._calculate_correlation(prices, volumes)
        
        # Accumulation/Distribution calculation
        accumulation_distribution = self._calculate_accumulation_distribution(price_data[-20:])
        
        return VolumeAnalysis(
            avg_volume=avg_volume,
            volume_trend=volume_trend,
            volume_spike_ratio=volume_spike_ratio,
            price_volume_correlation=price_volume_correlation,
            accumulation_distribution=accumulation_distribution
        )
    
    def _detect_candlestick_patterns(self, price_data: List[PriceData]) -> List[Dict[str, Any]]:
        """Detect advanced candlestick patterns including multi-candle combinations"""
        
        patterns = []
        
        # Need enough data for multi-candle patterns
        if len(price_data) < 5:
            return patterns
        
        for i in range(4, len(price_data)):
            current = price_data[i]
            prev = price_data[i-1]
            prev2 = price_data[i-2]
            prev3 = price_data[i-3]
            prev4 = price_data[i-4]
            
            # Calculate candle properties
            current_body = abs(current.close - current.open)
            current_range = current.high - current.low
            current_lower_shadow = min(current.open, current.close) - current.low
            current_upper_shadow = current.high - max(current.open, current.close)
            
            prev_body = abs(prev.close - prev.open)
            prev_range = prev.high - prev.low
            prev2_body = abs(prev2.close - prev2.open)
            
            # === MULTI-CANDLE COMBINATION PATTERNS ===
            
            # Three White Soldiers (Very Strong Bullish)
            if (self._is_bullish_candle(prev2) and 
                self._is_bullish_candle(prev) and 
                self._is_bullish_candle(current)):
                if (prev.close > prev2.close and 
                    current.close > prev.close and
                    prev.open > prev2.open and 
                    current.open > prev.open):
                    patterns.append({
                        "pattern": CandlestickPattern.THREE_WHITE_SOLDIERS.value,
                        "timestamp": current.timestamp,
                        "strength": 90,
                        "reliability": PatternReliability.VERY_HIGH.value,
                        "direction": TrendDirection.BULLISH.value,
                        "combination_type": "three_candle",
                        "context_required": "after_downtrend",
                        "description": "Three White Soldiers - Very strong bullish reversal pattern"
                    })
            
            # Three Black Crows (Very Strong Bearish)
            if (self._is_bearish_candle(prev2) and 
                self._is_bearish_candle(prev) and 
                self._is_bearish_candle(current)):
                if (prev.close < prev2.close and 
                    current.close < prev.close and
                    prev.open < prev2.open and 
                    current.open < prev.open):
                    patterns.append({
                        "pattern": CandlestickPattern.THREE_BLACK_CROWS.value,
                        "timestamp": current.timestamp,
                        "strength": 90,
                        "reliability": PatternReliability.VERY_HIGH.value,
                        "direction": TrendDirection.BEARISH.value,
                        "combination_type": "three_candle",
                        "context_required": "after_uptrend",
                        "description": "Three Black Crows - Very strong bearish reversal pattern"
                    })
            
            # Morning Star (Strong Bullish Reversal)
            if (self._is_bearish_candle(prev2) and  # First candle bearish
                prev_body < prev2_body * 0.3 and     # Second candle small body (star)
                self._is_bullish_candle(current) and # Third candle bullish
                current.close > (prev2.open + prev2.close) / 2):  # Closes above midpoint of first candle
                patterns.append({
                    "pattern": CandlestickPattern.MORNING_STAR.value,
                    "timestamp": current.timestamp,
                    "strength": 85,
                    "reliability": PatternReliability.VERY_HIGH.value,
                    "direction": TrendDirection.BULLISH.value,
                    "combination_type": "three_candle",
                    "context_required": "after_downtrend",
                    "description": "Morning Star - Strong bullish reversal pattern"
                })
            
            # Evening Star (Strong Bearish Reversal)
            if (self._is_bullish_candle(prev2) and  # First candle bullish
                prev_body < prev2_body * 0.3 and     # Second candle small body (star)
                self._is_bearish_candle(current) and # Third candle bearish
                current.close < (prev2.open + prev2.close) / 2):  # Closes below midpoint of first candle
                patterns.append({
                    "pattern": CandlestickPattern.EVENING_STAR.value,
                    "timestamp": current.timestamp,
                    "strength": 85,
                    "reliability": PatternReliability.VERY_HIGH.value,
                    "direction": TrendDirection.BEARISH.value,
                    "combination_type": "three_candle",
                    "context_required": "after_uptrend",
                    "description": "Evening Star - Strong bearish reversal pattern"
                })
            
            # Bullish Harami
            if (self._is_bearish_candle(prev) and 
                self._is_bullish_candle(current) and
                current.open > prev.close and 
                current.close < prev.open and
                current_body < prev_body * 0.7):
                patterns.append({
                    "pattern": CandlestickPattern.BULLISH_HARAMI.value,
                    "timestamp": current.timestamp,
                    "strength": 70,
                    "reliability": PatternReliability.HIGH.value,
                    "direction": TrendDirection.BULLISH.value,
                    "combination_type": "two_candle",
                    "context_required": "after_downtrend",
                    "description": "Bullish Harami - Potential bullish reversal"
                })
            
            # Bearish Harami
            if (self._is_bullish_candle(prev) and 
                self._is_bearish_candle(current) and
                current.open < prev.close and 
                current.close > prev.open and
                current_body < prev_body * 0.7):
                patterns.append({
                    "pattern": CandlestickPattern.BEARISH_HARAMI.value,
                    "timestamp": current.timestamp,
                    "strength": 70,
                    "reliability": PatternReliability.HIGH.value,
                    "direction": TrendDirection.BEARISH.value,
                    "combination_type": "two_candle",
                    "context_required": "after_uptrend",
                    "description": "Bearish Harami - Potential bearish reversal"
                })
            
            # Three Inside Up (Bullish)
            if (self._is_bearish_candle(prev2) and 
                self._is_bullish_candle(prev) and
                prev.open > prev2.close and 
                prev.close < prev2.open and
                self._is_bullish_candle(current) and
                current.close > prev2.open):
                patterns.append({
                    "pattern": CandlestickPattern.THREE_INSIDE_UP.value,
                    "timestamp": current.timestamp,
                    "strength": 80,
                    "reliability": PatternReliability.HIGH.value,
                    "direction": TrendDirection.BULLISH.value,
                    "combination_type": "three_candle",
                    "context_required": "after_downtrend",
                    "description": "Three Inside Up - Strong bullish reversal confirmation"
                })
            
            # Three Inside Down (Bearish)
            if (self._is_bullish_candle(prev2) and 
                self._is_bearish_candle(prev) and
                prev.open < prev2.close and 
                prev.close > prev2.open and
                self._is_bearish_candle(current) and
                current.close < prev2.open):
                patterns.append({
                    "pattern": CandlestickPattern.THREE_INSIDE_DOWN.value,
                    "timestamp": current.timestamp,
                    "strength": 80,
                    "reliability": PatternReliability.HIGH.value,
                    "direction": TrendDirection.BEARISH.value,
                    "combination_type": "three_candle",
                    "context_required": "after_uptrend",
                    "description": "Three Inside Down - Strong bearish reversal confirmation"
                })
            
            # Tweezer Top (Bearish)
            if (abs(prev.high - current.high) < prev.high * 0.002 and  # Nearly identical highs
                self._is_bullish_candle(prev) and 
                self._is_bearish_candle(current)):
                patterns.append({
                    "pattern": CandlestickPattern.TWEEZER_TOP.value,
                    "timestamp": current.timestamp,
                    "strength": 75,
                    "reliability": PatternReliability.HIGH.value,
                    "direction": TrendDirection.BEARISH.value,
                    "combination_type": "two_candle",
                    "context_required": "at_resistance",
                    "description": "Tweezer Top - Bearish reversal at resistance"
                })
            
            # Tweezer Bottom (Bullish)
            if (abs(prev.low - current.low) < prev.low * 0.002 and  # Nearly identical lows
                self._is_bearish_candle(prev) and 
                self._is_bullish_candle(current)):
                patterns.append({
                    "pattern": CandlestickPattern.TWEEZER_BOTTOM.value,
                    "timestamp": current.timestamp,
                    "strength": 75,
                    "reliability": PatternReliability.HIGH.value,
                    "direction": TrendDirection.BULLISH.value,
                    "combination_type": "two_candle",
                    "context_required": "at_support",
                    "description": "Tweezer Bottom - Bullish reversal at support"
                })
            
            # Rising Three Methods (Bullish Continuation)
            if (self._is_bullish_candle(prev4) and
                self._is_bearish_candle(prev3) and
                self._is_bearish_candle(prev2) and
                self._is_bearish_candle(prev) and
                self._is_bullish_candle(current) and
                current.close > prev4.close and
                prev3.high < prev4.close and
                prev2.high < prev4.close and
                prev.high < prev4.close):
                patterns.append({
                    "pattern": CandlestickPattern.RISING_THREE_METHODS.value,
                    "timestamp": current.timestamp,
                    "strength": 75,
                    "reliability": PatternReliability.HIGH.value,
                    "direction": TrendDirection.BULLISH.value,
                    "combination_type": "five_candle",
                    "context_required": "in_uptrend",
                    "description": "Rising Three Methods - Bullish continuation pattern"
                })
            
            # Falling Three Methods (Bearish Continuation)
            if (self._is_bearish_candle(prev4) and
                self._is_bullish_candle(prev3) and
                self._is_bullish_candle(prev2) and
                self._is_bullish_candle(prev) and
                self._is_bearish_candle(current) and
                current.close < prev4.close and
                prev3.low > prev4.close and
                prev2.low > prev4.close and
                prev.low > prev4.close):
                patterns.append({
                    "pattern": CandlestickPattern.FALLING_THREE_METHODS.value,
                    "timestamp": current.timestamp,
                    "strength": 75,
                    "reliability": PatternReliability.HIGH.value,
                    "direction": TrendDirection.BEARISH.value,
                    "combination_type": "five_candle",
                    "context_required": "in_downtrend",
                    "description": "Falling Three Methods - Bearish continuation pattern"
                })
            
            # === SINGLE CANDLE PATTERNS ===
            
            # Bullish Engulfing
            if (self._is_bearish_candle(prev) and
                self._is_bullish_candle(current) and
                current.open < prev.close and
                current.close > prev.open):
                patterns.append({
                    "pattern": CandlestickPattern.BULLISH_ENGULFING.value,
                    "timestamp": current.timestamp,
                    "strength": 75,
                    "reliability": PatternReliability.HIGH.value,
                    "direction": TrendDirection.BULLISH.value,
                    "combination_type": "two_candle",
                    "context_required": "after_downtrend",
                    "description": "Bullish Engulfing - Potential bullish reversal"
                })
            
            # Bearish Engulfing
            if (self._is_bullish_candle(prev) and
                self._is_bearish_candle(current) and
                current.open > prev.close and
                current.close < prev.open):
                patterns.append({
                    "pattern": CandlestickPattern.BEARISH_ENGULFING.value,
                    "timestamp": current.timestamp,
                    "strength": 75,
                    "reliability": PatternReliability.HIGH.value,
                    "direction": TrendDirection.BEARISH.value,
                    "combination_type": "two_candle",
                    "context_required": "after_uptrend",
                    "description": "Bearish Engulfing - Potential bearish reversal"
                })
            
            # Hammer (bullish reversal at support)
            if (current_range > 0 and
                current_lower_shadow > 2 * current_body and
                current_upper_shadow < 0.5 * current_body):
                patterns.append({
                    "pattern": CandlestickPattern.HAMMER.value,
                    "timestamp": current.timestamp,
                    "strength": 65,
                    "reliability": PatternReliability.MEDIUM.value,
                    "direction": TrendDirection.BULLISH.value,
                    "combination_type": "single_candle",
                    "context_required": "at_support",
                    "description": "Hammer - Potential bullish reversal at support"
                })
            
            # Shooting Star (bearish reversal at resistance)
            if (current_range > 0 and
                current_upper_shadow > 2 * current_body and
                current_lower_shadow < 0.5 * current_body):
                patterns.append({
                    "pattern": CandlestickPattern.SHOOTING_STAR.value,
                    "timestamp": current.timestamp,
                    "strength": 65,
                    "reliability": PatternReliability.MEDIUM.value,
                    "direction": TrendDirection.BEARISH.value,
                    "combination_type": "single_candle",
                    "context_required": "at_resistance",
                    "description": "Shooting Star - Potential bearish reversal at resistance"
                })
            
            # Doji (indecision)
            if current_body < 0.1 * current_range:
                patterns.append({
                    "pattern": CandlestickPattern.DOJI.value,
                    "timestamp": current.timestamp,
                    "strength": 50,
                    "reliability": PatternReliability.LOW.value,
                    "direction": TrendDirection.SIDEWAYS.value,
                    "combination_type": "single_candle",
                    "context_required": "any",
                    "description": "Doji - Market indecision, potential reversal"
                })
        
        return patterns[-15:]  # Return last 15 patterns
    
    def _is_bullish_candle(self, candle: PriceData) -> bool:
        """Check if candle is bullish (close > open)"""
        return candle.close > candle.open
    
    def _is_bearish_candle(self, candle: PriceData) -> bool:
        """Check if candle is bearish (close < open)"""
        return candle.close < candle.open
    
    def _analyze_moving_averages(
        self, 
        price_data: List[PriceData], 
        ma_50: List[float], 
        ma_200: List[float]
    ) -> Dict[str, Any]:
        """Analyze moving average relationships and crossovers"""
        
        current_price = price_data[-1].close
        current_ma_50 = ma_50[-1] if ma_50 else 0
        current_ma_200 = ma_200[-1] if ma_200 else 0
        
        # Golden Cross / Death Cross analysis
        golden_cross = current_ma_50 > current_ma_200
        death_cross = current_ma_50 < current_ma_200
        
        # Price position relative to MAs
        above_ma_50 = current_price > current_ma_50
        above_ma_200 = current_price > current_ma_200
        
        # MA slope analysis
        ma_50_slope = self._calculate_ma_slope(ma_50[-10:]) if len(ma_50) >= 10 else 0
        ma_200_slope = self._calculate_ma_slope(ma_200[-10:]) if len(ma_200) >= 10 else 0
        
        # Crossover detection in recent periods
        recent_crossover = self._detect_recent_crossover(ma_50[-5:], ma_200[-5:])
        
        return {
            "ma_50_current": current_ma_50,
            "ma_200_current": current_ma_200,
            "golden_cross": golden_cross,
            "death_cross": death_cross,
            "price_above_ma_50": above_ma_50,
            "price_above_ma_200": above_ma_200,
            "ma_50_slope": ma_50_slope,
            "ma_200_slope": ma_200_slope,
            "recent_crossover": recent_crossover,
            "ma_alignment": self._assess_ma_alignment(current_price, current_ma_50, current_ma_200)
        }
    
    def _analyze_trend_direction(
        self,
        price_data: List[PriceData],
        ma_50: List[float],
        ma_200: List[float]
    ) -> tuple:
        """Return (slope, days_left) as two ints."""
        # Price trend analysis
        prices = [p.close for p in price_data[-50:]]
        price_slope = self._calculate_trend_slope([i for i in range(len(prices))], prices)
        slope_int = int(round(price_slope * 100))

        # Estimate days_left: days until slope crosses zero if trend continues linearly
        # If slope is zero, days_left is 0 (no trend)
        # If slope is positive, days_left = int(prices[-1] / abs(price_slope)) if price_slope < 0 else a large number
        # If slope is negative, days_left = int(prices[-1] / abs(price_slope)) if price_slope > 0 else a large number
        if price_slope == 0:
            days_left = 0
        else:
            # Estimate how many days until the trend reverses (crosses zero slope)
            # For simplicity, use the magnitude of the last price divided by the slope per day
            try:
                days_left = int(abs(prices[-1] / price_slope)) if price_slope != 0 else 0
                # Cap days_left to a reasonable max (e.g., 10000)
                days_left = max(0, min(days_left, 10000))
            except Exception:
                days_left = 0

        return (slope_int, days_left)
    
    def _calculate_price_targets(
        self, 
        price_data: List[PriceData], 
        fibonacci_analysis: Dict[str, Any],
        support_resistance: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate price targets and optimal exit points"""
        
        current_price = price_data[-1].close
        
        # Fibonacci-based targets
        fib_levels = fibonacci_analysis["fibonacci_levels"]
        
        # Find next resistance level as upside target
        upside_targets = [
            level["price"] for level in fib_levels 
            if level["price"] > current_price
        ]
        
        # Find next support level as downside target
        downside_targets = [
            level["price"] for level in fib_levels 
            if level["price"] < current_price
        ]
        
        # Support/Resistance based targets
        resistance_levels = support_resistance["resistance_levels"]
        support_levels = support_resistance["support_levels"]
        
        # Calculate optimal exit point using risk-reward ratio
        nearest_resistance = min(upside_targets) if upside_targets else None
        nearest_support = max(downside_targets) if downside_targets else None
        
        if nearest_resistance and nearest_support:
            potential_gain = nearest_resistance - current_price
            potential_loss = current_price - nearest_support
            risk_reward_ratio = potential_gain / potential_loss if potential_loss > 0 else 0
            
            # Optimal exit at 2:1 risk-reward or at strong resistance
            if risk_reward_ratio >= 2:
                optimal_exit = nearest_resistance * 0.95  # 5% below resistance for safety
            else:
                optimal_exit = current_price + (potential_loss * 2)  # 2:1 risk-reward
        else:
            optimal_exit = current_price * 1.1  # Default 10% target
        
        # Time period prediction based on historical volatility
        volatility = self._calculate_volatility(price_data[-30:])
        time_to_target = self._estimate_time_to_target(current_price, optimal_exit, volatility)
        
        return {
            "current_price": current_price,
            "upside_targets": sorted(upside_targets)[:3],  # Top 3 upside targets
            "downside_targets": sorted(downside_targets, reverse=True)[:3],  # Top 3 downside targets
            "optimal_exit_price": optimal_exit,
            "stop_loss_price": nearest_support * 1.02 if nearest_support else current_price * 0.95,
            "risk_reward_ratio": risk_reward_ratio if 'risk_reward_ratio' in locals() else 0,
            "estimated_time_to_target": {
                "min_days": time_to_target["min_days"],
                "max_days": time_to_target["max_days"],
                "most_likely_days": time_to_target["most_likely_days"]
            },
            "confidence_level": self._calculate_target_confidence(
                fibonacci_analysis, support_resistance, current_price
            )
        }
    
    def _calculate_weighted_signals(
        self,
        fibonacci_analysis: Dict[str, Any],
        support_resistance: Dict[str, Any],
        volume_analysis: VolumeAnalysis,
        candlestick_patterns: List[Dict[str, Any]],
        ma_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate weighted technical signals based on historical accuracy"""
        
        signals = []
        
        # Fibonacci signals (Weight: 25%)
        fib_signal = self._evaluate_fibonacci_signal(fibonacci_analysis)
        signals.append(TechnicalSignal(
            signal_type="fibonacci",
            strength=fib_signal["strength"],
            direction=TrendDirection(fib_signal["direction"]),
            confidence=fib_signal["confidence"],
            timeframe="medium_term",
            description=fib_signal["description"]
        ))
        
        # Support/Resistance signals (Weight: 30%)
        sr_signal = self._evaluate_support_resistance_signal(support_resistance)
        signals.append(TechnicalSignal(
            signal_type="support_resistance",
            strength=sr_signal["strength"],
            direction=TrendDirection(sr_signal["direction"]),
            confidence=sr_signal["confidence"],
            timeframe="short_term",
            description=sr_signal["description"]
        ))
        
        # Volume signals (Weight: 20%)
        vol_signal = self._evaluate_volume_signal(volume_analysis)
        signals.append(TechnicalSignal(
            signal_type="volume",
            strength=vol_signal["strength"],
            direction=vol_signal["direction"],
            confidence=vol_signal["confidence"],
            timeframe="short_term",
            description=vol_signal["description"]
        ))
        
        # Moving Average signals (Weight: 15%)
        ma_signal = self._evaluate_ma_signal(ma_analysis)
        signals.append(TechnicalSignal(
            signal_type="moving_average",
            strength=ma_signal["strength"],
            direction=TrendDirection(ma_signal["direction"]),
            confidence=ma_signal["confidence"],
            timeframe="long_term",
            description=ma_signal["description"]
        ))
        
        # Candlestick signals (Weight: 10%)
        cs_signal = self._evaluate_candlestick_signal(candlestick_patterns)
        signals.append(TechnicalSignal(
            signal_type="candlestick",
            strength=cs_signal["strength"],
            direction=TrendDirection(cs_signal["direction"]),
            confidence=cs_signal["confidence"],
            timeframe="very_short_term",
            description=cs_signal["description"]
        ))
        
        # Calculate weighted overall signal
        weights = self.indicator_weights
        overall_strength = sum(
            signal.strength * weights[signal.signal_type] for signal in signals
        ) / sum(weights.values())
        
        overall_confidence = sum(
            signal.confidence * weights[signal.signal_type] for signal in signals
        ) / sum(weights.values())
        
        # Determine overall direction
        weighted_directions = {}
        for signal in signals:
            direction = signal.direction.value
            if direction not in weighted_directions:
                weighted_directions[direction] = 0
            weighted_directions[direction] += signal.strength * weights[signal.signal_type]
        
        overall_direction = max(weighted_directions.keys(), key=lambda k: weighted_directions[k])
        
        return {
            "individual_signals": [
                {
                    "type": signal.signal_type,
                    "strength": signal.strength,
                    "direction": signal.direction.value,
                    "confidence": signal.confidence,
                    "timeframe": signal.timeframe,
                    "description": signal.description,
                    "weight": weights[signal.signal_type]
                } for signal in signals
            ],
            "overall_signal": {
                "strength": overall_strength,
                "direction": overall_direction,
                "confidence": overall_confidence,
                "recommendation": self._generate_signal_recommendation(
                    overall_strength, overall_direction, overall_confidence
                )
            }
        }
    
    def _generate_investment_recommendation(
        self,
        weighted_signals: Dict[str, Any],
        price_targets: Dict[str, Any],
        trend_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate final investment recommendation"""
        
        overall_signal = weighted_signals["overall_signal"]
        
        recommendation_type = "hold"
        confidence = overall_signal["confidence"]
        
        if overall_signal["strength"] > 70:
            if overall_signal["direction"] == "bullish":
                recommendation_type = "strong_buy"
            elif overall_signal["direction"] == "bearish":
                recommendation_type = "strong_sell"
        elif overall_signal["strength"] > 50:
            if overall_signal["direction"] == "bullish":
                recommendation_type = "buy"
            elif overall_signal["direction"] == "bearish":
                recommendation_type = "sell"
        
        return {
            "recommendation": recommendation_type,
            "confidence": confidence,
            "target_price": price_targets["optimal_exit_price"],
            "stop_loss": price_targets["stop_loss_price"],
            "time_horizon": price_targets["estimated_time_to_target"],
            "risk_level": self._assess_risk_level(overall_signal, trend_analysis),
            "key_factors": self._identify_key_factors(weighted_signals),
            "reasoning": self._generate_recommendation_reasoning(
                overall_signal, price_targets, trend_analysis
            )
        }
    
    # Helper methods
    def _calculate_moving_average(self, price_data: List[PriceData], period: int) -> List[float]:
        """Calculate simple moving average"""
        if len(price_data) < period:
            return []
        
        ma_values = []
        for i in range(period - 1, len(price_data)):
            period_sum = sum(p.close for p in price_data[i - period + 1:i + 1])
            ma_values.append(period_sum / period)
        
        return ma_values

    def _calculate_on_balance_volume(self, price_data: List[PriceData]) -> List[int]:
        """Calculate On-Balance Volume (OBV)"""
        if not price_data:
            return []
        obv = [price_data[0].volume]
        for i in range(1, len(price_data)):
            if price_data[i].close > price_data[i-1].close:
                obv.append(obv[-1] + price_data[i].volume)
            elif price_data[i].close < price_data[i-1].close:
                obv.append(obv[-1] - price_data[i].volume)
            else:
                obv.append(obv[-1])
        return obv

    def _calculate_bollinger_bands(self, price_data: List[PriceData], window: int = 20, num_std: int = 2) -> dict:
        """Calculate Bollinger Bands"""
        if len(price_data) < window:
            return {"upper": [], "middle": [], "lower": []}
        closes = [p.close for p in price_data]
        bands = {"upper": [], "middle": [], "lower": []}
        for i in range(window - 1, len(closes)):
            window_closes = closes[i - window + 1:i + 1]
            ma = sum(window_closes) / window
            std = (sum((x - ma) ** 2 for x in window_closes) / window) ** 0.5
            bands["middle"].append(ma)
            bands["upper"].append(ma + num_std * std)
            bands["lower"].append(ma - num_std * std)
        return bands

    def _calculate_rsi(self, price_data: List[PriceData], period: int = 14) -> List[float]:
        """Calculate Relative Strength Index (RSI)"""
        if len(price_data) < period + 1:
            return []
        closes = [p.close for p in price_data]
        rsis = []
        for i in range(period, len(closes)):
            gains = 0
            losses = 0
            for j in range(i - period + 1, i + 1):
                change = closes[j] - closes[j - 1]
                if change > 0:
                    gains += change
                else:
                    losses -= change
            avg_gain = gains / period
            avg_loss = losses / period if losses != 0 else 1e-10
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            rsis.append(rsi)
        return rsis
    
    def _calculate_trend_slope(self, x_values: List[int], y_values: List[float]) -> float:
        """Calculate trend slope using linear regression"""
        if len(x_values) != len(y_values) or len(x_values) < 2:
            return 0
        
        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x_squared = sum(x * x for x in x_values)
        
        denominator = n * sum_x_squared - sum_x * sum_x
        if denominator == 0:
            return 0
        
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        return slope
    
    def _calculate_correlation(self, x_values: List[float], y_values: List[float]) -> float:
        """Calculate correlation coefficient between two series"""
        if len(x_values) != len(y_values) or len(x_values) < 2:
            return 0
        
        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x_squared = sum(x * x for x in x_values)
        sum_y_squared = sum(y * y for y in y_values)
        
        numerator = n * sum_xy - sum_x * sum_y
        denominator_x = n * sum_x_squared - sum_x * sum_x
        denominator_y = n * sum_y_squared - sum_y * sum_y
        
        if denominator_x <= 0 or denominator_y <= 0:
            return 0
        
        correlation = numerator / math.sqrt(denominator_x * denominator_y)
        return correlation
    
    def _calculate_volatility(self, price_data: List[PriceData]) -> float:
        """Calculate price volatility"""
        if len(price_data) < 2:
            return 0
        
        returns = []
        for i in range(1, len(price_data)):
            daily_return = (price_data[i].close - price_data[i-1].close) / price_data[i-1].close
            returns.append(daily_return)
        
        if not returns:
            return 0
        
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        
        return math.sqrt(variance) * math.sqrt(252)  # Annualized volatility
    
    def _load_indicator_weights(self) -> Dict[str, float]:
        """Load historical accuracy weights for different indicators"""
        return {
            "support_resistance": 0.30,  # Highest weight - most reliable
            "fibonacci": 0.25,           # Golden ratio analysis
            "volume": 0.20,              # Volume confirms price moves
            "moving_average": 0.15,      # Trend following
            "candlestick": 0.10          # Short-term patterns
        }
    
    def _evaluate_candlestick_signal(self, candlestick_patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate candlestick pattern signals with combination analysis"""
        
        if not candlestick_patterns:
            return {
                "strength": 50,
                "direction": TrendDirection.SIDEWAYS,
                "confidence": 30,
                "description": "No significant candlestick patterns detected"
            }
        
        # Analyze pattern combinations and context
        pattern_analysis = self._analyze_pattern_combinations(candlestick_patterns)
        
        # Weight patterns by reliability and recency
        weighted_score = 0
        direction_scores = {"bullish": 0, "bearish": 0, "sideways": 0}
        total_weight = 0
        
        for i, pattern in enumerate(candlestick_patterns[-10:]):  # Last 10 patterns
            # Recency weight (more recent = higher weight)
            recency_weight = 1.0 - (i * 0.05)  # Decay by 5% per older pattern
            
            # Reliability weight
            reliability_weight = pattern.get("reliability", 65) / 100
            
            # Combination bonus
            combination_bonus = pattern_analysis["combination_bonuses"].get(pattern["pattern"], 0)
            
            # Total weight for this pattern
            pattern_weight = (pattern["strength"] * reliability_weight * recency_weight) + combination_bonus
            
            # Add to direction scores
            direction = pattern["direction"]
            direction_scores[direction] += pattern_weight
            total_weight += pattern_weight
        
        # Determine overall direction
        max_direction = max(direction_scores.keys(), key=lambda k: direction_scores[k])
        direction_strength = direction_scores[max_direction]
        
        # Calculate overall strength (0-100)
        if total_weight > 0:
            strength = min(100, (direction_strength / total_weight) * 100)
        else:
            strength = 50
        
        # Confidence based on pattern agreement and reliability
        confidence = pattern_analysis["overall_confidence"]
        
        # Description
        top_patterns = sorted(
            candlestick_patterns[-5:], 
            key=lambda p: p.get("reliability", 65) * p["strength"], 
            reverse=True
        )[:3]
        
        pattern_names = [p["pattern"].replace("_", " ").title() for p in top_patterns]
        description = f"Detected patterns: {', '.join(pattern_names)}. {pattern_analysis['summary']}"
        
        return {
            "strength": strength,
            "direction": TrendDirection(max_direction),
            "confidence": confidence,
            "description": description,
            "pattern_analysis": pattern_analysis
        }
    
    def _analyze_trend_following_after_patterns(
        self, 
        patterns: List[Dict[str, Any]], 
        price_data: List[PriceData]
    ) -> Dict[str, Any]:
        """
        Analyze price movement following specific patterns
        Measures how well patterns predict subsequent price action
        """
        
        if not patterns or len(price_data) < 20:
            return {
                "pattern_outcomes": [],
                "success_rate": 0,
                "avg_move_after_bullish": 0,
                "avg_move_after_bearish": 0
            }
        
        pattern_outcomes = []
        
        # Track each pattern and subsequent price movement
        for pattern in patterns:
            # Find pattern in price data by timestamp
            pattern_time = pattern["timestamp"]
            pattern_idx = None
            
            for i, price in enumerate(price_data):
                if hasattr(price.timestamp, 'isoformat'):
                    price_time_str = price.timestamp.isoformat()
                else:
                    price_time_str = str(price.timestamp)
                    
                if price_time_str == str(pattern_time):
                    pattern_idx = i
                    break
            
            if pattern_idx is None or pattern_idx >= len(price_data) - 10:
                continue
            
            pattern_price = price_data[pattern_idx].close
            
            # Measure moves at multiple time horizons
            moves = {}
            for days in [1, 3, 5, 10]:
                if pattern_idx + days < len(price_data):
                    future_price = price_data[pattern_idx + days].close
                    pct_change = ((future_price - pattern_price) / pattern_price) * 100
                    moves[f"{days}d"] = pct_change
            
            # Determine if pattern prediction was correct
            direction = pattern["direction"]
            predicted_correctly = False
            
            if "5d" in moves:
                if direction == "bullish" and moves["5d"] > 0:
                    predicted_correctly = True
                elif direction == "bearish" and moves["5d"] < 0:
                    predicted_correctly = True
                elif direction == "sideways" and abs(moves["5d"]) < 1:
                    predicted_correctly = True
            
            pattern_outcomes.append({
                "pattern": pattern["pattern"],
                "direction": direction,
                "reliability": pattern.get("reliability", 65),
                "predicted_correctly": predicted_correctly,
                "moves": moves,
                "magnitude": abs(moves.get("5d", 0))
            })
        
        # Calculate aggregate statistics
        if pattern_outcomes:
            bullish_outcomes = [p for p in pattern_outcomes if p["direction"] == "bullish"]
            bearish_outcomes = [p for p in pattern_outcomes if p["direction"] == "bearish"]
            
            success_rate = (sum(1 for p in pattern_outcomes if p["predicted_correctly"]) / 
                          len(pattern_outcomes) * 100)
            
            avg_move_bullish = (sum(p["moves"].get("5d", 0) for p in bullish_outcomes) / 
                               len(bullish_outcomes)) if bullish_outcomes else 0
            
            avg_move_bearish = (sum(p["moves"].get("5d", 0) for p in bearish_outcomes) / 
                               len(bearish_outcomes)) if bearish_outcomes else 0
        else:
            success_rate = 0
            avg_move_bullish = 0
            avg_move_bearish = 0
        
        return {
            "pattern_outcomes": pattern_outcomes,
            "success_rate": success_rate,
            "avg_move_after_bullish": avg_move_bullish,
            "avg_move_after_bearish": avg_move_bearish,
            "total_patterns_analyzed": len(pattern_outcomes)
        }
    
    def _analyze_pattern_frequency_changes(
        self, 
        patterns: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Detect proportion changes in candlestick patterns over time
        Identifies regime shifts in market behavior
        """
        
        if not patterns or len(patterns) < 10:
            return {
                "frequency_changes": {},
                "regime_shift_detected": False,
                "current_regime": "unknown"
            }
        
        # Split patterns into time windows
        total_patterns = len(patterns)
        window_size = max(5, total_patterns // 3)  # Use 1/3 of data as window
        
        recent_window = patterns[-window_size:]
        older_window = patterns[-2*window_size:-window_size] if len(patterns) >= 2*window_size else patterns[:window_size]
        
        # Count pattern types in each window
        def count_pattern_types(pattern_list):
            counts = {}
            for p in pattern_list:
                ptype = p["pattern"]
                counts[ptype] = counts.get(ptype, 0) + 1
            return counts
        
        recent_counts = count_pattern_types(recent_window)
        older_counts = count_pattern_types(older_window)
        
        # Calculate proportion changes
        frequency_changes = {}
        all_pattern_types = set(list(recent_counts.keys()) + list(older_counts.keys()))
        
        for ptype in all_pattern_types:
            recent_freq = recent_counts.get(ptype, 0) / len(recent_window) if recent_window else 0
            older_freq = older_counts.get(ptype, 0) / len(older_window) if older_window else 0
            
            if older_freq > 0:
                pct_change = ((recent_freq - older_freq) / older_freq) * 100
            else:
                pct_change = 100 if recent_freq > 0 else 0
            
            frequency_changes[ptype] = {
                "recent_frequency": recent_freq,
                "older_frequency": older_freq,
                "percent_change": pct_change,
                "trend": "increasing" if pct_change > 20 else "decreasing" if pct_change < -20 else "stable"
            }
        
        # Detect regime shift
        # Significant shift if multiple patterns show >50% frequency change
        significant_changes = [
            fc for fc in frequency_changes.values() 
            if abs(fc["percent_change"]) > 50
        ]
        
        regime_shift_detected = len(significant_changes) >= 3
        
        # Determine current regime based on dominant pattern types
        recent_bullish = sum(1 for p in recent_window if p["direction"] == "bullish")
        recent_bearish = sum(1 for p in recent_window if p["direction"] == "bearish")
        
        if recent_bullish > recent_bearish * 1.5:
            current_regime = "bullish_dominant"
        elif recent_bearish > recent_bullish * 1.5:
            current_regime = "bearish_dominant"
        else:
            current_regime = "mixed_signals"
        
        return {
            "frequency_changes": frequency_changes,
            "regime_shift_detected": regime_shift_detected,
            "current_regime": current_regime,
            "significant_changes_count": len(significant_changes),
            "recent_window_size": len(recent_window),
            "older_window_size": len(older_window)
        }
    
    def _analyze_pattern_evolution(
        self, 
        patterns: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Track how pattern characteristics evolve over time
        Measures changes in reliability, strength, and effectiveness
        """
        
        if not patterns or len(patterns) < 10:
            return {
                "reliability_trend": "insufficient_data",
                "strength_trend": "insufficient_data",
                "pattern_characteristics": {}
            }
        
        # Split into time periods
        total = len(patterns)
        third = total // 3
        
        period1 = patterns[:third] if third > 0 else []
        period2 = patterns[third:2*third] if 2*third <= total else []
        period3 = patterns[2*third:] if 2*third < total else patterns
        
        def calculate_period_stats(period_patterns):
            if not period_patterns:
                return {"avg_reliability": 0, "avg_strength": 0, "pattern_count": 0}
            
            return {
                "avg_reliability": sum(p.get("reliability", 65) for p in period_patterns) / len(period_patterns),
                "avg_strength": sum(p.get("strength", 50) for p in period_patterns) / len(period_patterns),
                "pattern_count": len(period_patterns),
                "bullish_ratio": sum(1 for p in period_patterns if p["direction"] == "bullish") / len(period_patterns)
            }
        
        p1_stats = calculate_period_stats(period1)
        p2_stats = calculate_period_stats(period2)
        p3_stats = calculate_period_stats(period3)
        
        # Detect trends
        reliability_values = [p1_stats["avg_reliability"], p2_stats["avg_reliability"], p3_stats["avg_reliability"]]
        strength_values = [p1_stats["avg_strength"], p2_stats["avg_strength"], p3_stats["avg_strength"]]
        
        def detect_trend(values):
            if values[2] > values[1] > values[0]:
                return "increasing"
            elif values[2] < values[1] < values[0]:
                return "decreasing"
            elif values[2] > values[0]:
                return "improving"
            elif values[2] < values[0]:
                return "declining"
            else:
                return "stable"
        
        reliability_trend = detect_trend(reliability_values)
        strength_trend = detect_trend(strength_values)
        
        # Calculate adaptive reliability adjustment
        # If recent patterns are more/less reliable, adjust scoring
        recent_reliability = p3_stats["avg_reliability"]
        historical_reliability = (p1_stats["avg_reliability"] + p2_stats["avg_reliability"]) / 2
        
        if historical_reliability > 0:
            reliability_adjustment = ((recent_reliability - historical_reliability) / historical_reliability) * 100
        else:
            reliability_adjustment = 0
        
        return {
            "reliability_trend": reliability_trend,
            "strength_trend": strength_trend,
            "reliability_adjustment": reliability_adjustment,
            "period_statistics": {
                "early_period": p1_stats,
                "middle_period": p2_stats,
                "recent_period": p3_stats
            },
            "pattern_characteristics": {
                "reliability_improving": reliability_trend in ["increasing", "improving"],
                "strength_improving": strength_trend in ["increasing", "improving"],
                "overall_quality": "improving" if reliability_trend in ["increasing", "improving"] else "stable"
            }
        }
    
    def _calculate_adaptive_pattern_score(
        self,
        patterns: List[Dict[str, Any]],
        trend_following: Dict[str, Any],
        frequency_changes: Dict[str, Any],
        evolution: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate pattern confidence score that adapts based on recent performance
        Rather than just using static historical reliability
        """
        
        if not patterns:
            return {
                "base_score": 50,
                "trend_following_adjustment": 0,
                "frequency_adjustment": 0,
                "evolution_adjustment": 0,
                "final_adaptive_score": 50
            }
        
        # Start with base pattern score
        recent_patterns = patterns[-10:]
        bullish_count = sum(1 for p in recent_patterns if p["direction"] == "bullish")
        bearish_count = sum(1 for p in recent_patterns if p["direction"] == "bearish")
        
        if bullish_count > bearish_count:
            base_score = 50 + (bullish_count / len(recent_patterns)) * 30
        else:
            base_score = 50 - (bearish_count / len(recent_patterns)) * 30
        
        # Trend-following adjustment (-15 to +15)
        success_rate = trend_following.get("success_rate", 50)
        trend_following_adjustment = ((success_rate - 50) / 50) * 15
        
        # Frequency adjustment (-10 to +10)
        regime = frequency_changes.get("current_regime", "mixed_signals")
        if regime == "bullish_dominant":
            frequency_adjustment = 10
        elif regime == "bearish_dominant":
            frequency_adjustment = -10
        else:
            frequency_adjustment = 0
        
        # Evolution adjustment (-10 to +10)
        reliability_adj = evolution.get("reliability_adjustment", 0)
        evolution_adjustment = max(-10, min(10, reliability_adj / 10))
        
        # Calculate final score
        final_score = base_score + trend_following_adjustment + frequency_adjustment + evolution_adjustment
        final_score = max(0, min(100, final_score))
        
        return {
            "base_score": base_score,
            "trend_following_adjustment": trend_following_adjustment,
            "frequency_adjustment": frequency_adjustment,
            "evolution_adjustment": evolution_adjustment,
            "final_adaptive_score": final_score,
            "adjustments_summary": {
                "trend_following": f"{'+' if trend_following_adjustment > 0 else ''}{trend_following_adjustment:.1f}",
                "frequency": f"{'+' if frequency_adjustment > 0 else ''}{frequency_adjustment:.1f}",
                "evolution": f"{'+' if evolution_adjustment > 0 else ''}{evolution_adjustment:.1f}"
            }
        }
    
    def _analyze_pattern_combinations(self, patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze pattern combinations for enhanced prediction accuracy"""
        
        if not patterns:
            return {
                "combination_bonuses": {},
                "overall_confidence": 30,
                "summary": "Insufficient pattern data"
            }
        
        combination_bonuses = {}
        combination_analysis = []
        
        # Look for reinforcing pattern combinations
        recent_patterns = patterns[-5:]  # Last 5 patterns
        
        # Count pattern types
        bullish_count = sum(1 for p in recent_patterns if p["direction"] == "bullish")
        bearish_count = sum(1 for p in recent_patterns if p["direction"] == "bearish")
        
        # High reliability pattern combinations
        very_high_reliability = [p for p in recent_patterns if p.get("reliability", 0) >= 85]
        high_reliability = [p for p in recent_patterns if 75 <= p.get("reliability", 0) < 85]
        
        # Combination 1: Multiple Very High Reliability Patterns (Same Direction)
        if len(very_high_reliability) >= 2:
            directions = [p["direction"] for p in very_high_reliability]
            if directions.count("bullish") >= 2:
                combination_analysis.append("Multiple very high reliability bullish patterns detected - Strong confidence")
                for p in very_high_reliability:
                    if p["direction"] == "bullish":
                        combination_bonuses[p["pattern"]] = 15
            elif directions.count("bearish") >= 2:
                combination_analysis.append("Multiple very high reliability bearish patterns detected - Strong confidence")
                for p in very_high_reliability:
                    if p["direction"] == "bearish":
                        combination_bonuses[p["pattern"]] = 15
        
        # Combination 2: Reversal Pattern + Confirmation Pattern
        reversal_patterns = ["morning_star", "evening_star", "bullish_engulfing", "bearish_engulfing",
                            "three_white_soldiers", "three_black_crows"]
        confirmation_patterns = ["three_inside_up", "three_inside_down", "bullish_harami", "bearish_harami"]
        
        has_reversal = any(p["pattern"] in reversal_patterns for p in recent_patterns)
        has_confirmation = any(p["pattern"] in confirmation_patterns for p in recent_patterns)
        
        if has_reversal and has_confirmation:
            reversal_direction = next((p["direction"] for p in recent_patterns if p["pattern"] in reversal_patterns), None)
            confirmation_direction = next((p["direction"] for p in recent_patterns if p["pattern"] in confirmation_patterns), None)
            
            if reversal_direction == confirmation_direction:
                combination_analysis.append(f"Reversal pattern confirmed by follow-up pattern - High confidence {reversal_direction} signal")
                for p in recent_patterns:
                    if p["pattern"] in reversal_patterns or p["pattern"] in confirmation_patterns:
                        combination_bonuses[p["pattern"]] = combination_bonuses.get(p["pattern"], 0) + 10
        
        # Combination 3: Continuation Patterns in Trend
        continuation_patterns = ["rising_three_methods", "falling_three_methods"]
        has_continuation = any(p["pattern"] in continuation_patterns for p in recent_patterns)
        
        if has_continuation:
            combination_analysis.append("Continuation pattern detected - Trend likely to persist")
            for p in recent_patterns:
                if p["pattern"] in continuation_patterns:
                    combination_bonuses[p["pattern"]] = combination_bonuses.get(p["pattern"], 0) + 8
        
        # Combination 4: Support/Resistance Confirmation Patterns
        sr_patterns = ["hammer", "shooting_star", "tweezer_top", "tweezer_bottom"]
        sr_pattern_count = sum(1 for p in recent_patterns if p["pattern"] in sr_patterns)
        
        if sr_pattern_count >= 2:
            combination_analysis.append("Multiple support/resistance patterns - Key level identified")
            for p in recent_patterns:
                if p["pattern"] in sr_patterns:
                    combination_bonuses[p["pattern"]] = combination_bonuses.get(p["pattern"], 0) + 7
        
        # Combination 5: Pattern Agreement (All pointing same direction)
        if bullish_count >= 4 and bearish_count == 0:
            combination_analysis.append("Strong bullish consensus across all patterns")
            for p in recent_patterns:
                if p["direction"] == "bullish":
                    combination_bonuses[p["pattern"]] = combination_bonuses.get(p["pattern"], 0) + 12
        elif bearish_count >= 4 and bullish_count == 0:
            combination_analysis.append("Strong bearish consensus across all patterns")
            for p in recent_patterns:
                if p["direction"] == "bearish":
                    combination_bonuses[p["pattern"]] = combination_bonuses.get(p["pattern"], 0) + 12
        
        # Combination 6: Conflicting Signals (Reduces confidence)
        if bullish_count > 0 and bearish_count > 0 and abs(bullish_count - bearish_count) <= 1:
            combination_analysis.append("Mixed signals detected - Lower confidence until trend clarifies")
            # No bonuses for conflicting patterns
        
        # Calculate overall confidence
        confidence_factors = []
        
        # Factor 1: Pattern agreement
        total_directional = bullish_count + bearish_count
        if total_directional > 0:
            agreement = max(bullish_count, bearish_count) / total_directional
            confidence_factors.append(agreement * 40)  # Max 40 points
        
        # Factor 2: High reliability pattern presence
        if very_high_reliability:
            confidence_factors.append(25)  # 25 points for very high reliability
        elif high_reliability:
            confidence_factors.append(15)  # 15 points for high reliability
        
        # Factor 3: Combination presence
        if combination_analysis:
            confidence_factors.append(len(combination_analysis) * 5)  # 5 points per combination
        
        # Factor 4: Multi-candle patterns (more reliable than single candle)
        multi_candle_count = sum(1 for p in recent_patterns 
                                if p.get("combination_type") in ["three_candle", "five_candle"])
        if multi_candle_count >= 2:
            confidence_factors.append(15)
        
        overall_confidence = min(95, sum(confidence_factors))  # Cap at 95%
        
        # Generate summary
        if overall_confidence >= 80:
            summary = "Very strong pattern combination with high predictive value"
        elif overall_confidence >= 65:
            summary = "Good pattern combination with solid reliability"
        elif overall_confidence >= 50:
            summary = "Moderate pattern signals, use with other indicators"
        else:
            summary = "Weak or conflicting patterns, low confidence"
        
        return {
            "combination_bonuses": combination_bonuses,
            "overall_confidence": overall_confidence,
            "summary": summary,
            "combination_details": combination_analysis,
            "pattern_agreement": {
                "bullish_count": bullish_count,
                "bearish_count": bearish_count,
                "agreement_score": confidence_factors[0] if confidence_factors else 0
            }
        }
    
    def _analyze_insider_and_calculus(
        self,
        symbol: str,
        price_data: List[Any],
        candlestick_patterns: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Integrate insider trading analysis with calculus-based critical point detection.
        This combines:
        1. Insider trading influence on technical patterns
        2. First/second derivative analysis for critical/inflection points
        3. Volume shift detection
        4. Optimal entry/exit prediction
        5. Growth/loss predictions
        """
        try:
            # Convert PriceData objects to dicts for insider service
            price_dict_data = []
            for p in price_data:
                if hasattr(p, '__dict__'):
                    price_dict_data.append({
                        'date': p.date.isoformat() if hasattr(p.date, 'isoformat') else str(p.date),
                        'open': p.open,
                        'high': p.high,
                        'low': p.low,
                        'close': p.close,
                        'volume': p.volume if hasattr(p, 'volume') else 0
                    })
                else:
                    price_dict_data.append(p)
            
            # Run comprehensive insider analysis
            insider_analysis = insider_analysis_service.analyze_insider_activity(
                symbol=symbol,
                price_data=price_dict_data,
                insider_trades=None  # Will simulate if not provided
            )
            
            return {
                "insider_summary": insider_analysis.get("insider_summary", {}),
                "insider_influence": insider_analysis.get("insider_influence", {}),
                "critical_points": insider_analysis.get("critical_points", {}),
                "inflection_points": insider_analysis.get("inflection_points", {}),
                "volume_analysis": insider_analysis.get("volume_analysis", {}),
                "optimal_trade": insider_analysis.get("optimal_trade", {}),
                "predictions": insider_analysis.get("predictions", {}),
                "integration_notes": {
                    "candlestick_adjustment": insider_analysis.get("insider_influence", {}).get("adjustments", {}).get("candlestick", 0),
                    "ma_adjustment": insider_analysis.get("insider_influence", {}).get("adjustments", {}).get("moving_average", 0),
                    "fibonacci_adjustment": insider_analysis.get("insider_influence", {}).get("adjustments", {}).get("fibonacci", 0),
                    "description": "Insider trading activity influences technical indicator confidence"
                }
            }
        except Exception as e:
            logger.error(f"Error in insider/calculus analysis for {symbol}: {str(e)}")
            return {
                "error": str(e),
                "insider_summary": {},
                "insider_influence": {"score": 0, "sentiment": "neutral"},
                "critical_points": {},
                "inflection_points": {},
                "volume_analysis": {},
                "optimal_trade": {},
                "predictions": {}
            }
    
    # Additional helper methods would be implemented here...
    # (Simplified for brevity - full implementation would include all helper methods)

# Initialize technical analysis engine
technical_analysis_service = TechnicalAnalysisEngine()