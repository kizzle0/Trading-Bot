"""
Backtesting Engine
"""
import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import yfinance as yf
from typing import Dict, Any
from datetime import datetime, timedelta

# Optional imports
try:
    import ccxt
    CCXT_AVAILABLE = True
except ImportError:
    CCXT_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from strategies.sma_atr import sma, atr


class SmaAtrStrategy(Strategy):
    """SMA Crossover Strategy with ATR-based Stop Loss for backtesting"""
    
    fast = 20
    slow = 50
    atr_window = 14
    atr_mult = 2.0

    def init(self):
        close = self.data.Close
        high = self.data.High
        low = self.data.Low
        self.fast_sma = self.I(sma, close, self.fast)
        self.slow_sma = self.I(sma, close, self.slow)
        self.atr_ind = self.I(lambda o,h,l,c,w: atr(pd.DataFrame({'Open':o,'High':h,'Low':l,'Close':c}), w), 
                              self.data.Open, self.data.High, self.data.Low, self.data.Close, self.atr_window)

    def next(self):
        if not self.position:
            if crossover(self.fast_sma, self.slow_sma):
                sl = self.data.Close[-1] - self.atr_mult * self.atr_ind[-1]
                self.buy(sl=sl)
            elif crossover(self.slow_sma, self.fast_sma):
                sl = self.data.Close[-1] + self.atr_mult * self.atr_ind[-1]
                self.sell(sl=sl)
        else:
            if self.position.is_long and crossover(self.slow_sma, self.fast_sma):
                self.position.close()
            elif self.position.is_short and crossover(self.fast_sma, self.slow_sma):
                self.position.close()


def fetch_ohlc_yahoo(symbol: str, period: str = "1y", interval: str = "1h") -> pd.DataFrame:
    """Fetch OHLC data from Yahoo Finance with robust error handling"""
    print(f"  📊 Fetching {symbol} from Yahoo Finance ({period}, {interval})")
    
    try:
        # Try standard download first
        df = yf.download(
            symbol,
            period=period,
            interval=interval,
            auto_adjust=False,
            progress=False,
            group_by="column",
        )

        # If nothing came back, try different approaches
        if df is None or df.empty:
            print(f"  ⚠️ No data for {symbol} with {interval}, trying daily data...")
            df = yf.download(symbol, period=period, interval="1d", auto_adjust=False, progress=False, group_by="column")
        
        # If still empty, try with a shorter period
        if df is None or df.empty:
            print(f"  ⚠️ No data for {symbol} with {period}, trying 6 months...")
            df = yf.download(symbol, period="6mo", interval="1d", auto_adjust=False, progress=False, group_by="column")
        
        # If still empty, try with 3 months
        if df is None or df.empty:
            print(f"  ⚠️ No data for {symbol} with 6mo, trying 3 months...")
            df = yf.download(symbol, period="3mo", interval="1d", auto_adjust=False, progress=False, group_by="column")

        # Check if we got any data
        if df is None or df.empty:
            print(f"  ❌ No data found for {symbol}")
            return pd.DataFrame()

        # If still MultiIndex, try to select the symbol level or flatten to last level
        if isinstance(df.columns, pd.MultiIndex):
            # Try to get the first level (column names) instead of symbol level
            df.columns = df.columns.get_level_values(0)

        # Normalize column names to Title case (Open, High, Low, Close, Volume)
        df.columns = [str(c).strip().title() for c in df.columns]

        # Create Volume if missing (common for FX)
        for needed in ["Open", "High", "Low", "Close", "Volume"]:
            if needed not in df.columns:
                if needed == "Volume":
                    df["Volume"] = 0
                else:
                    # Sometimes Yahoo returns 'Adj Close' but not 'Close' for weird combos
                    # If 'Adj Close' exists and 'Close' missing, use it
                    if needed == "Close" and "Adj Close" in df.columns:
                        df["Close"] = df["Adj Close"]
                    else:
                        # Last resort: duplicate Close into missing O/H/L if truly absent (rare)
                        if "Close" in df.columns:
                            df[needed] = df["Close"]
                        else:
                            print(f"  ❌ Missing required column: {needed}")
                            return pd.DataFrame()
        
        # Validate we have the required columns
        required_cols = ["Open", "High", "Low", "Close"]
        if not all(col in df.columns for col in required_cols):
            print(f"  ❌ Missing required columns. Available: {list(df.columns)}")
            return pd.DataFrame()
        
        # Remove any rows with NaN values
        df = df.dropna()
        
        if len(df) == 0:
            print(f"  ❌ No valid data after cleaning NaN values")
            return pd.DataFrame()
        
        print(f"  ✅ Successfully fetched {len(df)} data points")
        return df
        
    except Exception as e:
        print(f"  ❌ Yahoo Finance error for {symbol}: {e}")
        return pd.DataFrame()


def fetch_ohlc_ccxt(symbol: str, period: str = "1y", interval: str = "1h") -> pd.DataFrame:
    """Fetch OHLC data from CCXT exchange (crypto) with robust fallback"""
    print(f"  📊 Fetching {symbol} from CCXT (crypto)")
    
    if not CCXT_AVAILABLE:
        print("  ⚠️ CCXT not available, falling back to Yahoo Finance")
        return fetch_ohlc_yahoo(symbol, period, interval)
    
    # Map intervals
    interval_map = {
        "1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m",
        "1h": "1h", "4h": "4h", "1d": "1d"
    }
    
    # Map periods to days
    period_map = {
        "1mo": 30, "3mo": 90, "6mo": 180, "1y": 365, "2y": 730, "5y": 1825
    }
    
    # Try multiple exchanges
    exchanges = [
        ccxt.binance(),
        ccxt.coinbase(),
        ccxt.kraken(),
        ccxt.bitfinex()
    ]
    
    timeframe = interval_map.get(interval, "1h")
    days = period_map.get(period, 365)
    
    for exchange in exchanges:
        try:
            print(f"  🔄 Trying {exchange.id} exchange...")
            # Calculate start time
            since = exchange.milliseconds() - (days * 24 * 60 * 60 * 1000)
            
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=1000)
            
            if ohlcv and len(ohlcv) > 0:
                # Convert to DataFrame
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                
                print(f"  ✅ Successfully fetched {len(df)} data points from {exchange.id}")
                return df
            else:
                print(f"  ⚠️ {exchange.id} returned empty data")
                
        except Exception as e:
            print(f"  ❌ {exchange.id} failed: {e}")
            continue
    
    print("  ⚠️ All CCXT exchanges failed, falling back to Yahoo Finance")
    # Fallback to Yahoo Finance with crypto symbol conversion
    return fetch_ohlc_yahoo(symbol, period, interval)


def fetch_ohlc_oanda(symbol: str, period: str = "1y", interval: str = "1h") -> pd.DataFrame:
    """Fetch OHLC data from OANDA (forex) with robust fallback"""
    print(f"  📊 Fetching {symbol} from OANDA (forex)")
    
    # OANDA API requires authentication, so we'll use Yahoo Finance for backtesting
    # Try multiple OANDA to Yahoo symbol conversions
    oanda_symbols = []
    
    if "_" in symbol:
        # Try different OANDA to Yahoo conversions
        oanda_symbols = [
            symbol.replace("_", "") + "=X",  # EUR_USD -> EURUSD=X
            symbol.replace("_", "/") + "=X", # EUR_USD -> EUR/USD=X
            symbol.replace("_", ""),         # EUR_USD -> EURUSD
            symbol.replace("_", "/"),        # EUR_USD -> EUR/USD
        ]
    else:
        # If no underscore, try adding =X
        oanda_symbols = [symbol, symbol + "=X"]
    
    # Try each OANDA symbol format
    for oanda_symbol in oanda_symbols:
        try:
            print(f"  🔄 Trying OANDA symbol: {oanda_symbol}")
            df = fetch_ohlc_yahoo(oanda_symbol, period, interval)
            
            if df is not None and not df.empty and len(df) > 10:
                print(f"  ✅ Successfully fetched {len(df)} data points using OANDA symbol: {oanda_symbol}")
                return df
            else:
                print(f"  ⚠️ OANDA symbol {oanda_symbol} returned empty data")
        except Exception as e:
            print(f"  ❌ OANDA symbol {oanda_symbol} failed: {e}")
    
    print("  ⚠️ All OANDA symbol formats failed")
    return pd.DataFrame()


def fetch_ohlc_alpaca(symbol: str, period: str = "1y", interval: str = "1h") -> pd.DataFrame:
    """Fetch OHLC data from Alpaca (stocks) with robust fallback"""
    print(f"  📊 Fetching {symbol} from Alpaca (stocks)")
    
    # Alpaca API requires authentication, so we'll use Yahoo Finance for backtesting
    # Try multiple stock symbol formats
    alpaca_symbols = [
        symbol,                    # AAPL -> AAPL
        symbol + ".TO",           # AAPL -> AAPL.TO (Toronto)
        symbol + ".L",            # AAPL -> AAPL.L (London)
        symbol + ".T",            # AAPL -> AAPL.T (Tokyo)
        symbol + ".HK",           # AAPL -> AAPL.HK (Hong Kong)
        symbol + ".AX",           # AAPL -> AAPL.AX (Australia)
    ]
    
    # Try each Alpaca symbol format
    for alpaca_symbol in alpaca_symbols:
        try:
            print(f"  🔄 Trying Alpaca symbol: {alpaca_symbol}")
            df = fetch_ohlc_yahoo(alpaca_symbol, period, interval)
            
            if df is not None and not df.empty and len(df) > 10:
                print(f"  ✅ Successfully fetched {len(df)} data points using Alpaca symbol: {alpaca_symbol}")
                return df
            else:
                print(f"  ⚠️ Alpaca symbol {alpaca_symbol} returned empty data")
        except Exception as e:
            print(f"  ❌ Alpaca symbol {alpaca_symbol} failed: {e}")
    
    print("  ⚠️ All Alpaca symbol formats failed")
    return pd.DataFrame()


def fetch_ohlc(symbol: str, broker: str = "yahoo", period: str = "1y", interval: str = "1h") -> pd.DataFrame:
    """Fetch OHLC data based on broker type with fallbacks"""
    print(f"Fetching data for {symbol} using {broker} broker...")
    
    # Try the specified broker first
    try:
        if broker == "ccxt":
            df = fetch_ohlc_ccxt(symbol, period, interval)
        elif broker == "oanda":
            df = fetch_ohlc_oanda(symbol, period, interval)
        elif broker == "alpaca":
            df = fetch_ohlc_alpaca(symbol, period, interval)
        else:  # yahoo or default
            df = fetch_ohlc_yahoo(symbol, period, interval)
        
        # Check if we got valid data
        if df is not None and not df.empty and len(df) > 10:
            print(f"✅ Successfully fetched {len(df)} data points from {broker}")
            return df
        else:
            print(f"⚠️ {broker} returned empty or insufficient data, trying fallbacks...")
    except Exception as e:
        print(f"❌ {broker} failed: {e}, trying fallbacks...")
    
    # Fallback to Yahoo Finance with different symbol formats
    fallback_symbols = []
    
    if broker == "oanda":
        if "_" in symbol:
            # Try different OANDA to Yahoo conversions
            fallback_symbols = [
                symbol.replace("_", "") + "=X",  # EUR_USD -> EURUSD=X
                symbol.replace("_", "/") + "=X", # EUR_USD -> EUR/USD=X
                symbol.replace("_", ""),         # EUR_USD -> EURUSD
                symbol.replace("_", "/"),        # EUR_USD -> EUR/USD
            ]
        else:
            fallback_symbols = [symbol, symbol + "=X"]
            
    elif broker == "ccxt":
        if "/" in symbol:
            # Try different crypto formats for Yahoo Finance
            base, quote = symbol.split("/")
            fallback_symbols = [
                f"{base}-{quote}",              # BTC/USDT -> BTC-USDT
                f"{base}-USD",                  # BTC/USDT -> BTC-USD
                f"{base}USD",                   # BTC/USDT -> BTCUSD
                f"{base}{quote}",               # BTC/USDT -> BTCUSDT
                f"{base}-{quote}-USD",          # BTC/USDT -> BTC-USDT-USD
                symbol,                         # BTC/USDT -> BTC/USDT (original)
            ]
        else:
            fallback_symbols = [symbol, symbol + "-USD", symbol + "USD"]
            
    elif broker == "alpaca":
        # Try different stock formats
        fallback_symbols = [
            symbol,                         # AAPL -> AAPL
            symbol + ".TO",                 # AAPL -> AAPL.TO (Toronto)
            symbol + ".L",                  # AAPL -> AAPL.L (London)
            symbol + ".T",                  # AAPL -> AAPL.T (Tokyo)
            symbol + ".HK",                 # AAPL -> AAPL.HK (Hong Kong)
            symbol + ".AX",                 # AAPL -> AAPL.AX (Australia)
        ]
    else:
        # For yahoo or unknown brokers, try the original symbol
        fallback_symbols = [symbol]
    
    # Try each fallback symbol
    for fallback_symbol in fallback_symbols:
        try:
            print(f"🔄 Trying fallback symbol: {fallback_symbol}")
            df = fetch_ohlc_yahoo(fallback_symbol, period, interval)
            
            if df is not None and not df.empty and len(df) > 10:
                print(f"✅ Successfully fetched {len(df)} data points using fallback: {fallback_symbol}")
                return df
            else:
                print(f"⚠️ Fallback {fallback_symbol} returned empty data")
        except Exception as e:
            print(f"❌ Fallback {fallback_symbol} failed: {e}")
    
    # If all fallbacks failed, raise an error with helpful message
    raise ValueError(f"""
    ❌ Could not fetch data for symbol '{symbol}' with broker '{broker}'.
    
    Troubleshooting:
    1. Check if the symbol exists and is valid
    2. Try a different time period (e.g., '6mo' instead of '1y')
    3. Try a different interval (e.g., '1d' instead of '1h')
    4. For forex: Use format like 'EURUSD=X' or 'EUR_USD'
    5. For crypto: Use format like 'BTC-USD' or 'BTC/USDT'
    6. For stocks: Use format like 'AAPL' or 'MSFT'
    
    Tried fallback symbols: {fallback_symbols}
    """)


def run_backtest(
    symbol: str,
    broker: str = "yahoo",
    period: str = "1y",
    interval: str = "1d",
    fast: int = 20,
    slow: int = 50,
    atr_window: int = 14,
    atr_mult: float = 2.0,
    cash: float = 10000,
    commission: float = 0.0002
) -> Dict[str, Any]:
    """
    Run backtest with given parameters
    
    Args:
        symbol: Trading symbol
        broker: Broker type (yahoo, oanda, ccxt, alpaca)
        period: Time period for backtest
        interval: Data interval
        fast: Fast SMA period
        slow: Slow SMA period
        atr_window: ATR window
        atr_mult: ATR multiplier
        cash: Starting cash
        commission: Commission rate
    
    Returns:
        Dictionary with backtest results
    """
    # Fetch data based on broker
    df = fetch_ohlc(symbol, broker, period, interval)
    
    # Set strategy parameters
    SmaAtrStrategy.fast = fast
    SmaAtrStrategy.slow = slow
    SmaAtrStrategy.atr_window = atr_window
    SmaAtrStrategy.atr_mult = atr_mult

    # Run backtest
    bt = Backtest(
        df, 
        SmaAtrStrategy, 
        cash=cash, 
        commission=commission, 
        trade_on_close=False, 
        hedging=False, 
        exclusive_orders=True
    )
    
    stats = bt.run()
    
    return {
        'stats': stats,
        'backtest': bt,
        'data': df
    }


def plot_backtest(bt: Backtest, open_browser: bool = False):
    """Plot backtest results"""
    try:
        bt.plot(open_browser=open_browser)
    except Exception as e:
        print("Plotting failed (likely headless env). Stats printed above.")
        print(f"Error: {e}")
