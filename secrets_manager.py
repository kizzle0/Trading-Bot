"""
Secrets Manager for Streamlit App
Handles both local .env files and Streamlit secrets for deployed apps
"""
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

def get_secret(key: str, default: str = "") -> str:
    """
    Get secret from either Streamlit secrets or .env file
    Priority: Streamlit secrets > .env file > default
    """
    try:
        import streamlit as st
        # Try Streamlit secrets first (for deployed apps)
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except:
        pass
    
    # Fallback to .env file (for local development)
    load_dotenv()
    return os.getenv(key, default)

def get_all_secrets() -> Dict[str, str]:
    """Get all secrets as a dictionary"""
    secrets = {}
    
    # List of all secret keys we need
    secret_keys = [
        'BROKER',
        'OANDA_ACCESS_TOKEN', 'OANDA_ACCOUNT_ID', 'OANDA_ENVIRONMENT',
        'CCXT_EXCHANGE', 'CCXT_API_KEY', 'CCXT_SECRET', 'CCXT_SANDBOX',
        'ALPACA_API_KEY', 'ALPACA_SECRET_KEY', 'ALPACA_BASE_URL', 'ALPACA_PAPER',
        'INSTRUMENT', 'GRANULARITY', 'RISK_PER_TRADE', 'MAX_DAILY_DRAWDOWN', 'UNITS_CAP',
        'SLOW_SMA', 'FAST_SMA', 'ATR_WINDOW', 'ATR_MULTIPLIER'
    ]
    
    for key in secret_keys:
        secrets[key] = get_secret(key)
    
    return secrets

def create_secrets_template() -> str:
    """Create a template for Streamlit secrets"""
    return """
# Streamlit Secrets Template
# Add this to your Streamlit Cloud app's secrets management

[broker]
BROKER = "alpaca"  # or "oanda", "ccxt"

[oanda]
OANDA_ACCESS_TOKEN = "your_oanda_access_token_here"
OANDA_ACCOUNT_ID = "your_oanda_account_id_here"
OANDA_ENVIRONMENT = "practice"  # or "live"

[ccxt]
CCXT_EXCHANGE = "binance"
CCXT_API_KEY = "your_ccxt_api_key_here"
CCXT_SECRET = "your_ccxt_secret_here"
CCXT_SANDBOX = true

[alpaca]
ALPACA_API_KEY = "your_alpaca_api_key_here"
ALPACA_SECRET_KEY = "your_alpaca_secret_key_here"
ALPACA_BASE_URL = "https://paper-api.alpaca.markets"
ALPACA_PAPER = true

[trading]
INSTRUMENT = "EUR_USD"
GRANULARITY = "M1"
RISK_PER_TRADE = 0.005
MAX_DAILY_DRAWDOWN = 0.02
UNITS_CAP = 20000

[strategy]
SLOW_SMA = 50
FAST_SMA = 20
ATR_WINDOW = 14
ATR_MULTIPLIER = 2.0
"""
