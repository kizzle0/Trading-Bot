#!/usr/bin/env python3
"""
Streamlit Dashboard for Universal Trading Bot
"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import threading
import queue
import json
import os
from typing import Dict, Any, Optional

# Import our trading bot modules
try:
    # Try secrets-based config first (for Streamlit Cloud)
    from config_secrets import settings
    print("Using secrets-based configuration")
except ImportError:
    # Fallback to .env-based config (for local development)
    from config import settings
    print("Using .env-based configuration")

from importlib import reload
import config
from strategies.sma_atr import SMAATRStrategy
from risk.atr_sizing import RiskParams, position_size_by_risk, get_pip_value_per_unit
from backtest.backtest import run_backtest, plot_backtest

# Import broker clients
from brokers.ccxt_client import CCXTClient
from brokers.oanda_client import OANDAClient
from brokers.alpaca_client import AlpacaClient

# Configure Streamlit page
st.set_page_config(
    page_title="Universal Trading Bot Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #8B5CF6;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #8B5CF6;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'broker_client' not in st.session_state:
    st.session_state.broker_client = None
if 'trading_active' not in st.session_state:
    st.session_state.trading_active = False
if 'trading_thread' not in st.session_state:
    st.session_state.trading_thread = None
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'positions' not in st.session_state:
    st.session_state.positions = {}
if 'equity_history' not in st.session_state:
    st.session_state.equity_history = []
if 'trading_mode' not in st.session_state:
    st.session_state.trading_mode = "paper"  # paper or live

def reload_settings():
    """Reload settings from .env file"""
    try:
        reload(config)
        return config.settings
    except Exception as e:
        st.error(f"Failed to reload settings: {e}")
        return settings

def update_env_file(trading_mode: str):
    """Update .env file with trading mode settings"""
    env_file = ".env"
    
    # Read current .env file
    env_vars = {}
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    
    # Update trading mode settings
    if trading_mode == "live":
        env_vars['ALPACA_PAPER'] = 'false'
        env_vars['ALPACA_BASE_URL'] = 'https://api.alpaca.markets'
        env_vars['OANDA_ENVIRONMENT'] = 'live'
        env_vars['OANDA_API_URL'] = 'https://api-fxtrade.oanda.com'
        env_vars['OANDA_STREAM_URL'] = 'https://stream-fxtrade.oanda.com'
        env_vars['CCXT_SANDBOX'] = 'false'
    else:  # paper
        env_vars['ALPACA_PAPER'] = 'true'
        env_vars['ALPACA_BASE_URL'] = 'https://paper-api.alpaca.markets'
        env_vars['OANDA_ENVIRONMENT'] = 'practice'
        env_vars['OANDA_API_URL'] = 'https://api-fxpractice.oanda.com'
        env_vars['OANDA_STREAM_URL'] = 'https://stream-fxpractice.oanda.com'
        env_vars['CCXT_SANDBOX'] = 'true'
    
    # Write updated .env file
    with open(env_file, 'w') as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    
    # Reload settings
    from importlib import reload
    import config
    reload(config)
    global settings
    settings = config.settings

def get_broker_client(broker: str, trading_mode: str = None):
    """Get broker client instance"""
    try:
        # Use session state trading mode if not provided
        if trading_mode is None:
            trading_mode = st.session_state.trading_mode
            
        if broker == 'ccxt':
            # Determine sandbox mode based on trading mode
            sandbox = trading_mode == "paper"
            return CCXTClient(
                exchange=settings.CCXT_EXCHANGE,
                api_key=settings.CCXT_API_KEY,
                secret=settings.CCXT_SECRET,
                sandbox=sandbox
            )
        elif broker == 'oanda':
            # Determine environment based on trading mode
            environment = "practice" if trading_mode == "paper" else "live"
            return OANDAClient(
                access_token=settings.OANDA_ACCESS_TOKEN,
                account_id=settings.OANDA_ACCOUNT_ID,
                environment=environment
            )
        elif broker == 'alpaca':
            # Determine paper mode and base URL based on trading mode
            paper = trading_mode == "paper"
            base_url = "https://paper-api.alpaca.markets" if paper else "https://api.alpaca.markets"
            return AlpacaClient(
                api_key=settings.ALPACA_API_KEY,
                secret_key=settings.ALPACA_SECRET_KEY,
                base_url=base_url,
                paper=paper
            )
    except Exception as e:
        st.error(f"Failed to initialize {broker} client: {e}")
        return None

def add_log(message: str, level: str = "INFO"):
    """Add log message to session state"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {
        "timestamp": timestamp,
        "level": level,
        "message": message
    }
    st.session_state.logs.insert(0, log_entry)
    # Keep only last 100 logs
    if len(st.session_state.logs) > 100:
        st.session_state.logs = st.session_state.logs[:100]

def home_tab():
    """Home tab - Broker selection and account info"""
    st.markdown('<div class="main-header">🏠 Home Dashboard</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("🔧 Broker Configuration")
        
        # Broker selection
        broker_options = {
            "OANDA (Forex)": "oanda",
            "CCXT (Crypto)": "ccxt", 
            "Alpaca (Stocks)": "alpaca"
        }
        
        selected_broker = st.selectbox(
            "Select Broker:",
            options=list(broker_options.keys()),
            index=0
        )
        
        broker_key = broker_options[selected_broker]
        
        # Show broker-specific configuration
        if broker_key == "oanda":
            st.subheader("🌍 Forex Configuration")
            forex_pairs = [
                "EUR_USD", "GBP_USD", "USD_JPY", "USD_CHF", "AUD_USD", "USD_CAD",
                "NZD_USD", "EUR_GBP", "EUR_JPY", "GBP_JPY", "CHF_JPY", "AUD_JPY",
                "CAD_JPY", "NZD_JPY", "EUR_CHF", "EUR_AUD", "EUR_CAD", "EUR_NZD",
                "GBP_CHF", "GBP_AUD", "GBP_CAD", "GBP_NZD", "AUD_CHF", "AUD_CAD",
                "AUD_NZD", "CAD_CHF", "NZD_CHF", "NZD_CAD"
            ]
            
            selected_pair = st.selectbox(
                "Select Currency Pair:",
                options=forex_pairs,
                index=0
            )
            
            st.info(f"Selected: {selected_pair}")
            
        elif broker_key == "ccxt":
            st.subheader("₿ Crypto Configuration")
            crypto_pairs = [
                "BTC/USDT", "ETH/USDT", "BNB/USDT", "ADA/USDT", "DOT/USDT",
                "LINK/USDT", "LTC/USDT", "BCH/USDT", "XLM/USDT", "EOS/USDT",
                "TRX/USDT", "XRP/USDT", "DOGE/USDT", "SHIB/USDT", "MATIC/USDT",
                "AVAX/USDT", "SOL/USDT", "ATOM/USDT", "FTM/USDT", "ALGO/USDT"
            ]
            
            selected_pair = st.selectbox(
                "Select Crypto Pair:",
                options=crypto_pairs,
                index=0
            )
            
            st.info(f"Selected: {selected_pair}")
            
        elif broker_key == "alpaca":
            st.subheader("📈 Stock Configuration")
            stock_symbols = [
                "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX",
                "AMD", "INTC", "CRM", "ADBE", "PYPL", "UBER", "LYFT", "ZOOM",
                "SPOT", "SQ", "ROKU", "PINS", "SNAP", "TWTR", "SHOP", "ZM"
            ]
            
            selected_symbol = st.selectbox(
                "Select Stock Symbol:",
                options=stock_symbols,
                index=0
            )
            
            st.info(f"Selected: {selected_symbol}")
        
        # API Configuration Status
        st.subheader("🔑 API Configuration")
        
        # Check credentials for the selected broker
        if broker_key == "oanda":
            if settings.OANDA_ACCESS_TOKEN and settings.OANDA_ACCESS_TOKEN != "your_oanda_access_token_here" and settings.OANDA_ACCOUNT_ID and settings.OANDA_ACCOUNT_ID != "your_oanda_account_id_here":
                st.success("✅ OANDA credentials configured")
            else:
                st.error("❌ OANDA credentials missing")
                with st.expander("📋 OANDA Setup Instructions"):
                    st.markdown("""
                    **Quick Setup:**
                    1. Go to [OANDA Demo Account](https://www.oanda.com/demo-account/)
                    2. Sign up and get your API token
                    3. Add to `.env` file:
                       ```
                       OANDA_ACCESS_TOKEN=your_token
                       OANDA_ACCOUNT_ID=your_account_id
                       ```
                    4. Restart the dashboard
                    """)
                
        elif broker_key == "ccxt":
            if settings.CCXT_API_KEY and settings.CCXT_API_KEY != "your_ccxt_api_key_here" and settings.CCXT_SECRET and settings.CCXT_SECRET != "your_ccxt_secret_here":
                st.success("✅ CCXT credentials configured")
            else:
                st.error("❌ CCXT credentials missing")
                with st.expander("📋 CCXT Setup Instructions"):
                    st.markdown("""
                    **Quick Setup:**
                    1. Go to [Binance](https://www.binance.com/) (or your preferred exchange)
                    2. Create account and enable API access
                    3. Generate API keys (spot trading only)
                    4. Add to `.env` file:
                       ```
                       CCXT_EXCHANGE=binance
                       CCXT_API_KEY=your_key
                       CCXT_SECRET=your_secret
                       ```
                    5. Restart the dashboard
                    """)
                
        elif broker_key == "alpaca":
            if settings.ALPACA_API_KEY and settings.ALPACA_API_KEY != "your_alpaca_api_key_here" and settings.ALPACA_SECRET_KEY and settings.ALPACA_SECRET_KEY != "your_alpaca_secret_key_here":
                st.success("✅ Alpaca credentials configured")
            else:
                st.error("❌ Alpaca credentials missing")
                with st.expander("📋 Alpaca Setup Instructions"):
                    st.markdown("""
                    **Quick Setup:**
                    1. Go to [Alpaca Markets](https://alpaca.markets/)
                    2. Sign up for paper trading account
                    3. Generate API keys
                    4. Add to `.env` file:
                       ```
                       ALPACA_API_KEY=your_key
                       ALPACA_SECRET_KEY=your_secret
                       ```
                    5. Restart the dashboard
                    """)
        
        # Quick setup link
        st.markdown("---")
        st.markdown("📖 **Need help?** Check the [Broker Setup Guide](BROKER_SETUP.md) for detailed instructions.")
        
        # Debug information
        st.markdown("---")
        st.markdown("### 🔍 **Debug Information**")
        with st.expander("Show Configuration Status"):
            st.write(f"**Configuration Source:** {'Secrets' if 'config_secrets' in str(type(settings)) else 'Environment'}")
            st.write(f"**Broker:** {settings.BROKER}")
            st.write(f"**Alpaca API Key:** {settings.ALPACA_API_KEY[:10] + '...' if settings.ALPACA_API_KEY else 'Not set'}")
            st.write(f"**Alpaca Secret Key:** {settings.ALPACA_SECRET_KEY[:10] + '...' if settings.ALPACA_SECRET_KEY else 'Not set'}")
            st.write(f"**OANDA Token:** {settings.OANDA_ACCESS_TOKEN[:10] + '...' if settings.OANDA_ACCESS_TOKEN else 'Not set'}")
            st.write(f"**CCXT API Key:** {settings.CCXT_API_KEY[:10] + '...' if settings.CCXT_API_KEY else 'Not set'}")
        
        # Streamlit Cloud setup info
        st.markdown("---")
        st.markdown("### 🌐 **For Streamlit Cloud Users**")
        st.info("""
        **If you're using the published Streamlit app:**
        1. Go to your app's settings in Streamlit Cloud
        2. Add your API credentials to the **Secrets** section
        3. Use the configuration from [Streamlit Cloud Setup Guide](STREAMLIT_CLOUD_SETUP.md)
        4. **Wait 1-2 minutes** for changes to propagate
        5. **Refresh the page** to see updated credentials
        """)
        
        # Connect button
        if st.button("🔌 Connect to Broker", type="primary"):
            with st.spinner(f"Connecting to {selected_broker}..."):
                client = get_broker_client(broker_key, st.session_state.trading_mode)
                if client and client.connect():
                    st.session_state.broker_client = client
                    st.session_state.current_broker = broker_key
                    if broker_key == "oanda":
                        st.session_state.selected_instrument = selected_pair
                    elif broker_key == "ccxt":
                        st.session_state.selected_instrument = selected_pair
                    elif broker_key == "alpaca":
                        st.session_state.selected_instrument = selected_symbol
                    add_log(f"Connected to {selected_broker} ({st.session_state.trading_mode} mode)")
                    st.success(f"✅ Connected to {selected_broker} ({st.session_state.trading_mode} mode)")
                else:
                    st.error(f"❌ Failed to connect to {selected_broker}")
                    add_log(f"Failed to connect to {selected_broker}", "ERROR")
    
    with col2:
        st.subheader("💰 Account Information")
        
        if st.session_state.broker_client:
            try:
                balance = st.session_state.broker_client.get_balance()
                
                if balance:
                    # Display balance information
                    if st.session_state.current_broker == 'oanda':
                        col_a, col_b, col_c, col_d = st.columns(4)
                        with col_a:
                            st.metric("NAV", f"${balance.get('NAV', 0):,.2f}")
                        with col_b:
                            st.metric("Balance", f"${balance.get('balance', 0):,.2f}")
                        with col_c:
                            st.metric("Unrealized P&L", f"${balance.get('unrealizedPL', 0):,.2f}")
                        with col_d:
                            st.metric("Realized P&L", f"${balance.get('realizedPL', 0):,.2f}")
                    
                    elif st.session_state.current_broker == 'alpaca':
                        col_a, col_b, col_c, col_d = st.columns(4)
                        with col_a:
                            st.metric("Equity", f"${balance.get('equity', 0):,.2f}")
                        with col_b:
                            st.metric("Buying Power", f"${balance.get('buying_power', 0):,.2f}")
                        with col_c:
                            st.metric("Cash", f"${balance.get('cash', 0):,.2f}")
                        with col_d:
                            st.metric("Portfolio Value", f"${balance.get('portfolio_value', 0):,.2f}")
                    
                    else:  # ccxt
                        st.write("**Available Balances:**")
                        for currency, amount in balance.items():
                            if amount > 0:
                                st.write(f"• {currency}: {amount:.8f}")
                else:
                    st.warning("No balance information available")
                    
            except Exception as e:
                st.error(f"Error fetching balance: {e}")
                add_log(f"Error fetching balance: {e}", "ERROR")
        else:
            st.info("👆 Please connect to a broker first")

def backtest_tab():
    """Backtest tab - Run backtests with custom parameters"""
    st.markdown('<div class="main-header">📊 Backtesting</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("⚙️ Backtest Parameters")
        
        # Broker selection for backtest
        st.subheader("🏦 Data Source")
        broker_options = {
            "Yahoo Finance (Default)": "yahoo",
            "OANDA (Forex)": "oanda",
            "CCXT (Crypto)": "ccxt", 
            "Alpaca (Stocks)": "alpaca"
        }
        
        selected_broker = st.selectbox(
            "Select Data Source:",
            options=list(broker_options.keys()),
            index=0
        )
        
        broker_key = broker_options[selected_broker]
        
        # Symbol selection based on broker
        st.subheader("📊 Symbol Selection")
        if broker_key == "oanda":
            forex_pairs = [
                "EUR_USD", "GBP_USD", "USD_JPY", "USD_CHF", "AUD_USD", "USD_CAD",
                "NZD_USD", "EUR_GBP", "EUR_JPY", "GBP_JPY", "CHF_JPY", "AUD_JPY"
            ]
            symbol = st.selectbox("Select Currency Pair:", options=forex_pairs, index=0)
            st.info(f"Selected: {symbol}")
            
        elif broker_key == "ccxt":
            crypto_pairs = [
                "BTC/USDT", "ETH/USDT", "BNB/USDT", "ADA/USDT", "DOT/USDT",
                "LINK/USDT", "LTC/USDT", "BCH/USDT", "XLM/USDT", "EOS/USDT"
            ]
            symbol = st.selectbox("Select Crypto Pair:", options=crypto_pairs, index=0)
            st.info(f"Selected: {symbol}")
            
        elif broker_key == "alpaca":
            stock_symbols = [
                "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX",
                "AMD", "INTC", "CRM", "ADBE", "PYPL", "UBER", "LYFT", "ZOOM"
            ]
            symbol = st.selectbox("Select Stock Symbol:", options=stock_symbols, index=0)
            st.info(f"Selected: {symbol}")
            
        else:  # yahoo
            if 'selected_instrument' in st.session_state:
                default_symbol = st.session_state.selected_instrument
            else:
                default_symbol = "EURUSD=X"
                
            # Symbol input with suggestions based on broker
            if broker_key == "alpaca":
                symbol_options = ["AAPL", "MSFT", "TSLA", "GOOGL", "AMZN", "META", "NVDA", "NFLX", "CUSTOM"]
                symbol_choice = st.selectbox("Symbol:", options=symbol_options, help="Select a popular stock symbol")
                if symbol_choice == "CUSTOM":
                    symbol = st.text_input("Custom Symbol:", value="AAPL", help="Enter any stock symbol")
                else:
                    symbol = symbol_choice
            elif broker_key == "oanda":
                symbol_options = ["EUR_USD", "GBP_USD", "USD_JPY", "USD_CHF", "AUD_USD", "USD_CAD", "CUSTOM"]
                symbol_choice = st.selectbox("Symbol:", options=symbol_options, help="Select a popular forex pair")
                if symbol_choice == "CUSTOM":
                    symbol = st.text_input("Custom Symbol:", value="EUR_USD", help="Enter any forex pair (e.g., EUR_USD)")
                else:
                    symbol = symbol_choice
            elif broker_key == "ccxt":
                symbol_options = ["BTC-USD", "ETH-USD", "ADA-USD", "SOL-USD", "DOGE-USD", "MATIC-USD", "CUSTOM"]
                symbol_choice = st.selectbox("Symbol:", options=symbol_options, help="Select a popular crypto symbol")
                if symbol_choice == "CUSTOM":
                    symbol = st.text_input("Custom Symbol:", value="BTC-USD", help="Enter any crypto symbol (e.g., BTC-USD)")
                else:
                    symbol = symbol_choice
            else:  # yahoo
                symbol_options = ["AAPL", "MSFT", "BTC-USD", "ETH-USD", "EURUSD=X", "GBPUSD=X", "CUSTOM"]
                symbol_choice = st.selectbox("Symbol:", options=symbol_options, help="Select a popular symbol")
                if symbol_choice == "CUSTOM":
                    symbol = st.text_input("Custom Symbol:", value="AAPL", help="Enter any symbol")
                else:
                    symbol = symbol_choice
        
        # Period and interval
        col_a, col_b = st.columns(2)
        with col_a:
            period = st.selectbox("Period:", 
                                ["1mo", "3mo", "6mo", "1y", "2y", "5y"], 
                                index=3)
        with col_b:
            interval = st.selectbox("Interval:", 
                                  ["1m", "5m", "15m", "1h", "1d"], 
                                  index=4)
        
        # Strategy parameters
        st.subheader("📈 Strategy Settings")
        col_c, col_d = st.columns(2)
        with col_c:
            fast_sma = st.number_input("Fast SMA:", min_value=1, max_value=200, value=20)
        with col_d:
            slow_sma = st.number_input("Slow SMA:", min_value=1, max_value=200, value=50)
        
        col_e, col_f = st.columns(2)
        with col_e:
            atr_window = st.number_input("ATR Window:", min_value=1, max_value=50, value=14)
        with col_f:
            atr_mult = st.number_input("ATR Multiplier:", min_value=0.1, max_value=10.0, value=2.0, step=0.1)
        
        # Trading parameters
        st.subheader("💰 Trading Settings")
        col_g, col_h = st.columns(2)
        with col_g:
            cash = st.number_input("Starting Cash ($):", min_value=1000, max_value=1000000, value=10000)
        with col_h:
            commission = st.number_input("Commission (%):", min_value=0.0, max_value=1.0, value=0.0002, step=0.0001)
        
        # Run backtest button
        if st.button("🚀 Run Backtest", type="primary", use_container_width=True):
            with st.spinner(f"Running backtest with {selected_broker}..."):
                try:
                    result = run_backtest(
                        symbol=symbol,
                        broker=broker_key,
                        period=period,
                        interval=interval,
                        fast=fast_sma,
                        slow=slow_sma,
                        atr_window=atr_window,
                        atr_mult=atr_mult,
                        cash=cash,
                        commission=commission
                    )
                    
                    st.session_state.backtest_result = result
                    add_log(f"Backtest completed for {symbol}")
                    st.success("✅ Backtest completed!")
                    
                except Exception as e:
                    error_msg = str(e)
                    st.error(f"❌ Backtest failed: {error_msg}")
                    add_log(f"Backtest failed: {error_msg}", "ERROR")
                    
                    # Provide helpful suggestions
                    with st.expander("🔧 Troubleshooting Tips"):
                        st.markdown("""
                        **Common Solutions:**
                        
                        1. **Try a different symbol format:**
                           - **Forex**: `EURUSD=X`, `EUR_USD`, `GBPUSD=X`
                           - **Crypto**: `BTC-USD`, `ETH-USD`, `ADA-USD` (NOT BTC/USDT)
                           - **Stocks**: `AAPL`, `MSFT`, `TSLA`, `GOOGL`
                        
                        2. **Try a shorter time period:**
                           - Use `6mo` instead of `1y`
                           - Use `3mo` instead of `6mo`
                           - Use `1mo` for very recent data
                        
                        3. **Try a different interval:**
                           - Use `1d` instead of `1h`
                           - Use `1h` instead of `1m`
                           - Use `1w` for longer-term analysis
                        
                        4. **Check if the symbol exists:**
                           - Verify the symbol is correct
                           - Try a well-known symbol like `AAPL` or `BTC-USD`
                           - Check if the asset is still trading
                        
                        5. **Try a different broker:**
                           - **Yahoo Finance**: Works for most symbols
                           - **OANDA**: Best for forex (EUR_USD, GBP_USD)
                           - **CCXT**: Best for crypto (BTC-USD, ETH-USD)
                           - **Alpaca**: Best for stocks (AAPL, MSFT)
                        
                        6. **Popular working symbols:**
                           - **Stocks**: `AAPL`, `MSFT`, `TSLA`, `GOOGL`, `AMZN`
                           - **Crypto**: `BTC-USD`, `ETH-USD`, `ADA-USD`, `SOL-USD`
                           - **Forex**: `EURUSD=X`, `GBPUSD=X`, `USDJPY=X`
                        """)
    
    with col2:
        st.subheader("📈 Backtest Results")
        
        if 'backtest_result' in st.session_state:
            result = st.session_state.backtest_result
            stats = result['stats']
            data = result['data']
            
            # Key metrics
            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a:
                st.metric("Total Return", f"{stats['Return [%]']:.2f}%")
            with col_b:
                st.metric("Sharpe Ratio", f"{stats['Sharpe Ratio']:.2f}")
            with col_c:
                st.metric("Max Drawdown", f"{stats['Max. Drawdown [%]']:.2f}%")
            with col_d:
                st.metric("# Trades", f"{stats['# Trades']}")
            
            # Equity curve
            st.subheader("📊 Equity Curve")
            if hasattr(result['backtest'], '_equity_curve'):
                equity_curve = result['backtest']._equity_curve
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=equity_curve.index,
                    y=equity_curve.values,
                    mode='lines',
                    name='Equity',
                    line=dict(color='#8B5CF6', width=2)
                ))
                fig.update_layout(
                    title="Portfolio Equity Over Time",
                    xaxis_title="Date",
                    yaxis_title="Equity ($)",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Detailed stats
            st.subheader("📋 Detailed Statistics")
            stats_df = pd.DataFrame([stats]).T
            stats_df.columns = ['Value']
            st.dataframe(stats_df, use_container_width=True)
            
            # Trades table
            if hasattr(result['backtest'], '_trades') and len(result['backtest']._trades) > 0:
                st.subheader("💼 Trade History")
                trades_df = result['backtest']._trades
                st.dataframe(trades_df, use_container_width=True)
        else:
            st.info("👆 Run a backtest to see results here")

def live_trading_tab():
    """Live Trading tab - Start/stop live trading"""
    st.markdown('<div class="main-header">⚡ Live Trading</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("🎛️ Trading Controls")
        
        if not st.session_state.broker_client:
            st.warning("⚠️ Please connect to a broker first in the Home tab")
            return
        
        # Trading parameters
        st.subheader("⚙️ Risk Parameters")
        risk_per_trade = st.number_input(
            "Risk per Trade (%):", 
            min_value=0.1, max_value=10.0, 
            value=float(settings.RISK_PER_TRADE * 100), 
            step=0.1
        ) / 100
        
        max_daily_dd = st.number_input(
            "Max Daily Drawdown (%):", 
            min_value=1.0, max_value=50.0, 
            value=float(settings.MAX_DAILY_DRAWDOWN * 100), 
            step=1.0
        ) / 100
        
        # Strategy parameters
        st.subheader("📈 Strategy Parameters")
        col_a, col_b = st.columns(2)
        with col_a:
            fast_sma = st.number_input("Fast SMA:", min_value=1, max_value=200, value=settings.FAST_SMA)
        with col_b:
            slow_sma = st.number_input("Slow SMA:", min_value=1, max_value=200, value=settings.SLOW_SMA)
        
        col_c, col_d = st.columns(2)
        with col_c:
            atr_window = st.number_input("ATR Window:", min_value=1, max_value=50, value=settings.ATR_WINDOW)
        with col_d:
            atr_mult = st.number_input("ATR Multiplier:", min_value=0.1, max_value=10.0, value=settings.ATR_MULTIPLIER, step=0.1)
        
        # Trading controls
        st.subheader("🎮 Trading Controls")
        
        if not st.session_state.trading_active:
            if st.button("▶️ Start Live Trading", type="primary", use_container_width=True):
                st.session_state.trading_active = True
                add_log("Live trading started")
                st.success("✅ Live trading started!")
                st.rerun()
        else:
            if st.button("⏹️ Stop Live Trading", type="secondary", use_container_width=True):
                st.session_state.trading_active = False
                add_log("Live trading stopped")
                st.success("✅ Live trading stopped!")
                st.rerun()
    
    with col2:
        st.subheader("📊 Live Trading Status")
        
        if st.session_state.trading_active:
            st.success("🟢 Trading is ACTIVE")
            
            # Simulate live data updates
            if st.button("🔄 Refresh Data"):
                st.rerun()
            
            # Current positions (simulated)
            st.subheader("💼 Current Positions")
            if st.session_state.positions:
                positions_df = pd.DataFrame(st.session_state.positions).T
                st.dataframe(positions_df, use_container_width=True)
            else:
                st.info("No open positions")
            
            # Equity history
            st.subheader("📈 Equity History")
            if st.session_state.equity_history:
                equity_df = pd.DataFrame(st.session_state.equity_history)
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=equity_df['timestamp'],
                    y=equity_df['equity'],
                    mode='lines+markers',
                    name='Equity',
                    line=dict(color='#8B5CF6', width=2)
                ))
                fig.update_layout(
                    title="Live Equity Curve",
                    xaxis_title="Time",
                    yaxis_title="Equity ($)",
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No equity history yet")
        else:
            st.info("🔴 Trading is INACTIVE")
            st.markdown("""
            **To start live trading:**
            1. Ensure you're connected to a broker
            2. Set your risk parameters
            3. Click "Start Live Trading"
            """)

def logs_tab():
    """Logs tab - Display trading logs and events"""
    st.markdown('<div class="main-header">📝 Trading Logs</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("📋 Recent Activity")
        
        if st.session_state.logs:
            # Create logs dataframe
            logs_df = pd.DataFrame(st.session_state.logs)
            
            # Color code by level
            def color_log_level(val):
                if val == "ERROR":
                    return "background-color: #f8d7da; color: #721c24"
                elif val == "WARNING":
                    return "background-color: #fff3cd; color: #856404"
                elif val == "INFO":
                    return "background-color: #d1ecf1; color: #0c5460"
                return ""
            
            styled_logs = logs_df.style.applymap(color_log_level, subset=['level'])
            st.dataframe(styled_logs, use_container_width=True, hide_index=True)
        else:
            st.info("No logs yet. Start trading to see activity here.")
    
    with col2:
        st.subheader("🔧 Log Controls")
        
        if st.button("🗑️ Clear Logs"):
            st.session_state.logs = []
            st.success("Logs cleared!")
            st.rerun()
        
        if st.button("📥 Export Logs"):
            if st.session_state.logs:
                logs_df = pd.DataFrame(st.session_state.logs)
                csv = logs_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"trading_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No logs to export")
        
        # Log level filter
        log_levels = st.multiselect(
            "Filter by Level:",
            options=["INFO", "WARNING", "ERROR"],
            default=["INFO", "WARNING", "ERROR"]
        )
        
        if log_levels and st.session_state.logs:
            filtered_logs = [log for log in st.session_state.logs if log['level'] in log_levels]
            st.write(f"Showing {len(filtered_logs)} of {len(st.session_state.logs)} logs")

def main():
    """Main dashboard function"""
    # Reload settings to get latest .env values
    global settings
    settings = reload_settings()
    
    # Header with trading mode indicator
    mode_emoji = "📝" if st.session_state.trading_mode == "paper" else "💰"
    mode_text = "Paper Trading" if st.session_state.trading_mode == "paper" else "Live Trading"
    mode_color = "#8B5CF6" if st.session_state.trading_mode == "paper" else "#DC2626"
    
    st.markdown(f'''
    <div class="main-header">
        🚀 Universal Trading Bot Dashboard
        <br>
        <span style="font-size: 1.2rem; color: {mode_color};">
            {mode_emoji} {mode_text}
        </span>
    </div>
    ''', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/200x100/1f77b4/ffffff?text=Trading+Bot", width=200)
        st.markdown("---")
        
        # Trading Mode Toggle
        st.subheader("🎯 Trading Mode")
        current_mode = st.session_state.trading_mode
        
        if current_mode == "paper":
            st.success("📝 Paper Trading")
            if st.button("🔄 Switch to Live Trading", type="secondary", use_container_width=True):
                st.session_state.trading_mode = "live"
                update_env_file("live")
                st.session_state.broker_client = None  # Disconnect to force reconnection
                add_log("Switched to LIVE trading mode")
                st.success("✅ Switched to Live Trading!")
                st.rerun()
        else:
            st.error("💰 Live Trading")
            if st.button("🔄 Switch to Paper Trading", type="primary", use_container_width=True):
                st.session_state.trading_mode = "paper"
                update_env_file("paper")
                st.session_state.broker_client = None  # Disconnect to force reconnection
                add_log("Switched to PAPER trading mode")
                st.success("✅ Switched to Paper Trading!")
                st.rerun()
        
        st.markdown("---")
        
        # Current status
        st.subheader("📊 Current Status")
        if st.session_state.broker_client:
            st.success("🟢 Broker Connected")
        else:
            st.error("🔴 No Broker")
        
        if st.session_state.trading_active:
            st.success("🟢 Trading Active")
        else:
            st.info("🔴 Trading Inactive")
        
        st.markdown("---")
        
        # Quick stats
        st.subheader("📈 Quick Stats")
        st.metric("Total Logs", len(st.session_state.logs))
        st.metric("Open Positions", len(st.session_state.positions))
        st.metric("Equity Points", len(st.session_state.equity_history))
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🏠 Home", "📊 Backtest", "⚡ Live Trading", "📝 Logs"])
    
    with tab1:
        home_tab()
    
    with tab2:
        backtest_tab()
    
    with tab3:
        live_trading_tab()
    
    with tab4:
        logs_tab()
    
    # Auto-refresh for live trading
    if st.session_state.trading_active:
        time.sleep(5)
        st.rerun()

if __name__ == "__main__":
    main()
