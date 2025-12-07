# Financial Analysis Tool - Complete Guide

## Overview
The Financial Analysis Tool is a comprehensive investment analysis system that processes financial data from multiple sources (Barchart, Morningstar, CSV, Excel, SEC EDGAR) and provides detailed quality scoring, predictability analysis, and actionable buy/sell recommendations with specific price points.

## Table of Contents
1. [Features](#features)
2. [Supported Data Formats](#supported-data-formats)
3. [Analysis Indicators](#analysis-indicators)
4. [How to Use](#how-to-use)
5. [Understanding Results](#understanding-results)
6. [API Reference](#api-reference)
7. [Sample Files](#sample-files)
8. [Troubleshooting](#troubleshooting)

---

## Features

### 🎯 Comprehensive Analysis
- **All Quality Indicators**: Profitability, Liquidity, Efficiency, Growth
- **Predictability Metrics**: QoQ (Quarter-over-Quarter) and QoY (Quarter-over-Year) consistency scoring
- **Report Depth Analysis**: 10-K disclosure quality and year-over-year expansion trends
- **Technical Analysis Integration**: Support/resistance levels, Fibonacci retracements

### 💰 Buy/Sell Points
- **Entry Points**: Optimal buy prices based on support levels and quality scores
- **Target Prices**: Profit-taking levels using resistance and quality-based upside
- **Stop Loss Levels**: Risk management with calculated stop-loss prices
- **Potential Return**: Calculated expected returns based on entry and target prices

### 🏆 Sorted Rankings
- Companies automatically ranked from **strongest to weakest** prediction
- Multiple sorting options: Score, Potential Return, Confidence, Risk Level
- Easy identification of top investment opportunities

### 📊 Confidence Scoring
- **STRONG BUY** (95% confidence): Excellent fundamentals, improving trends
- **BUY** (80% confidence): Solid fundamentals, positive indicators
- **HOLD** (65% confidence): Acceptable metrics, monitor for changes
- **WATCH** (50% confidence): Below-average, wait for improvement
- **AVOID** (30% confidence): Poor fundamentals, high risk

---

## Supported Data Formats

### 1. Barchart Format
**Source**: Export from Barchart.com financial tables

**Required Columns**:
- `Symbol` or `Ticker`: Stock ticker (1-5 letters)
- Any of these metrics:
  - `Revenue`, `Revenue (M)`, `Revenue (B)`
  - `Net Income`, `Net Income (M)`
  - `ROE (%)`, `ROA (%)`
  - `Debt/Equity`, `Debt-to-Equity`
  - `Current Ratio`, `Quick Ratio`
  - `Profit Margin (%)`, `Operating Margin (%)`

**Example**:
```csv
Symbol,Revenue (M),Net Income (M),ROE (%),Debt/Equity,Current Ratio
AAPL,394328,96995,147.4,1.78,0.98
MSFT,211915,72361,43.1,0.35,1.77
GOOGL,307394,73795,28.2,0.12,2.61
```

**File**: `sample-barchart-financials.csv`

### 2. Morningstar Format
**Source**: Export from Morningstar.com stock data

**Required Columns**:
- `Ticker` or `Symbol`: Stock ticker
- Any of these metrics:
  - `Price`, `Current Price`
  - `P/E Ratio`, `PE`, `Price/Earnings`
  - `EPS`, `Earnings Per Share`
  - `Market Cap (B)`, `Market Cap`
  - `Revenue Growth (%)`, `Earnings Growth (%)`
  - `Dividend Yield (%)`

**Example**:
```csv
Ticker,Price,P/E Ratio,EPS,Revenue Growth (%),Earnings Growth (%)
AAPL,175.43,28.5,6.16,9.5,13.2
MSFT,378.91,36.2,10.48,11.8,18.5
GOOGL,140.93,26.3,5.36,8.6,15.9
```

**File**: `sample-morningstar-financials.csv`

### 3. CSV/Excel Format
**Source**: Custom exports, spreadsheets

**Required**:
- At least one column with ticker symbols: `ticker`, `symbol`, `stock_symbol`, `company`, `Symbol`, `Ticker`
- Optional: Any financial metrics (revenue, earnings, ratios)

**Supported Extensions**: `.csv`, `.xlsx`, `.xls`

### 4. Optional Chart Data File (ENHANCED ANALYSIS)
**Source**: Historical price/volume data, quarterly time series

**Purpose**: Provides supplementary data for more accurate technical analysis and buy/sell point calculations when not available in the main financial data file.

**Benefits**:
- ✅ **More Accurate Analysis**: Uses actual historical data instead of fetching from external APIs
- ✅ **Custom Data Sources**: Include proprietary or specialized data not available publicly
- ✅ **No API Rate Limits**: Analyze without dependency on market data API availability
- ✅ **Quarterly Time Series**: Include quarterly revenue/earnings data for better trend analysis
- ✅ **Enhanced Technical Indicators**: More precise support/resistance and Fibonacci levels

**Required Columns** (case-insensitive):
- `Ticker` or `Symbol`: Stock ticker to match with main data
- `Date`: Trading date (YYYY-MM-DD, MM/DD/YYYY, or similar)
- `Close`: Closing price for the date
- `Volume`: Trading volume (optional but recommended)

**Optional Columns**:
- `Open`, `High`, `Low`: Additional OHLC data
- `Quarterly_Revenue`, `Quarterly_Earnings`: Time series fundamentals
- Any technical indicators (RSI, MACD, etc.)

**Example**:
```csv
Ticker,Date,Open,High,Low,Close,Volume
AAPL,2024-01-02,185.64,186.95,184.27,185.58,52816200
AAPL,2024-01-03,184.25,185.93,182.63,184.25,45923400
AAPL,2024-01-04,182.15,183.98,180.88,181.18,54426100
MSFT,2024-01-02,372.22,373.78,368.17,371.41,17089800
MSFT,2024-01-03,369.63,373.67,365.88,368.33,18439800
```

**File**: `sample-chart-data.csv` (includes 20 companies with 10 days of OHLCV data)

**When to Use**:
- You have historical price data from a specialized source (Bloomberg, proprietary systems)
- You want to analyze companies with limited market data API coverage
- You need quarterly financial time series (revenue/earnings by quarter)
- You're analyzing during market hours and want real-time data you've captured
- You want to include custom technical indicators you've pre-calculated

**Fallback Behavior**:
If chart data is not provided or parsing fails, the system will automatically fetch historical data from the market data API (yfinance). Your analysis will still complete successfully, but may use slightly less precise data depending on API availability.

**Supported Extensions**: `.csv`, `.xlsx`, `.xls`

### 4. SEC EDGAR Format
**Source**: sec.gov/edgar

**Supported Formats**:
- `.xml`, `.xbrl`: XBRL financial data (10-K, 10-Q filings)
- `.htm`, `.html`: HTML-formatted SEC reports
- `.json`: SEC API JSON responses
- `.txt`: Plain text filings

**Download from**: [https://www.sec.gov/edgar](https://www.sec.gov/edgar)

---

## Analysis Indicators

### Predictability Metrics
Measures consistency and reliability of financial performance over time.

#### Quarter-over-Quarter (QoQ) Score (0-100)
- **What it measures**: Consistency of quarterly results
- **Calculation**: Based on coefficient of variation of QoQ growth rates
- **Interpretation**:
  - 85-100: Excellent predictability
  - 70-84: Good consistency
  - 55-69: Fair, some volatility
  - <55: Poor, unpredictable

#### Quarter-over-Year (QoY) Score (0-100)
- **What it measures**: Year-over-year seasonal consistency
- **Calculation**: Compares same quarters across years
- **Weight**: 60% of overall predictability (more important than QoQ)

#### Predictability Grade
- **Excellent** (≥85): Highly predictable revenue patterns
- **Good** (70-84): Consistent performance
- **Fair** (55-69): Moderate volatility
- **Poor** (<55): Unpredictable patterns

#### Predictability Trend
- **Improving** 📈: Becoming more consistent (positive sign)
- **Stable** ➡️: Maintaining consistency
- **Declining** 📉: Becoming less predictable (caution)

### Profitability Metrics

#### Gross Profit Margin
- **Formula**: (Revenue - COGS) / Revenue × 100
- **Benchmark**: >40% excellent, 20-40% good, <20% concerning

#### Operating Margin
- **Formula**: Operating Income / Revenue × 100
- **Benchmark**: >15% strong, 5-15% moderate, <5% weak

#### Net Profit Margin
- **Formula**: Net Income / Revenue × 100
- **Benchmark**: >20% excellent, 10-20% good, <10% concerning

#### Return on Equity (ROE)
- **Formula**: Net Income / Shareholders' Equity × 100
- **Benchmark**: >20% excellent, 15-20% good, 10-15% fair, <10% poor

#### Return on Assets (ROA)
- **Formula**: Net Income / Total Assets × 100
- **Benchmark**: >10% excellent, 5-10% good, <5% concerning

#### Return on Invested Capital (ROIC)
- **Formula**: (Net Income - Dividends) / (Debt + Equity) × 100
- **Benchmark**: >15% excellent, 10-15% good, <10% concerning

### Liquidity Metrics

#### Current Ratio
- **Formula**: Current Assets / Current Liabilities
- **Benchmark**: >2.0 strong, 1.5-2.0 good, 1.0-1.5 adequate, <1.0 concerning

#### Quick Ratio (Acid Test)
- **Formula**: (Current Assets - Inventory) / Current Liabilities
- **Benchmark**: >1.5 strong, 1.0-1.5 good, <1.0 concerning

#### Cash Ratio
- **Formula**: Cash & Cash Equivalents / Current Liabilities
- **Benchmark**: >0.5 excellent, 0.2-0.5 good, <0.2 concerning

### Solvency Metrics

#### Debt-to-Assets Ratio
- **Formula**: Total Debt / Total Assets
- **Benchmark**: <30% excellent, 30-50% moderate, >50% high leverage

#### Debt-to-Equity Ratio
- **Formula**: Total Debt / Shareholders' Equity
- **Benchmark**: <0.5 excellent, 0.5-1.5 moderate, >1.5 high leverage

#### Interest Coverage Ratio
- **Formula**: Operating Income / Interest Expense
- **Benchmark**: >5x strong, 2-5x adequate, <2x concerning

### Efficiency Metrics

#### Asset Turnover
- **Formula**: Revenue / Average Total Assets
- **Benchmark**: >2.0 efficient, 1.0-2.0 moderate, <1.0 inefficient

#### Inventory Turnover
- **Formula**: Cost of Goods Sold / Average Inventory
- **Benchmark**: Industry-dependent (higher generally better)

#### Receivables Turnover
- **Formula**: Revenue / Average Accounts Receivable
- **Benchmark**: >10x excellent, 5-10x good, <5x concerning

### Growth Metrics

#### Revenue Growth (1-Year)
- **Calculation**: (Current Year Revenue - Prior Year) / Prior Year × 100
- **Benchmark**: >15% high growth, 5-15% moderate, <5% slow growth

#### Revenue Growth (3-Year)
- **Calculation**: Compound Annual Growth Rate over 3 years
- **Benchmark**: >20% exceptional, 10-20% strong, <10% stable

#### Earnings Growth (1-Year)
- **Benchmark**: >20% strong, 10-20% good, <10% concerning

#### Earnings Growth (3-Year)
- **Benchmark**: >25% exceptional, 15-25% strong, <15% moderate

### Report Depth Analysis

#### 10-K Disclosure Quality
Measures transparency and comprehensiveness of SEC filings.

**Components**:
1. **Total Line Items** (25% weight): Number of financial statement items
   - Benchmark: >400 comprehensive, 200-400 detailed, <200 minimal
   
2. **Disclosure Sections** (25% weight): Number of disclosure topics
   - Benchmark: >25 comprehensive, 15-25 adequate, <15 minimal
   
3. **Segment Details** (20% weight): Business segment breakdown
   - Benchmark: >6 segments detailed, 3-6 good, <3 limited
   
4. **Risk Factors** (15% weight): Identified risk disclosures
   - Benchmark: >40 comprehensive, 20-40 adequate, <20 minimal
   
5. **MD&A Pages** (15% weight): Management Discussion & Analysis length
   - Benchmark: >30 pages detailed, 15-30 adequate, <15 brief

#### Expansion Trend
- **Expanding** 🔼: Increasing disclosure (positive transparency)
- **Stable Positive** ✅: Maintaining high disclosure levels
- **Stable** ➡️: Consistent disclosure
- **Contracting** 🔽: Decreasing disclosure (RED FLAG)

### Quality Score Components

#### Overall Quality Score (0-100)
Weighted combination of all metrics:
- **Predictability**: 35% (most important)
- **Report Depth**: 25%
- **Expansion Trend**: 20%
- **Growth**: 20%

#### Quality Grade
- **A+ / A / A-** (80-100): Excellent investment quality
- **B+ / B / B-** (65-79): Good quality, solid fundamentals
- **C+ / C / C-** (50-64): Fair quality, acceptable risk
- **D** (<50): Poor quality, high risk

---

## How to Use

### Step 1: Prepare Your Data

#### Option A: Export from Barchart
1. Go to [Barchart.com](https://www.barchart.com)
2. Search for companies and navigate to financial tables
3. Export data to CSV/Excel
4. Ensure ticker symbols are included

#### Option B: Export from Morningstar
1. Go to [Morningstar.com](https://www.morningstar.com)
2. Navigate to stock data tables
3. Export to CSV/Excel
4. Ensure ticker column is present

#### Option C: Download SEC Filings
1. Go to [SEC EDGAR](https://www.sec.gov/edgar)
2. Search for company (CIK or ticker)
3. Download 10-K, 10-Q, or 8-K filing
4. Supported formats: XBRL (.xml), HTML (.htm), JSON

#### Option D: Create Custom CSV
1. Create spreadsheet with ticker column
2. Add any available financial metrics
3. Save as CSV or Excel (.xlsx)

### Step 2: Upload to Financial Analysis Tool

#### Basic Upload (Main Financial Data Only)
1. **Open the App**: Navigate to "Financial Analysis" tab
2. **Select File**: Tap "Select Financial Data File" button (Step 1)
3. **Choose File**: Pick your prepared CSV/Excel/XBRL file
4. **Analyze**: Tap "Analyze Financials" button
5. **Wait**: Processing typically takes 10-30 seconds depending on file size

#### Enhanced Upload (With Optional Chart Data) - RECOMMENDED
For more accurate buy/sell points and technical analysis:

1. **Upload Main Data**: Follow steps 1-3 above
2. **Select Chart Data** (Optional): Tap "Select Chart Data (Optional)" button (Step 2)
3. **Choose Chart File**: Pick your historical price/volume CSV/Excel file
   - Must include: `Ticker`, `Date`, `Close`, `Volume` columns
   - Example: `sample-chart-data.csv` (provided)
4. **Analyze**: Tap "Analyze Financials" button
5. **Wait**: Processing with chart data may take 5-10 seconds longer
6. **Enhanced Results**: You'll see more precise price targets and support/resistance levels

**Note**: If you don't provide chart data, the system will automatically fetch historical prices from the market data API. Chart data is optional but recommended for:
- Custom or proprietary price data
- Better accuracy in volatile markets
- Companies with limited API coverage
- Offline analysis scenarios

### Step 3: Review Results

Results are displayed in **ranked order** (best to worst):

1. **Summary Card**:
   - Total companies analyzed
   - Average quality score
   - Highest/lowest scores
   - Key insights

2. **Company Cards** (tap to expand):
   - **Rank Badge**: #1, #2, etc.
   - **Quality Grade**: A+, A, B+, etc.
   - **Overall Score**: 0-100 scale
   - **Recommendation Banner**: STRONG BUY, BUY, HOLD, WATCH, AVOID

3. **Expanded Details** (when card is tapped):
   - **Price Points**: Current, Buy, Target, Stop Loss
   - **Potential Return**: Expected % gain
   - **Predictability Analysis**: QoQ/QoY scores and grade
   - **Report Depth**: Disclosure quality and trend
   - **Quality Components**: Visual breakdown of score components
   - **Reasons**: Specific factors driving the recommendation

---

## Understanding Results

### Recommendation Actions

#### STRONG BUY 🚀
- **Criteria**:
  - Overall Score ≥80
  - Predictability improving
  - Report depth expanding or stable-positive
- **Confidence**: 95%
- **Action**: High-conviction purchase
- **Timeframe**: Long-term (1-2+ years)
- **Risk Level**: Low

#### BUY ✅
- **Criteria**:
  - Overall Score ≥70
  - Predictability stable or improving
- **Confidence**: 80%
- **Action**: Good investment opportunity
- **Timeframe**: Medium-term (6-12 months)
- **Risk Level**: Low to Medium

#### HOLD ✋
- **Criteria**:
  - Overall Score ≥60
  - Mixed indicators
- **Confidence**: 65%
- **Action**: Monitor position, don't add/sell
- **Timeframe**: Monitor quarterly
- **Risk Level**: Medium

#### WATCH 👀
- **Criteria**:
  - Overall Score ≥50
  - Some concerns present
- **Confidence**: 50%
- **Action**: Watch for improvement before entering
- **Timeframe**: Not recommended for investment
- **Risk Level**: High

#### AVOID ⛔
- **Criteria**:
  - Overall Score <50
  - Poor fundamentals
  - Contracting disclosure
- **Confidence**: 30%
- **Action**: Do not invest
- **Timeframe**: N/A
- **Risk Level**: Very High

### Price Points Explained

#### Current Price
- Latest market price at time of analysis
- Used as baseline for all calculations

#### Buy Point
- **For STRONG BUY/BUY**: Support level or 3% below current
- **For HOLD**: 5% below current
- **For WATCH/AVOID**: 15% below current (significant drop needed)
- **Purpose**: Optimal entry price for position

#### Target Price
- **For STRONG BUY**: 15% above buy point (quality score ≥80)
- **For BUY**: 10% above buy point
- **For HOLD**: Resistance level or 8% above current
- **Purpose**: Profit-taking level

#### Stop Loss
- **For STRONG BUY/BUY**: 8% below buy point
- **For HOLD**: 12% below current
- **Purpose**: Risk management, exit if thesis breaks

#### Potential Return
- **Calculation**: ((Target Price - Buy Point) / Buy Point) × 100
- **Interpretation**:
  - >15%: Excellent upside
  - 10-15%: Good opportunity
  - 5-10%: Moderate potential
  - <5%: Limited upside

### Support & Resistance Levels
- **Support**: Price levels where buying interest increases (floor)
- **Resistance**: Price levels where selling pressure increases (ceiling)
- **Usage**: Alternative entry/exit points for trades

### Fibonacci Levels
Golden ratio-based technical levels (23.6%, 38.2%, 50%, 61.8%, 100%):
- Used to identify potential retracement and extension targets
- Confluence with support/resistance increases reliability

---

## API Reference

### Endpoint
```
POST /api/insights/analyze-financials
```

### Request
```typescript
Content-Type: multipart/form-data
Authorization: Bearer {token}

Body:
- file: File (CSV, Excel, XBRL, HTML, JSON, TXT)
```

### Response
```typescript
{
  "success": true,
  "analysis_type": "comprehensive_financial",
  "file_name": "sample-barchart-financials.csv",
  "analysis_results": {
    "total_companies": 20,
    "file_type": "balance_sheet",
    "companies": [
      {
        "ticker": "AAPL",
        "company_name": "Apple Inc.",
        "overall_score": 87.3,
        "quality_score": {
          "overall": 87.3,
          "components": {
            "predictability": 85.2,
            "report_depth": 78.5,
            "expansion_trend": 100,
            "growth": 72.8
          },
          "grade": "A"
        },
        "recommendation": {
          "action": "STRONG BUY",
          "confidence": 95,
          "color": "green",
          "reasons": [
            "✓ Excellent revenue predictability",
            "✓ Predictability improving over time",
            "✓ Expanding 10-K depth (transparency increasing)",
            "✓ Positive revenue growth trend"
          ],
          "summary": "Excellent fundamentals with excellent predictability and comprehensive report depth. Strong investment candidate."
        },
        "predictability": {
          "qoq_score": 82.5,
          "qoy_score": 87.3,
          "overall_predictability": 85.2,
          "trend": "improving",
          "grade": "excellent"
        },
        "report_depth": {
          "depth_score": 78.5,
          "trend_score": 100,
          "expansion_trend": "expanding",
          "grade": "detailed"
        },
        "price_analysis": {
          "current_price": 175.43,
          "buy_point": 170.17,
          "target_price": 195.70,
          "stop_loss": 156.56,
          "support_levels": [168.25, 164.80, 160.50],
          "resistance_levels": [182.40, 189.75, 199.62],
          "potential_return": 15.0
        }
      }
    ],
    "summary": {
      "total_screened": 20,
      "average_score": 67.4,
      "median_score": 69.2,
      "highest_score": 87.3,
      "lowest_score": 32.1,
      "recommendations": {
        "STRONG BUY": 3,
        "BUY": 5,
        "HOLD": 7,
        "WATCH": 3,
        "AVOID": 2
      },
      "insights": [
        "✓ 3 companies with excellent fundamentals (score ≥ 80)",
        "✓ 5 companies showing improving predictability",
        "✓ 8 companies expanding report depth (good transparency)"
      ]
    }
  }
}
```

---

## Sample Files

### Barchart Sample
**File**: `sample-barchart-financials.csv`
- **Companies**: 20 major US stocks (AAPL, MSFT, GOOGL, etc.)
- **Metrics**: Revenue, Net Income, ROE, ROA, Debt/Equity, Current Ratio, Margins
- **Format**: Barchart export style

### Morningstar Sample
**File**: `sample-morningstar-financials.csv`
- **Companies**: Same 20 stocks for comparison
- **Metrics**: Price, P/E, EPS, Market Cap, Growth rates, Dividend Yield
- **Format**: Morningstar export style

### Usage
1. Download sample files from repository root
2. Upload to Financial Analysis tool
3. Review results to understand output format
4. Compare with your own data exports

---

## Troubleshooting

### File Upload Issues

#### "Invalid file format"
- **Solution**: Ensure file has one of these extensions: `.csv`, `.xlsx`, `.xls`, `.xml`, `.xbrl`, `.htm`, `.html`, `.txt`, `.json`
- **Tip**: Re-save file with correct extension if needed

#### "No companies detected in file"
- **Solution**: Verify file has a ticker/symbol column
- **Accepted column names**: `ticker`, `symbol`, `stock_symbol`, `company`, `Symbol`, `Ticker`, `Company`
- **Ticker format**: 1-5 uppercase letters (AAPL, MSFT)

#### "File contains no data rows"
- **Solution**: Ensure file has at least one data row below headers
- **Check**: File isn't corrupted, opens properly in Excel

### Analysis Issues

#### "Insufficient financial data"
- **Solution**: System needs at least 4 quarters of data for predictability
- **Tip**: For SEC filings, ensure XBRL contains historical data

#### Low scores across all companies
- **Possible causes**:
  - Missing key financial metrics in file
  - Data quality issues (zeros, nulls, invalid values)
  - Companies are genuinely weak performers
- **Solution**: Verify source data completeness and accuracy

#### No price analysis data
- **Cause**: Market data API couldn't fetch current prices
- **Impact**: Analysis still works, but no buy/sell points
- **Solutions**:
  1. Check internet connection, try again later
  2. **Upload optional chart data file** with historical prices (RECOMMENDED)
  3. Verify ticker symbols are correct in your file

#### Chart data file not recognized (Optional Upload)
- **Cause**: Missing required columns or incorrect format
- **Required columns** (case-insensitive): `Ticker`, `Date`, `Close`, `Volume`
- **Solution**: Use `sample-chart-data.csv` as template
- **Format examples**:
  ```csv
  Ticker,Date,Close,Volume
  AAPL,2024-01-02,185.58,52816200
  ```
- **Note**: If chart data fails, system automatically falls back to market API

#### Chart data uploaded but not being used
- **Check**: Ensure ticker symbols in chart data match those in main financial data file exactly
- **Tip**: Log messages will show "Using provided chart data for {TICKER}" when successfully used
- **Common issue**: Ticker mismatch (e.g., "AAPL" in main file, "Apple" in chart data)

### Data Format Issues

#### Mixed or inconsistent results
- **Solution**: Standardize column names and data formats
- **Tip**: Use sample files as templates

#### Excel file not parsing
- **Solution**: Save as `.xlsx` (not `.xls` legacy format)
- **Tip**: Remove special characters from column names

#### XBRL file not parsing
- **Solution**: Ensure file is valid XBRL from SEC EDGAR
- **Tip**: Download directly from sec.gov rather than third-party sources

### Network Issues

#### "Unable to connect to server"
- **Solutions**:
  1. Check internet connection
  2. Verify backend server is running (`http://localhost:8000`)
  3. Check firewall settings
  4. Restart mobile app

#### "Request timeout"
- **Cause**: Large file or slow network
- **Solutions**:
  1. Reduce number of companies in file
  2. Use faster internet connection
  3. Increase timeout settings (developer)

---

## Best Practices

### Data Preparation
1. ✅ Include as many financial metrics as possible
2. ✅ Use recent data (within last 2 years)
3. ✅ Verify ticker symbols are correct
4. ✅ Remove rows with all missing data
5. ✅ Standardize number formats (remove $, %, commas)
6. ✅ **RECOMMENDED**: Prepare optional chart data file with historical prices (90-180 days)
7. ✅ Ensure ticker symbols match exactly between main and chart data files

### Analysis Workflow
1. **Start with sample files** to understand output format
2. **Export your data** from Barchart or Morningstar
3. **Review file** before uploading (check tickers, data quality)
4. **Analyze** and review ranked results
5. **Deep dive** on top-ranked companies (expand cards)
6. **Note buy/sell points** for actionable trades
7. **Monitor** WATCH-rated companies for improvement

### Interpretation Tips
1. **Focus on top 25%** of ranked companies
2. **Consider multiple factors**: Don't rely solely on score
3. **Check predictability trend**: Improving > Stable > Declining
4. **Verify report depth expansion**: Expanding = good transparency
5. **Use price points**: Don't chase, wait for entry opportunities
6. **Set stop losses**: Always manage risk with stop-loss orders
7. **Review reasons**: Understand WHY a recommendation was made

### Portfolio Construction
- **STRONG BUY (95% confidence)**: 40-50% of portfolio
- **BUY (80% confidence)**: 30-40% of portfolio
- **HOLD**: Keep existing positions, monitor
- **WATCH**: Small speculative positions only (<10%)
- **AVOID**: No allocation

---

## Technical Details

### Backend Processing
- **Language**: Python 3.9+
- **Framework**: FastAPI
- **Analysis Engine**: fundamental_analysis_service.py
- **Parser**: sec_edgar_parser.py (for XBRL/SEC formats)
- **Technical Analysis**: technical_analysis_service.py

### Frontend
- **Framework**: React Native (Expo)
- **Screen**: FinancialAnalysisScreen.tsx
- **API Service**: financialAnalysisApi.ts
- **Navigation**: BottomTabs.tsx

### Algorithms
- **Predictability**: Coefficient of Variation (CV) analysis on QoQ/QoY growth
- **Quality Score**: Weighted combination (35% pred, 25% depth, 20% trend, 20% growth)
- **Buy/Sell Points**: Technical analysis with support/resistance + Fibonacci
- **Risk Scoring**: Multi-factor model with score, predictability, and action

---

## FAQ

**Q: How accurate are the recommendations?**
A: Recommendations are based on historical fundamental data and technical analysis. They are educational tools, not guaranteed predictions. Always do additional research and consider your risk tolerance.

**Q: Can I analyze international stocks?**
A: Currently optimized for US stocks with SEC filings. International stocks work if you have comparable financial data, but may lack 10-K depth analysis.

**Q: How often should I run analysis?**
A: Quarterly (after earnings reports) for active management, or annually for long-term positions.

**Q: What if a company has no price data?**
A: Fundamental analysis still works. You won't get buy/sell price points, but quality score and ranking remain valid.

**Q: Can I analyze private companies?**
A: Yes, if you have financial statements. However, no public price data means no buy/sell points or technical analysis.

**Q: How many companies can I analyze at once?**
A: Recommended limit: 50-100 companies per file. Larger files may take longer to process.

**Q: What's the difference between this and Company Screening?**
A: **Financial Analysis** provides comprehensive metrics with buy/sell points. **Company Screening** is lighter-weight screening tool. Use Financial Analysis for deep investment research.

---

## Support & Contributing

### Report Issues
- GitHub: [budget-tracker/issues](https://github.com/Head2MyToes/budget-tracker/issues)
- Include: File format, error message, sample data (anonymized)

### Feature Requests
- Request via GitHub Issues with `enhancement` label
- Describe use case and expected behavior

### Documentation Updates
- Submit PRs for documentation improvements
- Update this guide as features evolve

---

**Last Updated**: November 24, 2025  
**Version**: 1.0.0  
**Status**: Production Ready ✅
