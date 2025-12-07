# Technical Analysis Methodology

## Overview
The `technical_analysis_service.py` implements a comprehensive multi-layered technical analysis engine that combines candlestick pattern recognition, Fibonacci golden ratio analysis, and moving average calculations for period-based chart data interpretation.

## 🎯 Core Architecture

### TechnicalAnalysisEngine Class
- **Golden Ratio**: 1.618 (φ - Fibonacci constant)
- **Fibonacci Levels**: [0.236, 0.382, 0.5, 0.618 (golden ratio), 0.786]
- **Moving Averages**: 50-day, 200-day, 250-day
- **Analysis Period**: Configurable window for pattern detection

## 📊 Analysis Flow

The `analyze_security(symbol, price_data, analysis_period)` method orchestrates a comprehensive six-layer analysis:

### 1. Fibonacci Retracement Analysis

**Purpose**: Identify key support/resistance levels using golden ratio proportions

**Methodology**:
- Scans last 100 periods to find swing high and swing low
- Determines trend direction:
  - **Uptrend**: Swing high occurs after swing low → calculates retracements from high
  - **Downtrend**: Swing low occurs after swing high → calculates extensions from low
- Calculates price levels for each Fibonacci ratio:
  ```
  If uptrend:    fib_price = swing_high - (price_range × level)
  If downtrend:  fib_price = swing_low + (price_range × level)
  ```

**Golden Ratio Weighting**:
```python
golden_ratio_factor = 1 / (1 + abs(level - 0.618))
```
- Levels near 0.618 receive strongest weight
- Levels at exactly 0.618 get maximum significance
- Distance from current price factors into support/resistance strength

**Output**:
- Swing high/low prices
- Price range
- Trend direction (BULLISH/BEARISH)
- Array of Fibonacci levels with support/resistance strengths
- Golden ratio significance analysis

### 2. Moving Average Analysis

**Purpose**: Detect trend direction and momentum using MA crossovers

**Key Calculations**:
- **MA-50**: 50-period simple moving average
- **MA-200**: 200-period simple moving average
- **MA Slopes**: Rate of change over last 10-20 periods

**Signal Detection**:
- **Golden Cross**: MA-50 crosses above MA-200 → Strong BULLISH signal
- **Death Cross**: MA-50 crosses below MA-200 → Strong BEARISH signal
- **Price Position**: Above/below MA-50 and MA-200
- **MA Alignment**: Optimal bullish = Price > MA-50 > MA-200

**Crossover Detection**:
- Monitors last 5 periods for recent crossovers
- Confirms trend reversals
- Validates momentum shifts

**Output**:
- Current MA-50 and MA-200 values
- Golden/Death cross status
- Price position relative to MAs
- MA slopes (momentum indicators)
- Recent crossover events
- MA alignment assessment

### 3. Candlestick Pattern Detection

**Purpose**: Identify reversal and continuation patterns from candlestick formations

**Pattern Recognition** (over last 20 periods):

#### Multi-Candle Combinations

**Three White Soldiers** (Strength: 90, Reliability: VERY HIGH)
- Three consecutive bullish candles
- Each candle closes higher than previous
- Each candle opens within previous body
- Context: After downtrend
- Signal: Very strong bullish reversal

**Three Black Crows** (Strength: 90, Reliability: VERY HIGH)
- Three consecutive bearish candles
- Each candle closes lower than previous
- Each candle opens within previous body
- Context: After uptrend
- Signal: Very strong bearish reversal

**Morning Star** (Strength: 85, Reliability: VERY HIGH)
- Three-candle pattern:
  1. Large bearish candle
  2. Small body "star" (indecision)
  3. Large bullish candle closing above first candle's midpoint
- Context: After downtrend
- Signal: Strong bullish reversal

**Evening Star** (Strength: 85, Reliability: VERY HIGH)
- Three-candle pattern:
  1. Large bullish candle
  2. Small body "star" (indecision)
  3. Large bearish candle closing below first candle's midpoint
- Context: After uptrend
- Signal: Strong bearish reversal

**Rising Three Methods** (Strength: 75)
- Five-candle pattern:
  1. Large bullish candle
  2-4. Three small bearish candles (pullback)
  5. Large bullish candle closing above first
- Context: During uptrend
- Signal: Bullish continuation (healthy pullback)

**Falling Three Methods** (Strength: 75)
- Five-candle pattern:
  1. Large bearish candle
  2-4. Three small bullish candles (bounce)
  5. Large bearish candle closing below first
- Context: During downtrend
- Signal: Bearish continuation (failed rally)

#### Two-Candle Patterns

**Bullish/Bearish Engulfing** (Strength: 75, Reliability: HIGH)
- Second candle completely engulfs previous candle's body
- Bullish: bearish → bullish engulfing
- Bearish: bullish → bearish engulfing
- Signal: Potential reversal

**Harami Patterns** (Strength: 70, Reliability: HIGH)
- Small candle contained within previous candle's body
- Bullish Harami: after downtrend, signals potential upward reversal
- Bearish Harami: after uptrend, signals potential downward reversal

**Tweezer Top/Bottom** (Strength: 75)
- Two candles with nearly identical highs (top) or lows (bottom)
- Tweezer Top: at resistance, bearish reversal
- Tweezer Bottom: at support, bullish reversal
- Detection threshold: ±0.2% of price

#### Single-Candle Patterns

**Hammer** (Strength: 65, Reliability: MEDIUM)
- Long lower shadow (>2× body length)
- Small upper shadow (<0.5× body length)
- Context: At support level
- Signal: Potential bullish reversal (buying pressure)

**Shooting Star** (Strength: 65, Reliability: MEDIUM)
- Long upper shadow (>2× body length)
- Small lower shadow (<0.5× body length)
- Context: At resistance level
- Signal: Potential bearish reversal (selling pressure)

**Doji** (Strength: 50, Reliability: LOW)
- Body < 10% of total range
- Open ≈ Close
- Signal: Indecision, potential reversal (requires confirmation)

**Pattern Output**:
- Pattern name and type
- Timestamp of detection
- Strength score (50-90)
- Reliability level (LOW/MEDIUM/HIGH/VERY HIGH)
- Direction (BULLISH/BEARISH/SIDEWAYS)
- Combination type (single/two/three/five-candle)
- Context required (e.g., "after_downtrend", "at_support")
- Description

### 4. Support/Resistance Level Identification

**Purpose**: Find key price levels where reversals are likely

**Detection Algorithm**:
- Scans 20-period windows across price history
- **Resistance**: Local high where all surrounding highs are lower
- **Support**: Local low where all surrounding lows are higher

**Level Strength Calculation**:
- Counts "touches" (price approaches within 1% tolerance)
- More touches = stronger level
- Recent touches weighted more heavily

**Consolidation**:
- Removes duplicate levels (within 1% of each other)
- Keeps strongest version of overlapping levels
- Ranks by strength score

**Output**:
- Top 10 support levels (sorted by strength)
- Top 10 resistance levels (sorted by strength)
- Nearest support/resistance to current price
- Distance from current price (percentage)
- Strength scores for nearest levels
- Last touch timestamp

### 5. Volume Pattern Analysis

**Purpose**: Confirm price movements with volume analysis

**Metrics Calculated**:

**Average Volume**: 50-period moving average of volume

**Volume Trend**:
- Calculates volume slope over time
- BULLISH: Volume increasing (slope > 0.1)
- BEARISH: Volume decreasing (slope < -0.1)
- SIDEWAYS: Volume stable (-0.1 ≤ slope ≤ 0.1)

**Volume Spike Ratio**:
```
spike_ratio = recent_avg_volume (10 periods) / historical_avg_volume (50 periods)
```
- Ratio > 1.5: Significant spike (strong conviction)
- Ratio > 2.0: Explosive volume (extreme interest)

**Price-Volume Correlation**:
- Calculates correlation coefficient between price and volume
- Positive correlation: Volume confirms uptrend
- Negative correlation: Divergence (warning sign)
- Near zero: No relationship (weak signal)

**Accumulation/Distribution**:
- Tracks whether volume flows into buying (accumulation) or selling (distribution)
- Uses price position within range and volume
- Positive values: Accumulation (bullish)
- Negative values: Distribution (bearish)

**Output**:
- Average volume
- Volume trend direction
- Volume spike ratio
- Price-volume correlation
- Accumulation/distribution score

### 6. Weighted Signal Generation

**Purpose**: Combine all analysis layers into actionable recommendation

**Signal Weighting Formula**:
```
total_signal = (
  fibonacci_signal × 0.25 +
  candlestick_signal × 0.25 +
  ma_signal × 0.20 +
  support_resistance_signal × 0.15 +
  volume_signal × 0.15
)
```

**Component Signals**:

1. **Fibonacci Signal**:
   - Price near golden ratio level (0.618) → High weight
   - At support (below current price) → Bullish
   - At resistance (above current price) → Bearish

2. **Candlestick Signal**:
   - Pattern strength × reliability score
   - Very high reliability patterns dominate
   - Direction (BULLISH/BEARISH) determines sign

3. **MA Signal**:
   - Golden Cross → Strong bullish (+100)
   - Death Cross → Strong bearish (-100)
   - Price above both MAs → Bullish (+50)
   - Price below both MAs → Bearish (-50)

4. **Support/Resistance Signal**:
   - Near strong support → Bullish
   - Near strong resistance → Bearish
   - Distance and strength affect magnitude

5. **Volume Signal**:
   - Volume confirms price movement → Amplify signal
   - Volume diverges → Reduce signal confidence
   - Accumulation → Bullish
   - Distribution → Bearish

**Investment Recommendations**:
- **STRONG_BUY**: Total signal > 75 (overwhelming bullish)
- **BUY**: 50 < Total signal ≤ 75 (solid bullish)
- **HOLD**: -50 ≤ Total signal ≤ 50 (neutral/mixed)
- **SELL**: -75 < Total signal ≤ -50 (solid bearish)
- **STRONG_SELL**: Total signal ≤ -75 (overwhelming bearish)

**Price Targets**:
- **Buy Point**: Nearest strong support level
- **Target Price**: Next resistance level or Fibonacci extension
- **Stop Loss**: Below support with buffer (typically 2-3%)

## 🔢 Period-Based Reading

The analysis processes chart data **period by period** (e.g., daily candles):

1. **Incremental MA Calculation**:
   - MA-50: Averages last 50 closing prices
   - MA-200: Averages last 200 closing prices
   - Updates with each new period

2. **Pattern Evolution Tracking**:
   - Monitors pattern frequency over time
   - Detects changes in pattern reliability
   - Identifies trend shifts

3. **Temporal Pattern Analysis**:
   - **Trend Following**: Do patterns lead to expected moves?
   - **Frequency Changes**: Are patterns becoming more/less common?
   - **Pattern Evolution**: Are patterns strengthening or weakening?

4. **Adaptive Scoring**:
   - Patterns that work well recently get higher scores
   - Failed patterns get reduced weights
   - Self-learning from historical accuracy

## 📈 Golden Ratio Integration

The golden ratio (φ = 1.618, or 0.618 = φ - 1) is central to the analysis:

### Why 0.618 Matters

1. **Natural Market Proportions**:
   - Markets often retrace ~61.8% of previous move
   - Fibonacci sequence appears in price waves
   - Golden ratio = mathematical harmony

2. **Support/Resistance Strength**:
   - 0.618 retracement is **strongest** turning point
   - More reliable than other Fibonacci levels
   - Price tends to react most at this level

3. **Weighting in Analysis**:
```python
golden_ratio_factor = 1 / (1 + abs(level - 0.618))
```
- Level 0.618: factor = 1.0 (maximum weight)
- Level 0.5: factor = 0.894 (slightly reduced)
- Level 0.236: factor = 0.724 (noticeably reduced)
- Level 0.786: factor = 0.856 (reduced)

4. **Entry/Exit Optimization**:
   - **Buy**: Near 0.618 retracement in uptrend
   - **Sell**: At 1.618 extension (profit target)
   - **Stop**: Below 0.786 retracement

### Practical Application

**Example Uptrend Analysis**:
```
Swing Low: $100
Swing High: $150
Range: $50

Fibonacci Levels:
- 0.236: $150 - ($50 × 0.236) = $138.20 (weak support)
- 0.382: $150 - ($50 × 0.382) = $130.90 (moderate support)
- 0.500: $150 - ($50 × 0.500) = $125.00 (psychological support)
- 0.618: $150 - ($50 × 0.618) = $119.10 (GOLDEN RATIO - strong support)
- 0.786: $150 - ($50 × 0.786) = $110.70 (last support before trend failure)

If current price = $120:
- Very close to golden ratio level ($119.10)
- Golden ratio factor maximized
- High probability bounce zone
- Ideal buy point with stop at $118
```

## 🎯 Investment Workflow

1. **Input**: Price data (OHLCV) for analysis period
2. **Process**: Six-layer analysis (Fibonacci, MA, candlesticks, S/R, volume, signals)
3. **Output**:
   - Comprehensive analysis dictionary
   - Price targets (buy/sell/stop)
   - Weighted signals
   - Investment recommendation
   - Confidence score
   - Risk assessment

## 📊 Example Output Structure

```python
{
  "fibonacci_analysis": {
    "swing_high": 150.0,
    "swing_low": 100.0,
    "trend_direction": "BULLISH",
    "fibonacci_levels": [...],
    "golden_ratio_analysis": {...}
  },
  "moving_average_analysis": {
    "ma_50_current": 125.0,
    "ma_200_current": 115.0,
    "golden_cross": True,
    "ma_alignment": "BULLISH"
  },
  "candlestick_patterns": [
    {
      "pattern": "MORNING_STAR",
      "strength": 85,
      "reliability": "VERY_HIGH",
      "direction": "BULLISH"
    }
  ],
  "support_resistance": {
    "nearest_support": 119.10,
    "nearest_resistance": 138.20,
    "support_strength": 85,
    "resistance_strength": 70
  },
  "volume_analysis": {
    "volume_spike_ratio": 1.8,
    "price_volume_correlation": 0.85,
    "accumulation_distribution": "ACCUMULATION"
  },
  "weighted_signals": {
    "total_signal": 82,
    "fibonacci_signal": 20,
    "candlestick_signal": 21,
    "ma_signal": 20,
    "support_resistance_signal": 12,
    "volume_signal": 9
  },
  "investment_recommendation": "STRONG_BUY",
  "price_targets": {
    "buy_point": 119.10,
    "target_price": 138.20,
    "stop_loss": 116.00
  }
}
```

## 🔍 Key Advantages

1. **Multi-Layer Confirmation**: Requires agreement across multiple indicators
2. **Golden Ratio Precision**: Leverages natural market proportions
3. **Period-Based Adaptability**: Learns from recent pattern performance
4. **Volume Validation**: Confirms moves with conviction analysis
5. **Risk Management**: Provides specific entry/exit/stop levels
6. **Comprehensive Output**: All raw data available for further analysis

## ⚠️ Limitations

- **Historical Data Required**: Needs sufficient history (200+ periods for MA-200)
- **Lagging Indicators**: MAs react to price, don't predict
- **Pattern Subjectivity**: Candlestick patterns need context
- **No Fundamental Analysis**: Purely technical (ignores earnings, news, etc.)
- **Market Conditions**: Works best in trending markets, less effective in choppy/sideways markets

## 🚀 Usage Example

```python
from technical_analysis_service import TechnicalAnalysisEngine, PriceData

# Initialize engine
engine = TechnicalAnalysisEngine()

# Prepare price data
price_data = [
    PriceData(timestamp="2024-01-01", open=100, high=105, low=98, close=103, volume=1000000),
    # ... more data points
]

# Analyze security
results = engine.analyze_security(
    symbol="AAPL",
    price_data=price_data,
    analysis_period="daily"
)

# Access results
print(f"Recommendation: {results['investment_recommendation']}")
print(f"Buy Point: ${results['price_targets']['buy_point']:.2f}")
print(f"Target: ${results['price_targets']['target_price']:.2f}")
```

---

**Disclaimer**: This analysis methodology is for educational purposes. Not financial advice. All investment decisions carry risk and should be made with proper due diligence and professional consultation.
