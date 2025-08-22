import pandas as pd
import numpy as np
from strategy_base import BaseStrategy
from config import TOP_LIQUID_STOCKS
from stock_selector import DynamicStockSelector
import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta

class TimeBasedPatternStrategy(BaseStrategy):
    def __init__(self, api, demo_mode=False):
        super().__init__(
            name="Time-Based Patterns",
            allocation_percent=0.03,
            api=api
        )
        
        # Add dynamic stock selection
        self.stock_selector = DynamicStockSelector()
        self.target_stocks = self.stock_selector.get_optimized_stock_list(self.name, 6)
        self.last_optimization = datetime.now()
        
        self.patterns = {
            '10:30': 'reversal',
            '14:00': 'momentum',
            '15:00': 'positioning'
        }
        self.demo_mode = demo_mode
        
        if demo_mode:
            from demo_data import demo_provider
            self.demo_provider = demo_provider
        
        print(f"{self.name} initialized with {len(self.target_stocks)} optimized stocks: {self.target_stocks[:5]}...")
    
    def optimize_stock_list(self):
        """Periodically optimize stock list based on performance"""
        if (datetime.now() - self.last_optimization).days < 1:
            return
        
        old_list = self.target_stocks.copy()
        self.target_stocks = self.stock_selector.update_strategy_targets(self, self.target_stocks)
        self.last_optimization = datetime.now()
        
        if old_list != self.target_stocks:
            print(f"{self.name} stock list updated!")
    
    def scan_for_signals(self):
        """Look for time-based pattern opportunities"""
        
        # Optimize stock list periodically
        self.optimize_stock_list()
        
        if self.demo_mode:
            print(f"  Using demo data for {len(self.target_stocks)} optimized stocks...")
            signals = []
            import random
            
            current_time = random.choice(['10:30', '14:00', '15:00'])
            pattern_type = self.patterns[current_time]
            
            print(f"    Time: {current_time} - {pattern_type} pattern window")
            
            for symbol in self.target_stocks[:3]:  # Check 3 optimized stocks
                if random.random() < 0.4:  # 40% chance pattern triggers
                    price_data = self.demo_provider.prices.get(symbol, {})
                    current_price = price_data.get('current_price', 100.0)
                    
                    if pattern_type == 'reversal':
                        direction = random.choice(['long', 'short'])
                        pattern_strength = random.uniform(0.002, 0.008)
                        target_move = pattern_strength
                    elif pattern_type == 'momentum':
                        direction = random.choice(['long', 'short'])
                        pattern_strength = random.uniform(0.003, 0.012)
                        target_move = pattern_strength
                    else:  # positioning
                        direction = random.choice(['long', 'short'])
                        pattern_strength = random.uniform(0.001, 0.005)
                        target_move = pattern_strength
                    
                    signal = {
                        'symbol': symbol,
                        'current_price': current_price,
                        'pattern_time': current_time,
                        'pattern_type': pattern_type,
                        'direction': direction,
                        'strength': pattern_strength,
                        'target_move': target_move,
                        'strategy': self.name
                    }
                    signals.append(signal)
                    print(f"    {symbol}: {pattern_type} pattern at {current_time}")
                    print(f"    DEMO SIGNAL: {direction} {symbol} ({pattern_type} pattern)")
            
            return signals
            
        return []
    
    def calculate_position_size(self, account_value, signal_strength=1.0):
        """Calculate position size for time pattern trades"""
        base_size = account_value * self.allocation_percent * 1.0
        adjusted_size = base_size * min(signal_strength * 3, 1.5)
        return min(adjusted_size, account_value * 0.02)

if __name__ == "__main__":
    from config import ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL
    
    api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL)
    strategy = TimeBasedPatternStrategy(api, demo_mode=True)
    
    print("Testing optimized Time-Based Pattern strategy...")
    signals = strategy.scan_for_signals()
    print(f"\nFound {len(signals)} time pattern signals")