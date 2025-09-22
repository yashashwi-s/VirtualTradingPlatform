from fastapi import APIRouter

from app.api.api_v1.endpoints import auth, portfolio, trading, market, strategy

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(portfolio.router, prefix="/portfolios", tags=["portfolios"])
api_router.include_router(trading.router, prefix="/trades", tags=["trading"])
api_router.include_router(market.router, prefix="/market", tags=["market-data"])
api_router.include_router(strategy.router, prefix="/strategies", tags=["strategies"])