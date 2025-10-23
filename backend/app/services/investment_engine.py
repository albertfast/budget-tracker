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
        # Load configuration and defaults used across methods
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

    # Restored helper methods (minimal yet functional implementations)
    def _load_investment_products(self) -> Dict[str, Any]:
        """Define a small catalog of investment products with basic metadata."""
        return {
            "high_yield_savings": {
                "type": "cash",
                "risk": "low",
                "expected_return": 0.03,
                "liquidity": "high",
            },
            "bond_fund": {
                "type": "fixed_income",
                "risk": "low",
                "expected_return": 0.04,
                "liquidity": "medium",
            },
            "index_fund": {
                "type": "equity",
                "risk": "moderate",
                "expected_return": 0.07,
                "liquidity": "high",
            },
            "growth_etf": {
                "type": "equity",
                "risk": "high",
                "expected_return": 0.10,
                "liquidity": "high",
            },
        }

    def _load_savings_thresholds(self) -> Dict[str, Any]:
        """Basic savings and risk thresholds used in recommendations."""
        return {
            "emergency_fund_months_min": 3,
            "emergency_fund_months_target": 6,
            "min_investment_amount": 50.0,
            "max_position_size_pct": 20.0,
        }

    def _map_recommendation_to_direction(self, rec: str) -> str:
        rec_norm = (rec or "").lower()
        if rec_norm in ("strong_buy", "buy"):  # bullish
            return "bullish"
        if rec_norm in ("strong_sell", "sell"):  # bearish
            return "bearish"
        return "neutral"

    def _identify_key_combined_factors(
        self,
        technical_analysis: Dict[str, Any],
        fundamental_analysis: Dict[str, Any],
        weights: Dict[str, float],
    ) -> List[str]:
        """Summarize a few key factors from both analyses for explainability."""
        factors: List[str] = []
        # Technical drivers
        ma = technical_analysis.get("moving_average_analysis", {})
        if ma.get("golden_cross"):
            factors.append("50/200 MA golden cross")
        if ma.get("death_cross"):
            factors.append("50/200 MA death cross")
        fib = technical_analysis.get("fibonacci_analysis", {}).get("golden_ratio_analysis", {})
        if fib.get("strength", 0) > 60:
            factors.append("Strong golden ratio confluence")
        # Fundamental drivers
        health = fundamental_analysis.get("company_health", {})
        score = health.get("overall_score")
        if isinstance(score, (int, float)):
            if score >= 80:
                factors.append("Excellent fundamentals")
            elif score <= 40:
                factors.append("Weak fundamentals")
        growth = fundamental_analysis.get("growth_assessment", {})
        if growth.get("growth_score", 0) > 70:
            factors.append("Strong growth potential")
        # Weight emphasis
        if weights.get("fundamental", 0) > weights.get("technical", 0):
            factors.append("Fundamentals weighted more due to horizon/risk")
        else:
            factors.append("Technical momentum weighted more due to volatility")
        return factors[:6]

    def _calculate_optimal_position_size(
        self,
        recommendation: str,
        confidence: int,
        user_profile: Dict[str, Any],
        fundamental_analysis: Dict[str, Any],
    ) -> float:
        """Very simple position sizing rule-of-thumb in percent of portfolio."""
        base = 5.0  # baseline per position
        risk_level = user_profile.get("risk_profile", {}).get("risk_level", "moderate")
        if recommendation in ("strong_buy", "strong_sell"):
            base += 3.0
        elif recommendation in ("buy", "sell"):
            base += 1.5
        # Confidence scaling
        base *= (0.5 + (confidence / 200.0))  # 0.5x to ~1.0x
        # Risk tolerance
        if risk_level == "low":
            base *= 0.7
        elif risk_level == "high":
            base *= 1.3
        return float(min(base, self.savings_thresholds.get("max_position_size_pct", 20.0)))

    def _generate_investment_thesis(
        self,
        symbol: str,
        technical_analysis: Dict[str, Any],
        fundamental_analysis: Dict[str, Any],
        combined_analysis: Dict[str, Any],
    ) -> str:
        direction = combined_analysis.get("combined_direction", "neutral")
        score = combined_analysis.get("combined_score", 50)
        sector = fundamental_analysis.get("company_health", {}).get("sector", "")
        return (
            f"{symbol} shows {direction} conditions (score {int(score)}). "
            f"Technical signals and fundamental health suggest a risk-adjusted opportunity"
            + (f" within the {sector} sector." if sector else ".")
        )

    def _identify_investment_catalysts(
        self,
        technical_analysis: Dict[str, Any],
        fundamental_analysis: Dict[str, Any],
    ) -> List[str]:
        catalysts: List[str] = []
        # Earnings or revenue growth
        growth = fundamental_analysis.get("growth_assessment", {})
        if growth.get("revenue_growth_trend") == "improving":
            catalysts.append("Improving revenue growth")
        # Technical breakouts
        sr = technical_analysis.get("support_resistance", {})
        if sr.get("recent_breakout", False):
            catalysts.append("Recent resistance breakout")
        if not catalysts:
            catalysts.append("Favorable risk/reward setup")
        return catalysts

    def _identify_investment_risks(
        self,
        technical_analysis: Dict[str, Any],
        fundamental_analysis: Dict[str, Any],
        user_profile: Dict[str, Any],
    ) -> List[str]:
        risks: List[str] = []
        debt = fundamental_analysis.get("debt_analysis", {})
        if debt.get("debt_to_equity", 0) > 1.0:
            risks.append("Elevated leverage (D/E > 1)")
        trend = technical_analysis.get("trend_analysis", {})
        if trend.get("primary_trend") == "downtrend":
            risks.append("Prevailing downtrend")
        if not risks:
            risks.append("General market volatility")
        return risks

    def _define_monitoring_levels(
        self,
        technical_analysis: Dict[str, Any],
        price_targets: Dict[str, Any],
    ) -> Dict[str, Any]:
        sr = technical_analysis.get("support_resistance", {})
        supports = sr.get("support_levels", [])
        resistances = sr.get("resistance_levels", [])
        return {
            "watch_support": supports[:2],
            "watch_resistance": resistances[:2],
            "re_evaluate_below": price_targets.get("stop_loss"),
            "re_evaluate_above": price_targets.get("primary_target"),
        }

    def _define_exit_strategy(
        self,
        recommendation: str,
        price_targets: Dict[str, Any],
        time_horizon: Dict[str, Any],
        user_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "take_profit": price_targets.get("primary_target"),
            "stop_loss": price_targets.get("stop_loss"),
            "review_in": time_horizon,
            "notes": "Tighten stop on strong moves; scale out near resistance.",
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
    
    # Additional helper methods (restored minimal implementations)
    def _analyze_income_expenses(self, db: Session, user_id: str, days: int) -> Dict[str, Any]:
        """Compute simple income vs expenses over window and normalize monthly."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        txs: List[Transaction] = db.query(Transaction).join(BankAccount).filter(
            BankAccount.user_id == user_id,
            Transaction.date >= start_date,
            Transaction.date <= end_date,
        ).all()
        income = sum(tx.amount for tx in txs if tx.amount > 0)
        expenses = sum(-tx.amount for tx in txs if tx.amount < 0)
        scale = 30.0 / max(1, days)
        monthly_income = income * scale
        monthly_expenses = expenses * scale
        return {
            "period_days": days,
            "total_income": income,
            "total_expenses": expenses,
            "monthly_income": monthly_income,
            "monthly_expenses": monthly_expenses,
            "net_monthly": monthly_income - monthly_expenses,
        }

    def _calculate_savings_potential(
        self,
        spending_analysis: Dict[str, Any],
        recurring_analysis: List[Dict[str, Any]],
        income_expense: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Estimate potential savings from discretionary spend and subscriptions."""
        # Heuristic: 10% of avg daily spend times 30 plus 30% of recurring subs
        discretionary = (spending_analysis.get("avg_daily_spend", 0) * 30) * 0.10
        recurring_total = sum(item.get("amount", 0) for item in recurring_analysis if item.get("frequency") == "monthly")
        recurring_savings = recurring_total * 0.30
        total = max(0.0, income_expense.get("net_monthly", 0)) * 0.20 + discretionary + recurring_savings
        return {
            "from_discretionary": discretionary,
            "from_subscriptions": recurring_savings,
            "income_based": max(0.0, income_expense.get("net_monthly", 0)) * 0.20,
            "total_monthly_potential": total,
        }

    def _assess_risk_profile(
        self,
        spending_analysis: Dict[str, Any],
        income_expense: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Basic risk profile based on savings capacity and spending stability."""
        savings_capacity = income_expense.get("net_monthly", 0)
        avg_tx = spending_analysis.get("avg_transaction_amount", 0)
        if savings_capacity > 1000 and avg_tx < 100:
            level = "high"
        elif savings_capacity > 300:
            level = "moderate"
        else:
            level = "low"
        return {
            "risk_level": level,
            "notes": "Heuristic assessment based on cash flow and spending dispersion.",
        }

    def generate_investment_recommendations(self, financial_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Produce a simple, prioritized set of actions from the user's profile."""
        recs: List[Dict[str, Any]] = []
        monthly_net = financial_profile.get("income_expense_analysis", {}).get("net_monthly", 0)
        savings_potential = financial_profile.get("savings_potential", {}).get("total_monthly_potential", 0)
        risk_level = financial_profile.get("risk_profile", {}).get("risk_level", "moderate")

        # 1) Emergency fund
        recs.append({
            "type": "cash_reserve",
            "priority": "high",
            "title": "Build Emergency Fund (3-6 months)",
            "description": "Maintain 3-6 months of expenses in high-yield savings.",
            "recommended_allocation": 40.0,
            "expected_return": self.investment_products["high_yield_savings"]["expected_return"],
            "risk_level": "low",
        })

        # 2) Core diversified equity
        equity_alloc = 40.0 if risk_level != "low" else 25.0
        recs.append({
            "type": "core_equity",
            "priority": "medium",
            "title": "Low-Cost Index Fund",
            "description": "Dollar-cost average into a broad market index fund.",
            "recommended_allocation": equity_alloc,
            "expected_return": self.investment_products["index_fund"]["expected_return"],
            "risk_level": "moderate",
        })

        # 3) Bonds for stability
        bond_alloc = 20.0 if risk_level == "low" else 10.0
        recs.append({
            "type": "bonds",
            "priority": "medium",
            "title": "Bond Fund for Stability",
            "description": "Add bonds to reduce volatility and drawdowns.",
            "recommended_allocation": bond_alloc,
            "expected_return": self.investment_products["bond_fund"]["expected_return"],
            "risk_level": "low",
        })

        summary = {
            "monthly_investable": max(0.0, monthly_net) + savings_potential,
            "risk_level": risk_level,
        }
        return {"recommendations": recs, "summary": summary, "priority_actions": [r["title"] for r in recs[:2]]}

# Initialize investment recommendation engine
investment_engine = AdvancedInvestmentRecommendationEngine()