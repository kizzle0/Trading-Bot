# 🚀 Universal Trading Bot

A powerful, multi-broker trading bot with live trading, backtesting, and a beautiful Streamlit dashboard.

## ✨ Features

- **Multi-Broker Support**: OANDA (Forex), CCXT (Crypto), Alpaca (Stocks)
- **Live Trading**: Real-time trading with risk management
- **Backtesting**: Test strategies across all brokers
- **Beautiful Dashboard**: Purple-themed Streamlit interface
- **Paper & Live Trading**: One-click switching between modes
- **Risk Management**: ATR-based stop losses and position sizing

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Credentials
Create a `.env` file with your broker credentials:
```env
BROKER=alpaca
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here
```

### 3. Run the Dashboard
```bash
streamlit run dashboard.py
```

## 🏦 Supported Brokers

| Broker | Type | Paper Trading | Live Trading |
|--------|------|---------------|--------------|
| **OANDA** | Forex | ✅ | ✅ |
| **CCXT** | Crypto | ✅ | ✅ |
| **Alpaca** | Stocks | ✅ | ✅ |

## 📊 Usage

### Dashboard
- **Home**: Connect to brokers and view account info
- **Backtest**: Test strategies with historical data
- **Live Trading**: Start/stop live trading
- **Logs**: View trading activity

### Command Line
```bash
# Run backtest
python run_backtest.py --broker alpaca --symbol AAPL --period 1y

# Start live trading
python run_live.py
```

## 🔧 Configuration

### Environment Variables
- `BROKER`: Choose broker (oanda, ccxt, alpaca)
- `ALPACA_API_KEY`: Alpaca API key
- `ALPACA_SECRET_KEY`: Alpaca secret key
- `OANDA_ACCESS_TOKEN`: OANDA access token
- `OANDA_ACCOUNT_ID`: OANDA account ID
- `CCXT_API_KEY`: Exchange API key
- `CCXT_SECRET`: Exchange secret

### Strategy Parameters
- `FAST_SMA`: Fast moving average period (default: 20)
- `SLOW_SMA`: Slow moving average period (default: 50)
- `ATR_WINDOW`: ATR calculation window (default: 14)
- `ATR_MULTIPLIER`: Stop loss multiplier (default: 2.0)

## 🌐 Streamlit Cloud Deployment

For deployed apps, use Streamlit secrets instead of `.env`:

1. Go to your app's settings in Streamlit Cloud
2. Add credentials to the **Secrets** section
3. Use this format:
```toml
[broker]
BROKER = "alpaca"

[alpaca]
ALPACA_API_KEY = "your_api_key_here"
ALPACA_SECRET_KEY = "your_secret_key_here"
ALPACA_BASE_URL = "https://paper-api.alpaca.markets"
ALPACA_PAPER = true
```

## ⚠️ Important Notes

- **Start with paper trading** to test your strategies
- **Never commit API keys** to version control
- **Use proper risk management** for live trading
- **Test thoroughly** before going live

## 📁 Project Structure

```
├── dashboard.py              # Main Streamlit dashboard
├── run_live.py              # Live trading script
├── run_backtest.py          # Backtesting script
├── config.py                # Configuration (local)
├── config_secrets.py        # Configuration (cloud)
├── secrets_manager.py       # Secrets management
├── backtest/                # Backtesting engine
├── brokers/                 # Broker clients
├── strategies/              # Trading strategies
├── risk/                    # Risk management
└── requirements.txt         # Dependencies
```

## 🎯 Strategy

**SMA + ATR Strategy**:
- **Entry**: Fast SMA crosses above/below Slow SMA
- **Exit**: Opposite crossover or ATR-based stop loss
- **Risk Management**: Position sizing based on account equity

## 🆘 Support

For issues or questions:
1. Check the debug information in the dashboard
2. Verify your API credentials are correct
3. Ensure you're using the right broker for your asset type

---

**Happy Trading! 🚀📈**