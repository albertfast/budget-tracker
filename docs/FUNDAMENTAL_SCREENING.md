# Fundamental Company Screening Feature 📊

## Overview
The fundamental screening system analyzes companies from uploaded financial documents to identify high-quality investment candidates based on predictability, transparency, and growth metrics.

---

## 🎯 What It Does

This feature screens companies by analyzing:
1. **Predictability**: How consistent are revenue patterns quarter-over-quarter and year-over-year?
2. **Report Depth**: Is the company increasing disclosure depth in 10-K reports (transparency)?
3. **Quality Score**: Overall fundamental health combining 4 components
4. **Recommendations**: Investment actions from STRONG BUY to AVOID

---

## 📁 Supported File Types

### Auto-Detected Document Types
The system automatically detects file type by analyzing column names:

| Document Type | Keywords | Example Columns |
|--------------|----------|-----------------|
| **Balance Sheet** | assets, liabilities, equity, net_worth | Total Assets, Current Liabilities, Shareholder Equity |
| **Profit & Loss** | revenue, income, profit, expense, earnings | Net Revenue, Operating Income, Net Profit, COGS |
| **Portfolio** | ticker, symbol, shares, position, holdings | Ticker, Shares Owned, Position Value, Cost Basis |
| **Pink Slips** | employee, layoff, termination, separation | Employee Name, Termination Date, Department |

### File Format Requirements
- **Formats**: CSV (`.csv`) or Excel (`.xlsx`, `.xls`)
- **Required Column**: At least one column containing company ticker symbols
- **Ticker Column Names**: `ticker`, `symbol`, `stock_symbol`, `company`, or similar
- **Ticker Format**: 1-5 uppercase letters (e.g., AAPL, TSLA, MSFT)

---

## 🧮 Screening Algorithms

### 1️⃣ Predictability Scoring

**What It Measures**: Revenue consistency and volatility

**Algorithm**: Coefficient of Variation (CV)
```
CV = Standard Deviation / Mean
Predictability Score = 100 × (1 - min(CV, 1.0))
```

**Components**:
- **QoQ (Quarter-over-Quarter)**: Consistency between consecutive quarters
  - Weight: 40%
  - Data: Last 8 quarters
  
- **QoY (Quarter-over-Year)**: Year-over-year growth stability
  - Weight: 60%
  - Data: Quarters compared to same quarter previous year

**Score Interpretation**:
| Score Range | Grade | Meaning |
|-------------|-------|---------|
| ≥ 85 | Excellent | Highly predictable, low volatility |
| 70-84 | Good | Generally consistent with minor variations |
| 55-69 | Fair | Moderate volatility, some unpredictability |
| < 55 | Poor | High volatility, unpredictable patterns |

**Trend Detection**:
- **Improving**: Recent CV < Older CV (getting more predictable)
- **Declining**: Recent CV > Older CV (getting less predictable)
- **Stable**: Little change in CV over time

---

### 2️⃣ 10-K Report Depth Analysis

**What It Measures**: Year-over-year changes in disclosure depth (transparency indicator)

**5 Depth Metrics**:

| Metric | Weight | What It Tracks |
|--------|--------|----------------|
| `line_items` | 25% | Number of financial statement line items |
| `disclosure_sections` | 25% | Number of disclosure sections |
| `segment_details` | 20% | Business segment breakdowns |
| `risk_factors` | 15% | Risk factor disclosures |
| `md_and_a_pages` | 15% | Management Discussion & Analysis length |

**Expansion Trend**:
- **Expanding**: 4+ metrics increased YoY → Increasing transparency ✅
- **Stable-Positive**: 3 metrics increased YoY → Maintaining good disclosure
- **Stable**: 2 metrics increased YoY → Neutral
- **Contracting**: < 2 metrics increased YoY → Reducing transparency ⚠️

**Score Calculation**:
```
Depth Score = Σ(metric_value × weight) for all 5 metrics
```

**Grade Interpretation**:
| Score Range | Grade | Meaning |
|-------------|-------|---------|
| ≥ 80 | Excellent | Very comprehensive disclosure |
| 65-79 | Good | Above-average transparency |
| 50-64 | Fair | Adequate disclosure |
| < 50 | Poor | Limited transparency |

---

### 3️⃣ Quality Score (Overall)

**4 Components**:

| Component | Weight | Description |
|-----------|--------|-------------|
| **Predictability** | 35% | QoQ/QoY consistency (most important) |
| **Report Depth** | 25% | 10-K disclosure quality |
| **Expansion Trend** | 20% | YoY depth improvement |
| **Growth** | 20% | Revenue growth trajectory |

**Calculation**:
```python
quality_score = (
    (predictability_score × 0.35) +
    (report_depth_score × 0.25) +
    (expansion_trend_score × 0.20) +
    (growth_score × 0.20)
)
```

**Letter Grades**:
| Score | Grade | Investment Quality |
|-------|-------|-------------------|
| ≥ 90 | A+ | Exceptional fundamentals |
| 85-89 | A | Excellent fundamentals |
| 80-84 | A- | Very good fundamentals |
| 75-79 | B+ | Good fundamentals |
| 70-74 | B | Above-average fundamentals |
| 65-69 | B- | Decent fundamentals |
| 60-64 | C+ | Fair fundamentals |
| 55-59 | C | Mediocre fundamentals |
| 50-54 | C- | Below-average fundamentals |
| < 50 | D | Poor fundamentals |

---

### 4️⃣ Investment Recommendations

**Action Levels**:

| Recommendation | Criteria | Confidence | Meaning |
|----------------|----------|------------|---------|
| **STRONG BUY** | Score ≥ 80, improving predictability, expanding depth | 95% | Top-tier investment candidate |
| **BUY** | Score ≥ 70, improving/stable predictability | 80% | Strong fundamentals, consider buying |
| **HOLD** | Score ≥ 60, stable metrics | 65% | Acceptable quality, monitor |
| **WATCH** | Score ≥ 50, declining predictability or contracting depth | 50% | Concerning trends, caution advised |
| **AVOID** | Score < 50, poor quality score | 30% | Weak fundamentals, avoid investment |

**Reasoning Components**:
Each recommendation includes specific reasons:
- Predictability grade and trend
- Report depth grade and expansion trend
- Growth trajectory
- Quality score interpretation
- Specific warnings or highlights

---

## 🔧 API Usage

### Endpoint
```http
POST /api/insights/screen-companies
```

### Request
```bash
curl -X POST "http://localhost:8000/api/insights/screen-companies" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@companies.csv"
```

### Response Structure
```json
{
  "status": "success",
  "file_name": "companies.csv",
  "screening_results": {
    "total_companies": 15,
    "companies": [
      {
        "ticker": "AAPL",
        "overall_score": 87.5,
        "overall_grade": "A",
        "recommendation": {
          "action": "STRONG BUY",
          "confidence": 95,
          "reasons": [
            "Excellent predictability (score: 92, grade: excellent)",
            "Improving predictability trend",
            "Expanding 10-K report depth (excellent transparency)",
            "Strong revenue growth trajectory"
          ]
        },
        "predictability": {
          "qoq_score": 88,
          "qoy_score": 94,
          "overall_score": 92,
          "grade": "excellent",
          "trend": "improving"
        },
        "report_depth": {
          "depth_score": 85,
          "grade": "excellent",
          "expansion_trend": "expanding",
          "depth_metrics": {
            "line_items": 245,
            "disclosure_sections": 18,
            "segment_details": 12,
            "risk_factors": 35,
            "md_and_a_pages": 42
          },
          "yoy_changes": {
            "line_items": 15,
            "disclosure_sections": 2,
            "segment_details": 1,
            "risk_factors": 5,
            "md_and_a_pages": 3
          }
        },
        "quality_components": {
          "predictability": 32.2,
          "depth": 21.25,
          "expansion_trend": 18.0,
          "growth": 16.05
        }
      }
    ],
    "summary": {
      "statistics": {
        "average_score": 72.3,
        "median_score": 74.5,
        "highest_score": 87.5,
        "lowest_score": 52.1
      },
      "distribution": {
        "recommendations": {
          "STRONG BUY": 3,
          "BUY": 5,
          "HOLD": 4,
          "WATCH": 2,
          "AVOID": 1
        },
        "grades": {
          "A": 3,
          "B": 7,
          "C": 4,
          "D": 1
        }
      },
      "top_performers": [
        {"ticker": "AAPL", "score": 87.5, "recommendation": "STRONG BUY"},
        {"ticker": "MSFT", "score": 85.2, "recommendation": "STRONG BUY"},
        {"ticker": "GOOGL", "score": 82.8, "recommendation": "STRONG BUY"}
      ],
      "insights": [
        "3 companies show strong buy signals with excellent fundamentals",
        "8 companies demonstrate improving predictability trends",
        "11 companies show expanding 10-K report depth",
        "WARNING: 1 company has contracting report depth (reduced transparency)"
      ]
    }
  },
  "message": "Successfully screened 15 companies"
}
```

---

## 📋 Example CSV Formats

### Portfolio File
```csv
ticker,shares,cost_basis,current_value
AAPL,100,15000,18500
MSFT,50,12500,16000
GOOGL,25,7500,9200
TSLA,30,8000,7500
```

### Balance Sheet Extract
```csv
ticker,total_assets,total_liabilities,shareholders_equity
AAPL,352755000000,287912000000,64843000000
MSFT,364840000000,191791000000,173049000000
```

### Profit & Loss Extract
```csv
ticker,quarter,revenue,operating_income,net_income
AAPL,Q1_2024,119575000000,40323000000,33916000000
AAPL,Q2_2024,90753000000,27421000000,23636000000
```

---

## 🎯 Use Cases

### 1. Portfolio Review
**Scenario**: You hold 50 stocks and want to identify which to prioritize

**Action**: Upload portfolio CSV, screen all holdings

**Outcome**: Focus on STRONG BUY/BUY rated stocks, consider exiting AVOIDs

---

### 2. Watchlist Screening
**Scenario**: You have 100 companies on your radar

**Action**: Upload watchlist with tickers, screen for quality

**Outcome**: Prioritize top 10-15 with highest scores and STRONG BUY ratings

---

### 3. Sector Analysis
**Scenario**: Comparing 20 tech stocks to find best fundamentals

**Action**: Upload tech sector list, analyze quality scores

**Outcome**: Identify sector leaders with best predictability + transparency

---

### 4. Red Flag Detection
**Scenario**: Checking for transparency concerns

**Action**: Screen companies, filter for "contracting" report depth

**Outcome**: Investigate or avoid companies reducing disclosure

---

## ⚙️ Advanced Features

### Data Simulation vs Real Data
**Current State**: Uses simulated financial data for screening
```python
# Quarterly: 8 quarters with revenue growth + realistic noise
# Annual: 2 years with 5 depth metrics
```

**Future Enhancement**: Ready for API integration
- SEC EDGAR API for 10-K/10-Q data
- Yahoo Finance / Alpha Vantage for revenue data
- Real-time updates

---

### Customization Options

**File Type Override**: Specify exact document type
```python
# If auto-detection fails
screening_results = screen_companies_from_file(df, file_type="portfolio")
```

**Supported Overrides**:
- `auto` (default)
- `balance_sheet`
- `profit_loss`
- `portfolio`
- `pink_slips`

---

## 📊 Interpretation Guide

### Strong Investment Signals
✅ **Score ≥ 80** with improving predictability  
✅ **Expanding 10-K depth** (4+ metrics increasing)  
✅ **Excellent/Good grades** in both predictability and depth  
✅ **Improving trend** in predictability  

### Warning Signs
⚠️ **Score < 60** with declining predictability  
⚠️ **Contracting 10-K depth** (transparency reducing)  
⚠️ **Poor grade** in predictability (high volatility)  
⚠️ **Declining trend** in consistency metrics  

### Neutral Indicators
⏸️ **Score 60-70** with stable metrics  
⏸️ **Fair grades** across components  
⏸️ **Stable trends** without improvement or decline  

---

## 🧪 Testing

### Test with Sample Data
Use provided sample files in repository root:
- `sample-portfolio.csv`: Example portfolio with tickers
- `sample-balance-sheet.csv`: Balance sheet format
- `sample-profit-loss.csv`: P&L statement format

### Expected Output
Each company receives:
- Overall quality score (0-100)
- Letter grade (A+ through D)
- Investment recommendation (STRONG BUY through AVOID)
- Detailed predictability analysis
- Report depth breakdown
- Component-level scoring

---

## 🔮 Future Enhancements

### Planned Features
1. **Real Data Integration**: Connect to SEC EDGAR API, financial data APIs
2. **Historical Backtesting**: Test screening system against historical performance
3. **Industry Benchmarking**: Compare companies to industry averages
4. **Custom Weightings**: Allow users to adjust component weights
5. **Alert System**: Notify when watched companies' grades change
6. **Export Reports**: PDF/Excel export of screening results
7. **Batch Processing**: Screen 100+ companies efficiently
8. **Trend Visualization**: Charts showing predictability/depth trends over time

---

## 📚 Related Documentation

- **[PORTFOLIO_CHART_ANALYSIS.md](./PORTFOLIO_CHART_ANALYSIS.md)**: Technical analysis with candlesticks, MA, Fibonacci
- **[TEMPORAL_ANALYSIS_SUMMARY.md](./TEMPORAL_ANALYSIS_SUMMARY.md)**: Pattern performance tracking over time
- **[INSIDER_CALCULUS_ANALYSIS.md](./INSIDER_CALCULUS_ANALYSIS.md)**: Insider trading + calculus-based predictions
- **[FINANCIAL_DOCUMENT_ANALYSIS.md](./FINANCIAL_DOCUMENT_ANALYSIS.md)**: General document processing

---

## 💡 Tips

### Maximizing Results
1. **Upload portfolios** with 20-50 companies for best screening efficiency
2. **Focus on top 10%** - Prioritize companies with scores ≥ 80
3. **Watch trends** - Improving predictability > absolute score
4. **Transparency matters** - Expanding depth = increasing accountability
5. **Combine analyses** - Use fundamental screening + technical analysis + insider analysis for comprehensive view

### Common Pitfalls
❌ **Don't rely on score alone** - Check trend direction  
❌ **Don't ignore warnings** - Contracting depth is a red flag  
❌ **Don't compare across sectors** - Tech vs utilities have different norms  
❌ **Don't overlook context** - Recent events may explain volatility  

---

## 📞 Support

For questions or issues:
1. Check error messages in API response
2. Verify CSV format matches examples
3. Ensure ticker symbols are valid (1-5 uppercase letters)
4. Review file type detection results
5. Open GitHub issue with sample file if problems persist

---

**Version**: 5.0.0  
**Last Updated**: 2024  
**Feature Status**: ✅ Core Complete, Frontend Pending
