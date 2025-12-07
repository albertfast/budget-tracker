# Sample Chart Data File

## Overview
This file contains historical price and volume data for 20 major companies, designed to be used as optional supplementary data for the Financial Analysis Tool.

## File Details
- **Filename**: `sample-chart-data.csv`
- **Format**: CSV (Comma-Separated Values)
- **Rows**: 200 data points (20 companies × 10 trading days each)
- **Date Range**: January 2-16, 2024 (10 consecutive trading days)
- **Columns**: Ticker, Date, Open, High, Low, Close, Volume

## Included Companies
1. **AAPL** - Apple Inc.
2. **MSFT** - Microsoft Corporation
3. **GOOGL** - Alphabet Inc. (Google)
4. **AMZN** - Amazon.com Inc.
5. **NVDA** - NVIDIA Corporation
6. **TSLA** - Tesla Inc.
7. **META** - Meta Platforms Inc. (Facebook)
8. **NFLX** - Netflix Inc.
9. **JPM** - JPMorgan Chase & Co.
10. **V** - Visa Inc.
11. **WMT** - Walmart Inc.
12. **DIS** - The Walt Disney Company
13. **BA** - The Boeing Company
14. **KO** - The Coca-Cola Company
15. **PFE** - Pfizer Inc.
16. **NKE** - NIKE Inc.
17. **INTC** - Intel Corporation
18. **CSCO** - Cisco Systems Inc.
19. **XOM** - Exxon Mobil Corporation
20. **CVX** - Chevron Corporation

## Column Descriptions

### Ticker
- Stock ticker symbol (1-5 uppercase letters)
- Used to match with main financial data file

### Date
- Trading date in YYYY-MM-DD format
- Range: 2024-01-02 to 2024-01-16 (excludes weekends)

### Open
- Opening price for the trading day
- In USD, formatted to 2 decimal places

### High
- Highest price reached during the trading day
- In USD, formatted to 2 decimal places

### Low
- Lowest price reached during the trading day
- In USD, formatted to 2 decimal places

### Close
- Closing price for the trading day
- **Required for analysis** - used for technical indicators
- In USD, formatted to 2 decimal places

### Volume
- Total number of shares traded during the day
- **Recommended for analysis** - used for liquidity assessment
- Integer value

## Usage

### With Financial Analysis Tool
1. Upload your main financial data file (Barchart, Morningstar, or custom CSV)
2. **Optionally** upload this chart data file for enhanced analysis
3. System will match tickers and use historical data for:
   - More accurate buy/sell point calculations
   - Support/resistance level identification
   - Fibonacci retracement levels
   - Technical indicator analysis

### Benefits of Using Chart Data
✅ **More Accurate Analysis**: Uses actual historical data instead of API-fetched data  
✅ **Enhanced Technical Indicators**: Better support/resistance and Fibonacci levels  
✅ **No API Dependencies**: Works offline or when market APIs are unavailable  
✅ **Custom Data Sources**: Can include proprietary or specialized data  
✅ **Faster Processing**: Pre-loaded data reduces API call overhead  

### Without Chart Data
- System will automatically fetch historical prices from market data API (yfinance)
- Analysis will still complete successfully
- Slightly less precise technical indicators depending on API availability

## File Format Requirements

### Minimum Required Columns (case-insensitive)
- `Ticker` or `Symbol` - Stock identifier
- `Date` - Trading date
- `Close` - Closing price
- `Volume` - Trading volume (recommended but optional)

### Accepted Date Formats
- `YYYY-MM-DD` (preferred): 2024-01-02
- `MM/DD/YYYY`: 01/02/2024
- `DD-MM-YYYY`: 02-01-2024

### Column Name Variants (case-insensitive)
The system recognizes various column name formats:
- **Ticker**: `ticker`, `symbol`, `stock_symbol`, `Symbol`, `Ticker`
- **Date**: `date`, `Date`, `trading_date`, `Trade Date`
- **Close**: `close`, `Close`, `closing_price`, `Adj Close`, `price`
- **Volume**: `volume`, `Volume`, `trading_volume`, `Vol`

## Creating Your Own Chart Data File

### Option 1: Export from Yahoo Finance
1. Go to https://finance.yahoo.com
2. Search for your stock ticker
3. Click "Historical Data" tab
4. Select date range (90-180 days recommended)
5. Click "Download" to get CSV file
6. Combine multiple stock files if needed

### Option 2: Export from Trading Platform
Most trading platforms (TD Ameritrade, Interactive Brokers, etc.) allow CSV export of historical data.

### Option 3: Create Custom CSV
Use this template:
```csv
Ticker,Date,Open,High,Low,Close,Volume
YOUR_TICKER,2024-01-02,100.00,105.00,99.00,103.50,1000000
YOUR_TICKER,2024-01-03,103.50,107.00,102.00,106.25,1200000
```

### Recommendations
- **Date Range**: 90-180 days for technical analysis
- **Data Frequency**: Daily OHLC data (not intraday)
- **Ticker Matching**: Ensure ticker symbols exactly match your main financial data file
- **Data Quality**: Remove any rows with missing or zero values

## Example Usage

### Matching with Barchart Data
If your `sample-barchart-financials.csv` contains:
```csv
Symbol,Revenue (M),Net Income (M),ROE (%)
AAPL,394328,96995,147.4
MSFT,211915,72361,43.1
```

Then this chart data file provides historical prices for AAPL and MSFT, enabling:
- Current price analysis
- Buy point calculation based on support levels
- Target price based on resistance levels
- Stop loss recommendations

### Sample Analysis Output
With chart data:
```
AAPL Analysis:
- Current Price: $185.58 (from chart data)
- Buy Point: $180.88 (recent low + support)
- Target Price: $189.99 (resistance level)
- Stop Loss: $175.50
- Potential Return: 5.2%
```

Without chart data:
```
AAPL Analysis:
- Current Price: $186.50 (from API, may be delayed)
- Buy Point: $181.00 (estimated support)
- Target Price: $190.00 (estimated resistance)
- Stop Loss: $176.00
- Potential Return: 5.0%
```

## Compatibility

### Supported Formats
- ✅ CSV (`.csv`)
- ✅ Excel 2007+ (`.xlsx`)
- ✅ Excel Legacy (`.xls`)

### Encoding
- UTF-8 (recommended)
- ASCII
- ISO-8859-1

### File Size
- Recommended: < 10 MB
- Maximum: 50 MB
- Typical: 200-1000 rows = ~50 KB

## Troubleshooting

### "Chart data file not recognized"
**Solution**: Ensure your file has required columns: Ticker, Date, Close, Volume

### "Ticker mismatch"
**Problem**: Tickers in chart data don't match main financial data  
**Solution**: Verify ticker symbols are identical (case-sensitive: "AAPL" ≠ "aapl")

### "Chart data not being used"
**Check**: Look for log message "Using provided chart data for {TICKER}"  
**Solution**: Ensure date range overlaps with analysis period (recent 90-180 days)

### "Invalid date format"
**Solution**: Use YYYY-MM-DD format or MM/DD/YYYY

## Best Practices

### Data Quality
1. ✅ Include at least 90 days of historical data
2. ✅ Ensure no gaps in trading days (weekends/holidays excluded)
3. ✅ Verify prices are reasonable (no outliers or errors)
4. ✅ Include volume data for liquidity analysis

### Performance
1. ✅ Keep file size under 10 MB for fast upload
2. ✅ Remove unnecessary columns to reduce size
3. ✅ Use CSV format for fastest parsing

### Accuracy
1. ✅ Use recent data (within last 6 months)
2. ✅ Verify ticker symbols match exactly
3. ✅ Use adjusted close prices (if available) for split/dividend accuracy

## Data Source
The sample data in this file is **simulated** for demonstration purposes. For real analysis, use actual historical data from:
- Yahoo Finance (free)
- Alpha Vantage (free tier available)
- IEX Cloud (free tier available)
- Your trading platform's export feature

## License
This sample file is provided for educational and testing purposes. Replace with actual market data for production use.

---

**Created**: January 2025  
**Version**: 1.0  
**Purpose**: Optional supplementary data for Financial Analysis Tool  
**Status**: Ready for use
