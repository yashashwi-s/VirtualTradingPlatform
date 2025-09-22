from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.crud.user import create_trade, get_user_trades, get_user_portfolios
from app.schemas.user import TradeCreate, TradeResponse
from app.models.user import User
from app.services.trading_engine import trading_engine

router = APIRouter()


@router.post("/", response_model=TradeResponse, status_code=status.HTTP_201_CREATED)
async def place_trade(
    trade: TradeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Place a new trade order"""
    
    # Verify portfolio belongs to current user
    portfolios = await get_user_portfolios(db, current_user.id)
    portfolio_ids = [p.id for p in portfolios]
    
    if trade.portfolio_id not in portfolio_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    # Create trade
    db_trade = await create_trade(db, trade, current_user.id)
    
    # Execute trade immediately (in a real system, this might be async)
    execution_success = await trading_engine.execute_trade(db, db_trade)
    
    if not execution_success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trade execution failed - insufficient funds or shares"
        )
    
    # Refresh trade object to get updated status
    await db.refresh(db_trade)
    return db_trade


@router.get("/", response_model=List[TradeResponse])
async def get_trades(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all trades for the current user"""
    return await get_user_trades(db, current_user.id)


@router.get("/{trade_id}", response_model=TradeResponse)
async def get_trade(
    trade_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific trade by ID"""
    trades = await get_user_trades(db, current_user.id)
    trade = next((t for t in trades if t.id == trade_id), None)
    
    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trade not found"
        )
    
    return trade