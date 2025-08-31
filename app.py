#!/usr/bin/env python3
"""
Simple Streamlit app for cloud deployment
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="Trading Bot",
    page_icon="📈",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 32px;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 30px;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<div class="main-header">🚀 Universal Trading Bot</div>', unsafe_allow_html=True)
    
    # Status metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Balance", "$1,250.00", "+$25.00")
    
    with col2:
        st.metric("📈 Today's P&L", "+$15.50", "+1.2%")
    
    with col3:
        st.metric("🔄 Active Trades", "3")
    
    with col4:
        st.metric("📊 Win Rate", "68%", "+5%")
    
    # Quick actions
    st.markdown("### 🎯 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("▶️ Start Trading", type="primary"):
            st.success("✅ Trading started!")
            st.balloons()
    
    with col2:
        if st.button("⏹️ Stop Trading"):
            st.warning("⏹️ Trading stopped!")
    
    with col3:
        if st.button("📊 Run Backtest"):
            st.info("📊 Backtest completed!")
    
    # Current positions
    st.markdown("### 📊 Current Positions")
    
    positions_data = {
        'Symbol': ['EUR/USD', 'BTC/USDT', 'AAPL'],
        'Side': ['Long', 'Long', 'Short'],
        'Size': ['10,000', '0.5', '100'],
        'Entry': ['1.0850', '45,200', '150.25'],
        'Current': ['1.0865', '45,800', '149.80'],
        'P&L': ['+$15.00', '+$300.00', '+$45.00']
    }
    
    df = pd.DataFrame(positions_data)
    st.dataframe(df, use_container_width=True)
    
    # Performance chart
    st.markdown("### 📈 Performance")
    
    # Generate sample data
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
    performance = [1000 + i * 10 + (i % 7 - 3) * 5 for i in range(len(dates))]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=performance,
        mode='lines',
        name='Portfolio Value',
        line=dict(color='#1f77b4', width=3)
    ))
    
    fig.update_layout(
        title="Portfolio Performance (30 Days)",
        xaxis_title="Date",
        yaxis_title="Value ($)",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Trading settings
    with st.expander("⚙️ Trading Settings"):
        col1, col2 = st.columns(2)
        
        with col1:
            risk_per_trade = st.slider("Risk per Trade (%)", 0.5, 5.0, 1.0, 0.1)
            daily_drawdown = st.slider("Daily Drawdown Limit (%)", 1.0, 10.0, 3.0, 0.5)
        
        with col2:
            fast_sma = st.slider("Fast SMA", 5, 50, 20)
            slow_sma = st.slider("Slow SMA", 20, 200, 50)
        
        if st.button("💾 Save Settings"):
            st.success("Settings saved!")
    
    # Recent trades
    st.markdown("### 📋 Recent Trades")
    
    trades_data = {
        'Time': ['09:15', '10:30', '11:45', '14:20'],
        'Symbol': ['EUR/USD', 'BTC/USDT', 'AAPL', 'GBP/USD'],
        'Action': ['Buy', 'Sell', 'Sell', 'Buy'],
        'P&L': ['+$12.50', '+$45.00', '-$8.75', '+$22.30']
    }
    
    trades_df = pd.DataFrame(trades_data)
    st.dataframe(trades_df, use_container_width=True)

if __name__ == "__main__":
    main()
