from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


class OrderType(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    EXECUTED = "EXECUTED"
    CANCELLED = "CANCELLED"


class StrategyType(str, enum.Enum):
    MANUAL = "MANUAL"
    ALGORITHMIC = "ALGORITHMIC"
    WEBHOOK = "WEBHOOK"


class StrategyStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    STOPPED = "STOPPED"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    portfolios = relationship("Portfolio", back_populates="user")
    trades = relationship("Trade", back_populates="user")
    strategies = relationship("Strategy", back_populates="user")


class Portfolio(Base):
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    cash_balance = Column(Float, default=100000.0)  # Starting with $100,000 virtual cash
    total_value = Column(Float, default=100000.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="portfolios")
    positions = relationship("Position", back_populates="portfolio")
    trades = relationship("Trade", back_populates="portfolio")
    strategies = relationship("Strategy", back_populates="portfolio")


class Position(Base):
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    symbol = Column(String, nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    average_cost = Column(Float, nullable=False)
    current_price = Column(Float, default=0.0)
    market_value = Column(Float, default=0.0)
    unrealized_pnl = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="positions")


class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=True)
    symbol = Column(String, nullable=False, index=True)
    order_type = Column(Enum(OrderType), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    executed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="trades")
    portfolio = relationship("Portfolio", back_populates="trades")
    strategy = relationship("Strategy", back_populates="trades")


class MarketData(Base):
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False, index=True)
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Strategy(Base):
    __tablename__ = "strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    strategy_type = Column(Enum(StrategyType), default=StrategyType.MANUAL)
    status = Column(Enum(StrategyStatus), default=StrategyStatus.DRAFT)
    
    # Configuration
    capital_allocation = Column(Float, default=0.0)  # Amount allocated to this strategy
    max_position_size = Column(Float, default=0.1)   # Max % of capital per position
    
    # Webhook configuration (for external strategies)
    webhook_url = Column(String, nullable=True)
    webhook_secret = Column(String, nullable=True)
    
    # Strategy parameters (JSON field for flexibility)
    parameters = Column(JSON, default=dict)
    
    # Performance metrics
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    total_return = Column(Float, default=0.0)
    current_drawdown = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_executed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="strategies")
    portfolio = relationship("Portfolio", back_populates="strategies")
    trades = relationship("Trade", back_populates="strategy")
    executions = relationship("StrategyExecution", back_populates="strategy")


class StrategyExecution(Base):
    __tablename__ = "strategy_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=False)
    
    # Execution details
    signal_type = Column(String, nullable=False)  # BUY, SELL, HOLD
    symbol = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    
    # Signal metadata
    signal_strength = Column(Float, default=1.0)
    signal_data = Column(JSON, default=dict)  # Raw signal data
    
    # Execution results
    executed = Column(Boolean, default=False)
    trade_id = Column(Integer, ForeignKey("trades.id"), nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    signal_timestamp = Column(DateTime(timezone=True), nullable=False)
    executed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    strategy = relationship("Strategy", back_populates="executions")