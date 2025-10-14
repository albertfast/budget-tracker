from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from ..models.database import Transaction, BankAccount, User
from .transaction_processor import transaction_processor
from .technical_analysis import technical_analysis_engine, PriceData
from .fundamental_analysis import fundamental_analysis_engine, FinancialStatement
from .market_data import market_data_service
import logging
from collections import defaultdict
import asyncio

logger = logging.getLogger(__name__)

class AdvancedInvestmentRecommendationEngine:
    """Enhanced investment recommendation engine with technical and fundamental analysis"""
    
    def __init__(self):
        self.investment_products = self._load_investment_products()
        self.savings_thresholds = self._load_savings_thresholds()
        self.analysis_weights = self._load_analysis_weights()
    
    async def analyze_investment_opportunity(
        self,
        symbol: str,
        user_profile: Dict[str, Any],
        analysis_period: str = "1y"
    ) -> Dict[str, Any]:
        """Comprehensive investment analysis combining technical and fundamental analysis"""
        
        try:
            async with market_data_service:
                # Fetch market data
                historical_data = await market_data_service.get_historical_data(
                    symbol, analysis_period, "1d"
                )
                
                current_quote = await market_data_service.get_real_time_quote(symbol)
                
                company_profile = await market_data_service.get_company_profile(symbol)
                
                financial_statements_data = await market_data_service.get_financial_statements(symbol)
                
                # Convert financial data to FinancialStatement objects
                financial_statements = [
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
                    ) for stmt in financial_statements_data
                ]
                
                # Technical Analysis
                technical_analysis = technical_analysis_engine.analyze_security(
                    symbol, historical_data, len(historical_data)
                )
                
                # Fundamental Analysis
                fundamental_analysis = fundamental_analysis_engine.analyze_company_fundamentals(
                    symbol, financial_statements, company_profile.industry if company_profile else "general"
                )
                
                # Combined Analysis
                combined_analysis = self._combine_analyses(
                    technical_analysis, fundamental_analysis, user_profile
                )
                
                # Investment Recommendation
                investment_recommendation = self._generate_comprehensive_recommendation(
                    symbol, technical_analysis, fundamental_analysis, combined_analysis, user_profile
                )
                
                return {
                    "symbol": symbol,
                    "analysis_timestamp": datetime.utcnow(),
                    "current_price": current_quote.last_price if current_quote else historical_data[-1].close,
                    "company_profile": {
                        "name": company_profile.name if company_profile else f"{symbol} Corporation",
                        "sector": company_profile.sector if company_profile else "Unknown",
                        "industry": company_profile.industry if company_profile else "Unknown",
                        "market_cap": company_profile.market_cap if company_profile else 0
                    },
                    "technical_analysis": technical_analysis,
                    "fundamental_analysis": fundamental_analysis,
                    "combined_analysis": combined_analysis,
                    "investment_recommendation": investment_recommendation,
                    "risk_assessment": self._assess_investment_risk(
                        technical_analysis, fundamental_analysis, user_profile
                    ),
                    "portfolio_fit": self._assess_portfolio_fit(
                        investment_recommendation, user_profile
                    )
                }
                
        except Exception as e:
            logger.error(f"Error analyzing investment opportunity for {symbol}: {str(e)}")
            raise
    
    def _combine_analyses(
        self,
        technical_analysis: Dict[str, Any],
        fundamental_analysis: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Combine technical and fundamental analysis with weighted scoring"""
        
        # Extract key signals
        technical_signal = technical_analysis["weighted_signals"]["overall_signal"]
        fundamental_recommendation = fundamental_analysis["investment_recommendation"]
        
        # Get analysis weights based on user profile and market conditions
        weights = self._get_dynamic_weights(user_profile, technical_analysis, fundamental_analysis)
        
        # Technical score (0-100)
        technical_score = technical_signal["strength"]
        technical_direction = technical_signal["direction"]
        
        # Fundamental score (0-100)
        fundamental_score = fundamental_analysis["company_health"]["overall_score"]
        fundamental_direction = self._map_recommendation_to_direction(
            fundamental_recommendation["recommendation"]
        )
        
        # Calculate combined score
        combined_score = (
            technical_score * weights["technical"] +
            fundamental_score * weights["fundamental"]
        ) / (weights["technical"] + weights["fundamental"])
        
        # Determine combined direction
        if technical_direction == fundamental_direction:
            combined_direction = technical_direction
            direction_confidence = 90
        else:
            # Conflicting signals - use the higher weighted analysis
            if weights["technical"] > weights["fundamental"]:
                combined_direction = technical_direction
                direction_confidence = 60
            else:
                combined_direction = fundamental_direction
                direction_confidence = 60
        
        # Golden ratio analysis integration
        fibonacci_analysis = technical_analysis.get("fibonacci_analysis", {})
        golden_ratio_strength = fibonacci_analysis.get("golden_ratio_analysis", {}).get("strength", 0)
        
        # Adjust score based on golden ratio proximity
        if golden_ratio_strength > 70:
            combined_score += 5  # Boost for strong golden ratio signals
        
        # Support/resistance level analysis
        support_resistance = technical_analysis.get("support_resistance", {})
        nearest_support_strength = support_resistance.get("support_strength", 0)
        nearest_resistance_strength = support_resistance.get("resistance_strength", 0)
        
        # Volume analysis impact
        volume_analysis = technical_analysis.get("volume_analysis", {})
        volume_confirmation = volume_analysis.get("price_volume_correlation", 0)
        
        if abs(volume_confirmation) > 0.7:  # Strong volume confirmation
            combined_score += 3
        
        # MA analysis (50/200 day crossover significance)
        ma_analysis = technical_analysis.get("moving_average_analysis", {})
        golden_cross = ma_analysis.get("golden_cross", False)
        death_cross = ma_analysis.get("death_cross", False)
        
        if golden_cross and combined_direction == "bullish":
            combined_score += 7
        elif death_cross and combined_direction == "bearish":
            combined_score += 7
        
        return {
            "combined_score": min(combined_score, 100),  # Cap at 100
            "combined_direction": combined_direction,
            "direction_confidence": direction_confidence,
            "analysis_weights": weights,
            "technical_contribution": technical_score * weights["technical"],
            "fundamental_contribution": fundamental_score * weights["fundamental"],
            "signal_alignment": technical_direction == fundamental_direction,
            "key_factors": self._identify_key_combined_factors(
                technical_analysis, fundamental_analysis, weights
            ),
            "confidence_factors": {
                "golden_ratio_strength": golden_ratio_strength,
                "support_resistance_strength": max(nearest_support_strength, nearest_resistance_strength),
                "volume_confirmation": abs(volume_confirmation),
                "ma_crossover_significance": 7 if (golden_cross or death_cross) else 0
            }
        }
    
    def _generate_comprehensive_recommendation(
        self,
        symbol: str,
        technical_analysis: Dict[str, Any],
        fundamental_analysis: Dict[str, Any],
        combined_analysis: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive investment recommendation"""
        
        combined_score = combined_analysis["combined_score"]
        combined_direction = combined_analysis["combined_direction"]
        direction_confidence = combined_analysis["direction_confidence"]
        
        # Technical targets
        technical_targets = technical_analysis["price_targets"]
        
        # Fundamental valuation
        fundamental_rec = fundamental_analysis["investment_recommendation"]
        
        # User risk profile
        user_risk_tolerance = user_profile.get("risk_profile", {}).get("risk_level", "moderate")
        
        # Determine recommendation
        if combined_score >= 80 and direction_confidence >= 80:
            if combined_direction == "bullish":
                recommendation = "strong_buy"
                confidence = 95
            else:
                recommendation = "strong_sell"
                confidence = 95
        elif combined_score >= 65 and direction_confidence >= 70:
            if combined_direction == "bullish":
                recommendation = "buy"
                confidence = 80
            else:
                recommendation = "sell"
                confidence = 80
        elif combined_score >= 50:
            recommendation = "hold"
            confidence = 60
        else:
            if combined_direction == "bearish":
                recommendation = "sell"
                confidence = 70
            else:
                recommendation = "hold"
                confidence = 40
        
        # Adjust for user risk tolerance
        if user_risk_tolerance == "low" and recommendation in ["strong_buy", "buy"]:
            if combined_score < 75:
                recommendation = "hold"
                confidence -= 10
        elif user_risk_tolerance == "high" and recommendation == "hold":
            if combined_score > 60:
                recommendation = "buy" if combined_direction == "bullish" else "sell"
                confidence += 5
        
        # Calculate position sizing
        position_size = self._calculate_optimal_position_size(
            recommendation, confidence, user_profile, fundamental_analysis
        )
        
        # Time horizon based on technical analysis
        time_horizon = technical_targets["estimated_time_to_target"]
        
        # Price targets with fibonacci and support/resistance integration
        price_targets = self._calculate_enhanced_price_targets(
            technical_analysis, fundamental_analysis, combined_analysis
        )
        
        return {
            "recommendation": recommendation,
            "confidence": confidence,
            "position_size_percentage": position_size,
            "target_price": price_targets["primary_target"],
            "stop_loss": price_targets["stop_loss"],
            "alternative_targets": price_targets["alternative_targets"],
            "time_horizon": time_horizon,
            "investment_thesis": self._generate_investment_thesis(
                symbol, technical_analysis, fundamental_analysis, combined_analysis
            ),
            "key_catalysts": self._identify_investment_catalysts(
                technical_analysis, fundamental_analysis
            ),
            "risk_factors": self._identify_investment_risks(
                technical_analysis, fundamental_analysis, user_profile
            ),
            "monitoring_levels": self._define_monitoring_levels(
                technical_analysis, price_targets
            ),
            "exit_strategy": self._define_exit_strategy(
                recommendation, price_targets, time_horizon, user_profile
            )
        }
    
    def _calculate_enhanced_price_targets(
        self,
        technical_analysis: Dict[str, Any],
        fundamental_analysis: Dict[str, Any],
        combined_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate enhanced price targets using multiple methodologies"""
        
        current_price = technical_analysis["current_price"]
        
        # Technical targets from Fibonacci and support/resistance
        technical_targets = technical_analysis["price_targets"]
        fibonacci_levels = technical_analysis["fibonacci_analysis"]["fibonacci_levels"]
        support_resistance = technical_analysis["support_resistance"]
        
        # Fundamental valuation targets
        fundamental_rec = fundamental_analysis["investment_recommendation"]
        company_health = fundamental_analysis["company_health"]["overall_score"]
        
        # Primary target based on combined analysis
        if combined_analysis["combined_direction"] == "bullish":
            # Use next resistance level or fibonacci target
            resistance_targets = [
                level["price"] for level in support_resistance["resistance_levels"]
                if level["price"] > current_price
            ]
            
            fib_targets = [
                level["price"] for level in fibonacci_levels
                if level["price"] > current_price and level["level"] in [0.618, 0.786]
            ]
            
            if resistance_targets and fib_targets:
                primary_target = min(resistance_targets[0], fib_targets[0])
            elif resistance_targets:
                primary_target = resistance_targets[0]
            elif fib_targets:
                primary_target = fib_targets[0]
            else:
                primary_target = technical_targets["optimal_exit_price"]
            
            # Stop loss at support level
            support_levels = [
                level["price"] for level in support_resistance["support_levels"]
                if level["price"] < current_price
            ]
            stop_loss = support_levels[0] if support_levels else technical_targets["stop_loss_price"]
            
        else:  # Bearish direction
            # Target at support levels
            support_targets = [
                level["price"] for level in support_resistance["support_levels"]
                if level["price"] < current_price
            ]
            
            primary_target = support_targets[0] if support_targets else current_price * 0.9
            stop_loss = current_price * 1.05  # 5% stop loss for short positions
        
        # Alternative targets
        alternative_targets = []
        if combined_analysis["combined_direction"] == "bullish":
            # Add multiple resistance levels as targets
            for level in support_resistance["resistance_levels"][:3]:
                if level["price"] > current_price:
                    alternative_targets.append({
                        "price": level["price"],
                        "probability": level["strength"],
                        "type": "resistance_level"
                    })
            
            # Add fibonacci extension levels
            for level in fibonacci_levels:
                if level["price"] > current_price and level["level"] > 1.0:
                    alternative_targets.append({
                        "price": level["price"],
                        "probability": level["support_strength"],
                        "type": "fibonacci_extension"
                    })
        
        return {
            "primary_target": primary_target,
            "stop_loss": stop_loss,
            "alternative_targets": alternative_targets[:5],  # Top 5 alternative targets
            "risk_reward_ratio": abs(primary_target - current_price) / abs(current_price - stop_loss) if stop_loss != current_price else 0,
            "price_methodology": "fibonacci_support_resistance_combined"
        }
    
    def _get_dynamic_weights(
        self,
        user_profile: Dict[str, Any],
        technical_analysis: Dict[str, Any],
        fundamental_analysis: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate dynamic weights based on market conditions and user profile"""
        
        # Base weights
        base_technical_weight = 0.4
        base_fundamental_weight = 0.6
        
        # Adjust based on user investment horizon
        investment_horizon = user_profile.get("investment_horizon", "medium_term")
        
        if investment_horizon == "short_term":  # < 3 months
            technical_weight = 0.7
            fundamental_weight = 0.3
        elif investment_horizon == "medium_term":  # 3-12 months
            technical_weight = 0.5
            fundamental_weight = 0.5
        else:  # long_term > 12 months
            technical_weight = 0.3
            fundamental_weight = 0.7
        
        # Adjust based on market volatility
        volatility = technical_analysis.get("trend_analysis", {}).get("trend_strength", 50)
        if volatility > 70:  # High volatility - favor technical
            technical_weight += 0.1
            fundamental_weight -= 0.1
        
        # Adjust based on fundamental strength
        company_health = fundamental_analysis.get("company_health", {}).get("overall_score", 50)
        if company_health > 80:  # Strong fundamentals
            fundamental_weight += 0.1
            technical_weight -= 0.1
        elif company_health < 40:  # Weak fundamentals
            technical_weight += 0.1
            fundamental_weight -= 0.1
        
        # Ensure weights sum to 1
        total_weight = technical_weight + fundamental_weight
        technical_weight /= total_weight
        fundamental_weight /= total_weight
        
        return {
            "technical": technical_weight,
            "fundamental": fundamental_weight
        }
    
    def _load_analysis_weights(self) -> Dict[str, float]:
        """Load analysis methodology weights based on historical accuracy"""
        return {
            "fibonacci_golden_ratio": 0.25,     # Highest accuracy in trending markets
            "support_resistance": 0.30,         # Most reliable technical indicator
            "volume_analysis": 0.20,           # Confirms price movements
            "candlestick_patterns": 0.10,      # Short-term signals
            "moving_averages": 0.15,           # Trend confirmation
            "fundamental_health": 0.35,        # Long-term value
            "growth_potential": 0.25,          # Growth assessment
            "debt_analysis": 0.25,             # Financial stability
            "profitability": 0.15              # Current performance
        }
    
    # Keep existing methods from original investment_engine.py
    def analyze_financial_profile(
        self, 
        db: Session, 
        user_id: str, 
        analysis_days: int = 90
    ) -> Dict[str, Any]:
        """Analyze user's financial profile for investment recommendations"""
        
        # Get comprehensive spending analysis
        spending_analysis = transaction_processor.get_spending_analysis(
            db, user_id, analysis_days
        )
        
        # Get recurring transactions (subscriptions, etc.)
        recurring_analysis = transaction_processor.detect_recurring_transactions(
            db, user_id, analysis_days
        )
        
        # Calculate income vs expenses
        income_expense_analysis = self._analyze_income_expenses(db, user_id, analysis_days)
        
        # Assess savings potential
        savings_potential = self._calculate_savings_potential(
            spending_analysis, recurring_analysis, income_expense_analysis
        )
        
        # Generate risk profile
        risk_profile = self._assess_risk_profile(spending_analysis, income_expense_analysis)
        
        return {
            "user_id": user_id,
            "analysis_period_days": analysis_days,
            "spending_analysis": spending_analysis,
            "recurring_transactions": recurring_analysis,
            "income_expense_analysis": income_expense_analysis,
            "savings_potential": savings_potential,
            "risk_profile": risk_profile,
            "generated_at": datetime.utcnow()
        }
    
    # Additional helper methods would be implemented here...
    # (Include all other methods from the original investment_engine.py)

# Initialize enhanced investment recommendation engine
investment_engine = AdvancedInvestmentRecommendationEngine()
    """Engine for analyzing spending and providing investment recommendations"""
    
    def __init__(self):
        self.investment_products = self._load_investment_products()
        self.savings_thresholds = self._load_savings_thresholds()
    
    def analyze_financial_profile(
        self, 
        db: Session, 
        user_id: str, 
        analysis_days: int = 90
    ) -> Dict[str, Any]:
        """Analyze user's financial profile for investment recommendations"""
        
        # Get comprehensive spending analysis
        spending_analysis = transaction_processor.get_spending_analysis(
            db, user_id, analysis_days
        )
        
        # Get recurring transactions (subscriptions, etc.)
        recurring_analysis = transaction_processor.detect_recurring_transactions(
            db, user_id, analysis_days
        )
        
        # Calculate income vs expenses
        income_expense_analysis = self._analyze_income_expenses(db, user_id, analysis_days)
        
        # Assess savings potential
        savings_potential = self._calculate_savings_potential(
            spending_analysis, recurring_analysis, income_expense_analysis
        )
        
        # Generate risk profile
        risk_profile = self._assess_risk_profile(spending_analysis, income_expense_analysis)
        
        return {
            "user_id": user_id,
            "analysis_period_days": analysis_days,
            "spending_analysis": spending_analysis,
            "recurring_transactions": recurring_analysis,
            "income_expense_analysis": income_expense_analysis,
            "savings_potential": savings_potential,
            "risk_profile": risk_profile,
            "generated_at": datetime.utcnow()
        }
    
    def generate_investment_recommendations(
        self, 
        financial_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate personalized investment recommendations"""
        
        savings_potential = financial_profile["savings_potential"]
        risk_profile = financial_profile["risk_profile"]
        spending_analysis = financial_profile["spending_analysis"]
        
        recommendations = []
        
        # Emergency fund recommendation
        emergency_fund_rec = self._recommend_emergency_fund(savings_potential, spending_analysis)
        if emergency_fund_rec:
            recommendations.append(emergency_fund_rec)
        
        # Investment recommendations based on savings capacity
        if savings_potential["monthly_savings_potential"] > 100:
            
            # Low-risk investments for conservative users
            if risk_profile["risk_level"] in ["low", "moderate"]:
                recommendations.extend(self._get_conservative_investments(savings_potential))
            
            # Growth investments for moderate to high risk users
            if risk_profile["risk_level"] in ["moderate", "high"]:
                recommendations.extend(self._get_growth_investments(savings_potential))
            
            # Retirement planning
            retirement_rec = self._recommend_retirement_planning(savings_potential, risk_profile)
            if retirement_rec:
                recommendations.append(retirement_rec)
        
        # Debt optimization recommendations
        debt_recommendations = self._analyze_debt_optimization(financial_profile)
        recommendations.extend(debt_recommendations)
        
        # Spending optimization recommendations
        spending_recs = self._recommend_spending_optimizations(financial_profile)
        recommendations.extend(spending_recs)
        
        return {
            "recommendations": recommendations,
            "summary": self._generate_recommendation_summary(recommendations),
            "priority_actions": self._prioritize_recommendations(recommendations)
        }
    
    def _analyze_income_expenses(
        self, 
        db: Session, 
        user_id: str, 
        days: int
    ) -> Dict[str, Any]:
        """Analyze income vs expenses pattern"""
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get all transactions
        transactions = db.query(Transaction).join(BankAccount).filter(
            BankAccount.user_id == user_id,
            Transaction.date >= start_date
        ).all()
        
        total_income = 0
        total_expenses = 0
        income_transactions = []
        expense_transactions = []
        
        for tx in transactions:
            if tx.amount > 0:  # Income
                total_income += tx.amount
                income_transactions.append(tx)
            else:  # Expense
                total_expenses += abs(tx.amount)
                expense_transactions.append(tx)
        
        # Calculate monthly averages
        months = days / 30.0
        monthly_income = total_income / months if months > 0 else 0
        monthly_expenses = total_expenses / months if months > 0 else 0
        
        return {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "monthly_income": monthly_income,
            "monthly_expenses": monthly_expenses,
            "net_monthly": monthly_income - monthly_expenses,
            "expense_ratio": (monthly_expenses / monthly_income) if monthly_income > 0 else 0,
            "income_sources": self._analyze_income_sources(income_transactions),
            "expense_categories": self._analyze_expense_categories(expense_transactions)
        }
    
    def _calculate_savings_potential(
        self, 
        spending_analysis: Dict[str, Any], 
        recurring_analysis: List[Dict[str, Any]],
        income_expense_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate potential savings from various optimizations"""
        
        # Base savings from positive cash flow
        base_monthly_savings = max(0, income_expense_analysis["net_monthly"])
        
        # Potential savings from subscription optimization
        subscription_savings = self._calculate_subscription_savings(recurring_analysis)
        
        # Potential savings from spending category optimization
        category_savings = self._calculate_category_savings(spending_analysis)
        
        # Total potential savings
        total_potential = base_monthly_savings + subscription_savings + category_savings
        
        return {
            "current_monthly_savings": base_monthly_savings,
            "subscription_optimization_savings": subscription_savings,
            "category_optimization_savings": category_savings,
            "total_monthly_potential": total_potential,
            "annual_potential": total_potential * 12,
            "savings_rate": (base_monthly_savings / income_expense_analysis["monthly_income"]) 
                          if income_expense_analysis["monthly_income"] > 0 else 0
        }
    
    def _assess_risk_profile(
        self, 
        spending_analysis: Dict[str, Any], 
        income_expense_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess user's risk profile based on financial behavior"""
        
        # Factors that indicate risk tolerance
        expense_ratio = income_expense_analysis["expense_ratio"]
        spending_volatility = self._calculate_spending_volatility(spending_analysis)
        emergency_fund_capacity = income_expense_analysis["net_monthly"] * 6  # 6 months expenses
        
        # Risk scoring
        risk_score = 0
        
        # Lower expense ratio indicates higher risk capacity
        if expense_ratio < 0.5:
            risk_score += 3
        elif expense_ratio < 0.7:
            risk_score += 2
        elif expense_ratio < 0.9:
            risk_score += 1
        
        # Lower spending volatility indicates stability
        if spending_volatility < 0.2:
            risk_score += 2
        elif spending_volatility < 0.4:
            risk_score += 1
        
        # Determine risk level
        if risk_score >= 4:
            risk_level = "high"
        elif risk_score >= 2:
            risk_level = "moderate"
        else:
            risk_level = "low"
        
        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "expense_ratio": expense_ratio,
            "spending_volatility": spending_volatility,
            "recommended_emergency_fund": emergency_fund_capacity
        }
    
    def _recommend_emergency_fund(
        self, 
        savings_potential: Dict[str, Any], 
        spending_analysis: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Recommend emergency fund based on spending patterns"""
        
        monthly_expenses = spending_analysis["total_spent"] / (spending_analysis["period_days"] / 30)
        recommended_emergency_fund = monthly_expenses * 6  # 6 months of expenses
        
        if savings_potential["current_monthly_savings"] > 0:
            months_to_build = recommended_emergency_fund / savings_potential["current_monthly_savings"]
            
            return {
                "type": "emergency_fund",
                "priority": "high",
                "title": "Build Emergency Fund",
                "description": f"Build a ${recommended_emergency_fund:.0f} emergency fund (6 months of expenses)",
                "recommended_amount": recommended_emergency_fund,
                "monthly_contribution": min(
                    savings_potential["current_monthly_savings"] * 0.5, 
                    recommended_emergency_fund / 12
                ),
                "time_to_goal": f"{months_to_build:.1f} months",
                "investment_type": "high_yield_savings",
                "expected_return": 0.04  # 4% APY for high-yield savings
            }
        
        return None
    
    def _get_conservative_investments(
        self, 
        savings_potential: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get conservative investment recommendations"""
        
        monthly_capacity = savings_potential["total_monthly_potential"]
        recommendations = []
        
        if monthly_capacity >= 50:
            # High-yield savings account
            recommendations.append({
                "type": "high_yield_savings",
                "priority": "high",
                "title": "High-Yield Savings Account",
                "description": "Earn higher interest on your savings with FDIC protection",
                "recommended_allocation": min(monthly_capacity * 0.4, 500),
                "expected_return": 0.04,
                "risk_level": "very_low",
                "liquidity": "high"
            })
        
        if monthly_capacity >= 100:
            # Conservative bond funds
            recommendations.append({
                "type": "bond_fund",
                "priority": "medium",
                "title": "Conservative Bond Index Fund",
                "description": "Diversified bond portfolio for steady income",
                "recommended_allocation": min(monthly_capacity * 0.3, 300),
                "expected_return": 0.05,
                "risk_level": "low",
                "liquidity": "medium"
            })
        
        return recommendations
    
    def _get_growth_investments(
        self, 
        savings_potential: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get growth-oriented investment recommendations"""
        
        monthly_capacity = savings_potential["total_monthly_potential"]
        recommendations = []
        
        if monthly_capacity >= 100:
            # Stock market index funds
            recommendations.append({
                "type": "stock_index_fund",
                "priority": "high",
                "title": "Total Stock Market Index Fund",
                "description": "Diversified exposure to the entire stock market",
                "recommended_allocation": min(monthly_capacity * 0.6, 1000),
                "expected_return": 0.10,
                "risk_level": "medium",
                "liquidity": "high"
            })
        
        if monthly_capacity >= 200:
            # International diversification
            recommendations.append({
                "type": "international_fund",
                "priority": "medium",
                "title": "International Stock Index Fund",
                "description": "Diversify globally with international market exposure",
                "recommended_allocation": min(monthly_capacity * 0.2, 400),
                "expected_return": 0.08,
                "risk_level": "medium",
                "liquidity": "high"
            })
        
        return recommendations
    
    def _recommend_spending_optimizations(
        self, 
        financial_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Recommend spending optimizations to increase savings"""
        
        spending_analysis = financial_profile["spending_analysis"]
        recurring_transactions = financial_profile["recurring_transactions"]
        
        recommendations = []
        
        # Subscription optimization
        total_subscriptions = sum(
            tx["total_spent"] for tx in recurring_transactions 
            if "subscription" in tx["merchant"].lower() or "streaming" in tx["merchant"].lower()
        )
        
        if total_subscriptions > 50:  # More than $50/month in subscriptions
            recommendations.append({
                "type": "subscription_optimization",
                "priority": "medium",
                "title": "Optimize Subscriptions",
                "description": f"Review ${total_subscriptions:.0f}/month in subscriptions",
                "potential_savings": total_subscriptions * 0.3,  # Assume 30% can be saved
                "action_items": [
                    "Cancel unused subscriptions",
                    "Downgrade to cheaper plans",
                    "Share family plans",
                    "Use annual billing for discounts"
                ]
            })
        
        # High spending categories
        top_categories = spending_analysis["top_categories"]
        for category, amount in top_categories[:3]:
            if amount > 500:  # High spending category
                recommendations.append({
                    "type": "category_optimization",
                    "priority": "low",
                    "title": f"Optimize {category} Spending",
                    "description": f"High spending in {category}: ${amount:.0f}/month",
                    "potential_savings": amount * 0.15,  # 15% reduction potential
                    "suggestions": self._get_category_suggestions(category)
                })
        
        return recommendations
    
    def _get_category_suggestions(self, category: str) -> List[str]:
        """Get spending reduction suggestions for specific categories"""
        suggestions = {
            "Food and Drink": [
                "Cook more meals at home",
                "Use meal planning apps",
                "Buy generic brands",
                "Use grocery store loyalty programs"
            ],
            "Transportation": [
                "Use public transportation",
                "Carpool or rideshare",
                "Combine errands into single trips",
                "Consider gas rewards credit cards"
            ],
            "Entertainment": [
                "Look for free local events",
                "Use library resources",
                "Share streaming subscriptions",
                "Take advantage of happy hour pricing"
            ],
            "Shops": [
                "Use cashback apps",
                "Compare prices before buying",
                "Wait for sales and clearances",
                "Use coupon apps"
            ]
        }
        
        return suggestions.get(category, ["Review spending in this category"])
    
    def _prioritize_recommendations(
        self, 
        recommendations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Prioritize recommendations by importance and impact"""
        
        priority_order = {"high": 3, "medium": 2, "low": 1}
        
        return sorted(
            recommendations, 
            key=lambda x: (
                priority_order.get(x.get("priority", "low"), 1),
                x.get("potential_savings", x.get("recommended_allocation", 0))
            ),
            reverse=True
        )[:5]  # Top 5 recommendations
    
    def _calculate_spending_volatility(self, spending_analysis: Dict[str, Any]) -> float:
        """Calculate spending volatility from daily spending data"""
        daily_spending = spending_analysis.get("daily_spending", {})
        
        if len(daily_spending) < 7:
            return 1.0  # High volatility if insufficient data
        
        amounts = list(daily_spending.values())
        avg_spending = sum(amounts) / len(amounts)
        
        if avg_spending == 0:
            return 0.0
        
        variance = sum((amount - avg_spending) ** 2 for amount in amounts) / len(amounts)
        return (variance ** 0.5) / avg_spending  # Coefficient of variation
    
    def _load_investment_products(self) -> Dict[str, Any]:
        """Load available investment products and their characteristics"""
        return {
            "high_yield_savings": {
                "name": "High-Yield Savings Account",
                "expected_return": 0.04,
                "risk_level": "very_low",
                "minimum_investment": 1
            },
            "bond_fund": {
                "name": "Bond Index Fund",
                "expected_return": 0.05,
                "risk_level": "low",
                "minimum_investment": 100
            },
            "stock_index_fund": {
                "name": "Stock Index Fund",
                "expected_return": 0.10,
                "risk_level": "medium",
                "minimum_investment": 100
            }
        }
    
    def _load_savings_thresholds(self) -> Dict[str, float]:
        """Load savings thresholds for different recommendations"""
        return {
            "emergency_fund_months": 6,
            "minimum_investment": 50,
            "high_savings_threshold": 500
        }

# Initialize investment recommendation engine
investment_engine = InvestmentRecommendationEngine()