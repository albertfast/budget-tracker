from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta

from ..core.database import get_db
from ..core.security import verify_token
from ..models.database import User, Transaction, BankAccount
from ..services.transaction_processor import transaction_processor
from ..services.investment_engine import investment_engine
from ..services.technical_analysis import technical_analysis_engine
from ..services.fundamental_analysis import fundamental_analysis_engine
from ..services.market_data import market_data_service
from ..api.banks import get_current_user

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
            analysis = technical_analysis_engine.analyze_security(
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
            from ..services.fundamental_analysis import FinancialStatement
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
            analysis = fundamental_analysis_engine.analyze_company_fundamentals(
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
        user_profile = investment_engine.analyze_financial_profile(db, current_user.id, 90)
        
        # Perform combined analysis
        analysis = await investment_engine.analyze_investment_opportunity(
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
            full_analysis = technical_analysis_engine.analyze_security(
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
        user_profile = investment_engine.analyze_financial_profile(db, current_user.id, 90)
        
        # Get combined analysis for enhanced price targets
        combined_analysis = await investment_engine.analyze_investment_opportunity(
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
            analysis = technical_analysis_engine.analyze_security(
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
        analysis = transaction_processor.get_spending_analysis(db, current_user.id, days)
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
        recurring = transaction_processor.detect_recurring_transactions(db, current_user.id, days)
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
        profile = investment_engine.analyze_financial_profile(db, current_user.id, days)
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
        financial_profile = investment_engine.analyze_financial_profile(db, current_user.id, days)
        
        # Generate recommendations
        recommendations = investment_engine.generate_investment_recommendations(financial_profile)
        
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
        analysis = transaction_processor.get_spending_analysis(db, current_user.id, days)
        
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
        analysis = transaction_processor.get_spending_analysis(db, current_user.id, days)
        
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
        financial_profile = investment_engine.analyze_financial_profile(db, current_user.id, 90)
        
        # Get recurring transactions for subscription analysis
        recurring = transaction_processor.detect_recurring_transactions(db, current_user.id, 90)
        
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