import httpx
import json
from typing import Dict, Optional
from datetime import datetime, timedelta

from app.core.config import settings
from app.core.redis import cache


class AlphaVantageService:
    def __init__(self):
        self.api_key = settings.ALPHA_VANTAGE_API_KEY
        self.base_url = "https://www.alphavantage.co/query"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_quote(self, symbol: str) -> Optional[Dict]:
        """Get real-time quote for a symbol"""
        cache_key = f"quote:{symbol}"
        
        # Check cache first
        cached_data = await cache.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
        
        # Fetch from Alpha Vantage API
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        try:
            response = await self.client.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "Global Quote" in data:
                quote_data = data["Global Quote"]
                processed_data = {
                    "symbol": quote_data.get("01. symbol", symbol),
                    "price": float(quote_data.get("05. price", "0")),
                    "change": float(quote_data.get("09. change", "0")),
                    "change_percent": quote_data.get("10. change percent", "0%").replace("%", ""),
                    "timestamp": datetime.now().isoformat()
                }
                
                # Cache for 1 minute
                await cache.set(cache_key, json.dumps(processed_data), expire=60)
                return processed_data
                
        except Exception as e:
            print(f"Error fetching quote for {symbol}: {e}")
            # Return demo data if API fails
            return {
                "symbol": symbol,
                "price": 100.0,
                "change": 1.5,
                "change_percent": "1.5",
                "timestamp": datetime.now().isoformat()
            }
        
        return None
    
    async def get_intraday_data(self, symbol: str, interval: str = "5min") -> Optional[Dict]:
        """Get intraday time series data"""
        cache_key = f"intraday:{symbol}:{interval}"
        
        # Check cache first
        cached_data = await cache.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
        
        params = {
            "function": "TIME_SERIES_INTRADAY",
            "symbol": symbol,
            "interval": interval,
            "apikey": self.api_key,
            "outputsize": "compact"
        }
        
        try:
            response = await self.client.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if f"Time Series ({interval})" in data:
                time_series = data[f"Time Series ({interval})"]
                
                # Process data for charting
                chart_data = []
                for timestamp, values in sorted(time_series.items()):
                    chart_data.append({
                        "timestamp": timestamp,
                        "open": float(values["1. open"]),
                        "high": float(values["2. high"]),
                        "low": float(values["3. low"]),
                        "close": float(values["4. close"]),
                        "volume": int(values["5. volume"])
                    })
                
                result = {
                    "symbol": symbol,
                    "interval": interval,
                    "data": chart_data[-100:]  # Last 100 data points
                }
                
                # Cache for 5 minutes
                await cache.set(cache_key, json.dumps(result), expire=300)
                return result
                
        except Exception as e:
            print(f"Error fetching intraday data for {symbol}: {e}")
        
        return None
    
    async def search_symbols(self, keywords: str) -> Optional[list]:
        """Search for stock symbols"""
        cache_key = f"search:{keywords}"
        
        # Check cache first
        cached_data = await cache.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
        
        params = {
            "function": "SYMBOL_SEARCH",
            "keywords": keywords,
            "apikey": self.api_key
        }
        
        try:
            response = await self.client.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "bestMatches" in data:
                results = []
                for match in data["bestMatches"][:10]:  # Top 10 results
                    results.append({
                        "symbol": match.get("1. symbol"),
                        "name": match.get("2. name"),
                        "type": match.get("3. type"),
                        "region": match.get("4. region"),
                        "currency": match.get("8. currency")
                    })
                
                # Cache for 1 hour
                await cache.set(cache_key, json.dumps(results), expire=3600)
                return results
                
        except Exception as e:
            print(f"Error searching symbols for {keywords}: {e}")
        
        return None
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()


# Global service instance
market_service = AlphaVantageService()