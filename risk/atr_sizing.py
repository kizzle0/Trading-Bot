"""
ATR-based Position Sizing and Risk Management
"""
from dataclasses import dataclass
import math
from typing import Optional


@dataclass
class RiskParams:
    """Risk management parameters"""
    equity: float          # account equity in quote currency
    risk_per_trade: float  # e.g., 0.005 = 0.5%
    max_position_size: Optional[float] = None  # maximum position size in base currency


def position_size_by_risk(
    entry_price: float, 
    stop_price: float, 
    pip_value_per_unit: float, 
    params: RiskParams, 
    units_cap: Optional[int] = None
) -> int:
    """
    Calculate position size based on risk and stop distance.
    
    Args:
        entry_price: Entry price of the trade
        stop_price: Stop loss price
        pip_value_per_unit: Value of 1 pip for 1 unit of base currency
        params: Risk management parameters
        units_cap: Maximum units to trade (optional)
    
    Returns:
        Integer units to trade
    """
    stop_distance = abs(entry_price - stop_price)
    if stop_distance <= 0:
        return 0
    
    risk_amount = params.equity * params.risk_per_trade
    units_float = risk_amount / (stop_distance * pip_value_per_unit)
    units = int(math.floor(units_float))
    
    # Apply position size limits
    if units_cap:
        units = max(0, min(units, units_cap))
    
    if params.max_position_size:
        max_units = int(params.max_position_size)
        units = max(0, min(units, max_units))
    
    return units


def calculate_stop_distance(entry_price: float, atr: float, atr_multiplier: float) -> float:
    """Calculate stop loss distance based on ATR"""
    return atr * atr_multiplier


def calculate_position_size_atr(
    entry_price: float,
    atr: float,
    atr_multiplier: float,
    pip_value_per_unit: float,
    params: RiskParams,
    units_cap: Optional[int] = None
) -> int:
    """
    Calculate position size using ATR-based stop loss.
    
    Args:
        entry_price: Entry price
        atr: Average True Range value
        atr_multiplier: ATR multiplier for stop loss
        pip_value_per_unit: Value of 1 pip for 1 unit
        params: Risk parameters
        units_cap: Maximum units to trade
    
    Returns:
        Integer units to trade
    """
    stop_distance = calculate_stop_distance(entry_price, atr, atr_multiplier)
    return position_size_by_risk(entry_price, entry_price - stop_distance, pip_value_per_unit, params, units_cap)


def get_pip_value_per_unit(instrument: str) -> float:
    """
    Get pip value per unit for different instruments.
    This is a simplified version - production should handle contract specs properly.
    """
    # Forex pairs
    if 'USD' in instrument and len(instrument) == 7:  # e.g., EURUSD
        return 0.0001
    elif 'JPY' in instrument:  # JPY pairs
        return 0.01
    # Crypto (simplified)
    elif any(crypto in instrument.upper() for crypto in ['BTC', 'ETH', 'ADA', 'DOT']):
        return 1.0  # 1 unit = 1 unit
    # Stocks (simplified)
    else:
        return 1.0  # 1 share = 1 unit
