from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query

from app.services.market_data import market_service
from app.schemas.user import QuoteResponse, MarketDataResponse

router = APIRouter()


@router.get("/quote/{symbol}", response_model=QuoteResponse)
async def get_stock_quote(symbol: str):
    """Get real-time stock quote"""
    quote = await market_service.get_quote(symbol.upper())
    
    if not quote:
        raise HTTPException(
            status_code=404,
            detail=f"Quote not found for symbol {symbol}"
        )
    
    return QuoteResponse(**quote)


@router.get("/intraday/{symbol}")
async def get_intraday_data(
    symbol: str,
    interval: str = Query(default="5min", regex="^(1min|5min|15min|30min|60min)$")
):
    """Get intraday chart data"""
    data = await market_service.get_intraday_data(symbol.upper(), interval)
    
    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"Intraday data not found for symbol {symbol}"
        )
    
    return data


@router.get("/search")
async def search_stocks(keywords: str = Query(..., min_length=1)):
    """Search for stock symbols"""
    results = await market_service.search_symbols(keywords)
    
    if not results:
        return []
    
    return results