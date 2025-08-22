from abc import ABC, abstractmethod
import pandas as pd
from datetime import datetime

class BaseStrategy(ABC):
    """Base class for all trading strategies"""
    
    def __init__(self, name, allocation_percent, api):
        self.name = name
        self.allocation_percent = allocation_percent  # e.g., 0.15 for 15%
        self.api = api
        self.trades_today = []
        self.losses_today = 0
        self.active_positions = {}
        
    @abstractmethod
    def scan_for_signals(self):
        """Each strategy implements its own signal detection"""
        pass
    
    @abstractmethod
    def calculate_position_size(self, account_value, signal_strength=1.0):
        """Calculate position size based on strategy allocation"""
        pass
    
    def can_trade(self):
        """Check if strategy can make new trades"""
        # Don't trade if we've had 3 losses today
        if self.losses_today >= 3:
            return False
        return True
    
    def log_trade(self, symbol, action, quantity, price, reason):
        """Log trade for tracking"""
        trade = {
            'timestamp': datetime.now(),
            'symbol': symbol,
            'action': action,
            'quantity': quantity,
            'price': price,
            'reason': reason,
            'strategy': self.name
        }
        self.trades_today.append(trade)
        print(f"[{self.name}] {action} {quantity} {symbol} @ ${price:.2f} - {reason}")