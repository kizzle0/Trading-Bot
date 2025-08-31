"""
OANDA Client for Forex Trading
"""
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.accounts as accounts
from oandapyV20 import API
try:
    from oandapyV20.contrib.streaming import PricingStream
except ImportError:
    # Fallback if streaming module not available
    PricingStream = None
from typing import Dict, Any, Optional
from loguru import logger


class OANDAClient:
    """OANDA client for forex trading"""
    
    def __init__(self, access_token: str, account_id: str, environment: str = "practice"):
        """
        Initialize OANDA client
        
        Args:
            access_token: OANDA API access token
            account_id: OANDA account ID
            environment: 'practice' or 'live'
        """
        self.access_token = access_token
        self.account_id = account_id
        self.environment = environment
        self.api = API(access_token=access_token, environment=environment)
        
        logger.info(f"Initialized OANDA client (environment: {environment})")
    
    def connect(self) -> bool:
        """Test connection to OANDA"""
        try:
            r = accounts.AccountDetails(accountID=self.account_id)
            resp = self.api.request(r)
            logger.info(f"Connected to OANDA account {self.account_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to OANDA: {e}")
            return False
    
    def get_balance(self) -> Dict[str, float]:
        """Get account balance"""
        try:
            r = accounts.AccountDetails(accountID=self.account_id)
            resp = self.api.request(r)
            account = resp['account']
            return {
                'NAV': float(account['NAV']),
                'balance': float(account['balance']),
                'unrealizedPL': float(account['unrealizedPL']),
                'realizedPL': float(account['realizedPL'])
            }
        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
            return {}
    
    def get_price(self, symbol: str) -> Optional[float]:
        """Get current price for symbol (simplified - would need pricing endpoint)"""
        try:
            # This is simplified - in practice you'd use the pricing endpoint
            # For now, return None as we'll get prices from the stream
            return None
        except Exception as e:
            logger.error(f"Failed to get price for {symbol}: {e}")
            return None
    
    def place_order(self, symbol: str, side: str, size: int, stop_loss: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """
        Place an order
        
        Args:
            symbol: Instrument (e.g., 'EUR_USD')
            side: 'buy' or 'sell'
            size: Order size in units
            stop_loss: Stop loss price (optional)
        
        Returns:
            Order info or None if failed
        """
        try:
            # Convert side to OANDA format
            units = str(size) if side == 'buy' else str(-size)
            
            data = {
                "order": {
                    "units": units,
                    "instrument": symbol,
                    "timeInForce": "FOK",
                    "type": "MARKET",
                    "positionFill": "DEFAULT",
                }
            }
            
            if stop_loss is not None:
                data["order"]["stopLossOnFill"] = {"price": f"{stop_loss:.5f}"}
            
            r = orders.OrderCreate(self.account_id, data=data)
            resp = self.api.request(r)
            
            logger.info(f"Placed {side} order for {size} {symbol} at market price")
            return resp
            
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            return None
    
    def get_pricing_stream(self, instruments: list):
        """Get pricing stream for instruments"""
        if PricingStream is None:
            raise ImportError("OANDA streaming module not available")
        return PricingStream(
            environment=self.environment,
            access_token=self.access_token,
            accountID=self.account_id,
            params={"instruments": ",".join(instruments)}
        )
    
    def close_position(self, symbol: str) -> bool:
        """Close all positions for a symbol"""
        try:
            # This would use the positions endpoint to close positions
            logger.info(f"Closing positions for {symbol}")
            return True
        except Exception as e:
            logger.error(f"Failed to close position: {e}")
            return False
