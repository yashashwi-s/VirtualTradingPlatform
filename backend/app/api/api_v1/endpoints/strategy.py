from typing import List
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.strategy import (
    StrategyCreate, StrategyUpdate, StrategyResponse, 
    WebhookSignal, StrategyPerformanceResponse
)
from app.services.strategy import strategy_service

router = APIRouter()


@router.post("/", response_model=StrategyResponse)
async def create_strategy(
    strategy: StrategyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new trading strategy"""
    try:
        created_strategy = await strategy_service.create_strategy(db, current_user.id, strategy)
        return created_strategy
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create strategy")


@router.get("/", response_model=List[StrategyResponse])
async def get_strategies(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all strategies for the current user"""
    strategies = await strategy_service.get_user_strategies(db, current_user.id)
    return strategies


@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(
    strategy_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific strategy"""
    strategy = await strategy_service.get_strategy(db, current_user.id, strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy


@router.put("/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(
    strategy_id: int,
    strategy_update: StrategyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a strategy"""
    strategy = await strategy_service.update_strategy(db, current_user.id, strategy_id, strategy_update)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy


@router.delete("/{strategy_id}")
async def delete_strategy(
    strategy_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a strategy"""
    success = await strategy_service.delete_strategy(db, current_user.id, strategy_id)
    if not success:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return {"message": "Strategy deleted successfully"}


@router.get("/{strategy_id}/performance", response_model=StrategyPerformanceResponse)
async def get_strategy_performance(
    strategy_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed performance metrics for a strategy"""
    performance = await strategy_service.get_strategy_performance(db, current_user.id, strategy_id)
    if not performance:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return performance


@router.post("/webhook", status_code=200)
async def webhook_handler(
    signal: WebhookSignal,
    db: AsyncSession = Depends(get_db),
    x_signature: str = Header(None, alias="X-Signature")
):
    """Handle incoming webhook signals from external strategy services"""
    if not x_signature:
        raise HTTPException(status_code=401, detail="Missing signature header")
    
    result = await strategy_service.execute_webhook_signal(db, signal, x_signature)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.post("/{strategy_id}/activate")
async def activate_strategy(
    strategy_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Activate a strategy for live trading"""
    from app.models.user import StrategyStatus
    
    strategy_update = StrategyUpdate(status=StrategyStatus.ACTIVE)
    strategy = await strategy_service.update_strategy(db, current_user.id, strategy_id, strategy_update)
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    return {"message": "Strategy activated", "strategy_id": strategy_id}


@router.post("/{strategy_id}/pause")
async def pause_strategy(
    strategy_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Pause a strategy"""
    from app.models.user import StrategyStatus
    
    strategy_update = StrategyUpdate(status=StrategyStatus.PAUSED)
    strategy = await strategy_service.update_strategy(db, current_user.id, strategy_id, strategy_update)
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    return {"message": "Strategy paused", "strategy_id": strategy_id}


@router.post("/{strategy_id}/stop")
async def stop_strategy(
    strategy_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Stop a strategy"""
    from app.models.user import StrategyStatus
    
    strategy_update = StrategyUpdate(status=StrategyStatus.STOPPED)
    strategy = await strategy_service.update_strategy(db, current_user.id, strategy_id, strategy_update)
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    return {"message": "Strategy stopped", "strategy_id": strategy_id}