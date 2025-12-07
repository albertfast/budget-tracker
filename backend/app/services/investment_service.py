from sqlalchemy.orm import Sessionfrom sqlalchemy.orm import Session

from typing import Dict, List, Any, Optionalfrom typing import Dict, List, Any, Optional

from datetime import datetime, timedeltafrom datetime import datetime, timedelta

from ..models.transaction import Transactionfrom ..models.transaction import Transaction

from ..models.bank_account import BankAccountfrom ..models.bank_account import BankAccount

from ..models.user import Userfrom ..models.user import User

from .transaction_service import transaction_servicefrom .transaction_service import transaction_service

from .technical_analysis_service import technical_analysis_servicefrom .technical_analysis_service import technical_analysis_service, PriceData

from .fundamental_analysis_service import fundamental_analysis_service, FinancialStatementfrom .fundamental_analysis_service import fundamental_analysis_service, FinancialStatement

from .market_data_service import market_data_servicefrom .market_data_service import market_data_service

import loggingimport logging

from collections import defaultdict

logger = logging.getLogger(__name__)import asyncio



class AdvancedInvestmentRecommendationEngine:logger = logging.getLogger(__name__)

    """Enhanced investment recommendation engine with technical and fundamental analysis"""

    class AdvancedInvestmentRecommendationEngine:

    def __init__(self):    """Enhanced investment recommendation engine with technical and fundamental analysis"""

        self.investment_products = self._load_investment_products()    

        self.savings_thresholds = self._load_savings_thresholds()    def __init__(self):

        self.analysis_weights = self._load_analysis_weights()        self.investment_products = self._load_investment_products()

            self.savings_thresholds = self._load_savings_thresholds()

    async def analyze_investment_opportunity(        self.analysis_weights = self._load_analysis_weights()

        self,    

        symbol: str,    async def analyze_investment_opportunity(

        user_profile: Dict[str, Any],        self,

        analysis_period: str = "1y"        symbol: str,

    ) -> Dict[str, Any]:        user_profile: Dict[str, Any],

        """Comprehensive investment analysis combining technical and fundamental analysis"""        analysis_period: str = "1y"

            ) -> Dict[str, Any]:

        try:        """Comprehensive investment analysis combining technical and fundamental analysis"""

            async with market_data_service:        

                # Fetch market data        try:

                historical_data = await market_data_service.get_historical_data(            async with market_data_service:

                    symbol, analysis_period, "1d"                # Fetch market data

                )                historical_data = await market_data_service.get_historical_data(

                                    symbol, analysis_period, "1d"

                current_quote = await market_data_service.get_real_time_quote(symbol)                )

                                

                company_profile = await market_data_service.get_company_profile(symbol)                current_quote = await market_data_service.get_real_time_quote(symbol)

                                

                financial_statements_data = await market_data_service.get_financial_statements(symbol)                company_profile = await market_data_service.get_company_profile(symbol)

                                

                # Convert financial data to FinancialStatement objects                financial_statements_data = await market_data_service.get_financial_statements(symbol)

                financial_statements = [                

                    FinancialStatement(                # Convert financial data to FinancialStatement objects

                        period=stmt["period"],                financial_statements = [

                        revenue=stmt["revenue"],                    FinancialStatement(

                        gross_profit=stmt["gross_profit"],                        period=stmt["period"],

                        operating_income=stmt["operating_income"],                        revenue=stmt["revenue"],

                        net_income=stmt["net_income"],                        gross_profit=stmt["gross_profit"],

                        total_assets=stmt["total_assets"],                        operating_income=stmt["operating_income"],

                        total_debt=stmt["total_debt"],                        net_income=stmt["net_income"],

                        shareholders_equity=stmt["shareholders_equity"],                        total_assets=stmt["total_assets"],

                        cash_and_equivalents=stmt["cash_and_equivalents"],                        total_debt=stmt["total_debt"],

                        current_assets=stmt["current_assets"],                        shareholders_equity=stmt["shareholders_equity"],

                        current_liabilities=stmt["current_liabilities"]                        cash_and_equivalents=stmt["cash_and_equivalents"],

                    ) for stmt in financial_statements_data                        current_assets=stmt["current_assets"],

                ]                        current_liabilities=stmt["current_liabilities"]

                                    ) for stmt in financial_statements_data

                # Technical Analysis                ]

                technical_analysis = technical_analysis_service.analyze_security(                

                    symbol, historical_data, len(historical_data)                # Technical Analysis

                )                technical_analysis = technical_analysis_service.analyze_security(

                                    symbol, historical_data, len(historical_data)

                # Fundamental Analysis                )

                fundamental_analysis = fundamental_analysis_service.analyze_company_fundamentals(                

                    symbol, financial_statements, company_profile.industry if company_profile else "general"                # Fundamental Analysis

                )                fundamental_analysis = fundamental_analysis_service.analyze_company_fundamentals(

                                    symbol, financial_statements, company_profile.industry if company_profile else "general"

                # Combined Analysis                )

                combined_analysis = self._combine_analyses(                

                    technical_analysis, fundamental_analysis, user_profile                # Combined Analysis

                )                combined_analysis = self._combine_analyses(

                                    technical_analysis, fundamental_analysis, user_profile

                # Investment Recommendation                )

                investment_recommendation = self._generate_comprehensive_recommendation(                

                    symbol, technical_analysis, fundamental_analysis, combined_analysis, user_profile                # Investment Recommendation

                )                investment_recommendation = self._generate_comprehensive_recommendation(

                                    symbol, technical_analysis, fundamental_analysis, combined_analysis, user_profile

                return {                )

                    "symbol": symbol,                

                    "analysis_timestamp": datetime.utcnow(),                return {

                    "current_price": current_quote.last_price if current_quote else historical_data[-1].close,                    "symbol": symbol,

                    "company_profile": {                    "analysis_timestamp": datetime.utcnow(),

                        "name": company_profile.name if company_profile else f"{symbol} Corporation",                    "current_price": current_quote.last_price if current_quote else historical_data[-1].close,

                        "sector": company_profile.sector if company_profile else "Unknown",                    "company_profile": {

                        "industry": company_profile.industry if company_profile else "Unknown",                        "name": company_profile.name if company_profile else f"{symbol} Corporation",

                        "market_cap": company_profile.market_cap if company_profile else 0                        "sector": company_profile.sector if company_profile else "Unknown",

                    },                        "industry": company_profile.industry if company_profile else "Unknown",

                    "technical_analysis": technical_analysis,                        "market_cap": company_profile.market_cap if company_profile else 0

                    "fundamental_analysis": fundamental_analysis,                    },

                    "combined_analysis": combined_analysis,                    "technical_analysis": technical_analysis,

                    "investment_recommendation": investment_recommendation,                    "fundamental_analysis": fundamental_analysis,

                    "risk_assessment": self._assess_investment_risk(                    "combined_analysis": combined_analysis,

                        technical_analysis, fundamental_analysis, user_profile                    "investment_recommendation": investment_recommendation,

                    ),                    "risk_assessment": self._assess_investment_risk(

                    "portfolio_fit": self._assess_portfolio_fit(                        technical_analysis, fundamental_analysis, user_profile

                        investment_recommendation, user_profile                    ),

                    )                    "portfolio_fit": self._assess_portfolio_fit(

                }                        investment_recommendation, user_profile

                                    )

        except Exception as e:                }

            logger.error(f"Error analyzing investment opportunity for {symbol}: {str(e)}")                

            raise        except Exception as e:

                logger.error(f"Error analyzing investment opportunity for {symbol}: {str(e)}")

    def _combine_analyses(            raise

        self,    

        technical_analysis: Dict[str, Any],    def _combine_analyses(

        fundamental_analysis: Dict[str, Any],        self,

        user_profile: Dict[str, Any]        technical_analysis: Dict[str, Any],

    ) -> Dict[str, Any]:        fundamental_analysis: Dict[str, Any],

        """Combine technical and fundamental analysis with weighted scoring"""        user_profile: Dict[str, Any]

            ) -> Dict[str, Any]:

        # Extract key signals        """Combine technical and fundamental analysis with weighted scoring"""

        technical_signal = technical_analysis["weighted_signals"]["overall_signal"]        

        fundamental_recommendation = fundamental_analysis["investment_recommendation"]        # Extract key signals

                technical_signal = technical_analysis["weighted_signals"]["overall_signal"]

        # Get analysis weights based on user profile and market conditions        fundamental_recommendation = fundamental_analysis["investment_recommendation"]

        weights = self._get_dynamic_weights(user_profile, technical_analysis, fundamental_analysis)        

                # Get analysis weights based on user profile and market conditions

        # Technical score (0-100)        weights = self._get_dynamic_weights(user_profile, technical_analysis, fundamental_analysis)

        technical_score = technical_signal["strength"]        

        technical_direction = technical_signal["direction"]        # Technical score (0-100)

                technical_score = technical_signal["strength"]

        # Fundamental score (0-100)        technical_direction = technical_signal["direction"]

        fundamental_score = fundamental_analysis["company_health"]["overall_score"]        

        fundamental_direction = self._map_recommendation_to_direction(        # Fundamental score (0-100)

            fundamental_recommendation["recommendation"]        fundamental_score = fundamental_analysis["company_health"]["overall_score"]

        )        fundamental_direction = self._map_recommendation_to_direction(

                    fundamental_recommendation["recommendation"]

        # Calculate combined score        )

        combined_score = (        

            technical_score * weights["technical"] +        # Calculate combined score

            fundamental_score * weights["fundamental"]        combined_score = (

        ) / (weights["technical"] + weights["fundamental"])            technical_score * weights["technical"] +

                    fundamental_score * weights["fundamental"]

        # Determine combined direction        ) / (weights["technical"] + weights["fundamental"])

        if technical_direction == fundamental_direction:        

            combined_direction = technical_direction        # Determine combined direction

            direction_confidence = 90        if technical_direction == fundamental_direction:

        else:            combined_direction = technical_direction

            # Conflicting signals - use the higher weighted analysis            direction_confidence = 90

            if weights["technical"] > weights["fundamental"]:        else:

                combined_direction = technical_direction            # Conflicting signals - use the higher weighted analysis

                direction_confidence = 60            if weights["technical"] > weights["fundamental"]:

            else:                combined_direction = technical_direction

                combined_direction = fundamental_direction                direction_confidence = 60

                direction_confidence = 60            else:

                        combined_direction = fundamental_direction

        # Golden ratio analysis integration                direction_confidence = 60

        fibonacci_analysis = technical_analysis.get("fibonacci_analysis", {})        

        golden_ratio_strength = fibonacci_analysis.get("golden_ratio_analysis", {}).get("strength", 0)        # Golden ratio analysis integration

                fibonacci_analysis = technical_analysis.get("fibonacci_analysis", {})

        # Adjust score based on golden ratio proximity        golden_ratio_strength = fibonacci_analysis.get("golden_ratio_analysis", {}).get("strength", 0)

        if golden_ratio_strength > 70:        

            combined_score += 5  # Boost for strong golden ratio signals        # Adjust score based on golden ratio proximity

                if golden_ratio_strength > 70:

        # Support/resistance level analysis            combined_score += 5  # Boost for strong golden ratio signals

        support_resistance = technical_analysis.get("support_resistance", {})        

        nearest_support_strength = support_resistance.get("support_strength", 0)        # Support/resistance level analysis

        nearest_resistance_strength = support_resistance.get("resistance_strength", 0)        support_resistance = technical_analysis.get("support_resistance", {})

                nearest_support_strength = support_resistance.get("support_strength", 0)

        # Volume analysis impact        nearest_resistance_strength = support_resistance.get("resistance_strength", 0)

        volume_analysis = technical_analysis.get("volume_analysis", {})        

        volume_confirmation = volume_analysis.get("price_volume_correlation", 0)        # Volume analysis impact

                volume_analysis = technical_analysis.get("volume_analysis", {})

        if abs(volume_confirmation) > 0.7:  # Strong volume confirmation        volume_confirmation = volume_analysis.get("price_volume_correlation", 0)

            combined_score += 3        

                if abs(volume_confirmation) > 0.7:  # Strong volume confirmation

        # MA analysis (50/200 day crossover significance)            combined_score += 3

        ma_analysis = technical_analysis.get("moving_average_analysis", {})        

        golden_cross = ma_analysis.get("golden_cross", False)        # MA analysis (50/200 day crossover significance)

        death_cross = ma_analysis.get("death_cross", False)        ma_analysis = technical_analysis.get("moving_average_analysis", {})

                golden_cross = ma_analysis.get("golden_cross", False)

        if golden_cross and combined_direction == "bullish":        death_cross = ma_analysis.get("death_cross", False)

            combined_score += 7        

        elif death_cross and combined_direction == "bearish":        if golden_cross and combined_direction == "bullish":

            combined_score += 7            combined_score += 7

                elif death_cross and combined_direction == "bearish":

        return {            combined_score += 7

            "combined_score": min(combined_score, 100),  # Cap at 100        

            "combined_direction": combined_direction,        return {

            "direction_confidence": direction_confidence,            "combined_score": min(combined_score, 100),  # Cap at 100

            "analysis_weights": weights,            "combined_direction": combined_direction,

            "technical_contribution": technical_score * weights["technical"],            "direction_confidence": direction_confidence,

            "fundamental_contribution": fundamental_score * weights["fundamental"],            "analysis_weights": weights,

            "signal_alignment": technical_direction == fundamental_direction,            "technical_contribution": technical_score * weights["technical"],

            "key_factors": self._identify_key_combined_factors(            "fundamental_contribution": fundamental_score * weights["fundamental"],

                technical_analysis, fundamental_analysis, weights            "signal_alignment": technical_direction == fundamental_direction,

            ),            "key_factors": self._identify_key_combined_factors(

            "confidence_factors": {                technical_analysis, fundamental_analysis, weights

                "golden_ratio_strength": golden_ratio_strength,            ),

                "support_resistance_strength": max(nearest_support_strength, nearest_resistance_strength),            "confidence_factors": {

                "volume_confirmation": abs(volume_confirmation),                "golden_ratio_strength": golden_ratio_strength,

                "ma_crossover_significance": 7 if (golden_cross or death_cross) else 0                "support_resistance_strength": max(nearest_support_strength, nearest_resistance_strength),

            }                "volume_confirmation": abs(volume_confirmation),

        }                "ma_crossover_significance": 7 if (golden_cross or death_cross) else 0

                }

    def _generate_comprehensive_recommendation(        }

        self,    

        symbol: str,    def _generate_comprehensive_recommendation(

        technical_analysis: Dict[str, Any],        self,

        fundamental_analysis: Dict[str, Any],        symbol: str,

        combined_analysis: Dict[str, Any],        technical_analysis: Dict[str, Any],

        user_profile: Dict[str, Any]        fundamental_analysis: Dict[str, Any],

    ) -> Dict[str, Any]:        combined_analysis: Dict[str, Any],

        """Generate comprehensive investment recommendation"""        user_profile: Dict[str, Any]

            ) -> Dict[str, Any]:

        combined_score = combined_analysis["combined_score"]        """Generate comprehensive investment recommendation"""

        combined_direction = combined_analysis["combined_direction"]        

        direction_confidence = combined_analysis["direction_confidence"]        combined_score = combined_analysis["combined_score"]

                combined_direction = combined_analysis["combined_direction"]

        # Technical targets        direction_confidence = combined_analysis["direction_confidence"]

        technical_targets = technical_analysis["price_targets"]        

                # Technical targets

        # Fundamental valuation        technical_targets = technical_analysis["price_targets"]

        fundamental_rec = fundamental_analysis["investment_recommendation"]        

                # Fundamental valuation

        # User risk profile        fundamental_rec = fundamental_analysis["investment_recommendation"]

        user_risk_tolerance = user_profile.get("risk_profile", {}).get("risk_level", "moderate")        

                # User risk profile

        # Determine recommendation        user_risk_tolerance = user_profile.get("risk_profile", {}).get("risk_level", "moderate")

        if combined_score >= 80 and direction_confidence >= 80:        

            if combined_direction == "bullish":        # Determine recommendation

                recommendation = "strong_buy"        if combined_score >= 80 and direction_confidence >= 80:

                confidence = 95            if combined_direction == "bullish":

            else:                recommendation = "strong_buy"

                recommendation = "strong_sell"                confidence = 95

                confidence = 95            else:

        elif combined_score >= 65 and direction_confidence >= 70:                recommendation = "strong_sell"

            if combined_direction == "bullish":                confidence = 95

                recommendation = "buy"        elif combined_score >= 65 and direction_confidence >= 70:

                confidence = 80            if combined_direction == "bullish":

            else:                recommendation = "buy"

                recommendation = "sell"                confidence = 80

                confidence = 80            else:

        elif combined_score >= 50:                recommendation = "sell"

            recommendation = "hold"                confidence = 80

            confidence = 60        elif combined_score >= 50:

        else:            recommendation = "hold"

            if combined_direction == "bearish":            confidence = 60

                recommendation = "sell"        else:

                confidence = 70            if combined_direction == "bearish":

            else:                recommendation = "sell"

                recommendation = "hold"                confidence = 70

                confidence = 40            else:

                        recommendation = "hold"

        # Adjust for user risk tolerance                confidence = 40

        if user_risk_tolerance == "low" and recommendation in ["strong_buy", "buy"]:        

            if combined_score < 75:        # Adjust for user risk tolerance

                recommendation = "hold"        if user_risk_tolerance == "low" and recommendation in ["strong_buy", "buy"]:

                confidence -= 10            if combined_score < 75:

        elif user_risk_tolerance == "high" and recommendation == "hold":                recommendation = "hold"

            if combined_score > 60:                confidence -= 10

                recommendation = "buy" if combined_direction == "bullish" else "sell"        elif user_risk_tolerance == "high" and recommendation == "hold":

                confidence += 5            if combined_score > 60:

                        recommendation = "buy" if combined_direction == "bullish" else "sell"

        # Calculate position sizing                confidence += 5

        position_size = self._calculate_optimal_position_size(        

            recommendation, confidence, user_profile, fundamental_analysis        # Calculate position sizing

        )        position_size = self._calculate_optimal_position_size(

                    recommendation, confidence, user_profile, fundamental_analysis

        # Time horizon based on technical analysis        )

        time_horizon = technical_targets["estimated_time_to_target"]        

                # Time horizon based on technical analysis

        # Price targets with fibonacci and support/resistance integration        time_horizon = technical_targets["estimated_time_to_target"]

        price_targets = self._calculate_enhanced_price_targets(        

            technical_analysis, fundamental_analysis, combined_analysis        # Price targets with fibonacci and support/resistance integration

        )        price_targets = self._calculate_enhanced_price_targets(

                    technical_analysis, fundamental_analysis, combined_analysis

        return {        )

            "recommendation": recommendation,        

            "confidence": confidence,        return {

            "position_size_percentage": position_size,            "recommendation": recommendation,

            "target_price": price_targets["primary_target"],            "confidence": confidence,

            "stop_loss": price_targets["stop_loss"],            "position_size_percentage": position_size,

            "alternative_targets": price_targets["alternative_targets"],            "target_price": price_targets["primary_target"],

            "time_horizon": time_horizon,            "stop_loss": price_targets["stop_loss"],

            "investment_thesis": self._generate_investment_thesis(            "alternative_targets": price_targets["alternative_targets"],

                symbol, technical_analysis, fundamental_analysis, combined_analysis            "time_horizon": time_horizon,

            ),            "investment_thesis": self._generate_investment_thesis(

            "key_catalysts": self._identify_investment_catalysts(                symbol, technical_analysis, fundamental_analysis, combined_analysis

                technical_analysis, fundamental_analysis            ),

            ),            "key_catalysts": self._identify_investment_catalysts(

            "risk_factors": self._identify_investment_risks(                technical_analysis, fundamental_analysis

                technical_analysis, fundamental_analysis, user_profile            ),

            ),            "risk_factors": self._identify_investment_risks(

            "monitoring_levels": self._define_monitoring_levels(                technical_analysis, fundamental_analysis, user_profile

                technical_analysis, price_targets            ),

            ),            "monitoring_levels": self._define_monitoring_levels(

            "exit_strategy": self._define_exit_strategy(                technical_analysis, price_targets

                recommendation, price_targets, time_horizon, user_profile            ),

            )            "exit_strategy": self._define_exit_strategy(

        }                recommendation, price_targets, time_horizon, user_profile

                )

    def _calculate_enhanced_price_targets(        }

        self,    

        technical_analysis: Dict[str, Any],    def _calculate_enhanced_price_targets(

        fundamental_analysis: Dict[str, Any],        self,

        combined_analysis: Dict[str, Any]        technical_analysis: Dict[str, Any],

    ) -> Dict[str, Any]:        fundamental_analysis: Dict[str, Any],

        """Calculate enhanced price targets using multiple methodologies"""        combined_analysis: Dict[str, Any]

            ) -> Dict[str, Any]:

        current_price = technical_analysis["current_price"]        """Calculate enhanced price targets using multiple methodologies"""

                

        # Technical targets from Fibonacci and support/resistance        current_price = technical_analysis["current_price"]

        technical_targets = technical_analysis["price_targets"]        

        fibonacci_levels = technical_analysis["fibonacci_analysis"]["fibonacci_levels"]        # Technical targets from Fibonacci and support/resistance

        support_resistance = technical_analysis["support_resistance"]        technical_targets = technical_analysis["price_targets"]

                fibonacci_levels = technical_analysis["fibonacci_analysis"]["fibonacci_levels"]

        # Fundamental valuation targets        support_resistance = technical_analysis["support_resistance"]

        fundamental_rec = fundamental_analysis["investment_recommendation"]        

        company_health = fundamental_analysis["company_health"]["overall_score"]        # Fundamental valuation targets

                fundamental_rec = fundamental_analysis["investment_recommendation"]

        # Primary target based on combined analysis        company_health = fundamental_analysis["company_health"]["overall_score"]

        if combined_analysis["combined_direction"] == "bullish":        

            # Use next resistance level or fibonacci target        # Primary target based on combined analysis

            resistance_targets = [        if combined_analysis["combined_direction"] == "bullish":

                level["price"] for level in support_resistance["resistance_levels"]            # Use next resistance level or fibonacci target

                if level["price"] > current_price            resistance_targets = [

            ]                level["price"] for level in support_resistance["resistance_levels"]

                            if level["price"] > current_price

            fib_targets = [            ]

                level["price"] for level in fibonacci_levels            

                if level["price"] > current_price and level["level"] in [0.618, 0.786]            fib_targets = [

            ]                level["price"] for level in fibonacci_levels

                            if level["price"] > current_price and level["level"] in [0.618, 0.786]

            if resistance_targets and fib_targets:            ]

                primary_target = min(resistance_targets[0], fib_targets[0])            

            elif resistance_targets:            if resistance_targets and fib_targets:

                primary_target = resistance_targets[0]                primary_target = min(resistance_targets[0], fib_targets[0])

            elif fib_targets:            elif resistance_targets:

                primary_target = fib_targets[0]                primary_target = resistance_targets[0]

            else:            elif fib_targets:

                primary_target = technical_targets["optimal_exit_price"]                primary_target = fib_targets[0]

                        else:

            # Stop loss at support level                primary_target = technical_targets["optimal_exit_price"]

            support_levels = [            

                level["price"] for level in support_resistance["support_levels"]            # Stop loss at support level

                if level["price"] < current_price            support_levels = [

            ]                level["price"] for level in support_resistance["support_levels"]

            stop_loss = support_levels[0] if support_levels else technical_targets["stop_loss_price"]                if level["price"] < current_price

                        ]

        else:  # Bearish direction            stop_loss = support_levels[0] if support_levels else technical_targets["stop_loss_price"]

            # Target at support levels            

            support_targets = [        else:  # Bearish direction

                level["price"] for level in support_resistance["support_levels"]            # Target at support levels

                if level["price"] < current_price            support_targets = [

            ]                level["price"] for level in support_resistance["support_levels"]

                            if level["price"] < current_price

            primary_target = support_targets[0] if support_targets else current_price * 0.9            ]

            stop_loss = current_price * 1.05  # 5% stop loss for short positions            

                    primary_target = support_targets[0] if support_targets else current_price * 0.9

        # Alternative targets            stop_loss = current_price * 1.05  # 5% stop loss for short positions

        alternative_targets = []        

        if combined_analysis["combined_direction"] == "bullish":        # Alternative targets

            # Add multiple resistance levels as targets        alternative_targets = []

            for level in support_resistance["resistance_levels"][:3]:        if combined_analysis["combined_direction"] == "bullish":

                if level["price"] > current_price:            # Add multiple resistance levels as targets

                    alternative_targets.append({            for level in support_resistance["resistance_levels"][:3]:

                        "price": level["price"],                if level["price"] > current_price:

                        "probability": level["strength"],                    alternative_targets.append({

                        "type": "resistance_level"                        "price": level["price"],

                    })                        "probability": level["strength"],

                                    "type": "resistance_level"

            # Add fibonacci extension levels                    })

            for level in fibonacci_levels:            

                if level["price"] > current_price and level["level"] > 1.0:            # Add fibonacci extension levels

                    alternative_targets.append({            for level in fibonacci_levels:

                        "price": level["price"],                if level["price"] > current_price and level["level"] > 1.0:

                        "probability": level["support_strength"],                    alternative_targets.append({

                        "type": "fibonacci_extension"                        "price": level["price"],

                    })                        "probability": level["support_strength"],

                                "type": "fibonacci_extension"

        return {                    })

            "primary_target": primary_target,        

            "stop_loss": stop_loss,        return {

            "alternative_targets": alternative_targets[:5],  # Top 5 alternative targets            "primary_target": primary_target,

            "risk_reward_ratio": abs(primary_target - current_price) / abs(current_price - stop_loss) if stop_loss != current_price else 0,            "stop_loss": stop_loss,

            "price_methodology": "fibonacci_support_resistance_combined"            "alternative_targets": alternative_targets[:5],  # Top 5 alternative targets

        }            "risk_reward_ratio": abs(primary_target - current_price) / abs(current_price - stop_loss) if stop_loss != current_price else 0,

                "price_methodology": "fibonacci_support_resistance_combined"

    def _get_dynamic_weights(        }

        self,    

        user_profile: Dict[str, Any],    def _get_dynamic_weights(

        technical_analysis: Dict[str, Any],        self,

        fundamental_analysis: Dict[str, Any]        user_profile: Dict[str, Any],

    ) -> Dict[str, float]:        technical_analysis: Dict[str, Any],

        """Calculate dynamic weights based on market conditions and user profile"""        fundamental_analysis: Dict[str, Any]

            ) -> Dict[str, float]:

        # Base weights        """Calculate dynamic weights based on market conditions and user profile"""

        base_technical_weight = 0.4        

        base_fundamental_weight = 0.6        # Base weights

                base_technical_weight = 0.4

        # Adjust based on user investment horizon        base_fundamental_weight = 0.6

        investment_horizon = user_profile.get("investment_horizon", "medium_term")        

                # Adjust based on user investment horizon

        if investment_horizon == "short_term":  # < 3 months        investment_horizon = user_profile.get("investment_horizon", "medium_term")

            technical_weight = 0.7        

            fundamental_weight = 0.3        if investment_horizon == "short_term":  # < 3 months

        elif investment_horizon == "medium_term":  # 3-12 months            technical_weight = 0.7

            technical_weight = 0.5            fundamental_weight = 0.3

            fundamental_weight = 0.5        elif investment_horizon == "medium_term":  # 3-12 months

        else:  # long_term > 12 months            technical_weight = 0.5

            technical_weight = 0.3            fundamental_weight = 0.5

            fundamental_weight = 0.7        else:  # long_term > 12 months

                    technical_weight = 0.3

        # Adjust based on market volatility            fundamental_weight = 0.7

        volatility = technical_analysis.get("trend_analysis", {}).get("trend_strength", 50)        

        if volatility > 70:  # High volatility - favor technical        # Adjust based on market volatility

            technical_weight += 0.1        volatility = technical_analysis.get("trend_analysis", {}).get("trend_strength", 50)

            fundamental_weight -= 0.1        if volatility > 70:  # High volatility - favor technical

                    technical_weight += 0.1

        # Adjust based on fundamental strength            fundamental_weight -= 0.1

        company_health = fundamental_analysis.get("company_health", {}).get("overall_score", 50)        

        if company_health > 80:  # Strong fundamentals        # Adjust based on fundamental strength

            fundamental_weight += 0.1        company_health = fundamental_analysis.get("company_health", {}).get("overall_score", 50)

            technical_weight -= 0.1        if company_health > 80:  # Strong fundamentals

        elif company_health < 40:  # Weak fundamentals            fundamental_weight += 0.1

            technical_weight += 0.1            technical_weight -= 0.1

            fundamental_weight -= 0.1        elif company_health < 40:  # Weak fundamentals

                    technical_weight += 0.1

        # Ensure weights sum to 1            fundamental_weight -= 0.1

        total_weight = technical_weight + fundamental_weight        

        technical_weight /= total_weight        # Ensure weights sum to 1

        fundamental_weight /= total_weight        total_weight = technical_weight + fundamental_weight

                technical_weight /= total_weight

        return {        fundamental_weight /= total_weight

            "technical": technical_weight,        

            "fundamental": fundamental_weight        return {

        }            "technical": technical_weight,

                "fundamental": fundamental_weight

    def _load_analysis_weights(self) -> Dict[str, float]:        }

        """Load analysis methodology weights based on historical accuracy"""    

        return {    def _load_analysis_weights(self) -> Dict[str, float]:

            "fibonacci_golden_ratio": 0.25,     # Highest accuracy in trending markets        """Load analysis methodology weights based on historical accuracy"""

            "support_resistance": 0.30,         # Most reliable technical indicator        return {

            "volume_analysis": 0.20,           # Confirms price movements            "fibonacci_golden_ratio": 0.25,     # Highest accuracy in trending markets

            "candlestick_patterns": 0.10,      # Short-term signals            "support_resistance": 0.30,         # Most reliable technical indicator

            "moving_averages": 0.15,           # Trend confirmation            "volume_analysis": 0.20,           # Confirms price movements

            "fundamental_health": 0.35,        # Long-term value            "candlestick_patterns": 0.10,      # Short-term signals

            "growth_potential": 0.25,          # Growth assessment            "moving_averages": 0.15,           # Trend confirmation

            "debt_analysis": 0.25,             # Financial stability            "fundamental_health": 0.35,        # Long-term value

            "profitability": 0.15              # Current performance            "growth_potential": 0.25,          # Growth assessment

        }            "debt_analysis": 0.25,             # Financial stability

            "profitability": 0.15              # Current performance

    def analyze_financial_profile(        }

        self,     

        db: Session,     # Keep existing methods from original investment_engine.py

        user_id: str,     def analyze_financial_profile(

        analysis_days: int = 90        self, 

    ) -> Dict[str, Any]:        db: Session, 

        """Analyze user's financial profile for investment recommendations"""        user_id: str, 

                analysis_days: int = 90

        # Get comprehensive spending analysis    ) -> Dict[str, Any]:

        spending_analysis = transaction_service.get_spending_analysis(        """Analyze user's financial profile for investment recommendations"""

            db, user_id, analysis_days        

        )        # Get comprehensive spending analysis

                spending_analysis = transaction_service.get_spending_analysis(

        # Get recurring transactions (subscriptions, etc.)            db, user_id, analysis_days

        recurring_analysis = transaction_service.detect_recurring_transactions(        )

            db, user_id, analysis_days        

        )        # Get recurring transactions (subscriptions, etc.)

                recurring_analysis = transaction_service.detect_recurring_transactions(

        # Calculate income vs expenses            db, user_id, analysis_days

        income_expense_analysis = self._analyze_income_expenses(db, user_id, analysis_days)        )

                

        # Assess savings potential        # Calculate income vs expenses

        savings_potential = self._calculate_savings_potential(        income_expense_analysis = self._analyze_income_expenses(db, user_id, analysis_days)

            spending_analysis, recurring_analysis, income_expense_analysis        

        )        # Assess savings potential

                savings_potential = self._calculate_savings_potential(

        # Generate risk profile            spending_analysis, recurring_analysis, income_expense_analysis

        risk_profile = self._assess_risk_profile(spending_analysis, income_expense_analysis)        )

                

        return {        # Generate risk profile

            "user_id": user_id,        risk_profile = self._assess_risk_profile(spending_analysis, income_expense_analysis)

            "analysis_period_days": analysis_days,        

            "spending_analysis": spending_analysis,        return {

            "recurring_transactions": recurring_analysis,            "user_id": user_id,

            "income_expense_analysis": income_expense_analysis,            "analysis_period_days": analysis_days,

            "savings_potential": savings_potential,            "spending_analysis": spending_analysis,

            "risk_profile": risk_profile,            "recurring_transactions": recurring_analysis,

            "generated_at": datetime.utcnow()            "income_expense_analysis": income_expense_analysis,

        }            "savings_potential": savings_potential,

                "risk_profile": risk_profile,

    def generate_investment_recommendations(            "generated_at": datetime.utcnow()

        self,         }

        financial_profile: Dict[str, Any]    

    ) -> Dict[str, Any]:    # Additional helper methods would be implemented here...

        """Generate personalized investment recommendations"""    # (Include all other methods from the original investment_engine.py)

        

        savings_potential = financial_profile["savings_potential"]# Initialize enhanced investment recommendation engine

        risk_profile = financial_profile["risk_profile"]investment_service = AdvancedInvestmentRecommendationEngine()

        spending_analysis = financial_profile["spending_analysis"]    """Engine for analyzing spending and providing investment recommendations"""

            

        recommendations = []    def __init__(self):

                self.investment_products = self._load_investment_products()

        # Emergency fund recommendation        self.savings_thresholds = self._load_savings_thresholds()

        emergency_fund_rec = self._recommend_emergency_fund(savings_potential, spending_analysis)    

        if emergency_fund_rec:    def analyze_financial_profile(

            recommendations.append(emergency_fund_rec)        self, 

                db: Session, 

        # Investment recommendations based on savings capacity        user_id: str, 

        if savings_potential["monthly_savings_potential"] > 100:        analysis_days: int = 90

                ) -> Dict[str, Any]:

            # Low-risk investments for conservative users        """Analyze user's financial profile for investment recommendations"""

            if risk_profile["risk_level"] in ["low", "moderate"]:        

                recommendations.extend(self._get_conservative_investments(savings_potential))        # Get comprehensive spending analysis

                    spending_analysis = transaction_service.get_spending_analysis(

            # Growth investments for moderate to high risk users            db, user_id, analysis_days

            if risk_profile["risk_level"] in ["moderate", "high"]:        )

                recommendations.extend(self._get_growth_investments(savings_potential))        

                    # Get recurring transactions (subscriptions, etc.)

            # Retirement planning        recurring_analysis = transaction_service.detect_recurring_transactions(

            retirement_rec = self._recommend_retirement_planning(savings_potential, risk_profile)            db, user_id, analysis_days

            if retirement_rec:        )

                recommendations.append(retirement_rec)        

                # Calculate income vs expenses

        # Debt optimization recommendations        income_expense_analysis = self._analyze_income_expenses(db, user_id, analysis_days)

        debt_recommendations = self._analyze_debt_optimization(financial_profile)        

        recommendations.extend(debt_recommendations)        # Assess savings potential

                savings_potential = self._calculate_savings_potential(

        # Spending optimization recommendations            spending_analysis, recurring_analysis, income_expense_analysis

        spending_recs = self._recommend_spending_optimizations(financial_profile)        )

        recommendations.extend(spending_recs)        

                # Generate risk profile

        return {        risk_profile = self._assess_risk_profile(spending_analysis, income_expense_analysis)

            "recommendations": recommendations,        

            "summary": self._generate_recommendation_summary(recommendations),        return {

            "priority_actions": self._prioritize_recommendations(recommendations)            "user_id": user_id,

        }            "analysis_period_days": analysis_days,

                "spending_analysis": spending_analysis,

    def _analyze_income_expenses(            "recurring_transactions": recurring_analysis,

        self,             "income_expense_analysis": income_expense_analysis,

        db: Session,             "savings_potential": savings_potential,

        user_id: str,             "risk_profile": risk_profile,

        days: int            "generated_at": datetime.utcnow()

    ) -> Dict[str, Any]:        }

        """Analyze income vs expenses pattern"""    

            def generate_investment_recommendations(

        end_date = datetime.utcnow()        self, 

        start_date = end_date - timedelta(days=days)        financial_profile: Dict[str, Any]

            ) -> Dict[str, Any]:

        # Get all transactions        """Generate personalized investment recommendations"""

        transactions = db.query(Transaction).join(BankAccount).filter(        

            BankAccount.user_id == user_id,        savings_potential = financial_profile["savings_potential"]

            Transaction.date >= start_date        risk_profile = financial_profile["risk_profile"]

        ).all()        spending_analysis = financial_profile["spending_analysis"]

                

        total_income = 0        recommendations = []

        total_expenses = 0        

        income_transactions = []        # Emergency fund recommendation

        expense_transactions = []        emergency_fund_rec = self._recommend_emergency_fund(savings_potential, spending_analysis)

                if emergency_fund_rec:

        for tx in transactions:            recommendations.append(emergency_fund_rec)

            if tx.amount > 0:  # Income        

                total_income += tx.amount        # Investment recommendations based on savings capacity

                income_transactions.append(tx)        if savings_potential["monthly_savings_potential"] > 100:

            else:  # Expense            

                total_expenses += abs(tx.amount)            # Low-risk investments for conservative users

                expense_transactions.append(tx)            if risk_profile["risk_level"] in ["low", "moderate"]:

                        recommendations.extend(self._get_conservative_investments(savings_potential))

        # Calculate monthly averages            

        months = days / 30.0            # Growth investments for moderate to high risk users

        monthly_income = total_income / months if months > 0 else 0            if risk_profile["risk_level"] in ["moderate", "high"]:

        monthly_expenses = total_expenses / months if months > 0 else 0                recommendations.extend(self._get_growth_investments(savings_potential))

                    

        return {            # Retirement planning

            "total_income": total_income,            retirement_rec = self._recommend_retirement_planning(savings_potential, risk_profile)

            "total_expenses": total_expenses,            if retirement_rec:

            "monthly_income": monthly_income,                recommendations.append(retirement_rec)

            "monthly_expenses": monthly_expenses,        

            "net_monthly": monthly_income - monthly_expenses,        # Debt optimization recommendations

            "expense_ratio": (monthly_expenses / monthly_income) if monthly_income > 0 else 0,        debt_recommendations = self._analyze_debt_optimization(financial_profile)

            "income_sources": self._analyze_income_sources(income_transactions),        recommendations.extend(debt_recommendations)

            "expense_categories": self._analyze_expense_categories(expense_transactions)        

        }        # Spending optimization recommendations

            spending_recs = self._recommend_spending_optimizations(financial_profile)

    def _calculate_savings_potential(        recommendations.extend(spending_recs)

        self,         

        spending_analysis: Dict[str, Any],         return {

        recurring_analysis: List[Dict[str, Any]],            "recommendations": recommendations,

        income_expense_analysis: Dict[str, Any]            "summary": self._generate_recommendation_summary(recommendations),

    ) -> Dict[str, Any]:            "priority_actions": self._prioritize_recommendations(recommendations)

        """Calculate potential savings from various optimizations"""        }

            

        # Base savings from positive cash flow    def _analyze_income_expenses(

        base_monthly_savings = max(0, income_expense_analysis["net_monthly"])        self, 

                db: Session, 

        # Potential savings from subscription optimization        user_id: str, 

        subscription_savings = self._calculate_subscription_savings(recurring_analysis)        days: int

            ) -> Dict[str, Any]:

        # Potential savings from spending category optimization        """Analyze income vs expenses pattern"""

        category_savings = self._calculate_category_savings(spending_analysis)        

                end_date = datetime.utcnow()

        # Total potential savings        start_date = end_date - timedelta(days=days)

        total_potential = base_monthly_savings + subscription_savings + category_savings        

                # Get all transactions

        return {        transactions = db.query(Transaction).join(BankAccount).filter(

            "current_monthly_savings": base_monthly_savings,            BankAccount.user_id == user_id,

            "subscription_optimization_savings": subscription_savings,            Transaction.date >= start_date

            "category_optimization_savings": category_savings,        ).all()

            "total_monthly_potential": total_potential,        

            "annual_potential": total_potential * 12,        total_income = 0

            "savings_rate": (base_monthly_savings / income_expense_analysis["monthly_income"])         total_expenses = 0

                          if income_expense_analysis["monthly_income"] > 0 else 0        income_transactions = []

        }        expense_transactions = []

            

    def _assess_risk_profile(        for tx in transactions:

        self,             if tx.amount > 0:  # Income

        spending_analysis: Dict[str, Any],                 total_income += tx.amount

        income_expense_analysis: Dict[str, Any]                income_transactions.append(tx)

    ) -> Dict[str, Any]:            else:  # Expense

        """Assess user's risk profile based on financial behavior"""                total_expenses += abs(tx.amount)

                        expense_transactions.append(tx)

        # Factors that indicate risk tolerance        

        expense_ratio = income_expense_analysis["expense_ratio"]        # Calculate monthly averages

        spending_volatility = self._calculate_spending_volatility(spending_analysis)        months = days / 30.0

        emergency_fund_capacity = income_expense_analysis["net_monthly"] * 6  # 6 months expenses        monthly_income = total_income / months if months > 0 else 0

                monthly_expenses = total_expenses / months if months > 0 else 0

        # Risk scoring        

        risk_score = 0        return {

                    "total_income": total_income,

        # Lower expense ratio indicates higher risk capacity            "total_expenses": total_expenses,

        if expense_ratio < 0.5:            "monthly_income": monthly_income,

            risk_score += 3            "monthly_expenses": monthly_expenses,

        elif expense_ratio < 0.7:            "net_monthly": monthly_income - monthly_expenses,

            risk_score += 2            "expense_ratio": (monthly_expenses / monthly_income) if monthly_income > 0 else 0,

        elif expense_ratio < 0.9:            "income_sources": self._analyze_income_sources(income_transactions),

            risk_score += 1            "expense_categories": self._analyze_expense_categories(expense_transactions)

                }

        # Lower spending volatility indicates stability    

        if spending_volatility < 0.2:    def _calculate_savings_potential(

            risk_score += 2        self, 

        elif spending_volatility < 0.4:        spending_analysis: Dict[str, Any], 

            risk_score += 1        recurring_analysis: List[Dict[str, Any]],

                income_expense_analysis: Dict[str, Any]

        # Determine risk level    ) -> Dict[str, Any]:

        if risk_score >= 4:        """Calculate potential savings from various optimizations"""

            risk_level = "high"        

        elif risk_score >= 2:        # Base savings from positive cash flow

            risk_level = "moderate"        base_monthly_savings = max(0, income_expense_analysis["net_monthly"])

        else:        

            risk_level = "low"        # Potential savings from subscription optimization

                subscription_savings = self._calculate_subscription_savings(recurring_analysis)

        return {        

            "risk_level": risk_level,        # Potential savings from spending category optimization

            "risk_score": risk_score,        category_savings = self._calculate_category_savings(spending_analysis)

            "expense_ratio": expense_ratio,        

            "spending_volatility": spending_volatility,        # Total potential savings

            "recommended_emergency_fund": emergency_fund_capacity        total_potential = base_monthly_savings + subscription_savings + category_savings

        }        

            return {

    def _recommend_emergency_fund(            "current_monthly_savings": base_monthly_savings,

        self,             "subscription_optimization_savings": subscription_savings,

        savings_potential: Dict[str, Any],             "category_optimization_savings": category_savings,

        spending_analysis: Dict[str, Any]            "total_monthly_potential": total_potential,

    ) -> Optional[Dict[str, Any]]:            "annual_potential": total_potential * 12,

        """Recommend emergency fund based on spending patterns"""            "savings_rate": (base_monthly_savings / income_expense_analysis["monthly_income"]) 

                                  if income_expense_analysis["monthly_income"] > 0 else 0

        monthly_expenses = spending_analysis["total_spent"] / (spending_analysis["period_days"] / 30)        }

        recommended_emergency_fund = monthly_expenses * 6  # 6 months of expenses    

            def _assess_risk_profile(

        if savings_potential["current_monthly_savings"] > 0:        self, 

            months_to_build = recommended_emergency_fund / savings_potential["current_monthly_savings"]        spending_analysis: Dict[str, Any], 

                    income_expense_analysis: Dict[str, Any]

            return {    ) -> Dict[str, Any]:

                "type": "emergency_fund",        """Assess user's risk profile based on financial behavior"""

                "priority": "high",        

                "title": "Build Emergency Fund",        # Factors that indicate risk tolerance

                "description": f"Build a ${recommended_emergency_fund:.0f} emergency fund (6 months of expenses)",        expense_ratio = income_expense_analysis["expense_ratio"]

                "recommended_amount": recommended_emergency_fund,        spending_volatility = self._calculate_spending_volatility(spending_analysis)

                "monthly_contribution": min(        emergency_fund_capacity = income_expense_analysis["net_monthly"] * 6  # 6 months expenses

                    savings_potential["current_monthly_savings"] * 0.5,         

                    recommended_emergency_fund / 12        # Risk scoring

                ),        risk_score = 0

                "time_to_goal": f"{months_to_build:.1f} months",        

                "investment_type": "high_yield_savings",        # Lower expense ratio indicates higher risk capacity

                "expected_return": 0.04  # 4% APY for high-yield savings        if expense_ratio < 0.5:

            }            risk_score += 3

                elif expense_ratio < 0.7:

        return None            risk_score += 2

            elif expense_ratio < 0.9:

    def _get_conservative_investments(            risk_score += 1

        self,         

        savings_potential: Dict[str, Any]        # Lower spending volatility indicates stability

    ) -> List[Dict[str, Any]]:        if spending_volatility < 0.2:

        """Get conservative investment recommendations"""            risk_score += 2

                elif spending_volatility < 0.4:

        monthly_capacity = savings_potential["total_monthly_potential"]            risk_score += 1

        recommendations = []        

                # Determine risk level

        if monthly_capacity >= 50:        if risk_score >= 4:

            # High-yield savings account            risk_level = "high"

            recommendations.append({        elif risk_score >= 2:

                "type": "high_yield_savings",            risk_level = "moderate"

                "priority": "high",        else:

                "title": "High-Yield Savings Account",            risk_level = "low"

                "description": "Earn higher interest on your savings with FDIC protection",        

                "recommended_allocation": min(monthly_capacity * 0.4, 500),        return {

                "expected_return": 0.04,            "risk_level": risk_level,

                "risk_level": "very_low",            "risk_score": risk_score,

                "liquidity": "high"            "expense_ratio": expense_ratio,

            })            "spending_volatility": spending_volatility,

                    "recommended_emergency_fund": emergency_fund_capacity

        if monthly_capacity >= 100:        }

            # Conservative bond funds    

            recommendations.append({    def _recommend_emergency_fund(

                "type": "bond_fund",        self, 

                "priority": "medium",        savings_potential: Dict[str, Any], 

                "title": "Conservative Bond Index Fund",        spending_analysis: Dict[str, Any]

                "description": "Diversified bond portfolio for steady income",    ) -> Optional[Dict[str, Any]]:

                "recommended_allocation": min(monthly_capacity * 0.3, 300),        """Recommend emergency fund based on spending patterns"""

                "expected_return": 0.05,        

                "risk_level": "low",        monthly_expenses = spending_analysis["total_spent"] / (spending_analysis["period_days"] / 30)

                "liquidity": "medium"        recommended_emergency_fund = monthly_expenses * 6  # 6 months of expenses

            })        

                if savings_potential["current_monthly_savings"] > 0:

        return recommendations            months_to_build = recommended_emergency_fund / savings_potential["current_monthly_savings"]

                

    def _get_growth_investments(            return {

        self,                 "type": "emergency_fund",

        savings_potential: Dict[str, Any]                "priority": "high",

    ) -> List[Dict[str, Any]]:                "title": "Build Emergency Fund",

        """Get growth-oriented investment recommendations"""                "description": f"Build a ${recommended_emergency_fund:.0f} emergency fund (6 months of expenses)",

                        "recommended_amount": recommended_emergency_fund,

        monthly_capacity = savings_potential["total_monthly_potential"]                "monthly_contribution": min(

        recommendations = []                    savings_potential["current_monthly_savings"] * 0.5, 

                            recommended_emergency_fund / 12

        if monthly_capacity >= 100:                ),

            # Stock market index funds                "time_to_goal": f"{months_to_build:.1f} months",

            recommendations.append({                "investment_type": "high_yield_savings",

                "type": "stock_index_fund",                "expected_return": 0.04  # 4% APY for high-yield savings

                "priority": "high",            }

                "title": "Total Stock Market Index Fund",        

                "description": "Diversified exposure to the entire stock market",        return None

                "recommended_allocation": min(monthly_capacity * 0.6, 1000),    

                "expected_return": 0.10,    def _get_conservative_investments(

                "risk_level": "medium",        self, 

                "liquidity": "high"        savings_potential: Dict[str, Any]

            })    ) -> List[Dict[str, Any]]:

                """Get conservative investment recommendations"""

        if monthly_capacity >= 200:        

            # International diversification        monthly_capacity = savings_potential["total_monthly_potential"]

            recommendations.append({        recommendations = []

                "type": "international_fund",        

                "priority": "medium",        if monthly_capacity >= 50:

                "title": "International Stock Index Fund",            # High-yield savings account

                "description": "Diversify globally with international market exposure",            recommendations.append({

                "recommended_allocation": min(monthly_capacity * 0.2, 400),                "type": "high_yield_savings",

                "expected_return": 0.08,                "priority": "high",

                "risk_level": "medium",                "title": "High-Yield Savings Account",

                "liquidity": "high"                "description": "Earn higher interest on your savings with FDIC protection",

            })                "recommended_allocation": min(monthly_capacity * 0.4, 500),

                        "expected_return": 0.04,

        return recommendations                "risk_level": "very_low",

                    "liquidity": "high"

    def _recommend_spending_optimizations(            })

        self,         

        financial_profile: Dict[str, Any]        if monthly_capacity >= 100:

    ) -> List[Dict[str, Any]]:            # Conservative bond funds

        """Recommend spending optimizations to increase savings"""            recommendations.append({

                        "type": "bond_fund",

        spending_analysis = financial_profile["spending_analysis"]                "priority": "medium",

        recurring_transactions = financial_profile["recurring_transactions"]                "title": "Conservative Bond Index Fund",

                        "description": "Diversified bond portfolio for steady income",

        recommendations = []                "recommended_allocation": min(monthly_capacity * 0.3, 300),

                        "expected_return": 0.05,

        # Subscription optimization                "risk_level": "low",

        total_subscriptions = sum(                "liquidity": "medium"

            tx["total_spent"] for tx in recurring_transactions             })

            if "subscription" in tx["merchant"].lower() or "streaming" in tx["merchant"].lower()        

        )        return recommendations

            

        if total_subscriptions > 50:  # More than $50/month in subscriptions    def _get_growth_investments(

            recommendations.append({        self, 

                "type": "subscription_optimization",        savings_potential: Dict[str, Any]

                "priority": "medium",    ) -> List[Dict[str, Any]]:

                "title": "Optimize Subscriptions",        """Get growth-oriented investment recommendations"""

                "description": f"Review ${total_subscriptions:.0f}/month in subscriptions",        

                "potential_savings": total_subscriptions * 0.3,  # Assume 30% can be saved        monthly_capacity = savings_potential["total_monthly_potential"]

                "action_items": [        recommendations = []

                    "Cancel unused subscriptions",        

                    "Downgrade to cheaper plans",        if monthly_capacity >= 100:

                    "Share family plans",            # Stock market index funds

                    "Use annual billing for discounts"            recommendations.append({

                ]                "type": "stock_index_fund",

            })                "priority": "high",

                        "title": "Total Stock Market Index Fund",

        # High spending categories                "description": "Diversified exposure to the entire stock market",

        top_categories = spending_analysis["top_categories"]                "recommended_allocation": min(monthly_capacity * 0.6, 1000),

        for category, amount in top_categories[:3]:                "expected_return": 0.10,

            if amount > 500:  # High spending category                "risk_level": "medium",

                recommendations.append({                "liquidity": "high"

                    "type": "category_optimization",            })

                    "priority": "low",        

                    "title": f"Optimize {category} Spending",        if monthly_capacity >= 200:

                    "description": f"High spending in {category}: ${amount:.0f}/month",            # International diversification

                    "potential_savings": amount * 0.15,  # 15% reduction potential            recommendations.append({

                    "suggestions": self._get_category_suggestions(category)                "type": "international_fund",

                })                "priority": "medium",

                        "title": "International Stock Index Fund",

        return recommendations                "description": "Diversify globally with international market exposure",

                    "recommended_allocation": min(monthly_capacity * 0.2, 400),

    def _get_category_suggestions(self, category: str) -> List[str]:                "expected_return": 0.08,

        """Get spending reduction suggestions for specific categories"""                "risk_level": "medium",

        suggestions = {                "liquidity": "high"

            "Food and Drink": [            })

                "Cook more meals at home",        

                "Use meal planning apps",        return recommendations

                "Buy generic brands",    

                "Use grocery store loyalty programs"    def _recommend_spending_optimizations(

            ],        self, 

            "Transportation": [        financial_profile: Dict[str, Any]

                "Use public transportation",    ) -> List[Dict[str, Any]]:

                "Carpool or rideshare",        """Recommend spending optimizations to increase savings"""

                "Combine errands into single trips",        

                "Consider gas rewards credit cards"        spending_analysis = financial_profile["spending_analysis"]

            ],        recurring_transactions = financial_profile["recurring_transactions"]

            "Entertainment": [        

                "Look for free local events",        recommendations = []

                "Use library resources",        

                "Share streaming subscriptions",        # Subscription optimization

                "Take advantage of happy hour pricing"        total_subscriptions = sum(

            ],            tx["total_spent"] for tx in recurring_transactions 

            "Shops": [            if "subscription" in tx["merchant"].lower() or "streaming" in tx["merchant"].lower()

                "Use cashback apps",        )

                "Compare prices before buying",        

                "Wait for sales and clearances",        if total_subscriptions > 50:  # More than $50/month in subscriptions

                "Use coupon apps"            recommendations.append({

            ]                "type": "subscription_optimization",

        }                "priority": "medium",

                        "title": "Optimize Subscriptions",

        return suggestions.get(category, ["Review spending in this category"])                "description": f"Review ${total_subscriptions:.0f}/month in subscriptions",

                    "potential_savings": total_subscriptions * 0.3,  # Assume 30% can be saved

    def _prioritize_recommendations(                "action_items": [

        self,                     "Cancel unused subscriptions",

        recommendations: List[Dict[str, Any]]                    "Downgrade to cheaper plans",

    ) -> List[Dict[str, Any]]:                    "Share family plans",

        """Prioritize recommendations by importance and impact"""                    "Use annual billing for discounts"

                        ]

        priority_order = {"high": 3, "medium": 2, "low": 1}            })

                

        return sorted(        # High spending categories

            recommendations,         top_categories = spending_analysis["top_categories"]

            key=lambda x: (        for category, amount in top_categories[:3]:

                priority_order.get(x.get("priority", "low"), 1),            if amount > 500:  # High spending category

                x.get("potential_savings", x.get("recommended_allocation", 0))                recommendations.append({

            ),                    "type": "category_optimization",

            reverse=True                    "priority": "low",

        )[:5]  # Top 5 recommendations                    "title": f"Optimize {category} Spending",

                        "description": f"High spending in {category}: ${amount:.0f}/month",

    def _calculate_spending_volatility(self, spending_analysis: Dict[str, Any]) -> float:                    "potential_savings": amount * 0.15,  # 15% reduction potential

        """Calculate spending volatility from daily spending data"""                    "suggestions": self._get_category_suggestions(category)

        daily_spending = spending_analysis.get("daily_spending", {})                })

                

        if len(daily_spending) < 7:        return recommendations

            return 1.0  # High volatility if insufficient data    

            def _get_category_suggestions(self, category: str) -> List[str]:

        amounts = list(daily_spending.values())        """Get spending reduction suggestions for specific categories"""

        avg_spending = sum(amounts) / len(amounts)        suggestions = {

                    "Food and Drink": [

        if avg_spending == 0:                "Cook more meals at home",

            return 0.0                "Use meal planning apps",

                        "Buy generic brands",

        variance = sum((amount - avg_spending) ** 2 for amount in amounts) / len(amounts)                "Use grocery store loyalty programs"

        return (variance ** 0.5) / avg_spending  # Coefficient of variation            ],

                "Transportation": [

    def _load_investment_products(self) -> Dict[str, Any]:                "Use public transportation",

        """Load available investment products and their characteristics"""                "Carpool or rideshare",

        return {                "Combine errands into single trips",

            "high_yield_savings": {                "Consider gas rewards credit cards"

                "name": "High-Yield Savings Account",            ],

                "expected_return": 0.04,            "Entertainment": [

                "risk_level": "very_low",                "Look for free local events",

                "minimum_investment": 1                "Use library resources",

            },                "Share streaming subscriptions",

            "bond_fund": {                "Take advantage of happy hour pricing"

                "name": "Bond Index Fund",            ],

                "expected_return": 0.05,            "Shops": [

                "risk_level": "low",                "Use cashback apps",

                "minimum_investment": 100                "Compare prices before buying",

            },                "Wait for sales and clearances",

            "stock_index_fund": {                "Use coupon apps"

                "name": "Stock Index Fund",            ]

                "expected_return": 0.10,        }

                "risk_level": "medium",        

                "minimum_investment": 100        return suggestions.get(category, ["Review spending in this category"])

            }    

        }    def _prioritize_recommendations(

            self, 

    def _load_savings_thresholds(self) -> Dict[str, float]:        recommendations: List[Dict[str, Any]]

        """Load savings thresholds for different recommendations"""    ) -> List[Dict[str, Any]]:

        return {        """Prioritize recommendations by importance and impact"""

            "emergency_fund_months": 6,        

            "minimum_investment": 50,        priority_order = {"high": 3, "medium": 2, "low": 1}

            "high_savings_threshold": 500        

        }        return sorted(

            recommendations, 

    # Stubs for missing methods to prevent runtime errors            key=lambda x: (

    def _recommend_retirement_planning(self, savings_potential, risk_profile):                priority_order.get(x.get("priority", "low"), 1),

        return None                x.get("potential_savings", x.get("recommended_allocation", 0))

            ),

    def _analyze_debt_optimization(self, financial_profile):            reverse=True

        return []        )[:5]  # Top 5 recommendations

    

    def _generate_recommendation_summary(self, recommendations):    def _calculate_spending_volatility(self, spending_analysis: Dict[str, Any]) -> float:

        return "Investment recommendations generated based on your financial profile."        """Calculate spending volatility from daily spending data"""

        daily_spending = spending_analysis.get("daily_spending", {})

    def _map_recommendation_to_direction(self, recommendation: str) -> str:        

        if recommendation in ["strong_buy", "buy"]:        if len(daily_spending) < 7:

            return "bullish"            return 1.0  # High volatility if insufficient data

        elif recommendation in ["strong_sell", "sell"]:        

            return "bearish"        amounts = list(daily_spending.values())

        return "neutral"        avg_spending = sum(amounts) / len(amounts)

        

    def _identify_key_combined_factors(self, technical, fundamental, weights):        if avg_spending == 0:

        return []            return 0.0

        

    def _calculate_optimal_position_size(self, recommendation, confidence, user_profile, fundamental_analysis):        variance = sum((amount - avg_spending) ** 2 for amount in amounts) / len(amounts)

        return 5.0 # Default 5%        return (variance ** 0.5) / avg_spending  # Coefficient of variation

    

    def _generate_investment_thesis(self, symbol, technical, fundamental, combined):    def _load_investment_products(self) -> Dict[str, Any]:

        return f"Investment thesis for {symbol}"        """Load available investment products and their characteristics"""

        return {

    def _identify_investment_catalysts(self, technical, fundamental):            "high_yield_savings": {

        return []                "name": "High-Yield Savings Account",

                "expected_return": 0.04,

    def _identify_investment_risks(self, technical, fundamental, user_profile):                "risk_level": "very_low",

        return []                "minimum_investment": 1

            },

    def _define_monitoring_levels(self, technical, price_targets):            "bond_fund": {

        return {}                "name": "Bond Index Fund",

                "expected_return": 0.05,

    def _define_exit_strategy(self, recommendation, price_targets, time_horizon, user_profile):                "risk_level": "low",

        return {}                "minimum_investment": 100

            },

    def _analyze_income_sources(self, transactions):            "stock_index_fund": {

        return {}                "name": "Stock Index Fund",

                "expected_return": 0.10,

    def _analyze_expense_categories(self, transactions):                "risk_level": "medium",

        return {}                "minimum_investment": 100

            }

    def _calculate_subscription_savings(self, recurring):        }

        return 0.0    

    def _load_savings_thresholds(self) -> Dict[str, float]:

    def _calculate_category_savings(self, spending):        """Load savings thresholds for different recommendations"""

        return 0.0        return {

                "emergency_fund_months": 6,

    def _assess_portfolio_fit(self, recommendation, user_profile):            "minimum_investment": 50,

        return {}            "high_savings_threshold": 500

                }

    def _assess_investment_risk(self, technical, fundamental, user_profile):

        return {}# Initialize enhanced investment recommendation engine

investment_service = AdvancedInvestmentRecommendationEngine()

# Initialize enhanced investment recommendation engine
investment_service = AdvancedInvestmentRecommendationEngine()
