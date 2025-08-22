import pandas as pd
import numpy as np
from strategy_base import BaseStrategy
from config import TOP_LIQUID_STOCKS
from stock_selector import DynamicStockSelector
import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta

class EndOfDayMomentumStrategy(BaseStrategy):
    def __init__(self, api, demo_mode=False):
        super().__init__(
            name="End-of-Day Momentum",
            allocation_percent=0.05,
            api=api
        )
        
        # Add dynamic stock selection
        self.stock_selector = DynamicStockSelector()
        self.target_stocks = self.stock_selector.get_optimized_stock_list(self.name, 8)
        self.last_optimization = datetime.now()
        
        self.min_momentum_hours = 2
        self.min_momentum_strength = 0.005
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
        """Look for end-of-day momentum continuation"""
        
        # Optimize stock list periodically
        self.optimize_stock_list()
        
        if self.demo_mode:
            print(f"  Using demo data for {len(self.target_stocks)} optimized stocks...")
            signals = []
            import random
            
            current_time = "15:30"
            
            for symbol in self.target_stocks[:4]:  # Check 4 most liquid optimized stocks
                if random.random() < 0.3:  # 30% chance of momentum
                    price_data = self.demo_provider.prices.get(symbol, {})
                    current_price = price_data.get('current_price', 100.0)
                    
                    # Simulate sustained momentum
                    momentum_direction = random.choice(['up', 'down'])
                    momentum_strength = random.uniform(0.005, 0.02)
                    
                    if momentum_direction == 'up':
                        opening_price = current_price / (1 + momentum_strength)
                        direction = 'long'
                    else:
                        opening_price = current_price / (1 - momentum_strength)
                        direction = 'short'
                    
                    # Simulate volume confirmation
                    volume_support = random.choice([True, False])
                    
                    if volume_support:
                        signal = {
                            'symbol': symbol,
                            'current_price': current_price,
                            'opening_price': opening_price,
                            'momentum_strength': momentum_strength,
                            'direction': direction,
                            'strength': momentum_strength,
                            'entry_time': current_time,
                            'exit_time': '15:50',
                            'strategy': self.name
                        }
                        signals.append(signal)
                        print(f"    {symbol}: {momentum_direction} momentum {momentum_strength:.1%} since open")
                        print(f"    DEMO SIGNAL: {direction} {symbol} (EOD momentum continuation)")
            
            return signals
            
        return []
    
    def calculate_position_size(self, account_value, signal_strength=1.0):
        """Calculate position size for EOD momentum trades"""
        base_size = account_value * self.allocation_percent * 1.0
        adjusted_size = base_size * min(signal_strength * 2, 1.2)
        return min(adjusted_size, account_value * 0.03)

if __name__ == "__main__":
    from config import ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL
    
    api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL)
    strategy = EndOfDayMomentumStrategy(api, demo_mode=True)
    
    print("Testing optimized End-of-Day Momentum strategy...")
    signals = strategy.scan_for_signals()
    print(f"\nFound {len(signals)} EOD momentum signals")