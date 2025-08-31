#!/usr/bin/env python3
"""
Live Trading Script
"""
import time
import datetime as dt
import pandas as pd
from loguru import logger
from typing import Dict, Any

from config import settings
from strategies.sma_atr import SMAATRStrategy
from risk.atr_sizing import RiskParams, position_size_by_risk, get_pip_value_per_unit

# Import broker clients
from brokers.ccxt_client import CCXTClient
from brokers.oanda_client import OANDAClient
from brokers.alpaca_client import AlpacaClient


class CandleAggregator:
    """Aggregate tick data into candles"""
    
    def __init__(self, timeframe_minutes: int = 1):
        self.timeframe_minutes = timeframe_minutes
        self.current_candle = None
        self.ohlc = None

    def update(self, price: float, now: dt.datetime):
        """Update with new price data"""
        # Round to timeframe
        minute = now.replace(second=0, microsecond=0)
        candle_start = minute.replace(minute=(minute.minute // self.timeframe_minutes) * self.timeframe_minutes)
        
        if self.current_candle is None:
            self.current_candle = candle_start
            self.ohlc = {'Open': price, 'High': price, 'Low': price, 'Close': price}
            return None

        if candle_start == self.current_candle:
            # Update current candle
            self.ohlc['High'] = max(self.ohlc['High'], price)
            self.ohlc['Low'] = min(self.ohlc['Low'], price)
            self.ohlc['Close'] = price
            return None
        else:
            # Return completed candle and start new one
            closed = pd.DataFrame([self.ohlc], index=[self.current_candle])
            self.current_candle = candle_start
            self.ohlc = {'Open': price, 'High': price, 'Low': price, 'Close': price}
            return closed


class LiveTrader:
    """Live trading bot"""
    
    def __init__(self, broker: str):
        self.broker = broker
        self.client = None
        self.strategy = SMAATRStrategy(
            fast=settings.FAST_SMA,
            slow=settings.SLOW_SMA,
            atr_window=settings.ATR_WINDOW,
            atr_mult=settings.ATR_MULTIPLIER
        )
        self.agg = CandleAggregator()
        self.hist = pd.DataFrame()
        self.daily_start_equity = None
        self.halted_today = False
        
    def initialize_client(self):
        """Initialize the appropriate broker client"""
        if self.broker == 'ccxt':
            self.client = CCXTClient(
                exchange=settings.CCXT_EXCHANGE,
                api_key=settings.CCXT_API_KEY,
                secret=settings.CCXT_SECRET,
                sandbox=settings.CCXT_SANDBOX
            )
        elif self.broker == 'oanda':
            self.client = OANDAClient(
                access_token=settings.OANDA_ACCESS_TOKEN,
                account_id=settings.OANDA_ACCOUNT_ID,
                environment=settings.OANDA_ENVIRONMENT
            )
        elif self.broker == 'alpaca':
            self.client = AlpacaClient(
                api_key=settings.ALPACA_API_KEY,
                secret_key=settings.ALPACA_SECRET_KEY,
                base_url=settings.ALPACA_BASE_URL,
                paper=settings.ALPACA_PAPER
            )
        else:
            raise ValueError(f"Unknown broker: {self.broker}")
    
    def get_equity(self) -> float:
        """Get current account equity"""
        balance = self.client.get_balance()
        if self.broker == 'oanda':
            return balance.get('NAV', 0)
        elif self.broker == 'alpaca':
            return balance.get('equity', 0)
        else:  # ccxt
            # Sum all balances (simplified)
            return sum(balance.values())
    
    def check_daily_drawdown(self):
        """Check if daily drawdown limit is exceeded"""
        if self.daily_start_equity is None:
            self.daily_start_equity = self.get_equity()
            return False
        
        current_equity = self.get_equity()
        dd = (self.daily_start_equity - current_equity) / self.daily_start_equity
        
        if dd >= settings.MAX_DAILY_DRAWDOWN:
            if not self.halted_today:
                logger.warning(f"Daily drawdown limit hit ({dd:.2%}). Halting new entries for today.")
                self.halted_today = True
            return True
        
        return False
    
    def process_signal(self, signal_data: Dict[str, Any], current_price: float):
        """Process trading signal"""
        signal = signal_data['signal']
        
        if signal == 0 or self.halted_today:
            return
        
        # Get risk parameters
        equity = self.get_equity()
        risk_params = RiskParams(
            equity=equity,
            risk_per_trade=settings.RISK_PER_TRADE
        )
        
        # Get pip value
        pip_value = get_pip_value_per_unit(settings.INSTRUMENT)
        
        if signal == 1:  # Long signal
            stop_price = signal_data['long_stop']
            if stop_price and current_price > stop_price:
                size = position_size_by_risk(
                    current_price, stop_price, pip_value, risk_params, settings.UNITS_CAP
                )
                if size > 0:
                    self.client.place_order(settings.INSTRUMENT, 'buy', size, stop_price)
                    logger.info(f"LONG {size} units @ {current_price} | SL {stop_price}")
        
        elif signal == -1:  # Short signal
            stop_price = signal_data['short_stop']
            if stop_price and current_price < stop_price:
                size = position_size_by_risk(
                    current_price, stop_price, pip_value, risk_params, settings.UNITS_CAP
                )
                if size > 0:
                    self.client.place_order(settings.INSTRUMENT, 'sell', size, stop_price)
                    logger.info(f"SHORT {size} units @ {current_price} | SL {stop_price}")
    
    def run_ccxt(self):
        """Run live trading with CCXT (crypto)"""
        logger.info(f"Starting live trading with {settings.CCXT_EXCHANGE}")
        
        # Get price stream (simplified - would use WebSocket in production)
        while True:
            try:
                price = self.client.get_price(settings.INSTRUMENT)
                if price is None:
                    time.sleep(1)
                    continue
                
                now = dt.datetime.now()
                closed_candle = self.agg.update(price, now)
                
                if closed_candle is not None:
                    self.hist = pd.concat([self.hist, closed_candle]).tail(400)
                    
                    if len(self.hist) >= 60:  # Need enough data for indicators
                        self.check_daily_drawdown()
                        signal_data = self.strategy.get_last_signal(self.hist)
                        self.process_signal(signal_data, price)
                
                time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("Stopping live trading...")
                break
            except Exception as e:
                logger.error(f"Error in live trading: {e}")
                time.sleep(5)
    
    def run_oanda(self):
        """Run live trading with OANDA (forex)"""
        logger.info(f"Starting live trading with OANDA")
        
        # Get pricing stream
        stream = self.client.get_pricing_stream([settings.INSTRUMENT])
        
        for msg in stream:
            try:
                if 'instrument' not in msg or 'bids' not in msg or 'asks' not in msg:
                    continue
                
                bid = float(msg['bids'][0]['price'])
                ask = float(msg['asks'][0]['price'])
                mid = (bid + ask) / 2
                spread = ask - bid
                
                # Skip if spread too wide
                if spread > 0.0001:  # ~1 pip
                    continue
                
                # Parse timestamp
                ts = msg['time'].split('.')[0]
                now = dt.datetime.fromisoformat(ts.replace('Z','')) if 'Z' in ts else dt.datetime.fromisoformat(ts)
                
                closed_candle = self.agg.update(mid, now)
                
                if closed_candle is not None:
                    self.hist = pd.concat([self.hist, closed_candle]).tail(400)
                    
                    if len(self.hist) >= 60:
                        self.check_daily_drawdown()
                        signal_data = self.strategy.get_last_signal(self.hist)
                        
                        # Use ask for long, bid for short
                        if signal_data['signal'] == 1:
                            self.process_signal(signal_data, ask)
                        elif signal_data['signal'] == -1:
                            self.process_signal(signal_data, bid)
                
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                logger.info("Stopping live trading...")
                break
            except Exception as e:
                logger.error(f"Error in live trading: {e}")
                time.sleep(5)
    
    def run_alpaca(self):
        """Run live trading with Alpaca (stocks)"""
        logger.info(f"Starting live trading with Alpaca")
        
        # Get price stream (simplified - would use WebSocket in production)
        while True:
            try:
                price = self.client.get_price(settings.INSTRUMENT)
                if price is None:
                    time.sleep(1)
                    continue
                
                now = dt.datetime.now()
                closed_candle = self.agg.update(price, now)
                
                if closed_candle is not None:
                    self.hist = pd.concat([self.hist, closed_candle]).tail(400)
                    
                    if len(self.hist) >= 60:
                        self.check_daily_drawdown()
                        signal_data = self.strategy.get_last_signal(self.hist)
                        self.process_signal(signal_data, price)
                
                time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("Stopping live trading...")
                break
            except Exception as e:
                logger.error(f"Error in live trading: {e}")
                time.sleep(5)
    
    def run(self):
        """Run live trading"""
        # Initialize client
        self.initialize_client()
        
        # Test connection
        if not self.client.connect():
            logger.error("Failed to connect to broker")
            return
        
        logger.info(f"Connected to {self.broker} broker")
        logger.info(f"Trading {settings.INSTRUMENT} with {self.strategy.get_params()}")
        
        # Run appropriate trading loop
        if self.broker == 'ccxt':
            self.run_ccxt()
        elif self.broker == 'oanda':
            self.run_oanda()
        elif self.broker == 'alpaca':
            self.run_alpaca()


def main():
    """Main entry point"""
    logger.info(f"Starting live trading bot with broker: {settings.BROKER}")
    
    trader = LiveTrader(settings.BROKER)
    trader.run()


if __name__ == "__main__":
    main()
