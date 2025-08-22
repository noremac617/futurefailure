import pandas as pd
import numpy as np
from strategy_base import BaseStrategy
from config import NASDAQ_100
from stock_selector import DynamicStockSelector
import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta

class RSIMeanReversionStrategy(BaseStrategy):
    def __init__(self, api, demo_mode=False):
        super().__init__(
            name="RSI Mean Reversion",
            allocation_percent=0.07,
            api=api
        )
        
        # Add dynamic stock selection
        self.stock_selector = DynamicStockSelector()
        self.target_stocks = self.stock_selector.get_optimized_stock_list(self.name, 12)
        self.last_optimization = datetime.now()
        
        self.oversold_threshold = 25
        self.overbought_threshold = 75
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
        """Look for RSI mean reversion opportunities"""
        
        # Optimize stock list periodically
        self.optimize_stock_list()
        
        if self.demo_mode:
            print(f"  Using demo data for {len(self.target_stocks)} optimized stocks...")
            signals = []
            import random
            
            for symbol in self.target_stocks[:6]:  # Check 6 optimized stocks
                if random.random() < 0.25:  # 25% chance of RSI extreme
                    price_data = self.demo_provider.prices.get(symbol, {})
                    current_price = price_data.get('current_price', 100.0)
                    
                    # Simulate RSI values
                    if random.random() < 0.5:
                        rsi_value = random.uniform(15, 25)
                        direction = 'long'
                    else:
                        rsi_value = random.uniform(75, 85)
                        direction = 'short'
                    
                    signal = {
                        'symbol': symbol,
                        'current_price': current_price,
                        'rsi_value': rsi_value,
                        'direction': direction,
                        'strength': abs(50 - rsi_value) / 50,
                        'target_rsi': 50,
                        'strategy': self.name
                    }
                    signals.append(signal)
                    print(f"    {symbol}: Price=${current_price:.2f}, RSI={rsi_value:.0f}")
                    print(f"    ✅ DEMO SIGNAL: {direction} {symbol} (RSI {rsi_value:.0f})")
            
            return signals
            
        return []
    
    def calculate_position_size(self, account_value, signal_strength=1.0):
        """Calculate position size for RSI trades"""
        base_size = account_value * self.allocation_percent * 0.8
        adjusted_size = base_size * min(signal_strength * 1.3, 1.1)
        return min(adjusted_size, account_value * 0.04)

if __name__ == "__main__":
    from config import ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL
    
    api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL)
    strategy = RSIMeanReversionStrategy(api, demo_mode=True)
    
    print("Testing optimized RSI Mean Reversion strategy...")
    signals = strategy.scan_for_signals()
    print(f"\nFound {len(signals)} RSI signals")