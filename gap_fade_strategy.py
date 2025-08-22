import pandas as pd
import numpy as np
from strategy_base import BaseStrategy
from config import NASDAQ_100
from stock_selector import DynamicStockSelector
import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta

class GapFadeStrategy(BaseStrategy):
    def __init__(self, api, demo_mode=False):
        super().__init__(
            name="Gap Fade",
            allocation_percent=0.10,
            api=api
        )
        
        # Add dynamic stock selection
        self.stock_selector = DynamicStockSelector()
        self.target_stocks = self.stock_selector.get_optimized_stock_list(self.name, 15)
        self.last_optimization = datetime.now()
        
        self.min_gap = 0.008
        self.max_gap = 0.025
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
        """Look for gap opportunities to fade"""
        
        # Optimize stock list periodically
        self.optimize_stock_list()
        
        if self.demo_mode:
            print(f"  Using demo data for {len(self.target_stocks)} optimized stocks...")
            signals = []
            import random
            
            for symbol in self.target_stocks[:8]:  # Check 8 optimized stocks for gaps
                if random.random() < 0.2:  # 20% chance of gap
                    price_data = self.demo_provider.prices.get(symbol, {})
                    current_price = price_data.get('current_price', 100.0)
                    yesterday_close = price_data.get('yesterday_close', current_price * random.uniform(0.98, 1.02))
                    
                    # Calculate gap
                    gap = (current_price - yesterday_close) / yesterday_close
                    
                    if self.min_gap <= abs(gap) <= self.max_gap:
                        # Simulate volume check
                        volume_normal = random.choice([True, False])
                        
                        if volume_normal:
                            signal = {
                                'symbol': symbol,
                                'current_price': current_price,
                                'yesterday_close': yesterday_close,
                                'gap_percent': gap,
                                'direction': 'short' if gap > 0 else 'long',
                                'strength': abs(gap),
                                'target_fill': 0.75,
                                'strategy': self.name
                            }
                            signals.append(signal)
                            print(f"    {symbol}: Gap={gap:.1%} (${yesterday_close:.2f} → ${current_price:.2f})")
                            print(f"    ✅ DEMO SIGNAL: {signal['direction']} {symbol} (fade {gap:.1%} gap)")
            
            return signals
            
        return []
    
    def calculate_position_size(self, account_value, signal_strength=1.0):
        """Calculate position size for gap fades"""
        base_size = account_value * self.allocation_percent * 0.7
        adjusted_size = base_size * min(signal_strength * 1.5, 1.2)
        return min(adjusted_size, account_value * 0.05)

if __name__ == "__main__":
    from config import ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL
    
    api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL)
    strategy = GapFadeStrategy(api, demo_mode=True)
    
    print("Testing optimized Gap Fade strategy...")
    signals = strategy.scan_for_signals()
    print(f"\nFound {len(signals)} gap fade signals")