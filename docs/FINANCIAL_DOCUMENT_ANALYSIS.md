# Financial Document Analysis Feature

## 📊 Overview

The investment analysis tool has been enhanced to support multiple financial document types beyond simple portfolios. The system now intelligently detects and analyzes:

1. **Portfolio Holdings** - Stock/ETF positions with cost basis
2. **Profit & Loss Statements** - Company financial performance
3. **Balance Sheets** - Financial position and health metrics
4. **Pink Slips (Trade Confirmations)** - Historical trades and current positions

## 🎯 Features

### Automatic Document Detection
- AI automatically detects document type based on content
- No manual selection required
- Supports flexible CSV formats with case-insensitive headers

### Document Types Supported

#### 1. Portfolio Analysis
**Format:**
```csv
Symbol,Quantity,Cost Basis
AAPL,10,150.00
MSFT,5,280.50
GOOGL,2,2500.00
```

**Analysis Provided:**
- Current market value vs cost basis
- Gain/loss calculations ($ and %)
- AI-powered buy/sell/hold recommendations
- Price targets with confidence levels
- Technical & fundamental analysis per holding

#### 2. Profit & Loss Statement
**Format:**
```csv
Category,Amount
Revenue,500000
Cost of Goods Sold,200000
Operating Expenses,120000
Net Income,135000
```

**Analysis Provided:**
- Profitability assessment
- Gross profit margin
- Net profit margin
- Expense ratio
- Operating margin
- Actionable recommendations for improvement

**Sample Recommendations:**
- ⚠️ Low profit margin - Focus on cost reduction
- 💸 High expense ratio - Review operational efficiency
- ✅ Strong profit margins - Consider reinvesting for growth

#### 3. Balance Sheet
**Format:**
```csv
Account,Amount
Current Assets,150000
Total Assets,500000
Current Liabilities,75000
Total Liabilities,250000
Shareholders Equity,250000
```

**Analysis Provided:**
- Financial health assessment (strong/moderate/weak)
- Current ratio (liquidity)
- Quick ratio
- Debt-to-equity ratio
- Debt-to-assets ratio
- Working capital
- Equity ratio

**Sample Recommendations:**
- ✅ Strong liquidity position - Good short-term financial health
- ⚠️ Liquidity concern - Current assets below liabilities
- 💪 Conservative capital structure

#### 4. Pink Slips (Trade Confirmations)
**Format:**
```csv
Symbol,Shares,Price,Commission,Date,Type
AAPL,10,150.00,0.50,2024-01-15,buy
MSFT,5,280.50,0.25,2024-01-20,buy
AAPL,5,165.00,0.25,2024-02-28,sell
```

**Analysis Provided:**
- Trade history summary
- Current open positions after netting buys/sells
- Aggregated cost basis per symbol
- Total invested vs total proceeds
- Current market value of positions
- AI recommendations for each open position

## 🚀 Usage

### Backend Setup

1. **Ensure the document parser service is imported:**
   ```python
   from ..services.document_parser_service import document_parser
   ```

2. **Use the unified upload endpoint:**
   ```
   POST /api/insights/upload-financial-document
   ```

### Frontend Integration

1. **Component renders format examples:**
   - Tab-based interface showing all 4 document types
   - Sample CSV format for each type
   - Clear instructions on required columns

2. **Upload flow:**
   ```typescript
   const uploadDocument = async (file: any) => {
     const response = await investmentApi.uploadPortfolio(file);
     // Response automatically includes document_type
     setDocumentType(response.document_type);
     setAnalysis(response);
   };
   ```

3. **Display results based on document type:**
   - Portfolio: Holdings with recommendations
   - P&L: Profitability metrics and suggestions
   - Balance Sheet: Financial health indicators
   - Pink Slips: Trade history and current positions

## 📝 Sample Files

Sample CSV files are provided in the project root:
- `sample-portfolio.csv` - Portfolio holdings
- `sample-profit-loss.csv` - P&L statement
- `sample-balance-sheet.csv` - Balance sheet
- `sample-pink-slips.csv` - Trade confirmations

## 🔧 Technical Implementation

### Document Parser (`document_parser_service.py`)

```python
class FinancialDocumentParser:
    def detect_document_type(content: str) -> str:
        # Analyzes keywords to determine document type
        
    def parse_csv(file_content: bytes) -> Tuple[str, Dict]:
        # Returns (document_type, parsed_data)
        
    def parse_profit_loss(content: str) -> Dict:
        # Extracts revenue, expenses, calculates metrics
        
    def parse_balance_sheet(content: str) -> Dict:
        # Extracts assets, liabilities, equity, calculates ratios
        
    def parse_pink_slip(content: str) -> Dict:
        # Parses trades, aggregates by symbol, calculates positions
```

### Key Metrics Calculated

**P&L Metrics:**
- Gross Profit Margin = (Gross Profit / Revenue) × 100
- Net Profit Margin = (Net Income / Revenue) × 100
- Expense Ratio = (Total Expenses / Revenue) × 100
- Operating Margin = (Operating Income / Revenue) × 100

**Balance Sheet Metrics:**
- Current Ratio = Current Assets / Current Liabilities
- Quick Ratio = (Current Assets - Inventory) / Current Liabilities
- Debt-to-Equity = Total Liabilities / Total Equity
- Debt-to-Assets = Total Liabilities / Total Assets
- Working Capital = Current Assets - Current Liabilities

## 🎨 UI Features

### Mobile Component (`PortfolioUpload.tsx`)

**Format Selection Tabs:**
- 4 tabs: Portfolio, P&L, Balance Sheet, Pink Slips
- Each shows relevant sample format
- Horizontal scrollable table for better mobile UX

**Smart Analysis Display:**
- Automatically renders appropriate view based on document type
- Color-coded recommendations (green=positive, red=negative, yellow=caution)
- Scrollable results for large documents

**Upload States:**
- Loading indicator during analysis
- Success/error alerts with meaningful messages
- Clear format instructions

## 📊 API Response Structures

### Portfolio Response
```json
{
  "document_type": "Portfolio",
  "portfolio_summary": {
    "total_value": 150000,
    "total_gain_loss": 25000,
    "item_count": 5
  },
  "holdings": [...]
}
```

### P&L Response
```json
{
  "document_type": "Profit & Loss Statement",
  "data": {...},
  "analysis": {
    "profitability_assessment": "profitable",
    "gross_margin": "60.0%",
    "net_margin": "27.0%",
    "recommendations": [...]
  }
}
```

### Balance Sheet Response
```json
{
  "document_type": "Balance Sheet",
  "data": {...},
  "analysis": {
    "financial_health": "strong",
    "current_ratio": "2.00",
    "debt_to_equity": "1.00",
    "recommendations": [...]
  }
}
```

### Pink Slip Response
```json
{
  "document_type": "Trade Confirmations (Pink Slips)",
  "trades": [...],
  "current_positions": [...],
  "trade_summary": {
    "total_trades": 8,
    "total_invested": 50000,
    "open_positions": 4
  }
}
```

## 🔐 Security Considerations

- All uploads require authentication (Bearer token)
- File type validation (CSV only)
- Content parsing with error handling
- No persistent storage of uploaded files
- User-specific analysis (scoped to current_user.id)

## 🚦 Testing

### Test each document type:

1. **Portfolio:**
   ```bash
   curl -X POST http://localhost:8000/api/insights/upload-financial-document \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "file=@sample-portfolio.csv"
   ```

2. **P&L:**
   ```bash
   curl -X POST http://localhost:8000/api/insights/upload-financial-document \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "file=@sample-profit-loss.csv"
   ```

3. **Balance Sheet:**
   ```bash
   curl -X POST http://localhost:8000/api/insights/upload-financial-document \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "file=@sample-balance-sheet.csv"
   ```

4. **Pink Slips:**
   ```bash
   curl -X POST http://localhost:8000/api/insights/upload-financial-document \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "file=@sample-pink-slips.csv"
   ```

## 📈 Future Enhancements

- [ ] PDF document parsing (OCR)
- [ ] Excel file support (.xlsx)
- [ ] Multi-period P&L comparison
- [ ] Balance sheet trend analysis
- [ ] Tax loss harvesting recommendations (from pink slips)
- [ ] Dividend tracking integration
- [ ] Portfolio rebalancing suggestions
- [ ] Cash flow statement analysis
- [ ] Customizable metrics thresholds

## 🐛 Troubleshooting

**"Could not determine document type"**
- Ensure CSV has clear headers
- Check that content matches one of the supported formats
- Headers are case-insensitive but must contain key identifiers

**"No valid portfolio items found"**
- Verify Symbol column exists
- Check that Quantity and Cost Basis have numeric values
- Remove any empty rows

**"Failed to process document"**
- Check file encoding (must be UTF-8)
- Verify CSV is properly formatted
- Ensure no special characters in numbers (use plain numbers, not formulas)

## 📚 Related Documentation

- [Investment Service Documentation](./backend/app/services/investment_service.py)
- [Technical Analysis Service](./backend/app/services/technical_analysis_service.py)
- [Fundamental Analysis Service](./backend/app/services/fundamental_analysis_service.py)
- [Plaid Integration](./docs/PLAID_INTEGRATION.md)
