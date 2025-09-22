from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.models.user import User, Portfolio, Position, Trade, OrderStatus
from app.schemas.user import UserCreate, PortfolioCreate, TradeCreate
from app.core.utils import get_password_hash


async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
    """Get user by ID"""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get user by email"""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """Get user by username"""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    """Create new user"""
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    # Create default portfolio
    default_portfolio = Portfolio(
        user_id=db_user.id,
        name="Main Portfolio"
    )
    db.add(default_portfolio)
    await db.commit()
    await db.refresh(default_portfolio)
    
    return db_user


async def get_user_portfolios(db: AsyncSession, user_id: int) -> List[Portfolio]:
    """Get all portfolios for a user"""
    result = await db.execute(
        select(Portfolio)
        .where(Portfolio.user_id == user_id)
        .options(selectinload(Portfolio.positions))
    )
    return result.scalars().all()


async def create_portfolio(db: AsyncSession, portfolio: PortfolioCreate, user_id: int) -> Portfolio:
    """Create new portfolio"""
    db_portfolio = Portfolio(
        user_id=user_id,
        name=portfolio.name
    )
    db.add(db_portfolio)
    await db.commit()
    await db.refresh(db_portfolio)
    return db_portfolio


async def get_portfolio_positions(db: AsyncSession, portfolio_id: int) -> List[Position]:
    """Get all positions for a portfolio"""
    result = await db.execute(
        select(Position).where(Position.portfolio_id == portfolio_id)
    )
    return result.scalars().all()


async def get_user_trades(db: AsyncSession, user_id: int) -> List[Trade]:
    """Get all trades for a user"""
    result = await db.execute(
        select(Trade)
        .where(Trade.user_id == user_id)
        .order_by(Trade.created_at.desc())
    )
    return result.scalars().all()


async def create_trade(db: AsyncSession, trade: TradeCreate, user_id: int) -> Trade:
    """Create new trade"""
    total_amount = trade.quantity * trade.price
    
    db_trade = Trade(
        user_id=user_id,
        portfolio_id=trade.portfolio_id,
        symbol=trade.symbol,
        order_type=trade.order_type,
        quantity=trade.quantity,
        price=trade.price,
        total_amount=total_amount
    )
    db.add(db_trade)
    await db.commit()
    await db.refresh(db_trade)
    return db_trade


async def update_trade_status(db: AsyncSession, trade_id: int, status: OrderStatus) -> Optional[Trade]:
    """Update trade status"""
    result = await db.execute(
        update(Trade)
        .where(Trade.id == trade_id)
        .values(status=status)
        .returning(Trade)
    )
    await db.commit()
    return result.scalar_one_or_none()


async def get_position_by_symbol(db: AsyncSession, portfolio_id: int, symbol: str) -> Optional[Position]:
    """Get position by portfolio and symbol"""
    result = await db.execute(
        select(Position)
        .where(Position.portfolio_id == portfolio_id)
        .where(Position.symbol == symbol)
    )
    return result.scalar_one_or_none()


async def update_position(db: AsyncSession, position_id: int, quantity: int, average_cost: float, current_price: float) -> Optional[Position]:
    """Update position details"""
    market_value = quantity * current_price
    unrealized_pnl = (current_price - average_cost) * quantity
    
    result = await db.execute(
        update(Position)
        .where(Position.id == position_id)
        .values(
            quantity=quantity,
            average_cost=average_cost,
            current_price=current_price,
            market_value=market_value,
            unrealized_pnl=unrealized_pnl
        )
        .returning(Position)
    )
    await db.commit()
    return result.scalar_one_or_none()


async def create_position(db: AsyncSession, portfolio_id: int, symbol: str, quantity: int, average_cost: float, current_price: float) -> Position:
    """Create new position"""
    market_value = quantity * current_price
    unrealized_pnl = (current_price - average_cost) * quantity
    
    db_position = Position(
        portfolio_id=portfolio_id,
        symbol=symbol,
        quantity=quantity,
        average_cost=average_cost,
        current_price=current_price,
        market_value=market_value,
        unrealized_pnl=unrealized_pnl
    )
    db.add(db_position)
    await db.commit()
    await db.refresh(db_position)
    return db_position