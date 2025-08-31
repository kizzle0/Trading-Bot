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
from config import settings
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
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
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

def get_broker_client(broker: str):
    """Get broker client instance"""
    try:
        if broker == 'ccxt':
            return CCXTClient(
                exchange=settings.CCXT_EXCHANGE,
                api_key=settings.CCXT_API_KEY,
                secret=settings.CCXT_SECRET,
                sandbox=settings.CCXT_SANDBOX
            )
        elif broker == 'oanda':
            return OANDAClient(
                access_token=settings.OANDA_ACCESS_TOKEN,
                account_id=settings.OANDA_ACCOUNT_ID,
                environment=settings.OANDA_ENVIRONMENT
            )
        elif broker == 'alpaca':
            return AlpacaClient(
                api_key=settings.ALPACA_API_KEY,
                secret_key=settings.ALPACA_SECRET_KEY,
                base_url=settings.ALPACA_BASE_URL,
                paper=settings.ALPACA_PAPER
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
        
        if broker_key == "oanda":
            if settings.OANDA_ACCESS_TOKEN and settings.OANDA_ACCOUNT_ID:
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
            if settings.CCXT_API_KEY and settings.CCXT_SECRET:
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
            if settings.ALPACA_API_KEY and settings.ALPACA_SECRET_KEY:
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
        
        # Connect button
        if st.button("🔌 Connect to Broker", type="primary"):
            with st.spinner(f"Connecting to {selected_broker}..."):
                client = get_broker_client(broker_key)
                if client and client.connect():
                    st.session_state.broker_client = client
                    st.session_state.current_broker = broker_key
                    if broker_key == "oanda":
                        st.session_state.selected_instrument = selected_pair
                    elif broker_key == "ccxt":
                        st.session_state.selected_instrument = selected_pair
                    elif broker_key == "alpaca":
                        st.session_state.selected_instrument = selected_symbol
                    add_log(f"Connected to {selected_broker}")
                    st.success(f"✅ Connected to {selected_broker}")
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
        
        # Symbol selection
        if 'selected_instrument' in st.session_state:
            default_symbol = st.session_state.selected_instrument
        else:
            default_symbol = "EURUSD=X"
            
        symbol = st.text_input("Symbol:", value=default_symbol, 
                              help="Examples: EURUSD=X, BTC-USD, AAPL")
        
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
            with st.spinner("Running backtest..."):
                try:
                    result = run_backtest(
                        symbol=symbol,
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
                    st.error(f"❌ Backtest failed: {e}")
                    add_log(f"Backtest failed: {e}", "ERROR")
    
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
                    line=dict(color='#1f77b4', width=2)
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
                    line=dict(color='#2ecc71', width=2)
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
    # Header
    st.markdown('<div class="main-header">🚀 Universal Trading Bot Dashboard</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/200x100/1f77b4/ffffff?text=Trading+Bot", width=200)
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
