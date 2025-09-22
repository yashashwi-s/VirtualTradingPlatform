from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.crud.user import get_user_portfolios, create_portfolio, get_portfolio_positions
from app.schemas.user import PortfolioCreate, PortfolioResponse, PositionResponse, PortfolioSummary
from app.models.user import User
from app.services.trading_engine import trading_engine

router = APIRouter()


@router.get("/", response_model=List[PortfolioResponse])
async def get_portfolios(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all portfolios for the current user"""
    return await get_user_portfolios(db, current_user.id)


@router.post("/", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
async def create_user_portfolio(
    portfolio: PortfolioCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new portfolio for the current user"""
    return await create_portfolio(db, portfolio, current_user.id)


@router.get("/{portfolio_id}/positions", response_model=List[PositionResponse])
async def get_portfolio_positions_endpoint(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all positions for a specific portfolio"""
    # Verify portfolio belongs to current user
    portfolios = await get_user_portfolios(db, current_user.id)
    portfolio_ids = [p.id for p in portfolios]
    
    if portfolio_id not in portfolio_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    return await get_portfolio_positions(db, portfolio_id)


@router.get("/{portfolio_id}/summary", response_model=dict)
async def get_portfolio_summary(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive portfolio summary"""
    # Verify portfolio belongs to current user
    portfolios = await get_user_portfolios(db, current_user.id)
    portfolio_ids = [p.id for p in portfolios]
    
    if portfolio_id not in portfolio_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    summary = await trading_engine.get_portfolio_summary(db, portfolio_id)
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    return summary