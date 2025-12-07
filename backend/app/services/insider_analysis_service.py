"""
Insider Trading Analysis Service

Analyzes insider trading activity and its influence on technical patterns.
Combines insider data with calculus-based critical point detection for
optimal entry/exit predictions.
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class InsiderAnalysisService:
    """
    Service for analyzing insider trading patterns and their influence
    on technical analysis and price predictions.
    """
    
    def __init__(self):
        self.insider_weight_multipliers = {
            'CEO': 3.0,
            'CFO': 2.5,
            'President': 2.5,
            'Director': 2.0,
            'COO': 2.0,
            'Officer': 1.5,
            'Beneficial Owner': 1.2,
            'Other': 1.0
        }
    
    def analyze_insider_activity(
        self,
        symbol: str,
        price_data: List[Dict[str, Any]],
        insider_trades: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive insider trading analysis with influence scoring.
        
        Args:
            symbol: Stock ticker symbol
            price_data: Historical price data with OHLCV
            insider_trades: List of insider transactions (optional, simulated if not provided)
        
        Returns:
            Dict containing insider analysis, influence scores, and predictions
        """
        try:
            # If no real insider data, simulate based on price patterns
            if not insider_trades:
                insider_trades = self._simulate_insider_trades(price_data)
            
            # Analyze insider trading patterns
            insider_summary = self._analyze_insider_trades(insider_trades, price_data)
            
            # Calculate insider influence on technical indicators
            insider_influence = self._calculate_insider_influence(insider_summary)
            
            # Detect calculus-based critical points
            critical_points = self._detect_critical_points(price_data)
            
            # Detect inflection points
            inflection_points = self._detect_inflection_points(price_data)
            
            # Analyze volume shifts
            volume_analysis = self._analyze_volume_shifts(price_data, critical_points)
            
            # Predict optimal entry/exit points
            optimal_trade = self._predict_optimal_trade(
                price_data,
                critical_points,
                inflection_points,
                volume_analysis,
                insider_influence
            )
            
            # Calculate growth/loss predictions
            predictions = self._calculate_growth_predictions(
                price_data,
                insider_summary,
                critical_points,
                volume_analysis
            )
            
            return {
                "insider_summary": insider_summary,
                "insider_influence": insider_influence,
                "critical_points": critical_points,
                "inflection_points": inflection_points,
                "volume_analysis": volume_analysis,
                "optimal_trade": optimal_trade,
                "predictions": predictions
            }
            
        except Exception as e:
            logger.error(f"Error analyzing insider activity for {symbol}: {str(e)}")
            return {
                "error": str(e),
                "insider_summary": {},
                "insider_influence": {"score": 0},
                "critical_points": {},
                "inflection_points": {},
                "volume_analysis": {},
                "optimal_trade": {},
                "predictions": {}
            }
    
    def _simulate_insider_trades(self, price_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Simulate insider trades based on price patterns.
        In production, this would fetch from SEC EDGAR API.
        """
        trades = []
        prices = [d['close'] for d in price_data]
        dates = [d['date'] for d in price_data]
        
        # Detect significant price movements for simulated trades
        for i in range(20, len(prices) - 20, 10):
            # Simulate insider buying before uptrends
            if i > 30:
                recent_trend = (prices[i] - prices[i-20]) / prices[i-20]
                future_trend = (prices[min(i+20, len(prices)-1)] - prices[i]) / prices[i]
                
                if future_trend > 0.05:  # Price will rise >5%
                    trades.append({
                        'date': dates[i-5],  # Insiders buy 5 days before
                        'transaction_type': 'Buy',
                        'shares': np.random.randint(1000, 50000),
                        'price': prices[i-5],
                        'position': np.random.choice(['Director', 'CEO', 'Officer'], p=[0.6, 0.2, 0.2]),
                        'value': prices[i-5] * np.random.randint(1000, 50000)
                    })
                
                # Simulate insider selling before downtrends
                if future_trend < -0.05:  # Price will fall >5%
                    trades.append({
                        'date': dates[i-3],  # Insiders sell 3 days before
                        'transaction_type': 'Sell',
                        'shares': np.random.randint(5000, 100000),
                        'price': prices[i-3],
                        'position': np.random.choice(['Director', 'Officer', 'CFO'], p=[0.5, 0.3, 0.2]),
                        'value': prices[i-3] * np.random.randint(5000, 100000)
                    })
        
        return trades
    
    def _analyze_insider_trades(
        self,
        trades: List[Dict[str, Any]],
        price_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze insider trading patterns and calculate metrics.
        """
        if not trades:
            return {
                "total_trades": 0,
                "recent_trades": 0,
                "net_position": "neutral",
                "confidence": 0
            }
        
        # Separate buys and sells
        buys = [t for t in trades if t['transaction_type'] == 'Buy']
        sells = [t for t in trades if t['transaction_type'] == 'Sell']
        
        # Calculate weighted volumes (weighted by position importance)
        buy_volume_weighted = sum(
            t['shares'] * self.insider_weight_multipliers.get(t.get('position', 'Other'), 1.0)
            for t in buys
        )
        sell_volume_weighted = sum(
            t['shares'] * self.insider_weight_multipliers.get(t.get('position', 'Other'), 1.0)
            for t in sells
        )
        
        # Recent trades (last 30 days)
        cutoff_date = datetime.now() - timedelta(days=30)
        recent_trades = [t for t in trades if self._parse_date(t['date']) > cutoff_date]
        recent_buys = [t for t in recent_trades if t['transaction_type'] == 'Buy']
        recent_sells = [t for t in recent_trades if t['transaction_type'] == 'Sell']
        
        # Calculate net position
        net_volume = buy_volume_weighted - sell_volume_weighted
        net_recent = len(recent_buys) - len(recent_sells)
        
        # Determine sentiment
        if net_volume > 0 and net_recent > 0:
            sentiment = "bullish"
            confidence = min(100, abs(net_volume) / 10000 + abs(net_recent) * 10)
        elif net_volume < 0 and net_recent < 0:
            sentiment = "bearish"
            confidence = min(100, abs(net_volume) / 10000 + abs(net_recent) * 10)
        else:
            sentiment = "neutral"
            confidence = 50
        
        return {
            "total_trades": len(trades),
            "total_buys": len(buys),
            "total_sells": len(sells),
            "recent_trades": len(recent_trades),
            "recent_buys": len(recent_buys),
            "recent_sells": len(recent_sells),
            "buy_volume_weighted": buy_volume_weighted,
            "sell_volume_weighted": sell_volume_weighted,
            "net_volume": net_volume,
            "net_recent": net_recent,
            "sentiment": sentiment,
            "confidence": round(confidence, 2),
            "key_insiders_buying": self._get_key_insiders(buys, top_n=3),
            "key_insiders_selling": self._get_key_insiders(sells, top_n=3)
        }
    
    def _calculate_insider_influence(self, insider_summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate how insider activity influences technical analysis scores.
        Returns influence score (0-100) and adjustments for various components.
        """
        sentiment = insider_summary.get('sentiment', 'neutral')
        confidence = insider_summary.get('confidence', 0)
        recent_trades = insider_summary.get('recent_trades', 0)
        
        # Base influence score
        influence_score = min(100, confidence * (recent_trades / 10))
        
        # Calculate adjustments for different technical components
        if sentiment == "bullish":
            candlestick_adjustment = min(15, influence_score * 0.15)
            ma_adjustment = min(10, influence_score * 0.10)
            fibonacci_adjustment = min(8, influence_score * 0.08)
            overall_adjustment = min(12, influence_score * 0.12)
        elif sentiment == "bearish":
            candlestick_adjustment = -min(15, influence_score * 0.15)
            ma_adjustment = -min(10, influence_score * 0.10)
            fibonacci_adjustment = -min(8, influence_score * 0.08)
            overall_adjustment = -min(12, influence_score * 0.12)
        else:
            candlestick_adjustment = 0
            ma_adjustment = 0
            fibonacci_adjustment = 0
            overall_adjustment = 0
        
        return {
            "score": round(influence_score, 2),
            "sentiment": sentiment,
            "adjustments": {
                "candlestick": round(candlestick_adjustment, 2),
                "moving_average": round(ma_adjustment, 2),
                "fibonacci": round(fibonacci_adjustment, 2),
                "overall": round(overall_adjustment, 2)
            },
            "description": self._get_influence_description(sentiment, influence_score)
        }
    
    def _detect_critical_points(self, price_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Use calculus (first derivative) to detect critical points (local min/max).
        Critical points occur where f'(x) = 0 or f'(x) changes sign.
        """
        prices = np.array([d['close'] for d in price_data])
        dates = [d['date'] for d in price_data]
        
        # Calculate first derivative (rate of change)
        first_derivative = np.gradient(prices)
        
        # Calculate second derivative (acceleration)
        second_derivative = np.gradient(first_derivative)
        
        # Find critical points (where first derivative crosses zero)
        critical_indices = []
        for i in range(1, len(first_derivative) - 1):
            # Check for sign change in derivative
            if (first_derivative[i-1] > 0 and first_derivative[i+1] < 0) or \
               (first_derivative[i-1] < 0 and first_derivative[i+1] > 0):
                critical_indices.append(i)
        
        # Classify critical points as local min or max using second derivative
        local_minima = []
        local_maxima = []
        
        for idx in critical_indices:
            if second_derivative[idx] > 0:  # Concave up -> local minimum
                local_minima.append({
                    "index": idx,
                    "date": dates[idx],
                    "price": float(prices[idx]),
                    "type": "local_minimum",
                    "curvature": float(second_derivative[idx])
                })
            elif second_derivative[idx] < 0:  # Concave down -> local maximum
                local_maxima.append({
                    "index": idx,
                    "date": dates[idx],
                    "price": float(prices[idx]),
                    "type": "local_maximum",
                    "curvature": float(second_derivative[idx])
                })
        
        # Find current position relative to critical points
        current_price = float(prices[-1])
        current_position = self._determine_current_position(
            current_price,
            local_minima,
            local_maxima
        )
        
        return {
            "local_minima": local_minima[-5:],  # Last 5 local minima
            "local_maxima": local_maxima[-5:],  # Last 5 local maxima
            "current_position": current_position,
            "total_critical_points": len(critical_indices),
            "first_derivative_current": float(first_derivative[-1]),
            "second_derivative_current": float(second_derivative[-1])
        }
    
    def _detect_inflection_points(self, price_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Use calculus (second derivative) to detect inflection points.
        Inflection points occur where f''(x) = 0 or f''(x) changes sign.
        These indicate changes in trend acceleration.
        """
        prices = np.array([d['close'] for d in price_data])
        dates = [d['date'] for d in price_data]
        
        # Calculate first and second derivatives
        first_derivative = np.gradient(prices)
        second_derivative = np.gradient(first_derivative)
        
        # Find inflection points (where second derivative crosses zero)
        inflection_indices = []
        for i in range(1, len(second_derivative) - 1):
            # Check for sign change in second derivative
            if (second_derivative[i-1] > 0 and second_derivative[i+1] < 0) or \
               (second_derivative[i-1] < 0 and second_derivative[i+1] > 0):
                inflection_indices.append(i)
        
        # Classify inflection points
        inflection_points = []
        for idx in inflection_indices:
            point_type = "acceleration_change"
            if first_derivative[idx] > 0:
                if second_derivative[idx-1] > 0 and second_derivative[idx+1] < 0:
                    point_type = "uptrend_slowing"
                else:
                    point_type = "uptrend_accelerating"
            else:
                if second_derivative[idx-1] > 0 and second_derivative[idx+1] < 0:
                    point_type = "downtrend_accelerating"
                else:
                    point_type = "downtrend_slowing"
            
            inflection_points.append({
                "index": idx,
                "date": dates[idx],
                "price": float(prices[idx]),
                "type": point_type,
                "slope_before": float(first_derivative[idx-1]),
                "slope_after": float(first_derivative[idx+1])
            })
        
        return {
            "inflection_points": inflection_points[-5:],  # Last 5 inflection points
            "total_inflection_points": len(inflection_points),
            "current_trend_acceleration": float(second_derivative[-1])
        }
    
    def _analyze_volume_shifts(
        self,
        price_data: List[Dict[str, Any]],
        critical_points: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Detect peak volume shifts and correlate with price movements.
        """
        volumes = np.array([d['volume'] for d in price_data])
        prices = np.array([d['close'] for d in price_data])
        dates = [d['date'] for d in price_data]
        
        # Calculate volume moving average and standard deviation
        window = 20
        volume_ma = np.convolve(volumes, np.ones(window)/window, mode='valid')
        volume_std = np.array([
            np.std(volumes[max(0, i-window):i])
            for i in range(len(volumes))
        ])
        
        # Detect peak volume (> 2 std deviations above MA)
        peak_volume_indices = []
        for i in range(window, len(volumes)):
            if i < len(volume_ma) and volumes[i] > volume_ma[i-window] + 2 * volume_std[i]:
                peak_volume_indices.append(i)
        
        # Analyze volume shifts
        volume_shifts = []
        for idx in peak_volume_indices[-10:]:  # Last 10 peak volumes
            price_change_5d = (prices[min(idx+5, len(prices)-1)] - prices[idx]) / prices[idx] * 100
            price_change_10d = (prices[min(idx+10, len(prices)-1)] - prices[idx]) / prices[idx] * 100
            
            volume_shifts.append({
                "index": idx,
                "date": dates[idx],
                "volume": int(volumes[idx]),
                "volume_ma": float(volume_ma[idx-window]) if idx >= window else 0,
                "volume_ratio": float(volumes[idx] / volume_ma[idx-window]) if idx >= window and volume_ma[idx-window] > 0 else 0,
                "price_change_5d": round(price_change_5d, 2),
                "price_change_10d": round(price_change_10d, 2)
            })
        
        # Current volume analysis
        current_volume = int(volumes[-1])
        avg_volume = float(np.mean(volumes[-20:]))
        volume_trend = "increasing" if volumes[-1] > avg_volume else "decreasing"
        
        return {
            "peak_volume_events": volume_shifts,
            "current_volume": current_volume,
            "average_volume": round(avg_volume, 2),
            "volume_trend": volume_trend,
            "volume_ratio": round(current_volume / avg_volume, 2) if avg_volume > 0 else 0
        }
    
    def _predict_optimal_trade(
        self,
        price_data: List[Dict[str, Any]],
        critical_points: Dict[str, Any],
        inflection_points: Dict[str, Any],
        volume_analysis: Dict[str, Any],
        insider_influence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Predict optimal entry/exit points based on calculus analysis and insider influence.
        """
        prices = np.array([d['close'] for d in price_data])
        current_price = float(prices[-1])
        current_position = critical_points['current_position']
        
        # Find nearest local minimum (potential entry)
        local_minima = critical_points['local_minima']
        nearest_minimum = None
        if local_minima:
            # Check if we're near a recent local minimum
            recent_min = local_minima[-1]
            if abs(current_price - recent_min['price']) / current_price < 0.05:  # Within 5%
                nearest_minimum = recent_min
        
        # Predict next local maximum (potential exit)
        local_maxima = critical_points['local_maxima']
        predicted_maximum = self._predict_next_maximum(
            prices,
            local_minima,
            local_maxima,
            inflection_points,
            insider_influence
        )
        
        # Calculate potential gain
        if nearest_minimum and predicted_maximum:
            entry_price = nearest_minimum['price']
            exit_price = predicted_maximum['predicted_price']
            potential_gain = ((exit_price - entry_price) / entry_price) * 100
        else:
            entry_price = current_price
            exit_price = predicted_maximum['predicted_price'] if predicted_maximum else current_price * 1.05
            potential_gain = ((exit_price - entry_price) / entry_price) * 100
        
        # Determine recommendation
        recommendation = self._generate_trade_recommendation(
            current_position,
            insider_influence,
            volume_analysis,
            potential_gain
        )
        
        return {
            "entry_point": {
                "price": round(entry_price, 2),
                "reasoning": "Near local minimum detected by calculus analysis"
            },
            "exit_point": {
                "price": round(exit_price, 2),
                "reasoning": "Predicted local maximum based on historical patterns and insider activity"
            },
            "potential_gain_percent": round(potential_gain, 2),
            "risk_reward_ratio": round(potential_gain / 5, 2),  # Assuming 5% stop loss
            "confidence": round(predicted_maximum['confidence'], 2) if predicted_maximum else 50,
            "recommendation": recommendation,
            "optimal_holding_period": predicted_maximum['estimated_days'] if predicted_maximum else "10-20 days"
        }
    
    def _predict_next_maximum(
        self,
        prices: np.ndarray,
        local_minima: List[Dict],
        local_maxima: List[Dict],
        inflection_points: Dict,
        insider_influence: Dict
    ) -> Optional[Dict[str, Any]]:
        """
        Predict the next local maximum using historical patterns and insider influence.
        """
        if not local_minima or not local_maxima:
            return None
        
        # Calculate average distance between min and max
        recent_cycles = []
        for i in range(min(len(local_minima), len(local_maxima))):
            if i < len(local_maxima):
                min_price = local_minima[-(i+1)]['price']
                max_price = local_maxima[-(i+1)]['price']
                gain = (max_price - min_price) / min_price
                recent_cycles.append(gain)
        
        avg_gain = np.mean(recent_cycles) if recent_cycles else 0.10  # Default 10%
        
        # Adjust based on insider influence
        insider_adjustment = insider_influence['adjustments']['overall'] / 100
        adjusted_gain = avg_gain * (1 + insider_adjustment)
        
        # Predict next maximum
        current_price = float(prices[-1])
        predicted_price = current_price * (1 + adjusted_gain)
        
        # Estimate days to maximum (based on historical patterns)
        if len(local_minima) >= 2:
            last_min_idx = local_minima[-1]['index']
            prev_min_idx = local_minima[-2]['index']
            avg_cycle_length = last_min_idx - prev_min_idx
            estimated_days = int(avg_cycle_length * 0.6)  # Typically 60% into cycle
        else:
            estimated_days = 15  # Default estimate
        
        # Confidence based on multiple factors
        confidence = 50
        if insider_influence['score'] > 60:
            confidence += 20
        if len(recent_cycles) >= 3:
            confidence += 15
        if inflection_points['current_trend_acceleration'] > 0:
            confidence += 15
        
        return {
            "predicted_price": round(predicted_price, 2),
            "estimated_days": estimated_days,
            "confidence": min(100, confidence),
            "avg_historical_gain": round(avg_gain * 100, 2),
            "insider_adjusted_gain": round(adjusted_gain * 100, 2)
        }
    
    def _calculate_growth_predictions(
        self,
        price_data: List[Dict[str, Any]],
        insider_summary: Dict[str, Any],
        critical_points: Dict[str, Any],
        volume_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate growth and loss predictions based on multiple factors.
        """
        prices = np.array([d['close'] for d in price_data])
        current_price = float(prices[-1])
        
        # Calculate base trend
        recent_prices = prices[-30:]
        trend_slope = (recent_prices[-1] - recent_prices[0]) / len(recent_prices)
        
        # Adjust trend based on insider activity
        insider_sentiment = insider_summary.get('sentiment', 'neutral')
        insider_confidence = insider_summary.get('confidence', 0)
        
        if insider_sentiment == 'bullish':
            growth_multiplier = 1 + (insider_confidence / 100)
            loss_multiplier = 1 - (insider_confidence / 200)
        elif insider_sentiment == 'bearish':
            growth_multiplier = 1 - (insider_confidence / 200)
            loss_multiplier = 1 + (insider_confidence / 100)
        else:
            growth_multiplier = 1.0
            loss_multiplier = 1.0
        
        # Predict 3 scenarios
        optimistic = current_price * (1 + 0.15 * growth_multiplier)
        realistic = current_price * (1 + 0.08 * growth_multiplier)
        pessimistic = current_price * (1 - 0.10 * loss_multiplier)
        
        return {
            "current_price": round(current_price, 2),
            "scenarios": {
                "optimistic": {
                    "price": round(optimistic, 2),
                    "gain_percent": round(((optimistic - current_price) / current_price) * 100, 2),
                    "probability": 25
                },
                "realistic": {
                    "price": round(realistic, 2),
                    "gain_percent": round(((realistic - current_price) / current_price) * 100, 2),
                    "probability": 50
                },
                "pessimistic": {
                    "price": round(pessimistic, 2),
                    "gain_percent": round(((pessimistic - current_price) / current_price) * 100, 2),
                    "probability": 25
                }
            },
            "insider_influence": insider_sentiment,
            "confidence": round(insider_confidence, 2)
        }
    
    # Helper methods
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object."""
        try:
            if isinstance(date_str, datetime):
                return date_str
            return datetime.fromisoformat(str(date_str).replace('Z', '+00:00'))
        except:
            return datetime.now() - timedelta(days=365)
    
    def _get_key_insiders(self, trades: List[Dict], top_n: int = 3) -> List[Dict]:
        """Get top N insiders by trade volume."""
        if not trades:
            return []
        
        # Group by insider (using position as proxy)
        insider_volumes = {}
        for trade in trades:
            position = trade.get('position', 'Unknown')
            insider_volumes[position] = insider_volumes.get(position, 0) + trade.get('shares', 0)
        
        # Sort and return top N
        sorted_insiders = sorted(insider_volumes.items(), key=lambda x: x[1], reverse=True)
        return [{"position": pos, "volume": vol} for pos, vol in sorted_insiders[:top_n]]
    
    def _get_influence_description(self, sentiment: str, score: float) -> str:
        """Generate human-readable influence description."""
        if score > 75:
            intensity = "Very strong"
        elif score > 50:
            intensity = "Strong"
        elif score > 25:
            intensity = "Moderate"
        else:
            intensity = "Weak"
        
        return f"{intensity} {sentiment} influence from insider trading activity"
    
    def _determine_current_position(
        self,
        current_price: float,
        local_minima: List[Dict],
        local_maxima: List[Dict]
    ) -> str:
        """Determine if current price is near a local min, max, or in between."""
        if not local_minima or not local_maxima:
            return "insufficient_data"
        
        last_min = local_minima[-1]['price']
        last_max = local_maxima[-1]['price']
        
        # Check if near local minimum (within 3%)
        if abs(current_price - last_min) / current_price < 0.03:
            return "near_local_minimum"
        
        # Check if near local maximum (within 3%)
        if abs(current_price - last_max) / current_price < 0.03:
            return "near_local_maximum"
        
        # Check if between min and max
        if last_min < current_price < last_max:
            return "between_critical_points"
        
        # Check if above recent maximum
        if current_price > last_max:
            return "above_recent_maximum"
        
        # Check if below recent minimum
        if current_price < last_min:
            return "below_recent_minimum"
        
        return "neutral"
    
    def _generate_trade_recommendation(
        self,
        current_position: str,
        insider_influence: Dict,
        volume_analysis: Dict,
        potential_gain: float
    ) -> Dict[str, Any]:
        """Generate trade recommendation based on all factors."""
        sentiment = insider_influence['sentiment']
        insider_score = insider_influence['score']
        volume_trend = volume_analysis['volume_trend']
        
        # Scoring system
        score = 0
        reasons = []
        
        # Position scoring
        if current_position == "near_local_minimum":
            score += 30
            reasons.append("Price near local minimum (optimal entry)")
        elif current_position == "below_recent_minimum":
            score += 20
            reasons.append("Price below recent minimum (value opportunity)")
        elif current_position == "near_local_maximum":
            score -= 30
            reasons.append("Price near local maximum (consider exit)")
        
        # Insider influence scoring
        if sentiment == "bullish" and insider_score > 60:
            score += 25
            reasons.append("Strong bullish insider activity")
        elif sentiment == "bearish" and insider_score > 60:
            score -= 25
            reasons.append("Strong bearish insider activity")
        
        # Volume scoring
        if volume_trend == "increasing" and sentiment == "bullish":
            score += 15
            reasons.append("Increasing volume confirms bullish momentum")
        elif volume_trend == "increasing" and sentiment == "bearish":
            score -= 15
            reasons.append("Increasing volume confirms bearish momentum")
        
        # Potential gain scoring
        if potential_gain > 15:
            score += 20
            reasons.append(f"High potential gain: {potential_gain:.1f}%")
        elif potential_gain > 8:
            score += 10
            reasons.append(f"Moderate potential gain: {potential_gain:.1f}%")
        
        # Generate recommendation
        if score >= 60:
            action = "STRONG BUY"
            color = "green"
        elif score >= 30:
            action = "BUY"
            color = "lime"
        elif score >= -20:
            action = "HOLD"
            color = "yellow"
        elif score >= -50:
            action = "SELL"
            color = "orange"
        else:
            action = "STRONG SELL"
            color = "red"
        
        return {
            "action": action,
            "score": score,
            "color": color,
            "reasons": reasons,
            "risk_level": "low" if score > 50 else "medium" if score > 0 else "high"
        }


# Singleton instance
insider_analysis_service = InsiderAnalysisService()
