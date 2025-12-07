# Portfolio Chart Analysis - Quick Start Guide

## 🚀 Quick Start

### Backend
```bash
# Start the FastAPI server
cd backend
uvicorn app.main:app --reload

# Test the endpoint
curl "http://localhost:8000/api/insights/portfolio-chart-data/AAPL?period=1y" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Frontend
```bash
# Start the Expo app
cd mobile
npm start

# Navigate to Portfolio Chart screen
# Enter symbol: AAPL
# Click "Analyze"
```

## 📊 Understanding the Confidence Score

### Score Components (Max 120 pts, normalized to 100)

| Component | Max Points | What It Measures |
|-----------|-----------|------------------|
| MA Alignment | 35 | Price position vs MAs (Price > MA50 > MA200 > MA250 = best) |
| MA Trend | 15 | How many MAs are trending up (3/3 = 15 pts) |
| Golden Cross | ±10 | MA50 crosses above/below MA200 |
| Fibonacci Position | 15 | Proximity to 0.618 golden ratio |
| Golden Ratio Strength | 15 | Significance of current Fib level |
| Volume Confirmation | 10 | Price-volume correlation strength |
| Support/Resistance | 10 | Current level strength |
| Overall Technical | 10 | Aggregate technical signals |

### Rating Scale

```
100 ████████████ Very Bullish     🌟
 80 ██████████   Bullish          📈
 65 ████████     Neutral/Positive ➡️
 50 ██████       Neutral/Negative ⚠️
 35 ████         Bearish          📉
  0 ██           Very Bearish     🔻
```

## 🎯 Key Signals to Watch

### 🌟 Very Bullish (80+)
- Golden Cross detected
- Strongly Bullish MA Alignment
- Price at Fibonacci Golden Ratio (0.618)
- All MAs trending up
- High volume confirmation

### 📈 Bullish (65-79)
- Bullish MA Alignment
- Price above all key MAs
- Strong Fibonacci support
- Positive price-volume correlation

### ➡️ Neutral (50-64)
- Mixed MA signals
- Price between key levels
- No clear trend direction

### 📉 Bearish (<50)
- Death Cross detected
- Bearish MA Alignment
- Price below key MAs
- Negative technical signals

## 📋 Example Analysis

### AAPL - Strong Bullish Setup
```
Current Price: $185.50
MA50:  $182.30 (Bullish, +0.8 slope)
MA200: $175.60 (Bullish, +0.5 slope)
MA250: $172.40 (Bullish, +0.4 slope)

MA Alignment: Strongly Bullish ✅
Golden Cross: Yes 🌟
Fibonacci: At 0.618 Golden Ratio ✨
Distance from 250-MA: +7.6%

Confidence Score: 85/100 (Very Bullish)

Key Signals:
🌟 Golden Cross Detected - Strong Bullish Signal
📈 Bullish MA Alignment
✨ Price at Fibonacci Golden Ratio
🚀 Price Extended Above 250-Day MA

Risk Factors: None detected
```

## 🔧 API Response Structure

```json
{
  "symbol": "AAPL",
  "current_price": 185.50,
  
  "moving_averages": {
    "ma_50": { "current": 182.30, "trend": "bullish" },
    "ma_200": { "current": 175.60, "trend": "bullish" },
    "ma_250": { 
      "current": 172.40,
      "distance_from_price": 7.6
    },
    "golden_cross": true,
    "ma_alignment": "strongly_bullish"
  },
  
  "fibonacci_analysis": {
    "current_fib_position": "at_golden_ratio",
    "golden_ratio_strength": 85.0,
    "fib_trend_alignment": "bullish"
  },
  
  "bullish_confidence": {
    "overall_score": 82.5,
    "rating": "Very Bullish",
    "key_signals": [...],
    "risk_factors": [...]
  }
}
```

## 🎨 UI Components

### Main Sections
1. **Period Selector** - 1M, 3M, 6M, 1Y, 2Y, 5Y
2. **Price Chart** - Visual with MA overlays
3. **Confidence Score** - Large circular display
4. **Moving Averages** - Individual MA cards
5. **Fibonacci** - Golden ratio analysis
6. **Signals** - Key bullish/bearish factors

### Colors
- Very Bullish: Green (#22c55e)
- Bullish: Lime (#84cc16)
- Neutral: Yellow (#eab308)
- Bearish: Orange/Red (#f97316/#ef4444)

## 💡 Pro Tips

### For Day Traders
- Focus on MA50 crossovers
- Watch golden cross formation
- Check volume confirmation

### For Swing Traders
- Monitor MA200 as support/resistance
- Look for Fibonacci bounces
- Track confidence score trends

### For Long-Term Investors
- MA250 is your friend
- Perfect MA Alignment = strong entry
- High confidence + Fibonacci = ideal setup

## ⚡ Quick Checks

**Bullish Entry Checklist:**
- [ ] MA Alignment: Bullish or Strongly Bullish
- [ ] Golden Cross: Recently detected
- [ ] Price: Above MA50 and MA200
- [ ] Fibonacci: At or near golden ratio support
- [ ] Volume: Positive correlation
- [ ] Confidence: Above 65

**Bearish Exit Checklist:**
- [ ] Death Cross detected
- [ ] Price below MA50
- [ ] Bearish MA Alignment
- [ ] Confidence drops below 50
- [ ] Negative volume correlation

## 🔍 Troubleshooting

**"Insufficient historical data"**
- Need at least 50 days for MA50
- Need 250 days for MA250
- Try shorter period or different symbol

**"Confidence seems low"**
- Check MA alignment
- Verify no death cross
- Review risk factors section

**"Chart not loading"**
- Verify backend is running
- Check API token is valid
- Ensure symbol exists

## 📚 Learning Resources

**Moving Averages:**
- 50-day: Short-term trend
- 200-day: Long-term trend (most watched)
- 250-day: Institutional perspective

**Fibonacci:**
- 0.618: Primary golden ratio (most important)
- 0.382: Secondary retracement
- 1.618: Extension target

**Golden Cross:**
- MA50 crosses above MA200
- Strong bullish signal
- Often marks trend reversals

---

**Need Help?** See full docs: `PORTFOLIO_CHART_ANALYSIS.md`
