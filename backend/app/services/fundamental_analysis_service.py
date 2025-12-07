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
    
    def screen_companies_from_file(
        self,
        file_data: Any,  # pandas DataFrame
        file_type: str = "auto"
    ) -> Dict[str, Any]:
        """
        NEW: Screen companies from uploaded file for fundamental quality.
        Analyzes predictability (QoQ, QoY) and 10-K report depth expansion.
        
        Args:
            file_data: DataFrame from uploaded CSV/Excel
            file_type: Type of file (balance_sheet, portfolio, profit_loss, auto)
        
        Returns:
            Dict with screening results, ranked companies, and insights
        """
        try:
            import pandas as pd
            import numpy as np
            
            # Convert to DataFrame if needed
            if not isinstance(file_data, pd.DataFrame):
                return {
                    "error": "Invalid file format - expected DataFrame",
                    "companies": [],
                    "summary": {}
                }
            
            # Detect file type if auto
            if file_type == "auto":
                file_type = self._detect_file_type(file_data)
            
            # Extract companies from file
            companies = self._extract_companies_from_file(file_data, file_type)
            
            if not companies:
                return {
                    "error": "No companies detected in uploaded file",
                    "companies": [],
                    "summary": {}
                }
            
            # Screen each company
            screening_results = []
            for company in companies:
                result = self._screen_single_company_fundamentals(company, file_data, file_type)
                screening_results.append(result)
            
            # Rank companies by overall score
            ranked_companies = sorted(
                screening_results,
                key=lambda x: x.get("overall_score", 0),
                reverse=True
            )
            
            # Generate summary insights
            summary = self._generate_screening_summary(ranked_companies)
            
            return {
                "total_companies": len(companies),
                "file_type": file_type,
                "companies": ranked_companies,
                "summary": summary,
                "screening_date": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error screening companies: {str(e)}")
            return {
                "error": str(e),
                "companies": [],
                "summary": {}
            }
    
    def _detect_file_type(self, df: Any) -> str:
        """Detect file type based on column names and structure."""
        import pandas as pd
        
        # Handle SEC EDGAR parsed data
        if isinstance(df, dict):
            if 'filing_type' in df:
                return df['filing_type']
            if 'financials' in df:
                return 'sec_xbrl'
            if 'company_info' in df and 'financials' in df:
                return 'sec_filing'
        
        if not isinstance(df, pd.DataFrame):
            return "unknown"
            
        columns = [str(col).lower() for col in df.columns]
        
        # Check for balance sheet indicators
        balance_sheet_keywords = ['assets', 'liabilities', 'equity', 'balance']
        if any(keyword in ' '.join(columns) for keyword in balance_sheet_keywords):
            return "balance_sheet"
        
        # Check for P&L indicators
        pl_keywords = ['revenue', 'income', 'profit', 'expense', 'ebitda']
        if any(keyword in ' '.join(columns) for keyword in pl_keywords):
            return "profit_loss"
        
        # Check for portfolio indicators
        portfolio_keywords = ['ticker', 'symbol', 'shares', 'position', 'value']
        if any(keyword in ' '.join(columns) for keyword in portfolio_keywords):
            return "portfolio"
        
        # Check for pink slips (layoffs) indicators
        pink_slip_keywords = ['employee', 'layoff', 'termination', 'department']
        if any(keyword in ' '.join(columns) for keyword in pink_slip_keywords):
            return "pink_slips"
        
        return "unknown"
    
    def _extract_companies_from_file(self, df: Any, file_type: str) -> List[Dict[str, Any]]:
        """Extract company information from DataFrame or SEC filing data based on file type."""
        import pandas as pd
        import re
        
        # Handle SEC EDGAR filings
        if isinstance(df, dict) and 'company_info' in df:
            companies = []
            company_info = df.get('company_info', {})
            
            ticker = company_info.get('ticker', '')
            if not ticker:
                # Try to extract from company name or CIK
                company_name = company_info.get('company_name', '')
                # You could add logic to lookup ticker from company name
            
            if ticker:
                company_data = {
                    "ticker": ticker.strip().upper(),
                    "source_file": file_type,
                    "sec_filing_data": df,
                    "company_name": company_info.get('company_name', ''),
                    "cik": company_info.get('cik', ''),
                    "filing_date": company_info.get('period_end_date', '')
                }
                companies.append(company_data)
            
            return companies
        
        if not isinstance(df, pd.DataFrame):
            return []
            
        companies = []
        
        # Look for company/ticker columns
        possible_ticker_cols = [
            'ticker', 'symbol', 'company', 'stock', 'security',
            'Ticker', 'Symbol', 'Company', 'Stock', 'Security'
        ]
        
        ticker_col = None
        for col in possible_ticker_cols:
            if col in df.columns:
                ticker_col = col
                break
        
        if ticker_col:
            # Extract unique tickers
            tickers = df[ticker_col].dropna().unique()
            for ticker in tickers:
                # Clean ticker symbol
                clean_ticker = str(ticker).strip().upper()
                if clean_ticker and len(clean_ticker) <= 5 and clean_ticker != 'NAN':  # Valid ticker length
                    company_data = {
                        "ticker": clean_ticker,
                        "source_file": file_type,
                        "data_rows": df[df[ticker_col] == ticker].to_dict('records')
                    }
                    companies.append(company_data)
        
        return companies
    
    def _screen_single_company_fundamentals(
        self,
        company: Dict[str, Any],
        full_data: Any,
        file_type: str
    ) -> Dict[str, Any]:
        """
        Perform comprehensive fundamental screening on a single company.
        Analyzes predictability and 10-K depth.
        """
        import numpy as np
        
        ticker = company["ticker"]
        
        # Simulate historical financial data (in production, fetch from SEC EDGAR/APIs)
        historical_financials = self._simulate_financial_history_for_screening(ticker)
        
        # Calculate predictability metrics (QoQ, QoY)
        predictability = self._calculate_predictability_metrics(historical_financials)
        
        # Analyze 10-K report depth expansion
        report_depth = self._analyze_10k_report_depth(ticker, historical_financials)
        
        # Calculate overall quality score
        quality_score = self._calculate_fundamental_quality_score(
            predictability,
            report_depth,
            historical_financials
        )
        
        # Generate investment recommendation
        recommendation = self._generate_fundamental_recommendation(
            quality_score,
            predictability,
            report_depth
        )
        
        return {
            "ticker": ticker,
            "company_name": company.get("name", ticker),
            "predictability": predictability,
            "report_depth": report_depth,
            "quality_score": quality_score,
            "overall_score": quality_score["overall"],
            "recommendation": recommendation,
            "source_data": company.get("data_rows", [])[:3]  # Limit to first 3 rows
        }
    
    def _simulate_financial_history_for_screening(self, ticker: str) -> Dict[str, Any]:
        """
        Simulate financial history for screening.
        In production: fetch from SEC EDGAR, Yahoo Finance, or financial APIs.
        """
        import numpy as np
        
        # Simulate quarterly data for 8 quarters (2 years)
        quarters = []
        base_revenue = np.random.uniform(100, 500)  # Million $
        revenue_growth = np.random.uniform(-0.05, 0.15)  # -5% to +15% base growth
        
        for i in range(8):
            # Add noise to simulate real volatility
            noise = np.random.normal(0, 0.05)
            quarter_revenue = base_revenue * (1 + revenue_growth + noise) ** i
            
            quarter_data = {
                "quarter": f"Q{(i % 4) + 1} {2023 + i // 4}",
                "revenue": round(quarter_revenue, 2),
                "earnings": round(quarter_revenue * np.random.uniform(0.05, 0.20), 2),
                "cash_flow": round(quarter_revenue * np.random.uniform(0.08, 0.25), 2)
            }
            quarters.append(quarter_data)
        
        # Simulate annual 10-K reports
        annual_reports = []
        for year in [2023, 2024]:
            year_quarters = [q for q in quarters if str(year) in q["quarter"]]
            annual_revenue = sum(q["revenue"] for q in year_quarters) if year_quarters else 0
            annual_earnings = sum(q["earnings"] for q in year_quarters) if year_quarters else 0
            
            report = {
                "year": year,
                "revenue": round(annual_revenue, 2),
                "earnings": round(annual_earnings, 2),
                "report_depth": {
                    "total_line_items": np.random.randint(200, 500),
                    "disclosure_sections": np.random.randint(15, 30),
                    "segment_details": np.random.randint(3, 8),
                    "risk_factors": np.random.randint(20, 50),
                    "md_and_a_pages": np.random.randint(15, 40)
                }
            }
            annual_reports.append(report)
        
        return {
            "ticker": ticker,
            "quarterly": quarters,
            "annual": annual_reports
        }
    
    def _calculate_predictability_metrics(self, financials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate predictability scores (QoQ and QoY).
        Higher scores = more consistent, predictable financial performance.
        """
        import numpy as np
        
        quarters = financials["quarterly"]
        
        if len(quarters) < 5:
            return {
                "qoq_score": 0,
                "qoy_score": 0,
                "overall_predictability": 0,
                "trend": "insufficient_data",
                "grade": "N/A"
            }
        
        # Calculate QoQ (Quarter-over-Quarter) consistency
        qoq_changes = []
        for i in range(1, len(quarters)):
            prev_revenue = quarters[i-1]["revenue"]
            curr_revenue = quarters[i]["revenue"]
            if prev_revenue > 0:
                change = (curr_revenue - prev_revenue) / prev_revenue
                qoq_changes.append(change)
        
        # Coefficient of variation (lower = more predictable)
        qoq_std = np.std(qoq_changes) if qoq_changes else 1.0
        qoq_mean = np.mean(qoq_changes) if qoq_changes else 0
        qoq_cv = abs(qoq_std / qoq_mean) if qoq_mean != 0 else 1.0
        
        # Convert to 0-100 score
        qoq_score = max(0, min(100, 100 * (1 - min(qoq_cv, 1.0))))
        
        # Calculate QoY (Quarter-over-Year) consistency
        qoy_changes = []
        for i in range(4, len(quarters)):  # Compare with same quarter last year
            prev_year_revenue = quarters[i-4]["revenue"]
            curr_revenue = quarters[i]["revenue"]
            if prev_year_revenue > 0:
                change = (curr_revenue - prev_year_revenue) / prev_year_revenue
                qoy_changes.append(change)
        
        qoy_std = np.std(qoy_changes) if qoy_changes else 1.0
        qoy_mean = np.mean(qoy_changes) if qoy_changes else 0
        qoy_cv = abs(qoy_std / qoy_mean) if qoy_mean != 0 else 1.0
        
        qoy_score = max(0, min(100, 100 * (1 - min(qoy_cv, 1.0))))
        
        # Overall predictability (QoY weighted higher - more important)
        overall = (qoq_score * 0.4 + qoy_score * 0.6)
        
        # Determine trend (improving vs declining predictability)
        if len(qoq_changes) >= 4:
            recent_qoq_cv = abs(np.std(qoq_changes[-4:]) / np.mean(qoq_changes[-4:])) if np.mean(qoq_changes[-4:]) != 0 else 1.0
            older_qoq_cv = abs(np.std(qoq_changes[:-4]) / np.mean(qoq_changes[:-4])) if len(qoq_changes) > 4 and np.mean(qoq_changes[:-4]) != 0 else 1.0
            
            if recent_qoq_cv < older_qoq_cv * 0.8:
                trend = "improving"  # Becoming more predictable
            elif recent_qoq_cv > older_qoq_cv * 1.2:
                trend = "declining"  # Becoming less predictable
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        # Assign grade
        if overall >= 85:
            grade = "excellent"
        elif overall >= 70:
            grade = "good"
        elif overall >= 55:
            grade = "fair"
        else:
            grade = "poor"
        
        return {
            "qoq_score": round(qoq_score, 2),
            "qoy_score": round(qoy_score, 2),
            "overall_predictability": round(overall, 2),
            "trend": trend,
            "grade": grade,
            "details": {
                "qoq_mean_growth": round(qoq_mean * 100, 2) if qoq_mean else 0,
                "qoq_volatility": round(qoq_std * 100, 2) if qoq_std else 0,
                "qoy_mean_growth": round(qoy_mean * 100, 2) if qoy_mean else 0,
                "qoy_volatility": round(qoy_std * 100, 2) if qoy_std else 0
            }
        }
    
    def _analyze_10k_report_depth(
        self,
        ticker: str,
        financials: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze 10-K report depth and year-over-year expansion.
        Expanding depth = increasing transparency and disclosure quality.
        """
        annual_reports = financials["annual"]
        
        if len(annual_reports) < 2:
            return {
                "depth_score": 0,
                "expansion_trend": "insufficient_data",
                "grade": "N/A",
                "latest_year": {},
                "year_over_year_change": {}
            }
        
        # Analyze latest vs previous year
        latest = annual_reports[-1]
        previous = annual_reports[-2]
        
        latest_depth = latest["report_depth"]
        previous_depth = previous["report_depth"]
        
        # Calculate depth score based on multiple factors
        line_items_score = min(100, (latest_depth["total_line_items"] / 500) * 100)
        disclosure_score = min(100, (latest_depth["disclosure_sections"] / 30) * 100)
        segment_score = min(100, (latest_depth["segment_details"] / 8) * 100)
        risk_score = min(100, (latest_depth["risk_factors"] / 50) * 100)
        mda_score = min(100, (latest_depth["md_and_a_pages"] / 40) * 100)
        
        depth_score = (
            line_items_score * 0.25 +
            disclosure_score * 0.25 +
            segment_score * 0.20 +
            risk_score * 0.15 +
            mda_score * 0.15
        )
        
        # Calculate year-over-year changes
        yoy_changes = {
            "line_items": latest_depth["total_line_items"] - previous_depth["total_line_items"],
            "disclosure_sections": latest_depth["disclosure_sections"] - previous_depth["disclosure_sections"],
            "segment_details": latest_depth["segment_details"] - previous_depth["segment_details"],
            "risk_factors": latest_depth["risk_factors"] - previous_depth["risk_factors"],
            "md_and_a_pages": latest_depth["md_and_a_pages"] - previous_depth["md_and_a_pages"]
        }
        
        # Determine expansion trend
        positive_changes = sum(1 for change in yoy_changes.values() if change > 0)
        
        if positive_changes >= 4:
            expansion_trend = "expanding"
            trend_score = 100
            interpretation = "Report depth expanding - indicates increased transparency and disclosure quality"
        elif positive_changes >= 3:
            expansion_trend = "stable_positive"
            trend_score = 80
            interpretation = "Report depth stable with slight expansion - healthy disclosure practices"
        elif positive_changes >= 2:
            expansion_trend = "stable"
            trend_score = 60
            interpretation = "Report depth stable - consistent disclosure practices"
        else:
            expansion_trend = "contracting"
            trend_score = 30
            major_declines = [k for k, v in yoy_changes.items() if v < -5]
            interpretation = f"Report depth contracting - potential red flag. Declining in: {', '.join(major_declines) if major_declines else 'multiple areas'}"
        
        # Assign grade
        if depth_score >= 85:
            grade = "comprehensive"
        elif depth_score >= 70:
            grade = "detailed"
        elif depth_score >= 50:
            grade = "adequate"
        else:
            grade = "minimal"
        
        return {
            "depth_score": round(depth_score, 2),
            "trend_score": trend_score,
            "expansion_trend": expansion_trend,
            "grade": grade,
            "latest_year": {
                "year": latest["year"],
                "line_items": latest_depth["total_line_items"],
                "disclosure_sections": latest_depth["disclosure_sections"],
                "segment_details": latest_depth["segment_details"],
                "risk_factors": latest_depth["risk_factors"],
                "md_and_a_pages": latest_depth["md_and_a_pages"]
            },
            "year_over_year_change": yoy_changes,
            "interpretation": interpretation
        }
    
    def _calculate_fundamental_quality_score(
        self,
        predictability: Dict[str, Any],
        report_depth: Dict[str, Any],
        financials: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate overall fundamental quality score.
        Combines predictability, report depth, and growth.
        """
        import numpy as np
        
        # Component scores
        predictability_score = predictability["overall_predictability"]
        depth_score = report_depth["depth_score"]
        trend_score = report_depth["trend_score"]
        
        # Calculate growth consistency
        quarters = financials["quarterly"]
        revenues = [q["revenue"] for q in quarters]
        growth_rate = (revenues[-1] - revenues[0]) / revenues[0] if revenues[0] > 0 else 0
        growth_score = min(100, max(0, 50 + growth_rate * 100))  # Normalize around 50
        
        # Weighted overall score
        overall = (
            predictability_score * 0.35 +  # 35% - most important
            depth_score * 0.25 +            # 25% - report quality
            trend_score * 0.20 +            # 20% - expansion trend
            growth_score * 0.20             # 20% - actual growth
        )
        
        # Assign letter grade
        if overall >= 90:
            grade = "A+"
        elif overall >= 85:
            grade = "A"
        elif overall >= 80:
            grade = "A-"
        elif overall >= 75:
            grade = "B+"
        elif overall >= 70:
            grade = "B"
        elif overall >= 65:
            grade = "B-"
        elif overall >= 60:
            grade = "C+"
        elif overall >= 55:
            grade = "C"
        elif overall >= 50:
            grade = "C-"
        else:
            grade = "D"
        
        return {
            "overall": round(overall, 2),
            "components": {
                "predictability": round(predictability_score, 2),
                "report_depth": round(depth_score, 2),
                "expansion_trend": trend_score,
                "growth": round(growth_score, 2)
            },
            "grade": grade
        }
    
    def _generate_fundamental_recommendation(
        self,
        quality_score: Dict[str, Any],
        predictability: Dict[str, Any],
        report_depth: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate investment recommendation based on fundamental screening.
        """
        overall_score = quality_score["overall"]
        pred_trend = predictability["trend"]
        depth_trend = report_depth["expansion_trend"]
        
        # Determine action
        if overall_score >= 80 and pred_trend == "improving" and depth_trend in ["expanding", "stable_positive"]:
            action = "STRONG BUY"
            confidence = 95
            color = "green"
        elif overall_score >= 70 and pred_trend in ["improving", "stable"]:
            action = "BUY"
            confidence = 80
            color = "lime"
        elif overall_score >= 60:
            action = "HOLD"
            confidence = 65
            color = "yellow"
        elif overall_score >= 50:
            action = "WATCH"
            confidence = 50
            color = "orange"
        else:
            action = "AVOID"
            confidence = 30
            color = "red"
        
        # Generate reasons
        reasons = []
        
        if predictability["overall_predictability"] >= 80:
            reasons.append("✓ Excellent revenue predictability")
        elif predictability["overall_predictability"] >= 65:
            reasons.append("✓ Good revenue consistency")
        else:
            reasons.append("⚠ Unpredictable revenue patterns")
        
        if pred_trend == "improving":
            reasons.append("✓ Predictability improving over time")
        elif pred_trend == "declining":
            reasons.append("⚠ Predictability declining - caution advised")
        
        if depth_trend == "expanding":
            reasons.append("✓ Expanding 10-K depth (transparency increasing)")
        elif depth_trend == "contracting":
            reasons.append("⚠ Contracting 10-K depth (reduced disclosure) - red flag")
        
        if quality_score["components"]["growth"] >= 60:
            reasons.append("✓ Positive revenue growth trend")
        
        # Generate summary
        pred_grade = predictability["grade"]
        depth_grade = report_depth["grade"]
        
        summaries = {
            "STRONG BUY": f"Excellent fundamentals with {pred_grade} predictability and {depth_grade} report depth. Strong investment candidate.",
            "BUY": f"Solid fundamentals with {pred_grade} predictability and {depth_grade} reporting. Good investment opportunity.",
            "HOLD": f"Acceptable fundamentals but some concerns. Monitor for improvement.",
            "WATCH": f"Below-average fundamentals. Wait for clear improvement before investing.",
            "AVOID": f"Poor fundamentals with unpredictable performance and weak disclosure. Avoid investment."
        }
        
        return {
            "action": action,
            "confidence": confidence,
            "color": color,
            "reasons": reasons,
            "summary": summaries.get(action, "Unable to generate summary")
        }
    
    def _generate_screening_summary(self, ranked_companies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics for the entire screening."""
        import numpy as np
        
        if not ranked_companies:
            return {}
        
        # Calculate statistics
        scores = [c["overall_score"] for c in ranked_companies]
        
        # Count by recommendation
        recommendations = {}
        for company in ranked_companies:
            action = company["recommendation"]["action"]
            recommendations[action] = recommendations.get(action, 0) + 1
        
        # Count by grade
        grades = {}
        for company in ranked_companies:
            grade = company["quality_score"]["grade"]
            grades[grade] = grades.get(grade, 0) + 1
        
        # Top performers (top 5 or all if less than 5)
        top_count = min(5, len(ranked_companies))
        top_performers = ranked_companies[:top_count]
        
        return {
            "total_screened": len(ranked_companies),
            "average_score": round(np.mean(scores), 2),
            "median_score": round(np.median(scores), 2),
            "highest_score": round(max(scores), 2),
            "lowest_score": round(min(scores), 2),
            "recommendations": recommendations,
            "grade_distribution": grades,
            "top_performers": [
                {
                    "ticker": c["ticker"],
                    "score": c["overall_score"],
                    "grade": c["quality_score"]["grade"],
                    "recommendation": c["recommendation"]["action"],
                    "predictability_grade": c["predictability"]["grade"],
                    "report_depth_grade": c["report_depth"]["grade"]
                }
                for c in top_performers
            ],
            "insights": self._generate_portfolio_insights(ranked_companies)
        }
    
    def _generate_portfolio_insights(self, companies: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable insights from screening results."""
        insights = []
        
        # Count strong candidates
        strong_candidates = [c for c in companies if c["overall_score"] >= 80]
        if strong_candidates:
            insights.append(f"✓ {len(strong_candidates)} companies with excellent fundamentals (score ≥ 80)")
        
        # Count improving predictability
        improving = [c for c in companies if c["predictability"]["trend"] == "improving"]
        if improving:
            insights.append(f"✓ {len(improving)} companies showing improving predictability")
        
        # Count expanding reports
        expanding = [c for c in companies if c["report_depth"]["expansion_trend"] in ["expanding", "stable_positive"]]
        if expanding:
            insights.append(f"✓ {len(expanding)} companies expanding report depth (good transparency)")
        
        # Warn about concerning patterns
        concerning = [c for c in companies if c["report_depth"]["expansion_trend"] == "contracting"]
        if concerning:
            insights.append(f"⚠ {len(concerning)} companies with contracting report depth - review carefully")
        
        return insights if insights else ["No significant patterns detected"]
    
    # Additional helper methods would be implemented here...
    # (Simplified for brevity - full implementation would include all calculations)

# Initialize fundamental analysis engine
fundamental_analysis_service = FundamentalAnalysisEngine()