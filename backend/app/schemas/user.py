from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from app.models.user import OrderType, OrderStatus


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    first_name: str
    last_name: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


# Portfolio Schemas
class PortfolioBase(BaseModel):
    name: str


class PortfolioCreate(PortfolioBase):
    pass


class PortfolioResponse(PortfolioBase):
    id: int
    user_id: int
    cash_balance: float
    total_value: float
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Position Schemas
class PositionResponse(BaseModel):
    id: int
    portfolio_id: int
    symbol: str
    quantity: int
    average_cost: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    
    class Config:
        from_attributes = True


# Trade Schemas
class TradeBase(BaseModel):
    symbol: str
    order_type: OrderType
    quantity: int
    price: float


class TradeCreate(TradeBase):
    portfolio_id: int


class TradeResponse(TradeBase):
    id: int
    user_id: int
    portfolio_id: int
    total_amount: float
    status: OrderStatus
    executed_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Market Data Schemas
class MarketDataResponse(BaseModel):
    symbol: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int
    timestamp: datetime
    
    class Config:
        from_attributes = True


class QuoteResponse(BaseModel):
    symbol: str
    price: float
    change: float
    change_percent: float
    timestamp: datetime


# Portfolio Summary
class PortfolioSummary(BaseModel):
    portfolio: PortfolioResponse
    positions: List[PositionResponse]
    total_gain_loss: float
    total_gain_loss_percent: float