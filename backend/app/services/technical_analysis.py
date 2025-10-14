from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import math
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class CandlestickPattern(Enum):
    """Candlestick pattern types"""
    BULLISH_ENGULFING = "bullish_engulfing"
    BEARISH_ENGULFING = "bearish_engulfing"
    HAMMER = "hammer"
    SHOOTING_STAR = "shooting_star"
    DOJI = "doji"
    MORNING_STAR = "morning_star"
    EVENING_STAR = "evening_star"
    PIERCING_LINE = "piercing_line"
    DARK_CLOUD_COVER = "dark_cloud_cover"

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
        
        # Candlestick patterns
        candlestick_patterns = self._detect_candlestick_patterns(price_data[-20:])  # Last 20 periods
        
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
        
        return {
            "symbol": symbol,
            "analysis_timestamp": datetime.utcnow(),
            "current_price": price_data[-1].close,
            "fibonacci_analysis": fibonacci_analysis,
            "support_resistance": support_resistance,
            "volume_analysis": volume_analysis,
            "candlestick_patterns": candlestick_patterns,
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
        """Detect candlestick patterns in recent price data"""
        
        patterns = []
        
        for i in range(2, len(price_data)):
            current = price_data[i]
            prev = price_data[i-1]
            prev2 = price_data[i-2] if i >= 2 else None
            
            # Bullish Engulfing
            if (prev.close < prev.open and  # Previous candle is bearish
                current.close > current.open and  # Current candle is bullish
                current.open < prev.close and  # Current opens below previous close
                current.close > prev.open):  # Current closes above previous open
                patterns.append({
                    "pattern": CandlestickPattern.BULLISH_ENGULFING.value,
                    "timestamp": current.timestamp,
                    "strength": 75,
                    "direction": TrendDirection.BULLISH.value,
                    "description": "Bullish engulfing pattern - potential reversal signal"
                })
            
            # Bearish Engulfing
            if (prev.close > prev.open and  # Previous candle is bullish
                current.close < current.open and  # Current candle is bearish
                current.open > prev.close and  # Current opens above previous close
                current.close < prev.open):  # Current closes below previous open
                patterns.append({
                    "pattern": CandlestickPattern.BEARISH_ENGULFING.value,
                    "timestamp": current.timestamp,
                    "strength": 75,
                    "direction": TrendDirection.BEARISH.value,
                    "description": "Bearish engulfing pattern - potential reversal signal"
                })
            
            # Hammer (bullish reversal at support)
            body_size = abs(current.close - current.open)
            total_range = current.high - current.low
            lower_shadow = min(current.open, current.close) - current.low
            upper_shadow = current.high - max(current.open, current.close)
            
            if (total_range > 0 and
                lower_shadow > 2 * body_size and
                upper_shadow < 0.5 * body_size):
                patterns.append({
                    "pattern": CandlestickPattern.HAMMER.value,
                    "timestamp": current.timestamp,
                    "strength": 60,
                    "direction": TrendDirection.BULLISH.value,
                    "description": "Hammer pattern - potential bullish reversal"
                })
            
            # Shooting Star (bearish reversal at resistance)
            if (total_range > 0 and
                upper_shadow > 2 * body_size and
                lower_shadow < 0.5 * body_size):
                patterns.append({
                    "pattern": CandlestickPattern.SHOOTING_STAR.value,
                    "timestamp": current.timestamp,
                    "strength": 60,
                    "direction": TrendDirection.BEARISH.value,
                    "description": "Shooting star pattern - potential bearish reversal"
                })
            
            # Doji (indecision)
            if body_size < 0.1 * total_range:
                patterns.append({
                    "pattern": CandlestickPattern.DOJI.value,
                    "timestamp": current.timestamp,
                    "strength": 40,
                    "direction": TrendDirection.SIDEWAYS.value,
                    "description": "Doji pattern - market indecision"
                })
        
        return patterns[-10:]  # Return last 10 patterns
    
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
    ) -> Dict[str, Any]:
        """Comprehensive trend analysis"""
        
        # Price trend analysis
        prices = [p.close for p in price_data[-50:]]
        price_slope = self._calculate_trend_slope([i for i in range(len(prices))], prices)
        
        # Moving average trends
        ma_50_slope = self._calculate_ma_slope(ma_50[-20:]) if len(ma_50) >= 20 else 0
        ma_200_slope = self._calculate_ma_slope(ma_200[-20:]) if len(ma_200) >= 20 else 0
        
        # Overall trend determination
        trend_signals = []
        if price_slope > 0.1:
            trend_signals.append(TrendDirection.BULLISH)
        elif price_slope < -0.1:
            trend_signals.append(TrendDirection.BEARISH)
        else:
            trend_signals.append(TrendDirection.SIDEWAYS)
        
        if ma_50_slope > 0:
            trend_signals.append(TrendDirection.BULLISH)
        elif ma_50_slope < 0:
            trend_signals.append(TrendDirection.BEARISH)
        else:
            trend_signals.append(TrendDirection.SIDEWAYS)
        
        # Determine primary trend
        bullish_signals = trend_signals.count(TrendDirection.BULLISH)
        bearish_signals = trend_signals.count(TrendDirection.BEARISH)
        
        if bullish_signals > bearish_signals:
            primary_trend = TrendDirection.BULLISH
        elif bearish_signals > bullish_signals:
            primary_trend = TrendDirection.BEARISH
        else:
            primary_trend = TrendDirection.SIDEWAYS
        
        # Trend strength calculation
        trend_strength = abs(price_slope) * 50  # Scale to 0-100
        trend_strength = min(trend_strength, 100)
        
        return {
            "primary_trend": primary_trend.value,
            "trend_strength": trend_strength,
            "price_slope": price_slope,
            "ma_50_slope": ma_50_slope,
            "ma_200_slope": ma_200_slope,
            "trend_consistency": self._calculate_trend_consistency(prices),
            "trend_duration": self._estimate_trend_duration(prices)
        }
    
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
    
    # Additional helper methods would be implemented here...
    # (Simplified for brevity - full implementation would include all helper methods)

# Initialize technical analysis engine
technical_analysis_engine = TechnicalAnalysisEngine()