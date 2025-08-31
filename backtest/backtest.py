"""
Backtesting Engine
"""
import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import yfinance as yf
from typing import Dict, Any

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


def fetch_ohlc(symbol: str, period: str = "1y", interval: str = "1h") -> pd.DataFrame:
    """Fetch OHLC data from Yahoo Finance"""
    # Try standard download first
    df = yf.download(
        symbol,
        period=period,
        interval=interval,
        auto_adjust=False,
        progress=False,
        group_by="column",
    )

    # If nothing came back, fall back to daily data
    if df is None or df.empty:
        df = yf.download(symbol, period="1y", interval="1d", auto_adjust=False, progress=False, group_by="column")

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
                        raise ValueError(f"Missing required column even after fallback: {needed}")
    
    return df


def run_backtest(
    symbol: str,
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
    
    Returns:
        Dictionary with backtest results
    """
    # Fetch data
    df = fetch_ohlc(symbol, period, interval)
    
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
