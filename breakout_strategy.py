import pandas as pd
import numpy as np
from strategy_base import BaseStrategy
from config import NASDAQ_100
from stock_selector import DynamicStockSelector
import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta

class TechnicalBreakoutStrategy(BaseStrategy):
    def __init__(self, api, demo_mode=False):
        super().__init__(
            name="Technical Breakout",
            allocation_percent=0.15,
            api=api
        )
        
        # Add dynamic stock selection
        self.stock_selector = DynamicStockSelector()
        self.target_stocks = self.stock_selector.get_optimized_stock_list(self.name, 12)
        self.last_optimization = datetime.now()
        
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
        """Look for technical breakout opportunities"""
        
        # Optimize stock list periodically
        self.optimize_stock_list()
        
        if self.demo_mode:
            print(f"  Using demo data for {len(self.target_stocks)} optimized stocks...")
            signals = []
            import random
            
            for symbol in self.target_stocks[:6]:  # Check 6 optimized stocks
                if random.random() < 0.25:  # 25% chance of breakout signal
                    price_data = self.demo_provider.prices.get(symbol, {})
                    current_price = price_data.get('current_price', 100.0)
                    
                    # Simulate breakout conditions
                    resistance_level = current_price * random.uniform(0.96, 0.99)
                    breakout_strength = (current_price - resistance_level) / resistance_level
                    
                    # Simulate volume confirmation
                    volume_multiplier = random.uniform(1.5, 3.0)
                    
                    signal = {
                        'symbol': symbol,
                        'current_price': current_price,
                        'resistance_level': resistance_level,
                        'breakout_strength': breakout_strength,
                        'direction': 'long',
                        'strength': breakout_strength,
                        'volume_multiplier': volume_multiplier,
                        'target_days': random.randint(2, 7),
                        'strategy': self.name
                    }
                    signals.append(signal)
                    print(f"    {symbol}: Price=${current_price:.2f}, Resistance=${resistance_level:.2f}")
                    print(f"    Volume: {volume_multiplier:.1f}x normal")
                    print(f"    ✅ DEMO SIGNAL: {signal['direction']} {symbol} (breakout strength: {breakout_strength:.1%})")
            
            return signals
            
        return []
    
    def calculate_position_size(self, account_value, signal_strength=1.0):
        """Calculate position size for breakout trades"""
        base_size = account_value * self.allocation_percent * 0.5
        adjusted_size = base_size * min(signal_strength * 3, 1.5)
        return min(adjusted_size, account_value * 0.08)

if __name__ == "__main__":
    from config import ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL
    
    api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL)
    strategy = TechnicalBreakoutStrategy(api, demo_mode=True)
    
    print("Testing optimized Technical Breakout strategy...")
    signals = strategy.scan_for_signals()
    print(f"\nFound {len(signals)} breakout signals")