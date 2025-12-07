from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional, Any, Dict
from pydantic import BaseModel
from datetime import datetime, timedelta
import csv
import io

# Database imports made optional for Python 3.13 compatibility
try:
    from sqlalchemy.orm import Session
    from ..core.database import get_db
    from ..core.security import verify_token
    from ..models.user import User
    from ..models.transaction import Transaction
    from ..models.bank_account import BankAccount
    from ..services.transaction_service import transaction_service
    from ..api.banks import get_current_user
    DB_AVAILABLE = True
except (ImportError, AssertionError) as e:
    # SQLAlchemy not compatible with Python 3.13 or database not configured
    print(f"Database disabled: {e}")
    Session = Any
    User = Any
    Transaction = Any
    BankAccount = Any
    DB_AVAILABLE = False
    def get_db():
        """Dummy database dependency when DB is unavailable"""
        return None
    def verify_token(token):
        """Dummy token verification when DB is unavailable"""
        return None
    def get_current_user(token=None, db=None):
        """Dummy user when DB is unavailable"""
        return None
    class transaction_service:
        """Dummy transaction service"""
        pass
from ..services.investment_service import investment_service
from ..services.technical_analysis_service import technical_analysis_service
from ..services.fundamental_analysis_service import fundamental_analysis_service
from ..services.market_data_service import market_data_service

router = APIRouter()
security = HTTPBearer()

# Enhanced Pydantic models for advanced investment analysis
class TechnicalAnalysisResponse(BaseModel):
    symbol: str
    current_price: float
    fibonacci_analysis: dict
    support_resistance: dict
    volume_analysis: dict
    candlestick_patterns: List[dict]
    moving_average_analysis: dict
    trend_analysis: dict
    price_targets: dict
    weighted_signals: dict
    investment_recommendation: dict

class FundamentalAnalysisResponse(BaseModel):
    symbol: str
    profitability_metrics: dict
    liquidity_metrics: dict
    efficiency_metrics: dict
    growth_metrics: dict
    profit_loss_analysis: dict
    debt_analysis: dict
    company_health: dict
    growth_assessment: dict
    investment_recommendation: dict

class CombinedInvestmentAnalysisResponse(BaseModel):
    symbol: str
    analysis_timestamp: datetime
    current_price: float
    company_profile: dict
    technical_analysis: dict
    fundamental_analysis: dict
    combined_analysis: dict
    investment_recommendation: dict
    risk_assessment: dict
    portfolio_fit: dict

class PriceTargetResponse(BaseModel):
    primary_target: float
    stop_loss: float
    alternative_targets: List[dict]
    risk_reward_ratio: float
    estimated_time_to_target: dict
    confidence_level: float

# Original endpoints (keeping for backward compatibility)
class SpendingAnalysisResponse(BaseModel):
    period_days: int
    total_spent: float
    transaction_count: int
    avg_daily_spend: float
    avg_transaction_amount: float
    category_breakdown: dict
    top_categories: List[tuple]
    top_merchants: List[tuple]
    daily_spending: dict

class RecurringTransactionResponse(BaseModel):
    merchant: str
    amount: float
    frequency: str
    avg_interval_days: float
    occurrence_count: int
    last_transaction: datetime
    total_spent: float

class InvestmentRecommendationResponse(BaseModel):
    type: str
    priority: str
    title: str
    description: str
    recommended_allocation: Optional[float] = None
    potential_savings: Optional[float] = None
    expected_return: Optional[float] = None
    risk_level: Optional[str] = None

class FinancialProfileResponse(BaseModel):
    user_id: str
    analysis_period_days: int
    spending_analysis: dict
    recurring_transactions: List[dict]
    income_expense_analysis: dict
    savings_potential: dict
    risk_profile: dict
    generated_at: datetime

class TransactionResponse(BaseModel):
    id: str
    amount: float
    description: str
    date: datetime
    category_primary: Optional[str]
    merchant_name: Optional[str]
    is_pending: bool
    is_recurring: bool

# NEW ADVANCED INVESTMENT ANALYSIS ENDPOINTS

@router.get("/technical-analysis/{symbol}", response_model=TechnicalAnalysisResponse)
async def get_technical_analysis(
    symbol: str,
    period: str = Query("1y", description="Analysis period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive technical analysis for a stock symbol"""
    try:
        async with market_data_service:
            # Fetch historical data
            historical_data = await market_data_service.get_historical_data(
                symbol.upper(), period, "1d"
            )
            
            if not historical_data or len(historical_data) < 50:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient historical data for {symbol}"
                )
            
            # Perform technical analysis
            analysis = technical_analysis_service.analyze_security(
                symbol.upper(), historical_data, len(historical_data)
            )
            
            return TechnicalAnalysisResponse(**analysis)
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform technical analysis: {str(e)}"
        )

@router.get("/fundamental-analysis/{symbol}", response_model=FundamentalAnalysisResponse)
async def get_fundamental_analysis(
    symbol: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive fundamental analysis for a stock symbol"""
    try:
        async with market_data_service:
            # Fetch financial statements
            financial_data = await market_data_service.get_financial_statements(symbol.upper())
            company_profile = await market_data_service.get_company_profile(symbol.upper())
            
            if not financial_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"No financial data available for {symbol}"
                )
            
            # Convert to FinancialStatement objects
            from ..services.fundamental_analysis_service import FinancialStatement
            statements = [
                FinancialStatement(
                    period=stmt["period"],
                    revenue=stmt["revenue"],
                    gross_profit=stmt["gross_profit"],
                    operating_income=stmt["operating_income"],
                    net_income=stmt["net_income"],
                    total_assets=stmt["total_assets"],
                    total_debt=stmt["total_debt"],
                    shareholders_equity=stmt["shareholders_equity"],
                    cash_and_equivalents=stmt["cash_and_equivalents"],
                    current_assets=stmt["current_assets"],
                    current_liabilities=stmt["current_liabilities"]
                ) for stmt in financial_data
            ]
            
            # Perform fundamental analysis
            analysis = fundamental_analysis_service.analyze_company_fundamentals(
                symbol.upper(), 
                statements,
                company_profile.industry if company_profile else "general"
            )
            
            return FundamentalAnalysisResponse(**analysis)
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform fundamental analysis: {str(e)}"
        )

@router.get("/combined-investment-analysis/{symbol}", response_model=CombinedInvestmentAnalysisResponse)
async def get_combined_investment_analysis(
    symbol: str,
    period: str = Query("1y", description="Analysis period"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive combined technical and fundamental investment analysis"""
    try:
        # Get user financial profile for personalized recommendations
        user_profile = investment_service.analyze_financial_profile(db, current_user.id, 90)
        
        # Perform combined analysis
        analysis = await investment_service.analyze_investment_opportunity(
            symbol.upper(), user_profile, period
        )
        
        return CombinedInvestmentAnalysisResponse(**analysis)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform combined investment analysis: {str(e)}"
        )

@router.get("/fibonacci-analysis/{symbol}")
async def get_fibonacci_analysis(
    symbol: str,
    period: str = Query("1y", description="Analysis period"),
    current_user: User = Depends(get_current_user)
):
    """Get detailed Fibonacci golden ratio analysis"""
    try:
        async with market_data_service:
            historical_data = await market_data_service.get_historical_data(
                symbol.upper(), period, "1d"
            )
            
            if not historical_data or len(historical_data) < 100:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient data for Fibonacci analysis"
                )
            
            # Extract Fibonacci analysis from technical analysis
            full_analysis = technical_analysis_service.analyze_security(
                symbol.upper(), historical_data, len(historical_data)
            )
            
            fibonacci_data = full_analysis["fibonacci_analysis"]
            current_price = historical_data[-1].close
            
            # Enhanced Fibonacci analysis with golden ratio focus
            enhanced_fibonacci = {
                "symbol": symbol.upper(),
                "current_price": current_price,
                "fibonacci_levels": fibonacci_data["fibonacci_levels"],
                "golden_ratio_analysis": fibonacci_data["golden_ratio_analysis"],
                "swing_high": fibonacci_data["swing_high"],
                "swing_low": fibonacci_data["swing_low"],
                "trend_direction": fibonacci_data["trend_direction"],
                "key_levels": [
                    level for level in fibonacci_data["fibonacci_levels"]
                    if level["level"] == 0.618  # Golden ratio level
                ],
                "price_targets": full_analysis["price_targets"],
                "support_at_fibonacci": [
                    level for level in fibonacci_data["fibonacci_levels"]
                    if level["price"] < current_price and level["support_strength"] > 60
                ],
                "resistance_at_fibonacci": [
                    level for level in fibonacci_data["fibonacci_levels"]
                    if level["price"] > current_price and level["resistance_strength"] > 60
                ]
            }
            
            return enhanced_fibonacci
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform Fibonacci analysis: {str(e)}"
        )

@router.get("/price-targets/{symbol}", response_model=PriceTargetResponse)
async def get_price_targets(
    symbol: str,
    period: str = Query("1y", description="Analysis period"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed price targets with time predictions"""
    try:
        # Get user profile for personalized analysis
        user_profile = investment_service.analyze_financial_profile(db, current_user.id, 90)
        
        # Get combined analysis for enhanced price targets
        combined_analysis = await investment_service.analyze_investment_opportunity(
            symbol.upper(), user_profile, period
        )
        
        price_targets = combined_analysis["investment_recommendation"]
        
        return PriceTargetResponse(
            primary_target=price_targets["target_price"],
            stop_loss=price_targets["stop_loss"],
            alternative_targets=price_targets["alternative_targets"],
            risk_reward_ratio=price_targets.get("risk_reward_ratio", 0),
            estimated_time_to_target=price_targets["time_horizon"],
            confidence_level=price_targets["confidence"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate price targets: {str(e)}"
        )

@router.get("/market-sentiment/{symbol}")
async def get_market_sentiment(
    symbol: str,
    current_user: User = Depends(get_current_user)
):
    """Get market sentiment analysis based on technical indicators"""
    try:
        async with market_data_service:
            historical_data = await market_data_service.get_historical_data(
                symbol.upper(), "3mo", "1d"
            )
            
            if not historical_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"No data available for {symbol}"
                )
            
            # Perform technical analysis
            analysis = technical_analysis_service.analyze_security(
                symbol.upper(), historical_data, len(historical_data)
            )
            
            # Extract sentiment indicators
            weighted_signals = analysis["weighted_signals"]
            volume_analysis = analysis["volume_analysis"]
            trend_analysis = analysis["trend_analysis"]
            candlestick_patterns = analysis["candlestick_patterns"]
            
            # Calculate overall sentiment score
            sentiment_score = weighted_signals["overall_signal"]["strength"]
            sentiment_direction = weighted_signals["overall_signal"]["direction"]
            
            # Recent pattern sentiment
            recent_patterns = [p for p in candlestick_patterns if p["timestamp"] >= datetime.now() - timedelta(days=7)]
            pattern_sentiment = "neutral"
            if recent_patterns:
                bullish_patterns = [p for p in recent_patterns if p["direction"] == "bullish"]
                bearish_patterns = [p for p in recent_patterns if p["direction"] == "bearish"]
                
                if len(bullish_patterns) > len(bearish_patterns):
                    pattern_sentiment = "bullish"
                elif len(bearish_patterns) > len(bullish_patterns):
                    pattern_sentiment = "bearish"
            
            return {
                "symbol": symbol.upper(),
                "overall_sentiment": sentiment_direction,
                "sentiment_score": sentiment_score,
                "confidence": weighted_signals["overall_signal"]["confidence"],
                "volume_sentiment": volume_analysis.volume_trend.value,
                "trend_sentiment": trend_analysis["primary_trend"],
                "pattern_sentiment": pattern_sentiment,
                "key_indicators": {
                    "volume_spike": volume_analysis.volume_spike_ratio > 1.5,
                    "price_volume_correlation": volume_analysis.price_volume_correlation,
                    "trend_strength": trend_analysis["trend_strength"],
                    "recent_patterns": len(recent_patterns)
                },
                "sentiment_breakdown": weighted_signals["individual_signals"]
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze market sentiment: {str(e)}"
        )

# EXISTING ENDPOINTS (keeping for backward compatibility)
class SpendingAnalysisResponse(BaseModel):
    period_days: int
    total_spent: float
    transaction_count: int
    avg_daily_spend: float
    avg_transaction_amount: float
    category_breakdown: dict
    top_categories: List[tuple]
    top_merchants: List[tuple]
    daily_spending: dict

class RecurringTransactionResponse(BaseModel):
    merchant: str
    amount: float
    frequency: str
    avg_interval_days: float
    occurrence_count: int
    last_transaction: datetime
    total_spent: float

class InvestmentRecommendationResponse(BaseModel):
    type: str
    priority: str
    title: str
    description: str
    recommended_allocation: Optional[float] = None
    potential_savings: Optional[float] = None
    expected_return: Optional[float] = None
    risk_level: Optional[str] = None

class FinancialProfileResponse(BaseModel):
    user_id: str
    analysis_period_days: int
    spending_analysis: dict
    recurring_transactions: List[dict]
    income_expense_analysis: dict
    savings_potential: dict
    risk_profile: dict
    generated_at: datetime

class TransactionResponse(BaseModel):
    id: str
    amount: float
    description: str
    date: datetime
    category_primary: Optional[str]
    merchant_name: Optional[str]
    is_pending: bool
    is_recurring: bool

@router.get("/spending-analysis", response_model=SpendingAnalysisResponse)
async def get_spending_analysis(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive spending analysis for the user"""
    try:
        analysis = transaction_service.get_spending_analysis(db, current_user.id, days)
        return SpendingAnalysisResponse(**analysis)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate spending analysis: {str(e)}"
        )

@router.get("/recurring-transactions", response_model=List[RecurringTransactionResponse])
async def get_recurring_transactions(
    days: int = Query(90, ge=30, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recurring transactions and subscriptions"""
    try:
        recurring = transaction_service.detect_recurring_transactions(db, current_user.id, days)
        return [RecurringTransactionResponse(**tx) for tx in recurring]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to detect recurring transactions: {str(e)}"
        )

@router.get("/financial-profile", response_model=FinancialProfileResponse)
async def get_financial_profile(
    days: int = Query(90, ge=30, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive financial profile for investment recommendations"""
    try:
        profile = investment_service.analyze_financial_profile(db, current_user.id, days)
        return FinancialProfileResponse(**profile)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate financial profile: {str(e)}"
        )

@router.get("/investment-recommendations")
async def get_investment_recommendations(
    days: int = Query(90, ge=30, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized investment recommendations"""
    try:
        # Get financial profile
        financial_profile = investment_service.analyze_financial_profile(db, current_user.id, days)
        
        # Generate recommendations
        recommendations = investment_service.generate_investment_recommendations(financial_profile)
        
        return {
            "financial_profile_summary": {
                "monthly_income": financial_profile["income_expense_analysis"]["monthly_income"],
                "monthly_expenses": financial_profile["income_expense_analysis"]["monthly_expenses"],
                "net_monthly": financial_profile["income_expense_analysis"]["net_monthly"],
                "savings_potential": financial_profile["savings_potential"]["total_monthly_potential"],
                "risk_level": financial_profile["risk_profile"]["risk_level"]
            },
            "recommendations": recommendations["recommendations"],
            "summary": recommendations["summary"],
            "priority_actions": recommendations["priority_actions"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate investment recommendations: {str(e)}"
        )

@router.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of transactions"),
    offset: int = Query(0, ge=0, description="Number of transactions to skip"),
    category: Optional[str] = Query(None, description="Filter by category"),
    merchant: Optional[str] = Query(None, description="Filter by merchant"),
    min_amount: Optional[float] = Query(None, description="Minimum transaction amount"),
    max_amount: Optional[float] = Query(None, description="Maximum transaction amount"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get filtered list of transactions"""
    try:
        # Build query
        query = db.query(Transaction).join(BankAccount).filter(
            BankAccount.user_id == current_user.id
        )
        
        # Apply filters
        if category:
            query = query.filter(Transaction.category_primary.ilike(f"%{category}%"))
        
        if merchant:
            query = query.filter(Transaction.merchant_name.ilike(f"%{merchant}%"))
        
        if min_amount is not None:
            query = query.filter(Transaction.amount >= min_amount)
        
        if max_amount is not None:
            query = query.filter(Transaction.amount <= max_amount)
        
        # Order by date (newest first) and apply pagination
        transactions = query.order_by(Transaction.date.desc()).offset(offset).limit(limit).all()
        
        # Convert to response format
        transaction_responses = []
        for tx in transactions:
            transaction_responses.append(TransactionResponse(
                id=tx.id,
                amount=tx.amount,
                description=tx.description,
                date=tx.date,
                category_primary=tx.category_primary,
                merchant_name=tx.merchant_name,
                is_pending=tx.is_pending,
                is_recurring=tx.is_recurring
            ))
        
        return transaction_responses
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve transactions: {str(e)}"
        )

@router.get("/categories")
async def get_spending_categories(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get spending breakdown by categories"""
    try:
        analysis = transaction_service.get_spending_analysis(db, current_user.id, days)
        
        categories = []
        total_spending = sum(analysis["category_breakdown"].values())
        
        for category, amount in analysis["category_breakdown"].items():
            percentage = (amount / total_spending * 100) if total_spending > 0 else 0
            categories.append({
                "category": category,
                "amount": amount,
                "percentage": round(percentage, 1),
                "transaction_count": 0  # Could be enhanced to count transactions per category
            })
        
        # Sort by amount descending
        categories.sort(key=lambda x: x["amount"], reverse=True)
        
        return {
            "categories": categories,
            "total_spending": total_spending,
            "analysis_period_days": days
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get category breakdown: {str(e)}"
        )

@router.get("/merchants")
async def get_top_merchants(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    limit: int = Query(10, ge=1, le=50, description="Number of top merchants to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get top merchants by spending amount"""
    try:
        analysis = transaction_service.get_spending_analysis(db, current_user.id, days)
        
        merchants = []
        for merchant, amount in analysis["top_merchants"][:limit]:
            merchants.append({
                "merchant": merchant,
                "amount": amount,
                "percentage": (amount / analysis["total_spent"] * 100) if analysis["total_spent"] > 0 else 0
            })
        
        return {
            "merchants": merchants,
            "analysis_period_days": days
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get merchant analysis: {str(e)}"
        )

@router.get("/savings-opportunities")
async def get_savings_opportunities(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific savings opportunities and optimization suggestions"""
    try:
        # Get financial profile
        financial_profile = investment_service.analyze_financial_profile(db, current_user.id, 90)
        
        # Get recurring transactions for subscription analysis
        recurring = transaction_service.detect_recurring_transactions(db, current_user.id, 90)
        
        opportunities = []
        
        # Subscription optimization
        subscriptions = [tx for tx in recurring if "subscription" in tx["merchant"].lower() 
                        or any(keyword in tx["merchant"].lower() for keyword in 
                              ["netflix", "spotify", "gym", "streaming"])]
        
        if subscriptions:
            total_subscription_cost = sum(tx["amount"] for tx in subscriptions)
            opportunities.append({
                "type": "subscription_optimization",
                "title": "Optimize Subscriptions",
                "description": f"You spend ${total_subscription_cost:.2f}/month on subscriptions",
                "potential_monthly_savings": total_subscription_cost * 0.3,
                "action_items": [
                    f"Review {len(subscriptions)} active subscriptions",
                    "Cancel unused services",
                    "Downgrade to cheaper plans",
                    "Share family plans where possible"
                ],
                "subscriptions": subscriptions
            })
        
        # High spending categories
        top_categories = financial_profile["spending_analysis"]["top_categories"]
        for category, amount in top_categories[:2]:
            monthly_amount = amount / (financial_profile["analysis_period_days"] / 30)
            if monthly_amount > 300:  # Only suggest for categories > $300/month
                opportunities.append({
                    "type": "category_optimization",
                    "title": f"Reduce {category} Spending",
                    "description": f"High spending in {category}: ${monthly_amount:.0f}/month",
                    "potential_monthly_savings": monthly_amount * 0.15,
                    "suggestions": _get_category_optimization_tips(category)
                })
        
        return {
            "opportunities": opportunities,
            "total_potential_monthly_savings": sum(opp.get("potential_monthly_savings", 0) for opp in opportunities),
            "total_potential_annual_savings": sum(opp.get("potential_monthly_savings", 0) for opp in opportunities) * 12
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to identify savings opportunities: {str(e)}"
        )

def _get_category_optimization_tips(category: str) -> List[str]:
    """Get optimization tips for specific spending categories"""
    tips = {
        "Food and Drink": [
            "Plan meals and create shopping lists",
            "Cook more meals at home",
            "Use grocery store apps for coupons",
            "Buy generic brands",
            "Limit dining out to special occasions"
        ],
        "Transportation": [
            "Use public transportation when possible",
            "Carpool or use rideshare services",
            "Combine errands into single trips",
            "Consider a gas rewards credit card",
            "Maintain your vehicle for better fuel efficiency"
        ],
        "Entertainment": [
            "Look for free local events and activities",
            "Use library resources for books and movies",
            "Share streaming service subscriptions",
            "Attend matinee showings for lower prices"
        ],
        "Shops": [
            "Use price comparison apps before purchasing",
            "Wait for sales and clearance events",
            "Use cashback and coupon apps",
            "Consider buying used or refurbished items"
        ]
    }
    
    return tips.get(category, [
        "Track spending in this category",
        "Set a monthly budget limit",
        "Look for alternatives or better deals"
    ])

@router.post("/upload-financial-document")
async def upload_financial_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload and analyze financial documents (CSV or HTML/XBRL):
    Supports:
    - Portfolio (Symbol, Quantity, Cost Basis)
    - Profit & Loss Statement (Revenue, Expenses, Net Income)
    - Balance Sheet (Assets, Liabilities, Equity)
    - Pink Slips / Trade Confirmations (Symbol, Shares, Price, Date, Type)
    - Multi-period financial filings (auto-detected -> multi_financials)
    """
    allowed = ('.csv', '.htm', '.html', '.xbrl', '.xml', '.txt')
    if not file.filename.lower().endswith(allowed):
        raise HTTPException(status_code=400, detail=f"Invalid file format. Supported: {', '.join(allowed)}")

    try:
        from ..services.document_parser_service import document_parser
        
        content = await file.read()
        
        # Parse document and detect type
        doc_type, parsed_data = document_parser.parse_csv(content, filename=file.filename)
        
        # Safe user profile acquisition (offline or missing method)
        import logging
        logger = logging.getLogger(__name__)
        try:
            if current_user and hasattr(investment_service, 'analyze_financial_profile'):
                user_profile = investment_service.analyze_financial_profile(db, getattr(current_user, 'id', 'anonymous'), 90)
            else:
                user_profile = {}
        except Exception as _e:
            logger.warning(f"Could not derive user profile: {_e}")
            user_profile = {}
        
        # Handle different document types
        if doc_type == 'multi_financials':
            inc = parsed_data.get('income_statement', {})
            periods = inc.get('periods', {})
            metrics = inc.get('metrics', {})
            summary = []
            for yr, m in metrics.items():
                summary.append({
                    'year': yr,
                    'revenue': m.get('total_revenue', 0),
                    'expenses': m.get('total_expenses', 0),
                    'gross_profit_margin': m.get('gross_profit_margin', 0),
                    'net_profit_margin': m.get('net_profit_margin', 0),
                    'expense_ratio': m.get('expense_ratio', 0),
                    'profitable': m.get('profitable', False),
                    'period_type': periods.get(yr, {}).get('period_type', 'annual')
                })
            return {
                'document_type': 'Multi-period Financials',
                'summary_periods': summary,
                'income_statement': inc,
                'balance_sheet': parsed_data.get('balance_sheet', {}),
                'cash_flow_statement': parsed_data.get('cash_flow_statement', {}),
                'raw': parsed_data
            }
        elif doc_type == 'portfolio':
            return await _analyze_portfolio(parsed_data, user_profile)
        
        elif doc_type == 'profit_loss':
            return {
                "document_type": "Profit & Loss Statement",
                "data": parsed_data,
                "analysis": {
                    "profitability_assessment": parsed_data['metrics']['profitability'],
                    "gross_margin": f"{parsed_data['metrics']['gross_profit_margin']:.1f}%",
                    "net_margin": f"{parsed_data['metrics']['net_profit_margin']:.1f}%",
                    "expense_ratio": f"{parsed_data['metrics']['expense_ratio']:.1f}%",
                    "recommendations": _generate_pl_recommendations(parsed_data)
                },
                "summary": {
                    "total_revenue": parsed_data['metrics']['total_revenue'],
                    "total_expenses": parsed_data['metrics']['total_expenses'],
                    "net_income": parsed_data['net_income']
                }
            }
        
        elif doc_type == 'balance_sheet':
            return {
                "document_type": "Balance Sheet",
                "data": parsed_data,
                "analysis": {
                    "financial_health": parsed_data['metrics']['financial_health'],
                    "current_ratio": f"{parsed_data['metrics']['current_ratio']:.2f}",
                    "debt_to_equity": f"{parsed_data['metrics']['debt_to_equity']:.2f}",
                    "working_capital": parsed_data['metrics']['working_capital'],
                    "recommendations": _generate_bs_recommendations(parsed_data)
                },
                "summary": {
                    "total_assets": parsed_data['assets']['total'],
                    "total_liabilities": parsed_data['liabilities']['total'],
                    "total_equity": sum(parsed_data['equity'].values())
                }
            }
        
        elif doc_type == 'pink_slip':
            # Analyze trades and current positions
            positions = list(parsed_data['portfolio_summary'].values())
            
            # Get market analysis for current positions
            analysis_results = []
            for position in positions:
                try:
                    analysis = await investment_service.analyze_investment_opportunity(
                        position['symbol'], user_profile, "1y"
                    )
                    
                    current_price = analysis['current_price']
                    current_value = current_price * position['shares']
                    cost_basis = position['avg_price']
                    cost_value = cost_basis * position['shares']
                    gain_loss = current_value - cost_value
                    gain_loss_percent = (gain_loss / cost_value * 100) if cost_value > 0 else 0
                    
                    analysis_results.append({
                        "symbol": position['symbol'],
                        "quantity": position['shares'],
                        "avg_cost_basis": cost_basis,
                        "current_price": current_price,
                        "current_value": current_value,
                        "gain_loss": gain_loss,
                        "gain_loss_percent": gain_loss_percent,
                        "recommendation": analysis['investment_recommendation']['recommendation'],
                        "confidence": analysis['investment_recommendation']['confidence'],
                        "target_price": analysis['investment_recommendation']['target_price']
                    })
                except Exception as e:
                    logger.error(f"Error analyzing {position['symbol']}: {str(e)}")
                    continue
            
            return {
                "document_type": "Trade Confirmations (Pink Slips)",
                "trades": parsed_data['trades'],
                "current_positions": analysis_results,
                "trade_summary": {
                    "total_trades": len(parsed_data['trades']),
                    "total_invested": parsed_data['total_invested'],
                    "total_proceeds": parsed_data['total_proceeds'],
                    "open_positions": len(analysis_results)
                },
                "portfolio_value": {
                    "total_value": sum(item['current_value'] for item in analysis_results),
                    "total_gain_loss": sum(item['gain_loss'] for item in analysis_results),
                    "total_gain_loss_percent": (sum(item['gain_loss'] for item in analysis_results) / 
                                                sum(item['quantity'] * item['avg_cost_basis'] for item in analysis_results) * 100)
                                               if analysis_results else 0
                }
            }
        
        else:
            raise HTTPException(status_code=400, detail="Could not determine document type")

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")


async def _analyze_portfolio(portfolio_items: List[Dict], user_profile: Dict) -> Dict:
    """Analyze simple portfolio"""
    analysis_results = []
    
    for item in portfolio_items:
        try:
            analysis = await investment_service.analyze_investment_opportunity(
                item['symbol'], user_profile, "1y"
            )
            
            current_price = analysis['current_price']
            current_value = current_price * item['quantity']
            cost_value = item['cost_basis'] * item['quantity']
            gain_loss = current_value - cost_value
            gain_loss_percent = (gain_loss / cost_value * 100) if cost_value > 0 else 0
            
            analysis_results.append({
                "symbol": item['symbol'],
                "quantity": item['quantity'],
                "cost_basis": item['cost_basis'],
                "current_price": current_price,
                "current_value": current_value,
                "gain_loss": gain_loss,
                "gain_loss_percent": gain_loss_percent,
                "recommendation": analysis['investment_recommendation']['recommendation'],
                "confidence": analysis['investment_recommendation']['confidence'],
                "target_price": analysis['investment_recommendation']['target_price']
            })
        except Exception as e:
            logger.error(f"Error analyzing {item['symbol']}: {str(e)}")
            continue
    
    return {
        "document_type": "Portfolio",
        "portfolio_summary": {
            "total_value": sum(item['current_value'] for item in analysis_results),
            "total_gain_loss": sum(item['gain_loss'] for item in analysis_results),
            "item_count": len(analysis_results)
        },
        "holdings": analysis_results
    }


def _generate_pl_recommendations(pl_data: Dict) -> List[str]:
    """Generate recommendations based on P&L analysis"""
    recommendations = []
    metrics = pl_data['metrics']
    
    if metrics['net_profit_margin'] < 5:
        recommendations.append("⚠️ Low profit margin - Focus on cost reduction and revenue optimization")
    elif metrics['net_profit_margin'] > 20:
        recommendations.append("✅ Strong profit margins - Consider reinvesting profits for growth")
    
    if metrics['expense_ratio'] > 80:
        recommendations.append("💸 High expense ratio - Review operational efficiency and cost structure")
    
    if metrics['gross_profit_margin'] < 30:
        recommendations.append("📊 Low gross margins - Consider pricing strategy review or supplier negotiations")
    
    if pl_data['net_income'] > 0:
        recommendations.append("💰 Profitable operations - Maintain current strategies and explore expansion")
    else:
        recommendations.append("🔴 Operating at a loss - Urgent review of revenue streams and cost controls needed")
    
    return recommendations if recommendations else ["Continue monitoring financial performance"]


def _generate_bs_recommendations(bs_data: Dict) -> List[str]:
    """Generate recommendations based on balance sheet analysis"""
    recommendations = []
    metrics = bs_data['metrics']
    
    if metrics['current_ratio'] < 1:
        recommendations.append("⚠️ Liquidity concern - Current assets below current liabilities")
    elif metrics['current_ratio'] > 2:
        recommendations.append("✅ Strong liquidity position - Good short-term financial health")
    
    if metrics['debt_to_equity'] > 2:
        recommendations.append("💳 High leverage - Consider debt reduction strategies")
    elif metrics['debt_to_equity'] < 0.5:
        recommendations.append("💪 Conservative capital structure - Could leverage debt for growth if needed")
    
    if metrics['working_capital'] < 0:
        recommendations.append("🚨 Negative working capital - Immediate attention to cash flow management required")
    else:
        recommendations.append("✅ Positive working capital - Good operational buffer")
    
    if metrics['debt_to_assets'] > 0.6:
        recommendations.append("📉 High debt relative to assets - Focus on debt paydown")
    
    return recommendations if recommendations else ["Maintain current financial structure"]


@router.post("/screen-companies")
async def screen_companies(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    NEW: Screen companies from uploaded file for fundamental quality.
    
    Supports:
    - CSV/Excel files (traditional format)
    - XBRL files (SEC EDGAR format)
    - XML files (SEC filings)
    - HTML files (SEC 10-K, 10-Q, 8-K)
    - JSON files (modern SEC API format)
    
    Analyzes:
    - Predictability (QoQ and QoY revenue consistency)
    - 10-K Report Depth (expanding vs contracting disclosure)
    - Overall fundamental quality
    
    Returns ranked list of companies by quality score.
    """
    # Support CSV, Excel, and SEC EDGAR file formats
    allowed_extensions = ('.csv', '.xlsx', '.xls', '.xml', '.xbrl', '.htm', '.html', '.txt', '.json')
    if not file.filename.endswith(allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file format. Supported formats: {', '.join(allowed_extensions)}"
        )
    
    try:
        import pandas as pd
        import logging
        from app.services.sec_edgar_parser import sec_edgar_parser
        
        logger = logging.getLogger(__name__)
        
        # Read file content
        content = await file.read()
        
        if not content:
            raise HTTPException(
                status_code=400,
                detail="Empty file uploaded"
            )
        
        # Determine file type and parse accordingly
        file_data = None
        
        # Check if this is a SEC EDGAR filing
        if file.filename.endswith(('.xml', '.xbrl', '.htm', '.html', '.txt', '.json')):
            logger.info(f"Parsing SEC EDGAR file: {file.filename}")
            
            # Use SEC EDGAR parser
            parsed_data = sec_edgar_parser.parse_file(content, file.filename)
            
            if not parsed_data.get('parsed_successfully', False):
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to parse SEC filing: {parsed_data.get('error', 'Unknown error')}"
                )
            
            file_data = parsed_data
            
        # Traditional CSV/Excel files
        else:
            try:
                if file.filename.endswith('.csv'):
                    df = pd.read_csv(io.BytesIO(content))
                else:
                    # For Excel files, openpyxl is required
                    df = pd.read_excel(io.BytesIO(content), engine='openpyxl')
                    
                # Check if DataFrame is empty
                if df.empty:
                    raise HTTPException(
                        status_code=400,
                        detail="File contains no data rows"
                    )
                    
                file_data = df
                
            except pd.errors.EmptyDataError:
                raise HTTPException(
                    status_code=400,
                    detail="File is empty or contains no data"
                )
            except pd.errors.ParserError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to parse file: {str(e)}. Please ensure file is properly formatted."
                )
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to read file: {str(e)}. Ensure file is a valid CSV or Excel file."
                )
        
        # Screen companies using fundamental analysis service
        screening_results = fundamental_analysis_service.screen_companies_from_file(
            file_data=file_data,
            file_type="auto"  # Auto-detect file type
        )
        
        if "error" in screening_results:
            raise HTTPException(
                status_code=400,
                detail=screening_results["error"]
            )
        
        return {
            "status": "success",
            "file_name": file.filename,
            "file_type": screening_results.get("file_type", "unknown"),
            "screening_results": screening_results,
            "message": f"Successfully screened {screening_results.get('total_companies', 0)} companies"
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ImportError as e:
        logger.error(f"Missing required library: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Server configuration error: required data analysis libraries not installed"
        )
    except Exception as e:
        logger.error(f"Error screening companies: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to screen companies: {str(e)}"
        )


@router.post("/analyze-financials")
async def analyze_financials(
    file: UploadFile = File(...),
    chart_data_file: Optional[UploadFile] = File(None),
    current_user: Optional[Any] = Depends(get_current_user) if DB_AVAILABLE else None,
    db: Optional[Any] = Depends(get_db) if DB_AVAILABLE else None
):
    """
    NEW: Comprehensive Financial Analysis Tool
    
    Accepts financial data in table formats from:
    - Barchart (exports, custom tables)
    - Morningstar (stock data tables)
    - CSV/Excel with financial metrics
    
    Optional second file (chart_data_file):
    - Historical price data (Date, Close, Volume)
    - Quarterly financial data (Quarter, Revenue, Earnings, Cash Flow)
    - Technical indicators (RSI, MACD, Moving Averages)
    - Provides enhanced analysis when available
    
    Analyzes ALL quality indicators:
    - Predictability (QoQ, QoY revenue consistency)
    - 10-K Report Depth (disclosure quality & expansion)
    - Profitability Metrics (margins, ROE, ROA, ROIC)
    - Liquidity Metrics (current, quick, cash ratios)
    - Efficiency Metrics (turnover ratios)
    - Growth Metrics (revenue, earnings, asset growth)
    - Debt Structure (leverage ratios, coverage)
    
    Returns:
    - Sorted list from strongest to weakest prediction
    - Buy/Sell/Hold recommendations with price points
    - Confidence scores for each recommendation
    - Detailed analysis for each company
    """
    # Support CSV, Excel, and SEC EDGAR file formats
    allowed_extensions = ('.csv', '.xlsx', '.xls', '.xml', '.xbrl', '.htm', '.html', '.txt', '.json')
    if not file.filename.endswith(allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file format. Supported formats: {', '.join(allowed_extensions)}"
        )
    
    try:
        import pandas as pd
        import logging
        from app.services.sec_edgar_parser import sec_edgar_parser
        
        logger = logging.getLogger(__name__)
        
        # Read file content
        content = await file.read()
        
        if not content:
            raise HTTPException(
                status_code=400,
                detail="Empty file uploaded"
            )
        
        # Determine file type and parse accordingly
        file_data = None
        
        # Check if this is a SEC EDGAR filing
        if file.filename.endswith(('.xml', '.xbrl', '.htm', '.html', '.txt', '.json')):
            logger.info(f"Parsing SEC EDGAR file for financial analysis: {file.filename}")
            
            # Use SEC EDGAR parser
            parsed_data = sec_edgar_parser.parse_file(content, file.filename)
            
            if not parsed_data.get('parsed_successfully', False):
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to parse SEC filing: {parsed_data.get('error', 'Unknown error')}"
                )
            
            file_data = parsed_data
            
        # Traditional CSV/Excel files (Barchart, Morningstar formats)
        else:
            try:
                if file.filename.endswith('.csv'):
                    df = pd.read_csv(io.BytesIO(content))
                else:
                    # For Excel files, openpyxl is required
                    df = pd.read_excel(io.BytesIO(content), engine='openpyxl')
                    
                # Check if DataFrame is empty
                if df.empty:
                    raise HTTPException(
                        status_code=400,
                        detail="File contains no data rows"
                    )
                    
                file_data = df
                
            except pd.errors.EmptyDataError:
                raise HTTPException(
                    status_code=400,
                    detail="File is empty or contains no data"
                )
            except pd.errors.ParserError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to parse file: {str(e)}. Please ensure file is properly formatted."
                )
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to read file: {str(e)}. Ensure file is a valid CSV or Excel file."
                )
        
        # Parse optional chart data file if provided
        chart_data = None
        if chart_data_file and chart_data_file.filename:
            logger.info(f"Processing optional chart data file: {chart_data_file.filename}")
            try:
                chart_content = await chart_data_file.read()
                if chart_content:
                    if chart_data_file.filename.endswith('.csv'):
                        chart_data = pd.read_csv(io.BytesIO(chart_content))
                    else:
                        chart_data = pd.read_excel(io.BytesIO(chart_content), engine='openpyxl')
                    logger.info(f"Successfully parsed chart data: {len(chart_data)} rows")
            except Exception as e:
                logger.warning(f"Failed to parse chart data file: {str(e)}. Continuing without it.")
                chart_data = None
        
        # Perform comprehensive financial analysis
        user_id = current_user.id if current_user and hasattr(current_user, 'id') else 'anonymous'
        logger.info(f"Performing comprehensive financial analysis for user {user_id}")
        
        analysis_results = fundamental_analysis_service.screen_companies_from_file(
            file_data=file_data,
            file_type="auto"  # Auto-detect format
        )
        
        if "error" in analysis_results:
            raise HTTPException(
                status_code=400,
                detail=analysis_results["error"]
            )
        
        # Enhance results with buy/sell price points (pass chart_data for enhanced analysis)
        enhanced_results = await _add_buy_sell_points(analysis_results, db, chart_data)
        
        # Add metadata about chart data usage
        chart_data_status = "included" if chart_data is not None else "not_provided"
        
        return {
            "success": True,
            "analysis_type": "comprehensive_financial",
            "file_name": file.filename,
            "chart_data_file": chart_data_file.filename if chart_data_file else None,
            "chart_data_status": chart_data_status,
            "analysis_results": enhanced_results,
            "message": f"Successfully analyzed {enhanced_results.get('total_companies', 0)} companies" + 
                      (f" with enhanced chart data" if chart_data is not None else "")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing financials: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze financials: {str(e)}"
        )


async def _add_buy_sell_points(
    analysis_results: Dict[str, Any], 
    db: Session,
    chart_data: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Enhance analysis results with buy/sell price points using technical analysis.
    
    Args:
        analysis_results: Results from fundamental analysis
        db: Database session
        chart_data: Optional DataFrame with historical price/volume data
    """
    import pandas as pd
    enhanced_companies = []
    
    # Pre-process chart data if provided
    chart_data_by_ticker = {}
    if chart_data is not None and isinstance(chart_data, pd.DataFrame):
        # Try to identify ticker column
        ticker_cols = ['ticker', 'symbol', 'Ticker', 'Symbol', 'TICKER', 'SYMBOL']
        ticker_col = next((col for col in ticker_cols if col in chart_data.columns), None)
        
        if ticker_col:
            for ticker in chart_data[ticker_col].unique():
                ticker_data = chart_data[chart_data[ticker_col] == ticker]
                chart_data_by_ticker[str(ticker).upper()] = ticker_data
    
    for company in analysis_results.get("companies", []):
        ticker = company.get("ticker", "")
        
        try:
            # Check if we have chart data for this ticker
            ticker_chart_data = chart_data_by_ticker.get(ticker.upper())
            historical_data = None
            
            if ticker_chart_data is not None and not ticker_chart_data.empty:
                # Use provided chart data - convert to PriceData format
                try:
                    from app.services.technical_analysis_service import PriceData
                    from datetime import datetime
                    
                    price_data_list = []
                    date_cols = ['date', 'Date', 'DATE', 'timestamp', 'Timestamp']
                    date_col = next((col for col in date_cols if col in ticker_chart_data.columns), None)
                    
                    close_cols = ['close', 'Close', 'CLOSE', 'price', 'Price']
                    close_col = next((col for col in close_cols if col in ticker_chart_data.columns), None)
                    
                    volume_cols = ['volume', 'Volume', 'VOLUME']
                    volume_col = next((col for col in volume_cols if col in ticker_chart_data.columns), None)
                    
                    if date_col and close_col:
                        for _, row in ticker_chart_data.iterrows():
                            try:
                                timestamp = pd.to_datetime(row[date_col])
                                close = float(row[close_col])
                                volume = int(row[volume_col]) if volume_col and pd.notna(row[volume_col]) else 0
                                
                                price_data = PriceData(
                                    timestamp=timestamp,
                                    open=close,  # Use close as open if not available
                                    high=close,
                                    low=close,
                                    close=close,
                                    volume=volume
                                )
                                price_data_list.append(price_data)
                            except Exception:
                                continue
                        
                        if price_data_list:
                            historical_data = price_data_list
                            logger.info(f"Using provided chart data for {ticker}: {len(historical_data)} data points")
                except Exception as e:
                    logger.warning(f"Failed to convert chart data for {ticker}: {str(e)}")
            
            # Fallback to fetching from market data service if no chart data provided
            if not historical_data:
                async with market_data_service:
                    # Get recent price data (last 90 days for good technical analysis)
                    historical_data = await market_data_service.get_historical_data(
                        ticker, "3mo", "1d"
                    )
                
                if historical_data and len(historical_data) >= 20:
                    # Get current price
                    current_price = historical_data[-1].close
                    
                    # Perform technical analysis to get support/resistance levels
                    technical_analysis = technical_analysis_service.analyze_security(
                        ticker, historical_data, len(historical_data)
                    )
                    
                    # Extract support/resistance levels
                    support_resistance = technical_analysis.get("support_resistance", {})
                    fibonacci_levels = technical_analysis.get("fibonacci_analysis", {}).get("levels", {})
                    
                    # Calculate buy/sell points based on fundamental score and technical levels
                    recommendation = company.get("recommendation", {})
                    action = recommendation.get("action", "HOLD")
                    
                    buy_point = None
                    sell_point = None
                    target_price = None
                    stop_loss = None
                    
                    if action in ["STRONG BUY", "BUY"]:
                        # Buy point: Use support level or slight pullback from current
                        support_level = support_resistance.get("support_levels", [None])[0]
                        buy_point = support_level if support_level else round(current_price * 0.97, 2)
                        
                        # Sell/Target: Use resistance or quality-based upside
                        resistance_level = support_resistance.get("resistance_levels", [None])[0]
                        quality_score = company.get("overall_score", 70)
                        upside_multiplier = 1.15 if quality_score >= 80 else 1.10
                        target_price = resistance_level if resistance_level else round(current_price * upside_multiplier, 2)
                        
                        # Stop loss: Below support
                        stop_loss = round(buy_point * 0.92, 2) if buy_point else round(current_price * 0.90, 2)
                        
                    elif action == "HOLD":
                        # Hold: Monitor levels
                        support_level = support_resistance.get("support_levels", [None])[0]
                        resistance_level = support_resistance.get("resistance_levels", [None])[0]
                        buy_point = support_level if support_level else round(current_price * 0.95, 2)
                        sell_point = resistance_level if resistance_level else round(current_price * 1.08, 2)
                        stop_loss = round(current_price * 0.88, 2)
                        
                    elif action in ["AVOID", "WATCH"]:
                        # Sell recommendation
                        resistance_level = support_resistance.get("resistance_levels", [None])[0]
                        sell_point = resistance_level if resistance_level else current_price
                        buy_point = round(current_price * 0.85, 2)  # Only buy on significant drop
                    
                    # Add price points to company data
                    company["price_analysis"] = {
                        "current_price": round(current_price, 2),
                        "buy_point": buy_point,
                        "sell_point": sell_point,
                        "target_price": target_price,
                        "stop_loss": stop_loss,
                        "support_levels": support_resistance.get("support_levels", [])[:3],
                        "resistance_levels": support_resistance.get("resistance_levels", [])[:3],
                        "fibonacci_levels": {
                            k: round(v, 2) for k, v in fibonacci_levels.items() if isinstance(v, (int, float))
                        } if fibonacci_levels else {}
                    }
                    
                    # Calculate potential return
                    if action in ["STRONG BUY", "BUY"] and buy_point and target_price:
                        potential_return = ((target_price - buy_point) / buy_point) * 100
                        company["price_analysis"]["potential_return"] = round(potential_return, 2)
                    
                else:
                    company["price_analysis"] = {
                        "error": "Insufficient price data for technical analysis"
                    }
                    
        except Exception as e:
            logger.warning(f"Could not fetch price data for {ticker}: {str(e)}")
            company["price_analysis"] = {
                "error": f"Unable to fetch current price data: {str(e)}"
            }
        
        enhanced_companies.append(company)
    
    analysis_results["companies"] = enhanced_companies
    return analysis_results


@router.get("/portfolio-chart-data/{symbol}")
async def get_portfolio_chart_data(
    symbol: str,
    period: str = Query("1y", description="Data period (1mo, 3mo, 6mo, 1y, 2y, 5y)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive portfolio chart data with:
    - Historical price data
    - 50/200/250 day moving averages
    - Fibonacci golden ratio levels
    - Enhanced bullish confidence metrics
    - Volume analysis
    """
    try:
        async with market_data_service:
            # Fetch historical data (need enough for 250-day MA)
            historical_data = await market_data_service.get_historical_data(
                symbol.upper(), period, "1d"
            )
            
            if not historical_data or len(historical_data) < 50:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient historical data for {symbol}"
                )
            
            # Calculate moving averages
            ma_data = _calculate_long_term_moving_averages(historical_data)
            
            # Perform full technical analysis
            technical_analysis = technical_analysis_service.analyze_security(
                symbol.upper(), historical_data, len(historical_data)
            )
            
            # Enhanced Fibonacci analysis with golden ratio focus
            fibonacci_data = technical_analysis["fibonacci_analysis"]
            fibonacci_confidence = _calculate_fibonacci_confidence(
                historical_data, fibonacci_data
            )
            
            # Get candlestick patterns and temporal analysis
            candlestick_patterns = technical_analysis.get("candlestick_patterns", [])
            pattern_temporal = technical_analysis.get("pattern_temporal_analysis", {})
            
            # Use adaptive pattern score if available, otherwise calculate base score
            adaptive_score = pattern_temporal.get("adaptive_score", {})
            candlestick_score_override = adaptive_score.get("final_adaptive_score")
            
            # Get insider/calculus analysis
            insider_calculus = technical_analysis.get("insider_calculus_analysis", {})
            insider_influence = insider_calculus.get("insider_influence", {})
            
            # Calculate enhanced bullish confidence with candlestick analysis and insider influence
            bullish_confidence = _calculate_enhanced_bullish_confidence(
                ma_data, fibonacci_confidence, technical_analysis, candlestick_patterns,
                candlestick_score_override, insider_influence
            )
            
            # Prepare chart data points
            chart_data = []
            for i, data_point in enumerate(historical_data):
                point = {
                    "date": data_point.timestamp.isoformat() if hasattr(data_point.timestamp, 'isoformat') else str(data_point.timestamp),
                    "price": data_point.close,
                    "volume": data_point.volume,
                    "ma_50": ma_data["ma_50"][i] if i < len(ma_data["ma_50"]) else None,
                    "ma_200": ma_data["ma_200"][i] if i < len(ma_data["ma_200"]) else None,
                    "ma_250": ma_data["ma_250"][i] if i < len(ma_data["ma_250"]) else None
                }
                chart_data.append(point)
            
            return {
                "symbol": symbol.upper(),
                "period": period,
                "current_price": historical_data[-1].close,
                "chart_data": chart_data,
                "moving_averages": {
                    "ma_50": {
                        "current": ma_data["ma_50"][-1] if ma_data["ma_50"] else None,
                        "trend": ma_data["ma_50_trend"],
                        "slope": ma_data["ma_50_slope"]
                    },
                    "ma_200": {
                        "current": ma_data["ma_200"][-1] if ma_data["ma_200"] else None,
                        "trend": ma_data["ma_200_trend"],
                        "slope": ma_data["ma_200_slope"]
                    },
                    "ma_250": {
                        "current": ma_data["ma_250"][-1] if ma_data["ma_250"] else None,
                        "trend": ma_data["ma_250_trend"],
                        "slope": ma_data["ma_250_slope"],
                        "distance_from_price": ma_data["distance_from_250ma"]
                    },
                    "golden_cross": ma_data["golden_cross"],
                    "death_cross": ma_data["death_cross"],
                    "ma_alignment": ma_data["ma_alignment"]
                },
                "fibonacci_analysis": {
                    "levels": fibonacci_data["fibonacci_levels"],
                    "golden_ratio_levels": [
                        level for level in fibonacci_data["fibonacci_levels"]
                        if level["level"] in [0.618, 0.382, 1.618]
                    ],
                    "current_fib_position": fibonacci_confidence["current_position"],
                    "golden_ratio_strength": fibonacci_confidence["golden_ratio_strength"],
                    "fib_trend_alignment": fibonacci_confidence["trend_alignment"]
                },
                "bullish_confidence": {
                    "overall_score": bullish_confidence["overall_score"],
                    "rating": bullish_confidence["rating"],
                    "components": bullish_confidence["components"],
                    "key_signals": bullish_confidence["key_signals"],
                    "risk_factors": bullish_confidence["risk_factors"]
                },
                "candlestick_analysis": {
                    "patterns": candlestick_patterns,
                    "recent_patterns": candlestick_patterns[-5:] if candlestick_patterns else [],
                    "pattern_summary": _generate_pattern_summary(candlestick_patterns),
                    "temporal_analysis": {
                        "trend_following": pattern_temporal.get("trend_following", {}),
                        "frequency_changes": pattern_temporal.get("frequency_changes", {}),
                        "pattern_evolution": pattern_temporal.get("pattern_evolution", {}),
                        "adaptive_scoring": pattern_temporal.get("adaptive_score", {})
                    }
                },
                "insider_calculus_analysis": {
                    "insider_summary": insider_calculus.get("insider_summary", {}),
                    "insider_influence": insider_influence,
                    "critical_points": insider_calculus.get("critical_points", {}),
                    "inflection_points": insider_calculus.get("inflection_points", {}),
                    "volume_shifts": insider_calculus.get("volume_analysis", {}),
                    "optimal_trade": insider_calculus.get("optimal_trade", {}),
                    "predictions": insider_calculus.get("predictions", {})
                },
                "volume_analysis": technical_analysis["volume_analysis"],
                "support_resistance": technical_analysis["support_resistance"],
                "trend_analysis": technical_analysis["trend_analysis"]
            }
            
    except Exception as e:
        logger.error(f"Error generating portfolio chart data for {symbol}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate chart data: {str(e)}"
        )


def _calculate_long_term_moving_averages(historical_data: List) -> dict:
    """Calculate 50, 200, and 250 day moving averages with trend analysis"""
    import numpy as np
    
    prices = [d.close for d in historical_data]
    
    # Calculate moving averages
    ma_50 = []
    ma_200 = []
    ma_250 = []
    
    for i in range(len(prices)):
        # 50-day MA
        if i >= 49:
            ma_50.append(sum(prices[i-49:i+1]) / 50)
        else:
            ma_50.append(None)
        
        # 200-day MA
        if i >= 199:
            ma_200.append(sum(prices[i-199:i+1]) / 200)
        else:
            ma_200.append(None)
        
        # 250-day MA
        if i >= 249:
            ma_250.append(sum(prices[i-249:i+1]) / 250)
        else:
            ma_250.append(None)
    
    # Calculate trends and slopes
    def calculate_trend_and_slope(ma_values):
        valid_values = [v for v in ma_values if v is not None]
        if len(valid_values) < 10:
            return "neutral", 0
        
        recent_values = valid_values[-10:]
        slope = (recent_values[-1] - recent_values[0]) / len(recent_values)
        
        if slope > 0.5:
            trend = "bullish"
        elif slope < -0.5:
            trend = "bearish"
        else:
            trend = "neutral"
        
        return trend, slope
    
    ma_50_trend, ma_50_slope = calculate_trend_and_slope(ma_50)
    ma_200_trend, ma_200_slope = calculate_trend_and_slope(ma_200)
    ma_250_trend, ma_250_slope = calculate_trend_and_slope(ma_250)
    
    # Detect crossovers
    golden_cross = False
    death_cross = False
    
    if len(ma_50) > 1 and len(ma_200) > 1:
        if ma_50[-1] and ma_200[-1] and ma_50[-2] and ma_200[-2]:
            if ma_50[-2] <= ma_200[-2] and ma_50[-1] > ma_200[-1]:
                golden_cross = True
            elif ma_50[-2] >= ma_200[-2] and ma_50[-1] < ma_200[-1]:
                death_cross = True
    
    # MA Alignment (bullish when price > MA50 > MA200 > MA250)
    current_price = prices[-1]
    ma_alignment = "neutral"
    
    if ma_50[-1] and ma_200[-1] and ma_250[-1]:
        if current_price > ma_50[-1] > ma_200[-1] > ma_250[-1]:
            ma_alignment = "strongly_bullish"
        elif current_price > ma_50[-1] > ma_200[-1]:
            ma_alignment = "bullish"
        elif current_price < ma_50[-1] < ma_200[-1] < ma_250[-1]:
            ma_alignment = "strongly_bearish"
        elif current_price < ma_50[-1] < ma_200[-1]:
            ma_alignment = "bearish"
    
    # Distance from 250-day MA (key long-term indicator)
    distance_from_250ma = 0
    if ma_250[-1]:
        distance_from_250ma = ((current_price - ma_250[-1]) / ma_250[-1]) * 100
    
    return {
        "ma_50": ma_50,
        "ma_200": ma_200,
        "ma_250": ma_250,
        "ma_50_trend": ma_50_trend,
        "ma_200_trend": ma_200_trend,
        "ma_250_trend": ma_250_trend,
        "ma_50_slope": ma_50_slope,
        "ma_200_slope": ma_200_slope,
        "ma_250_slope": ma_250_slope,
        "golden_cross": golden_cross,
        "death_cross": death_cross,
        "ma_alignment": ma_alignment,
        "distance_from_250ma": distance_from_250ma
    }


def _generate_pattern_summary(candlestick_patterns: List[dict]) -> dict:
    """Generate summary of candlestick pattern analysis"""
    
    if not candlestick_patterns:
        return {
            "total_patterns": 0,
            "bullish_patterns": 0,
            "bearish_patterns": 0,
            "dominant_direction": "neutral",
            "strongest_pattern": None,
            "pattern_confidence": 30
        }
    
    recent_patterns = candlestick_patterns[-10:]
    
    bullish_count = sum(1 for p in recent_patterns if p.get("direction") == "bullish")
    bearish_count = sum(1 for p in recent_patterns if p.get("direction") == "bearish")
    neutral_count = len(recent_patterns) - bullish_count - bearish_count
    
    # Determine dominant direction
    if bullish_count > bearish_count and bullish_count > neutral_count:
        dominant_direction = "bullish"
    elif bearish_count > bullish_count and bearish_count > neutral_count:
        dominant_direction = "bearish"
    else:
        dominant_direction = "neutral"
    
    # Find strongest pattern
    strongest_pattern = max(
        recent_patterns,
        key=lambda p: p.get("reliability", 0) * p.get("strength", 0)
    ) if recent_patterns else None
    
    # Calculate pattern confidence
    if recent_patterns:
        avg_reliability = sum(p.get("reliability", 65) for p in recent_patterns) / len(recent_patterns)
        avg_strength = sum(p.get("strength", 50) for p in recent_patterns) / len(recent_patterns)
        pattern_confidence = (avg_reliability + avg_strength) / 2
    else:
        pattern_confidence = 30
    
    return {
        "total_patterns": len(recent_patterns),
        "bullish_patterns": bullish_count,
        "bearish_patterns": bearish_count,
        "neutral_patterns": neutral_count,
        "dominant_direction": dominant_direction,
        "strongest_pattern": {
            "pattern": strongest_pattern.get("pattern"),
            "direction": strongest_pattern.get("direction"),
            "strength": strongest_pattern.get("strength"),
            "reliability": strongest_pattern.get("reliability"),
            "description": strongest_pattern.get("description")
        } if strongest_pattern else None,
        "pattern_confidence": round(pattern_confidence, 2)
    }


def _calculate_candlestick_pattern_score(candlestick_patterns: List[dict]) -> float:
    """Calculate weighted score from candlestick patterns (0-20 points)"""
    
    if not candlestick_patterns:
        return 5  # Neutral score when no patterns
    
    # Get recent patterns (last 10)
    recent_patterns = candlestick_patterns[-10:] if len(candlestick_patterns) > 10 else candlestick_patterns
    
    bullish_score = 0
    bearish_score = 0
    total_patterns = 0
    
    for i, pattern in enumerate(recent_patterns):
        # Recency multiplier (more recent = more weight)
        recency_multiplier = 1.0 + (i / len(recent_patterns) * 0.5)  # Up to 1.5x for most recent
        
        # Get pattern strength and reliability
        strength = pattern.get("strength", 50) / 100  # Normalize to 0-1
        reliability = pattern.get("reliability", 65) / 100  # Normalize to 0-1
        
        # Calculate weighted score for this pattern
        pattern_score = strength * reliability * recency_multiplier
        
        # Add to appropriate direction
        if pattern.get("direction") == "bullish":
            bullish_score += pattern_score
        elif pattern.get("direction") == "bearish":
            bearish_score -= pattern_score  # Negative for bearish
        
        total_patterns += 1
    
    # Net score (bullish - bearish)
    net_score = bullish_score + bearish_score  # bearish_score is already negative
    
    # Normalize to 0-20 scale
    # Strong bullish patterns → 20 points
    # Neutral/no patterns → 10 points
    # Strong bearish patterns → 0 points
    
    if net_score > 0:
        # Bullish patterns
        score = 10 + min(10, net_score * 3)  # Scale up, max +10
    else:
        # Bearish patterns
        score = 10 + max(-10, net_score * 3)  # Scale up, max -10
    
    return max(0, min(20, score))


def _calculate_fibonacci_confidence(historical_data: List, fibonacci_data: dict) -> dict:
    """Calculate confidence metrics based on Fibonacci golden ratio analysis"""
    current_price = historical_data[-1].close
    fibonacci_levels = fibonacci_data["fibonacci_levels"]
    golden_ratio_analysis = fibonacci_data.get("golden_ratio_analysis", {})
    
    # Find current position relative to Fibonacci levels
    current_position = "between_levels"
    nearest_fib_level = None
    nearest_distance = float('inf')
    
    for level in fibonacci_levels:
        distance = abs(current_price - level["price"])
        if distance < nearest_distance:
            nearest_distance = distance
            nearest_fib_level = level
    
    # Golden ratio strength (0.618 is the golden ratio)
    golden_ratio_strength = 0
    
    if nearest_fib_level and nearest_fib_level["level"] == 0.618:
        # Very strong signal at golden ratio
        golden_ratio_strength = 90
        current_position = "at_golden_ratio"
    elif nearest_fib_level and nearest_fib_level["level"] in [0.382, 1.618]:
        # Strong signal at related Fibonacci levels
        golden_ratio_strength = 75
        current_position = "at_fibonacci_key_level"
    else:
        # Calculate proximity to golden ratio level
        golden_levels = [l for l in fibonacci_levels if l["level"] == 0.618]
        if golden_levels:
            golden_price = golden_levels[0]["price"]
            proximity = abs(current_price - golden_price) / golden_price
            golden_ratio_strength = max(0, 70 - (proximity * 100))
    
    # Trend alignment with Fibonacci
    trend_alignment = "neutral"
    if fibonacci_data.get("trend_direction") == "bullish":
        if current_price > nearest_fib_level["price"]:
            trend_alignment = "bullish"
        else:
            trend_alignment = "consolidating"
    elif fibonacci_data.get("trend_direction") == "bearish":
        if current_price < nearest_fib_level["price"]:
            trend_alignment = "bearish"
        else:
            trend_alignment = "recovering"
    
    # Price action at Fibonacci levels (support/resistance strength)
    fib_level_strength = golden_ratio_analysis.get("strength", 50)
    
    return {
        "current_position": current_position,
        "nearest_fib_level": nearest_fib_level,
        "golden_ratio_strength": golden_ratio_strength,
        "trend_alignment": trend_alignment,
        "fib_level_strength": fib_level_strength
    }


def _calculate_enhanced_bullish_confidence(
    ma_data: dict, 
    fibonacci_confidence: dict, 
    technical_analysis: dict,
    candlestick_patterns: List[dict] = None,
    candlestick_score_override: float = None,
    insider_influence: dict = None
) -> dict:
    """Calculate enhanced bullish confidence score with MA, Fibonacci, adaptive candlestick, and insider influence"""
    
    components = {
        "ma_alignment": 0,
        "ma_trend": 0,
        "golden_cross": 0,
        "fibonacci_position": 0,
        "golden_ratio_strength": 0,
        "volume_confirmation": 0,
        "support_resistance": 0,
        "overall_technical": 0,
        "candlestick_patterns": 0,  # Candlestick pattern score (can be adaptive)
        "insider_influence": 0  # NEW: 10th component for insider trading influence
    }
    
    # 1. MA Alignment Score (30 points max - reduced from 35)
    ma_alignment_scores = {
        "strongly_bullish": 30,
        "bullish": 22,
        "neutral": 9,
        "bearish": 4,
        "strongly_bearish": 0
    }
    components["ma_alignment"] = ma_alignment_scores.get(ma_data["ma_alignment"], 9)
    
    # 2. MA Trend Score (15 points max)
    trend_count = sum([
        1 for trend in [ma_data["ma_50_trend"], ma_data["ma_200_trend"], ma_data["ma_250_trend"]]
        if trend == "bullish"
    ])
    components["ma_trend"] = (trend_count / 3) * 15
    
    # 3. Golden Cross Bonus (10 points)
    if ma_data["golden_cross"]:
        components["golden_cross"] = 10
    elif ma_data["death_cross"]:
        components["golden_cross"] = -10
    
    # 4. Fibonacci Position (15 points max)
    fib_position_scores = {
        "at_golden_ratio": 15,
        "at_fibonacci_key_level": 12,
        "between_levels": 5
    }
    components["fibonacci_position"] = fib_position_scores.get(
        fibonacci_confidence["current_position"], 5
    )
    
    # 5. Golden Ratio Strength (15 points max)
    components["golden_ratio_strength"] = (fibonacci_confidence["golden_ratio_strength"] / 100) * 15
    
    # 6. Volume Confirmation (10 points max)
    volume_analysis = technical_analysis.get("volume_analysis", {})
    volume_correlation = abs(volume_analysis.get("price_volume_correlation", 0))
    if volume_correlation > 0.7:
        components["volume_confirmation"] = 10
    elif volume_correlation > 0.5:
        components["volume_confirmation"] = 6
    else:
        components["volume_confirmation"] = 2
    
    # 7. Support/Resistance (10 points max)
    support_resistance = technical_analysis.get("support_resistance", {})
    support_strength = support_resistance.get("support_strength", 0)
    components["support_resistance"] = (support_strength / 100) * 10
    
    # 8. Overall Technical Signals (10 points max)
    weighted_signals = technical_analysis.get("weighted_signals", {})
    overall_signal = weighted_signals.get("overall_signal", {})
    signal_strength = overall_signal.get("strength", 50)
    components["overall_technical"] = (signal_strength / 100) * 10
    
    # 9. Candlestick Pattern Analysis (20 points max) - Uses adaptive score if available
    if candlestick_score_override is not None:
        # Use adaptive score that factors in recent pattern performance
        components["candlestick_patterns"] = (candlestick_score_override / 100) * 20
    elif candlestick_patterns:
        # Fallback to base pattern score
        pattern_score = _calculate_candlestick_pattern_score(candlestick_patterns)
        components["candlestick_patterns"] = pattern_score
    
    # 10. Insider Influence (15 points max) - NEW insider trading analysis component
    if insider_influence:
        insider_score = insider_influence.get("score", 0)
        sentiment = insider_influence.get("sentiment", "neutral")
        
        if sentiment == "bullish":
            components["insider_influence"] = (insider_score / 100) * 15
        elif sentiment == "bearish":
            components["insider_influence"] = -(insider_score / 100) * 15
        else:
            components["insider_influence"] = 0
        
        # Apply insider adjustments to other components
        adjustments = insider_influence.get("adjustments", {})
        if adjustments:
            components["candlestick_patterns"] += adjustments.get("candlestick", 0)
            components["ma_alignment"] += adjustments.get("moving_average", 0)
            components["fibonacci_position"] += adjustments.get("fibonacci", 0)
    
    # Calculate total score (max 155 points with insider, normalized to 100)
    raw_score = sum(components.values())
    overall_score = min(100, (raw_score / 155) * 100)
    
    # Determine rating
    if overall_score >= 80:
        rating = "Very Bullish"
    elif overall_score >= 65:
        rating = "Bullish"
    elif overall_score >= 50:
        rating = "Neutral/Positive"
    elif overall_score >= 35:
        rating = "Neutral/Negative"
    else:
        rating = "Bearish"
    
    # Identify key signals
    key_signals = []
    if ma_data["golden_cross"]:
        key_signals.append("🌟 Golden Cross Detected - Strong Bullish Signal")
    if ma_data["ma_alignment"] in ["strongly_bullish", "bullish"]:
        key_signals.append("📈 Bullish MA Alignment")
    if fibonacci_confidence["current_position"] == "at_golden_ratio":
        key_signals.append("✨ Price at Fibonacci Golden Ratio - High Confidence Level")
    if fibonacci_confidence["golden_ratio_strength"] > 75:
        key_signals.append("💫 Strong Fibonacci Support/Resistance")
    if ma_data["distance_from_250ma"] > 10:
        key_signals.append("🚀 Price Extended Above 250-Day MA")
    
    # Insider signals
    if insider_influence:
        insider_score = insider_influence.get("score", 0)
        sentiment = insider_influence.get("sentiment", "neutral")
        if sentiment == "bullish" and insider_score > 60:
            key_signals.append("👔 Strong Bullish Insider Activity Detected")
        if sentiment == "bullish" and insider_score > 75:
            key_signals.append("🎯 Near Critical Point - Optimal Entry Opportunity")
    
    # Identify risk factors
    risk_factors = []
    if ma_data["death_cross"]:
        risk_factors.append("⚠️ Death Cross Detected - Bearish Signal")
    if ma_data["ma_alignment"] in ["bearish", "strongly_bearish"]:
        risk_factors.append("📉 Bearish MA Alignment")
    if ma_data["distance_from_250ma"] < -10:
        risk_factors.append("⚠️ Price Extended Below 250-Day MA")
    if volume_analysis.get("price_volume_correlation", 0) < -0.5:
        risk_factors.append("📊 Negative Price-Volume Correlation")
    
    # Insider risk factors
    if insider_influence:
        insider_score = insider_influence.get("score", 0)
        sentiment = insider_influence.get("sentiment", "neutral")
        if sentiment == "bearish" and insider_score > 60:
            risk_factors.append("⚠️ Strong Bearish Insider Activity Detected")
        if sentiment == "bearish" and insider_score > 75:
            risk_factors.append("🚨 Near Critical Point - Consider Exit")
    
    return {
        "overall_score": round(overall_score, 2),
        "rating": rating,
        "components": components,
        "key_signals": key_signals if key_signals else ["No strong bullish signals detected"],
        "risk_factors": risk_factors if risk_factors else ["No major risk factors identified"]
    }
