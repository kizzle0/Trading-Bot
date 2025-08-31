"""
SMA Crossover Strategy with ATR-based Stop Loss
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple


def sma(series, window: int):
    """Calculate Simple Moving Average. Works with both pandas Series and numpy arrays."""
    if hasattr(series, 'rolling'):
        # pandas Series
        return series.rolling(window).mean()
    else:
        # numpy array
        return pd.Series(series).rolling(window).mean().values


def atr(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Calculate Average True Range"""
    # df with columns: ['Open','High','Low','Close']
    high_low = df['High'] - df['Low']
    high_close = (df['High'] - df['Close'].shift()).abs()
    low_close = (df['Low'] - df['Close'].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(window).mean()


def generate_signals(df: pd.DataFrame, fast: int, slow: int):
    """Generate SMA crossover signals"""
    df = df.copy()
    df['fast'] = sma(df['Close'], fast)
    df['slow'] = sma(df['Close'], slow)
    df['signal'] = 0
    df.loc[(df['fast'] > df['slow']) & (df['fast'].shift() <= df['slow'].shift()), 'signal'] = 1   # golden cross
    df.loc[(df['fast'] < df['slow']) & (df['fast'].shift() >= df['slow'].shift()), 'signal'] = -1  # death cross
    return df


def stop_prices(df: pd.DataFrame, atr_window: int, atr_mult: float):
    """Calculate ATR-based stop prices"""
    df = df.copy()
    df['ATR'] = atr(df, atr_window)
    df['long_stop'] = df['Close'] - atr_mult * df['ATR']
    df['short_stop'] = df['Close'] + atr_mult * df['ATR']
    return df[['long_stop','short_stop','ATR']]


class SMAATRStrategy:
    """SMA Crossover Strategy with ATR-based Stop Loss"""
    
    def __init__(self, fast: int = 20, slow: int = 50, atr_window: int = 14, atr_mult: float = 2.0):
        self.fast = fast
        self.slow = slow
        self.atr_window = atr_window
        self.atr_mult = atr_mult
    
    def get_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Get trading signals for the given data"""
        signals = generate_signals(df, self.fast, self.slow)
        stops = stop_prices(df, self.atr_window, self.atr_mult)
        return signals.join(stops, how='inner')
    
    def get_last_signal(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get the latest signal and stop prices"""
        signals_df = self.get_signals(df)
        if len(signals_df) == 0:
            return {'signal': 0, 'long_stop': None, 'short_stop': None, 'atr': None}
        
        last = signals_df.iloc[-1]
        return {
            'signal': int(last['signal']),
            'long_stop': float(last['long_stop']) if pd.notna(last['long_stop']) else None,
            'short_stop': float(last['short_stop']) if pd.notna(last['short_stop']) else None,
            'atr': float(last['ATR']) if pd.notna(last['ATR']) else None
        }
    
    def get_params(self) -> Dict[str, Any]:
        """Get strategy parameters"""
        return {
            'fast': self.fast,
            'slow': self.slow,
            'atr_window': self.atr_window,
            'atr_mult': self.atr_mult
        }
