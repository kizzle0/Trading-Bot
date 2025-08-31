# Universal Trading Bot

A modular Python trading bot that supports crypto, forex, and stocks with moving average crossover strategy and ATR-based stop loss. Features backtesting and live trading across multiple brokers.

## Features

- **Multi-Broker Support**: Crypto (CCXT), Forex (OANDA), Stocks (Alpaca)
- **Strategy**: Moving average crossover (fast/slow SMA) with ATR-based stop loss
- **Backtesting**: Uses yfinance + backtesting.py for historical testing
- **Live Trading**: Real-time trading with risk management
- **Risk Management**: Position sizing based on account equity and risk per trade
- **Web Dashboard**: Beautiful Streamlit interface for easy control and monitoring
- **Modular Design**: Easy to add new strategies and brokers

## Quick Start

### 1. Setup Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\Activate.ps1

# Activate (Linux/Mac)
source venv/bin/activate
```

### 2. Install Dependencies

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

### 3. Configure Brokers

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys and settings
# See BROKER_SETUP.md for detailed broker configuration guide
```

### 4. Launch Web Dashboard (Recommended)

```bash
# Launch the Streamlit dashboard
streamlit run dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

**Dashboard Features:**
- 🏠 **Home**: Connect to brokers and view account balances
- 📊 **Backtest**: Run backtests with custom parameters and visualize results
- ⚡ **Live Trading**: Start/stop live trading with real-time monitoring
- 📝 **Logs**: View trading activity and export logs

### 5. Command Line Backtesting

```bash
# Test on EUR/USD (Forex)
python run_backtest.py --symbol EURUSD=X --period 1y --interval 1d --fast 20 --slow 50

# Test on Bitcoin (Crypto)
python run_backtest.py --symbol BTC-USD --period 1y --interval 1d --fast 20 --slow 50

# Test on Apple stock
python run_backtest.py --symbol AAPL --period 1y --interval 1d --fast 20 --slow 50
```

### 6. Live Trading Setup

1. Choose your broker and get API credentials:
   - **OANDA** (Forex): https://www.oanda.com/demo-account/
   - **Binance** (Crypto): https://www.binance.com/en/my/settings/api-management
   - **Alpaca** (Stocks): https://alpaca.markets/

2. Copy `.env.example` to `.env`
3. Fill in your broker credentials in `.env`
4. Set `BROKER=oanda` (or `ccxt` or `alpaca`)
5. Run live trading:

```bash
python run_live.py
```

## Configuration

Edit `.env` file to customize:

### Broker Selection
- `BROKER`: Choose broker (`ccxt`, `oanda`, `alpaca`)

### API Credentials
- **OANDA**: Access token, account ID, environment
- **CCXT**: Exchange, API key, secret, sandbox mode
- **Alpaca**: API key, secret key, base URL, paper trading

### Trading Settings
- `INSTRUMENT`: Trading pair/symbol
- `RISK_PER_TRADE`: Risk per trade (e.g., 0.005 = 0.5%)
- `MAX_DAILY_DRAWDOWN`: Daily drawdown limit
- `UNITS_CAP`: Maximum position size

### Strategy Parameters
- `FAST_SMA`: Fast SMA period (default: 20)
- `SLOW_SMA`: Slow SMA period (default: 50)
- `ATR_WINDOW`: ATR calculation window (default: 14)
- `ATR_MULTIPLIER`: ATR multiplier for stop loss (default: 2.0)

## Strategy Details

### Moving Average Crossover
- **Long Entry**: Fast SMA crosses above Slow SMA (golden cross)
- **Short Entry**: Fast SMA crosses below Slow SMA (death cross)
- **Exit**: Opposite crossover or stop loss hit

### Risk Management
- **Stop Loss**: ATR-based stop loss (default: 2x ATR)
- **Position Sizing**: Based on account equity and risk per trade
- **Daily Drawdown Limit**: Halts trading if daily loss exceeds limit

## File Structure

```
├── strategies/          # Trading strategies
│   ├── __init__.py
│   └── sma_atr.py      # SMA crossover + ATR strategy
├── risk/               # Risk management
│   ├── __init__.py
│   └── atr_sizing.py   # ATR-based position sizing
├── brokers/            # Broker clients
│   ├── __init__.py
│   ├── ccxt_client.py  # Crypto exchanges (CCXT)
│   ├── oanda_client.py # Forex (OANDA)
│   └── alpaca_client.py # Stocks (Alpaca)
├── backtest/           # Backtesting engine
│   ├── __init__.py
│   └── backtest.py     # Backtesting logic
├── run_backtest.py     # Backtest CLI wrapper
├── run_live.py         # Live trading script
├── dashboard.py        # Streamlit web dashboard
├── config.py           # Configuration loading
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
└── README.md           # This file
```

## Backtesting Examples

```bash
# Forex - EUR/USD 1-year daily
python run_backtest.py --symbol EURUSD=X --period 1y --interval 1d

# Crypto - Bitcoin with custom parameters
python run_backtest.py --symbol BTC-USD --period 2y --interval 1d --fast 10 --slow 30

# Stocks - Apple with different ATR settings
python run_backtest.py --symbol AAPL --period 1y --interval 1d --atr_window 21 --atr_mult 1.5

# Show plot after backtest
python run_backtest.py --symbol EURUSD=X --period 1y --interval 1d --plot
```

## Live Trading Examples

### Forex (OANDA)
```bash
# Set in .env:
BROKER=oanda
INSTRUMENT=EUR_USD
OANDA_ACCESS_TOKEN=your_token
OANDA_ACCOUNT_ID=your_account_id

python run_live.py
```

### Crypto (CCXT/Binance)
```bash
# Set in .env:
BROKER=ccxt
INSTRUMENT=BTC/USDT
CCXT_EXCHANGE=binance
CCXT_API_KEY=your_key
CCXT_SECRET=your_secret

python run_live.py
```

### Stocks (Alpaca)
```bash
# Set in .env:
BROKER=alpaca
INSTRUMENT=AAPL
ALPACA_API_KEY=your_key
ALPACA_SECRET_KEY=your_secret

python run_live.py
```

## Adding New Strategies

1. Create a new strategy file in `strategies/`:
```python
# strategies/my_strategy.py
class MyStrategy:
    def __init__(self, param1, param2):
        self.param1 = param1
        self.param2 = param2
    
    def get_signals(self, df):
        # Your strategy logic
        return signals_df
    
    def get_last_signal(self, df):
        # Return latest signal
        return signal_data
```

2. Update `run_live.py` to use your strategy
3. Add strategy parameters to `config.py` and `.env.example`

## Adding New Brokers

1. Create a new broker client in `brokers/`:
```python
# brokers/my_broker.py
class MyBrokerClient:
    def connect(self) -> bool:
        # Connection logic
        pass
    
    def get_balance(self) -> Dict[str, float]:
        # Get account balance
        pass
    
    def place_order(self, symbol, side, size, stop_loss=None):
        # Place order
        pass
```

2. Update `run_live.py` to support your broker
3. Add broker settings to `config.py` and `.env.example`

## Dependencies

- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `backtesting` - Backtesting framework
- `yfinance` - Yahoo Finance data
- `ccxt` - Crypto exchange library
- `oandapyV20` - OANDA API client
- `alpaca-trade-api` - Alpaca API client
- `python-dotenv` - Environment variable loading
- `loguru` - Logging
- `pydantic` - Configuration validation
- `streamlit` - Web dashboard framework
- `matplotlib` - Plotting and visualization
- `plotly` - Interactive charts

## Disclaimer

This is for educational purposes only. Trading involves risk of loss. Always test thoroughly before live trading with real money. Use paper trading/sandbox environments first.