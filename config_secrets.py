"""
Configuration using Streamlit secrets for deployed apps
"""
from pydantic import BaseModel
from secrets_manager import get_secret

class Settings(BaseModel):
    # Broker selection
    BROKER: str = get_secret("BROKER", "oanda")
    
    # OANDA settings
    OANDA_API_URL: str = get_secret("OANDA_API_URL", "https://api-fxpractice.oanda.com")
    OANDA_STREAM_URL: str = get_secret("OANDA_STREAM_URL", "https://stream-fxpractice.oanda.com")
    OANDA_ACCESS_TOKEN: str = get_secret("OANDA_ACCESS_TOKEN", "")
    OANDA_ACCOUNT_ID: str = get_secret("OANDA_ACCOUNT_ID", "")
    OANDA_ENVIRONMENT: str = get_secret("OANDA_ENVIRONMENT", "practice")
    
    # CCXT settings
    CCXT_EXCHANGE: str = get_secret("CCXT_EXCHANGE", "binance")
    CCXT_API_KEY: str = get_secret("CCXT_API_KEY", "")
    CCXT_SECRET: str = get_secret("CCXT_SECRET", "")
    CCXT_SANDBOX: bool = get_secret("CCXT_SANDBOX", "true").lower() == "true"
    
    # Alpaca settings
    ALPACA_API_KEY: str = get_secret("ALPACA_API_KEY", "")
    ALPACA_SECRET_KEY: str = get_secret("ALPACA_SECRET_KEY", "")
    ALPACA_BASE_URL: str = get_secret("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
    ALPACA_PAPER: bool = get_secret("ALPACA_PAPER", "true").lower() == "true"
    
    # Trading settings
    INSTRUMENT: str = get_secret("INSTRUMENT", "EUR_USD")
    GRANULARITY: str = get_secret("GRANULARITY", "M1")
    RISK_PER_TRADE: float = float(get_secret("RISK_PER_TRADE", "0.005"))
    MAX_DAILY_DRAWDOWN: float = float(get_secret("MAX_DAILY_DRAWDOWN", "0.02"))
    UNITS_CAP: int = int(get_secret("UNITS_CAP", "20000"))
    
    # Strategy parameters
    SLOW_SMA: int = int(get_secret("SLOW_SMA", "50"))
    FAST_SMA: int = int(get_secret("FAST_SMA", "20"))
    ATR_WINDOW: int = int(get_secret("ATR_WINDOW", "14"))
    ATR_MULTIPLIER: float = float(get_secret("ATR_MULTIPLIER", "2.0"))

settings = Settings()
