from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update as sql_update
from datetime import datetime
import hmac
import hashlib
import json

from app.models.user import Strategy, StrategyExecution, Trade, Portfolio, StrategyStatus, OrderType, OrderStatus
from app.schemas.strategy import StrategyCreate, StrategyUpdate, WebhookSignal
from app.services.trading_engine import trading_engine


class StrategyService:
    """Service for managing trading strategies and executions"""
    
    async def create_strategy(self, db: AsyncSession, user_id: int, strategy_data: StrategyCreate) -> Strategy:
        """Create a new trading strategy"""
        # Verify user owns the portfolio
        portfolio_result = await db.execute(
            select(Portfolio).where(
                Portfolio.id == strategy_data.portfolio_id,
                Portfolio.user_id == user_id
            )
        )
        portfolio = portfolio_result.scalar_one_or_none()
        if not portfolio:
            raise ValueError("Portfolio not found or access denied")
        
        # Create strategy
        strategy = Strategy(
            user_id=user_id,
            portfolio_id=strategy_data.portfolio_id,
            name=strategy_data.name,
            description=strategy_data.description,
            strategy_type=strategy_data.strategy_type,
            capital_allocation=strategy_data.capital_allocation,
            max_position_size=strategy_data.max_position_size,
            webhook_url=strategy_data.webhook_url,
            webhook_secret=strategy_data.webhook_secret,
            parameters=strategy_data.parameters
        )
        
        db.add(strategy)
        await db.commit()
        await db.refresh(strategy)
        
        return strategy
    
    async def get_strategy(self, db: AsyncSession, user_id: int, strategy_id: int) -> Optional[Strategy]:
        """Get a strategy by ID"""
        result = await db.execute(
            select(Strategy).where(
                Strategy.id == strategy_id,
                Strategy.user_id == user_id
            )
        )
        return result.scalar_one_or_none()
    
    async def get_user_strategies(self, db: AsyncSession, user_id: int) -> List[Strategy]:
        """Get all strategies for a user"""
        result = await db.execute(
            select(Strategy).where(Strategy.user_id == user_id).order_by(Strategy.created_at.desc())
        )
        return result.scalars().all()
    
    async def update_strategy(
        self, db: AsyncSession, user_id: int, strategy_id: int, strategy_data: StrategyUpdate
    ) -> Optional[Strategy]:
        """Update a strategy"""
        strategy = await self.get_strategy(db, user_id, strategy_id)
        if not strategy:
            return None
        
        # Update fields
        update_data = strategy_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(strategy, field, value)
        
        strategy.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(strategy)
        
        return strategy
    
    async def delete_strategy(self, db: AsyncSession, user_id: int, strategy_id: int) -> bool:
        """Delete a strategy"""
        strategy = await self.get_strategy(db, user_id, strategy_id)
        if not strategy:
            return False
        
        await db.delete(strategy)
        await db.commit()
        return True
    
    async def execute_webhook_signal(self, db: AsyncSession, signal: WebhookSignal, webhook_signature: str) -> Dict[str, Any]:
        """Process incoming webhook signal"""
        # Get strategy
        strategy = await self.get_strategy(db, None, signal.strategy_id)  # Note: No user_id check for webhook
        if not strategy or strategy.status != StrategyStatus.ACTIVE:
            return {"success": False, "error": "Strategy not found or not active"}
        
        # Verify webhook signature if secret is set
        if strategy.webhook_secret:
            expected_signature = hmac.new(
                strategy.webhook_secret.encode(),
                json.dumps(signal.dict(), default=str).encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(f"sha256={expected_signature}", webhook_signature):
                return {"success": False, "error": "Invalid signature"}
        
        # Process signal
        try:
            execution = await self._process_signal(db, strategy, signal)
            return {
                "success": True, 
                "execution_id": execution.id,
                "executed": execution.executed
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _process_signal(self, db: AsyncSession, strategy: Strategy, signal: WebhookSignal) -> StrategyExecution:
        """Process a trading signal"""
        # Create execution record
        execution = StrategyExecution(
            strategy_id=strategy.id,
            signal_type=signal.action,
            symbol=signal.symbol,
            quantity=signal.quantity or self._calculate_quantity(strategy, signal),
            price=signal.price or 0.0,  # Will be filled with current market price
            signal_strength=signal.signal_strength,
            signal_data=signal.metadata,
            signal_timestamp=signal.timestamp or datetime.utcnow()
        )
        
        db.add(execution)
        await db.commit()
        await db.refresh(execution)
        
        # Execute trade if signal is BUY or SELL
        if signal.action in ['BUY', 'SELL'] and strategy.status == StrategyStatus.ACTIVE:
            try:
                trade = await self._create_trade_from_signal(db, strategy, execution)
                if trade:
                    # Execute the trade
                    success = await trading_engine.execute_trade(db, trade)
                    if success:
                        execution.executed = True
                        execution.trade_id = trade.id
                        execution.executed_at = datetime.utcnow()
                        
                        # Update strategy metrics
                        await self._update_strategy_metrics(db, strategy)
                    else:
                        execution.error_message = "Trade execution failed"
                
            except Exception as e:
                execution.error_message = str(e)
        
        execution.executed_at = datetime.utcnow()
        await db.commit()
        await db.refresh(execution)
        
        return execution
    
    def _calculate_quantity(self, strategy: Strategy, signal: WebhookSignal) -> int:
        """Calculate position quantity based on allocation and signal"""
        if signal.percentage:
            # Use percentage of allocated capital
            position_value = strategy.capital_allocation * (signal.percentage / 100.0)
            if signal.price and signal.price > 0:
                return max(1, int(position_value / signal.price))
        
        # Default to small position
        return max(1, int(strategy.capital_allocation * strategy.max_position_size / (signal.price or 100)))
    
    async def _create_trade_from_signal(self, db: AsyncSession, strategy: Strategy, execution: StrategyExecution) -> Optional[Trade]:
        """Create a trade from a strategy execution"""
        from app.services.market_data import market_service
        
        # Get current market price if not provided
        if execution.price == 0.0:
            quote = await market_service.get_quote(execution.symbol)
            if not quote:
                raise ValueError(f"Could not get market data for {execution.symbol}")
            execution.price = quote["price"]
        
        # Create trade
        trade = Trade(
            user_id=strategy.user_id,
            portfolio_id=strategy.portfolio_id,
            strategy_id=strategy.id,
            symbol=execution.symbol,
            order_type=OrderType.BUY if execution.signal_type == 'BUY' else OrderType.SELL,
            quantity=execution.quantity,
            price=execution.price,
            total_amount=execution.quantity * execution.price,
            status=OrderStatus.PENDING
        )
        
        db.add(trade)
        await db.commit()
        await db.refresh(trade)
        
        return trade
    
    async def _update_strategy_metrics(self, db: AsyncSession, strategy: Strategy):
        """Update strategy performance metrics"""
        # Get all executed trades for this strategy
        result = await db.execute(
            select(Trade).where(
                Trade.strategy_id == strategy.id,
                Trade.status == OrderStatus.EXECUTED
            )
        )
        trades = result.scalars().all()
        
        if trades:
            strategy.total_trades = len(trades)
            # Note: More complex P&L calculation would be needed here
            # For now, just update basic counts
            strategy.last_executed_at = datetime.utcnow()
        
        await db.commit()
    
    async def get_strategy_performance(self, db: AsyncSession, user_id: int, strategy_id: int) -> Optional[Dict[str, Any]]:
        """Calculate detailed strategy performance metrics"""
        strategy = await self.get_strategy(db, user_id, strategy_id)
        if not strategy:
            return None
        
        # Get all trades for this strategy
        result = await db.execute(
            select(Trade).where(
                Trade.strategy_id == strategy_id,
                Trade.status == OrderStatus.EXECUTED
            ).order_by(Trade.executed_at.desc())
        )
        trades = result.scalars().all()
        
        # Calculate metrics
        total_trades = len(trades)
        winning_trades = 0
        total_pnl = 0.0
        
        # Simplified P&L calculation (would need more sophisticated logic for real use)
        for trade in trades:
            # This is a placeholder - real P&L would require position tracking
            if trade.order_type == OrderType.SELL:
                # Assume profit for demo
                winning_trades += 1
                total_pnl += trade.total_amount * 0.02  # 2% profit assumption
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        return {
            "strategy_id": strategy_id,
            "name": strategy.name,
            "total_return": total_pnl,
            "total_return_percent": (total_pnl / strategy.capital_allocation * 100) if strategy.capital_allocation > 0 else 0,
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": total_trades - winning_trades,
            "win_rate": win_rate,
            "avg_win": total_pnl / winning_trades if winning_trades > 0 else 0,
            "avg_loss": 0,  # Simplified
            "current_drawdown": strategy.current_drawdown,
            "max_drawdown": strategy.max_drawdown,
            "sharpe_ratio": None,  # Would need historical returns
            "recent_trades": [
                {
                    "symbol": trade.symbol,
                    "type": trade.order_type,
                    "quantity": trade.quantity,
                    "price": trade.price,
                    "total": trade.total_amount,
                    "executed_at": trade.executed_at
                }
                for trade in trades[:10]  # Last 10 trades
            ]
        }


# Global strategy service instance
strategy_service = StrategyService()