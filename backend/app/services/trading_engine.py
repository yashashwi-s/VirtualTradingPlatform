from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update as sql_update
from datetime import datetime

from app.models.user import Portfolio, Trade, OrderType, OrderStatus
from app.crud.user import (
    get_portfolio_positions, update_trade_status, get_position_by_symbol,
    update_position, create_position
)
from app.services.market_data import market_service


class TradingEngine:
    """Core trading engine for executing buy/sell orders"""
    
    async def execute_trade(self, db: AsyncSession, trade: Trade) -> bool:
        """Execute a pending trade"""
        try:
            # Get current market price
            quote = await market_service.get_quote(trade.symbol)
            if not quote:
                return False
            
            current_price = quote["price"]
            
            # Get portfolio
            portfolio_result = await db.execute(
                select(Portfolio).where(Portfolio.id == trade.portfolio_id)
            )
            portfolio = portfolio_result.scalar_one_or_none()
            if not portfolio:
                return False
            
            # Execute based on order type
            if trade.order_type == OrderType.BUY:
                success = await self._execute_buy_order(db, trade, portfolio, current_price)
            else:  # SELL
                success = await self._execute_sell_order(db, trade, portfolio, current_price)
            
            if success:
                # Update trade status
                await update_trade_status(db, trade.id, OrderStatus.EXECUTED)
                trade.executed_at = datetime.utcnow()
                await db.commit()
                
                # Update portfolio total value
                await self._update_portfolio_value(db, portfolio)
            
            return success
            
        except Exception as e:
            print(f"Error executing trade {trade.id}: {e}")
            return False
    
    async def _execute_buy_order(self, db: AsyncSession, trade: Trade, portfolio: Portfolio, current_price: float) -> bool:
        """Execute a buy order"""
        total_cost = trade.quantity * current_price
        
        # Check if portfolio has enough cash
        if portfolio.cash_balance < total_cost:
            return False
        
        # Update portfolio cash balance
        portfolio.cash_balance -= total_cost
        
        # Get existing position or create new one
        position = await get_position_by_symbol(db, portfolio.id, trade.symbol)
        
        if position:
            # Update existing position
            new_quantity = position.quantity + trade.quantity
            new_average_cost = ((position.average_cost * position.quantity) + total_cost) / new_quantity
            await update_position(db, position.id, new_quantity, new_average_cost, current_price)
        else:
            # Create new position
            await create_position(db, portfolio.id, trade.symbol, trade.quantity, current_price, current_price)
        
        return True
    
    async def _execute_sell_order(self, db: AsyncSession, trade: Trade, portfolio: Portfolio, current_price: float) -> bool:
        """Execute a sell order"""
        # Get existing position
        position = await get_position_by_symbol(db, portfolio.id, trade.symbol)
        
        if not position or position.quantity < trade.quantity:
            return False  # Not enough shares to sell
        
        # Calculate proceeds
        proceeds = trade.quantity * current_price
        
        # Update portfolio cash balance
        portfolio.cash_balance += proceeds
        
        # Update position
        new_quantity = position.quantity - trade.quantity
        
        if new_quantity == 0:
            # Remove position if quantity becomes zero
            await db.delete(position)
        else:
            # Update position quantity
            await update_position(db, position.id, new_quantity, position.average_cost, current_price)
        
        return True
    
    async def _update_portfolio_value(self, db: AsyncSession, portfolio: Portfolio):
        """Update portfolio total value"""
        positions = await get_portfolio_positions(db, portfolio.id)
        
        total_market_value = portfolio.cash_balance
        
        for position in positions:
            # Get current price for each position
            quote = await market_service.get_quote(position.symbol)
            if quote:
                current_price = quote["price"]
                position.current_price = current_price
                position.market_value = position.quantity * current_price
                position.unrealized_pnl = (current_price - position.average_cost) * position.quantity
                total_market_value += position.market_value
        
        portfolio.total_value = total_market_value
        await db.commit()
    
    async def calculate_portfolio_performance(self, db: AsyncSession, portfolio_id: int) -> dict:
        """Calculate portfolio performance metrics"""
        positions = await get_portfolio_positions(db, portfolio_id)
        
        total_cost = 0
        total_market_value = 0
        
        for position in positions:
            total_cost += position.average_cost * position.quantity
            total_market_value += position.market_value
        
        total_gain_loss = total_market_value - total_cost
        total_gain_loss_percent = (total_gain_loss / total_cost * 100) if total_cost > 0 else 0
        
        return {
            "total_cost": total_cost,
            "total_market_value": total_market_value,
            "total_gain_loss": total_gain_loss,
            "total_gain_loss_percent": round(total_gain_loss_percent, 2)
        }
    
    async def get_portfolio_summary(self, db: AsyncSession, portfolio_id: int) -> dict:
        """Get comprehensive portfolio summary"""
        # Get portfolio
        portfolio_result = await db.execute(
            select(Portfolio).where(Portfolio.id == portfolio_id)
        )
        portfolio = portfolio_result.scalar_one_or_none()
        
        if not portfolio:
            return None
        
        # Get positions
        positions = await get_portfolio_positions(db, portfolio_id)
        
        # Update current prices for all positions
        for position in positions:
            quote = await market_service.get_quote(position.symbol)
            if quote:
                current_price = quote["price"]
                await update_position(
                    db, position.id, position.quantity, 
                    position.average_cost, current_price
                )
        
        # Calculate performance
        performance = await self.calculate_portfolio_performance(db, portfolio_id)
        
        return {
            "portfolio": portfolio,
            "positions": positions,
            "performance": performance
        }


# Global trading engine instance
trading_engine = TradingEngine()