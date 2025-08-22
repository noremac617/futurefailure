import pandas as pd
import numpy as np
from strategy_base import BaseStrategy
from config import NASDAQ_100
from stock_selector import DynamicStockSelector
import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta

class VolumeSpikeReversalStrategy(BaseStrategy):
    def __init__(self, api, demo_mode=False):
        super().__init__(
            name="Volume Spike Reversal",
            allocation_percent=0.05,
            api=api
        )
        
        # Add dynamic stock selection
        self.stock_selector = DynamicStockSelector()
        self.target_stocks = self.stock_selector.get_optimized_stock_list(self.name, 10)
        self.last_optimization = datetime.now()
        
        self.min_price_move = 0.02
        self.min_volume_multiplier = 3.0
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
        """Look for volume spike reversal opportunities"""
        
        # Optimize stock list periodically
        self.optimize_stock_list()
        
        if self.demo_mode:
            print(f"  Using demo data for {len(self.target_stocks)} optimized stocks...")
            signals = []
            import random
            
            for symbol in self.target_stocks[:4]:  # Check 4 optimized stocks
                if random.random() < 0.2:  # 20% chance of volume spike
                    price_data = self.demo_provider.prices.get(symbol, {})
                    current_price = price_data.get('current_price', 100.0)
                    
                    # Simulate price spike
                    spike_direction = random.choice(['up', 'down'])
                    price_move = random.uniform(0.02, 0.05)
                    
                    if spike_direction == 'up':
                        normal_price = current_price / (1 + price_move)
                        fade_direction = 'short'
                    else:
                        normal_price = current_price / (1 - price_move)
                        fade_direction = 'long'
                    
                    # Simulate volume spike
                    volume_multiplier = random.uniform(3.0, 6.0)
                    
                    # Check if no major news (simplified)
                    no_news = random.choice([True, False])
                    
                    if no_news:
                        signal = {
                            'symbol': symbol,
                            'current_price': current_price,
                            'normal_price': normal_price,
                            'price_move': price_move,
                            'volume_multiplier': volume_multiplier,
                            'direction': fade_direction,
                            'strength': price_move,
                            'spike_direction': spike_direction,
                            'strategy': self.name
                        }
                        signals.append(signal)
                        print(f"    {symbol}: Price spike {spike_direction} {price_move:.1%}, Volume {volume_multiplier:.1f}x")
                        print(f"    DEMO SIGNAL: {fade_direction} {symbol} (fade volume spike)")
            
            return signals
            
        return []
    
    def calculate_position_size(self, account_value, signal_strength=1.0):
        """Calculate position size for volume spike trades"""
        base_size = account_value * self.allocation_percent * 0.9
        adjusted_size = base_size * min(signal_strength * 2, 1.3)
        return min(adjusted_size, account_value * 0.03)

if __name__ == "__main__":
    from config import ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL
    
    api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL)
    strategy = VolumeSpikeReversalStrategy(api, demo_mode=True)
    
    print("Testing optimized Volume Spike Reversal strategy...")
    signals = strategy.scan_for_signals()
    print(f"\nFound {len(signals)} volume spike signals")