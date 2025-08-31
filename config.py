from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    # Broker selection
    BROKER: str = os.getenv("BROKER", "oanda")  # ccxt, oanda, alpaca
    
    # OANDA settings
    OANDA_API_URL: str = os.getenv("OANDA_API_URL", "https://api-fxpractice.oanda.com")
    OANDA_STREAM_URL: str = os.getenv("OANDA_STREAM_URL", "https://stream-fxpractice.oanda.com")
    OANDA_ACCESS_TOKEN: str = os.getenv("OANDA_ACCESS_TOKEN", "")
    OANDA_ACCOUNT_ID: str = os.getenv("OANDA_ACCOUNT_ID", "")
    OANDA_ENVIRONMENT: str = os.getenv("OANDA_ENVIRONMENT", "practice")
    
    # CCXT settings
    CCXT_EXCHANGE: str = os.getenv("CCXT_EXCHANGE", "binance")
    CCXT_API_KEY: str = os.getenv("CCXT_API_KEY", "")
    CCXT_SECRET: str = os.getenv("CCXT_SECRET", "")
    CCXT_SANDBOX: bool = os.getenv("CCXT_SANDBOX", "true").lower() == "true"
    
    # Alpaca settings
    ALPACA_API_KEY: str = os.getenv("ALPACA_API_KEY", "")
    ALPACA_SECRET_KEY: str = os.getenv("ALPACA_SECRET_KEY", "")
    ALPACA_BASE_URL: str = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
    ALPACA_PAPER: bool = os.getenv("ALPACA_PAPER", "true").lower() == "true"
    
    # Trading settings
    INSTRUMENT: str = os.getenv("INSTRUMENT", "EUR_USD")
    GRANULARITY: str = os.getenv("GRANULARITY", "M1")
    RISK_PER_TRADE: float = float(os.getenv("RISK_PER_TRADE", "0.005"))
    MAX_DAILY_DRAWDOWN: float = float(os.getenv("MAX_DAILY_DRAWDOWN", "0.02"))
    UNITS_CAP: int = int(os.getenv("UNITS_CAP", "20000"))
    
    # Strategy parameters
    SLOW_SMA: int = int(os.getenv("SLOW_SMA", "50"))
    FAST_SMA: int = int(os.getenv("FAST_SMA", "20"))
    ATR_WINDOW: int = int(os.getenv("ATR_WINDOW", "14"))
    ATR_MULTIPLIER: float = float(os.getenv("ATR_MULTIPLIER", "2.0"))

settings = Settings()
