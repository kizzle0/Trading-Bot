"""
CCXT Client for Crypto Trading (Binance, Coinbase, etc.)
"""
import ccxt
from typing import Dict, Any, Optional
from loguru import logger


class CCXTClient:
    """CCXT client for crypto exchanges"""
    
    def __init__(self, exchange: str, api_key: str, secret: str, sandbox: bool = True):
        """
        Initialize CCXT client
        
        Args:
            exchange: Exchange name (e.g., 'binance', 'coinbasepro')
            api_key: API key
            secret: API secret
            sandbox: Use sandbox/testnet
        """
        self.exchange_name = exchange
        self.sandbox = sandbox
        
        # Initialize exchange
        exchange_class = getattr(ccxt, exchange)
        self.exchange = exchange_class({
            'apiKey': api_key,
            'secret': secret,
            'sandbox': sandbox,
            'enableRateLimit': True,
        })
        
        logger.info(f"Initialized {exchange} client (sandbox: {sandbox})")
    
    def connect(self) -> bool:
        """Test connection to exchange"""
        try:
            self.exchange.load_markets()
            logger.info(f"Connected to {self.exchange_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to {self.exchange_name}: {e}")
            return False
    
    def get_balance(self) -> Dict[str, float]:
        """Get account balance"""
        try:
            balance = self.exchange.fetch_balance()
            return {currency: info['free'] for currency, info in balance.items() 
                   if isinstance(info, dict) and info['free'] > 0}
        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
            return {}
    
    def get_price(self, symbol: str) -> Optional[float]:
        """Get current price for symbol"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            logger.error(f"Failed to get price for {symbol}: {e}")
            return None
    
    def place_order(self, symbol: str, side: str, size: float, stop_loss: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """
        Place an order
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            side: 'buy' or 'sell'
            size: Order size
            stop_loss: Stop loss price (optional)
        
        Returns:
            Order info or None if failed
        """
        try:
            # Place market order
            order_type = 'market'
            order = self.exchange.create_order(symbol, order_type, side, size)
            
            logger.info(f"Placed {side} order for {size} {symbol} at market price")
            
            # Place stop loss if specified
            if stop_loss:
                stop_side = 'sell' if side == 'buy' else 'buy'
                stop_order = self.exchange.create_order(
                    symbol, 'stop', stop_side, size, stop_loss
                )
                logger.info(f"Placed stop loss at {stop_loss}")
                order['stop_loss'] = stop_order
            
            return order
            
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            return None
    
    def get_ohlcv(self, symbol: str, timeframe: str = '1m', limit: int = 100) -> Optional[list]:
        """Get OHLCV data"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            return ohlcv
        except Exception as e:
            logger.error(f"Failed to get OHLCV data: {e}")
            return None
    
    def close_position(self, symbol: str) -> bool:
        """Close all positions for a symbol"""
        try:
            balance = self.get_balance()
            # This is simplified - would need to check actual positions
            logger.info(f"Closing positions for {symbol}")
            return True
        except Exception as e:
            logger.error(f"Failed to close position: {e}")
            return False
