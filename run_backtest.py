#!/usr/bin/env python3
"""
Backtest CLI Wrapper
"""
import argparse
from backtest.backtest import run_backtest, plot_backtest


def main():
    parser = argparse.ArgumentParser(description='Run backtest with SMA/ATR strategy')
    parser.add_argument('--symbol', type=str, default='EURUSD=X', 
                       help='Symbol to backtest (e.g., EURUSD=X, BTC-USD, AAPL)')
    parser.add_argument('--period', type=str, default='1y', 
                       help='Period for backtest (e.g., 1y, 2y, 6mo)')
    parser.add_argument('--interval', type=str, default='1d', 
                       help='Data interval (e.g., 1d, 1h, 1m)')
    parser.add_argument('--fast', type=int, default=20, 
                       help='Fast SMA period')
    parser.add_argument('--slow', type=int, default=50, 
                       help='Slow SMA period')
    parser.add_argument('--atr_window', type=int, default=14, 
                       help='ATR window')
    parser.add_argument('--atr_mult', type=float, default=2.0, 
                       help='ATR multiplier for stop loss')
    parser.add_argument('--cash', type=float, default=10000, 
                       help='Starting cash')
    parser.add_argument('--commission', type=float, default=0.0002, 
                       help='Commission rate')
    parser.add_argument('--plot', action='store_true', 
                       help='Show plot after backtest')
    
    args = parser.parse_args()
    
    print(f"Running backtest for {args.symbol}...")
    print(f"Period: {args.period}, Interval: {args.interval}")
    print(f"Strategy: SMA({args.fast}, {args.slow}) with ATR({args.atr_window}) x {args.atr_mult}")
    print("-" * 50)
    
    # Run backtest
    result = run_backtest(
        symbol=args.symbol,
        period=args.period,
        interval=args.interval,
        fast=args.fast,
        slow=args.slow,
        atr_window=args.atr_window,
        atr_mult=args.atr_mult,
        cash=args.cash,
        commission=args.commission
    )
    
    # Print results
    print(result['stats'])
    
    # Plot if requested
    if args.plot:
        plot_backtest(result['backtest'])


if __name__ == "__main__":
    main()
