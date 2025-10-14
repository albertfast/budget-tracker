from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class CompanyHealthRating(Enum):
    """Company financial health ratings"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"

class GrowthCategory(Enum):
    """Growth potential categories"""
    HIGH_GROWTH = "high_growth"
    MODERATE_GROWTH = "moderate_growth"
    STABLE = "stable"
    DECLINING = "declining"
    DISTRESSED = "distressed"

@dataclass
class FinancialStatement:
    """Financial statement data"""
    period: str
    revenue: float
    gross_profit: float
    operating_income: float
    net_income: float
    total_assets: float
    total_debt: float
    shareholders_equity: float
    cash_and_equivalents: float
    current_assets: float
    current_liabilities: float
    
@dataclass
class ProfitabilityMetrics:
    """Profitability analysis metrics"""
    gross_margin: float
    operating_margin: float
    net_margin: float
    return_on_assets: float
    return_on_equity: float
    return_on_invested_capital: float

@dataclass
class LiquidityMetrics:
    """Liquidity and solvency metrics"""
    current_ratio: float
    quick_ratio: float
    cash_ratio: float
    debt_to_assets: float
    debt_to_equity: float
    interest_coverage: float

@dataclass
class EfficiencyMetrics:
    """Operational efficiency metrics"""
    asset_turnover: float
    inventory_turnover: float
    receivables_turnover: float
    working_capital_turnover: float

@dataclass
class GrowthMetrics:
    """Growth analysis metrics"""
    revenue_growth_1yr: float
    revenue_growth_3yr: float
    earnings_growth_1yr: float
    earnings_growth_3yr: float
    asset_growth: float
    book_value_growth: float

class FundamentalAnalysisEngine:
    """Advanced fundamental analysis engine for company financial assessment"""
    
    def __init__(self):
        self.industry_benchmarks = self._load_industry_benchmarks()
        self.scoring_weights = self._load_scoring_weights()
    
    def analyze_company_fundamentals(
        self,
        symbol: str,
        financial_statements: List[FinancialStatement],
        industry: str = "general"
    ) -> Dict[str, Any]:
        """Comprehensive fundamental analysis of a company"""
        
        if len(financial_statements) < 4:
            raise ValueError("Insufficient financial data (minimum 4 quarters required)")
        
        # Sort by period (most recent first)
        statements = sorted(financial_statements, key=lambda x: x.period, reverse=True)
        current_statement = statements[0]
        
        # Calculate key financial metrics
        profitability = self._analyze_profitability(statements)
        liquidity = self._analyze_liquidity(statements)
        efficiency = self._analyze_efficiency(statements)
        growth = self._analyze_growth(statements)
        
        # P&L trend analysis
        pl_analysis = self._analyze_profit_loss_trends(statements)
        
        # Asset to debt analysis
        debt_analysis = self._analyze_debt_position(statements)
        
        # Company health assessment
        health_score = self._calculate_company_health_score(
            profitability, liquidity, efficiency, growth, debt_analysis
        )
        
        # Growth potential assessment
        growth_assessment = self._assess_growth_potential(
            growth, profitability, debt_analysis, industry
        )
        
        # Investment recommendation
        investment_recommendation = self._generate_fundamental_recommendation(
            health_score, growth_assessment, profitability, debt_analysis
        )
        
        return {
            "symbol": symbol,
            "analysis_timestamp": datetime.utcnow(),
            "current_financials": self._format_current_financials(current_statement),
            "profitability_metrics": profitability,
            "liquidity_metrics": liquidity,
            "efficiency_metrics": efficiency,
            "growth_metrics": growth,
            "profit_loss_analysis": pl_analysis,
            "debt_analysis": debt_analysis,
            "company_health": health_score,
            "growth_assessment": growth_assessment,
            "industry_comparison": self._compare_to_industry(
                profitability, liquidity, efficiency, industry
            ),
            "investment_recommendation": investment_recommendation,
            "key_strengths": self._identify_key_strengths(
                profitability, liquidity, efficiency, growth
            ),
            "key_concerns": self._identify_key_concerns(
                profitability, liquidity, efficiency, growth, debt_analysis
            )
        }
    
    def _analyze_profitability(self, statements: List[FinancialStatement]) -> Dict[str, Any]:
        """Analyze profitability metrics and trends"""
        
        current = statements[0]
        
        # Calculate current profitability ratios
        gross_margin = (current.gross_profit / current.revenue * 100) if current.revenue > 0 else 0
        operating_margin = (current.operating_income / current.revenue * 100) if current.revenue > 0 else 0
        net_margin = (current.net_income / current.revenue * 100) if current.revenue > 0 else 0
        
        roa = (current.net_income / current.total_assets * 100) if current.total_assets > 0 else 0
        roe = (current.net_income / current.shareholders_equity * 100) if current.shareholders_equity > 0 else 0
        
        # Calculate invested capital and ROIC
        invested_capital = current.shareholders_equity + current.total_debt
        roic = (current.operating_income / invested_capital * 100) if invested_capital > 0 else 0
        
        # Calculate trends over time
        margin_trends = self._calculate_margin_trends(statements)
        
        # Profitability score (0-100)
        profitability_score = self._calculate_profitability_score(
            gross_margin, operating_margin, net_margin, roa, roe, roic
        )
        
        return {
            "gross_margin": gross_margin,
            "operating_margin": operating_margin,
            "net_margin": net_margin,
            "return_on_assets": roa,
            "return_on_equity": roe,
            "return_on_invested_capital": roic,
            "margin_trends": margin_trends,
            "profitability_score": profitability_score,
            "profitability_grade": self._assign_grade(profitability_score),
            "competitive_position": self._assess_competitive_position(
                gross_margin, operating_margin, net_margin
            )
        }
    
    def _analyze_liquidity(self, statements: List[FinancialStatement]) -> Dict[str, Any]:
        """Analyze liquidity and solvency metrics"""
        
        current = statements[0]
        
        # Liquidity ratios
        current_ratio = (current.current_assets / current.current_liabilities) if current.current_liabilities > 0 else 0
        
        # Quick ratio (excluding inventory - estimated as 70% of current assets)
        quick_assets = current.current_assets * 0.7  # Simplified estimation
        quick_ratio = (quick_assets / current.current_liabilities) if current.current_liabilities > 0 else 0
        
        cash_ratio = (current.cash_and_equivalents / current.current_liabilities) if current.current_liabilities > 0 else 0
        
        # Solvency ratios
        debt_to_assets = (current.total_debt / current.total_assets * 100) if current.total_assets > 0 else 0
        debt_to_equity = (current.total_debt / current.shareholders_equity * 100) if current.shareholders_equity > 0 else 0
        
        # Interest coverage (estimated)
        interest_expense = current.total_debt * 0.05  # Assume 5% average interest rate
        interest_coverage = (current.operating_income / interest_expense) if interest_expense > 0 else 999
        
        # Liquidity trends
        liquidity_trends = self._calculate_liquidity_trends(statements)
        
        # Liquidity score
        liquidity_score = self._calculate_liquidity_score(
            current_ratio, quick_ratio, cash_ratio, debt_to_assets, debt_to_equity, interest_coverage
        )
        
        return {
            "current_ratio": current_ratio,
            "quick_ratio": quick_ratio,
            "cash_ratio": cash_ratio,
            "debt_to_assets": debt_to_assets,
            "debt_to_equity": debt_to_equity,
            "interest_coverage": interest_coverage,
            "liquidity_trends": liquidity_trends,
            "liquidity_score": liquidity_score,
            "liquidity_grade": self._assign_grade(liquidity_score),
            "financial_risk_level": self._assess_financial_risk(debt_to_assets, debt_to_equity, interest_coverage)
        }
    
    def _analyze_efficiency(self, statements: List[FinancialStatement]) -> Dict[str, Any]:
        """Analyze operational efficiency metrics"""
        
        current = statements[0]
        
        # Asset efficiency
        asset_turnover = (current.revenue / current.total_assets) if current.total_assets > 0 else 0
        
        # Working capital efficiency
        working_capital = current.current_assets - current.current_liabilities
        working_capital_turnover = (current.revenue / working_capital) if working_capital > 0 else 0
        
        # Estimated efficiency metrics (simplified)
        inventory_turnover = 12  # Estimated quarterly turnover
        receivables_turnover = 8  # Estimated quarterly turnover
        
        # Efficiency trends
        efficiency_trends = self._calculate_efficiency_trends(statements)
        
        # Efficiency score
        efficiency_score = self._calculate_efficiency_score(
            asset_turnover, working_capital_turnover, inventory_turnover, receivables_turnover
        )
        
        return {
            "asset_turnover": asset_turnover,
            "working_capital_turnover": working_capital_turnover,
            "inventory_turnover": inventory_turnover,
            "receivables_turnover": receivables_turnover,
            "efficiency_trends": efficiency_trends,
            "efficiency_score": efficiency_score,
            "efficiency_grade": self._assign_grade(efficiency_score),
            "operational_effectiveness": self._assess_operational_effectiveness(
                asset_turnover, working_capital_turnover
            )
        }
    
    def _analyze_growth(self, statements: List[FinancialStatement]) -> Dict[str, Any]:
        """Analyze growth metrics and trends"""
        
        if len(statements) < 4:
            return {"error": "Insufficient data for growth analysis"}
        
        current = statements[0]
        year_ago = statements[4] if len(statements) >= 5 else statements[-1]
        
        # Revenue growth
        revenue_growth_1yr = ((current.revenue - year_ago.revenue) / year_ago.revenue * 100) if year_ago.revenue > 0 else 0
        
        # Earnings growth
        earnings_growth_1yr = ((current.net_income - year_ago.net_income) / abs(year_ago.net_income) * 100) if year_ago.net_income != 0 else 0
        
        # Asset growth
        asset_growth = ((current.total_assets - year_ago.total_assets) / year_ago.total_assets * 100) if year_ago.total_assets > 0 else 0
        
        # Book value growth
        book_value_growth = ((current.shareholders_equity - year_ago.shareholders_equity) / year_ago.shareholders_equity * 100) if year_ago.shareholders_equity > 0 else 0
        
        # Calculate 3-year trends if available
        revenue_growth_3yr = self._calculate_cagr(statements, 'revenue', 3)
        earnings_growth_3yr = self._calculate_cagr(statements, 'net_income', 3)
        
        # Growth consistency
        growth_consistency = self._calculate_growth_consistency(statements)
        
        # Growth score
        growth_score = self._calculate_growth_score(
            revenue_growth_1yr, earnings_growth_1yr, revenue_growth_3yr, growth_consistency
        )
        
        return {
            "revenue_growth_1yr": revenue_growth_1yr,
            "revenue_growth_3yr": revenue_growth_3yr,
            "earnings_growth_1yr": earnings_growth_1yr,
            "earnings_growth_3yr": earnings_growth_3yr,
            "asset_growth": asset_growth,
            "book_value_growth": book_value_growth,
            "growth_consistency": growth_consistency,
            "growth_score": growth_score,
            "growth_grade": self._assign_grade(growth_score),
            "growth_sustainability": self._assess_growth_sustainability(
                revenue_growth_1yr, earnings_growth_1yr, growth_consistency
            )
        }
    
    def _analyze_profit_loss_trends(self, statements: List[FinancialStatement]) -> Dict[str, Any]:
        """Detailed P&L trend analysis"""
        
        # Revenue trend analysis
        revenues = [stmt.revenue for stmt in statements]
        revenue_trend = self._calculate_trend_direction(revenues)
        revenue_volatility = self._calculate_volatility(revenues)
        
        # Profit trend analysis
        net_incomes = [stmt.net_income for stmt in statements]
        profit_trend = self._calculate_trend_direction(net_incomes)
        profit_volatility = self._calculate_volatility(net_incomes)
        
        # Operating efficiency trend
        operating_incomes = [stmt.operating_income for stmt in statements]
        operating_trend = self._calculate_trend_direction(operating_incomes)
        
        # Margin analysis over time
        margin_evolution = []
        for stmt in statements:
            if stmt.revenue > 0:
                margin_evolution.append({
                    "period": stmt.period,
                    "gross_margin": (stmt.gross_profit / stmt.revenue) * 100,
                    "operating_margin": (stmt.operating_income / stmt.revenue) * 100,
                    "net_margin": (stmt.net_income / stmt.revenue) * 100
                })
        
        return {
            "revenue_trend": revenue_trend,
            "revenue_volatility": revenue_volatility,
            "profit_trend": profit_trend,
            "profit_volatility": profit_volatility,
            "operating_trend": operating_trend,
            "margin_evolution": margin_evolution,
            "earnings_quality": self._assess_earnings_quality(statements),
            "revenue_diversification": self._assess_revenue_quality(statements)
        }
    
    def _analyze_debt_position(self, statements: List[FinancialStatement]) -> Dict[str, Any]:
        """Comprehensive debt and capital structure analysis"""
        
        current = statements[0]
        
        # Basic debt metrics
        total_assets = current.total_assets
        total_debt = current.total_debt
        shareholders_equity = current.shareholders_equity
        
        # Asset to debt ratio
        asset_to_debt_ratio = (total_assets / total_debt) if total_debt > 0 else 999
        
        # Debt composition analysis
        debt_to_assets = (total_debt / total_assets * 100) if total_assets > 0 else 0
        debt_to_equity = (total_debt / shareholders_equity * 100) if shareholders_equity > 0 else 0
        equity_ratio = (shareholders_equity / total_assets * 100) if total_assets > 0 else 0
        
        # Debt capacity analysis
        debt_capacity = self._calculate_debt_capacity(current)
        
        # Debt trend analysis
        debt_trends = self._calculate_debt_trends(statements)
        
        # Credit risk assessment
        credit_risk = self._assess_credit_risk(current, statements)
        
        # Optimal capital structure assessment
        capital_efficiency = self._assess_capital_efficiency(current)
        
        return {
            "asset_to_debt_ratio": asset_to_debt_ratio,
            "debt_to_assets": debt_to_assets,
            "debt_to_equity": debt_to_equity,
            "equity_ratio": equity_ratio,
            "debt_capacity": debt_capacity,
            "debt_trends": debt_trends,
            "credit_risk": credit_risk,
            "capital_efficiency": capital_efficiency,
            "financial_leverage": self._calculate_financial_leverage(current),
            "debt_service_ability": self._assess_debt_service_ability(current)
        }
    
    def _calculate_company_health_score(
        self,
        profitability: Dict[str, Any],
        liquidity: Dict[str, Any],
        efficiency: Dict[str, Any],
        growth: Dict[str, Any],
        debt_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate overall company health score"""
        
        # Weight different aspects of financial health
        weights = {
            "profitability": 0.30,
            "liquidity": 0.25,
            "efficiency": 0.20,
            "growth": 0.15,
            "debt_structure": 0.10
        }
        
        # Extract scores
        prof_score = profitability.get("profitability_score", 0)
        liq_score = liquidity.get("liquidity_score", 0)
        eff_score = efficiency.get("efficiency_score", 0)
        growth_score = growth.get("growth_score", 0)
        debt_score = 100 - min(debt_analysis.get("debt_to_assets", 0), 100)  # Invert debt ratio
        
        # Calculate weighted health score
        health_score = (
            prof_score * weights["profitability"] +
            liq_score * weights["liquidity"] +
            eff_score * weights["efficiency"] +
            growth_score * weights["growth"] +
            debt_score * weights["debt_structure"]
        )
        
        # Determine health rating
        if health_score >= 85:
            health_rating = CompanyHealthRating.EXCELLENT
        elif health_score >= 70:
            health_rating = CompanyHealthRating.GOOD
        elif health_score >= 55:
            health_rating = CompanyHealthRating.FAIR
        elif health_score >= 40:
            health_rating = CompanyHealthRating.POOR
        else:
            health_rating = CompanyHealthRating.CRITICAL
        
        return {
            "overall_score": health_score,
            "health_rating": health_rating.value,
            "component_scores": {
                "profitability": prof_score,
                "liquidity": liq_score,
                "efficiency": eff_score,
                "growth": growth_score,
                "debt_structure": debt_score
            },
            "score_weights": weights,
            "strengths": self._identify_score_strengths(
                prof_score, liq_score, eff_score, growth_score, debt_score
            ),
            "weaknesses": self._identify_score_weaknesses(
                prof_score, liq_score, eff_score, growth_score, debt_score
            )
        }
    
    def _assess_growth_potential(
        self,
        growth: Dict[str, Any],
        profitability: Dict[str, Any],
        debt_analysis: Dict[str, Any],
        industry: str
    ) -> Dict[str, Any]:
        """Assess company's growth potential"""
        
        # Growth factors
        revenue_growth = growth.get("revenue_growth_1yr", 0)
        earnings_growth = growth.get("earnings_growth_1yr", 0)
        growth_consistency = growth.get("growth_consistency", 0)
        
        # Profitability factors
        operating_margin = profitability.get("operating_margin", 0)
        roe = profitability.get("return_on_equity", 0)
        
        # Financial capacity factors
        debt_ratio = debt_analysis.get("debt_to_assets", 100)
        asset_debt_ratio = debt_analysis.get("asset_to_debt_ratio", 0)
        
        # Calculate growth potential score
        growth_potential_score = self._calculate_growth_potential_score(
            revenue_growth, earnings_growth, growth_consistency,
            operating_margin, roe, debt_ratio, asset_debt_ratio
        )
        
        # Determine growth category
        if growth_potential_score >= 80:
            growth_category = GrowthCategory.HIGH_GROWTH
        elif growth_potential_score >= 60:
            growth_category = GrowthCategory.MODERATE_GROWTH
        elif growth_potential_score >= 40:
            growth_category = GrowthCategory.STABLE
        elif growth_potential_score >= 20:
            growth_category = GrowthCategory.DECLINING
        else:
            growth_category = GrowthCategory.DISTRESSED
        
        return {
            "growth_potential_score": growth_potential_score,
            "growth_category": growth_category.value,
            "growth_drivers": self._identify_growth_drivers(
                revenue_growth, earnings_growth, operating_margin, roe
            ),
            "growth_risks": self._identify_growth_risks(
                debt_ratio, growth_consistency, profitability
            ),
            "investment_horizon": self._recommend_investment_horizon(growth_category),
            "growth_sustainability": growth.get("growth_sustainability", "moderate")
        }
    
    def _generate_fundamental_recommendation(
        self,
        health_score: Dict[str, Any],
        growth_assessment: Dict[str, Any],
        profitability: Dict[str, Any],
        debt_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate fundamental investment recommendation"""
        
        overall_health = health_score["overall_score"]
        growth_potential = growth_assessment["growth_potential_score"]
        debt_ratio = debt_analysis.get("debt_to_assets", 0)
        
        # Determine recommendation
        if overall_health >= 70 and growth_potential >= 60 and debt_ratio < 50:
            recommendation = "strong_buy"
            confidence = 90
        elif overall_health >= 60 and growth_potential >= 50 and debt_ratio < 60:
            recommendation = "buy"
            confidence = 75
        elif overall_health >= 50 and debt_ratio < 70:
            recommendation = "hold"
            confidence = 60
        elif overall_health >= 35:
            recommendation = "weak_hold"
            confidence = 45
        else:
            recommendation = "sell"
            confidence = 80
        
        return {
            "recommendation": recommendation,
            "confidence": confidence,
            "investment_thesis": self._generate_investment_thesis(
                health_score, growth_assessment, profitability, debt_analysis
            ),
            "key_catalysts": self._identify_key_catalysts(growth_assessment, profitability),
            "risk_factors": self._identify_fundamental_risks(debt_analysis, profitability),
            "target_ownership_percentage": self._recommend_portfolio_allocation(
                recommendation, confidence, debt_ratio
            ),
            "monitoring_metrics": self._recommend_monitoring_metrics()
        }
    
    # Helper methods (simplified implementations)
    def _calculate_trend_direction(self, values: List[float]) -> str:
        """Calculate trend direction of a series"""
        if len(values) < 2:
            return "insufficient_data"
        
        # Simple trend calculation
        recent_avg = sum(values[:3]) / min(3, len(values))
        older_avg = sum(values[-3:]) / min(3, len(values))
        
        if recent_avg > older_avg * 1.05:
            return "increasing"
        elif recent_avg < older_avg * 0.95:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_volatility(self, values: List[float]) -> float:
        """Calculate volatility of a series"""
        if len(values) < 2:
            return 0
        
        mean_val = sum(values) / len(values)
        variance = sum((v - mean_val) ** 2 for v in values) / len(values)
        return (variance ** 0.5) / mean_val if mean_val != 0 else 0
    
    def _load_industry_benchmarks(self) -> Dict[str, Dict[str, float]]:
        """Load industry benchmark data"""
        return {
            "technology": {
                "gross_margin": 60,
                "operating_margin": 20,
                "debt_to_assets": 20,
                "current_ratio": 2.5
            },
            "general": {
                "gross_margin": 35,
                "operating_margin": 10,
                "debt_to_assets": 40,
                "current_ratio": 1.5
            }
        }
    
    def _load_scoring_weights(self) -> Dict[str, float]:
        """Load scoring weights for different metrics"""
        return {
            "profitability": 0.30,
            "liquidity": 0.25,
            "efficiency": 0.20,
            "growth": 0.15,
            "debt_structure": 0.10
        }
    
    # Additional helper methods would be implemented here...
    # (Simplified for brevity - full implementation would include all calculations)

# Initialize fundamental analysis engine
fundamental_analysis_engine = FundamentalAnalysisEngine()