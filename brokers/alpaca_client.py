"""
Alpaca Client for Stock Trading
"""
try:
    import alpaca_trade_api as tradeapi
except ImportError:
    tradeapi = None
from typing import Dict, Any, Optional
from loguru import logger


class AlpacaClient:
    """Alpaca client for stock trading"""
    
    def __init__(self, api_key: str, secret_key: str, base_url: str = None, paper: bool = True):
        """
        Initialize Alpaca client
        
        Args:
            api_key: Alpaca API key
            secret_key: Alpaca secret key
            base_url: API base URL (optional)
            paper: Use paper trading
        """
        if tradeapi is None:
            raise ImportError("alpaca-trade-api not installed")
            
        self.api_key = api_key
        self.secret_key = secret_key
        self.paper = paper
        
        # Set base URL for paper trading if not provided
        if base_url is None:
            base_url = 'https://paper-api.alpaca.markets' if paper else 'https://api.alpaca.markets'
        
        self.api = tradeapi.REST(
            api_key,
            secret_key,
            base_url,
            api_version='v2'
        )
        
        logger.info(f"Initialized Alpaca client (paper: {paper})")
    
    def connect(self) -> bool:
        """Test connection to Alpaca"""
        try:
            account = self.api.get_account()
            logger.info(f"Connected to Alpaca account {account.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Alpaca: {e}")
            return False
    
    def get_balance(self) -> Dict[str, float]:
        """Get account balance"""
        try:
            account = self.api.get_account()
            return {
                'equity': float(account.equity),
                'buying_power': float(account.buying_power),
                'cash': float(account.cash),
                'portfolio_value': float(account.portfolio_value)
            }
        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
            return {}
    
    def get_price(self, symbol: str) -> Optional[float]:
        """Get current price for symbol"""
        try:
            bars = self.api.get_latest_bar(symbol)
            return float(bars.c)
        except Exception as e:
            logger.error(f"Failed to get price for {symbol}: {e}")
            return None
    
    def place_order(self, symbol: str, side: str, size: int, stop_loss: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """
        Place an order
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            side: 'buy' or 'sell'
            size: Number of shares
            stop_loss: Stop loss price (optional)
        
        Returns:
            Order info or None if failed
        """
        try:
            # Place market order
            order = self.api.submit_order(
                symbol=symbol,
                qty=size,
                side=side,
                type='market',
                time_in_force='day'
            )
            
            logger.info(f"Placed {side} order for {size} shares of {symbol}")
            
            # Place stop loss if specified
            if stop_loss:
                stop_side = 'sell' if side == 'buy' else 'buy'
                stop_order = self.api.submit_order(
                    symbol=symbol,
                    qty=size,
                    side=stop_side,
                    type='stop',
                    stop_price=stop_loss,
                    time_in_force='day'
                )
                logger.info(f"Placed stop loss at {stop_loss}")
                order.stop_loss = stop_order
            
            return {
                'id': order.id,
                'symbol': order.symbol,
                'qty': order.qty,
                'side': order.side,
                'type': order.type,
                'status': order.status
            }
            
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            return None
    
    def get_bars(self, symbol: str, timeframe: str = '1Min', limit: int = 100) -> Optional[list]:
        """Get historical bars"""
        try:
            bars = self.api.get_bars(
                symbol,
                timeframe,
                limit=limit
            )
            return [{
                'timestamp': bar.t,
                'open': float(bar.o),
                'high': float(bar.h),
                'low': float(bar.l),
                'close': float(bar.c),
                'volume': int(bar.v)
            } for bar in bars]
        except Exception as e:
            logger.error(f"Failed to get bars: {e}")
            return None
    
    def close_position(self, symbol: str) -> bool:
        """Close all positions for a symbol"""
        try:
            position = self.api.get_position(symbol)
            if position.qty > 0:
                self.api.submit_order(
                    symbol=symbol,
                    qty=position.qty,
                    side='sell',
                    type='market',
                    time_in_force='day'
                )
            elif position.qty < 0:
                self.api.submit_order(
                    symbol=symbol,
                    qty=abs(position.qty),
                    side='buy',
                    type='market',
                    time_in_force='day'
                )
            logger.info(f"Closed position for {symbol}")
            return True
        except Exception as e:
            logger.error(f"Failed to close position: {e}")
            return False
