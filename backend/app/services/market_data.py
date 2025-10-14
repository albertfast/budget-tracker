from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
import asyncio
import aiohttp
from dataclasses import dataclass

from .technical_analysis import PriceData

logger = logging.getLogger(__name__)

@dataclass
class MarketQuote:
    """Real-time market quote"""
    symbol: str
    last_price: float
    bid: float
    ask: float
    volume: int
    market_cap: Optional[float]
    pe_ratio: Optional[float]
    timestamp: datetime

@dataclass
class CompanyProfile:
    """Company profile information"""
    symbol: str
    name: str
    sector: str
    industry: str
    market_cap: float
    employees: Optional[int]
    description: str

class MarketDataService:
    """Service for fetching market data from various sources"""
    
    def __init__(self):
        self.api_keys = self._load_api_keys()
        self.data_sources = {
            "alpha_vantage": "https://www.alphavantage.co/query",
            "yahoo_finance": "https://query1.finance.yahoo.com/v8/finance/chart",
            "iex_cloud": "https://cloud.iexapis.com/stable",
            "polygon": "https://api.polygon.io"
        }
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def get_historical_data(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d"
    ) -> List[PriceData]:
        """Fetch historical price data for a symbol"""
        
        try:
            # Try primary data source first
            data = await self._fetch_yahoo_finance_data(symbol, period, interval)
            if data:
                return data
            
            # Fallback to Alpha Vantage
            data = await self._fetch_alpha_vantage_data(symbol, period, interval)
            if data:
                return data
            
            # Generate mock data if no API available (for development)
            logger.warning(f"No market data available for {symbol}, generating mock data")
            return self._generate_mock_data(symbol, period)
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
            return self._generate_mock_data(symbol, period)
    
    async def get_real_time_quote(self, symbol: str) -> Optional[MarketQuote]:
        """Get real-time quote for a symbol"""
        
        try:
            # Try to fetch real-time data
            quote_data = await self._fetch_yahoo_quote(symbol)
            if quote_data:
                return quote_data
            
            # Fallback to mock data
            return self._generate_mock_quote(symbol)
            
        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {str(e)}")
            return self._generate_mock_quote(symbol)
    
    async def get_company_profile(self, symbol: str) -> Optional[CompanyProfile]:
        """Get company profile information"""
        
        try:
            profile_data = await self._fetch_company_profile(symbol)
            if profile_data:
                return profile_data
            
            return self._generate_mock_profile(symbol)
            
        except Exception as e:
            logger.error(f"Error fetching company profile for {symbol}: {str(e)}")
            return self._generate_mock_profile(symbol)
    
    async def get_financial_statements(self, symbol: str) -> List[Dict[str, Any]]:
        """Fetch financial statements data"""
        
        try:
            # Try to fetch real financial data
            statements = await self._fetch_financial_statements(symbol)
            if statements:
                return statements
            
            # Generate mock financial data
            return self._generate_mock_financial_statements(symbol)
            
        except Exception as e:
            logger.error(f"Error fetching financial statements for {symbol}: {str(e)}")
            return self._generate_mock_financial_statements(symbol)
    
    async def _fetch_yahoo_finance_data(
        self,
        symbol: str,
        period: str,
        interval: str
    ) -> Optional[List[PriceData]]:
        """Fetch data from Yahoo Finance API"""
        
        if not self.session:
            return None
        
        try:
            # Convert period to Yahoo Finance format
            period_map = {
                "1d": "1d", "5d": "5d", "1mo": "1mo", "3mo": "3mo",
                "6mo": "6mo", "1y": "1y", "2y": "2y", "5y": "5y", "10y": "10y"
            }
            yahoo_period = period_map.get(period, "1y")
            
            url = f"{self.data_sources['yahoo_finance']}/{symbol}"
            params = {
                "period1": self._get_period_start_timestamp(period),
                "period2": int(datetime.now().timestamp()),
                "interval": interval,
                "includePrePost": "false",
                "events": "div,splits"
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_yahoo_data(data, symbol)
                
        except Exception as e:
            logger.error(f"Yahoo Finance API error for {symbol}: {str(e)}")
        
        return None
    
    async def _fetch_alpha_vantage_data(
        self,
        symbol: str,
        period: str,
        interval: str
    ) -> Optional[List[PriceData]]:
        """Fetch data from Alpha Vantage API"""
        
        if not self.session or not self.api_keys.get("alpha_vantage"):
            return None
        
        try:
            function = "TIME_SERIES_DAILY" if interval == "1d" else "TIME_SERIES_INTRADAY"
            params = {
                "function": function,
                "symbol": symbol,
                "apikey": self.api_keys["alpha_vantage"],
                "outputsize": "full"
            }
            
            if function == "TIME_SERIES_INTRADAY":
                params["interval"] = interval
            
            async with self.session.get(self.data_sources["alpha_vantage"], params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_alpha_vantage_data(data, symbol)
                
        except Exception as e:
            logger.error(f"Alpha Vantage API error for {symbol}: {str(e)}")
        
        return None
    
    async def _fetch_yahoo_quote(self, symbol: str) -> Optional[MarketQuote]:
        """Fetch real-time quote from Yahoo Finance"""
        
        if not self.session:
            return None
        
        try:
            url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{symbol}"
            params = {
                "modules": "price,summaryDetail"
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_yahoo_quote(data, symbol)
                
        except Exception as e:
            logger.error(f"Yahoo quote API error for {symbol}: {str(e)}")
        
        return None
    
    async def _fetch_company_profile(self, symbol: str) -> Optional[CompanyProfile]:
        """Fetch company profile information"""
        
        if not self.session:
            return None
        
        try:
            url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{symbol}"
            params = {
                "modules": "assetProfile,summaryProfile"
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_company_profile(data, symbol)
                
        except Exception as e:
            logger.error(f"Company profile API error for {symbol}: {str(e)}")
        
        return None
    
    async def _fetch_financial_statements(self, symbol: str) -> Optional[List[Dict[str, Any]]]:
        """Fetch financial statements data"""
        
        if not self.session:
            return None
        
        try:
            url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{symbol}"
            params = {
                "modules": "incomeStatementHistory,balanceSheetHistory,cashflowStatementHistory"
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_financial_statements(data, symbol)
                
        except Exception as e:
            logger.error(f"Financial statements API error for {symbol}: {str(e)}")
        
        return None
    
    def _parse_yahoo_data(self, data: Dict[str, Any], symbol: str) -> List[PriceData]:
        """Parse Yahoo Finance historical data"""
        
        try:
            chart = data["chart"]["result"][0]
            timestamps = chart["timestamp"]
            indicators = chart["indicators"]["quote"][0]
            
            price_data = []
            for i, timestamp in enumerate(timestamps):
                if all(indicators[key][i] is not None for key in ["open", "high", "low", "close"]):
                    price_data.append(PriceData(
                        timestamp=datetime.fromtimestamp(timestamp),
                        open=float(indicators["open"][i]),
                        high=float(indicators["high"][i]),
                        low=float(indicators["low"][i]),
                        close=float(indicators["close"][i]),
                        volume=int(indicators["volume"][i] or 0)
                    ))
            
            return price_data
            
        except Exception as e:
            logger.error(f"Error parsing Yahoo data for {symbol}: {str(e)}")
            return []
    
    def _generate_mock_data(self, symbol: str, period: str) -> List[PriceData]:
        """Generate realistic mock price data for development"""
        
        import random
        import math
        
        # Calculate number of days
        days_map = {
            "1d": 1, "5d": 5, "1mo": 30, "3mo": 90,
            "6mo": 180, "1y": 365, "2y": 730, "5y": 1825
        }
        days = days_map.get(period, 365)
        
        # Starting parameters
        base_price = 100.0  # Base price
        volatility = 0.02   # Daily volatility (2%)
        trend = 0.0001      # Slight upward trend
        
        # Generate price data
        price_data = []
        current_price = base_price
        start_date = datetime.now() - timedelta(days=days)
        
        for i in range(days):
            date = start_date + timedelta(days=i)
            
            # Random walk with trend
            price_change = random.normalvariate(trend, volatility)
            current_price *= (1 + price_change)
            
            # Ensure positive prices
            current_price = max(current_price, 1.0)
            
            # Generate OHLC with some intraday volatility
            daily_volatility = volatility * 0.5
            intraday_high = current_price * (1 + abs(random.normalvariate(0, daily_volatility)))
            intraday_low = current_price * (1 - abs(random.normalvariate(0, daily_volatility)))
            
            # Ensure logical OHLC relationship
            open_price = current_price * (1 + random.normalvariate(0, daily_volatility * 0.5))
            close_price = current_price
            high_price = max(open_price, close_price, intraday_high)
            low_price = min(open_price, close_price, intraday_low)
            
            # Generate volume (log-normal distribution)
            base_volume = 1000000
            volume = int(random.lognormvariate(math.log(base_volume), 0.5))
            
            price_data.append(PriceData(
                timestamp=date,
                open=round(open_price, 2),
                high=round(high_price, 2),
                low=round(low_price, 2),
                close=round(close_price, 2),
                volume=volume
            ))
        
        return price_data
    
    def _generate_mock_quote(self, symbol: str) -> MarketQuote:
        """Generate mock real-time quote"""
        
        import random
        
        base_price = 150.0
        spread = 0.01
        
        last_price = base_price * (1 + random.normalvariate(0, 0.02))
        bid = last_price - (spread / 2)
        ask = last_price + (spread / 2)
        volume = random.randint(500000, 5000000)
        
        return MarketQuote(
            symbol=symbol,
            last_price=round(last_price, 2),
            bid=round(bid, 2),
            ask=round(ask, 2),
            volume=volume,
            market_cap=last_price * 1000000,  # Mock market cap
            pe_ratio=random.uniform(15, 25),
            timestamp=datetime.now()
        )
    
    def _generate_mock_profile(self, symbol: str) -> CompanyProfile:
        """Generate mock company profile"""
        
        mock_companies = {
            "AAPL": {
                "name": "Apple Inc.",
                "sector": "Technology",
                "industry": "Consumer Electronics",
                "market_cap": 3000000000000,
                "employees": 164000,
                "description": "Technology company specializing in consumer electronics"
            },
            "MSFT": {
                "name": "Microsoft Corporation",
                "sector": "Technology",
                "industry": "Software",
                "market_cap": 2800000000000,
                "employees": 221000,
                "description": "Software and cloud computing company"
            }
        }
        
        if symbol in mock_companies:
            company_data = mock_companies[symbol]
        else:
            company_data = {
                "name": f"{symbol} Corporation",
                "sector": "Technology",
                "industry": "Software",
                "market_cap": 100000000000,
                "employees": 50000,
                "description": f"Mock company for {symbol}"
            }
        
        return CompanyProfile(
            symbol=symbol,
            name=company_data["name"],
            sector=company_data["sector"],
            industry=company_data["industry"],
            market_cap=company_data["market_cap"],
            employees=company_data["employees"],
            description=company_data["description"]
        )
    
    def _generate_mock_financial_statements(self, symbol: str) -> List[Dict[str, Any]]:
        """Generate mock financial statements"""
        
        import random
        
        # Generate 4 quarters of financial data
        statements = []
        base_revenue = 10000000000  # $10B base revenue
        
        for quarter in range(4):
            # Add some quarterly variation
            revenue = base_revenue * (1 + random.uniform(-0.1, 0.2))
            gross_profit = revenue * random.uniform(0.35, 0.65)
            operating_income = gross_profit * random.uniform(0.15, 0.35)
            net_income = operating_income * random.uniform(0.7, 0.9)
            
            total_assets = revenue * random.uniform(1.5, 3.0)
            total_debt = total_assets * random.uniform(0.2, 0.5)
            shareholders_equity = total_assets - total_debt
            
            statements.append({
                "period": f"Q{4-quarter} 2024",
                "revenue": revenue,
                "gross_profit": gross_profit,
                "operating_income": operating_income,
                "net_income": net_income,
                "total_assets": total_assets,
                "total_debt": total_debt,
                "shareholders_equity": shareholders_equity,
                "cash_and_equivalents": total_assets * random.uniform(0.1, 0.3),
                "current_assets": total_assets * random.uniform(0.4, 0.6),
                "current_liabilities": total_assets * random.uniform(0.15, 0.25)
            })
        
        return statements
    
    def _get_period_start_timestamp(self, period: str) -> int:
        """Get start timestamp for a given period"""
        
        now = datetime.now()
        period_map = {
            "1d": timedelta(days=1),
            "5d": timedelta(days=5),
            "1mo": timedelta(days=30),
            "3mo": timedelta(days=90),
            "6mo": timedelta(days=180),
            "1y": timedelta(days=365),
            "2y": timedelta(days=730),
            "5y": timedelta(days=1825)
        }
        
        delta = period_map.get(period, timedelta(days=365))
        start_time = now - delta
        
        return int(start_time.timestamp())
    
    def _load_api_keys(self) -> Dict[str, str]:
        """Load API keys from environment or configuration"""
        
        import os
        
        return {
            "alpha_vantage": os.getenv("ALPHA_VANTAGE_API_KEY", ""),
            "iex_cloud": os.getenv("IEX_CLOUD_API_KEY", ""),
            "polygon": os.getenv("POLYGON_API_KEY", "")
        }

# Initialize market data service
market_data_service = MarketDataService()