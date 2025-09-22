from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel

from app.models.user import StrategyType, StrategyStatus


class StrategyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    strategy_type: StrategyType = StrategyType.MANUAL
    portfolio_id: int
    capital_allocation: float = 0.0
    max_position_size: float = 0.1
    webhook_url: Optional[str] = None
    webhook_secret: Optional[str] = None
    parameters: Dict[str, Any] = {}


class StrategyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[StrategyStatus] = None
    capital_allocation: Optional[float] = None
    max_position_size: Optional[float] = None
    webhook_url: Optional[str] = None
    webhook_secret: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


class StrategyResponse(BaseModel):
    id: int
    user_id: int
    portfolio_id: int
    name: str
    description: Optional[str]
    strategy_type: StrategyType
    status: StrategyStatus
    capital_allocation: float
    max_position_size: float
    webhook_url: Optional[str]
    parameters: Dict[str, Any]
    
    # Performance metrics
    total_trades: int
    winning_trades: int
    total_return: float
    current_drawdown: float
    max_drawdown: float
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime]
    last_executed_at: Optional[datetime]

    class Config:
        from_attributes = True


class StrategyExecutionCreate(BaseModel):
    strategy_id: int
    signal_type: str  # BUY, SELL, HOLD
    symbol: str
    quantity: int
    price: float
    signal_strength: float = 1.0
    signal_data: Dict[str, Any] = {}
    signal_timestamp: datetime


class StrategyExecutionResponse(BaseModel):
    id: int
    strategy_id: int
    signal_type: str
    symbol: str
    quantity: int
    price: float
    signal_strength: float
    signal_data: Dict[str, Any]
    executed: bool
    trade_id: Optional[int]
    error_message: Optional[str]
    signal_timestamp: datetime
    executed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class WebhookSignal(BaseModel):
    """Webhook payload format for external strategy signals"""
    strategy_id: int
    action: str  # BUY, SELL, HOLD
    symbol: str
    quantity: Optional[int] = None
    price: Optional[float] = None
    percentage: Optional[float] = None  # Position size as % of allocated capital
    signal_strength: float = 1.0
    metadata: Dict[str, Any] = {}
    timestamp: Optional[datetime] = None


class StrategyPerformanceResponse(BaseModel):
    strategy_id: int
    name: str
    total_return: float
    total_return_percent: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    avg_win: float
    avg_loss: float
    current_drawdown: float
    max_drawdown: float
    sharpe_ratio: Optional[float]
    recent_trades: List[Dict[str, Any]]